#!/bin/bash

# Quick fix for production deployment issues
echo "🔧 Fixing production deployment..."

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ Not in virtual environment. Creating one..."
    python3 -m venv venv_production
    source venv_production/bin/activate
fi

# Install missing dependencies
echo "📦 Installing missing dependencies..."

# Core dependencies
pip install fastapi uvicorn pydantic

# AI providers
pip install cohere groq google-generativeai openai

# Email processing
pip install beautifulsoup4 python-multipart

# Document processing
pip install PyMuPDF pytesseract Pillow pdfminer.six

# RAG components
pip install sentence-transformers numpy

# Frontend
pip install streamlit

# Vector database
pip install faiss-cpu

# Utilities
pip install python-dotenv requests pandas

# LangChain
pip install langchain langchain-core langchain-community langchain-text-splitters langchain-openai

# Test the installation
echo "🧪 Testing installation..."
python -c "
try:
    import fastapi
    print('✅ FastAPI installed')
except ImportError:
    print('❌ FastAPI missing')

try:
    import groq
    print('✅ Groq installed')
except ImportError:
    print('❌ Groq missing')

try:
    import cohere
    print('✅ Cohere installed')
except ImportError:
    print('❌ Cohere missing')

try:
    import google.generativeai as genai
    print('✅ Google Generative AI installed')
except ImportError:
    print('❌ Google Generative AI missing')

try:
    import streamlit
    print('✅ Streamlit installed')
except ImportError:
    print('❌ Streamlit missing')

print('🎉 Installation test complete!')
"

echo "✅ Production fix completed!"
echo ""
echo "To start the system:"
echo "source venv_production/bin/activate"
echo "uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001" 