# AGENTS.md — Universal AI Instructions

This file is the single source of truth for all AI coding assistants working on this project.
It applies to Cursor, Claude, Codex, Windsurf, and any other AI tool.
Read this file completely before writing or modifying any code.

---

## 1. Project Overview

**AI Product Search** is a FastAPI service that allows semantic + keyword hybrid search over a
product catalogue. Products are embedded at ingestion time and retrieved via a weighted scoring
pipeline backed by PostgreSQL + pgvector.

```
app/
  ai/
    runtime/         ← execution code (embeddings, future: ranking, reranking)
      embeddings/
        custom/      ← direct API integrations (Gemini, Ollama)
        langchain/   ← LangChain wrappers
        base.py      ← BaseEmbeddingService ABC
        factory.py   ← get_embedding_service() factory
    context/         ← AI memory (never imported by Python code)
      progress/      ← feature progress notes
      decisions/     ← architecture decision records
      experiments/   ← experiment results
      prompts/       ← reusable prompt templates
  core/config.py     ← all env-var settings via Settings class
  db/
    database.py      ← SQLAlchemy engine + SessionLocal + Base
    models/          ← ORM models only
  repositories/      ← data access layer (one repo per model)
  services/          ← business logic layer
  routers/           ← FastAPI route handlers
  schemas/           ← Pydantic request/response models
  utils/             ← pure helper functions
```

---

## 2. Architecture Rules

1. **Layering is strict:** routers → services → repositories → models. Never skip a layer.
2. Routers inject dependencies via FastAPI `Depends()`. Never instantiate services manually in a router.
3. Business logic lives in services only. Repositories do data access only.
4. Never put SQL or ORM queries in a router or service directly — use a repository method.
5. All configuration is read from environment variables through `app.core.config.Settings`.
   Never hard-code URLs, keys, or numeric thresholds anywhere else.
6. After every significant change, update `app/ai/context/progress/` with a file following
   `template.md`. This keeps AI memory current across sessions.

---

## 3. Database Design

**Engine:** PostgreSQL with the `pgvector` extension.
**ORM:** SQLAlchemy 2.x declarative models. **Never write raw SQL strings.**
**Migrations:** Alembic. Always generate a migration after any model change.

### Core Tables

| Table | Key Columns | Notes |
|---|---|---|
| `products` | id (UUID PK), name, description, price, category, created_at | `created_at` defaults to `func.now()` server-side |
| `product_embeddings` | id (UUID PK), product_id (FK→products CASCADE), embedding Vector(N), text_content | N must equal `settings.EMBEDDING_DIM` |
| `product_reviews` | id, product_id (FK), rating, content | Not yet used in search scoring |

### Rules

- Every `Product` must have exactly one `ProductEmbedding` row after creation.
- The `Vector(N)` dimension in `ProductEmbedding` **must** match `settings.EMBEDDING_DIM`.
  These must never drift — treat `EMBEDDING_DIM` as the single source of truth.
- Use `UUID(as_uuid=True)` + `default=uuid.uuid4` for all primary keys.
- Use `cascade="all, delete-orphan"` on all child relationships.
- Use `Mapped` + `mapped_column` (SQLAlchemy 2.x style). Do not use the legacy `Column()` API.

---

## 4. Embedding System Rules

**Location:** `app/ai/runtime/embeddings/`
**Entry point:** `get_embedding_service()` in `factory.py`

### Provider / Backend matrix

| `EMBEDDING_PROVIDER` | `EMBEDDING_BACKEND` | Class |
|---|---|---|
| `gemini` | `custom` | `GeminiEmbeddingService` |
| `gemini` | `langchain` | `LangchainGeminiEmbeddingService` |
| `ollama` | *(any)* | `OllamaEmbeddingService` |
| `ollama_langchain` | *(any)* | `LangchainOllamaEmbeddingService` |

### Rules

- All providers must subclass `BaseEmbeddingService` and implement `embed_text(text: str) -> list[float]`.
- The returned vector length must always equal `settings.EMBEDDING_DIM`. Raise `RuntimeError` if not.
- To add a new provider: create a file in `custom/` or `langchain/`, subclass `BaseEmbeddingService`,
  add a value to `EmbeddingProvider` enum, add a branch in `factory.py`.
- **Never** call an embedding provider directly from a service or router — always go through the factory.
- Backward-compat shims exist at `app/ai/embeddings/` so old import paths keep working.
  Do not remove the shim files.

---

## 5. Search System Logic

**File:** `app/services/search_service.py`

### Pipeline (in order)

1. Normalize query: `query.strip().lower()`
2. Extract keywords: tokens with length ≥ 2
3. Generate query embedding via `embedding_service.embed_text()`
4. Execute a single SQLAlchemy `select()` with:
   - `JOIN product_embeddings ON product_embeddings.product_id = products.id`
   - `WHERE (1 - cosine_distance) >= SEARCH_MIN_SIMILARITY`
   - Compute `similarity_score = 1 - cosine_distance`
   - Compute `keyword_score = CASE WHEN name/description ILIKE %kw% THEN 1.0 ELSE 0.0`
   - Compute `final_score = 0.8 * similarity_score + 0.2 * keyword_score`
   - `ORDER BY final_score DESC`
   - `LIMIT max(1, min(limit, 50))`
5. Map rows to `SearchResult` Pydantic objects

### Rules

- Weights (0.8 / 0.2) are currently hard-coded. Externalize to config before adding a third signal.
- `SEARCH_MIN_SIMILARITY` defaults to 0.45 and is read from env. Never hard-code the threshold.
- Do not use raw SQL. All filter/score logic must be expressed with SQLAlchemy core expressions.
- When adding a new ranking signal (e.g. review score), add it to the `final_score` expression and
  update the weight constants. Document the change in `app/ai/context/decisions/`.

---

## 6. Coding Rules

- **Python 3.12.** Use modern syntax: `str | None`, `list[float]`, `match` statements where appropriate.
- **No raw SQL.** Every DB interaction goes through SQLAlchemy ORM or core expressions.
- **Pydantic v2** for all request/response schemas. Use `model_dump()`, not `.dict()`.
- Type-annotate all function signatures (args + return type).
- Use `logging.getLogger(__name__)` — never `print()` for diagnostic output.
- Keep services, repositories, and routers in separate files. One class per file is preferred.
- Do not add comments or docstrings unless the logic is genuinely non-obvious.
- `app/ai/context/` directories contain Markdown only — never import them in Python.

---

## 7. Performance Constraints

- Max search `limit` is **50** (enforced in `SearchService` and validated by Pydantic `Field(le=50)`).
- Embedding calls are synchronous; keep them outside of DB transactions where possible.
- The pgvector index (IVFFlat or HNSW) must exist on `product_embeddings.embedding` before
  the table exceeds ~10k rows. Add the index in an Alembic migration.
- Bulk product creation (`create_products_bulk`) should accumulate all `ProductEmbedding` objects
  then call `add_all()` once — do not loop individual DB inserts.
- Never load all products into memory for search — always push filtering and ranking to the DB.

---

## 8. AI Memory Rules

- `app/ai/context/` is the persistent memory layer for AI assistants.
- **After every feature addition or refactor**, create or update a file in `app/ai/context/progress/`
  using the format in `template.md`.
- `app/ai/context/decisions/` — record any significant architectural choice as `NN-title.md`.
- `app/ai/context/experiments/` — record embedding model or scoring experiments with results.
- `app/ai/context/prompts/` — store reusable prompt templates for data generation or testing.
- These files must be committed to version control alongside the code changes they describe.
- When starting a new session, read `app/ai/context/progress/` first to restore working context.
