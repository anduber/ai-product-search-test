import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(db, Product)

    def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self.get(product_id)

    def list_products(self) -> list[Product]:
        return self.list()

    def search_by_embedding(self, query_vector: list[float]) -> list[Product]:
        """Search products by vector similarity."""
        pass

    def get_products_with_reviews(self) -> list[tuple[Product, Any]]:
        """Return products joined with their reviews."""
        pass

    def get_top_rated_products(self) -> list[Product]:
        """Return products ordered by highest average rating."""
        pass
