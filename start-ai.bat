@echo off
REM Quick start script for Windows - AI Microservice Only

echo.
echo ================================
echo   ParkMyCar AI - Quick Start
echo   AI Microservice Only
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

REM Start Docker Compose for AI only
echo Starting ParkMyCar AI Microservice...
echo.

docker compose -f docker-compose.ai.yml up -d --build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ ParkMyCar AI Microservice started successfully!
    echo.
    echo AI API:          http://localhost:8001
    echo AI API Docs:     http://localhost:8001/docs
    echo Health Check:    http://localhost:8001/health
    echo.
    echo View logs: docker compose -f docker-compose.ai.yml logs -f
    echo Stop:      docker compose -f docker-compose.ai.yml down
    echo.
) else (
    echo.
    echo × Failed to start ParkMyCar AI Microservice
    echo Please check Docker Desktop is running
    echo.
)

pause

