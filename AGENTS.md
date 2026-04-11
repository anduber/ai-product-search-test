# AGENTS.md — AI Product Search System

This file is the universal instruction set for all AI coding assistants (Cursor, Claude, Codex, Windsurf).

It provides high-level context and rules.  
For detailed information, refer to `app/ai/context/`.

---

## 1. Project Overview

AI Product Search is a FastAPI backend implementing:

- Semantic search using embeddings (pgvector)
- Hybrid search (semantic + keyword)
- Ranking via weighted scoring

Goal:
Return relevant products based on meaning, not just keywords.

---

## 2. Architecture

Layered structure (strict):

routers → services → repositories → models

Rules:

- Routers handle HTTP only
- Services contain business logic
- Repositories handle data access (CRUD)
- Complex queries (e.g. search) may live in services
- Never access DB directly from routers

---

## 3. Core Technologies

- FastAPI
- PostgreSQL + pgvector
- SQLAlchemy (ORM only, no raw SQL)
- Pydantic v2

All configuration comes from:
`app/core/config.py`

---

## 4. Embedding System

Location:
`app/ai/runtime/embeddings/`

Rules:

- Always use `get_embedding_service()` (factory)
- Do NOT call providers directly
- Query and product embeddings must use the same model
- Embedding dimension must match `EMBEDDING_DIM`

---

## 5. Search System (High-Level)

Pipeline:

1. Normalize query
2. Generate embedding
3. Execute DB query (vector + keyword)
4. Rank results
5. Return top matches

Ranking principles:

- Semantic similarity is primary
- Keyword matching is secondary (boost only)
- Exact matches (name) > description matches
- Avoid irrelevant results (e.g. accessories vs main product)

---

## 6. Database Rules

- Use SQLAlchemy ORM (no raw SQL)
- Use Alembic for migrations
- Vector column must match embedding dimension
- Always push filtering and ranking to the database

For schema details:
→ see `app/ai/context/decisions/`

---

## 7. Performance Constraints

- Max search limit = 50
- Do not load full tables into memory
- Use pgvector index for scaling
- Keep embedding calls outside DB transactions

---

## 8. AI Memory & Context

Persistent memory lives in:

`app/ai/context/`

Rules:

- After every feature, bug fix, or refactor:
  - update `progress/`
- Record key decisions in `decisions/`
- Store experiments in `experiments/`

Before starting work:
→ read `progress/` to understand current state

---

## 9. Working Principles

- Prefer simple, rule-based solutions over complex AI/LLM pipelines
- Do not over-engineer
- Keep logic inside the database when possible
- Follow existing patterns in the codebase

---

## 10. Additional Context (Progressive Disclosure)

For detailed information:

- Search evolution → `app/ai/context/progress/`
- Architecture decisions → `app/ai/context/decisions/`
- Experiments → `app/ai/context/experiments/`
- Prompt templates → `app/ai/context/prompts/`

Only load these when relevant.

---

## Summary

- This file defines the system at a high level
- Detailed knowledge lives in `app/ai/context/`
- Keep implementations consistent with architecture and search principles