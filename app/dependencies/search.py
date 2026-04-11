from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.runtime.embeddings.factory import get_embedding_service
from app.db.database import get_db
from app.services.search_service import SearchService


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    embedding_service = get_embedding_service()
    return SearchService(db=db, embedding_service=embedding_service)
