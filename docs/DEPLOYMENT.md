# Deployment Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16 with pgvector
- Docker & Docker Compose (optional)

## Option 1: Local Development

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your secrets
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Voice Assistant
```powershell
cd voice
npm install
npm run dev
# Open http://localhost:5174
```

## Option 2: Docker Compose

```powershell
docker compose up -d postgres
# Optional: docker compose --profile ollama up -d
cd backend
alembic upgrade head
```

Then run backend and frontends as in Option 1.

## Option 3: Production

### Backend
```powershell
# Set ENVIRONMENT=production in .env
# Set DEBUG=false
# Generate a strong SECRET_KEY
# Set ALLOW_REGISTRATION=false if needed
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run build
# Serve dist/ via nginx or similar
```

### Voice Assistant
```powershell
cd voice
npm install
npm run build
# Serve via nginx or similar
```

## Environment Variables

### Backend (`.env`)
| Variable | Required | Default |
|---|---|---|
| `SECRET_KEY` | Yes | change-me-in-production |
| `DATABASE_URL` | Yes | postgresql+asyncpg://... |
| `ENVIRONMENT` | No | development |
| `DEBUG` | No | true |
| `ALLOW_REGISTRATION` | No | true |
| `CORS_ORIGINS` | Yes | localhost:5173,... |
| `GEMINI_API_KEY` | No | (empty) |
| `OLLAMA_BASE_URL` | No | http://127.0.0.1:11434 |
| `EMBEDDING_PROVIDER` | No | ollama |

### Frontend (`vite.config.ts`)
- `VITE_API_URL` — Backend API URL (defaults to `/api`)

## Database Setup

```powershell
# Create database
$env:PGPASSWORD = "postgres"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE idealab;"

# Apply migrations
cd backend
python -m alembic upgrade head

# Load demo data
python -c "import asyncio; from app.db.demo_data import _main; asyncio.run(_main())"
```

## SSL/TLS

For production, terminate SSL at the reverse proxy (nginx, Caddy, Cloudflare). Set `ENVIRONMENT=production` to enable HSTS headers.

## Monitoring

Health endpoints:
- `GET /health` — Basic health check
- `GET /health/ready` — Readiness check (includes database)

Logs are structured JSON when `LOG_JSON=true`.