from app.core.config import EmbeddingBackend, EmbeddingProvider, settings

from .base import BaseEmbeddingService
from .custom.gemini_embedding import GeminiEmbeddingService
from .custom.ollama_embedding import OllamaEmbeddingService
from .langchain.gemini_embedding import LangchainGeminiEmbeddingService
from .langchain.ollama_embedding import LangchainOllamaEmbeddingService


def get_embedding_service() -> BaseEmbeddingService:
    provider = settings.EMBEDDING_PROVIDER
    backend = settings.EMBEDDING_BACKEND

    if provider == EmbeddingProvider.GEMINI:
        if backend == EmbeddingBackend.CUSTOM:
            return GeminiEmbeddingService()
        if backend == EmbeddingBackend.LANGCHAIN:
            return LangchainGeminiEmbeddingService()
        raise ValueError(f"Unsupported embedding backend for gemini: {backend}")

    if provider == EmbeddingProvider.OLLAMA:
        return OllamaEmbeddingService()

    if provider == EmbeddingProvider.OLLAMA_LANGCHAIN:
        return LangchainOllamaEmbeddingService()

    raise ValueError(f"Unsupported embedding provider: {provider}")
