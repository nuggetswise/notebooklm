# 📧 Email RAG Assistant

A complete AI-powered system for processing auto-forwarded emails and running RAG-based Q&A via a modern Streamlit interface.

## 🔒 CRITICAL SECURITY NOTICE

**⚠️ IMPORTANT: API Key Security**

This application requires API keys for AI services. To protect your credentials:

1. **NEVER commit API keys to git** - The `.env` file is ignored by git
2. **Use the template**: Copy `env.template` to `.env` and fill in your keys
3. **Keep keys secure**: Don't share your `.env` file or expose keys in logs
4. **Rotate keys regularly**: If keys are ever exposed, regenerate them immediately

```bash
# Safe setup (DO THIS)
cp env.template .env
# Edit .env with your real API keys

# NEVER DO THIS
git add .env  # ❌ This would expose your keys!
```

**Required API Keys:**
- `COHERE_API_KEY` - For embeddings and generation
- `GROQ_API_KEY` - For fast LLM responses  
- `GEMINI_API_KEY` - For Google AI services
- `OPENAI_API_KEY` - For OpenAI services (optional)

## 🏗️ System Architecture

The system consists of three main components:

1. **FastAPI Backend** (`ingestion_api/`) - Email ingestion and processing
2. **RAG Pipeline** (`rag/`) - Document retrieval and question answering
3. **Streamlit Frontend** (`frontend/`) - NotebookLM-style user interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment
- Cohere API key (optional, for enhanced embeddings and generation)

### Installation

1. **Clone and setup:**
```bash
git clone <repository>
cd emailragnew
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment setup:**
```bash
cp env.example .env
# Edit .env and add your Cohere API key if available
```

3. **Start the complete system:**
```bash
python start_system.py
```

This will start both the backend API (port 8001) and frontend UI (port 8501).

## 🌐 Access Points

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 📋 Features

### Email Processing
- ✅ MIME email parsing with Python's email module
- ✅ Attachment processing (PDFs via PyMuPDF, images via OCR)
- ✅ Email filtering by label and date range
- ✅ SQLite metadata storage
- ✅ Local file storage for parsed content

### RAG Pipeline
- ✅ Document chunking with LangChain
- ✅ Cohere embeddings (with fallback to text search)
- ✅ FAISS vector similarity search
- ✅ LLM-powered answer generation
- ✅ Context-aware responses with source documents

### User Interface
- ✅ Modern Streamlit interface with NotebookLM-style design
- ✅ Real-time chat interface
- ✅ Email label filtering
- ✅ Date range selection
- ✅ Source document viewing
- ✅ System status monitoring

## 🔧 API Endpoints

### Email Processing
- `POST /inbound-email` - Receive and process MIME emails
- `GET /emails` - List emails with filtering
- `GET /labels` - Get available email labels
- `GET /status` - System status and statistics

### RAG Querying
- `POST /query` - Query the RAG system with questions

## 📁 Project Structure

```
emailragnew/
├── ingestion_api/          # FastAPI backend
│   ├── main.py            # API endpoints and email processing
│   ├── parser.py          # MIME email parsing
│   ├── database.py        # SQLite operations
│   └── models.py          # Pydantic models
├── rag/                   # RAG pipeline
│   ├── email_pipeline.py  # Main RAG orchestration
│   ├── embedder.py        # Cohere embeddings
│   ├── retriever.py       # FAISS retrieval
│   ├── generator.py       # LLM answer generation
│   └── document_source.py # Document loading
├── frontend/              # Streamlit frontend
│   ├── app.py            # Main UI application
│   └── requirements.txt  # Frontend dependencies
├── data/                  # Data storage
│   ├── parsed_emails/    # Parsed email content
│   ├── maildir/          # Raw email storage
│   └── email_index.db    # SQLite metadata
├── tests/                # Test suite
├── start_system.py       # Complete system startup
├── run_frontend.py       # Frontend-only startup
└── requirements.txt      # Main dependencies
```

## 🔄 Email Forwarding Setup

To receive emails automatically, configure your email provider to forward emails to the API endpoint:

```
POST http://your-server:8001/inbound-email
Content-Type: message/rfc822
```

You can use services like:
- **Gmail**: Set up forwarding rules
- **Outlook**: Configure mail flow rules
- **SMTP2HTTP**: For custom email providers

## 🧪 Testing

Run the test suite:

```