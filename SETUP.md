# Setup

Instructions verified on **Windows** with Python 3.13 and PostgreSQL 16.
Adapt paths/commands for Linux/macOS.

## 1. Prerequisites

- Python 3.11+ (3.13 tested)
- PostgreSQL 16 with the **pgvector** extension
- Git (optional, for version control)

### pgvector on Windows

Windows PostgreSQL builds don't ship pgvector. An admin PowerShell can run:

```powershell
.\scripts\install_pgvector.ps1
```

It drops a prebuilt `vector.dll` + extension files into your PostgreSQL tree
(default `C:\Program Files\PostgreSQL\16`). Restart the PostgreSQL service
afterwards.

## 2. Python environment

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configuration

```powershell
cd backend
copy .env.example .env          # Linux/macOS: cp .env.example .env
```

Edit `.env` — at minimum:

| Variable | Notes |
|---|---|
| `SECRET_KEY` | **Must** change: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `DATABASE_URL` | default `postgresql+asyncpg://postgres:postgres@localhost:5432/idealab` |
| `GEMINI_API_KEY` | optional; without it the local Ollama provider is used |
| `OLLAMA_BASE_URL` | default `http://127.0.0.1:11434` |
| `CORS_ORIGINS` | comma-separated frontend origins |
| `ALLOW_REGISTRATION` | `false` to disable self-signup |

All options are documented inline in `.env.example` and typed in
`app/core/config.py`.

## 4. Database

```powershell
# create the database (once)
psql -U postgres -c 'CREATE DATABASE idealab;'

# apply migrations (creates 23 tables, pgvector extension, HNSW indexes)
cd backend
alembic upgrade head
```

Verify:

```powershell
psql -U postgres -d idealab -c '\dt'          # tables listed
psql -U postgres -d idealab -c 'SELECT version_num FROM alembic_version;'
# → 54444a3c7a8c
```

> Do **not** run `alembic revision --autogenerate` against a database that is
> already at head unless you intend to create a new migration.

## 5. Run the API

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Smoke checks:

- `GET http://127.0.0.1:8000/health` → `{"status":"ok",...}`
- `GET http://127.0.0.1:8000/health/ready` → `{"status":"ready",...}`
- `GET http://127.0.0.1:8000/docs` → interactive OpenAPI (debug mode only)
- Register/login under `/api/auth/*`

## 6. Tests

```powershell
cd backend
python -m pytest
```

The suite starts the app with `TestClient` (lifespan included) and exercises
the live database using throwaway `test.*@example.com` accounts that are
deleted automatically after each test. Configuration comes from
`pytest.ini` + `tests/conftest.py` (which sets a high-limit test
environment before the app imports — do not import `app.*` before
`conftest` has run).

## 7. Optional: local AI (Ollama)

```powershell
ollama pull llama3.2             # chat fallback
ollama pull nomic-embed-text     # default embedding model (768-dim)
```

Keep `EMBEDDING_PROVIDER=ollama` so private data never leaves the machine.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `extension "vector" is not available` | run `scripts\install_pgvector.ps1`, restart PostgreSQL |
| `password authentication failed` | check `DATABASE_URL` credentials in `backend/.env` |
| `relation "users" does not exist` | run `alembic upgrade head` from `backend/` |
| 429 on auth endpoints | expected rate limit; raise `RATE_LIMIT_AUTH` in `.env` for local load tests |
| `/docs` returns 404 | docs are hidden unless `DEBUG=true` |
| Ollama errors | ensure `ollama serve` is running; check `OLLAMA_BASE_URL` |
