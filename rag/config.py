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
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")  # openai, sentence-transformers, cohere
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # OpenAI's best model
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))  # OpenAI's dimension
    USE_SENTENCE_TRANSFORMERS: bool = os.getenv("USE_SENTENCE_TRANSFORMERS", "false").lower() == "true"
    
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
        if self.EMBEDDING_PROVIDER == "nomic":
            # Nomic is free, no API key needed
            return True
        elif self.EMBEDDING_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set for OpenAI embeddings.")
            return False
        elif self.EMBEDDING_PROVIDER == "cohere" and not self.COHERE_API_KEY:
            print("Warning: COHERE_API_KEY not set for Cohere embeddings.")
            return False
        return True

# Global settings instance
settings = RAGSettings() 