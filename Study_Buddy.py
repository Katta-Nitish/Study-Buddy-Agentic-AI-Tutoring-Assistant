from pydoc import doc
import re
import streamlit as st
import os
os.environ["STREAMLIT_GATHER_USAGE_STATS"] = "false"
import asyncio
import nest_asyncio

# Force Python to use the standard asyncio event loop instead of uvloop
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Now it is safe to apply nest_asyncio
nest_asyncio.apply()
import tempfile
from llama_index.llms.ollama import Ollama
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core import SummaryIndex
from llama_index.core.agent import ReActAgent
from llama_parse import LlamaParse
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.memory import ChatMemoryBuffer
import chromadb

import time

def stream_text(text):
    """A generator that yields text word-by-word to simulate AI streaming."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)

# --- HEADER ---
col_l, col_r = st.columns([2, 4])
with col_l:
    try:
        st.image("study_logo.png", width=300)
    except:
        st.write("📚")
with col_r:
    st.title("Study Buddy")
    st.caption("Ask your study buddy anything related to your lessons — answers come strictly from your uploaded documents 😉")

# --- SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("📚 Study Buddy Settings")
    
    user_key = st.text_input("Enter Gemini API Key (Optional)", type="password")
    st.caption("Get your free Gemini API key [here](https://aistudio.google.com/app/apikey) to enable the Conversational Agent.")
    st.info("Without a Gemini API key, you'll still get powerful answers based on your documents, but the agent won't be able to handle follow-up questions or maintain conversational context. For the best experience, we recommend using a Gemini API key.")

    st.divider() 
    
    llama_parse_key = st.text_input("Enter LlamaCloud Key (Optional)", type="password")
    st.caption("Get your free LlamaParse key [here](https://cloud.llamaindex.ai/) to enable advanced PDF extraction.")
    
    st.divider()
    
    st.info("Using a local embedding model: BGE-Small (No API cost for file reading) if using conversational agent, otherwise no embedding model is used. The app will use ChromaDB's internal embedding if you choose the Question Answer Agent mode without a Gemini API key.")

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = load_embedding_model()

uploaded_files = st.file_uploader(
    "Upload your lesson document here (PDF, TXT or DOCX only)",
    type=['pdf', 'txt', 'docx'],
    help="Only PDF, TXT, and DOCX files are allowed",
    accept_multiple_files=True
)
@st.cache_resource(show_spinner="Reading your documents...")
def build_index(file_key: str, file_contents: list[bytes], file_names: list[str]):
    if llama_parse_key:
        LLAMA_PARSE_API_KEY = llama_parse_key
    else:
        LLAMA_PARSE_API_KEY = st.secrets["LLAMA_PARSE_API_KEY"]
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            for name, content in zip(file_names, file_contents):
                path = os.path.join(temp_dir, name)
                with open(path, "wb") as f:
                    f.write(content)
                file_paths.append(path)
            parser = LlamaParse(
                api_key=LLAMA_PARSE_API_KEY,
                result_type="markdown",
                verbose=True
            )
        file_extractor = {".pdf": parser}
        documents = SimpleDirectoryReader(input_files=file_paths
                                          , file_extractor=file_extractor
                                          ).load_data()
    except Exception as e:
        st.error(f"Error during file parsing: {str(e)}. Please provide your LlamaParse API key Since we are facing an issue integrating our api key(ifkey is already provided check your key and ensure your files are in the correct format.)")
        return None, None, None

    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    client=chromadb.Client()
    Collection=client.get_or_create_collection(name="Lessons")
    doc_texts=[x.text for x in nodes]
    ids = [f"chunk_{i}" for i in range(len(doc_texts))]
    Collection.add(
        documents=doc_texts,
        ids=ids
    )
    vector_index = VectorStoreIndex(nodes)
    summary_index = SummaryIndex(nodes)
    return vector_index, summary_index,Collection


option=st.selectbox("Select Weather ypu want an convernational agant or a question answer agent",["Conversational Agent(Note: Gemini API key required)","Question Answer Agent"])
st.session_state.option=option

if st.session_state.option=="Conversational Agent(Note: Gemini API key required)":
    st.info("The Conversational Agent mode allows for follow-up questions and a more interactive tutoring experience. It uses the Google Gemini API, so an API key is required. If you don't have one, you can still use the Question Answer Agent mode without an API key.")

    # --- LLM SELECTION ---
    if user_key:
        llm = GoogleGenAI(api_key=user_key, model_name="models/gemini-1.5-flash")
        Settings.llm = llm


    # --- BUILD AGENT (No longer cached!) ---
    def build_agent(vector_index, summary_index, file_key: str):
        """
        Builds the ReActAgent. Not cached to avoid asyncio loop conflicts.
        Memory is persisted via Streamlit session_state instead.
        """
        vector_query = vector_index.as_query_engine(similarity_top_k=5)
        summary_query = summary_index.as_query_engine(
            response_mode="tree_summarize",
            use_async=False  # Safety check for Streamlit threading
        )

        vector_tool = QueryEngineTool(
            query_engine=vector_query,
            metadata=ToolMetadata(
                name="vector_tool",
                description=(
                    "Use this tool to answer specific or follow-up questions about a particular topic, "
                    "concept, or detail from the uploaded lessons. Prefer this for focused questions."
                )
            )
        )
        summary_tool = QueryEngineTool(
            query_engine=summary_query,
            metadata=ToolMetadata(
                name="summary_tool",
                description=(
                    "Use this tool ONLY when the student asks for a broad overview or summary of the "
                    "entire document. Do NOT use this for specific or follow-up questions."
                )
            )
        )

        system_prompt = """You are a rigorous but highly effective professor tutoring a student.
    You must answer using ONLY the content retrieved from the provided lesson documents via your tools.

    RULES:
    1. For every question — including follow-up questions — you MUST call the vector_tool with a 
    precise query that reflects exactly what the student is asking about right now.
    - For follow-ups, include the specific topic from the prior turn in your tool query 
        (e.g., if the student previously asked about "mitosis" and now asks "what happens next?", 
        query the tool for "mitosis next steps" or "phases after mitosis").
    2. Never answer from memory alone — always retrieve fresh context from the tools.
    3. Explain concepts clearly using bullet points; do not just state bare facts.
    4. If a question is outside the scope of the uploaded documents, firmly remind the student 
    to stay focused on the syllabus.
    5. Maintain a formal, academic, yet encouraging tone throughout.
    6. LANGUAGE LOCK: You MUST respond in English. Even if you are using a multilingual model, do not switch to any other language."""

        # Keep memory in session state so it survives reruns
        if "agent_memory" not in st.session_state:
            st.session_state.agent_memory = ChatMemoryBuffer.from_defaults(token_limit=4096)

        agent = ReActAgent(
            tools=[vector_tool, summary_tool],
            memory=st.session_state.agent_memory,
            system_prompt=system_prompt,
            verbose=True
        )
        return agent


    if uploaded_files:
        # Build a stable cache key from file names + sizes
        file_key = "_".join(f"{f.name}-{len(f.getvalue())}" for f in uploaded_files)
        file_contents = [f.getvalue() for f in uploaded_files]
        file_names = [f.name for f in uploaded_files]

        vector_index, summary_index = build_index(file_key, file_contents, file_names)
        
        # Reset chat and memory when files change
        if st.session_state.get("current_file_key") != file_key:
            st.session_state.messages = []
            st.session_state.current_file_key = file_key
            st.session_state.agent_memory = ChatMemoryBuffer.from_defaults(token_limit=4096)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Render chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle new user input
        if prompt := st.chat_input("Ask a question about your lessons..."):
            with st.chat_message("user"):
                st.markdown(prompt)

            # --- RAG AMNESIA FIX ---
            # Build conversation context from Streamlit history so the agent understands pronouns
            chat_context = ""
            if len(st.session_state.messages) > 0:
                chat_context = "--- RECENT CONVERSATION HISTORY ---\n"
                # Grab the last 4 messages to establish context
                for msg in st.session_state.messages[-4:]:
                    role = "Student" if msg["role"] == "user" else "Tutor"
                    chat_context += f"{role}: {msg['content']}\n"
                chat_context += "-----------------------------------\n\n"


            contextualized_prompt = f"{chat_context}Current Student Question: {prompt}\n\n(Note: Use history for context,The student may ask follow up questions if you see any answer based on the previous question, but answer the Current Student Question ONLY in English.)"
            # -----------------------

            # Save the clean prompt to the UI history
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    
                    async def generate_response():
                        try:
                            agent = build_agent(vector_index, summary_index, file_key)
                            return await agent.run(user_msg=contextualized_prompt)
                        except Exception as e:
                            if "429" in str(e):
                                return "⏳ **Whoops! I'm thinking a little too fast.** The Google Gemini API has reached its free-tier rate limit (too many requests in one minute). Please wait about 60 seconds and try asking your question again!"
                            else:
                                return f"⚠️ **An unexpected error occurred:** {str(e)}"
                    response = asyncio.run(generate_response())
                    
                    response_text = str(response)
                    st.markdown(response_text)

            st.session_state.messages.append({"role": "assistant", "content": response_text})
else:
    if uploaded_files:
        file_key = "_".join(f"{f.name}-{len(f.getvalue())}" for f in uploaded_files)
        file_contents = [f.getvalue() for f in uploaded_files]
        file_names = [f.name for f in uploaded_files]
        vector_index, summary_index, collection = build_index(file_key, file_contents, file_names)

        if "messages" not in st.session_state:
            st.session_state.messages=[]
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        if prompt:= st.chat_input("Ask a question about your lessons..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role":"user","content":prompt})
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = collection.query(query_texts=[prompt], n_results=1)
                    if response['documents'] and len(response['documents'][0]) > 0:
                        st.markdown("**Here is the most relevant information from your documents:**")
                        formatted_response = ""
                        for i, doc in enumerate(response['documents'][0]):
                            # Convert markdown headings to bold (no giant headers)
                            clean_doc = re.sub(r'^#{1,6}\s+(.*?)$', r'**\1**', doc, flags=re.MULTILINE)
                            # Collapse 3+ newlines
                            clean_doc = re.sub(r'\n{3,}', '\n\n', clean_doc)

                            lines = clean_doc.split('\n')
                            output = []
                            i_line = 0
                            while i_line < len(lines):
                                line = lines[i_line].strip()

                                if not line:
                                    output.append('')
                                    i_line += 1
                                    continue

                                if re.match(r'^(\-|\*|•|\d+[\.\)])\s+', line):
                                    output.append(line)
                                    i_line += 1
                                    continue

                                if re.match(r'^\*\*.+\*\*$', line):
                                    output.append(line)
                                    i_line += 1
                                    continue

                                if len(line) < 60 and not line.endswith(('.', ',', ';')):
                                    output.append(f"**{line}**" if not line.startswith('**') else line)
                                    i_line += 1
                                    continue
                                para_lines = []
                                while i_line < len(lines):
                                    l = lines[i_line].strip()
                                    if not l:
                                        break
                                    if re.match(r'^(\-|\*|•|\d+[\.\)])\s+', l):
                                        break
                                    if re.match(r'^\*\*.+\*\*$', l):
                                        break
                                    if len(l) < 60 and not l.endswith(('.', ',', ';')):
                                        break
                                    para_lines.append(l)
                                    i_line += 1
                                output.append(' '.join(para_lines))

                            clean_doc = '\n'.join(output)
                            formatted_response += f"**Excerpt {i+1}:**\n{clean_doc}\n\n"
                            
                        st.write_stream(stream_text(formatted_response))
                    else:
                        formatted_response = "I couldn't find any relevant information in the uploaded documents."
                st.session_state.messages.append({"role":"assistant","content":formatted_response})
            