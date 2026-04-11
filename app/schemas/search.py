from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float | None = None
    category: str | None = None
    similarity_score: float
    keyword_score: float
    final_score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
