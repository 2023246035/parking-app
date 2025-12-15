"""
FastAPI Main Application for ParkMyCar API
Standalone API server that can run independently from Reflex
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    # Startup
    logger.info("🚀 Starting ParkMyCar API...")
    
    try:
        # Initialize database
        from app.db.init_db import init_db
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    try:
        # Start background scheduler
        from app.services.notification_service import start_scheduler
        start_scheduler()
        logger.info("✅ Background scheduler started")
    except Exception as e:
        logger.warning(f"⚠️  Background scheduler failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down ParkMyCar API...")


# Create FastAPI app
app = FastAPI(
    title="ParkMyCar API",
    description="RESTful API for ParkMyCar parking management system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware - configure for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",  # Vite default
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


# Include API routes
from app.api.routes import router as api_router
app.include_router(api_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "ParkMyCar API",
        "version": "1.0.0"
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to ParkMyCar API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Custom exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("APP_ENV") == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    reload = os.getenv("APP_ENV", "production") == "development"
    
    logger.info(f"Starting API server on {host}:{port}")
    
    uvicorn.run(
        "app.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
