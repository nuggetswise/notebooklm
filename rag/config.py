import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGSettings:
    """Configuration settings for the RAG pipeline."""
    
    # API Keys
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "3"))
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "embed-english-v3.0"
    EMBEDDING_DIMENSION: int = 1024
    
    # Generation Settings
    GENERATION_MODEL: str = "command"
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "800"))
    TEMPERATURE: float = 0.7
    
    # Provider-specific limits
    COHERE_MAX_TOKENS: int = 4000
    GROQ_MAX_TOKENS: int = 8000
    GEMINI_MAX_TOKENS: int = 1000000
    
    # Storage Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    PARSED_EMAILS_DIR: Path = DATA_DIR / "parsed_emails"
    VECTOR_STORE_DIR: Path = DATA_DIR / "vector_store"
    
    # Development
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __post_init__(self):
        """Ensure required directories exist."""
        self.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present."""
        if not self.COHERE_API_KEY and not self.GEMINI_API_KEY:
            print("Warning: Neither COHERE_API_KEY nor GEMINI_API_KEY set. RAG functionality will be limited.")
            return False
        return True

# Global settings instance
settings = RAGSettings() 