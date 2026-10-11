# Starts the backend (FastAPI), the website (Vite, :5173) and the voice assistant (Vite, :5174)
# each in its own PowerShell window. Both frontends use the SAME backend at http://127.0.0.1:8000.
# Run from the repository root:  .\scripts\dev.ps1
# Prerequisites: see START.md (PostgreSQL running, backend\.venv created, `npm install` in website and voice-assistant).
$root = Split-Path -Parent $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; .\.venv\Scripts\python -m uvicorn app.main:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\website'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\voice-assistant'; npm run dev"

Write-Host "Backend : http://127.0.0.1:8000/health"
Write-Host "Website : http://localhost:5173"
Write-Host "Voice   : http://localhost:5174"