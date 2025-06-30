import numpy as np
import faiss
import pickle
import os
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import logging
from tqdm import tqdm

from .document_source import Document
from .embedder import embedder, HybridEmbedder
from .config import config

logger = logging.getLogger(__name__)

class FAISSRetriever:
    """FAISS-based retriever with Gemini fallback and optimizations for 500+ emails."""
    
    def __init__(self, vector_store_dir: Path, embedder: HybridEmbedder, cache_size: int = 1000):
        self.vector_store_dir = Path(vector_store_dir)
        self.embedder = embedder
        self.cache_size = cache_size
        
        # FAISS index and documents
        self.index = None
        self.documents = []
        self.document_metadata = []
        
        # Performance tracking
        self.stats = {
            'searches_performed': 0,
            'cache_hits': 0,
            'gemini_fallback_used': 0,
            'avg_search_time': 0.0
        }
        
        # Cache for search results
        self._search_cache = {}
        
        # Ensure vector store directory exists
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
    
    def build_index(self, documents: List[Document], force_rebuild: bool = False, 
                   show_progress: bool = True) -> bool:
        """Build FAISS index from documents with progress tracking."""
        try:
            index_path = self.vector_store_dir / "faiss_index.bin"
            docs_path = self.vector_store_dir / "documents.pkl"
            
            # Check if index exists and is recent
            if not force_rebuild and index_path.exists() and docs_path.exists():
                logger.info("Loading existing FAISS index...")
                return self._load_existing_index()
            
            logger.info(f"Building FAISS index for {len(documents)} documents...")
            
            # Extract text content and metadata
            texts = []
            metadata_list = []
            
            if show_progress:
                docs_iter = tqdm(documents, desc="Processing documents")
            else:
                docs_iter = documents
            
            for doc in docs_iter:
                texts.append(doc.content)
                metadata_list.append(doc.metadata)
            
            # Generate embeddings with fallback support
            logger.info("Generating embeddings...")
            embeddings = self.embedder.embed_texts(texts)
            
            if not embeddings or len(embeddings) == 0:
                logger.error("Failed to generate embeddings")
                return False
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Build FAISS index
            dimension = embeddings_array.shape[1]
            logger.info(f"Building FAISS index with dimension {dimension}")
            
            # Use IVF index for better performance with large datasets
            if len(documents) > 1000:
                # For large datasets, use IVF index
                nlist = min(4096, len(documents) // 10)  # Number of clusters
                quantizer = faiss.IndexFlatIP(dimension)
                self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
                
                # Train the index
                logger.info("Training IVF index...")
                self.index.train(embeddings_array)
            else:
                # For smaller datasets, use simple index
                self.index = faiss.IndexFlatIP(dimension)
            
            # Add vectors to index
            self.index.add(embeddings_array)
            
            # Store documents and metadata
            self.documents = documents
            self.document_metadata = metadata_list
            
            # Save index and documents
            self._save_index()
            
            logger.info(f"✅ FAISS index built successfully with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            return False
    
    def _load_existing_index(self) -> bool:
        """Load existing FAISS index and documents."""
        try:
            index_path = self.vector_store_dir / "faiss_index.bin"
            docs_path = self.vector_store_dir / "documents.pkl"
            
            logger.info(f"🔍 Attempting to load existing index from {index_path}")
            logger.info(f"🔍 Documents file path: {docs_path}")
            
            # Check if files exist
            if not index_path.exists():
                logger.error(f"❌ FAISS index file not found: {index_path}")
                return False
            
            if not docs_path.exists():
                logger.error(f"❌ Documents file not found: {docs_path}")
                return False
            
            # Load FAISS index
            logger.info("📖 Loading FAISS index...")
            self.index = faiss.read_index(str(index_path))
            logger.info(f"✅ FAISS index loaded successfully. Index type: {type(self.index).__name__}")
            
            # Load documents
            logger.info("📖 Loading documents...")
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            logger.info(f"✅ Documents loaded successfully. Count: {len(self.documents)}")
            
            # Extract metadata
            self.document_metadata = [doc.metadata for doc in self.documents]
            
            # Verify index and documents match
            if hasattr(self.index, 'ntotal') and self.index.ntotal != len(self.documents):
                logger.warning(f"⚠️ Index count ({self.index.ntotal}) doesn't match document count ({len(self.documents)})")
            
            logger.info(f"✅ FAISS index loaded with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading existing index: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return False
    
    def _save_index(self):
        """Save FAISS index and documents."""
        try:
            # Save FAISS index
            index_path = self.vector_store_dir / "faiss_index.bin"
            faiss.write_index(self.index, str(index_path))
            
            # Save documents
            docs_path = self.vector_store_dir / "documents.pkl"
            with open(docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info("💾 Index and documents saved")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def search(self, query: str, k: int = 5, label: Optional[str] = None, 
               max_age_days: Optional[int] = None, use_gemini_fallback: bool = True) -> List[Dict]:
        """Search for similar documents with filtering and fallback support."""
        import time
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{query}:{k}:{label}:{max_age_days}"
        if cache_key in self._search_cache:
            self.stats['cache_hits'] += 1
            return self._search_cache[cache_key]
        
        try:
            if self.index is None or len(self.documents) == 0:
                logger.warning("No FAISS index available, using fallback search")
                return self._fallback_search(query, k, label, max_age_days)
            
            # Generate query embedding
            query_embedding = self.embedder.embed_single_text(query)
            
            if not query_embedding or len(query_embedding) == 0:
                logger.warning("Failed to generate query embedding, using fallback")
                return self._fallback_search(query, k, label, max_age_days)
            
            # Convert to numpy array
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search FAISS index
            scores, indices = self.index.search(query_vector, min(k * 3, len(self.documents)))
            
            # Process results with filtering
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                doc = self.documents[idx]
                metadata = self.document_metadata[idx]
                
                # Apply filters
                if label and metadata.get('label') != label:
                    continue
                
                if max_age_days:
                    doc_date_str = metadata.get('date', '')
                    if doc_date_str:
                        try:
                            from datetime import datetime, timedelta
                            doc_date = datetime.fromisoformat(doc_date_str)
                            if doc_date < datetime.utcnow() - timedelta(days=max_age_days):
                                continue
                        except (ValueError, TypeError):
                            continue
                
                results.append({
                    'content': doc.content,
                    'metadata': metadata,
                    'score': float(score)
                })
                
                if len(results) >= k:
                    break
            
            # Cache results
            if len(self._search_cache) < self.cache_size:
                self._search_cache[cache_key] = results
            
            # Update stats
            search_time = time.time() - start_time
            self.stats['searches_performed'] += 1
            self.stats['avg_search_time'] = (
                (self.stats['avg_search_time'] * (self.stats['searches_performed'] - 1) + search_time) 
                / self.stats['searches_performed']
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in FAISS search: {e}")
            if use_gemini_fallback:
                self.stats['gemini_fallback_used'] += 1
                return self._fallback_search(query, k, label, max_age_days)
            return []
    
    def _fallback_search(self, query: str, k: int, label: Optional[str] = None, 
                        max_age_days: Optional[int] = None) -> List[Dict]:
        """Fallback search using simple text matching."""
        logger.info("🔄 Using fallback text search")
        
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            # Simple text matching
            if query_lower in doc.content.lower():
                metadata = doc.metadata
                
                # Apply filters
                if label and metadata.get('label') != label:
                    continue
                
                if max_age_days:
                    doc_date_str = metadata.get('date', '')
                    if doc_date_str:
                        try:
                            from datetime import datetime, timedelta
                            doc_date = datetime.fromisoformat(doc_date_str)
                            if doc_date < datetime.utcnow() - timedelta(days=max_age_days):
                                continue
                        except (ValueError, TypeError):
                            continue
                
                results.append({
                    'content': doc.content,
                    'metadata': metadata,
                    'score': 0.5  # Default score for fallback
                })
                
                if len(results) >= k:
                    break
        
        return results
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get FAISS index statistics."""
        if self.index is None:
            return {'status': 'not_initialized'}
        
        return {
            'total_documents': len(self.documents),
            'index_type': type(self.index).__name__,
            'dimension': self.index.d if hasattr(self.index, 'd') else 'unknown',
            'is_trained': self.index.is_trained if hasattr(self.index, 'is_trained') else True,
            'ntotal': self.index.ntotal if hasattr(self.index, 'ntotal') else len(self.documents),
            'search_stats': self.stats
        }
    
    def clear_cache(self):
        """Clear search cache."""
        self._search_cache.clear()
        logger.info("🧹 Search cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            **self.stats,
            'cache_size': len(self._search_cache),
            'total_documents': len(self.documents)
        }

# Legacy retriever for backward compatibility
class LegacyRetriever:
    """Legacy retriever for backward compatibility."""
    
    def __init__(self, vector_store_dir: str, embedder):
        self.faiss_retriever = FAISSRetriever(Path(vector_store_dir), embedder)
    
    def build_index(self, documents, force_rebuild=False):
        return self.faiss_retriever.build_index(documents, force_rebuild)
    
    def search(self, query, top_k=5):
        results = self.faiss_retriever.search(query, k=top_k)
        return [(Document(content=r['content'], metadata=r['metadata']), r['score']) for r in results]

# Global instances
# Note: The global retriever is deprecated. Use the retriever from EmailRAGPipeline instead.
# This is kept for backward compatibility but should not be used in new code.
try:
    from .embedder import HybridEmbedder
    retriever = LegacyRetriever("data/vector_store", HybridEmbedder())
except Exception as e:
    logger.warning(f"Could not initialize global retriever: {e}")
    retriever = None 