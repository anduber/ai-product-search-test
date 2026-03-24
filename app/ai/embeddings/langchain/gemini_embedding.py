import os
from ..base import BaseEmbeddingService

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
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
            
        model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
        # LangChain uses 'model' instead of 'model_name' in newer versions usually
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key,
            output_dimensionality=1536
        )

    def embed_text(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)
