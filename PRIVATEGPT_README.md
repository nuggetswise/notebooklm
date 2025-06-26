# 🔒 Private-GPT Email RAG Assistant

A **100% private** AI-powered email assistant that processes your emails locally using [Private-GPT](https://github.com/zylon-ai/private-gpt) as the backend. No data leaves your machine - everything runs locally with Ollama models and Qdrant vector storage.

## 🎯 Overview

This project refactors the existing Email RAG Assistant to use Private-GPT as the sole backend for:
- **Document Ingestion**: Automatic email processing via Private-GPT's `/v1/ingest` endpoint
- **Vector Storage**: Local Qdrant database for persistent embeddings
- **Text Generation**: Local LLM inference via Ollama (Mistral-7B, Llama2, etc.)
- **Retrieval**: Semantic search with local embeddings

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  Private-GPT     │    │   Email Source  │
│   (Port 8501)   │◄──►│  (Port 8001)     │◄──►│   ~/Emails/     │
│                 │    │                  │    │                 │
│ • File Upload   │    │ • /v1/ingest     │    │ • .eml files    │
│ • Chat Interface│    │ • /v1/retrieve   │    │ • Auto-saved    │
│ • Email Browser │    │ • /v1/chat       │    │ • ~100/day      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Local Storage  │
                       │                  │
                       │ • Qdrant DB      │
                       │ • Ollama Models  │
                       │ • Document Store │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (for Private-GPT)
- **Python 3.8+** (for Streamlit frontend)
- **8GB+ RAM** (for local LLM inference)
- **Mac M1/M2/M3** or **Linux x86_64** (recommended)

### 1. Install Private-GPT

```bash
# Clone Private-GPT
git clone https://github.com/zylon-ai/private-gpt.git
cd private-gpt

# Start with Docker Compose
docker-compose up -d

# Verify it's running
curl http://localhost:8001/health
```

### 2. Setup Ollama Models

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull mistral:7b-instruct
ollama pull llama2:7b-chat

# Test model
ollama run mistral:7b-instruct "Hello, world!"
```

### 3. Configure Private-GPT

Create `private-gpt/settings.yaml`:

```yaml
llm:
  mode: ollama
  ollama:
    base_url: http://host.docker.internal:11434
    model: mistral:7b-instruct

embedding:
  mode: local
  local:
    model: sentence-transformers/all-MiniLM-L6-v2

vectorstore:
  mode: qdrant
  qdrant:
    host: qdrant
    port: 6333
    collection_name: privategpt

data:
  local_data_folder: ./local_data
  database:
    mode: local
    local:
      database_path: ./local_data/database.db
```

### 4. Install Email RAG Frontend

```bash
# Clone this repository
git clone <your-repo>
cd emailragnew

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the frontend
python run_frontend.py
```

## 📧 Email Setup

### Automatic Email Forwarding

1. **Create email directory:**
```bash
mkdir ~/Emails
```

2. **Setup email forwarding** (example for Gmail):
   - Go to Gmail Settings → Filters and Blocked Addresses
   - Create filter for newsletters
   - Forward to: `your-server:8001/inbound-email`

3. **Email watcher script** (optional):
```bash
# Monitor ~/Emails/ for new .eml files
python scripts/email_watcher.py
```

### Manual Email Upload

Use the Streamlit interface to upload `.eml` files directly through the file uploader.

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Private-GPT Configuration
PRIVATEGPT_URL=http://localhost:8001
PRIVATEGPT_API_KEY=your_api_key_if_configured

# Email Configuration
EMAIL_WATCH_DIR=~/Emails
EMAIL_BATCH_SIZE=10
EMAIL_MAX_AGE_DAYS=365

# Frontend Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0

# Model Configuration
OLLAMA_MODEL=mistral:7b-instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Private-GPT Settings

Key settings in `private-gpt/settings.yaml`:

```yaml
# LLM Configuration
llm:
  mode: ollama
  ollama:
    model: mistral:7b-instruct
    temperature: 0.1
    max_tokens: 2048

# Embedding Configuration
embedding:
  mode: local
  local:
    model: sentence-transformers/all-MiniLM-L6-v2
    dimension: 384

# Vector Store Configuration
vectorstore:
  mode: qdrant
  qdrant:
    collection_name: email_rag
    distance_metric: cosine

# Document Processing
data:
  chunk_size: 512
  chunk_overlap: 50
  max_file_size: 10485760  # 10MB
```

## 🔄 Migration from Current System

### Phase 1: Data Migration

```bash
# Export existing emails
python scripts/export_emails.py

# Convert to Private-GPT format
python scripts/convert_to_privategpt.py

# Import to Private-GPT
python scripts/import_to_privategpt.py
```

### Phase 2: API Integration

The frontend automatically switches to Private-GPT endpoints:

- **Ingestion**: `POST /v1/ingest`
- **Retrieval**: `POST /v1/retrieve`
- **Chat**: `POST /v1/chat`

### Phase 3: Testing

```bash
# Test ingestion
curl -X POST http://localhost:8001/v1/ingest \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_email.eml"

# Test chat
curl -X POST http://localhost:8001/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What emails did I receive about AI?"}'
```

## 📊 Performance Optimization

### Memory Management

```yaml
# Private-GPT settings for Mac M3
llm:
  ollama:
    num_ctx: 2048  # Reduce context window
    num_thread: 8  # Limit CPU threads

embedding:
  local:
    device: cpu  # Use CPU for embeddings
```

### Batch Processing

```python
# Process emails in batches
BATCH_SIZE = 10
MAX_CONCURRENT_REQUESTS = 3
```

### Caching Strategy

- **Embedding Cache**: Local file cache for repeated queries
- **Response Cache**: Redis/Memory cache for common questions
- **Model Cache**: Ollama model persistence

## 🔍 Troubleshooting

### Common Issues

1. **Private-GPT won't start:**
```bash
# Check Docker logs
docker-compose logs private-gpt

# Verify ports
netstat -an | grep 8001
```

2. **Ollama model not found:**
```bash
# List available models
ollama list

# Pull missing model
ollama pull mistral:7b-instruct
```

3. **Memory issues:**
```bash
# Monitor memory usage
htop

# Reduce model size
ollama pull llama2:7b-chat-q4_K_M  # Quantized version
```

4. **Email ingestion fails:**
```bash
# Check file permissions
ls -la ~/Emails/

# Test API endpoint
curl -X POST http://localhost:8001/v1/ingest \
  -F "file=@test_email.eml"
```

### Performance Monitoring

```bash
# Monitor system resources
docker stats

# Check Private-GPT logs
docker-compose logs -f private-gpt

# Monitor email processing
tail -f logs/email_processing.log
```

## 🧪 Testing

### Unit Tests

```bash
# Test Private-GPT integration
python -m pytest tests/test_privategpt_integration.py

# Test email processing
python -m pytest tests/test_email_processing.py

# Test frontend
python -m pytest tests/test_frontend.py
```

### Load Testing

```bash
# Test with 500+ emails
python scripts/load_test.py --email-count 500

# Test concurrent users
python scripts/concurrent_test.py --users 10
```

## 🔒 Security & Privacy

### Data Privacy

- ✅ **100% Local Processing**: No data leaves your machine
- ✅ **Local Vector Storage**: Qdrant database on your hardware
- ✅ **Local LLM Inference**: Ollama models run locally
- ✅ **No External APIs**: All processing done locally

### Security Features

- **API Authentication**: Optional API key protection
- **File Validation**: Email content validation
- **Rate Limiting**: Request throttling
- **Input Sanitization**: XSS protection

## 📈 Scaling Considerations

### For Large Email Volumes (1000+ emails)

1. **Use Larger Models:**
```bash
ollama pull llama2:13b-chat
ollama pull mistral:7b-instruct-q4_K_M
```

2. **Optimize Vector Storage:**
```yaml
vectorstore:
  qdrant:
    collection_name: email_rag_large
    optimizers_config:
      memmap_threshold: 10000
```

3. **Batch Processing:**
```python
# Process emails in larger batches
BATCH_SIZE = 50
MAX_WORKERS = 4
```

### For Multiple Users

1. **Load Balancing:**
```yaml
# Docker Compose with multiple instances
services:
  private-gpt-1:
    ports:
      - "8001:8001"
  private-gpt-2:
    ports:
      - "8002:8001"
```

2. **Shared Storage:**
```yaml
# Use shared volume for Qdrant
volumes:
  - ./shared_data:/app/local_data
```

## 🎯 Usage Examples

### 1. Basic Email Query
```
Question: "What emails did I receive about project updates?"
Response: [Local LLM generates response with citations]
```

### 2. Advanced Filtering
```
Question: "Show me AI newsletters from the last week"
Response: [Filtered results with date range]
```

### 3. Document Search
```
Question: "Find emails with PDF attachments about budgets"
Response: [Search across content and metadata]
```

## 🔄 Development Workflow

### Adding New Features

1. **New Email Processors:**
```python
# Extend Private-GPT document processors
class EmailDocumentProcessor(BaseDocumentProcessor):
    def process(self, file_path: str) -> List[Document]:
        # Custom email processing logic
        pass
```

2. **Custom RAG Components:**
```python
# Extend Private-GPT retrievers
class EmailRetriever(BaseRetriever):
    def retrieve(self, query: str) -> List[Document]:
        # Custom retrieval logic
        pass
```

3. **UI Enhancements:**
```python
# Add new Streamlit components
def email_dashboard():
    st.title("Email Dashboard")
    # Custom dashboard logic
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📚 Additional Resources

- [Private-GPT Documentation](https://docs.privategpt.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🤝 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: [Project Wiki](link-to-wiki)

---

**Built with ❤️ for privacy-first AI email processing** 