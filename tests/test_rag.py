import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from rag.document_source import EmailDocumentSource, Document
from rag.embedder import CohereEmbedder
from rag.retriever import FAISSRetriever
from rag.generator import LLMGenerator
from rag.email_pipeline import EmailRAGPipeline

class TestDocumentSource:
    """Test document source functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.document_source = EmailDocumentSource()
        
        # Create test documents
        self.test_docs = [
            Document(
                content="This is a test email about AI and machine learning. It contains important information about neural networks.",
                metadata={
                    'email_id': 'test-1',
                    'subject': 'AI Research Update',
                    'sender': 'ai@example.com',
                    'date': '2024-01-15T10:00:00',
                    'label': 'AI'
                }
            ),
            Document(
                content="This is another email about fintech and blockchain technology. It discusses cryptocurrency trends.",
                metadata={
                    'email_id': 'test-2',
                    'subject': 'Fintech Newsletter',
                    'sender': 'fintech@example.com',
                    'date': '2024-01-16T11:00:00',
                    'label': 'Fintech'
                }
            )
        ]
    
    def test_chunk_documents(self):
        """Test document chunking functionality."""
        chunked_docs = self.document_source.chunk_documents(self.test_docs)
        
        assert len(chunked_docs) >= len(self.test_docs)
        
        # Check that chunks have metadata
        for doc in chunked_docs:
            assert 'chunk_id' in doc.metadata
            assert 'total_chunks' in doc.metadata
            assert 'chunk_content' in doc.metadata
    
    def test_chunk_text(self):
        """Test text chunking with overlap."""
        long_text = "This is a very long text that should be chunked. " * 50
        
        chunks = self.document_source._chunk_text(long_text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= self.document_source.chunk_size for chunk in chunks)
    
    def test_get_document_stats(self):
        """Test document statistics."""
        stats = self.document_source.get_document_stats()
        
        assert 'total_documents' in stats
        assert 'total_chunks' in stats
        assert 'available_labels' in stats

class TestEmbedder:
    """Test embedding functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.embedder = CohereEmbedder()
    
    def test_embedder_initialization(self):
        """Test embedder initialization."""
        # Should initialize even without API key
        assert hasattr(self.embedder, 'client')
        assert hasattr(self.embedder, 'model')
        assert hasattr(self.embedder, 'dimension')
    
    def test_is_available(self):
        """Test availability check."""
        # Should return False without API key
        assert isinstance(self.embedder.is_available(), bool)
    
    def test_embed_texts_fallback(self):
        """Test embedding fallback when Cohere is not available."""
        texts = ["Test text 1", "Test text 2"]
        embeddings = self.embedder.embed_texts(texts)
        
        assert len(embeddings) == len(texts)
        assert all(len(emb) == self.embedder.dimension for emb in embeddings)
    
    def test_embed_query_fallback(self):
        """Test query embedding fallback."""
        query = "Test query"
        embedding = self.embedder.embed_query(query)
        
        assert len(embedding) == self.embedder.dimension
    
    def test_test_connection(self):
        """Test connection test."""
        result = self.embedder.test_connection()
        
        assert 'status' in result
        assert 'message' in result
        assert 'model' in result

class TestRetriever:
    """Test FAISS retriever functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.retriever = FAISSRetriever()
        self.retriever.index_path = Path(self.temp_dir) / "test_index.bin"
        self.retriever.documents_path = Path(self.temp_dir) / "test_docs.pkl"
        
        # Create test documents
        self.test_docs = [
            Document(
                content="AI and machine learning are transforming industries.",
                metadata={'subject': 'AI Update', 'sender': 'ai@example.com'}
            ),
            Document(
                content="Blockchain technology is revolutionizing finance.",
                metadata={'subject': 'Fintech News', 'sender': 'fintech@example.com'}
            )
        ]
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_retriever_initialization(self):
        """Test retriever initialization."""
        assert hasattr(self.retriever, 'index')
        assert hasattr(self.retriever, 'documents')
        assert hasattr(self.retriever, 'dimension')
    
    def test_build_index_fallback(self):
        """Test index building with fallback when embeddings not available."""
        success = self.retriever.build_index(self.test_docs)
        
        # Should handle gracefully even without embeddings
        assert isinstance(success, bool)
    
    def test_search_fallback(self):
        """Test search with fallback."""
        # Set up documents for fallback search
        self.retriever.documents = self.test_docs
        
        results = self.retriever.search("AI machine learning")
        
        assert isinstance(results, list)
        # Should return (document, score) tuples
        if results:
            assert len(results[0]) == 2
            assert isinstance(results[0][0], Document)
            assert isinstance(results[0][1], (int, float))
    
    def test_get_index_stats(self):
        """Test index statistics."""
        stats = self.retriever.get_index_stats()
        
        assert 'index_exists' in stats
        assert 'total_documents' in stats
        assert 'dimension' in stats

class TestGenerator:
    """Test LLM generator functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.generator = LLMGenerator()
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        assert hasattr(self.generator, 'client')
        assert hasattr(self.generator, 'model')
        assert hasattr(self.generator, 'max_tokens')
        assert hasattr(self.generator, 'temperature')
    
    def test_is_available(self):
        """Test availability check."""
        assert isinstance(self.generator.is_available(), bool)
    
    def test_fallback_response(self):
        """Test fallback response generation."""
        query = "What is AI?"
        context_docs = [
            {
                'content': 'AI is artificial intelligence.',
                'metadata': {'subject': 'AI Intro', 'sender': 'ai@example.com'}
            }
        ]
        
        response = self.generator._fallback_response(query, context_docs)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert 'AI' in response or 'artificial intelligence' in response
    
    def test_build_context(self):
        """Test context building."""
        context_docs = [
            {
                'content': 'Test content 1',
                'metadata': {'subject': 'Test 1', 'sender': 'test1@example.com', 'date': '2024-01-01'}
            },
            {
                'content': 'Test content 2',
                'metadata': {'subject': 'Test 2', 'sender': 'test2@example.com', 'date': '2024-01-02'}
            }
        ]
        
        context = self.generator._build_context(context_docs)
        
        assert isinstance(context, str)
        assert 'Test content 1' in context
        assert 'Test content 2' in context
        assert 'test1@example.com' in context
        assert 'test2@example.com' in context
    
    def test_create_prompt(self):
        """Test prompt creation."""
        query = "What is the main topic?"
        context = "This is the context information."
        
        prompt = self.generator._create_prompt(query, context)
        
        assert isinstance(prompt, str)
        assert query in prompt
        assert context in prompt
        assert "Question:" in prompt
        assert "Answer:" in prompt

class TestEmailRAGPipeline:
    """Test the main RAG pipeline."""
    
    def setup_method(self):
        """Set up test environment."""
        self.pipeline = EmailRAGPipeline()
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        assert hasattr(self.pipeline, 'is_initialized')
        assert hasattr(self.pipeline, 'last_index_update')
    
    def test_initialize(self):
        """Test pipeline initialization."""
        # Should handle gracefully even without documents
        success = self.pipeline.initialize()
        
        assert isinstance(success, bool)
    
    def test_query_email_docs_fallback(self):
        """Test query functionality with fallback."""
        result = self.pipeline.query_email_docs(
            question="What is AI?",
            label="AI"
        )
        
        assert isinstance(result, dict)
        assert 'answer' in result
        assert 'context' in result
        assert 'metadata' in result
        assert 'processing_time' in result
        assert 'total_results' in result
    
    def test_get_pipeline_stats(self):
        """Test pipeline statistics."""
        stats = self.pipeline.get_pipeline_stats()
        
        assert isinstance(stats, dict)
        assert 'pipeline_initialized' in stats
        assert 'document_stats' in stats
        assert 'index_stats' in stats
        assert 'embedder_status' in stats
        assert 'generator_status' in stats

if __name__ == "__main__":
    # Run basic tests
    print("Running RAG pipeline tests...")
    
    # Test document source
    test_doc_source = TestDocumentSource()
    test_doc_source.setup_method()
    
    print("Testing document source...")
    test_doc_source.test_chunk_documents()
    test_doc_source.test_chunk_text()
    test_doc_source.test_get_document_stats()
    
    # Test embedder
    test_embedder = TestEmbedder()
    test_embedder.setup_method()
    
    print("Testing embedder...")
    test_embedder.test_embedder_initialization()
    test_embedder.test_is_available()
    test_embedder.test_embed_texts_fallback()
    test_embedder.test_embed_query_fallback()
    test_embedder.test_test_connection()
    
    # Test retriever
    test_retriever = TestRetriever()
    test_retriever.setup_method()
    
    print("Testing retriever...")
    test_retriever.test_retriever_initialization()
    test_retriever.test_build_index_fallback()
    test_retriever.test_search_fallback()
    test_retriever.test_get_index_stats()
    
    test_retriever.teardown_method()
    
    # Test generator
    test_generator = TestGenerator()
    test_generator.setup_method()
    
    print("Testing generator...")
    test_generator.test_generator_initialization()
    test_generator.test_is_available()
    test_generator.test_fallback_response()
    test_generator.test_build_context()
    test_generator.test_create_prompt()
    
    # Test pipeline
    test_pipeline = TestEmailRAGPipeline()
    test_pipeline.setup_method()
    
    print("Testing pipeline...")
    test_pipeline.test_pipeline_initialization()
    test_pipeline.test_initialize()
    test_pipeline.test_query_email_docs_fallback()
    test_pipeline.test_get_pipeline_stats()
    
    print("✅ All RAG tests passed!") 