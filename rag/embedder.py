import os
import logging
from typing import List, Dict, Optional, Any
from functools import lru_cache
import time
import numpy as np
import cohere
import google.generativeai as genai
from .config import settings

logger = logging.getLogger(__name__)

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
    """Hybrid embedder with Cohere primary and Gemini fallback, optimized for 500+ emails."""
    
    def __init__(self, primary_provider: str = "cohere", fallback_provider: str = "gemini", 
                 cache_size: int = 1000, dimension: int = 1024):
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.dimension = dimension
        self.cache_size = cache_size
        
        # Initialize clients
        self.cohere_client = None
        self.gemini_client = None
        
        # Performance tracking
        self.stats = {
            'cohere_embeddings': 0,
            'gemini_embeddings': 0,
            'fallback_used': 0,
            'cache_hits': 0,
            'total_requests': 0
        }
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize embedding clients with error handling."""
        # Initialize Cohere
        if self.primary_provider == "cohere":
            try:
                api_key = os.getenv('COHERE_API_KEY')
                if api_key:
                    self.cohere_client = cohere.Client(api_key)
                    logger.info("✅ Cohere client initialized with model: embed-english-v3.0")
                else:
                    logger.warning("⚠️ COHERE_API_KEY not found")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Cohere client: {e}")
        
        # Initialize Gemini
        if self.fallback_provider == "gemini":
            try:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_client = genai.GenerativeModel('models/embedding-001')
                    logger.info("✅ Gemini client initialized with model: models/embedding-001")
                else:
                    logger.warning("⚠️ GEMINI_API_KEY not found")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini client: {e}")
    
    @lru_cache(maxsize=1000)
    def _get_cached_embedding(self, text: str, provider: str) -> Optional[List[float]]:
        """Get cached embedding if available."""
        # This is a simplified cache - in production, use Redis or similar
        return None
    
    def _cache_embedding(self, text: str, embedding: List[float], provider: str):
        """Cache embedding for future use."""
        # In production, implement proper caching
        pass
    
    def embed_texts(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Generate embeddings for a list of texts with fallback support."""
        if not texts:
            return []
        
        self.stats['total_requests'] += 1
        
        # Try primary provider first
        embeddings = self._try_primary_provider(texts, use_cache)
        
        # If primary fails, use fallback
        if not embeddings and self.fallback_provider:
            logger.info(f"🔄 Primary provider failed, using {self.fallback_provider} fallback")
            embeddings = self._try_fallback_provider(texts, use_cache)
            self.stats['fallback_used'] += 1
        
        # If both fail, return zero embeddings
        if not embeddings:
            logger.warning("⚠️ All embedding providers failed, returning zero embeddings")
            return [[0.0] * self.dimension] * len(texts)
        
        return embeddings
    
    def _try_primary_provider(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        """Try to get embeddings from primary provider."""
        if self.primary_provider == "cohere":
            return self._embed_with_cohere(texts, use_cache)
        elif self.primary_provider == "gemini":
            return self._embed_with_gemini(texts, use_cache)
        return None
    
    def _try_fallback_provider(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        """Try to get embeddings from fallback provider."""
        if self.fallback_provider == "cohere":
            return self._embed_with_cohere(texts, use_cache)
        elif self.fallback_provider == "gemini":
            return self._embed_with_gemini(texts, use_cache)
        return None
    
    def _embed_with_cohere(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        """Generate embeddings using Cohere."""
        if not self.cohere_client:
            return None
        
        try:
            # Batch process texts
            batch_size = 100  # Cohere's recommended batch size
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Use the correct method signature for Cohere v4.37
                response = self.cohere_client.embed(
                    texts=batch,
                    model="embed-english-v3.0",
                    input_type="search_document"
                )
                
                batch_embeddings = response.embeddings
                all_embeddings.extend(batch_embeddings)
                
                # Add delay to respect rate limits
                time.sleep(0.1)
            
            self.stats['cohere_embeddings'] += len(texts)
            return all_embeddings
            
        except Exception as e:
            logger.error(f"❌ Cohere embedding error: {e}")
            return None
    
    def _embed_with_gemini(self, texts: List[str], use_cache: bool) -> Optional[List[List[float]]]:
        """Generate embeddings using Gemini."""
        if not self.gemini_client:
            return None
        
        try:
            all_embeddings = []
            
            for text in texts:
                # Check cache first
                if use_cache:
                    cached = self._get_cached_embedding(text, "gemini")
                    if cached:
                        all_embeddings.append(cached)
                        self.stats['cache_hits'] += 1
                        continue
                
                # Generate embedding
                embedding = self.gemini_client.embed_content(
                    content=text,
                    task_type="retrieval_document"
                )
                
                embedding_values = embedding.embedding
                all_embeddings.append(embedding_values)
                
                # Cache the embedding
                if use_cache:
                    self._cache_embedding(text, embedding_values, "gemini")
                
                # Add delay to respect rate limits
                time.sleep(0.1)
            
            self.stats['gemini_embeddings'] += len(texts)
            return all_embeddings
            
        except Exception as e:
            logger.error(f"❌ Gemini embedding error: {e}")
            return None
    
    def embed_single_text(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = self.embed_texts([text], use_cache)
        return embeddings[0] if embeddings else [0.0] * self.dimension
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to embedding providers."""
        results = {
            'primary_provider': self.primary_provider,
            'fallback_provider': self.fallback_provider,
            'overall_status': 'unknown'
        }
        
        # Test primary provider
        if self.primary_provider == "cohere":
            results['cohere'] = {
                'available': self.cohere_client is not None,
                'test_text': 'test'
            }
            if self.cohere_client:
                try:
                    test_embedding = self.embed_single_text('test', use_cache=False)
                    results['cohere']['working'] = len(test_embedding) > 0
                except Exception as e:
                    results['cohere']['working'] = False
                    results['cohere']['error'] = str(e)
        
        # Test fallback provider
        if self.fallback_provider == "gemini":
            results['gemini'] = {
                'available': self.gemini_client is not None,
                'test_text': 'test'
            }
            if self.gemini_client:
                try:
                    test_embedding = self.embed_single_text('test', use_cache=False)
                    results['gemini']['working'] = len(test_embedding) > 0
                except Exception as e:
                    results['gemini']['working'] = False
                    results['gemini']['error'] = str(e)
        
        # Determine overall status
        primary_working = results.get(self.primary_provider, {}).get('working', False)
        fallback_working = results.get(self.fallback_provider, {}).get('working', False)
        
        if primary_working:
            results['overall_status'] = 'success'
        elif fallback_working:
            results['overall_status'] = 'fallback'
        else:
            results['overall_status'] = 'failed'
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding statistics."""
        return {
            **self.stats,
            'cache_size': self.cache_size,
            'dimension': self.dimension,
            'providers': {
                'primary': self.primary_provider,
                'fallback': self.fallback_provider
            }
        }
    
    def clear_cache(self):
        """Clear embedding cache."""
        self._get_cached_embedding.cache_clear()
        logger.info("🧹 Embedding cache cleared")

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