@echo off
REM Run ParkMyCar AI Microservice without Docker (Development mode)

echo.
echo ================================
echo   ParkMyCar AI - Local Run
echo   No Docker Required
echo ================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed: https://www.python.org/
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q uvicorn[standard] python-multipart slowapi python-jose[cryptography]

REM Start the AI API
echo.
echo Starting ParkMyCar AI Microservice...
echo.
echo AI Service will be available at:
echo   - AI API Docs:     http://localhost:8001/docs
echo   - Health Check:    http://localhost:8001/health
echo.
echo Press Ctrl+C to stop the server
echo.

set AI_API_PORT=8001
uvicorn app.ai.main:app --host 0.0.0.0 --port 8001 --reload
