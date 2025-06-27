# 📚 Local RAG System

A completely **free** Retrieval-Augmented Generation (RAG) system that allows you to upload your own documents and ask questions using local models. No API keys required, everything runs on your machine!

## ✨ Features

- 📄 **Multi-format support**: Upload PDF, DOCX, and TXT files
- 🤖 **Local LLM integration**: Uses Ollama for completely free AI responses
- 🔍 **Intelligent retrieval**: Uses sentence-transformers for semantic search
- 💾 **Persistent storage**: ChromaDB vector database with persistence
- 🎨 **Beautiful UI**: Modern Streamlit interface
- 🔒 **Privacy-focused**: Everything runs locally, no data sent to external services
- ⚡ **Fast and efficient**: Optimized chunking and retrieval strategies

## 🛠️ Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Setup Ollama

#### On macOS:
```bash
# Install Ollama
brew install ollama

# Or download from https://ollama.ai
```

#### On Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### On Windows:
Download and install from [ollama.ai](https://ollama.ai)

### 3. Download a Local Model

```bash
# Start Ollama service (if not already running)
ollama serve

# Pull a model (choose one or more)
ollama pull llama2          # ~3.8GB - Good general purpose model
ollama pull mistral         # ~4.1GB - Fast and efficient
ollama pull codellama       # ~3.8GB - Better for code-related questions
ollama pull llama2:13b      # ~7.3GB - More capable but larger
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 How to Use

### 1. Upload Documents
- Use the sidebar to upload PDF, DOCX, or TXT files
- Click "Process Documents" to add them to the knowledge base
- The system will chunk and embed your documents automatically

### 2. Ask Questions
- Once documents are processed, use the main chat interface
- Ask questions about your uploaded documents
- The system will find relevant information and provide answers with sources

### 3. Customize Settings
- **Model Selection**: Choose different Ollama models for different use cases
- **Chunk Size**: Adjust how documents are split (200-1000 tokens)
- **Top K Results**: Control how many relevant chunks to retrieve (1-10)

## 🏗️ System Architecture

```
User Input → Document Processing → Chunking → Embeddings → Vector DB
                                                              ↓
User Question → Query Embedding → Similarity Search → Context → LLM → Response
```

### Components:

1. **Document Processor** (`document_processor.py`)
   - Handles PDF, DOCX, and TXT file extraction
   - Intelligent text chunking with overlap
   - Metadata preservation

2. **RAG System** (`rag_system.py`)
   - Sentence-transformers for embeddings (all-MiniLM-L6-v2)
   - ChromaDB for vector storage
   - Ollama integration for local LLM

3. **Streamlit App** (`app.py`)
   - User-friendly web interface
   - Real-time chat functionality
   - Document management and settings

## 🔧 Configuration

### Embedding Models
The system uses `all-MiniLM-L6-v2` by default (small, fast, good quality). You can modify this in `rag_system.py`:

```python
embedding_model_name = "all-MiniLM-L6-v2"  # Default
# Alternative options:
# "all-mpnet-base-v2"  # Better quality, larger
# "multi-qa-MiniLM-L6-cos-v1"  # Optimized for Q&A
```

### Chunk Settings
Adjust chunking parameters in the UI or modify defaults in `document_processor.py`:

```python
chunk_size = 500        # Tokens per chunk
chunk_overlap = 50      # Overlap between chunks
```

## 📁 Project Structure

```
RAG/
├── app.py                 # Main Streamlit application
├── rag_system.py         # Core RAG functionality
├── document_processor.py # Document processing and chunking
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── chroma_db/           # Persistent vector database (created automatically)
```

## 🚀 Performance Tips

### For Better Speed:
- Use smaller models like `llama2` or `mistral`
- Reduce chunk size for faster processing
- Lower the `top_k` value for fewer retrieved chunks

### For Better Quality:
- Use larger models like `llama2:13b`
- Increase chunk size for more context
- Higher `top_k` value for more comprehensive retrieval

## 🛡️ Privacy & Security

- ✅ **No internet required** for inference (after initial model download)
- ✅ **No API keys** or external services
- ✅ **Data stays local** - documents never leave your machine
- ✅ **Open source** - you can audit all code

## 🐛 Troubleshooting

### Ollama Issues:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve

# Check available models
ollama list
```

### Memory Issues:
- Use smaller models (`llama2` instead of `llama2:13b`)
- Reduce chunk size and top_k values
- Process documents in smaller batches

### Installation Issues:
```bash
# Upgrade pip
pip install --upgrade pip

# Install with no cache
pip install --no-cache-dir -r requirements.txt
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this RAG system!

## 📄 License

This project is open source and available under the MIT License.

---

**Happy RAG-ing!** 🚀📚 