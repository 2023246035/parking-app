@echo off
REM Run ParkMyCar API without Docker (Development mode)

echo.
echo ================================
echo   ParkMyCar API - Local Run
echo   No Docker Required
echo ================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from example...
    copy .env.example .env 2>nul
    if errorlevel 1 (
        echo WARNING: Could not find .env.example
        echo You may need to configure database settings manually
    )
)

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
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q uvicorn[standard] python-multipart slowapi python-jose[cryptography]

REM Initialize database
echo.
echo Initializing database...
python -c "from app.db.init_db import init_db; init_db()"

REM Start the API
echo.
echo Starting ParkMyCar API...
echo.
echo API will be available at:
echo   - API Docs: http://localhost:8000/api/docs
echo   - Health:   http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
