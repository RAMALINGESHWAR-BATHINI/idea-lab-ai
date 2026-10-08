# IdeaLab AI

A voice-first AI assistant for the college **IdeaLab** — helping students ask
questions, research ideas, learn skills, and develop projects through the
IdeaLab process:

> **Problem/Idea → Understand → Define → Ideate → Discuss → Prototype → Test →
> Get Feedback → Improve → Build**

The assistant supports students' thinking; it does not replace it. It asks
*what problem are you solving, who for, what already exists* before jumping to
"here's how to build it".

## Current status

| Layer | Status |
|---|---|
| Data models + initial Alembic migration (23 tables, pgvector) | ✅ implemented |
| Core: config, structured logging, JWT/bcrypt, audit trail, error envelopes | ✅ implemented |
| Security: RBAC access levels, SSRF guard, prompt-injection fencing | ✅ implemented |
| AI provider abstraction (Gemini + local Ollama, embeddings) | ✅ implemented |
| FastAPI app entry (`app/main.py`), rate limiting, CORS | ✅ implemented |
| Auth API: register / login / refresh / me + `get_current_user` | ✅ implemented |
| Health API: `/health`, `/health/ready` | ✅ implemented |
| Tests (30 passing: health, auth flow, security units) | ✅ implemented |
| Chat / voice / college knowledge / web intelligence / memory / admin APIs | ⏳ planned |
| Frontend | ⏳ planned |

## Repository layout

```text
idea-lab-ai/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point + app factory
│   │   ├── core/            # config, logging, security, audit, errors, rate_limit, deps
│   │   ├── db/              # async engine/session, Base, bootstrap (default roles)
│   │   ├── models/          # SQLAlchemy 2.x ORM models + enums
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routes/          # health.py, auth.py
│   │   ├── security/        # rbac, ssrf, prompt-injection defence
│   │   └── ai/              # provider protocols, Gemini/Ollama, embeddings, registry
│   ├── alembic/             # async migrations (initial schema: 54444a3c7a8c)
│   ├── tests/               # pytest suite (health, auth, security)
│   ├── .env.example
│   └── requirements.txt
├── scripts/
│   └── install_pgvector.ps1 # Windows pgvector installer for PostgreSQL 16
├── README.md
├── ARCHITECTURE.md
├── SECURITY.md
└── SETUP.md
```

## Quick start

See **[SETUP.md](SETUP.md)** for full instructions. Short version:

```powershell
cd backend
copy .env.example .env        # edit secrets!
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` (debug mode only).

Run tests:

```powershell
cd backend
python -m pytest
```

## More documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — layers, request flow, data model,
  AI provider abstraction
- **[SECURITY.md](SECURITY.md)** — threat model, authentication, RBAC, SSRF,
  prompt injection, rate limiting, audit
- **[SETUP.md](SETUP.md)** — environment setup, database, migrations, running
  and testing

## IdeaLab community philosophy

IdeaLab is not a rigid group with fixed roles. Anyone interested can
participate: attend a workshop, learn a skill, join a project, bring an
idea, mentor others later, or organise programs. The central idea is
**continuous learning through building, experimentation, collaboration,
mentoring, and sharing knowledge**.
