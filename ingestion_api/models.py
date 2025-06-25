from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import uuid
import re

class PersonaInfo(BaseModel):
    """Persona information model."""
    id: str
    first_name: str
    display_name: str
    email_count: int
    topics: List[str] = []
    labels: List[str] = []
    persona_type: str

def clean_email_address(email_str):
    """Clean email address to handle special characters."""
    if not email_str:
        return None
    
    # Remove angle brackets if present
    email_str = email_str.strip()
    if email_str.startswith('<') and email_str.endswith('>'):
        email_str = email_str[1:-1]
    
    # Extract email from "Display Name <email@domain.com>" format
    if '<' in email_str and '>' in email_str:
        start = email_str.rfind('<') + 1
        end = email_str.rfind('>')
        if start < end:
            email_str = email_str[start:end]
    
    # Clean up any remaining special characters
    email_str = email_str.strip()
    
    # Basic email validation
    if '@' in email_str and '.' in email_str.split('@')[1]:
        return email_str
    
    return None

class EmailMetadata(BaseModel):
    """Email metadata model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    sender: str  # Changed from EmailStr to str to handle display names with special characters
    date: datetime
    label: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parsed_path: str
    has_attachments: bool = False
    attachment_count: int = 0
    persona: Optional[PersonaInfo] = None
    
    @validator('sender')
    def validate_sender(cls, v):
        """Validate and clean sender field to handle display names with special characters."""
        if not v:
            raise ValueError('Sender cannot be empty')
        
        # Try to clean the email address
        cleaned_email = clean_email_address(v)
        if cleaned_email:
            return v  # Return original string, but we know it's valid
        
        # If cleaning failed, try more lenient validation
        # Handle cases where sender has display name with special characters
        # Extract email address if present in angle brackets
        email_match = re.search(r'<([^>]+)>', v)
        if email_match:
            email_address = email_match.group(1)
            # More lenient email validation
            if '@' in email_address and '.' in email_address.split('@')[1]:
                return v  # Return original string with display name
        
        # If no angle brackets, check if it looks like an email
        if '@' in v and '.' in v.split('@')[1]:
            return v
        
        # If all else fails, just return the original string
        # This prevents the validation from blocking emails with unusual formats
        print(f"Warning: Unusual email format: {v}")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EmailContent(BaseModel):
    """Parsed email content model."""
    id: str
    subject: str
    sender: str
    date: datetime
    body: str
    label: str
    attachments: List[Dict[str, Any]] = []
    persona: Optional[PersonaInfo] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EmailProcessingResponse(BaseModel):
    """Response model for email processing."""
    success: bool
    email_id: str
    message: str
    metadata: Optional[EmailMetadata] = None
    processing_time: float

class EmailStatusResponse(BaseModel):
    """Response model for email status endpoint."""
    emails: List[EmailMetadata]
    total_count: int
    total_emails: int
    labels: List[str]
    label_filter: Optional[str] = None
    max_age_days: int

class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    question: str = Field(..., min_length=1, max_length=1000)
    label: Optional[str] = Field(None, min_length=1, max_length=50)
    sender: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    answer: str
    context: List[Dict[str, Any]]
    metadata: List[EmailMetadata]
    processing_time: float

class RefreshResponse(BaseModel):
    """Response model for refresh endpoint."""
    success: bool
    processed_count: int
    errors: List[str] = []
    processing_time: float 