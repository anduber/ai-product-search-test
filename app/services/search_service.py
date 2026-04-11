from __future__ import annotations

import logging

from fastapi import Depends
from sqlalchemy import case, func, literal, select
from sqlalchemy.orm import Session

from app.ai.runtime.embeddings import BaseEmbeddingService
from app.ai.runtime.embeddings.factory import get_embedding_service
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Product, ProductEmbedding
from app.schemas.search import SearchResponse, SearchResult
from app.services.query_understanding import QueryUnderstandingService

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: Session, embedding_service: BaseEmbeddingService):
        self.db = db
        self.embedding_service = embedding_service
        self.query_understanding = QueryUnderstandingService()

    def _extract_keywords(self, query: str) -> list[str]:
        return [token for token in query.strip().lower().split() if len(token) >= 2]

    def _build_keyword_score_expression(self, keywords: list[str]):
        if not keywords:
            return literal(0.0)

        per_keyword_scores = [
            func.greatest(
                case((Product.name.ilike(f"%{kw}%"), literal(1.0)), else_=literal(0.0)),
                case((Product.description.ilike(f"%{kw}%"), literal(0.5)), else_=literal(0.0)),
            )
            for kw in keywords
        ]

        raw_sum = sum(per_keyword_scores[1:], per_keyword_scores[0])
        return raw_sum / literal(float(len(keywords)))

    def search_products(self, query: str, limit: int = 10) -> SearchResponse:
        processed_query = self.query_understanding.process(query)
        keywords = self._extract_keywords(processed_query)

        try:
            query_embedding = self.embedding_service.embed_text(processed_query)
        except Exception as exc:
            logger.exception("Failed to generate query embedding")
            raise RuntimeError("Failed to generate query embedding") from exc

        cosine_distance = ProductEmbedding.embedding.cosine_distance(query_embedding)
        similarity_expr = literal(1.0) - cosine_distance
        similarity_score = similarity_expr.label("similarity_score")
        keyword_score = self._build_keyword_score_expression(keywords).label("keyword_score")
        final_score = (
                (literal(0.8) * similarity_expr) + (literal(0.2) * keyword_score)
        ).label("final_score")

        stmt = (
            select(
                Product.id,
                Product.name,
                Product.description,
                Product.price,
                Product.category,
                similarity_score,
                keyword_score,
                final_score,
            )
            .join(ProductEmbedding, ProductEmbedding.product_id == Product.id)
            .where(similarity_expr >= settings.SEARCH_MIN_SIMILARITY)
            .order_by(final_score.desc())
            .limit(max(1, min(limit, 50)))
        )

        rows = self.db.execute(stmt).all()
        results = [
            SearchResult(
                id=str(row.id),
                name=row.name,
                description=row.description,
                price=row.price,
                category=row.category,
                similarity_score=round(float(row.similarity_score or 0.0), 4),
                keyword_score=round(float(row.keyword_score or 0.0), 4),
                final_score=round(float(row.final_score or 0.0), 4),
            )
            for row in rows
        ]
        return SearchResponse(results=results)


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    embedding_service = get_embedding_service()
    return SearchService(db=db, embedding_service=embedding_service)
