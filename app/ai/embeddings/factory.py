from .base import BaseEmbeddingService
from .custom.gemini_embedding import GeminiEmbeddingService
from .langchain.gemini_embedding import LangchainGeminiEmbeddingService
from app.core.config import settings, EmbeddingProvider, EmbeddingBackend

def get_embedding_service() -> BaseEmbeddingService:
    """
    Factory function to get the configured embedding service.
    
    Uses settings from app.core.config.
    """
    provider = settings.EMBEDDING_PROVIDER
    backend = settings.EMBEDDING_BACKEND

    if provider == EmbeddingProvider.GEMINI:
        if backend == EmbeddingBackend.CUSTOM:
            return GeminiEmbeddingService()
        elif backend == EmbeddingBackend.LANGCHAIN:
            return LangchainGeminiEmbeddingService()
        else:
            raise ValueError(f"Unsupported embedding backend for gemini: {backend}")
    
    raise ValueError(f"Unsupported embedding provider: {provider}")
