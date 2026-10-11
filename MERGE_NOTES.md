# Merge notes (2026-10-10)

Two folders existed: `idea-lab-ai` (full git repo) and `IdeaLab-AI` (9-file early scaffold).

- Base: `idea-lab-ai` (git history, 40 model classes, Alembic migrations, routes, services, tests, frontend).
- From `IdeaLab-AI` only `docker-compose.yml` was kept, reworked: env-driven credentials matching `.env.example`,
  ports bound to 127.0.0.1, Ollama behind a profile, GPU reservation moved to `docker-compose.gpu.yml`.
- Not carried over (superseded or conflicting): `init.sql` (hand-written schema that would clash with Alembic),
  `core/database.py` (repo has `db/session.py`), `tools/base.py` (repo has `services/tools.py`),
  older `requirements.txt` pins, models/schemas/config/security stubs.
- Left out of the zip: `backend/.env`, `node_modules`, `frontend/dist`, `__pycache__`, `.pytest_cache`.
- Nothing was committed. Working-tree changes and untracked files from the original repo are preserved as-is.

## Second pass: website + voice assistant (same backend)

- New `voice/` app (separate Vite/React app, port 5174) using the shared `/api` backend: push-to-talk microphone,
  consent notice, typed fallback, spoken replies, optional sign-in (token kept in memory only).
- Backend: `ChatRequest.channel` (`text` | `voice`) is now passed through to the orchestrator; voice adds a
  "speakable plain text" instruction. Test file: `backend/tests/test_voice_channel.py` (not run here).
- Website repairs: `frontend/src/api/client.ts` imported a non-existent `./types`; `frontend/tsconfig.json` had options
  that fail under TypeScript 6 (typo `useDefineForClassStyle`, `DOMIterable`, deprecated `node10`/`baseUrl`) and was
  replaced with a single working config (unused `tsconfig.app.json` / `tsconfig.node.json` removed);
  Tailwind v4 had no Vite/PostCSS plugin, so `@tailwindcss/vite` was added and wired (`@config` keeps your theme).
- `.env.example` CORS origins updated to ports 5173/5174. `scripts/dev.ps1` starts all three processes.
- Not verified here (no network to install packages): `npm install`, `npm run build`, pytest, migrations.
