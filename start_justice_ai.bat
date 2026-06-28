@echo off
title JusticeAI Launcher
echo ==============================================
echo       Starting JusticeAI Container Stack      
echo ==============================================
echo.
echo Bringing up the microservices (Postgres, Neo4j, Redis, API, UI)...
docker compose up -d

echo.
echo Waiting for services to initialize...
timeout /t 5 /nobreak > NUL

echo.
echo JusticeAI is now running!
echo The Frontend Dashboard is available at: http://localhost:5173
echo The Backend API is available at: http://localhost:8000
echo.
echo To view live logs, run: docker compose logs -f
echo To stop the system, run: docker compose down
echo.
pause
