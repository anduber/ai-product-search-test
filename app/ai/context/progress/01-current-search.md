# Feature: AI Product Search System

## System Overview

FastAPI application backed by PostgreSQL + pgvector that embeds product data at ingestion time
and retrieves results through a hybrid scoring pipeline at query time.

**Stack:**
- Python 3.12, FastAPI, SQLAlchemy 2.x (ORM only — no raw SQL)
- PostgreSQL with pgvector extension (`Vector(1024)` columns)
- Alembic for schema migrations
- Pluggable embedding backends: Gemini (custom & LangChain) and Ollama (custom & LangChain)

## What Is Implemented    

### Embedding System (`app/ai/runtime/embeddings/`)
- `BaseEmbeddingService` — abstract base class with `embed_text(text: str) -> list[float]`
- `factory.py` — `get_embedding_service()` reads `EMBEDDING_PROVIDER` + `EMBEDDING_BACKEND` from env
- **Custom backends:** `GeminiEmbeddingService`, `OllamaEmbeddingService` (direct HTTP calls)
- **LangChain backends:** `LangchainGeminiEmbeddingService`, `LangchainOllamaEmbeddingService`
- Backward-compat shim at `app/ai/embeddings/` so existing import paths are unbroken

### Database Models (`app/db/models/`)
- `Product` — id (UUID), name, description, price, category, created_at; has `reviews` + `embeddings` relationships
- `ProductEmbedding` — id, product_id (FK→products, CASCADE), `embedding Vector(1024)`, text_content
- `ProductReview` — exists in schema, not yet wired to search scoring

### Repositories (`app/repositories/`)
- `BaseRepository` — generic CRUD
- `ProductRepository` — list, paginate, get by id
- `ProductEmbeddingRepository` — create_embedding, add_all

### Services (`app/services/`)
- `ProductService` — single + bulk product creation with auto-embedding; paginated listing
- `SearchService` — full hybrid search pipeline (see below)
- `QueryUnderstandingService` — rule-based query preprocessing (normalize → synonyms → expand)

### Search Pipeline (`app/services/search_service.py`)
Hybrid scoring with two signals combined into `final_score`:

| Signal | Weight | How |
|---|---|---|
| Semantic similarity | 0.8 | `1 - cosine_distance(query_embedding, product_embedding)` |
| Keyword match | 0.2 | Per-keyword weighted: name match=1.0, description match=0.5, normalized by keyword count |

- Filters: `similarity >= SEARCH_MIN_SIMILARITY` (default 0.45, env-configurable)
- Limit: 1–50 (clamped), default 10
- Fully SQLAlchemy ORM — uses `select()`, `.join()`, `.where()`, `.order_by()`

### API Routers
- `POST /products/` — create single product
- `POST /products/bulk` — bulk create
- `GET /products/` — paginated list
- `GET /products/{id}` — get by id
- `POST /search/` — hybrid search (body: `{query, limit}`)
- `GET /health/db` — DB connectivity probe

### Config (`app/core/config.py`)
Env vars read at startup via `Settings`: `DATABASE_URL`, `GOOGLE_API_KEY`,
`GEMINI_EMBEDDING_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_EMBED_MODEL`,
`EMBEDDING_PROVIDER`, `EMBEDDING_BACKEND`, `EMBEDDING_DIM`, `SEARCH_MIN_SIMILARITY`

## Known Issues

- `ProductEmbedding.embedding` is declared as `Vector(1024)` in the ORM model but
  `EMBEDDING_DIM` defaults to 1536. If the model outputs 1536-dim vectors the DB insert
  will fail — they must be kept in sync.
- `ProductService.search_products()` and `get_top_products()` are stubs (return `None`).
- No authentication or rate-limiting on any endpoint.
- No test suite exists yet.
- Keyword scoring is weighted (name=1.0, desc=0.5, normalized) — binary version replaced.
- `ProductReview` model is defined but unused in search ranking.

## Next Steps

- [ ] Align `Vector(dim)` in the model with `EMBEDDING_DIM` (single source of truth)
- [ ] Add async DB sessions (`AsyncSession`) for production load
- [ ] Implement review-based ranking signal in `SearchService`
- [ ] Add category + price filter parameters to search endpoint
- [ ] Write unit tests for `SearchService` and `ProductService`
- [ ] Add re-ranking step (cross-encoder or rule-based) after initial retrieval
- [ ] Implement `ProductService.search_products()` as a thin wrapper over `SearchService`
