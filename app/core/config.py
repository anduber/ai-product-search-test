import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class EmbeddingProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    OLLAMA_LANGCHAIN = "ollama_langchain"


class EmbeddingBackend(str, Enum):
    CUSTOM = "custom"
    LANGCHAIN = "langchain"


class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
        self.GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
        self.OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

        provider_raw = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
        self.EMBEDDING_PROVIDER: EmbeddingProvider = EmbeddingProvider(provider_raw)

        backend_raw = os.getenv("EMBEDDING_BACKEND", "custom").lower()
        self.EMBEDDING_BACKEND: EmbeddingBackend = EmbeddingBackend(backend_raw)

        self.EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "1536"))
        self.SEARCH_MIN_SIMILARITY: float = float(os.getenv("SEARCH_MIN_SIMILARITY", "0.45"))

settings = Settings()
