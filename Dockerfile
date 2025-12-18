# Dockerfile for ParkMyCar (Render Free Tier Optimized)

# Stage 1: Build Stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
ENV PYTHONUNBUFFERED=1 \
    NODE_VERSION=20

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build the Reflex frontend
# This generates the .web directory
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Stage 2: Runtime Stage
FROM python:3.11-slim as runner

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    nodejs \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code and built frontend artifacts
COPY --from=builder /app /app

ENV PYTHONPATH=/app
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://0.0.0.0:$PORT || exit 1

# Run the app 
# Note: We use 'reflex run' but the frontend is already built, so it should skip the heavy build step
CMD ["bash", "-c", "reflex run --env prod --backend-host 0.0.0.0 --backend-port 8000 --frontend-port $PORT"]
