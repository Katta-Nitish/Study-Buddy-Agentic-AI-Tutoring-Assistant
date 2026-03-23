# 📚 Study Buddy

> An AI-powered study companion that answers your questions based on your lesson documents using advanced RAG (Retrieval Augmented Generation) techniques.

## 🌟 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **Intelligent RAG System**: Combines vector search and summarization for accurate answers
- **Context-Aware Responses**: All answers are grounded in your uploaded documents
- **Chat Memory**: Maintains conversation history for seamless multi-turn interactions
- **Expert Persona**: Acts as a rigorous Computer Science professor
- **Flexible LLM Backend**: Supports Google Gemini (cloud) or local Ollama as fallback

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- A [Google AI Studio](https://aistudio.google.com/) API key *(recommended)* **OR** [Ollama](https://ollama.ai/) for local inference

### System Requirements

- **RAM**: 4GB minimum (8GB recommended for local Ollama)
- **Storage**: 500MB for cloud setup; 5GB+ if using Ollama locally
- **GPU**: Not required when using Google Gemini (cloud)

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

- **streamlit** - Web UI framework
- **llama-index** - Vector store and RAG framework
- **llama-index-llms-google-genai** - Google Gemini integration
- **llama-index-llms-ollama** - Local Ollama fallback
- **huggingface-hub** - Local embedding model

See `requirements.txt` for the complete list.

## ⚙️ Configuration

### LLM Selection (Priority Order)

Study Buddy automatically selects an LLM in the following order:

| Priority | Source | How |
|----------|--------|-----|
| 1st | User-entered key in sidebar | Enter key at runtime — no setup needed |
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
   - Paste your Google GenAI key in the sidebar input for cloud inference
   - Leave blank to use Ollama locally

3. **Upload your documents**
   - Click on the file uploader
   - Select one or multiple lesson documents (PDF, TXT, or DOCX)
   - Wait for processing to complete

4. **Ask questions**
   - Type your question in the chat input
   - Study Buddy will search and summarize your documents
   - Get detailed, concept-focused answers

## 🛠️ How It Works

### Architecture

```
┌─────────────────────┐
│   Upload Documents  │
└──────────┬──────────┘
           ↓
┌─────────────────────────┐
│  Document Processing    │
│  (PDF/TXT/DOCX Parser)  │
└──────────┬──────────────┘
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
│  FunctionAgent with Tools        │
│  ├─ Vector Tool (Facts)          │
│  └─ Summary Tool (Concepts)      │
└──────────┬───────────────────────┘
           ↓
┌──────────────────────────────────┐
│  LLM Response                    │
│  (Gemini 1.5 Flash / Qwen3:4b)   │
└──────────────────────────────────┘
```

### Key Components

1. **Vector Store Index**: Retrieves specific facts and details using semantic similarity (top-5 results)

2. **Summary Index**: Provides high-level overviews and answers broad questions using the tree-summarize approach

3. **FunctionAgent**: Intelligently selects between vector or summary tools based on query type, with efficient tool execution

4. **Chat Memory**: Maintains conversation context (4000 token limit) for coherent multi-turn discussions

## 🏗️ Architecture Notes

### Key Design Decisions

1. **Google Gemini as Primary LLM**: `gemini-1.5-flash` offers fast, high-quality responses with a generous free tier — ideal for most users without a local GPU.

2. **Runtime API Key Input**: Users can paste their Google GenAI key directly in the sidebar without any file setup, making sharing and deployment frictionless.

3. **Local Ollama Fallback**: If no API key is available, the app gracefully falls back to `qwen3:4b` via Ollama for a fully offline, private experience.

4. **Local Embeddings Always**: The `BAAI/bge-small-en-v1.5` embedding model always runs locally — no API cost or data leakage for document indexing.

5. **FunctionAgent Architecture**: Replaced ReActAgent with FunctionAgent for improved tool selection efficiency and cleaner async execution.

6. **Session State Persistence**:
   - Agent and memory are initialized once per session
   - Survives Streamlit reruns without reprocessing documents
   - Smoother experience across interactions

7. **Optimized Memory**: 4000-token chat memory buffer for context preservation without instability.

---

## 🎯 System Prompt

The agent operates with a specialized system prompt that:

- Restricts answers to document content only
- Encourages concept explanation over simple answers
- Maintains a formal, academic tone
- Redirects off-topic questions back to the syllabus
- Always uses tools to find answers before responding

## 📝 Example Usage

```
User: "Explain neural networks"
↓
Study Buddy: [Searches documents for neural network content]
↓
Response: "Neural networks are computational models inspired by biological neurons. 
According to your lesson, they have the following characteristics:
• Composed of interconnected nodes
• Use activation functions for non-linearity
• [Additional points from your documents...]"
```

## 🔧 Technical Details

### LLM Configuration

| Setting | Value |
|---------|-------|
| Primary Model | `gemini-1.5-flash` (Google GenAI) |
| Fallback Model | `qwen3:4b` (Ollama local) |
| Memory Limit | 4000 tokens |
| Request Timeout (Ollama) | 150 seconds |

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

## 📊 Performance Considerations

- **First Load**: Embedding model download and document indexing may take 1-2 minutes (cached in session)
- **Gemini**: Fast cloud inference, minimal local resource usage
- **Ollama Fallback**: ~2GB RAM for Qwen3:4b; works on CPU without GPU
- **Session Persistence**: Agent and memory survive Streamlit reruns for seamless interactions
- **Scalability**: Suitable for documents up to several hundred pages

### Optimization Tips

- Use your Google GenAI key for the fastest experience
- For large documents, split into 20-30 page chunks for optimal performance
- Subsequent chats are much faster due to caching after the first load

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
- Interactive Q&A sessions
- Document-grounded knowledge base

## ❓ FAQ

**Q: Do I need a GPU?**
A: Not when using Google Gemini. For local Ollama fallback, a GPU is optional — Qwen3:4b runs fine on CPU.

**Q: Is there a cost to use this?**
A: Google Gemini has a free tier that is sufficient for most student use. The embedding model always runs locally for free. Ollama is also fully free.

**Q: Can I use a different Gemini model?**
A: Yes! Modify the `model_name` in the `GoogleGenAI(...)` call in `Study_Buddy.py`. See [Google AI Studio](https://aistudio.google.com/) for available models.

**Q: Is there a limit on document size?**
A: No hard limit, but processing time increases with document size. For best performance, keep documents under 30 pages per upload.

**Q: Can answers go beyond my documents?**
A: No — the system prompt explicitly restricts all responses to uploaded document content only.

**Q: How is my data handled?**
A: Document embedding always happens locally. If using Google Gemini, query text is sent to Google's API. If using Ollama, everything stays on your machine.

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for students who want smarter studying**

⭐ If you find this project helpful, please give it a star!
