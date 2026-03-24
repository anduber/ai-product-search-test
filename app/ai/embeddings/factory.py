import os
from .base import BaseEmbeddingService
from .custom.gemini_embedding import GeminiEmbeddingService
from .langchain.gemini_embedding import LangchainGeminiEmbeddingService

def get_embedding_service() -> BaseEmbeddingService:
    """
    Factory function to get the configured embedding service.
    
    Reads from environment variables:
    - EMBEDDING_PROVIDER: e.g. "gemini" (default: "gemini")
    - EMBEDDING_BACKEND: "custom" or "langchain" (default: "custom")
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
    backend = os.getenv("EMBEDDING_BACKEND", "custom").lower()

    if provider == "gemini":
        if backend == "custom":
            return GeminiEmbeddingService()
        elif backend == "langchain":
            return LangchainGeminiEmbeddingService()
        else:
            raise ValueError(f"Unsupported embedding backend for gemini: {backend}")
    
    raise ValueError(f"Unsupported embedding provider: {provider}")
