import uuid

from sqlalchemy.orm import Session

from app.db.models import ProductEmbedding
from app.repositories.base import BaseRepository


class ProductEmbeddingRepository(BaseRepository[ProductEmbedding]):
    def __init__(self, db: Session):
        super().__init__(db, ProductEmbedding)

    def create_embedding(
        self,
        product_id: uuid.UUID,
        embedding: list[float],
        text: str,
    ) -> ProductEmbedding:
        obj = ProductEmbedding(product_id=product_id, embedding=embedding, text_content=text)
        return self.create(obj)
