@echo off
title JusticeAI Launcher
echo Starting JusticeAI System...

echo Starting Backend Server (FastAPI)...
start "JusticeAI Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && uvicorn main:app --reload"

echo Starting Frontend Server (Vite/React)...
start "JusticeAI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both services have been launched in separate windows!
echo Once the frontend server is ready, it usually runs on http://localhost:5173
echo.
pause
