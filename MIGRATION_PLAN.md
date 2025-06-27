# Email-RAG to PrivateGPT Migration Plan

## Overview
This document outlines the step-by-step migration plan for integrating the email-RAG functionality into PrivateGPT, replacing Cohere/Gemini embeddings, FAISS vector store, and Cohere generation with PrivateGPT's local Qdrant, Ollama models, and API endpoints.

## Current State
- **Original**: emailragnew (Cohere/Gemini + FAISS + Cohere generation)
- **Target**: privategpt (Qdrant + Ollama + Local models)
- **Status**: Core components copied, ready for integration

## File Structure & Purposes

### Core Components (Already Copied)

#### `frontend/` - Streamlit User Interface
- **Purpose**: Web-based UI for email search, chat, and management
- **Key Files**:
  - `app.py` - Main Streamlit application
  - `persona_viewer.py` - Persona management interface
  - `prompt_manager.py` - Prompt template management
- **Migration Tasks**:
  - Update API endpoints to use PrivateGPT instead of Cohere
  - Modify chat interface to use Ollama models
  - Update search functionality to use Qdrant

#### `ingestion_api/` - Email Processing Pipeline
- **Purpose**: Email ingestion, parsing, and storage
- **Key Files**:
  - `main.py` - FastAPI server for email ingestion
  - `parser.py` - Email parsing and content extraction
  - `persona_extractor.py` - Persona identification from emails
  - `database.py` - Database operations
- **Migration Tasks**:
  - Replace Cohere embeddings with PrivateGPT embeddings
  - Update vector storage to use Qdrant instead of FAISS
  - Modify database schema if needed

#### `rag/` - Retrieval-Augmented Generation
- **Purpose**: Document retrieval and response generation
- **Key Files**:
  - `retriever.py` - Document retrieval from vector store
  - `generator.py` - Response generation using LLMs
  - `embedder.py` - Text embedding generation
  - `prompts.py` - Prompt templates
- **Migration Tasks**:
  - Replace Cohere generation with Ollama models
  - Update retrieval to use Qdrant
  - Modify prompts for local model compatibility

### Supporting Files
- `PRIVATEGPT_README.md` - Comprehensive migration documentation
- `requirements_email_rag.txt` - Email-RAG specific dependencies
- `requirements.txt` - PrivateGPT dependencies

## Migration Phases

### Phase 1: Environment Setup & Dependencies
**Goal**: Set up PrivateGPT environment and resolve dependencies

1. **Install PrivateGPT Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Email-RAG Dependencies**
   ```bash
   pip install -r requirements_email_rag.txt
   ```

3. **Set up PrivateGPT Backend**
   - Install and configure Qdrant
   - Set up Ollama with required models
   - Configure PrivateGPT API endpoints

4. **Environment Configuration**
   - Create `.env` file with PrivateGPT settings
   - Configure database connections
   - Set up logging

### Phase 2: Core Integration
**Goal**: Integrate email processing with PrivateGPT backend

1. **Update Embedding System**
   - Modify `rag/embedder.py` to use PrivateGPT embeddings
   - Test embedding generation and storage

2. **Update Vector Storage**
   - Modify `rag/retriever.py` to use Qdrant
   - Test document retrieval functionality

3. **Update Generation System**
   - Modify `rag/generator.py` to use Ollama models
   - Test response generation

### Phase 3: API Integration
**Goal**: Update ingestion API to use PrivateGPT

1. **Update Ingestion Pipeline**
   - Modify `ingestion_api/parser.py` for PrivateGPT compatibility
   - Update database operations if needed

2. **Test Email Processing**
   - Process sample emails through new pipeline
   - Verify embeddings and storage

### Phase 4: Frontend Integration
**Goal**: Update Streamlit frontend to use PrivateGPT

1. **Update API Calls**
   - Modify `frontend/app.py` to use PrivateGPT endpoints
   - Update chat interface for Ollama models

2. **Test User Interface**
   - Test email search functionality
   - Test chat interface
   - Test persona management

### Phase 5: Testing & Optimization
**Goal**: Comprehensive testing and performance optimization

1. **End-to-End Testing**
   - Test complete email processing pipeline
   - Test search and chat functionality
   - Performance testing

2. **Optimization**
   - Optimize retrieval performance
   - Fine-tune prompts for local models
   - Optimize memory usage

## Getting Started

### Prerequisites
1. **PrivateGPT Setup**
   ```bash
   # Clone and set up PrivateGPT
   git clone https://github.com/nuggetswise/privategpt.git
   cd privategpt
   pip install -r requirements.txt
   ```

2. **Ollama Installation**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull required models
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

3. **Qdrant Setup**
   ```bash
   # Install Qdrant
   docker run -p 6333:6333 qdrant/qdrant
   ```

### First Steps
1. **Start with Phase 1** - Set up the environment
2. **Test PrivateGPT** - Ensure basic functionality works
3. **Begin Phase 2** - Start with embedding integration
4. **Incremental Testing** - Test each component as you modify it

### Development Workflow
1. **Make Changes** - Modify one component at a time
2. **Test Locally** - Test changes before committing
3. **Commit Frequently** - Small, incremental commits
4. **Document Changes** - Update this plan as you progress

## Risk Mitigation

### Backup Strategy
- Original emailragnew remains untouched
- Frequent commits to privategpt repo
- Branch-based development for major changes

### Rollback Plan
- Keep original components as reference
- Maintain compatibility with original API structure
- Document all changes for easy rollback

### Testing Strategy
- Unit tests for each component
- Integration tests for API endpoints
- End-to-end tests for complete workflow

## Success Criteria

### Functional Requirements
- [ ] Email ingestion works with PrivateGPT
- [ ] Search functionality works with Qdrant
- [ ] Chat interface works with Ollama models
- [ ] Persona extraction and management works
- [ ] All original features are preserved

### Performance Requirements
- [ ] Response time < 5 seconds for search
- [ ] Response time < 10 seconds for chat
- [ ] Memory usage optimized for local deployment
- [ ] Scalable to handle large email volumes

### Quality Requirements
- [ ] No data loss during migration
- [ ] Maintained accuracy in search results
- [ ] Preserved chat quality
- [ ] Comprehensive error handling

## Next Actions

### Immediate (Today)
1. Set up PrivateGPT environment
2. Install and configure Ollama
3. Set up Qdrant
4. Test basic PrivateGPT functionality

### Short Term (This Week)
1. Begin Phase 2 integration
2. Update embedding system
3. Test vector storage integration
4. Update generation system

### Medium Term (Next Week)
1. Complete API integration
2. Update frontend
3. Comprehensive testing
4. Performance optimization

## Contact & Support
- Original emailragnew: `/Users/singhm/emailragnew`
- Migration repo: `/Users/singhm/privategpt`
- Documentation: `PRIVATEGPT_README.md`

## Notes
- Always test changes incrementally
- Keep original emailragnew as reference
- Document any deviations from this plan
- Update this document as migration progresses 