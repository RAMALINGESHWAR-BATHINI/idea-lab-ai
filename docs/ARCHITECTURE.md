# Architecture

## High-Level Overview

IdeaLab AI follows a **three-tier architecture**:

1. **Backend API** (FastAPI) — handles all business logic, authentication, database access, and AI orchestration
2. **Website Frontend** (React + Vite) — public-facing site with dashboards for content management
3. **Voice Assistant** (React + Vite) — separate SPA that uses browser speech APIs for voice input/output

All three apps communicate through a single REST API (`/api/*`).

## Request Flow

```
Browser/Voice App
    │
    │  HTTP (JSON)
    ▼
FastAPI Backend (port 8000)
    │
    ├── Auth (JWT/bcrypt)
    ├── Rate Limiting (slowapi)
    ├── RBAC Permission Check
    ├── Business Logic (services/)
    ├── AI Orchestration (ai/)
    │   ├── Gemini (cloud LLM)
    │   └── Ollama (local LLM fallback)
    ├── Database (PostgreSQL + pgvector)
    └── Audit Trail (append-only log)
```

## Backend Layers

```
backend/app/
├── main.py              # FastAPI app factory + lifespan
├── core/                # config, logging, security, rate_limit, deps, errors, audit
├── db/                  # async engine/session, Base, bootstrap (default roles/permissions)
├── models/              # SQLAlchemy 2.x ORM models + enums
├── schemas/             # Pydantic request/response schemas
├── routes/              # health, auth, content, chat, admin, devices
├── security/            # rbac, ssrf, prompt-injection defence
├── services/            # ai_orchestrator, document_processor, web_search, storage, memory
└── ai/                  # provider protocols, Gemini/Ollama, embeddings, registry
```

## Data Flow

### Chat Request
1. User sends message → `/api/ai/chat`
2. Rate limit check (per-user)
3. Auth check (optional token)
4. Prompt-injection fence (sanitizes input)
5. AI orchestrator selects provider:
   - If `GEMINI_API_KEY` set → Gemini (cloud)
   - Else → Ollama (local)
6. Optional web search tool (SSRF-guarded)
7. Response returned with sources + tool call metadata
8. Audit log entry written

### Content Request
1. GET `/api/content/events` (public, no auth)
2. Authenticated GET returns all rows; unauthenticated returns only `is_published` + `access_level=PUBLIC`
3. RBAC enforced on write operations (create/update/delete)

## AI Provider Abstraction

```
app/ai/
├── base.py         # Provider protocol (chat, embed, health)
├── registry.py     # Provider selection logic
├── gemini_provider.py  # Google Gemini implementation
├── ollama_provider.py  # Local Ollama implementation
└── embeddings.py   # Vector embedding generation
```

Providers are swappable — set `EMBEDDING_PROVIDER=ollama` to keep private data on-prem.

## Database Schema (23+ tables)

| Table | Purpose |
|---|---|
| `users` | Application users (auth) |
| `roles` | RBAC roles (14 default) |
| `permissions` | Granular permissions (40 default) |
| `audit_logs` | Append-only security/event log |
| `events` | Workshops, hackathons, seminars |
| `projects` | Student/faculty project showcase |
| `faculty` | Faculty mentors |
| `staff` | Non-teaching staff |
| `idealab_members` | IdeaLab community members |
| `students` | Student records |
| `equipment` | Lab equipment inventory |
| `equipment_bookings` | Equipment reservation system |
| `documents` | Institutional documents (with pgvector embeddings) |
| `document_chunks` | Vector-embedded document slices |
| `departments` | Academic departments |
| `research` | Research outputs (papers, patents) |
| `invitations` | Invitation codes for registration |
| `access_grants` | Temporary access grants |
| `device_tokens` | ESP32 robot authentication |
| `system_settings` | Key-value configuration |
| `chat_conversations` | Conversation history |
| `chat_messages` | Individual messages |
| `memory_items` | Long-term user memory |