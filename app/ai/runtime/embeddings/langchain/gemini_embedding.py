from ..base import BaseEmbeddingService
from app.core.config import settings

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:  # pragma: no cover
    GoogleGenerativeAIEmbeddings = None


class LangchainGeminiEmbeddingService(BaseEmbeddingService):
    def __init__(self) -> None:
        if GoogleGenerativeAIEmbeddings is None:
            raise RuntimeError(
                "langchain-google-genai is not installed. "
                "Please run `pip install langchain-google-genai`."
            )
        
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
            
        model = settings.GEMINI_EMBEDDING_MODEL
        # LangChain uses 'model' instead of 'model_name' in newer versions usually
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key,
            output_dimensionality=settings.EMBEDDING_DIM
        )

    def embed_text(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)
