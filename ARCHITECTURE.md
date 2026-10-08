# Architecture

IdeaLab AI is a **Python / FastAPI / PostgreSQL 16 + pgvector** backend with a
provider-agnostic AI layer. This document describes what exists in the code
today.

## High-level request flow

Every request passes through the security pipeline before and after any AI
invocation — the model never bypasses backend controls:

```text
Client request
  │
  ▼
CORS middleware            (origin allow-list from settings)
  │
  ▼
Rate limiting              (slowapi, per-IP; stricter budget on /auth)
  │
  ▼
Routing                    (app/routes/*)
  │
  ▼
Authentication             (core/deps.get_current_user → JWT → users row)
  │
  ▼
Authorization              (security/rbac.py access-level checks)
  │
  ▼
Handler (schemas validate the payload)
  │
  ▼
Audit log                  (core/audit.record_audit, best-effort)
  │
  ▼
JSON response              (errors.py envelopes for every error class)
```

For future AI/tool calls the intended order is:

```text
AI orchestration → tool permission check → tool execution → validated result → AI response
```

The AI output is treated as untrusted *data*, never as commands.

## Layers

| Package | Responsibility |
|---|---|
| `app/main.py` | FastAPI app factory: lifespan, CORS, rate limiting, exception handlers, router mounting |
| `app/core/` | Cross-cutting: `config` (pydantic-settings), `logging` (structlog), `security` (bcrypt + JWT), `audit`, `errors` (JSON envelopes), `rate_limit` (slowapi), `deps` (`get_current_user`) |
| `app/db/` | Async engine/session (`db/session.py`), declarative `Base` + mixins (`db/base.py`), default-role bootstrap (`db/bootstrap.py`) |
| `app/models/` | SQLAlchemy 2.x ORM models (mapped types) + shared enums |
| `app/schemas/` | Pydantic v2 request/response contracts |
| `app/routes/` | HTTP endpoints (`health.py`, `auth.py`) |
| `app/security/` | Pure security logic: `rbac`, `ssrf`, `injection` — no FastAPI dependency |
| `app/ai/` | Provider abstraction: `base` protocols, `gemini_provider`, `ollama_provider`, `embeddings`, `registry` |
| `alembic/` | Async migrations; initial schema revision `54444a3c7a8c` |

Dependency rule: `routes → schemas/deps → core/db/models`; `security` and `ai`
sit beside `core` and depend only on `core` + `models`. Nothing imports
`routes`.

## API surface (implemented)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/` | none | service name/version |
| GET | `/health` | none | liveness, no dependencies |
| GET | `/health/ready` | none | readiness, checks database (`503` if down) |
| POST | `/api/auth/register` | none | creates account, assigns `student` role, returns token pair |
| POST | `/api/auth/login` | none | uniform failure message, audited |
| POST | `/api/auth/refresh` | none | refresh token → new pair |
| GET | `/api/auth/me` | Bearer | current profile |

Interactive docs: `/docs`, `/redoc`, `/openapi.json` (debug mode only).

## Data model

23 tables created by the initial migration. Highlights:

- **Auth/RBAC**: `users`, `roles`, `permissions`, `role_permissions`
  (`users.role_id` → `roles.id`)
- **People/org**: `faculty`, `staff`, `students`, `idealab_members`,
  `departments`, `organizations` — each carries an `access_level`
- **Content**: `projects`, `events`, `workshops`, `notices`
- **Knowledge**: `documents`, `document_chunks` (pgvector `embedding`
  column + HNSW cosine index), `research`, `web_sources`
- **Memory**: `user_memories` (pgvector embedding + HNSW index, scoped
  `user` / `session` / `institution`)
- **Chat**: `conversations`, `messages` (with tool-call trace columns and
  `sources` JSONB)
- **Audit**: `audit_logs` (append-only)

All tables use UUID primary keys and DB-side `created_at`/`updated_at`
timestamps (`db/base.py` mixins). Constraint names follow a deterministic
naming convention so Alembic autogenerate stays stable.

`AccessLevel` (`public → internal → restricted → confidential`) is the single
classification driving both human RBAC and what may leave the institution to
cloud AI providers (see SECURITY.md).

## AI provider abstraction

`app/ai/base.py` defines two independent seams:

- `ChatProvider` — `generate()` (tools) and `generate_grounded()` (live web
  search), returning `ModelReply` (text, tool calls, sources)
- `EmbeddingProvider` — `embed()` / `embed_query()`

`registry.py` selects the provider at runtime:

- **Chat**: Gemini when `GEMINI_API_KEY` is set (tools + grounding), else
  local Ollama when enabled (direct answers; grounding fails explicitly
  rather than silently degrading)
- **Embeddings**: `EMBEDDING_PROVIDER=ollama` (default — private data stays
  on-premises) or `gemini`

Model IDs come only from settings (`.env`); nothing is hardcoded. Shutdown
disposes providers and the DB engine via the FastAPI lifespan.

## Configuration & background

- Settings are a cached pydantic-settings singleton
  (`core/config.py`, `backend/.env`, documented in `.env.example`)
- Logging is structured (structlog); `LOG_JSON=true` for machine-readable
  output
- Migrations are async (`alembic/env.py`); the URL is injected from settings
- The initial migration also enables `CREATE EXTENSION vector` and creates
  HNSW indexes for semantic retrieval

## Planned (not yet implemented)

Chat/voice orchestration, college knowledge search, web intelligence,
memory, documents, and admin APIs — following the layering above:
`routes → schemas → services → (security | ai) → db`.
