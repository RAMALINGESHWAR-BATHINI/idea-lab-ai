# Quick Start Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16 with pgvector extension
- Git (optional)

## 1. Clone the repository
```bash
git clone <repo-url>
cd IdeaLab-AI
```

## 2. Install pgvector (Windows only)
```powershell
cd scripts
.\install_pgvector.ps1
```
Restart PostgreSQL service afterwards.

## 3. Start PostgreSQL
```powershell
# Verify service is running
Get-Service -Name postgresql*
```

Create the database:
```powershell
$env:PGPASSWORD = "postgres"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE idealab;"
```

## 4. Backend setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` — at minimum set:
- `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_urlsafe(48))"`)
- `DATABASE_URL` (default is correct for local)
- `ALLOW_REGISTRATION=true`

Apply migrations:
```powershell
python -m alembic upgrade head
```

## 5. Load demo data
```powershell
python -c "import asyncio; from app.db.demo_data import _main; asyncio.run(_main())"
```

## 6. Start backend
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000/docs for API docs (debug mode only).

## 7. Start website
```powershell
cd website
npm install
npm run dev
```
Open http://localhost:5173

## 8. Start voice assistant (optional)
```powershell
cd voice-assistant
npm install
npm run dev
```
Open http://localhost:5174

## 9. Run tests
```powershell
cd backend
python -m pytest
```

## All-in-one dev script
```powershell
# From project root
.\scripts\dev.ps1
```
This opens backend + website + voice in three windows.

## Troubleshooting
| Issue | Fix |
|---|---|
| `extension "vector" is not available` | Run `.\scripts\install_pgvector.ps1`, restart PostgreSQL |
| `password authentication failed` | Check `DATABASE_URL` in `backend/.env` |
| `relation "users" does not exist` | Run `alembic upgrade head` from `backend/` |
| `/docs` returns 404 | Docs are hidden unless `DEBUG=true` |
| Pages show blank | Run demo data loader (step 5) |
| Script not signed | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` then try again |