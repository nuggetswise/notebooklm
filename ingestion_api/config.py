import os
from pathlib import Path
from typing import Optional

class Config:
    """Optimized configuration for production deployment."""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT != "production"
    
    # Server settings
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", "8080"))
    WORKERS = int(os.getenv("WORKERS", "1"))
    
    # Data paths
    BASE_DIR = Path("/app" if ENVIRONMENT == "production" else ".")
    DATA_DIR = BASE_DIR / "data"
    VECTOR_STORE_DIR = DATA_DIR / "vector_store"
    PARSED_EMAILS_DIR = DATA_DIR / "parsed_emails"
    
    # RAG settings (optimized for cost)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "800"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Embedding settings (cost-optimized)
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "nomic")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    NOMIC_INFERENCE_MODE = os.getenv("NOMIC_INFERENCE_MODE", "local")
    
    # API Keys (optional for local embeddings)
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/email_index.db")
    
    # Email settings
    MAX_AGE_DAYS = int(os.getenv("MAX_AGE_DAYS", "30"))
    DEFAULT_LABEL = os.getenv("DEFAULT_LABEL", "substack.com")
    
    # Performance settings
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration for production."""
        if cls.ENVIRONMENT == "production":
            try:
                # Ensure data directories exist
                cls.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
                cls.PARSED_EMAILS_DIR.mkdir(parents=True, exist_ok=True)
                
                # Validate embedding provider
                if cls.EMBEDDING_PROVIDER == "nomic":
                    if cls.NOMIC_INFERENCE_MODE != "local":
                        print("⚠️  Warning: Using remote Nomic embeddings may incur costs")
                
                # Check for required API keys if using paid services
                if cls.EMBEDDING_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
                    print("⚠️  Warning: OpenAI API key not set")
            except Exception as e:
                print(f"⚠️  Warning: Could not validate production config: {e}")
        
        return True

# Global config instance
config = Config()
config.validate() 