#!/bin/bash
# Render build script for Email RAG System

set -e  # Exit on any error

echo "🚀 Starting Render build process..."

# Install dependencies using our optimized requirements
echo "📦 Installing dependencies..."
pip install -r requirements_render.txt

# Verify critical packages
echo "🔍 Verifying installation..."
python -c "import numpy, pandas, fastapi, uvicorn, streamlit, sentence_transformers, faiss, cohere, openai; print('✅ All critical packages imported successfully')"

# Create necessary directories
echo "📁 Setting up directories..."
mkdir -p data/vector_store
mkdir -p data/parsed_emails

# Set permissions
chmod +x deploy_to_render.py

echo "✅ Build completed successfully!" 