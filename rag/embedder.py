import numpy as np
from typing import List, Dict, Any, Optional
import cohere
import google.generativeai as genai
from .config import settings

class GeminiEmbedder:
    """Google Gemini embedding integration as fallback."""
    
    def __init__(self):
        self.client = None
        self.model = "models/embedding-001"  # Gemini's embedding model
        
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.client = genai.GenerativeModel('gemini-pro')
                print(f"✅ Gemini client initialized with model: {self.model}")
            except Exception as e:
                print(f"❌ Error initializing Gemini client: {e}")
                self.client = None
        else:
            print("⚠️ GEMINI_API_KEY not set. Gemini fallback disabled.")
    
    def is_available(self) -> bool:
        """Check if Gemini client is available."""
        return self.client is not None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Gemini."""
        if not self.is_available():
            print("Warning: Gemini client not available.")
            return []
        
        try:
            embeddings = []
            for text in texts:
                # Use Gemini's embedding model
                embedding = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(embedding['embedding'])
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating Gemini embeddings: {e}")
            return []
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query using Gemini."""
        if not self.is_available():
            print("Warning: Gemini client not available.")
            return []
        
        try:
            embedding = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query"
            )
            
            return embedding['embedding']
            
        except Exception as e:
            print(f"Error generating Gemini query embedding: {e}")
            return []

class CohereEmbedder:
    """Cohere embedding integration for email documents."""
    
    def __init__(self):
        self.client = None
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        
        if settings.COHERE_API_KEY:
            try:
                self.client = cohere.Client(settings.COHERE_API_KEY)
                print(f"✅ Cohere client initialized with model: {self.model}")
            except Exception as e:
                print(f"❌ Error initializing Cohere client: {e}")
                self.client = None
        else:
            print("⚠️ COHERE_API_KEY not set. Embedding functionality disabled.")
    
    def is_available(self) -> bool:
        """Check if Cohere client is available."""
        return self.client is not None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not self.is_available():
            print("Warning: Cohere client not available. Returning empty embeddings.")
            return [[0.0] * self.dimension] * len(texts)
        
        try:
            # Batch process texts
            batch_size = 100  # Cohere's recommended batch size
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Use the correct method signature for Cohere v4.37
                response = self.client.embed(
                    texts=batch,
                    input_type="search_document"
                )
                
                batch_embeddings = response.embeddings
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * self.dimension] * len(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        if not self.is_available():
            print("Warning: Cohere client not available. Returning zero embedding.")
            return [0.0] * self.dimension
        
        try:
            # Use the correct method signature for Cohere v4.37
            response = self.client.embed(
                texts=[query],
                input_type="search_query"
            )
            
            return response.embeddings[0]
            
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return [0.0] * self.dimension
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Cohere connection and return status."""
        if not self.is_available():
            return {
                'status': 'error',
                'message': 'Cohere client not available',
                'model': self.model,
                'dimension': self.dimension
            }
        
        try:
            # Test with a simple embedding
            test_text = "This is a test embedding."
            embedding = self.embed_query(test_text)
            
            return {
                'status': 'success',
                'message': 'Cohere connection successful',
                'model': self.model,
                'dimension': self.dimension,
                'test_embedding_length': len(embedding),
                'test_embedding_sample': embedding[:5] if embedding else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Cohere connection failed: {str(e)}',
                'model': self.model,
                'dimension': self.dimension
            }

class HybridEmbedder:
    """Hybrid embedder with Cohere primary and Gemini fallback."""
    
    def __init__(self):
        self.cohere_embedder = CohereEmbedder()
        self.gemini_embedder = GeminiEmbedder()
        self.current_provider = "cohere" if self.cohere_embedder.is_available() else "gemini" if self.gemini_embedder.is_available() else "none"
        
        print(f"🔧 Hybrid embedder initialized with primary provider: {self.current_provider}")
    
    def is_available(self) -> bool:
        """Check if any embedding provider is available."""
        return self.current_provider != "none"
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with fallback logic."""
        # Try Cohere first
        if self.cohere_embedder.is_available():
            try:
                embeddings = self.cohere_embedder.embed_texts(texts)
                if embeddings and any(len(emb) > 0 for emb in embeddings):
                    self.current_provider = "cohere"
                    return embeddings
            except Exception as e:
                print(f"Cohere embedding failed, trying Gemini: {e}")
        
        # Fallback to Gemini
        if self.gemini_embedder.is_available():
            try:
                embeddings = self.gemini_embedder.embed_texts(texts)
                if embeddings and any(len(emb) > 0 for emb in embeddings):
                    self.current_provider = "gemini"
                    print("🔄 Using Gemini embeddings as fallback")
                    return embeddings
            except Exception as e:
                print(f"Gemini embedding also failed: {e}")
        
        # Last resort: return zero embeddings
        print("⚠️ All embedding providers failed. Using zero embeddings.")
        dimension = self.cohere_embedder.get_embedding_dimension()
        return [[0.0] * dimension] * len(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Generate query embedding with fallback logic."""
        # Try Cohere first
        if self.cohere_embedder.is_available():
            try:
                embedding = self.cohere_embedder.embed_query(query)
                if embedding and len(embedding) > 0:
                    self.current_provider = "cohere"
                    return embedding
            except Exception as e:
                print(f"Cohere query embedding failed, trying Gemini: {e}")
        
        # Fallback to Gemini
        if self.gemini_embedder.is_available():
            try:
                embedding = self.gemini_embedder.embed_query(query)
                if embedding and len(embedding) > 0:
                    self.current_provider = "gemini"
                    print("🔄 Using Gemini query embedding as fallback")
                    return embedding
            except Exception as e:
                print(f"Gemini query embedding also failed: {e}")
        
        # Last resort: return zero embedding
        print("⚠️ All embedding providers failed. Using zero embedding.")
        dimension = self.cohere_embedder.get_embedding_dimension()
        return [0.0] * dimension
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.cohere_embedder.get_embedding_dimension()
    
    def get_current_provider(self) -> str:
        """Get the current embedding provider being used."""
        return self.current_provider
    
    def test_connection(self) -> Dict[str, Any]:
        """Test all embedding connections and return status."""
        cohere_status = self.cohere_embedder.test_connection()
        gemini_status = {
            'status': 'success' if self.gemini_embedder.is_available() else 'error',
            'message': 'Gemini available' if self.gemini_embedder.is_available() else 'Gemini not available',
            'model': 'models/embedding-001'
        }
        
        return {
            'cohere': cohere_status,
            'gemini': gemini_status,
            'current_provider': self.current_provider,
            'overall_status': 'success' if self.is_available() else 'error'
        }

# Global embedder instance - now uses hybrid approach
embedder = HybridEmbedder() 