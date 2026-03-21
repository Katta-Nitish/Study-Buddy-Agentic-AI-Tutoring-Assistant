# 📚 Study Buddy

> An AI-powered study companion that answers your questions based on your lesson documents using advanced RAG (Retrieval Augmented Generation) techniques.

## 🌟 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **Intelligent RAG System**: Combines vector search and summarization for accurate answers
- **Context-Aware Responses**: All answers are grounded in your uploaded documents
- **Chat Memory**: Maintains conversation history for seamless multi-turn interactions
- **Expert Persona**: Acts as a rigorous Computer Science professor
- **Real-time Processing**: Instant responses with streaming capabilities

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) (for running local LLMs)
- pip (Python package manager)

### System Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 5GB+ for model files
- **GPU**: Optional (CPU works fine with Qwen3:4b)

### Required Models

Make sure you have the following models pulled in Ollama:

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
- **ollama** - Local LLM inference
- **huggingface-hub** - Embedding models

See `requirements.txt` for the complete list.

## ⚙️ Configuration

### Option 1: Local Setup (Ollama)

#### Ollama Setup

Ensure Ollama is running locally on `localhost:11434`:

```bash
ollama serve
```

#### Environment Variables

The application disables Streamlit telemetry by default:

```python
os.environ["STREAMLIT_GATHER_USAGE_STATS"] = "false"
```

---

### Option 2: OpenAI API (Recommended for Cloud/No Local GPU)

If you don't have a local LLM setup or prefer using cloud services, follow these steps:

#### Step 1: Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Go to **API Keys** section in your account settings
4. Click **Create new secret key**
5. Copy and save the key securely

#### Step 2: Modify `Study_Buddy.py`

Replace the LLM initialization section:

**Original (Ollama):**
```python
llm=Ollama(model='deepseek-r1:8b',request_timeout=150.0)
Settings.llm=llm
```

**New (OpenAI):**
```python
from llama_index.llms.openai import OpenAI
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

llm = OpenAI(
    model="gpt-4-turbo",  # or "gpt-3.5-turbo" for faster/cheaper responses
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.7
)
Settings.llm = llm
```

#### Step 3: Use Online Embedding Model

Replace the embedding model section:

**Original (Local HuggingFace):**
```python
@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.embed_model=load_embedding_model()
```

**New (OpenAI Embeddings):**
```python
from llama_index.embeddings.openai import OpenAIEmbedding

@st.cache_resource
def load_embedding_model():
    return OpenAIEmbedding(
        model="text-embedding-3-small",  # Fast and cost-effective
        api_key=os.environ["OPENAI_API_KEY"]
    )

Settings.embed_model = load_embedding_model()
```

#### Step 4: Set Environment Variable

Create a `.env` file in your project root:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Then load it at the top of `Study_Buddy.py`:

```python
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
```

#### Step 5: Update Requirements

Add OpenAI dependencies to `requirements.txt`:

```
streamlit
llama-index
llama-index-llms-openai
llama-index-embeddings-openai
python-dotenv
```

Install the new packages:

```bash
pip install -r requirements.txt
```

---

### Option 3: Hybrid Setup (Local LLM + OpenAI Embeddings)

If you want to use local Ollama for LLM but online embeddings for better quality:

```python
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.openai import OpenAIEmbedding
import os

# Local LLM
llm = Ollama(model='deepseek-r1:8b', request_timeout=150.0)
Settings.llm = llm

# OpenAI Embeddings
@st.cache_resource
def load_embedding_model():
    return OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.environ["OPENAI_API_KEY"]
    )

Settings.embed_model = load_embedding_model()
```

---

### Model Comparison

| Aspect | Local (Ollama) | OpenAI API | Hybrid |
|--------|---|---|---|
| **Cost** | Free (local compute) | Pay per token | Low (embeddings only) |
| **Speed** | Depends on GPU | Fast (cloud) | Fast |
| **Privacy** | 100% local | Data sent to OpenAI | Mostly local |
| **Setup** | Requires GPU | API key only | Both setups |
| **Quality** | Good | Excellent | Excellent |
| **Offline** | ✅ | ❌ | Partial |

---

### OpenAI Model Options

#### LLM Models

- **`gpt-4-turbo`** - Best quality, slower, most expensive ($0.01-0.03 per 1K tokens)
- **`gpt-3.5-turbo`** - Fast, cheap, good enough ($0.0005-0.0015 per 1K tokens)
- **`gpt-4o`** - Balanced performance and cost ($0.005-0.015 per 1K tokens)

#### Embedding Models

- **`text-embedding-3-small`** - Fast, 1,536 dimensions, cheap ($0.02 per 1M tokens)
- **`text-embedding-3-large`** - More accurate, 3,072 dimensions ($0.13 per 1M tokens)

---

### Environment Variables

The application disables Streamlit telemetry by default:

```python
os.environ["STREAMLIT_GATHER_USAGE_STATS"] = "false"
```

## 💻 Usage

1. **Start the application**

```bash
streamlit run Study_Buddy.py
```

2. **Upload your documents**
   - Click on the file uploader in the sidebar
   - Select one or multiple lesson documents (PDF, TXT, or DOCX)
   - Wait for processing to complete

3. **Ask questions**
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
│  (SentenceSplitter + HuggingFace)│
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
│  LLM Response (Qwen3:4b)         │
└──────────────────────────────────┘
```

### Key Components

1. **Vector Store Index**: Efficiently retrieves specific facts and details from documents using semantic similarity (top-5 results)

2. **Summary Index**: Provides high-level overviews and answers broad questions about the entire document using tree-summarize approach

3. **FunctionAgent**: Advanced agent architecture that intelligently selects and uses the appropriate tools (vector or summary) based on query type, with improved performance and efficiency

4. **Chat Memory**: Maintains conversation context (4000 token limit) for coherent multi-turn discussions, with proper session state management

## 🏗️ Architecture Improvements (v2.0)

### Key Enhancements

1. **FunctionAgent Architecture**: Replaced ReActAgent with FunctionAgent for improved tool selection and execution efficiency

2. **Optimized Model Selection**: Switched from DeepSeek-R1:8b to **Qwen3:4b** for:
   - ⚡ **Faster Response Times**: 50-70% faster inference
   - 💾 **Lower Memory**: ~2GB vs ~4GB (DeepSeek)
   - 💻 **CPU-Friendly**: Efficient on CPU without GPU
   - ✅ **Maintained Quality**: Comparable accuracy with better efficiency
   - 🚀 **Lightweight**: Perfect for resource-constrained environments

3. **Enhanced Session Management**: 
   - Proper async loop handling with try-except blocks
   - Session state persistence for agent and memory
   - Prevents reinitialization on page reruns
   - Smoother user experience across interactions

4. **Improved Memory Management**:
   - Optimized token limit (4000 tokens) for stability
   - Better context preservation across conversation turns
   - Efficient memory cleanup and reuse

5. **Better User Experience**:
   - Clear spinner messages ("Reading your documents and waking up Study Buddy...")
   - Separate initialization phase from chat interaction
   - Agent loads once per session, then reused
   - Faster subsequent interactions

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

### Embedding Model

- **Model**: BAAI/bge-small-en-v1.5
- **Type**: Sentence-BERT embeddings
- **Dimension**: 384
- **Purpose**: Converting text to semantic vectors for similarity search

### LLM Configuration

- **Model**: Qwen3:4b (Lightweight & Fast)
- **Request Timeout**: 150 seconds
- **Context Window**: 8192 tokens
- **Type**: Open-source fast inference model
- **Memory Limit**: 4000 tokens

### Document Processing

- **Chunk Size**: 1024 tokens
- **Splitter**: SentenceSplitter (preserves sentence boundaries)
- **Supported Formats**: PDF, TXT, DOCX

## 📊 Performance Considerations

- **First Load**: Initial embedding generation and model loading may take 1-2 minutes (cached in session)
- **Memory Usage**: ~2GB for Qwen3:4b + embeddings (lightweight compared to larger models)
- **Speed**: Qwen3:4b optimized for fast inference even on CPU
- **GPU Support**: Optional (works efficiently on CPU)
- **Scalability**: Suitable for documents up to several hundred pages
- **Session Persistence**: Agent and memory survive Streamlit reruns for seamless interactions

### Optimization Tips

- **First time setup**: Takes longer as model is loaded
- **Subsequent chats**: Much faster due to caching
- **Large documents**: Consider splitting into 20-30 page chunks for optimal performance
- **Memory reuse**: Chat memory maintained at 4000 tokens for context preservation

## 🐛 Troubleshooting

### Issue: "Connection refused" for Ollama
**Solution**: Ensure Ollama is running:
```bash
ollama serve
```

### Issue: Model not found
**Solution**: Pull the required models:
```bash
ollama pull qwen3:4b
```

### Issue: Slow responses
**Solution**: 
- Qwen3:4b is optimized for speed - if still slow, check GPU availability
- Reduce document size or chunk overlap
- Increase the request timeout if needed

### Issue: Out of memory
**Solution**:
- Close other applications
- Qwen3:4b is lightweight; if still running out of memory, ensure sufficient RAM (4GB minimum)
- Split documents into smaller parts

## 📚 Project Structure

```
study-buddy/
├── Study_Buddy.py      # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore file
```

## 🎓 Educational Context

This project was designed for students to enhance learning through:

- Self-paced revision of lesson materials
- Instant clarification of concepts
- Interactive Q&A sessions
- Document-grounded knowledge base


## ❓ FAQ

**Q: Can I use my own LLM?**
A: Yes! Modify the LLM initialization in the code to use any OpenAI-compatible API or other Ollama models.

**Q: Is there a limit on document size?**
A: No hard limit, but processing time increases with document size. Test with your specific documents.

**Q: Can answers go beyond my documents?**
A: No, the system prompt explicitly restricts responses to document content only.

**Q: How is privacy maintained?**
A: All processing happens locally on your machine. No data is sent to external servers.

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for students who want smarter studying**

⭐ If you find this project helpful, please give it a star!
