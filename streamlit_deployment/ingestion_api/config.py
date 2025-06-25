import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the email ingestion API."""
    
    # API Keys
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Email Processing
    MAX_AGE_DAYS: int = int(os.getenv("MAX_AGE_DAYS", "30"))
    DEFAULT_LABEL: str = os.getenv("DEFAULT_LABEL", "AI")
    SMTP2HTTP_PORT: int = int(os.getenv("SMTP2HTTP_PORT", "8025"))
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "2000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    
    # Storage Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    PARSED_EMAILS_DIR: Path = DATA_DIR / "parsed_emails"
    MAILDIR_DIR: Path = DATA_DIR / "maildir"
    
    # Development
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __post_init__(self):
        """Ensure required directories exist."""
        self.PARSED_EMAILS_DIR.mkdir(parents=True, exist_ok=True)
        self.MAILDIR_DIR.mkdir(parents=True, exist_ok=True)
        (self.MAILDIR_DIR / "cur").mkdir(parents=True, exist_ok=True)
        (self.MAILDIR_DIR / "new").mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings() 