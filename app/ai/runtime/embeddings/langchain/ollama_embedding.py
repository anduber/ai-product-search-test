from langchain_ollama import OllamaEmbeddings

from app.core.config import settings

from ..base import BaseEmbeddingService


class LangchainOllamaEmbeddingService(BaseEmbeddingService):
    def __init__(self) -> None:
        self.embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    def embed_text(self, text: str) -> list[float]:
        embedding = self.embeddings.embed_query(text)
        if not embedding:
            raise ValueError("LangChain Ollama returned an empty embedding")
        return embedding