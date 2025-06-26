import time
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .document_source import document_source, notebook_source, Document
from .embedder import embedder
from .retriever import retriever
from .generator import generator
from .config import settings

class EmailRAGPipeline:
    """Main RAG pipeline for email Q&A."""
    
    def __init__(self):
        self.is_initialized = False
        self.last_index_update = None
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize the RAG pipeline by building/loading the index."""
        try:
            print("🧠 Initializing RAG pipeline...")
            
            # Test Cohere connection
            embedder_status = embedder.test_connection()
            generator_status = generator.test_connection()
            
            print(f"Embedder status: {embedder_status['overall_status']}")
            print(f"Generator status: {generator_status['status']}")
            
            # Try to load documents from notebooks first, fallback to email files
            documents = notebook_source.load_documents()
            source_type = "notebook"
            
            if not documents:
                print("No notebook documents found, falling back to email files...")
                documents = document_source.load_documents()
                source_type = "email"
            
            if not documents:
                print("No documents found. Pipeline will work with fallback search.")
                self.is_initialized = True
                return True
            
            # Chunk documents
            if source_type == "notebook":
                chunked_docs = notebook_source.chunk_documents(documents)
            else:
                chunked_docs = document_source.chunk_documents(documents)
            
            print(f"Loaded {len(documents)} documents from {source_type} source, created {len(chunked_docs)} chunks")
            
            # Build FAISS index
            if embedder.is_available():
                success = retriever.build_index(chunked_docs, force_rebuild)
                if success:
                    print("✅ FAISS index built successfully")
                else:
                    print("⚠️ FAISS index build failed, using fallback search")
            else:
                print("⚠️ Cohere not available, using fallback search")
            
            self.is_initialized = True
            self.last_index_update = datetime.utcnow()
            
            return True
            
        except Exception as e:
            print(f"Error initializing RAG pipeline: {e}")
            return False
    
    def query(self, question: str, label: str = None, max_age_days: int = None, sender: str = None) -> Dict[str, Any]:
        """Query the RAG pipeline with a question. Supports persona first-person answers."""
        start_time = time.time()
        try:
            if not self.is_initialized:
                return {
                    'answer': 'RAG pipeline not initialized. Please try again.',
                    'context': [],
                    'processing_time': time.time() - start_time,
                    'error': 'Pipeline not initialized'
                }
            
            # Default to substack.com if no label specified
            if not label:
                label = "substack.com"
            
            # Detect if the question is addressed to a persona (e.g., "Nate, ...")
            persona_name = None
            # Improved regex to handle greetings and better name detection
            # Pattern: (greeting)? (name) [,:\-\s]+ (question)
            # This handles: "Hey Nate, tell me about AI", "Nate, tell me about AI", "Hello Nate tell me about AI"
            question_stripped = question.strip()
            
            # Common greetings to filter out
            greetings = {'hey', 'hello', 'hi', 'greetings', 'good morning', 'good afternoon', 'good evening'}
            
            # Try to match patterns like "Hey Nate, tell me about AI" or "Nate, tell me about AI"
            persona_match = re.match(r"^(?:(?:Hey|Hello|Hi|Greetings?)\s+)?([A-Z][a-z]+)[,:\-\s]+(.+)$", question_stripped)
            
            if persona_match:
                potential_name = persona_match.group(1)
                question_body = persona_match.group(2).strip()
                
                # Additional check to ensure it's likely a name (not a generic word)
                generic_words = {
                    'what', 'when', 'where', 'who', 'why', 'how', 'tell', 'show', 'give', 'find', 
                    'search', 'look', 'check', 'get', 'make', 'do', 'can', 'will', 'should', 
                    'could', 'would', 'may', 'might', 'must', 'shall', 'hey', 'hello', 'hi'
                }
                
                if potential_name.lower() not in generic_words:
                    persona_name = potential_name
                else:
                    # If the first word was a greeting, try to find a name in the question body
                    # Look for patterns like "Hey, Nate tell me about AI"
                    name_match = re.match(r"^([A-Z][a-z]+)\s+(.+)$", question_body)
                    if name_match:
                        second_name = name_match.group(1)
                        if second_name.lower() not in generic_words:
                            persona_name = second_name
                            question_body = name_match.group(2).strip()
            else:
                question_body = question
            # Retrieve relevant documents
            if embedder.is_available():
                search_results = retriever.search(question_body, top_k=settings.TOP_K_RETRIEVAL)
                context_docs = []
                for doc, score in search_results:
                    # Convert Document to dict for downstream compatibility
                    context_docs.append({'content': doc.content, 'metadata': doc.metadata, 'score': score})
            else:
                context_docs = document_source.simple_search(question_body, label, max_age_days, sender)
                # If not already dicts, wrap as needed
                context_docs = [{'content': doc.content, 'metadata': doc.metadata, 'score': 1.0} for doc in context_docs]
            # If persona_name is found, try to generate first-person answer
            if persona_name:
                try:
                    from ingestion_api.persona_extractor import persona_extractor
                    persona = persona_extractor.get_persona(persona_name)
                    if not persona:
                        persona = {'first_name': persona_name}
                    # Derive persona traits from context_docs
                    persona_traits = generator.derive_persona_traits(persona_name, context_docs)
                    answer = generator.generate_first_person_persona_response(
                        persona_name=persona_name,
                        persona_traits=persona_traits,
                        question=question_body,
                        context_docs=context_docs
                    )
                    return {
                        'answer': answer,
                        'context': context_docs,
                        'processing_time': time.time() - start_time,
                        'persona': persona,
                        'persona_traits': persona_traits
                    }
                except Exception as e:
                    print(f"Error in persona first-person response: {e}")
            # Default: normal RAG response
            answer = generator.generate_response(question_body, context_docs, sender=sender)
            return {
                'answer': answer,
                'context': context_docs,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            print(f"Error in RAG query: {e}")
            return {
                'answer': f'Error processing query: {str(e)}',
                'context': [],
                'processing_time': time.time() - start_time,
                'error': str(e)
            }
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG pipeline."""
        try:
            # Document stats from both sources
            notebook_stats = notebook_source.get_document_stats()
            email_stats = document_source.get_document_stats()
            
            # Index stats
            index_stats = retriever.get_index_stats()
            
            # Component status
            embedder_status = embedder.test_connection()
            generator_status = generator.test_connection()
            
            return {
                'pipeline_initialized': self.is_initialized,
                'last_index_update': self.last_index_update.isoformat() if self.last_index_update else None,
                'notebook_stats': notebook_stats,
                'email_stats': email_stats,
                'index_stats': index_stats,
                'embedder_status': embedder_status,
                'generator_status': generator_status,
                'settings': {
                    'chunk_size': settings.CHUNK_SIZE,
                    'chunk_overlap': settings.CHUNK_OVERLAP,
                    'top_k_retrieval': settings.TOP_K_RETRIEVAL,
                    'embedding_model': settings.EMBEDDING_MODEL,
                    'generation_model': settings.GENERATION_MODEL
                }
            }
            
        except Exception as e:
            return {
                'pipeline_initialized': self.is_initialized,
                'error': str(e)
            }
    
    def refresh_index(self, force_rebuild: bool = True) -> bool:
        """Refresh the FAISS index with latest documents."""
        try:
            print("🔄 Refreshing RAG index...")
            
            # Load latest documents from both sources
            notebook_docs = notebook_source.load_documents()
            email_docs = document_source.load_documents()
            
            # Combine documents, prioritizing notebooks
            all_documents = notebook_docs + email_docs
            
            if not all_documents:
                print("No documents found for index refresh.")
                return False
            
            # Chunk documents
            notebook_chunks = notebook_source.chunk_documents(notebook_docs)
            email_chunks = document_source.chunk_documents(email_docs)
            all_chunks = notebook_chunks + email_chunks
            
            print(f"Refreshing index with {len(all_documents)} documents ({len(notebook_docs)} notebooks, {len(email_docs)} emails), {len(all_chunks)} chunks")
            
            # Rebuild index
            if embedder.is_available():
                success = retriever.build_index(all_chunks, force_rebuild)
                if success:
                    self.last_index_update = datetime.utcnow()
                    print("✅ Index refreshed successfully")
                    return True
                else:
                    print("❌ Index refresh failed")
                    return False
            else:
                print("⚠️ Cohere not available, cannot refresh index")
                return False
                
        except Exception as e:
            print(f"Error refreshing index: {e}")
            return False
    
    def search_only(self, query: str, label: str = None, max_age_days: int = None) -> List[Dict[str, Any]]:
        """Search for documents without generating a response."""
        try:
            search_results = retriever.search(query)
            
            filtered_results = []
            for doc, score in search_results:
                # Apply filters
                if label and doc.metadata.get('label') != label:
                    continue
                
                if max_age_days:
                    doc_date_str = doc.metadata.get('date', '')
                    if doc_date_str:
                        try:
                            doc_date = datetime.fromisoformat(doc_date_str)
                            if doc_date < datetime.utcnow() - timedelta(days=max_age_days):
                                continue
                        except (ValueError, TypeError):
                            # Skip documents with invalid dates
                            continue
                
                filtered_results.append({
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'score': score
                })
            
            return filtered_results
            
        except Exception as e:
            print(f"Error in search_only: {e}")
            return []

# Global pipeline instance
pipeline = EmailRAGPipeline()

# Convenience function for external use
def query_email_docs(question: str, label: str = None, max_age_days: int = None) -> Dict[str, Any]:
    """Main function to query email documents using RAG."""
    return pipeline.query_email_docs(question, label, max_age_days) 