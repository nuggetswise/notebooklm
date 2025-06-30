import os
import logging
from typing import List, Dict, Optional, Any
from functools import lru_cache
import time
import numpy as np
from sentence_transformers import SentenceTransformer
import cohere  # Uncommented since we have API key
import google.generativeai as genai
import google.ai.generativelanguage as glm
from .config import config

logger = logging.getLogger(__name__)

class SentenceTransformersEmbedder:
    """Sentence Transformers embedding integration for free, local embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        
        try:
            print(f"🔄 Loading Sentence Transformers model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✅ Sentence Transformers loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            print(f"❌ Error loading Sentence Transformers model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Sentence Transformers model is available."""
        return self.model is not None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not self.is_available():
            print("Warning: Sentence Transformers model not available. Returning empty embeddings.")
            return [[0.0] * self.dimension] * len(texts)
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Convert to list of lists
            if len(embeddings.shape) == 1:
                embeddings = [embeddings.tolist()]
            else:
                embeddings = embeddings.tolist()
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating Sentence Transformers embeddings: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * self.dimension] * len(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        if not self.is_available():
            print("Warning: Sentence Transformers model not available. Returning zero embedding.")
            return [0.0] * self.dimension
        
        try:
            # Generate embedding
            embedding = self.model.encode([query], convert_to_tensor=False)
            
            # Convert to list
            if len(embedding.shape) == 1:
                return embedding.tolist()
            else:
                return embedding[0].tolist()
            
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return [0.0] * self.dimension
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Sentence Transformers connection and return status."""
        if not self.is_available():
            return {
                'status': 'error',
                'message': 'Sentence Transformers model not available',
                'model': self.model_name,
                'dimension': self.dimension
            }
        
        try:
            # Test with a simple embedding
            test_text = "This is a test embedding."
            embedding = self.embed_query(test_text)
            
            return {
                'status': 'success',
                'message': 'Sentence Transformers connection successful',
                'model': self.model_name,
                'dimension': self.dimension,
                'test_embedding_length': len(embedding),
                'test_embedding_sample': embedding[:5] if embedding else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Sentence Transformers connection failed: {str(e)}',
                'model': self.model_name,
                'dimension': self.dimension
            }

class GeminiEmbedder:
    """Google Gemini embedding integration as fallback."""
    
    def __init__(self):
        self.client = None
        self.model = "models/embedding-001"  # Gemini's embedding model
        
        if config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                # For embeddings, we need to use the Google AI client directly
                import google.ai.generativelanguage as glm
                self.client = glm.EmbeddingServiceClient()
                print(f"✅ Gemini embedding client initialized with model: {self.model}")
            except Exception as e:
                print(f"❌ Error initializing Gemini embedding client: {e}")
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
                # Use Gemini's embedding model with correct API
                request = glm.EmbedTextRequest(
                    model=self.model,
                    text=text
                )
                response = self.client.embed_text(request)
                embeddings.append(response.embedding.values)
            
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
            request = glm.EmbedTextRequest(
                model=self.model,
                text=query
            )
            response = self.client.embed_text(request)
            return response.embedding.values
            
        except Exception as e:
            print(f"Error generating Gemini query embedding: {e}")
            return []

class CohereEmbedder:
    """Cohere embedding integration for email documents."""
    
    def __init__(self):
        self.client = None
        self.model = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIMENSION
        
        if config.COHERE_API_KEY:
            try:
                self.client = cohere.Client(config.COHERE_API_KEY)
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

class NomicEmbedder:
    """Nomic AI embedding integration supporting both remote (Atlas API) and local inference."""
    def __init__(self):
        import requests
        self.requests = requests
        self.model = "nomic-embed-text-v1.5"
        self.dimension = 768
        self.api_key = os.getenv('ATLAS_KEY')
        self.base_url = "https://atlas.nomic.ai/api/v1"
        
        # Auto-detect inference mode
        self.inference_mode = os.getenv('NOMIC_INFERENCE_MODE')
        if not self.inference_mode:
            self.inference_mode = 'remote' if self.api_key else 'local'
        print(f"[NomicEmbedder] Using inference_mode: {self.inference_mode}")
        
        # For local mode, use the Python client
        if self.inference_mode == 'local':
            from nomic import embed
            self.embed = embed
    
    def is_available(self) -> bool:
        if self.inference_mode == 'remote':
            return self.api_key is not None
        return True  # Local mode always available if nomic is installed
    
    def embed_texts(self, texts: list) -> list:
        if self.inference_mode == 'remote':
            return self._embed_texts_remote(texts)
        else:
            return self._embed_texts_local(texts)
    
    def embed_query(self, query: str) -> list:
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else []
    
    def _embed_texts_remote(self, texts: list) -> list:
        """Use direct HTTP API with API key authentication."""
        if not self.api_key:
            print("Error: ATLAS_KEY not set for remote mode")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "texts": texts,
                "model": self.model,
                "task_type": "search_document",
                "dimensionality": self.dimension
            }
            
            response = self.requests.post(
                f"{self.base_url}/embed/text",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embeddings', [])
            else:
                print(f"Error generating Nomic embeddings: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error generating Nomic embeddings: {e}")
            return []
    
    def _embed_texts_local(self, texts: list) -> list:
        """Use local Nomic client."""
        try:
            output = self.embed.text(
                texts=texts,
                model=self.model,
                task_type='search_document',
                inference_mode='local',
                dimensionality=self.dimension
            )
            return output['embeddings']
        except Exception as e:
            print(f"Error generating Nomic local embeddings: {e}")
            return []

class HybridEmbedder:
    """Hybrid embedder with Nomic (local/remote) primary, OpenAI fallback, then Sentence Transformers."""
    def __init__(self, primary_provider: str = "nomic", fallback_provider: str = "openai", 
                 cache_size: int = 1000, dimension: int = 768):
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.dimension = dimension
        self.cache_size = cache_size
        # Initialize embedders
        self.nomic_embedder = NomicEmbedder()
        self.openai_client = None
        self.sentence_transformers_client = None
        self.cohere_client = None
        self.gemini_client = None
        self.stats = {
            'nomic_embeddings': 0,
            'openai_embeddings': 0,
            'sentence_transformers_embeddings': 0,
            'cohere_embeddings': 0,
            'gemini_embeddings': 0,
            'fallback_used': 0,
            'cache_hits': 0,
            'total_requests': 0
        }
        self._initialize_clients()
    def _initialize_clients(self):
        # OpenAI fallback
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                import openai
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized with model: text-embedding-3-small")
            else:
                logger.warning("⚠️ OPENAI_API_KEY not found")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        # Sentence Transformers fallback
        try:
            from sentence_transformers import SentenceTransformer
            self.sentence_transformers_client = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence Transformers client initialized with model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Sentence Transformers client: {e}")
        # Cohere (legacy)
        try:
            api_key = os.getenv('COHERE_API_KEY')
            if api_key:
                self.cohere_client = cohere.Client(api_key)
                logger.info("✅ Cohere client initialized (legacy)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cohere client: {e}")
        # Gemini (legacy)
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('models/embedding-001')
                logger.info("✅ Gemini client initialized (legacy)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
    @lru_cache(maxsize=1000)
    def _get_cached_embedding(self, text: str, provider: str) -> Optional[List[float]]:
        return None
    def _cache_embedding(self, text: str, embedding: List[float], provider: str):
        pass
    def embed_texts(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        if not texts:
            return []
        self.stats['total_requests'] += 1
        # Try Nomic first
        embeddings = self._embed_with_nomic(texts, use_cache)
        if embeddings:
            self.stats['nomic_embeddings'] += len(texts)
            return embeddings
        # Fallback to OpenAI
        embeddings = self._embed_with_openai(texts, use_cache)
        if embeddings:
            self.stats['openai_embeddings'] += len(texts)
            self.stats['fallback_used'] += 1
            return embeddings
        # Fallback to Sentence Transformers
        embeddings = self._embed_with_sentence_transformers(texts, use_cache)
        if embeddings:
            self.stats['sentence_transformers_embeddings'] += len(texts)
            self.stats['fallback_used'] += 1
            return embeddings
        logger.warning("⚠️ All embedding providers failed, returning zero embeddings")
        return [[0.0] * self.dimension] * len(texts)
    def _embed_with_nomic(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        try:
            return self.nomic_embedder.embed_texts(texts)
        except Exception as e:
            logger.error(f"❌ Nomic embedding error: {e}")
            return None
    def _embed_with_openai(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        if not self.openai_client:
            return None
        try:
            all_embeddings = []
            for text in texts:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                embedding_values = response.data[0].embedding
                all_embeddings.append(embedding_values)
            return all_embeddings
        except Exception as e:
            logger.error(f"❌ OpenAI embedding error: {e}")
            return None
    def _embed_with_sentence_transformers(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        if not self.sentence_transformers_client:
            return None
        try:
            all_embeddings = []
            for text in texts:
                embedding = self.sentence_transformers_client.encode([text], convert_to_tensor=False)
                embedding_values = embedding[0].tolist()
                all_embeddings.append(embedding_values)
            return all_embeddings
        except Exception as e:
            logger.error(f"❌ Sentence Transformers embedding error: {e}")
            return None
    def embed_single_text(self, text: str, use_cache: bool = True) -> List[float]:
        embeddings = self.embed_texts([text], use_cache)
        return embeddings[0] if embeddings else [0.0] * self.dimension

# Legacy embedder for backward compatibility
class CohereEmbedder:
    """Legacy Cohere embedder for backward compatibility."""
    
    def __init__(self):
        self.hybrid_embedder = HybridEmbedder(primary_provider="cohere", fallback_provider="gemini")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.hybrid_embedder.embed_texts(texts)
    
    def test_connection(self) -> Dict[str, Any]:
        return self.hybrid_embedder.test_connection()

# Global instances
hybrid_embedder = HybridEmbedder(primary_provider="cohere", fallback_provider="gemini")
embedder = CohereEmbedder()  # Legacy compatibility

class OpenAIEmbedder:
    """OpenAI embedding integration - best quality but paid."""
    
    def __init__(self):
        self.client = None
        self.model = "text-embedding-3-small"  # OpenAI's best model
        self.dimension = 1536  # OpenAI's dimension
        
        if config.OPENAI_API_KEY:
            try:
                import openai
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
                print(f"✅ OpenAI client initialized with model: {self.model}")
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
                self.client = None
        else:
            print("⚠️ OPENAI_API_KEY not set. OpenAI embeddings disabled.")
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return self.client is not None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using OpenAI."""
        if not self.is_available():
            print("Warning: OpenAI client not available.")
            return []
        
        try:
            embeddings = []
            for text in texts:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                embeddings.append(response.data[0].embedding)
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating OpenAI embeddings: {e}")
            return []
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query using OpenAI."""
        if not self.is_available():
            print("Warning: OpenAI client not available.")
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=query
            )
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating OpenAI query embedding: {e}")
            return [] 