import numpy as np
import faiss
import pickle
import os
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from .document_source import Document
from .embedder import embedder
from .config import settings

class FAISSRetriever:
    """FAISS-based retrieval system for semantic search."""
    
    def __init__(self):
        self.index = None
        self.documents = []
        self.index_path = settings.VECTOR_STORE_DIR / "faiss_index.bin"
        self.documents_path = settings.VECTOR_STORE_DIR / "documents.pkl"
        self.dimension = embedder.get_embedding_dimension()
    
    def build_index(self, documents: List[Document], force_rebuild: bool = False) -> bool:
        """Build FAISS index from documents."""
        try:
            # Check if index already exists and force_rebuild is False
            if not force_rebuild and self.index_path.exists() and self.documents_path.exists():
                print("Loading existing FAISS index...")
                return self.load_index()
            
            if not documents:
                print("No documents provided for indexing.")
                return False
            
            print(f"Building FAISS index for {len(documents)} documents...")
            
            # Generate embeddings for all documents
            texts = [doc.content for doc in documents]
            embeddings = embedder.embed_texts(texts)
            
            if not embeddings or len(embeddings) == 0:
                print("No embeddings generated. Using fallback search.")
                return False
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            self.index.add(embeddings_array)
            
            # Store documents
            self.documents = documents
            
            # Save index and documents
            self.save_index()
            
            print(f"✅ FAISS index built successfully with {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error building FAISS index: {e}")
            return False
    
    def save_index(self) -> bool:
        """Save FAISS index and documents to disk."""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            
            if self.documents:
                with open(self.documents_path, 'wb') as f:
                    pickle.dump(self.documents, f)
            
            return True
            
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
            return False
    
    def load_index(self) -> bool:
        """Load FAISS index and documents from disk."""
        try:
            if not self.index_path.exists() or not self.documents_path.exists():
                print("Index files not found.")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load documents
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            print(f"✅ FAISS index loaded with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return False
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[Document, float]]:
        """Search for similar documents using FAISS."""
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        
        try:
            # If no index available, fall back to text search
            if self.index is None or len(self.documents) == 0:
                print("No FAISS index available. Using fallback text search.")
                return self._fallback_search(query, top_k)
            
            # Generate query embedding
            query_embedding = embedder.embed_query(query)
            if not query_embedding or all(x == 0 for x in query_embedding):
                print("Query embedding failed. Using fallback text search.")
                return self._fallback_search(query, top_k)
            
            # Convert to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_array, top_k)
            
            # Return documents with scores
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(score)))
            
            return results
            
        except Exception as e:
            print(f"Error in FAISS search: {e}")
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int) -> List[Tuple[Document, float]]:
        """Fallback to simple text search when FAISS is not available."""
        try:
            from .document_source import document_source
            
            # Use document source for simple search
            results = document_source.search_documents(query)
            
            # Convert to (document, score) format
            scored_results = []
            for i, doc in enumerate(results):
                # Simple scoring based on position
                score = 1.0 / (i + 1)
                scored_results.append((doc, score))
            
            return scored_results[:top_k]
            
        except Exception as e:
            print(f"Error in fallback search: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the FAISS index."""
        try:
            if self.index is None:
                return {
                    'index_exists': False,
                    'total_documents': 0,
                    'dimension': self.dimension,
                    'index_type': 'None'
                }
            
            return {
                'index_exists': True,
                'total_documents': self.index.ntotal,
                'dimension': self.index.d,
                'index_type': type(self.index).__name__,
                'is_trained': self.index.is_trained
            }
            
        except Exception as e:
            return {
                'index_exists': False,
                'error': str(e),
                'dimension': self.dimension
            }
    
    def clear_index(self) -> bool:
        """Clear the FAISS index and documents."""
        try:
            self.index = None
            self.documents = []
            
            # Remove index files
            if self.index_path.exists():
                os.remove(self.index_path)
            
            if self.documents_path.exists():
                os.remove(self.documents_path)
            
            print("✅ FAISS index cleared successfully")
            return True
            
        except Exception as e:
            print(f"Error clearing FAISS index: {e}")
            return False

# Global retriever instance
retriever = FAISSRetriever() 