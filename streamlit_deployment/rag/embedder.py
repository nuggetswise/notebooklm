import numpy as np
from typing import List, Dict, Any, Optional
import cohere
from .config import settings

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
                
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
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
            response = self.client.embed(
                texts=[query],
                model=self.model,
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

# Global embedder instance
embedder = CohereEmbedder() 