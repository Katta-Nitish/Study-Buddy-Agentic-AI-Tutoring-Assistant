# 📚 Study Buddy

> An AI-powered study companion that answers your questions based on your lesson documents using advanced RAG (Retrieval Augmented Generation) techniques.

## 🌐 Live Demo

**Try it now:** [https://study-buddy-nitish.streamlit.app/](https://study-buddy-nitish.streamlit.app/)

No installation needed — bring a lesson document and optionally a Gemini API key!

---

## 🌟 Features

- **Two Agent Modes**: Choose between a full Conversational Agent or a lightweight Question Answer Agent — no API key needed for the latter
- **Document Upload**: Support for PDF, TXT, and DOCX files
- **LlamaParse Integration**: Advanced PDF extraction that preserves structure, tables, and formatting (optional, via LlamaCloud key)
- **ChromaDB Vector Store**: Powers the Question Answer Agent with fast, embedded vector search — no API key required
- **Intelligent RAG System**: Combines vector search and summarization for accurate answers
- **Context-Aware Responses**: All answers are grounded strictly in your uploaded documents
- **RAG Amnesia Fix**: Conversation history injected into each query so follow-up questions resolve correctly
- **Streaming Responses**: Word-by-word output in Question Answer mode for a natural reading experience
- **Rate Limit Handling**: Friendly error messages when the Gemini free-tier quota is hit
- **Language Lock**: Always responds in English regardless of the underlying model
- **Smart Cache**: Document index rebuilds only when files change — fast reruns in the same session

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- *(Optional)* A [Google AI Studio](https://aistudio.google.com/) API key — required for Conversational Agent mode
- *(Optional)* A [LlamaCloud](https://cloud.llamaindex.ai/) API key — for advanced PDF extraction
- *(Fallback)* [Ollama](https://ollama.ai/) — for fully local, offline inference

### System Requirements

- **RAM**: 4GB minimum (8GB recommended for local Ollama)
- **Storage**: 500MB for cloud setup; 5GB+ if using Ollama locally
- **GPU**: Not required when using Google Gemini

### Required Models (Ollama fallback only)

```bash
ollama pull qwen3:4b
```

---

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/Katta-Nitish/Study-Buddy-Agentic-AI-Tutoring-Assistant.git
cd study-buddy
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install required packages**

```bash
pip install -r requirements.txt
```

---

## 📦 Dependencies

- **streamlit** — Web UI framework
- **llama-index** — Vector store and RAG framework
- **llama-parse** — Advanced PDF extraction (LlamaCloud)
- **llama-index-llms-google-genai** — Google Gemini integration
- **llama-index-llms-ollama** — Local Ollama fallback
- **chromadb** — Embedded vector database for Question Answer mode
- **huggingface-hub** — Local embedding model

See `requirements.txt` for the complete list.

---

## 🤖 Agent Modes

Study Buddy offers two modes selectable from a dropdown in the app:

### 1. 🧠 Conversational Agent *(Gemini API key required)*

A full ReActAgent powered by Google Gemini that:
- Handles multi-turn conversations and follow-up questions
- Uses a dual-index RAG pipeline (vector search + document summarization)
- Maintains chat memory across turns via `ChatMemoryBuffer`
- Applies the RAG Amnesia Fix (last 4 messages injected into each prompt)
- Enforces Language Lock (always responds in English)
- Shows a friendly message when the Gemini free-tier rate limit (429) is hit

**Best for**: In-depth study sessions, concept explanations, follow-up questions.

---

### 2. 💬 Question Answer Agent *(No API key needed)*

A lightweight retrieval mode powered by ChromaDB that:
- Queries the document vector store directly and returns the most relevant chunk
- Streams the response word-by-word for a natural reading experience
- Cleans and formats raw document text (removes large headings, collapses whitespace, auto-bolds short titles)
- Uses ChromaDB's internal embedding — no external API cost

**Best for**: Quick lookups, checking specific facts, use when you don't have an API key.

---

### Mode Comparison

| Feature | Conversational Agent | Question Answer Agent |
|---------|---------------------|----------------------|
| **API key needed** | Gemini key required | ❌ None needed |
| **Follow-up questions** | ✅ Full support | ❌ Single-turn only |
| **Answer quality** | Explained, concept-focused | Raw document excerpt |
| **Streaming** | ❌ | ✅ Word-by-word |
| **Memory** | ✅ ChatMemoryBuffer | ❌ |
| **Vector backend** | LlamaIndex VectorStoreIndex | ChromaDB |
| **Embedding** | BGE-Small (local) | ChromaDB internal |

---

## ⚙️ Configuration

### API Keys (all optional)

| Key | Where to get it | Used for |
|-----|----------------|---------|
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/app/apikey) | Conversational Agent LLM |
| LlamaCloud Key | [LlamaCloud](https://cloud.llamaindex.ai/) | Advanced PDF parsing |

Both keys can be entered at runtime in the sidebar, or set persistently via Streamlit secrets (see below).

---

### LLM Selection (Conversational Agent — Priority Order)

| Priority | Source | How |
|----------|--------|-----|
| 1st | Sidebar input | Paste key at runtime — no file setup needed |
| 2nd | `st.secrets["GEMINI_API_KEY"]` | Set in `.streamlit/secrets.toml` for deployment |
| 3rd | Local Ollama | Runs `qwen3:4b` if no key is available |

---

### LlamaParse Selection (Priority Order)

| Priority | Source |
|----------|--------|
| 1st | Sidebar input |
| 2nd | `st.secrets["LLAMA_PARSE_API_KEY"]` |

If neither is available, `SimpleDirectoryReader` falls back to its built-in PDF parser.

---

### Persistent Keys via Streamlit Secrets

Create `.streamlit/secrets.toml` for deployment:

```toml
GEMINI_API_KEY = "your-gemini-key-here"
LLAMA_PARSE_API_KEY = "your-llamacloud-key-here"
```

---

### Embedding Model

Study Buddy always uses a local HuggingFace model for embeddings in Conversational Agent mode — no API cost:

- **Model**: `BAAI/bge-small-en-v1.5`
- **Type**: Sentence-BERT
- **Dimensions**: 384
- **Cost**: Free (runs locally)

In Question Answer Agent mode, ChromaDB uses its own internal embedding — also free.

---

### Setup Comparison

| Aspect | Gemini (Cloud) | Local Ollama |
|--------|---------------|--------------|
| **Cost** | Free tier available | Free (local compute) |
| **Speed** | Fast (cloud) | Depends on hardware |
| **Privacy** | Queries sent to Google | 100% local |
| **Setup** | API key only | Requires Ollama install |
| **Quality** | Excellent | Good |
| **Offline** | ❌ | ✅ |
| **GPU needed** | ❌ | Optional |

---

## 💻 Usage

1. **Start the application**

```bash
streamlit run Study_Buddy.py
```

2. **Configure in the sidebar** *(all optional)*
   - Paste your Gemini API key for Conversational Agent mode
   - Paste your LlamaCloud key for advanced PDF extraction

3. **Select your agent mode** from the dropdown

4. **Upload your documents**
   - Select one or multiple lesson documents (PDF, TXT, or DOCX)
   - The index builds once and is cached — reruns within the session are instant

5. **Ask questions**
   - Conversational mode: multi-turn, follow-up friendly
   - Question Answer mode: fast single-turn lookups with streaming output

---

## 🛠️ How It Works

### Architecture

```
┌─────────────────────────────────┐
│         Upload Documents        │
│   (LlamaParse for PDF if key    │
│    available, else built-in)    │
└──────────────┬──────────────────┘
               ↓
┌──────────────────────────────────┐
│   Text Chunking (SentenceSplitter│
│   chunk_size=1024)               │
└──────┬───────────────────────────┘
       │
       ├──────────────────────────────────────────┐
       ↓                                          ↓
┌──────────────────────┐              ┌───────────────────────────┐
│  Conversational Mode │              │  Question Answer Mode     │
│                      │              │                           │
│  VectorStoreIndex    │              │  ChromaDB Collection      │
│  SummaryIndex        │              │  (internal embedding)     │
│                      │              │                           │
│  RAG Amnesia Fix     │              │  Direct chunk retrieval   │
│  (last 4 messages)   │              │  + Markdown cleanup       │
│                      │              │  + Streaming output       │
│  ReActAgent          │              │                           │
│  (Gemini/Ollama)     │              └───────────────────────────┘
└──────────────────────┘
```

### Key Components

1. **LlamaParse**: Parses PDFs into clean Markdown, preserving tables, headings, and structure better than the default reader. Falls back to `SimpleDirectoryReader` if no key is provided.

2. **ChromaDB**: An in-memory vector store used by the Question Answer Agent. Stores all document chunks and retrieves the closest match to the user's query using its built-in embedding — no external API needed.

3. **VectorStoreIndex + SummaryIndex**: Used by the Conversational Agent for semantic fact retrieval (top-5) and full-document summarization (tree-summarize) respectively.

4. **ReActAgent**: Reasons step-by-step to select between `vector_tool` and `summary_tool` based on the query type.

5. **RAG Amnesia Fix**: The last 4 messages from chat history are prepended to every new prompt so the agent resolves follow-up questions and pronouns correctly.

6. **Streaming Output**: The Question Answer Agent uses a word-by-word generator (`stream_text`) with `st.write_stream` for a natural reading experience.

7. **Markdown Cleanup Pipeline**: Raw document chunks from ChromaDB are cleaned before display — large headings are converted to bold, excess whitespace is collapsed, and short lines are auto-formatted as titles.

8. **Rate Limit Handling**: A 429 error from the Gemini API surfaces a friendly user-facing message asking the user to wait ~60 seconds before retrying.

9. **asyncio Fix**: `asyncio.DefaultEventLoopPolicy()` is set before `nest_asyncio.apply()` to ensure a stable event loop under Streamlit's threading model.

---

## 🏗️ Architecture Notes

### Key Design Decisions

1. **Dual Agent Modes**: Splitting the app into a full conversational mode and a lightweight QA mode makes Study Buddy accessible to users who don't have or don't want to use an API key, without compromising the full experience for those who do.

2. **LlamaParse for PDFs**: The default PDF parser often loses tables and structured formatting. LlamaParse outputs clean Markdown, which dramatically improves the quality of retrieved chunks for technical or academic documents.

3. **ChromaDB for QA Mode**: An in-process ChromaDB client handles all vector storage and retrieval without any external dependencies. Its internal embedding means zero setup cost for the basic mode.

4. **Decoupled Index and Agent**: `build_index` is `@st.cache_resource` (rebuilds only on file change), while `build_agent` is intentionally not cached — this avoids asyncio event loop conflicts when caching async objects across Streamlit reruns.

5. **Memory via Session State**: `ChatMemoryBuffer` is stored in `st.session_state` so it persists across reruns without requiring the agent to be re-cached.

6. **RAG Amnesia Fix**: The last 4 conversation turns are explicitly injected into the prompt alongside the memory buffer, ensuring follow-ups like *"explain the second point"* are resolved with correct context even if the buffer is truncated.

7. **Language Lock**: The system prompt instructs the model to always respond in English, preventing multilingual models (e.g. Qwen) from switching languages mid-session.

8. **asyncio Stability**: Setting `asyncio.DefaultEventLoopPolicy()` before `nest_asyncio.apply()` prevents conflicts between Streamlit's internal event loop and LlamaIndex's async agent execution.

---

## 🎯 System Prompt Design (Conversational Agent)

The ReActAgent is instructed to:

- Always call `vector_tool` for every question, with a precise query in full context
- For follow-ups, include the topic from the prior turn in the tool query
- Never answer from memory alone — always retrieve fresh context via tools
- Use `summary_tool` only for broad document overviews
- Explain concepts clearly using bullet points
- Redirect off-topic questions back to the syllabus
- Maintain a formal, academic, yet encouraging tone
- Always respond in English (Language Lock)

---

## 📝 Example Usage

```
--- Conversational Agent ---

User: "Explain mitosis"
Agent: [Calls vector_tool("mitosis")] → retrieves content
Response: "Mitosis is the process by which a cell divides into two identical daughter cells.
• Prophase: chromosomes condense...
• Metaphase: chromosomes align at the cell plate...
..."

User: "What happens after that?"
Agent: [Sees injected history → calls vector_tool("mitosis phases after metaphase")]
Response: "Following metaphase, the cell enters Anaphase..."

--- Question Answer Agent ---

User: "What is a linked list?"
App: [Queries ChromaDB → retrieves top chunk → streams response word-by-word]
Response: "**Excerpt 1:**
**Linked Lists**
A linked list is a linear data structure where each element (node) contains a data field
and a reference to the next node in the sequence..."
```

---

## 🔧 Technical Details

### LLM Configuration

| Setting | Value |
|---------|-------|
| Primary Model | `gemini-1.5-flash` (Google GenAI) |
| Fallback Model | `qwen3:4b` (Ollama local) |
| Agent Type | `ReActAgent` |
| Memory Limit | 4096 tokens |
| Request Timeout (Ollama) | 150 seconds |
| Summary Async | Disabled (`use_async=False`) |

### Embedding Models

| Mode | Model | Cost |
|------|-------|------|
| Conversational Agent | `BAAI/bge-small-en-v1.5` (local, 384-dim) | Free |
| Question Answer Agent | ChromaDB internal | Free |

### Document Processing

| Setting | Value |
|---------|-------|
| Chunk Size | 1024 tokens |
| Splitter | SentenceSplitter |
| Supported Formats | PDF, TXT, DOCX |
| PDF Parser | LlamaParse (if key available) or built-in |
| Vector Top-K (Conversational) | 5 |
| Vector Top-K (QA Agent) | 1 |
| Context Window (history) | Last 4 messages |
| Index Caching | By file name + size key |

---

## 📊 Performance Considerations

- **First Load**: Embedding model download + document indexing takes ~1-2 minutes (cached for the session)
- **File Change**: New files automatically reset the index, memory, and chat history
- **Gemini Mode**: Fast cloud inference, minimal local resource usage
- **QA Agent Mode**: Near-instant responses via ChromaDB with no API latency
- **Ollama Fallback**: ~2GB RAM for Qwen3:4b; CPU-friendly

### Optimization Tips

- Use your Gemini key for the best conversational experience
- Use QA Agent mode for quick lookups without any API key
- For large documents, split into 20–30 page chunks for optimal indexing performance
- LlamaParse significantly improves results for PDFs with tables or complex layouts

---

## 🐛 Troubleshooting

### Issue: "Connection refused" (Ollama fallback)
```bash
ollama serve
```

### Issue: Gemini returns a rate limit error (429)
The app will show a friendly message asking you to wait ~60 seconds. This is a free-tier quota limit. You can also switch to Question Answer Agent mode while waiting.

### Issue: Gemini model not responding
Verify your API key at [Google AI Studio](https://aistudio.google.com/). Check your free-tier quota.

### Issue: Model not found (Ollama)
```bash
ollama pull qwen3:4b
```

### Issue: Poor PDF extraction quality
Enter a LlamaCloud key in the sidebar to enable LlamaParse, which produces much cleaner output for structured PDFs.

### Issue: Agent gives wrong answer to follow-up questions
Handled automatically by the RAG Amnesia Fix. If it persists, try rephrasing with more explicit context (e.g. *"what happens after mitosis metaphase?"* instead of *"what happens next?"*).

### Issue: Slow responses (Ollama)
Switch to Gemini (enter your API key in the sidebar), or check that you have ~2GB of free RAM for Qwen3:4b.

---

## 📚 Project Structure

```
study-buddy/
├── Study_Buddy.py          # Main application file
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .streamlit/
│   └── secrets.toml        # Optional: Gemini + LlamaCloud keys for deployment
└── .gitignore              # Git ignore file
```

---

## 🎓 Educational Context

This project was designed for students to enhance learning through:

- Self-paced revision of lesson materials
- Instant clarification of concepts
- Interactive Q&A sessions with follow-up support
- Document-grounded answers — no hallucinations from outside the syllabus

---

## ❓ FAQ

**Q: Do I need any API key at all?**
A: No! Select **Question Answer Agent** mode and you can use Study Buddy entirely for free with no external API calls.

**Q: What is LlamaParse and do I need it?**
A: LlamaParse is a cloud-based PDF parser that produces much cleaner output than the default reader, especially for PDFs with tables, multi-column layouts, or structured formatting. It's optional — the app works without it.

**Q: Do I need a GPU?**
A: Not when using Google Gemini or the Question Answer Agent mode. For Ollama fallback, a GPU is optional — Qwen3:4b runs fine on CPU.

**Q: Is there a cost?**
A: Google Gemini has a free tier sufficient for most student use. LlamaCloud also has a free tier. The QA Agent mode is completely free. Ollama is free. Embeddings always run locally for free.

**Q: Can answers go beyond my documents?**
A: No — the system prompt explicitly restricts all responses to uploaded document content only.

**Q: How is my data handled?**
A: Embeddings always happen locally. In Conversational mode with Gemini, query text is sent to Google's API. In QA Agent mode, everything stays on your machine. If using LlamaParse, PDF content is sent to LlamaCloud for parsing.

**Q: Why does the agent rebuild on every question?**
A: The index (the heavy part) is cached — only the lightweight agent wrapper rebuilds per query. This avoids asyncio conflicts when caching async agent objects across Streamlit reruns.

**Q: What happens when I upload new files?**
A: The index, chat history, and memory buffer all reset automatically so there's no contamination from previous documents.

---

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for students who want smarter studying**

⭐ If you find this project helpful, please give it a star!
