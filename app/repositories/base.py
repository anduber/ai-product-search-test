from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id: Any) -> ModelType | None:
        return self.db.get(self.model, id)

    def list(self) -> list[ModelType]:
        stmt = select(self.model)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        return obj

    def flush(self) -> None:
        self.db.flush()

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, obj: ModelType) -> ModelType:
        self.db.refresh(obj)
        return obj
