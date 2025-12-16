# Dockerfile for Full ParkMyCar Application (Reflex Frontend + Backend)
# This includes the complete UI and API

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NODE_VERSION=20

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    curl \
    bash \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize Reflex (this builds the frontend)
RUN reflex init

# Expose ports
EXPOSE 3000 8000

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Run the full Reflex application
# Uses PORT env variable for backend (Render requirement)
CMD ["bash", "-c", "reflex run --env prod --backend-port ${PORT:-8000} --frontend-port 3000"]
