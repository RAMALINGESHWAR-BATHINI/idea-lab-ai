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
| Data models + Alembic migrations (23+ tables, pgvector) | ✅ implemented |
| Core: config, structured logging, JWT/bcrypt, audit trail, error envelopes | ✅ implemented |
| Security: RBAC, SSRF guard, prompt-injection fencing | ✅ implemented (per-user) |
| AI provider abstraction (Gemini + local Ollama, embeddings) | ✅ implemented |
| FastAPI app entry (`app/main.py`), rate limiting, CORS | ✅ implemented |
| Auth API: register / login / refresh / me + `get_current_user` | ✅ implemented |
| Content API (events, projects, people, facilities, achievements, media) | ✅ implemented |
| AI Chat API + web search + document processing | ✅ implemented |
| Admin API (users, permissions, audit log, role management) | ✅ implemented |
| Device API (ESP32 robot: register / status / ping / chat / config) | ✅ implemented |
| Health API (`/health`, `/health/ready`) | ✅ implemented |
| Tests (56 passing: health, auth, content, admin, security, password reset) | ✅ all passing |
| Website frontend (`frontend/`: React + Vite + TypeScript + Tailwind, public site + dashboards) | implemented; build config repaired, build not re-verified |
| Voice assistant frontend (`voice/`: separate React + Vite app, same backend) | implemented (browser speech in/out); not yet run end to end |
| Device API routes for ESP32 robot | ✅ implemented |

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
│   │   ├── routes/          # health.py, auth.py, content.py, chat.py, admin.py, devices.py
│   │   ├── security/        # rbac, ssrf, prompt-injection defence
│   │   ├── services/        # ai_orchestrator, document processor, web search, storage, memory
│   │   └── ai/              # provider protocols, Gemini/Ollama, embeddings, registry
│   ├── alembic/             # async migrations
│   ├── tests/               # pytest suite (56 tests)
│   ├── .env.example
│   └── requirements.txt
├── voice/                   # SEPARATE voice assistant app (port 5174), same backend API
├── frontend/                # public website + dashboards (port 5173)
│   ├── src/
│   │   ├── api/             # API client with auth token support
│   │   ├── components/      # Navbar, Footer, Layout, RequireAuth
│   │   ├── contexts/        # AuthContext for state management
│   │   ├── pages/           # Public pages + dashboard pages
│   │   ├── App.tsx          # React Router v6 routing
│   │   └── index.css        # Tailwind CSS entry point
│   ├── vite.config.ts       # Vite + React + path alias config
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── package.json
│   └── dist/               # Production build output
├── scripts/
│   └── install_pgvector.ps1 # Windows pgvector installer for PostgreSQL 16
├── README.md
├── ARCHITECTURE.md
├── SECURITY.md
└── SETUP.md
```

## Quick start

See **[SETUP.md](SETUP.md)** for full instructions. Short version:

### Backend (Python + FastAPI)

```powershell
cd backend
copy .env.example .env        # edit secrets!
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` (debug mode only).

Run tests:

```powershell
cd backend
python -m pytest
```

### Frontend (React + Vite + TypeScript + Tailwind)

```powershell
cd frontend
npm install
npm run dev
```

Then open `http://127.0.0.1:5173`.

### Running both at once

```powershell
cd frontend
npm run dev:full
```

This starts both the backend API (`--reload`) and the frontend dev server concurrently.

Build for production:

```powershell
cd frontend
npm run build
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
