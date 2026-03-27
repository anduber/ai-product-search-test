from __future__ import annotations

import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.embeddings import BaseEmbeddingService
from app.ai.embeddings.factory import get_embedding_service
from app.db.database import get_db
from app.db.models import Product, ProductEmbedding
from app.schemas.search import SearchResponse, SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: Session, embedding_service: BaseEmbeddingService):
        self.db = db
        self.embedding_service = embedding_service

    def search_products(self, query: str, limit: int = 10) -> SearchResponse:
        try:
            query_embedding = self.embedding_service.embed_text(query)
        except Exception as exc:
            logger.exception("Failed to generate query embedding")
            raise RuntimeError("Failed to generate query embedding") from exc

        stmt = (
            select(
                Product.id,
                Product.name,
                Product.description,
                Product.price,
                Product.category,
                ProductEmbedding.embedding.cosine_distance(query_embedding).label("cosine_distance"),
            )
            .join(ProductEmbedding, ProductEmbedding.product_id == Product.id)
            .order_by(ProductEmbedding.embedding.cosine_distance(query_embedding).asc())
            .limit(limit)
        )

        rows = self.db.execute(stmt).all()
        results = [
            SearchResult(
                id=str(row.id),
                name=row.name,
                description=row.description,
                price=row.price,
                category=row.category,
                similarity_score=max(0.0, 1.0 - float(row.cosine_distance or 0.0)),
            )
            for row in rows
        ]
        return SearchResponse(results=results)


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    embedding_service = get_embedding_service()
    return SearchService(db=db, embedding_service=embedding_service)
