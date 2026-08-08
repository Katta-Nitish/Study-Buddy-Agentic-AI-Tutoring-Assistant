from langchain_community.document_loaders import PyPDFLoader
import os
import math
import time
import tempfile
from ragas.metrics import answer_relevancy, faithfulness
from ragas import evaluate
from datasets import Dataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import OllamaEmbeddings
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st
from langgraph.graph import StateGraph, START,END
from typing import TypedDict,Dict, Annotated
from langchain_core.output_parsers import StrOutputParser

class State(TypedDict):
    input: str
    messages: Annotated[list, add_messages]
    embedding: list
    first_response: str
    scores: Dict[str, float]
    attempt: int         
    max_attempts: int     
    top_k: int
    history: list[Dict]
    latency: float

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(time.time())

if "agent_memory" not in st.session_state:
    st.session_state.agent_memory=InMemorySaver()

st.set_page_config(page_title="Self Improving Bot", page_icon="🤖")
st.title("Self-Improving RAG Agent with Evaluation & Feedback Loop")

uploaded_file=st.file_uploader(
    "Upload a PDF document to train the agent",
    type=["pdf"],
    help="Only PDF documents are supported",
    accept_multiple_files=False
)
 


if "retriever" not in st.session_state:
    if uploaded_file:
        with st.spinner("Processing Documents..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path=tmp_file.name
            loader=PyPDFLoader(tmp_path)
            documents=loader.load()
            splitter=RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=110)
            chunks=splitter.split_documents(documents)
            embedding=OllamaEmbeddings(model="nomic-embed-text")
            vector=FAISS.from_documents(chunks,embedding)
            retriever=vector
            st.session_state.retriever=retriever
            os.remove(tmp_path)

if "retriever" not in st.session_state:
    st.warning("Please upload a PDF first")
    st.stop()

def embed(state: State):
        k=state.get("top_k", 5)
        retriv=st.session_state.retriever.as_retriever(search_kwargs={"k": k})
        res=retriv.invoke(state['input'])
        final=[doc.page_content for doc in res]
        return {"embedding": final}


def agent_builder(state: State):
    start_time = time.time()
    llm=ChatOllama(model="deepseek-r1:8b",temperature=0.2, keep_alive=False)
    context="\n\n".join(state['embedding'])

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant. Use the following pieces of retrieved "
            "context to answer the user's question. If you don't know the answer, "
            "just say that you don't know.\n\n"
            "Context:\n{context}"
        )),
        MessagesPlaceholder(variable_name="messages") 
        ])
    chain= prompt | llm | StrOutputParser()

    response = chain.invoke({"messages": state['messages'], "context": context})
    latency = time.time() - start_time
    return {"first_response": response, "latency": latency}



def evaluate_response(state: State):
    llm=LangchainLLMWrapper(ChatOllama(model="gemma3:12b",temperature=0, format="json", timeout=600))
    embedding=LangchainEmbeddingsWrapper(OllamaEmbeddings(model="nomic-embed-text"))
    data={
        'question': [state['input']],
        'answer': [state['first_response']],
        'contexts': [state['embedding']]
    }
    dataset=Dataset.from_dict(data)
    evaluation=evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embedding
    )
    raw = evaluation.scores[0]
    relevance = float(raw.get("answer_relevancy", 0.0))
    faith = float(raw.get("faithfulness", 0.0))
    if math.isnan(relevance): relevance = 0.0
    if math.isnan(faith): faith = 0.0
    result={
        "answer_relevancy": relevance,
        "faithfulness": faith
        }
    relevance = float(result["answer_relevancy"])
    faith = float(result["faithfulness"])

    history = list(state.get("history", []))

    history.append({
        "attempt": int(state.get("attempt", 1)),
        "relevance": float(relevance),
        "faithfulness": float(faith),
        "top_k": int(state.get("top_k", 5)),
        "latency": float(state.get("latency", 0))
    })

    return {"scores": result, "history": history}


def response_evaluation(state: State):
    score = state['scores']['answer_relevancy']
    attempt = state.get("attempt", 1)
    max_attempts = state.get("max_attempts", 3)
    if attempt >= max_attempts:
        return {"action":"stop"}
    if score < 0.3:
        new_k=16
    elif score < 0.5:
        new_k=12
    elif score < 0.85:
        new_k=8
    else:
        return {"action": "stop"}
    return {"top_k":new_k, "attempt":attempt+1, "action":"retry"}


    
def get_graph():
    builder=StateGraph(State)
    builder.add_node("embed", embed)
    builder.add_node("agent_builder", agent_builder)
    builder.add_node("evaluate_response", evaluate_response)
    builder.add_node("response_evaluation", response_evaluation)

    builder.add_edge(START, "embed")
    builder.add_edge("embed", "agent_builder")
    builder.add_edge("agent_builder", "evaluate_response")
    builder.add_edge("evaluate_response", "response_evaluation")
    builder.add_conditional_edges(
        "response_evaluation",
        lambda state: state['action'],
        {
            "retry": "embed",
            "stop": END
        }
    )
    return builder.compile(checkpointer=st.session_state.agent_memory)

graph=get_graph()

if "messages" not in st.session_state:
    st.session_state.messages=[]
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message['content'])
if input:=st.chat_input("Ask a question about the uploaded documents"):
    with st.chat_message("user"):
        st.markdown(input)
    st.session_state.messages.append({"role":"user","content":input})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start = time.time()
            response=graph.invoke({
                "input": input,
                "messages": [HumanMessage(content=input)],
                "attempt": 1,
                "max_attempts": 3,
                "top_k": 5
            },
            config=
                {
                    "configurable":
                    {
                        "thread_id": str(time.time()) # <--- Replaced st.session_state.thread_id here
                    }
                }
            )
            total_latency = time.time() - start
            final_answer = response.get("first_response")
            history = response.get("history", [])
            if len(history) > 1:
                st.markdown("✔ Improved using adaptive retrieval")
            st.markdown(final_answer)
            st.write("Attempts:", len(history))
            st.markdown(f"Total Latency: {total_latency:.2f} seconds")

            with st.sidebar:
                st.caption("First response and its scores:")
                st.write("The First Response Generated is:", response.get('first_response'))
                st.write("The Score OF first Response is:", response.get('scores'))
                if len(history) >= 2:
                    first = history[0]["relevance"]
                    last = history[-1]["relevance"]

                    st.write("Improvement:", first, "→", last)
                with st.expander("Full History"):
                    for h in history:
                        st.write(
                            f"Attempt {h['attempt']} | "
                            f"k={h['top_k']} | "
                            f"Rel={h['relevance']:.2f} | "
                            f"Faith={h['faithfulness']:.2f} | "
                            f"Latency={h['latency']:.2f}s"
                        )

            st.session_state.messages.append({"role":"assistant","content":final_answer})
