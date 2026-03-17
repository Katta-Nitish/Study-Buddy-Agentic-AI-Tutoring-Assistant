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
from llama_index.core.agent import ReActAgent
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.memory import ChatMemoryBuffer


st.title("Study Buddy")
st.write("Ask your study buddy anything related to your lessons and it will answer without any delay and the answers are only from your documents so dont worry about the out of box answers😉")

file=st.file_uploader(
    "Upload your lesson document here (Note: only pdf,txt and docx type)",
    type=['pdf','txt','docx'],
    help="Only PDF, TXT, and DOCX files are allowed",
    accept_multiple_files=True
)
llm=Ollama(model='deepseek-r1:8b',request_timeout=150.0)
Settings.llm=llm

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.embed_model=load_embedding_model()

if file:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths=[]
        for uploaded in file:
            temp_file_path=os.path.join(temp_dir,uploaded.name)
            with open(temp_file_path,"wb") as f:
                f.write(uploaded.getvalue())
            file_paths.append(temp_file_path)
        document=SimpleDirectoryReader(input_files=file_paths).load_data()
        splitter=SentenceSplitter(chunk_size=1024)
        node=splitter.get_nodes_from_documents(document)
        vector=VectorStoreIndex(node)
        summary=SummaryIndex(node)
    vector_query=vector.as_query_engine(
        similarity_top_k=5  
    )
    summary_query=summary.as_query_engine(
        response_mode="tree_summarize",
        use_async=True
    )
    vector_tool=QueryEngineTool(
        query_engine=vector_query,
        metadata=ToolMetadata(
            name="vector_tool",
            description="Use this tool to find specific facts or details from the uploaded lessons."
        )
    )
    summary_tool=QueryEngineTool(
        query_engine=summary_query,
        metadata=ToolMetadata(
            name="summary_tool",
            description="Use this tool to summarize the lessons or answer broad questions about the entire document."
        )
    )
    my_prompt ="""You are a rigorous but highly effective Computer Science professor specializing in AI and Machine Learning at MLRITM. 
    Your job is to tutor a B.Tech CSE student using ONLY the provided lesson documents.
    
    RULES:
    1. Base all your answers strictly on the retrieved document context from your tools.
    2. Do not just hand out the simple answer; explain the underlying concepts clearly using bullet points.
    3. If a question is outside the scope of the provided documents, sternly remind the student to stay focused on the syllabus.
    4. Maintain a formal, academic, yet encouraging tone."""

    
    if "agent_moemory" not in st.session_state:
        st.session_state.agent_memory=ChatMemoryBuffer.from_defaults(token_limit=4096)
    agent=ReActAgent(
        tools=[vector_tool,summary_tool],
        memory=st.session_state.agent_memory,
        system_prompt=my_prompt,
        verbose=True
    )
    if "messages" not in st.session_state:
        st.session_state.messages=[]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt:=st.chat_input("user"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                async def answer(user_input):
                    return await agent.run(user_msg=user_input)
                response=asyncio.run(answer(prompt))
                st.write(str(response))
        st.session_state.messages.append({"role":"assistant","content":str(response)})