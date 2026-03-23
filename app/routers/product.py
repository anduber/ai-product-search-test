import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService, get_product_service

product_router = APIRouter()


@product_router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    try:
        product = service.create_product(product_data)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create product") from exc
    return product


@product_router.get("/", response_model=list[ProductResponse])
async def get_all_products_endpoint(
    service: ProductService = Depends(get_product_service),
) -> list[ProductResponse]:
    return service.get_all_products()


@product_router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id_endpoint(
    product_id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    product = service.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
