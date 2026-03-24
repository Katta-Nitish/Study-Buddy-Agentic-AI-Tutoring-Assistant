import streamlit as st
import os
os.environ["STREAMLIT_GATHER_USAGE_STATS"] = "false"
import nest_asyncio
nest_asyncio.apply()  # Fix: prevents asyncio event loop conflicts in Streamlit
import asyncio
import tempfile
from llama_index.llms.ollama import Ollama
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core import SummaryIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.memory import ChatMemoryBuffer

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

# --- SIDEBAR ---
with st.sidebar:
    st.title("📚 Study Buddy Settings")
    user_key = st.text_input("Enter Gemini API Key (Optional)", type="password")
    st.info("Using a local embedding model: BGE-Small (No API cost for file reading)")

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.embed_model = load_embedding_model()

# --- LLM SELECTION ---
if user_key:
    llm = GoogleGenAI(api_key=user_key, model_name="models/gemini-1.5-flash")
elif "GEMINI_API_KEY" in st.secrets:
    llm = GoogleGenAI(api_key=st.secrets["GEMINI_API_KEY"], model_name="models/gemini-1.5-flash")
else:
    llm = Ollama(model='qwen3:4b', request_timeout=150.0)

Settings.llm = llm

# --- FILE UPLOAD ---
uploaded_files = st.file_uploader(
    "Upload your lesson document here (PDF, TXT or DOCX only)",
    type=['pdf', 'txt', 'docx'],
    help="Only PDF, TXT, and DOCX files are allowed",
    accept_multiple_files=True
)

@st.cache_resource(show_spinner="Reading your documents...")
def build_index(file_key: str, file_contents: list[bytes], file_names: list[str]):
    """
    Builds and returns (vector_index, summary_index).
    Cached by a key derived from file names and sizes — rebuilds only when files change.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        for name, content in zip(file_names, file_contents):
            path = os.path.join(temp_dir, name)
            with open(path, "wb") as f:
                f.write(content)
            file_paths.append(path)
        documents = SimpleDirectoryReader(input_files=file_paths).load_data()

    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)
    summary_index = SummaryIndex(nodes)
    return vector_index, summary_index

@st.cache_resource(show_spinner="Setting up your Study Buddy...")
def build_agent(_vector_index, _summary_index, file_key: str):
    """
    Builds and caches the ReActAgent with its own persistent memory.
    The leading underscore on index args tells Streamlit not to hash them.
    Keyed by file_key so agent+memory reset when new files are uploaded.
    """
    vector_query = _vector_index.as_query_engine(similarity_top_k=5)
    summary_query = _summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True
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
5. Maintain a formal, academic, yet encouraging tone throughout."""

    memory = ChatMemoryBuffer.from_defaults(token_limit=4096)

    agent = ReActAgent(
        tools=[vector_tool, summary_tool],
        memory=memory,
        system_prompt=system_prompt,
        verbose=True
    )
    return agent


# --- MAIN CHAT LOGIC ---
if uploaded_files:
    file_key = "_".join(f"{f.name}-{len(f.getvalue())}" for f in uploaded_files)
    file_contents = [f.getvalue() for f in uploaded_files]
    file_names = [f.name for f in uploaded_files]

    vector_index, summary_index = build_index(file_key, file_contents, file_names)
    agent = build_agent(vector_index, summary_index, file_key)

    if st.session_state.get("current_file_key") != file_key:
        st.session_state.messages = []
        st.session_state.current_file_key = file_key

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
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.chat(prompt)
                response_text = str(response)
                st.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})

else:
    st.info("👆 Upload one or more lesson documents to get started!")