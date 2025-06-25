# AI-Powered Email Processing & RAG System - Project Plan

## 📋 Project Overview

Building a complete, modular AI-powered system for processing auto-forwarded emails and running RAG-based Q&A via a Streamlit UI. The system consists of three main components working together to create a seamless email intelligence platform.

### 🎯 Core Objectives
- **Email Ingestion**: Automatically receive and process auto-forwarded emails via SMTP
- **Content Extraction**: Parse MIME emails, extract text from attachments (PDFs, images)
- **Intelligent Q&A**: Build a RAG system for querying email content with context
- **User Interface**: Create a NotebookLM-style Streamlit interface for email exploration

---

## 🏗️ System Architecture

### **Component 1: FastAPI Email Ingestion Backend**
**Purpose**: Receive, parse, and store auto-forwarded emails with full attachment processing

**Key Responsibilities**:
- Accept raw MIME emails via HTTP POST from smtp2http
- Parse email content (subject, sender, date, body)
- Extract text from attachments (PDFs via OCR, images via OCR)
- Filter emails based on labels and date ranges
- Store parsed content and maintain metadata

**Technical Stack**:
- **Framework**: FastAPI with Pydantic validation
- **Email Processing**: Python `email` module + BeautifulSoup
- **Document Processing**: PyMuPDF (PDFs), pytesseract (OCR)
- **Storage**: Local file system + SQLite database
- **Filtering**: Label-based + configurable date ranges

### **Component 2: Verba RAG Backend**
**Purpose**: Process email documents and provide intelligent Q&A capabilities

**Key Responsibilities**:
- Load and chunk parsed email documents
- Generate embeddings using Cohere
- Implement semantic search with FAISS
- Generate grounded responses using LLMs
- Filter documents by label and recency

**Technical Stack**:
- **Document Processing**: Custom email document source
- **Embeddings**: Cohere `embed-english-v3.0`
- **Vector Store**: FAISS for similarity search
- **Generation**: Cohere `command-r` or OpenAI
- **Chunking**: 2000-char chunks with 10% overlap

### **Component 3: Streamlit Frontend**
**Purpose**: Provide an intuitive NotebookLM-style interface for email Q&A

**Key Responsibilities**:
- Display available email labels and metadata
- Accept user queries with label context
- Present generated answers with supporting context
- Show email metadata and source information
- Provide expandable context sections

**Technical Stack**:
- **Framework**: Streamlit for rapid UI development
- **Styling**: Custom CSS for NotebookLM aesthetic
- **API Integration**: HTTP requests to FastAPI backend
- **State Management**: Streamlit session state

---

## 📁 File Structure

```
emailragnew/
├── ingestion_api/           # FastAPI Email Processing
│   ├── __init__.py
│   ├── main.py              # FastAPI app with endpoints
│   ├── parser.py            # MIME parsing & attachment processing
│   ├── models.py            # Pydantic data models
│   ├── database.py          # SQLite operations
│   └── config.py            # Configuration settings
├── rag/                     # RAG Pipeline
│   ├── __init__.py
│   ├── email_pipeline.py    # Main RAG orchestration
│   ├── document_source.py   # Email document loader
│   ├── embedder.py          # Cohere embedding integration
│   ├── retriever.py         # FAISS retrieval system
│   ├── generator.py         # LLM response generation
│   └── config.py            # RAG configuration
├── frontend/                # Streamlit UI
│   ├── __init__.py
│   ├── app.py               # Main Streamlit application
│   ├── components.py        # Reusable UI components
│   └── api_client.py        # FastAPI communication
├── data/                    # Data Storage
│   ├── parsed_emails/       # Clean text files for RAG
│   ├── maildir/             # Raw MIME storage
│   └── email_index.db       # SQLite metadata database
├── tests/                   # Testing Suite
│   ├── test_ingestion.py
│   ├── test_rag.py
│   └── test_frontend.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment configuration template
├── README.md               # Setup and usage documentation
└── docker-compose.yml      # Containerization (optional)
```

---

## 🔧 Technical Implementation Details

### **Email Processing Pipeline**

1. **SMTP Reception**:
   - Configure smtp2http to listen on port 8025
   - Forward all emails to `POST /inbound-email` endpoint
   - Accept raw MIME content as multipart/form-data

2. **MIME Parsing**:
   ```python
   # Extract email components
   - Subject, From, Date headers
   - Plain text body (primary)
   - HTML body (fallback, stripped with BeautifulSoup)
   - Attachments (PDFs, images, documents)
   ```

3. **Content Extraction**:
   ```python
   # PDF Processing
   - Use PyMuPDF for text extraction
   - Fallback to pdfminer.six if needed
   
   # Image Processing
   - Use pytesseract for OCR
   - Support common formats (PNG, JPG, TIFF)
   
   # Text Processing
   - Clean and normalize extracted text
   - Append to email body for RAG processing
   ```

4. **Filtering Logic**:
   ```python
   # Label-based filtering
   - Check subject line for "Label: X" pattern
   - Check email headers for X-Label
   - Configurable default label via environment
   
   # Date-based filtering
   - Only process emails within MAX_AGE_DAYS
   - Configurable via environment variable
   ```

### **RAG Pipeline Architecture**

1. **Document Loading**:
   ```python
   class EmailDocumentSource:
       def load_documents(self, label: str, max_age_days: int):
           # Load from ./data/parsed_emails/
           # Filter by label and date from SQLite
           # Return list of Document objects
   ```

2. **Chunking Strategy**:
   ```python
   # Chunk Configuration
   - Size: 2000 characters
   - Overlap: 200 characters (10%)
   - Preserve email boundaries
   - Include metadata in chunks
   ```

3. **Embedding & Retrieval**:
   ```python
   # Embedding Process
   - Use Cohere embed-english-v3.0
   - Batch processing for efficiency
   - Store in FAISS index
   
   # Retrieval Process
   - Semantic search with FAISS
   - Return top-5 most relevant chunks
   - Include similarity scores
   ```

4. **Response Generation**:
   ```python
   # Prompt Template
   Context:
   {retrieved_chunks}
   
   Question: {user_query}
   
   Answer: [Generate grounded response]
   ```

### **API Endpoints Design**

```python
# FastAPI Endpoints
POST /inbound-email
- Accept: multipart/form-data
- Body: Raw MIME email content
- Response: Processing status and email ID

GET /status
- Query params: label, max_age_days
- Response: List of email metadata

GET /email/{id}/content
- Response: Full parsed email content

POST /refresh
- Reprocess emails from maildir
- Response: Processing summary

# RAG Endpoints
POST /query
- Body: {"question": str, "label": str}
- Response: {"answer": str, "context": list, "metadata": list}
```

---

## 🚀 Implementation Phases

### **Phase 1: Core Infrastructure (Week 1)**
**Goals**: Set up foundation and email processing capabilities

**Tasks**:
1. ✅ Project structure setup
2. 🔄 Update requirements.txt with all dependencies
3. 🔄 Create configuration system (.env handling)
4. 🔄 Implement FastAPI email ingestion backend
5. 🔄 Build MIME parsing and attachment processing
6. 🔄 Set up SQLite database for email metadata
7. 🔄 Create basic testing framework

**Deliverables**:
- Working email ingestion API
- MIME parsing with attachment support
- Database schema and operations
- Basic test coverage

### **Phase 2: RAG Pipeline (Week 2)**
**Goals**: Implement intelligent document processing and Q&A

**Tasks**:
1. 🔄 Design email document source
2. 🔄 Implement document chunking strategy
3. 🔄 Set up Cohere embeddings integration
4. 🔄 Build FAISS retrieval system
5. 🔄 Create LLM response generation
6. 🔄 Implement query_email_docs function
7. 🔄 Add comprehensive RAG testing

**Deliverables**:
- Complete RAG pipeline
- Document processing and embedding
- Semantic search capabilities
- Response generation system

### **Phase 3: Streamlit Frontend (Week 3)**
**Goals**: Create intuitive user interface for email exploration

**Tasks**:
1. 🔄 Design NotebookLM-style UI layout
2. 🔄 Implement label selection sidebar
3. 🔄 Build query interface and response display
4. 🔄 Create context visualization components
5. 🔄 Add email metadata display
6. 🔄 Integrate with FastAPI and RAG backend
7. 🔄 Implement error handling and loading states

**Deliverables**:
- Complete Streamlit application
- User-friendly interface
- Real-time Q&A capabilities
- Context and metadata visualization

### **Phase 4: Integration & Polish (Week 4)**
**Goals**: System integration, optimization, and deployment readiness

**Tasks**:
1. 🔄 End-to-end system integration
2. 🔄 Performance optimization
3. 🔄 Error handling and edge cases
4. 🔄 Security considerations
5. 🔄 Documentation and deployment guide
6. 🔄 Optional Docker containerization
7. 🔄 Final testing and validation

**Deliverables**:
- Production-ready system
- Comprehensive documentation
- Deployment instructions
- Performance benchmarks

---

## 🔍 Key Technical Decisions

### **Email Processing Choices**
- **MIME Parser**: Python's built-in `email` module (reliable, well-tested)
- **PDF Processing**: PyMuPDF over pdfminer.six (better performance, more features)
- **OCR Engine**: pytesseract (mature, widely supported)
- **HTML Stripping**: BeautifulSoup (robust, handles edge cases)

### **RAG Architecture Decisions**
- **Chunking**: 2000-char chunks with 10% overlap (optimal for email content)
- **Embeddings**: Cohere embed-english-v3.0 (high quality, fast)
- **Vector Store**: FAISS (fast, memory-efficient)
- **Retrieval**: Top-5 chunks (good balance of context vs. noise)

### **Storage Strategy**
- **File System**: Parsed emails as .txt files (human-readable, debuggable)
- **Database**: SQLite (lightweight, no external dependencies)
- **Backup**: Raw MIME in maildir format (smtp2http compatible)

### **UI/UX Design Principles**
- **NotebookLM Style**: Clean, focused interface with sidebar navigation
- **Real-time Feedback**: Loading states and progress indicators
- **Context Visualization**: Expandable sections for retrieved content
- **Responsive Design**: Works on desktop and tablet

---

## 📊 Success Metrics & Validation

### **Functionality Metrics**
- ✅ Successfully parse and store auto-forwarded emails
- ✅ Extract text from various attachment types (PDFs, images)
- ✅ Filter emails by label and date range
- ✅ Generate accurate, grounded responses to email queries
- ✅ Provide intuitive user interface for email exploration

### **Performance Targets**
- ⚡ Email processing: < 5 seconds per email (including attachments)
- ⚡ RAG query response: < 3 seconds end-to-end
- ⚡ UI responsiveness: < 1 second for interactions
- ⚡ Memory usage: < 2GB for typical email volumes

### **Quality Assurance**
- 🧪 Unit test coverage: > 80% for core components
- 🧪 Integration test coverage: All major workflows
- 🧪 Error handling: Graceful degradation for edge cases
- 🧪 Security: Input validation and sanitization

---

## 🔧 Environment Configuration

### **Required Environment Variables**
```env
# API Keys
COHERE_API_KEY=your_cohere_api_key
OPENAI_API_KEY=optional_openai_key

# Email Processing
MAX_AGE_DAYS=30
DEFAULT_LABEL=AI
SMTP2HTTP_PORT=8025

# RAG Settings
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5

# Storage Paths
DATA_DIR=./data
PARSED_EMAILS_DIR=./data/parsed_emails
MAILDIR_DIR=./data/maildir

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### **Dependencies to Add**
```txt
# Core Framework
fastapi
uvicorn
pydantic
email-validator

# Email Processing
beautifulsoup4
python-multipart

# Document Processing
PyMuPDF
pytesseract
Pillow
pdfminer.six

# RAG Components
sentence-transformers
numpy

# Development
pytest
black
flake8
```

---

## 🚨 Risk Mitigation

### **Technical Risks**
1. **OCR Accuracy**: Implement fallback strategies and confidence scoring
2. **API Rate Limits**: Add retry logic and rate limiting for Cohere
3. **Memory Usage**: Implement streaming for large email volumes
4. **File System Limits**: Add cleanup and archival strategies

### **Operational Risks**
1. **Email Volume**: Implement queuing and batch processing
2. **Data Privacy**: Add encryption and access controls
3. **System Reliability**: Implement health checks and monitoring
4. **Scalability**: Design for horizontal scaling if needed

---

## 📚 Documentation Plan

### **Technical Documentation**
- API reference with examples
- Database schema documentation
- Configuration guide
- Deployment instructions

### **User Documentation**
- Setup and installation guide
- Usage examples and best practices
- Troubleshooting guide
- FAQ section

### **Developer Documentation**
- Architecture overview
- Contributing guidelines
- Testing procedures
- Code style guide

---

## 🎯 Next Steps

1. **Review and approve this plan**
2. **Set up development environment**
3. **Begin Phase 1 implementation**
4. **Establish regular progress reviews**
5. **Iterate based on testing feedback**

This plan provides a comprehensive roadmap for building a production-ready email RAG system that's modular, maintainable, and extensible. Each phase builds upon the previous one, ensuring robust integration and testing throughout the development process. 