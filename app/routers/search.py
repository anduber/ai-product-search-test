from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.search import get_search_service
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

search_router = APIRouter()


@search_router.post("/", response_model=SearchResponse)
def search_products_endpoint(
    payload: SearchRequest,
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    try:
        return service.search_products(payload.query, payload.limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
