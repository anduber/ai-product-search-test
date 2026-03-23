import uuid

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Product
from app.schemas.product import ProductCreate


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.db.add(product)
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
        self.db.refresh(product)
        return product

    def get_all_products(self) -> list[Product]:
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)
