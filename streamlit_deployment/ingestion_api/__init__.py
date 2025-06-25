"""
Email Processing & RAG API - Ingestion Module

This module provides FastAPI-based email ingestion and processing capabilities.
"""

from .main import app
from .parser import parser
from .database import db
from .config import settings

__version__ = "1.0.0"
__all__ = ["app", "parser", "db", "settings"] 