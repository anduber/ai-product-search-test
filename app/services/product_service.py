import uuid
import logging

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Product
from app.ai.embeddings import EmbeddingService
from app.repositories.product_embedding_repository import ProductEmbeddingRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate
from app.utils.text_builder import build_product_text

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        embedding_repository: ProductEmbeddingRepository,
        embedding_service: EmbeddingService,
    ):
        self.product_repository = product_repository
        self.embedding_repository = embedding_repository
        self.embedding_service = embedding_service

    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.product_repository.create(product)
        try:
            self.product_repository.commit()
        except SQLAlchemyError:
            self.product_repository.rollback()
            raise
        product = self.product_repository.refresh(product)

        try:
            text = build_product_text(product)
            print("embedded text:", text)
            if text:
                embedding = self.embedding_service.embed_text(text)
                self.embedding_repository.create_embedding(product.id, embedding, text)
                self.embedding_repository.commit()
        except Exception:
            self.embedding_repository.rollback()
            logger.exception("Failed to generate/store embedding for product_id=%s", product.id)

        return product

    def get_product(self, product_id: uuid.UUID) -> Product | None:
        return self.product_repository.get_by_id(product_id)

    def list_products(self) -> list[Product]:
        return self.product_repository.list_products()

    def get_all_products(self) -> list[Product]:
        return self.list_products()

    def get_product_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self.get_product(product_id)

    def search_products(self, query: str) -> list[Product]:
        """Search products by query text (future: vector search, ranking, filters)."""
        pass

    def get_top_products(self) -> list[Product]:
        """Return top products (future: combine ratings, relevance, popularity)."""
        pass


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repo = ProductRepository(db)
    embedding_repo = ProductEmbeddingRepository(db)
    embedding_service = EmbeddingService()
    return ProductService(product_repo, embedding_repo, embedding_service)
