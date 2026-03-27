from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, ConfigDict


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    price: float | None = None
    category: str | None = None
    similarity_score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
