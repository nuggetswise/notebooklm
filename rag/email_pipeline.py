import time
import re
import os
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from functools import lru_cache

from .document_source import document_source, notebook_source, Document, EmailDocumentSource
from .embedder import embedder, HybridEmbedder
from .retriever import retriever, FAISSRetriever
from .generator import generator, MultiProviderGenerator
from .config import settings
from .prompts import prompt_manager

logger = logging.getLogger(__name__)

class EmailRAGPipeline:
    """Email-centric RAG pipeline with optimizations for 500+ emails."""
    
    def __init__(self, data_dir: str = "data", cache_size: int = 128):
        self.data_dir = Path(data_dir)
        self.parsed_emails_dir = self.data_dir / "parsed_emails"
        self.vector_store_dir = self.data_dir / "vector_store"
        self.personas_file = self.data_dir / "personas.json"
        
        # Initialize components with lazy loading
        self._document_source = None
        self._embedder = None
        self._retriever = None
        self._generator = None
        self._personas = None
        
        # Cache settings
        self.cache_size = cache_size
        self._document_cache = {}
        self._embedding_cache = {}
        
        # Performance tracking
        self.stats = {
            'documents_loaded': 0,
            'embeddings_generated': 0,
            'queries_processed': 0,
            'cache_hits': 0
        }
    
    @property
    def document_source(self) -> EmailDocumentSource:
        """Lazy load document source."""
        if self._document_source is None:
            self._document_source = EmailDocumentSource()
        return self._document_source
    
    @property
    def embedder(self) -> HybridEmbedder:
        """Lazy load embedder with Gemini fallback."""
        if self._embedder is None:
            self._embedder = HybridEmbedder(
                primary_provider="cohere",
                fallback_provider="gemini",
                cache_size=self.cache_size
            )
        return self._embedder
    
    @property
    def retriever(self) -> FAISSRetriever:
        """Lazy load FAISS retriever."""
        if self._retriever is None:
            self._retriever = FAISSRetriever(
                self.vector_store_dir,
                self.embedder,
                cache_size=self.cache_size
            )
        return self._retriever
    
    @property
    def generator(self) -> MultiProviderGenerator:
        """Lazy load generator."""
        if self._generator is None:
            self._generator = MultiProviderGenerator()
        return self._generator
    
    @property
    def personas(self) -> Dict:
        """Lazy load personas with caching."""
        if self._personas is None:
            if self.personas_file.exists():
                with open(self.personas_file, 'r') as f:
                    self._personas = json.load(f)
            else:
                self._personas = {}
        return self._personas
    
    @lru_cache(maxsize=128)
    def _get_email_content(self, email_id: str) -> Optional[str]:
        """Cache email content for frequently accessed emails."""
        email_files = list(self.parsed_emails_dir.glob(f"{email_id}_*.txt"))
        if email_files:
            with open(email_files[0], 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def _batch_load_documents(self, batch_size: int = 50) -> List[Dict]:
        """Load documents in batches to reduce memory usage."""
        documents = []
        email_files = list(self.parsed_emails_dir.glob("*.txt"))
        
        for i in range(0, len(email_files), batch_size):
            batch_files = email_files[i:i + batch_size]
            batch_docs = self.document_source.load_email_documents(batch_files)
            documents.extend(batch_docs)
            
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_docs)} documents")
        
        return documents
    
    def initialize(self, force_rebuild: bool = False, batch_size: int = 50):
        """Initialize the RAG pipeline with lazy loading and batching."""
        logger.info("🧠 Initializing RAG pipeline with optimizations...")
        
        # Check if FAISS index exists and is recent
        faiss_index_path = self.vector_store_dir / "faiss_index.bin"
        if not force_rebuild and faiss_index_path.exists():
            # Check if index is recent (within 24 hours)
            index_age = datetime.now() - datetime.fromtimestamp(faiss_index_path.stat().st_mtime)
            if index_age < timedelta(hours=24):
                logger.info("✅ Using existing FAISS index (recent)")
                return
        
        # Load documents in batches
        documents = self._batch_load_documents(batch_size)
        
        if not documents:
            logger.warning("No documents found to process")
            return
        
        # Build FAISS index with progress tracking
        logger.info(f"🔧 Building FAISS index for {len(documents)} documents...")
        self.retriever.build_index(documents, show_progress=True)
        
        # Save stats
        self.stats['documents_loaded'] = len(documents)
        logger.info(f"✅ FAISS index built successfully with {len(documents)} documents")
    
    def query(self, question: str, label: Optional[str] = None, 
              max_age_days: Optional[int] = None, 
              use_cache: bool = True) -> Dict[str, Any]:
        """Query the RAG pipeline with caching and performance tracking."""
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"{question}:{label}:{max_age_days}"
        if use_cache and cache_key in self._document_cache:
            self.stats['cache_hits'] += 1
            logger.info("🎯 Cache hit - using cached results")
            return self._document_cache[cache_key]
        
        # Perform search
        try:
            # Use Gemini for embeddings if Cohere fails
            search_results = self.retriever.search(
                question, 
                k=5, 
                label=label,
                max_age_days=max_age_days,
                use_gemini_fallback=True
            )
            
            # Generate response
            generator_result = self.generator.generate_response(
                question, 
                search_results, 
                self._get_persona_context(question)
            )
            
            # Handle new response format (dict with provider info)
            if isinstance(generator_result, dict):
                answer = generator_result.get('response', 'No response generated')
                provider = generator_result.get('provider', 'unknown')
                model = generator_result.get('model', 'unknown')
            else:
                # Handle legacy string response format
                answer = generator_result
                provider = 'unknown'
                model = 'unknown'
            
            # Prepare result
            result = {
                'answer': answer,
                'context': search_results,
                'metadata': self._extract_metadata(search_results),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'stats': self.stats.copy(),
                'provider': provider,
                'model': model
            }
            
            # Cache result
            if use_cache:
                self._document_cache[cache_key] = result
                # Limit cache size
                if len(self._document_cache) > self.cache_size:
                    # Remove oldest entries
                    oldest_key = next(iter(self._document_cache))
                    del self._document_cache[oldest_key]
            
            self.stats['queries_processed'] += 1
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'context': [],
                'metadata': [],
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'error': str(e)
            }
    
    def _get_persona_context(self, question: str) -> Optional[str]:
        """Extract persona context from question."""
        # Simple persona detection
        question_lower = question.lower()
        for persona in self.personas.values():
            first_name = persona.get('first_name', '').lower()
            if first_name and f"hey {first_name}" in question_lower:
                return prompt_manager.get_persona_context_prompt(persona)
        return None
    
    def _extract_metadata(self, search_results: List[Dict]) -> List[Dict]:
        """Extract metadata from search results."""
        metadata = []
        for result in search_results:
            doc_metadata = result.get('metadata', {})
            metadata.append({
                'id': doc_metadata.get('email_id'),
                'subject': doc_metadata.get('subject', 'No Subject'),
                'sender': doc_metadata.get('sender', 'Unknown'),
                'date': doc_metadata.get('date', ''),
                'label': doc_metadata.get('label', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'parsed_path': doc_metadata.get('source_file'),
                'has_attachments': doc_metadata.get('has_attachments', False),
                'attachment_count': doc_metadata.get('attachment_count', 0),
                'persona': None  # Will be populated if persona detected
            })
        return metadata
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            **self.stats,
            'cache_size': len(self._document_cache),
            'embedding_cache_size': len(self._embedding_cache),
            'memory_usage_mb': self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> float:
        """Get approximate memory usage in MB."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def clear_cache(self):
        """Clear all caches."""
        self._document_cache.clear()
        self._embedding_cache.clear()
        self._get_email_content.cache_clear()
        logger.info("🧹 All caches cleared")
    
    def search_only(self, question: str, label: Optional[str] = None, 
                   max_age_days: Optional[int] = None) -> List[Dict]:
        """Search only without generating response."""
        return self.retriever.search(
            question, 
            k=5, 
            label=label,
            max_age_days=max_age_days,
            use_gemini_fallback=True
        )

# Global pipeline instance
pipeline = EmailRAGPipeline()

# Convenience function for external use
def query_email_docs(question: str, label: str = None, max_age_days: int = None) -> Dict[str, Any]:
    """Main function to query email documents using RAG."""
    return pipeline.query_email_docs(question, label, max_age_days) 