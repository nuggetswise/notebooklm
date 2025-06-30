#!/usr/bin/env python3
"""
Script to rebuild the FAISS index with new embeddings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.email_pipeline import EmailRAGPipeline
from rag.document_source import EmailDocumentSource
from rag.config import config
import time

def rebuild_index():
    """Rebuild the FAISS index with new embeddings."""
    print("🔨 Rebuilding FAISS Index...")
    
    # Initialize the pipeline
    pipeline = EmailRAGPipeline()
    
    # Force rebuild the index
    print("📚 Loading documents...")
    document_source = EmailDocumentSource()
    documents = document_source.load_documents()
    
    print(f"📄 Found {len(documents)} documents")
    
    if not documents:
        print("❌ No documents found. Please ensure emails are processed first.")
        return False
    
    # Rebuild the index
    print("🔧 Building FAISS index...")
    start_time = time.time()
    
    success = pipeline.retriever.build_index(
        documents=documents,
        force_rebuild=True,
        show_progress=True
    )
    
    end_time = time.time()
    
    if success:
        print(f"✅ Index rebuilt successfully in {end_time - start_time:.2f} seconds")
        print(f"📊 Index stats: {pipeline.retriever.get_index_stats()}")
        return True
    else:
        print("❌ Failed to rebuild index")
        return False

if __name__ == "__main__":
    rebuild_index() 