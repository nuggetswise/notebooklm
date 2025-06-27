#!/usr/bin/env python3
"""
Test script to verify the new fallback chain: Groq (Gemma2 9B) → Gemini → Cohere
"""

import requests
import json
import time

def test_fallback_chain():
    """Test the new fallback chain configuration."""
    print("🚀 Testing New Fallback Chain: Groq (Gemma2 9B) → Gemini → Cohere")
    print("=" * 70)
    
    test_queries = [
        "What is artificial intelligence?",
        "What are the latest AI developments?",
        "How does machine learning work?",
        "What are the main AI topics in the emails?",
        "Explain AI trends in 2025"
    ]
    
    results = []
    providers_used = set()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔄 Test #{i}: {query[:50]}...")
        print("-" * 50)
        
        payload = {
            "question": query,
            "sender": None
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8001/query",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                provider = result.get('provider', 'unknown')
                model = result.get('model', 'unknown')
                processing_time = result.get('processing_time', 0)
                answer_length = len(result.get('answer', ''))
                
                print(f"   ✅ Provider: {provider}")
                print(f"   🎯 Model: {model}")
                print(f"   ⏱️  Time: {processing_time:.2f}s")
                print(f"   📝 Answer length: {answer_length} chars")
                
                providers_used.add(provider)
                results.append({
                    'test': i,
                    'query': query,
                    'provider': provider,
                    'model': model,
                    'time': processing_time,
                    'answer_length': answer_length
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FALLBACK CHAIN ANALYSIS")
    print("=" * 70)
    
    print(f"Total tests: {len(results)}")
    print(f"Providers used: {', '.join(providers_used)}")
    
    # Count provider usage
    provider_counts = {}
    for result in results:
        provider = result['provider']
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
    
    print(f"\nProvider Usage:")
    for provider, count in provider_counts.items():
        percentage = (count / len(results)) * 100
        print(f"   {provider}: {count}/{len(results)} ({percentage:.1f}%)")
    
    # Check if Groq is being used as primary
    groq_usage = provider_counts.get('groq', 0)
    if groq_usage == len(results):
        print(f"\n🎉 SUCCESS: Groq (Gemma2 9B) is being used as primary for all queries!")
    elif groq_usage > 0:
        print(f"\n⚠️  Groq is being used for {groq_usage}/{len(results)} queries")
    else:
        print(f"\n❌ Groq is not being used - check configuration")
    
    # Show model breakdown
    print(f"\nModel Breakdown:")
    model_counts = {}
    for result in results:
        model = result['model']
        model_counts[model] = model_counts.get(model, 0) + 1
    
    for model, count in model_counts.items():
        percentage = (count / len(results)) * 100
        print(f"   {model}: {count}/{len(results)} ({percentage:.1f}%)")
    
    return results

def test_specific_groq_models():
    """Test if specific Groq models are being used."""
    print("\n🔬 Testing Groq Model Selection")
    print("=" * 50)
    
    # Test multiple queries to see which Groq model is used
    for i in range(3):
        print(f"\nTest {i+1}:")
        payload = {
            "question": f"What is AI? (test {i+1})",
            "sender": None
        }
        
        try:
            response = requests.post(
                "http://localhost:8001/query",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                provider = result.get('provider', 'unknown')
                model = result.get('model', 'unknown')
                
                print(f"   Provider: {provider}")
                print(f"   Model: {model}")
                
                if provider == 'groq':
                    if 'gemma2-9b' in model:
                        print("   ✅ Using Gemma2 9B (primary)")
                    elif 'llama-4-scout' in model:
                        print("   ⚠️  Using Llama 4 Scout (fallback)")
                    elif 'llama-3.3-70b' in model:
                        print("   ⚠️  Using Llama 3.3 70B (fallback)")
                    else:
                        print(f"   ℹ️  Using {model}")
                else:
                    print(f"   ⚠️  {provider.upper()} was used instead of Groq")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # Test the fallback chain
    test_fallback_chain()
    
    # Test specific Groq models
    test_specific_groq_models() 