from abc import ABC, abstractmethod

class BaseEmbeddingService(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for the given text."""
        raise NotImplementedError
