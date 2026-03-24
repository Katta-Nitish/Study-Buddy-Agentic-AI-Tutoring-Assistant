# 📚 Study Buddy

> An AI-powered study companion that answers your questions based on your lesson documents using advanced RAG (Retrieval Augmented Generation) techniques.

## 🌐 Live Demo

**Try it now:** [https://study-buddy-nitish.streamlit.app/](https://study-buddy-nitish.streamlit.app/)

No installation needed — just bring your Google Gemini API key and a lesson document!

---

## 🌟 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **Intelligent RAG System**: Combines vector search and summarization for accurate answers
- **Context-Aware Responses**: All answers are grounded in your uploaded documents
- **RAG Amnesia Fix**: Conversation history is injected into each query so follow-up questions resolve correctly (e.g. *"what happens next?"* understands what came before)
- **Chat Memory**: Maintains conversation history for seamless multi-turn interactions
- **Expert Persona**: Acts as a rigorous academic professor
- **Language Lock**: Always responds in English regardless of the underlying model
- **Flexible LLM Backend**: Supports Google Gemini (cloud) or local Ollama as fallback
- **Smart Cache**: Document index rebuilds only when files change — fast reruns in the same session

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- A [Google AI Studio](https://aistudio.google.com/) API key *(recommended)* **OR** [Ollama](https://ollama.ai/) for local inference

### System Requirements

- **RAM**: 4GB minimum (8GB recommended for local Ollama)
- **Storage**: 500MB for cloud setup; 5GB+ if using Ollama locally
- **GPU**: Not required when using Google Gemini

### Required Models (Ollama fallback only)

If you plan to use Ollama as a fallback, pull the required model:

```bash
ollama pull qwen3:4b
```

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

## 📦 Dependencies

The project uses the following key libraries:

- **streamlit** — Web UI framework
- **llama-index** — Vector store and RAG framework
- **llama-index-llms-google-genai** — Google Gemini integration
- **llama-index-llms-ollama** — Local Ollama fallback
- **huggingface-hub** — Local embedding model

See `requirements.txt` for the complete list.

## ⚙️ Configuration

### LLM Selection (Priority Order)

Study Buddy automatically selects an LLM in the following order:

| Priority | Source | How |
|----------|--------|-----|
| 1st | User-entered key in sidebar | Paste key at runtime — no setup needed |
| 2nd | `st.secrets["GEMINI_API_KEY"]` | Set in `.streamlit/secrets.toml` for deployment |
| 3rd | Local Ollama (fallback) | Runs `qwen3:4b` if no key is available |

---

### Option 1: Google Gemini (Recommended)

#### Step 1: Get a Google GenAI API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **Get API Key** → **Create API Key**
4. Copy and save the key securely

#### Step 2: Run and Enter Key in Sidebar

Start the app and paste your key directly into the sidebar input at runtime:

```bash
streamlit run Study_Buddy.py
```

No `.env` or secrets file needed for quick local use.

#### Step 3 (Optional): Set a Persistent Key via Streamlit Secrets

For deployment or to avoid re-entering the key every session, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

The app will automatically pick this up as the second priority.

---

### Option 2: Local Ollama (Fallback / Offline)

If no API key is provided, Study Buddy falls back to a local Ollama model. Ensure Ollama is running:

```bash
ollama serve
```

The default local model is `qwen3:4b`. Pull it if not already available:

```bash
ollama pull qwen3:4b
```

---

### Embedding Model

Study Buddy always uses a **local HuggingFace embedding model** — no API cost for document reading:

- **Model**: `BAAI/bge-small-en-v1.5`
- **Type**: Sentence-BERT
- **Dimensions**: 384
- **Cost**: Free (runs locally)

---

### Setup Comparison

| Aspect | Google Gemini | Local Ollama |
|--------|--------------|--------------|
| **Cost** | Free tier available | Free (local compute) |
| **Speed** | Fast (cloud) | Depends on hardware |
| **Privacy** | Data sent to Google | 100% local |
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

2. **Enter your API key** *(optional)*
   - Paste your Google Gemini key in the sidebar for cloud inference
   - Leave blank to use Ollama locally

3. **Upload your documents**
   - Click on the file uploader
   - Select one or multiple lesson documents (PDF, TXT, or DOCX)
   - The index builds once and is cached — reruns are instant

4. **Ask questions**
   - Type your question in the chat input
   - Follow-up questions work correctly thanks to the RAG Amnesia Fix
   - All answers are sourced strictly from your uploaded documents

## 🛠️ How It Works

### Architecture

```
┌─────────────────────┐
│   Upload Documents  │
└──────────┬──────────┘
           ↓
┌──────────────────────────────────┐
│  Document Processing             │
│  (PDF/TXT/DOCX Parser)           │
│  Cached by file name + size key  │
└──────────┬───────────────────────┘
           ↓
┌──────────────────────────────────┐
│  Text Chunking & Embedding       │
│  (SentenceSplitter + BGE-Small)  │
└──────────┬───────────────────────┘
           ↓
┌──────────────────────────────────┐
│  Dual Index Creation             │
│  ├─ Vector Index (Semantic)      │
│  └─ Summary Index (Overview)     │
└──────────┬───────────────────────┘
           ↓
┌──────────────────────────────────┐
│  RAG Amnesia Fix                 │
│  (Last 4 messages injected into  │
│   the prompt for context)        │
└──────────┬───────────────────────┘
           ↓
┌──────────────────────────────────┐
│  ReActAgent with Tools           │
│  ├─ vector_tool (Facts)          │
│  └─ summary_tool (Overviews)     │
└──────────┬───────────────────────┘
           ↓
┌──────────────────────────────────┐
│  LLM Response                    │
│  (Gemini 1.5 Flash / Qwen3:4b)   │
└──────────────────────────────────┘
```

### Key Components

1. **Vector Store Index**: Retrieves specific facts and details using semantic similarity (top-5 results)

2. **Summary Index**: Provides high-level overviews of the entire document using the tree-summarize approach; runs in sync mode (`use_async=False`) for Streamlit thread safety

3. **ReActAgent**: Reasons step-by-step and selects between the vector tool (specific questions) or summary tool (broad overviews) based on query type

4. **RAG Amnesia Fix**: The last 4 messages from the Streamlit chat history are prepended to every new prompt so the agent can resolve follow-up questions and pronouns correctly — even when the underlying LLM has no persistent memory

5. **File Change Detection**: A cache key derived from file names and sizes triggers a full reset of the chat history and memory buffer when new files are uploaded

## 🏗️ Architecture Notes

### Key Design Decisions

1. **Google Gemini as Primary LLM**: `gemini-1.5-flash` offers fast, high-quality responses with a generous free tier — ideal for most users without a local GPU.

2. **ReActAgent**: Uses step-by-step reasoning to decide which tool to call, making it more reliable for multi-hop and follow-up queries than a function-calling approach.

3. **Decoupled Index and Agent**: `build_index` is `@st.cache_resource` (rebuilds only when files change), while `build_agent` is intentionally *not* cached — this avoids asyncio event loop conflicts that arise when caching async objects across Streamlit reruns.

4. **Memory via Session State**: `ChatMemoryBuffer` is stored in `st.session_state` rather than inside the cached agent, so it persists across reruns without requiring the agent to be re-cached.

5. **RAG Amnesia Fix**: Rather than relying solely on the memory buffer (which can be truncated), the last 4 conversation turns are explicitly injected into the prompt. This ensures follow-ups like *"explain the second point further"* are resolved with the correct context.

6. **Language Lock**: The system prompt explicitly instructs the model to always respond in English, preventing multilingual models (like Qwen) from switching languages mid-conversation.

7. **Local Embeddings Always**: The `BAAI/bge-small-en-v1.5` embedding model always runs locally — no API cost or data leakage for document indexing.

---

## 🎯 System Prompt Design

The agent is instructed to:

- Always call `vector_tool` for every question, including follow-ups, with a precise query that reflects the current question in full context
- For follow-up questions, include the specific topic from the prior turn in the tool query
- Never answer from memory alone — always retrieve fresh context via tools
- Use `summary_tool` only for broad document overviews, not specific questions
- Explain concepts clearly using bullet points
- Redirect off-topic questions back to the syllabus firmly
- Maintain a formal, academic, yet encouraging tone
- Always respond in English (Language Lock)

## 📝 Example Usage

```
User: "Explain mitosis"
↓
Agent: [Calls vector_tool("mitosis")] → retrieves relevant content
↓
Response: "Mitosis is the process by which a cell divides into two identical daughter cells.
According to your lesson:
• Phase 1 — Prophase: chromosomes condense...
• Phase 2 — Metaphase: chromosomes align...
..."

User: "What happens after that?"
↓
Agent: [Sees injected history → calls vector_tool("mitosis phases after metaphase")]
↓
Response: "Following metaphase, the next stages are..."
```

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

### Embedding Model

| Setting | Value |
|---------|-------|
| Model | `BAAI/bge-small-en-v1.5` |
| Type | Sentence-BERT |
| Dimensions | 384 |
| Runs | Locally (no API cost) |

### Document Processing

| Setting | Value |
|---------|-------|
| Chunk Size | 1024 tokens |
| Splitter | SentenceSplitter |
| Supported Formats | PDF, TXT, DOCX |
| Vector Top-K | 5 |
| Index Caching | By file name + size key |
| Context Window (history) | Last 4 messages |

## 📊 Performance Considerations

- **First Load**: Embedding model download and document indexing may take 1-2 minutes (cached for the rest of the session)
- **File Change**: Uploading new files resets the index, memory, and chat history automatically
- **Gemini**: Fast cloud inference, minimal local resource usage
- **Ollama Fallback**: ~2GB RAM for Qwen3:4b; works on CPU without GPU
- **Follow-up Questions**: Handled efficiently via the RAG Amnesia Fix without extra API calls

### Optimization Tips

- Use your Google Gemini key for the fastest experience
- For large documents, split into 20-30 page chunks for optimal performance
- Subsequent questions in the same session are much faster due to index caching

## 🐛 Troubleshooting

### Issue: "Connection refused" (Ollama fallback)
**Solution**: Ensure Ollama is running:
```bash
ollama serve
```

### Issue: Gemini model not responding
**Solution**: Verify your API key is valid at [Google AI Studio](https://aistudio.google.com/). Ensure you have quota remaining on your free tier.

### Issue: Model not found (Ollama)
**Solution**: Pull the required model:
```bash
ollama pull qwen3:4b
```

### Issue: Agent gives wrong answer to follow-up questions
**Solution**: This is handled automatically by the RAG Amnesia Fix. If it persists, try rephrasing the follow-up with more context (e.g. *"what happens after mitosis metaphase?"* instead of *"what happens next?"*).

### Issue: Slow responses
**Solution**:
- Switch to Google Gemini (enter your API key in the sidebar)
- If using Ollama, check available RAM — Qwen3:4b needs ~2GB free

### Issue: Out of memory (Ollama)
**Solution**:
- Close other applications
- Alternatively, switch to Google Gemini to avoid local memory usage entirely

## 📚 Project Structure

```
study-buddy/
├── Study_Buddy.py          # Main application file
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .streamlit/
│   └── secrets.toml        # Optional: persistent Gemini API key
└── .gitignore              # Git ignore file
```

## 🎓 Educational Context

This project was designed for students to enhance learning through:

- Self-paced revision of lesson materials
- Instant clarification of concepts
- Interactive Q&A sessions with follow-up support
- Document-grounded knowledge base

## ❓ FAQ

**Q: Do I need a GPU?**
A: Not when using Google Gemini. For local Ollama fallback, a GPU is optional — Qwen3:4b runs fine on CPU.

**Q: Is there a cost to use this?**
A: Google Gemini has a free tier sufficient for most student use. The embedding model always runs locally for free. Ollama is also fully free.

**Q: Can I use a different Gemini model?**
A: Yes! Modify the `model_name` in the `GoogleGenAI(...)` call in `Study_Buddy.py`. See [Google AI Studio](https://aistudio.google.com/) for available models.

**Q: Is there a limit on document size?**
A: No hard limit, but processing time increases with document size. For best performance, keep documents under 30 pages per upload.

**Q: Can answers go beyond my documents?**
A: No — the system prompt explicitly restricts all responses to uploaded document content only.

**Q: How is my data handled?**
A: Document embedding always happens locally. If using Google Gemini, query text is sent to Google's API. If using Ollama, everything stays on your machine.

**Q: Why does the agent rebuild on every question?**
A: The index (the heavy part) is cached — only the lightweight agent wrapper rebuilds per query. This design avoids asyncio conflicts that occur when caching async agent objects across Streamlit reruns.

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for students who want smarter studying**

⭐ If you find this project helpful, please give it a star!
