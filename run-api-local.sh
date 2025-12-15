#!/bin/bash
# Run ParkMyCar API without Docker (Development mode)

echo ""
echo "================================"
echo "  ParkMyCar API - Local Run"
echo "  No Docker Required"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env 2>/dev/null || echo "WARNING: Could not find .env.example"
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Make sure Python 3 is installed"
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q uvicorn[standard] python-multipart slowapi python-jose[cryptography]

# Initialize database
echo ""
echo "Initializing database..."
python -c "from app.db.init_db import init_db; init_db()"

# Start the API
echo ""
echo "Starting ParkMyCar API..."
echo ""
echo "API will be available at:"
echo "  - API Docs: http://localhost:8000/api/docs"
echo "  - Health:   http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
