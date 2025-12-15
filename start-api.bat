@echo off
REM Quick start script for Windows - API Only

echo.
echo ================================
echo   ParkMyCar API - Quick Start
echo   Backend API Only
echo ================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from API template...
    copy .env.api .env
    echo.
    echo IMPORTANT: Please edit .env file and update the configuration!
    echo Press any key after updating .env file...
    pause >nul
)

REM Start Docker Compose for API only
echo Starting ParkMyCar API...
echo.

docker-compose -f docker-compose.api.yml up -d

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ ParkMyCar API started successfully!
    echo.
    echo API:          http://localhost:8000
    echo API Docs:     http://localhost:8000/api/docs
    echo Health Check: http://localhost:8000/health
    echo Database:     localhost:5432
    echo.
    echo View logs: docker-compose -f docker-compose.api.yml logs -f
    echo Stop:      docker-compose -f docker-compose.api.yml down
    echo.
) else (
    echo.
    echo × Failed to start ParkMyCar API
    echo Please check Docker Desktop is running
    echo.
)

pause
