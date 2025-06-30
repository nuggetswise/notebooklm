"""
Email Processing & RAG API - RAG Module

This module provides Verba-style document processing and Q&A capabilities.
"""

from .document_source import EmailDocumentSource, Document
from .embedder import SentenceTransformersEmbedder
from .retriever import FAISSRetriever
from .generator import MultiProviderGenerator
from .config import config

__version__ = "1.0.0"
__all__ = ["EmailDocumentSource", "Document", "SentenceTransformersEmbedder", "FAISSRetriever", "MultiProviderGenerator", "config"] 