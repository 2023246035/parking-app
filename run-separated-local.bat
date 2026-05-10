@echo off
echo ==============================================================
echo Starting ParkMyCar in 3 Strictly Separated Native Processes
echo (Bypassing Docker entirely!)
echo ==============================================================

:: Check for virtual environment
if not exist .venv (
    echo ERROR: Virtual environment not found. Please run run-ai-local.bat first to install it.
    pause
    exit /b 1
)

:: Start AI Microservice (Port 8001) in a new window
echo [1/3] Starting AI Microservice natively (Port 8001)...
start "AI Microservice (Port 8001)" cmd /k "call .venv\Scripts\activate.bat && set AI_API_PORT=8001 && uvicorn app.ai.main:app --host 127.0.0.1 --port 8001 --reload"

:: Start Core Backend (Port 8000) in a new window
echo [2/3] Starting Core Backend natively (Port 8000)...
start "Core Backend (Port 8000)" cmd /k "call .venv\Scripts\activate.bat && reflex run --backend-only"

:: Start Frontend UI (Port 3000) in a new window
echo [3/3] Starting Frontend UI natively (Port 3000)...
start "Frontend UI (Port 3000)" cmd /k "call .venv\Scripts\activate.bat && set API_URL=http://localhost:8000 && reflex run --frontend-only"

echo.
echo SUCCESS! 
echo Three completely separate terminal windows have been launched.
echo Your Frontend, Backend, and AI Microservice are now running in strict isolation just like Docker!
echo.
pause
