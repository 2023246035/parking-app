#!/bin/bash
# Quick start script for API Only - Linux/Mac

echo ""
echo "================================"
echo "  ParkMyCar API - Quick Start"
echo "  Backend API Only"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from API template..."
    cp .env.api .env
    echo ""
    echo "IMPORTANT: Please edit .env file and update the configuration!"
    echo "Press Enter after updating .env file..."
    read
fi

# Start Docker Compose for API only
echo "Starting ParkMyCar API..."
echo ""

docker-compose -f docker-compose.api.yml up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ ParkMyCar API started successfully!"
    echo ""
    echo "API:          http://localhost:8000"
    echo "API Docs:     http://localhost:8000/api/docs"
    echo "Health Check: http://localhost:8000/health"
    echo "Database:     localhost:5432"
    echo ""
    echo "View logs: docker-compose -f docker-compose.api.yml logs -f"
    echo "Stop:      docker-compose -f docker-compose.api.yml down"
    echo ""
else
    echo ""
    echo "× Failed to start ParkMyCar API"
    echo "Please check Docker is running"
    echo ""
fi
