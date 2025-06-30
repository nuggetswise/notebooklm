import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ingestion_api.database import db
from ingestion_api.models import EmailMetadata
from .config import config
from ingestion_api.parser import clean_email_address

class Document:
    """Simple document class for RAG processing."""
    
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata

class EmailDocumentSource:
    """Load and process email documents for RAG."""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def load_documents(self, label: str = None, max_age_days: int = None, sender: str = None) -> List[Document]:
        """Load email documents from parsed files."""
        try:
            # Default to substack.com if no label specified
            if not label:
                label = "substack.com"
            
            # Get email metadata from database
            if label:
                emails = db.get_emails_by_label(label, max_age_days)
            else:
                emails = db.get_all_emails(max_age_days)
            
            documents = []
            
            for email in emails:
                # Filter by sender if specified
                if sender:
                    # Extract first name from sender and compare
                    sender_str = str(email.sender)
                    
                    # Try to extract from display name first (e.g., "Aakash Gupta from Product Growth <email@domain.com>")
                    if '<' in sender_str and '>' in sender_str:
                        display_name = sender_str.split('<')[0].strip()
                        if display_name:
                            # Get first word as first name
                            display_first_name = display_name.split()[0].title()
                            if display_first_name == sender:
                                # This email matches the sender filter
                                pass
                            else:
                                continue
                    else:
                        # Try to extract from email address
                        sender_email = clean_email_address(sender_str)
                        if sender_email:
                            # Extract first name from email
                            email_first_name = sender_email.split('@')[0].replace('+', '.').split('.')[0].title()
                            if email_first_name != sender:
                                continue
                        else:
                            # If we can't parse it, skip this email
                            continue
                
                # Read email content from file
                if not os.path.exists(email.parsed_path):
                    print(f"Warning: Email file not found: {email.parsed_path}")
                    continue
                
                try:
                    with open(email.parsed_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create document with metadata
                    metadata = {
                        'email_id': email.id,
                        'subject': email.subject,
                        'sender': str(email.sender),
                        'date': email.date.isoformat(),
                        'label': email.label,
                        'has_attachments': email.has_attachments,
                        'attachment_count': email.attachment_count,
                        'source_file': email.parsed_path
                    }
                    
                    documents.append(Document(content, metadata))
                    
                except Exception as e:
                    print(f"Error reading email file {email.parsed_path}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks with overlap."""
        chunked_docs = []
        
        for doc in documents:
            chunks = self._chunk_text(doc.content)
            
            for i, chunk in enumerate(chunks):
                # Create metadata for each chunk
                chunk_metadata = doc.metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['chunk_content'] = chunk[:100] + "..." if len(chunk) > 100 else chunk
                
                chunked_docs.append(Document(chunk, chunk_metadata))
        
        return chunked_docs
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start + self.chunk_size - 200, start)
                search_text = text[search_start:end]
                
                # Find the last sentence ending
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                last_ending = -1
                
                for ending in sentence_endings:
                    pos = search_text.rfind(ending)
                    if pos > last_ending:
                        last_ending = pos
                
                if last_ending != -1:
                    end = search_start + last_ending + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def get_document_stats(self, label: str = None, max_age_days: int = None) -> Dict[str, Any]:
        """Get statistics about available documents."""
        try:
            documents = self.load_documents(label, max_age_days)
            chunked_docs = self.chunk_documents(documents)
            
            total_content_length = sum(len(doc.content) for doc in documents)
            total_chunks = len(chunked_docs)
            
            # Get unique labels
            labels = set()
            for doc in documents:
                labels.add(doc.metadata.get('label', 'Unknown'))
            
            return {
                'total_documents': len(documents),
                'total_chunks': total_chunks,
                'total_content_length': total_content_length,
                'average_chunk_size': total_content_length // max(total_chunks, 1),
                'available_labels': list(labels),
                'label_filter': label,
                'max_age_days': max_age_days
            }
            
        except Exception as e:
            print(f"Error getting document stats: {e}")
            return {
                'total_documents': 0,
                'total_chunks': 0,
                'total_content_length': 0,
                'average_chunk_size': 0,
                'available_labels': [],
                'label_filter': label,
                'max_age_days': max_age_days,
                'error': str(e)
            }
    
    def search_documents(self, query: str, label: str = None, max_age_days: int = None, sender: str = None) -> List[Document]:
        """Simple text search in documents (fallback when embeddings not available)."""
        try:
            documents = self.load_documents(label, max_age_days, sender)
            chunked_docs = self.chunk_documents(documents)
            
            # Simple keyword search
            query_terms = query.lower().split()
            scored_docs = []
            
            for doc in chunked_docs:
                content_lower = doc.content.lower()
                score = 0
                
                for term in query_terms:
                    if term in content_lower:
                        score += content_lower.count(term)
                
                if score > 0:
                    scored_docs.append((score, doc))
            
            # Sort by score and return top results
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            return [doc for score, doc in scored_docs[:config.TOP_K_RETRIEVAL]]
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def simple_search(self, query: str, label: str = None, max_age_days: int = None, sender: str = None) -> List[Document]:
        """Simple search method for RAG pipeline fallback."""
        return self.search_documents(query, label, max_age_days, sender)

    def load_email_documents(self, file_paths: list) -> list:
        """Load email documents from a list of file paths."""
        documents = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Try to extract metadata from filename: <uuid>_<subject>.txt
                file_name = os.path.basename(file_path)
                email_id = file_name.split('_')[0]
                subject = file_name[len(email_id)+1:-4] if file_name.endswith('.txt') else file_name[len(email_id)+1:]
                metadata = {
                    'email_id': email_id,
                    'subject': subject,
                    'sender': 'Unknown',
                    'date': '',
                    'label': 'Unknown',
                    'has_attachments': False,
                    'attachment_count': 0,
                    'source_file': str(file_path)
                }
                documents.append(Document(content, metadata))
            except Exception as e:
                print(f"Error loading email document {file_path}: {e}")
                continue
        return documents

class NotebookDocumentSource:
    """Load and process notebook documents for RAG."""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        self.notebooks_dir = Path("notebooks")
    
    def load_documents(self, label: str = None, max_age_days: int = None) -> List[Document]:
        """Load notebook documents from JSON files."""
        try:
            if not self.notebooks_dir.exists():
                print("Warning: Notebooks directory not found")
                return []
            
            documents = []
            
            # Load all notebook JSON files
            for notebook_file in self.notebooks_dir.glob("*.json"):
                try:
                    with open(notebook_file, 'r', encoding='utf-8') as f:
                        notebook_data = json.load(f)
                    
                    # Extract content from blocks
                    content_parts = []
                    for block in notebook_data.get('blocks', []):
                        content_parts.append(block.get('text', ''))
                    
                    content = '\n\n'.join(content_parts)
                    
                    # Create metadata
                    metadata = {
                        'notebook_id': notebook_data.get('id'),
                        'title': notebook_data.get('title'),
                        'sender': notebook_data.get('metadata', {}).get('sender', 'Unknown'),
                        'date': notebook_data.get('metadata', {}).get('date'),
                        'label': notebook_data.get('metadata', {}).get('label', 'Unknown'),
                        'source': 'notebook',
                        'source_file': str(notebook_file)
                    }
                    
                    documents.append(Document(content, metadata))
                    
                except Exception as e:
                    print(f"Error reading notebook file {notebook_file}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            print(f"Error loading notebook documents: {e}")
            return []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks with overlap."""
        chunked_docs = []
        
        for doc in documents:
            chunks = self._chunk_text(doc.content)
            
            for i, chunk in enumerate(chunks):
                # Create metadata for each chunk
                chunk_metadata = doc.metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['chunk_content'] = chunk[:100] + "..." if len(chunk) > 100 else chunk
                
                chunked_docs.append(Document(chunk, chunk_metadata))
        
        return chunked_docs
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start + self.chunk_size - 200, start)
                search_text = text[search_start:end]
                
                # Find the last sentence ending
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                last_ending = -1
                
                for ending in sentence_endings:
                    pos = search_text.rfind(ending)
                    if pos > last_ending:
                        last_ending = pos
                
                if last_ending != -1:
                    end = search_start + last_ending + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def get_document_stats(self, label: str = None, max_age_days: int = None) -> Dict[str, Any]:
        """Get statistics about available notebook documents."""
        try:
            documents = self.load_documents(label, max_age_days)
            chunked_docs = self.chunk_documents(documents)
            
            total_content_length = sum(len(doc.content) for doc in documents)
            total_chunks = len(chunked_docs)
            
            # Get unique labels
            labels = set()
            for doc in documents:
                labels.add(doc.metadata.get('label', 'Unknown'))
            
            return {
                'total_documents': len(documents),
                'total_chunks': total_chunks,
                'total_content_length': total_content_length,
                'average_chunk_size': total_content_length // max(total_chunks, 1),
                'available_labels': list(labels),
                'label_filter': label,
                'max_age_days': max_age_days
            }
            
        except Exception as e:
            print(f"Error getting notebook document stats: {e}")
            return {
                'total_documents': 0,
                'total_chunks': 0,
                'total_content_length': 0,
                'average_chunk_size': 0,
                'available_labels': [],
                'label_filter': label,
                'max_age_days': max_age_days,
                'error': str(e)
            }

# Global document source instance
document_source = EmailDocumentSource()
notebook_source = NotebookDocumentSource() 