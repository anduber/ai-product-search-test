from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal
from app.routers.product import product_router

app = FastAPI(title="AI Product Search")
app.include_router(product_router, prefix="/products")


@app.get("/health/db")
def health_db() -> dict[str, str]:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except SQLAlchemyError:
        return {"status": "error"}
    finally:
        db.close()
