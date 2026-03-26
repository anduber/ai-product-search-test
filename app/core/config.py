import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class EmbeddingProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"

class EmbeddingBackend(str, Enum):
    CUSTOM = "custom"
    LANGCHAIN = "langchain"

class Settings:
    def __init__(self):
        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/ai_product_search")

        # AI / Embeddings
        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
        self.GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
        
        provider_raw = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
        self.EMBEDDING_PROVIDER: EmbeddingProvider = EmbeddingProvider(provider_raw)
        
        backend_raw = os.getenv("EMBEDDING_BACKEND", "custom").lower()
        self.EMBEDDING_BACKEND: EmbeddingBackend = EmbeddingBackend(backend_raw)
        
        self.EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "1536"))

settings = Settings()
