"""
Email Processing & RAG API - RAG Module

This module provides Verba-style document processing and Q&A capabilities.
"""

from .document_source import EmailDocumentSource, Document
from .embedder import CohereEmbedder
from .retriever import FAISSRetriever
from .generator import LLMGenerator
from .config import settings

__version__ = "1.0.0"
__all__ = ["EmailDocumentSource", "Document", "CohereEmbedder", "FAISSRetriever", "LLMGenerator", "settings"] 