#!/usr/bin/env python3
"""
Test script to demonstrate embedding fallback functionality.
This script tests the hybrid embedder with Cohere primary and Gemini fallback.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embedder import embedder, HybridEmbedder

def test_embedding_fallback():
    """Test the embedding fallback functionality."""
    
    print("🧪 Testing Embedding Fallback System")
    print("=" * 50)
    
    # Test connection status
    print("\n📊 Connection Status:")
    status = embedder.test_connection()
    
    print(f"Cohere Status: {status['cohere']['status']}")
    print(f"Gemini Status: {status['gemini']['status']}")
    print(f"Current Provider: {status['current_provider']}")
    print(f"Overall Status: {status['overall_status']}")
    
    # Test text embedding
    print("\n🔤 Testing Text Embedding:")
    test_texts = [
        "This is a test email about AI trends.",
        "The latest developments in machine learning are fascinating.",
        "Substack newsletters provide great insights on technology."
    ]
    
    try:
        embeddings = embedder.embed_texts(test_texts)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"Provider used: {embedder.get_current_provider()}")
        print(f"First embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        
        # Show sample of first embedding
        if embeddings and embeddings[0]:
            print(f"Sample embedding values: {embeddings[0][:5]}")
            
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
    
    # Test query embedding
    print("\n❓ Testing Query Embedding:")
    test_query = "What are the latest AI trends in 2024?"
    
    try:
        query_embedding = embedder.embed_query(test_query)
        print(f"✅ Generated query embedding")
        print(f"Provider used: {embedder.get_current_provider()}")
        print(f"Query embedding dimension: {len(query_embedding)}")
        
        if query_embedding:
            print(f"Sample query embedding values: {query_embedding[:5]}")
            
    except Exception as e:
        print(f"❌ Error generating query embedding: {e}")
    
    # Test fallback scenarios
    print("\n🔄 Testing Fallback Scenarios:")
    
    # Create a new embedder instance to test fallback
    test_embedder = HybridEmbedder()
    
    # Simulate Cohere failure by temporarily removing the key
    original_cohere_key = os.environ.get('COHERE_API_KEY')
    if original_cohere_key:
        print("Testing fallback to Gemini (simulating Cohere failure)...")
        os.environ['COHERE_API_KEY'] = ''
        
        # Create new embedder without Cohere
        fallback_embedder = HybridEmbedder()
        
        if fallback_embedder.is_available():
            print("✅ Fallback embedder is available")
            test_embedding = fallback_embedder.embed_query("Test query")
            print(f"Fallback provider: {fallback_embedder.get_current_provider()}")
        else:
            print("❌ No fallback providers available")
        
        # Restore original key
        os.environ['COHERE_API_KEY'] = original_cohere_key

def main():
    """Main test function."""
    print("🚀 Email RAG Embedding Fallback Test")
    print("This test demonstrates the hybrid embedding system with Cohere primary and Gemini fallback.")
    
    # Check environment variables
    print("\n🔑 Environment Check:")
    cohere_key = os.getenv('COHERE_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print(f"Cohere API Key: {'✅ Set' if cohere_key else '❌ Not set'}")
    print(f"Gemini API Key: {'✅ Set' if gemini_key else '❌ Not set'}")
    
    if not cohere_key and not gemini_key:
        print("\n⚠️  Warning: No API keys found!")
        print("To test the fallback system, set either COHERE_API_KEY or GEMINI_API_KEY")
        print("You can set them in your .env file or as environment variables.")
        return
    
    # Run the test
    test_embedding_fallback()
    
    print("\n✅ Test completed!")
    print("\n💡 Tips:")
    print("- Set COHERE_API_KEY for primary embedding service")
    print("- Set GEMINI_API_KEY for fallback embedding service")
    print("- The system will automatically use the best available provider")
    print("- If both are available, Cohere will be used as primary")

if __name__ == "__main__":
    main() 