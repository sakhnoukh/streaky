from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.db import create_tables
from app.logging import setup_logging_middleware
from app.monitoring import MonitoringMiddleware
from app.routers import auth, habits
from app.routers import monitoring

# Create FastAPI app
app = FastAPI(
    title="Streaky Habit Tracker API",
    description="Track your habits and build streaks",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
    except Exception as e:
        # Log error but don't crash - health endpoint will show DB status
        import logging
        logging.error(f"Database initialization failed: {e}")

# Configure CORS for frontend (Azure + local) - MUST be first middleware
# Log CORS origins for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"CORS allowed origins: {settings.cors_origins}")

# Custom middleware to ensure CORS headers on all responses (including errors)
class CORSHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if origin and origin in settings.cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "*"
        
        return response

# Add CORS header middleware first (before CORS middleware)
app.add_middleware(CORSHeaderMiddleware)

# CORS middleware must be added to handle preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Add explicit CORS handler for OPTIONS requests
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle OPTIONS requests explicitly to ensure CORS headers are always present"""
    origin = request.headers.get("origin")
    if origin and origin in settings.cors_origins:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "600",
            }
        )
    return Response(status_code=200)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Add logging middleware
setup_logging_middleware(app)

# Include routers
app.include_router(monitoring.router)  # Health checks and metrics
app.include_router(auth.router)
app.include_router(habits.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Streaky Habit Tracker API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "habits": {
                "create": "POST /habits",
                "list": "GET /habits",
                "update": "PUT /habits/{id}",
                "delete": "DELETE /habits/{id}",
                "log_entry": "POST /habits/{id}/entries",
                "stats": "GET /habits/{id}/stats"
            },
            "auth": {
                "login": "POST /token"
            },
            "monitoring": {
                "health": "GET /health",
                "version": "GET /version",
                "metrics": "GET /metrics (Prometheus)",
                "business_metrics": "GET /business-metrics (JSON)",
                "system": "GET /system"
            }
        }
    }
