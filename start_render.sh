#!/usr/bin/env bash
# Render startup script for Email RAG System

echo "🚀 Starting Email RAG System on Render..."

# Set environment variables for production
export ENVIRONMENT=production
export LOG_LEVEL=INFO

# Start the FastAPI backend
echo "Starting backend API..."
exec uvicorn ingestion_api.main:app --host 0.0.0.0 --port $PORT --workers 1 