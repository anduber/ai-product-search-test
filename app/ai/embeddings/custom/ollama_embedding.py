import requests

from app.core.config import settings

from ..base import BaseEmbeddingService


class OllamaEmbeddingService(BaseEmbeddingService):
    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_EMBED_MODEL
        self.timeout = 30

    def embed_text(self, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=self.timeout,
        )
        if response.status_code != 200:
            response.raise_for_status()

        data = response.json()
        embedding = data.get("embedding")
        if not embedding:
            raise ValueError("Ollama returned an empty embedding")
        return embedding