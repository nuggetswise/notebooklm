#!/usr/bin/env python3
"""
Debug script to test RAG system and identify issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.email_pipeline import EmailRAGPipeline
from rag.embedder import HybridEmbedder
from rag.retriever import FAISSRetriever
from rag.generator import MultiProviderGenerator
from rag.config import config
import time

def test_rag_system():
    """Test the RAG system step by step."""
    print("🔍 Testing RAG System...")
    
    # Test 1: Check embedder
    print("\n1. Testing Embedder...")
    embedder = HybridEmbedder()
    test_embedding = embedder.embed_single_text("test query")
    print(f"   Embedding generated: {len(test_embedding) if test_embedding else 0} dimensions")
    
    # Test 2: Check retriever
    print("\n2. Testing Retriever...")
    retriever = FAISSRetriever(config.VECTOR_STORE_DIR, embedder)
    print(f"   FAISS index loaded: {retriever.index is not None}")
    print(f"   Documents loaded: {len(retriever.documents)}")
    
    # Test 3: Test search
    print("\n3. Testing Search...")
    search_results = retriever.search("AI trends", k=5)
    print(f"   Search results found: {len(search_results)}")
    for i, result in enumerate(search_results[:3]):
        metadata = result.get('metadata', {})
        subject = metadata.get('subject', 'No subject')
        print(f"   Result {i+1}: {subject}")
    
    # Test 4: Check generator
    print("\n4. Testing Generator...")
    generator = MultiProviderGenerator()
    print(f"   Generator available: {generator.is_available()}")
    print(f"   Groq available: {generator.groq_client is not None}")
    print(f"   Gemini available: {generator.gemini_client is not None}")
    
    # Test 5: Full pipeline test
    print("\n5. Testing Full Pipeline...")
    pipeline = EmailRAGPipeline()
    
    start_time = time.time()
    result = pipeline.query("What are the latest AI trends?", max_age_days=30)
    end_time = time.time()
    
    print(f"   Query time: {end_time - start_time:.2f} seconds")
    print(f"   Provider: {result.get('provider', 'unknown')}")
    print(f"   Model: {result.get('model', 'unknown')}")
    print(f"   Answer length: {len(result.get('answer', ''))}")
    print(f"   Context docs: {len(result.get('context', []))}")
    
    # Show first part of answer
    answer = result.get('answer', '')
    if answer:
        print(f"   Answer preview: {answer[:200]}...")
    else:
        print("   No answer generated!")

if __name__ == "__main__":
    test_rag_system() 