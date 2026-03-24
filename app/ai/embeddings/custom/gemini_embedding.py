import os
from collections.abc import Sequence
from ..base import BaseEmbeddingService

try:
    from google import genai
    from google.genai.types import EmbedContentConfig
except ImportError:  # pragma: no cover
    genai = None
    EmbedContentConfig = None


class GeminiEmbeddingService(BaseEmbeddingService):
    def _normalize_model(self, model: str) -> str:
        return model.removeprefix("models/")

    def __init__(self) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
        self.output_dimensionality = int(os.getenv("GEMINI_EMBEDDING_DIM", "1536"))
        self.client = genai.Client(api_key=self.api_key) if genai is not None and self.api_key else None

    def embed_text(self, text: str) -> list[float]:
        if self.client is None:
            if genai is None:
                raise RuntimeError("google-genai is not installed")
            raise RuntimeError("GOOGLE_API_KEY is not set")

        model = self._normalize_model(self.model)
        if EmbedContentConfig is not None:
            config = EmbedContentConfig(output_dimensionality=self.output_dimensionality)
            result = self.client.models.embed_content(model=model, contents=text, config=config)
        else:
            result = self.client.models.embed_content(model=model, contents=text)

        embeddings = result.get("embeddings") if isinstance(result, dict) else getattr(result, "embeddings", None)
        if embeddings is None:
            raise RuntimeError("Gemini embedding response missing embeddings")

        if isinstance(embeddings, Sequence) and embeddings:
            first = embeddings[0]
            values = None
            if isinstance(first, dict):
                values = first.get("values") or first.get("embedding")
            else:
                values = getattr(first, "values", None) or getattr(first, "embedding", None)
            if values is None and isinstance(first, Sequence):
                values = first
            if values is None:
                raise RuntimeError("Gemini embedding response missing embedding values")
            vector = [float(x) for x in values]
            if len(vector) > self.output_dimensionality:
                return vector[: self.output_dimensionality]
            if len(vector) < self.output_dimensionality:
                raise RuntimeError(f"Embedding dim {len(vector)} != expected {self.output_dimensionality}")
            return vector

        if isinstance(embeddings, Sequence):
            vector = [float(x) for x in embeddings]
            if len(vector) > self.output_dimensionality:
                return vector[: self.output_dimensionality]
            if len(vector) < self.output_dimensionality:
                raise RuntimeError(f"Embedding dim {len(vector)} != expected {self.output_dimensionality}")
            return vector

        raise RuntimeError("Gemini embedding has unexpected type")
