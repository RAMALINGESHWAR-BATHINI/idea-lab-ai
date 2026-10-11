@echo off
REM Starts backend + website + voice assistant in separate windows.
REM Run from project root:  scripts\dev.bat
set ROOT=%~dp0..

REM Start backend
start "Backend" powershell -NoExit -Command "cd '%ROOT%\backend'; .\.venv\Scripts\python -m uvicorn app.main:app --reload"

REM Start website
start "Website" powershell -NoExit -Command "cd '%ROOT%\website'; npm run dev"

REM Start voice assistant
start "Voice" powershell -NoExit -Command "cd '%ROOT%\voice-assistant'; npm run dev"

echo Backend : http://127.0.0.1:8000/health
echo Website : http://localhost:5173
echo Voice   : http://localhost:5174