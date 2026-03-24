import uuid

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.product_repository.create(product)
        try:
            self.product_repository.commit()
        except SQLAlchemyError:
            self.product_repository.rollback()
            raise
        return self.product_repository.refresh(product)

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
    return ProductService(ProductRepository(db))
