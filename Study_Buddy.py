import streamlit as st
import time
import os
os.environ["STREAMLIT_GATHER_USAGE_STATS"] = "false"
import asyncio
import tempfile
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core import SummaryIndex
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.google_genai import GoogleGenAI
import nest_asyncio
nest_asyncio.apply()

col_l, col_r = st.columns([2, 4])
with col_l:
    try:
        st.image("study_logo.png", width=200)
    except:
        st.write("📚")

with col_r:
    st.title("Study Buddy")
    st.caption("Ask your study buddy anything related to your lessons and it will answer without any delay and the answers are only from your documents so dont worry about the out of box answers😉")
with st.sidebar:
    st.title("📚 Study Buddy Settings")
    user_key = st.text_input("Enter Google GenAI API Key (Optional)", type="password")
    st.info("Get a key at [Google AI Studio](https://aistudio.google.com/)")
    st.info("Note: Using a local embedding model: BGE-Small (No API cost for file reading)")

file=st.file_uploader(
    "Upload your lesson document here (Note: only pdf,txt and docx type)",
    type=['pdf','txt','docx'],
    help="Only PDF, TXT, and DOCX files are allowed",
    accept_multiple_files=True
)
if user_key:
    # Use user provided key
    llm = GoogleGenAI(api_key=user_key, model_name="models/gemini-1.5-flash")
elif "GEMINI_API_KEY" in st.secrets:
    # Use your secret key
    llm = GoogleGenAI(api_key=st.secrets["GEMINI_API_KEY"], model_name="models/gemini-1.5-flash")
else:
    # Fallback to local Ollama for your Lenovo LOQ testing
    llm = Ollama(model='qwen3:4b', request_timeout=150.0)
Settings.llm=llm

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.embed_model=load_embedding_model()

if file:
    if "agent" not in st.session_state:
        with st.spinner("Reading your documents and waking up Study Buddy..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                file_paths=[]
                for uploaded in file:
                    temp_file_path = os.path.join(temp_dir, uploaded.name)
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    file_paths.append(temp_file_path)
                
                document = SimpleDirectoryReader(input_files=file_paths).load_data()
                splitter = SentenceSplitter(chunk_size=1024)
                node = splitter.get_nodes_from_documents(document)
                vector = VectorStoreIndex(node)
                summary = SummaryIndex(node)

            vector_query = vector.as_query_engine(similarity_top_k=5)
            summary_query = summary.as_query_engine(response_mode="tree_summarize", use_async=True)
            
            vector_tool = QueryEngineTool(
                query_engine=vector_query,
                metadata=ToolMetadata(
                    name="lesson_lookup",
                    description="Search for specific facts in the lesson documents."
                )
            )
            summary_tool = QueryEngineTool(
                query_engine=summary_query,
                metadata=ToolMetadata(
                    name="lesson_summary",
                    description="Summarize the entire document or provide broad overviews."
                )
            )

            my_prompt = """You are a rigorous but highly effective tutor who only uses the provided lesson documents.
            
            RULES:
            1. Base all your answers strictly on the retrieved document context from your tools.
            2. Do not just hand out the simple answer; explain the underlying concepts clearly using bullet points.
            3. If a question is outside the scope of the provided documents, sternly remind the student to stay focused on the syllabus.
            4. Maintain a formal, academic, yet encouraging tone.
            5. Always use your tools to find answers"""

            # Save the memory and agent into session state so they survive the Streamlit reruns
            st.session_state.chat_memory = ChatMemoryBuffer.from_defaults(token_limit=4000)
            st.session_state.agent = FunctionAgent(
                name="StudyBuddy",
                description="A helpful tutoring assistant.",
                tools=[vector_tool, summary_tool],
                system_prompt=my_prompt,
                verbose=True,
                llm=llm
            )
    if "messages" not in st.session_state:
        st.session_state.messages=[]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("user"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                # 1. Define a helper to run the async agent
                    async def get_agent_response(user_input):
                    # We pass the prompt to 'user_msg' as required by Workflow API
                        return await st.session_state.agent.run(user_msg=user_input)

                # 2. Use the existing loop safely thanks to nest_asyncio
                    loop = asyncio.get_event_loop()
                    response = loop.run_until_complete(get_agent_response(prompt))
                
                # 3. Handle the response
                    full_response = str(response)
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                except Exception as e:
                    st.error(f"Agent Error: {e}")