from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.db import create_tables
from app.logging import setup_logging_middleware
from app.monitoring import MonitoringMiddleware
from app.routers import auth, categories, habits
from app.routers import monitoring

# Create FastAPI app
app = FastAPI(
    title="Streaky Habit Tracker API",
    description="Track your habits and build streaks",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure logging once
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        # Run database migrations on startup (ensures schema is up to date)
        try:
            import subprocess
            import os
            # Only run migrations in production (Azure)
            if settings.ENVIRONMENT == "production":
                logger.info("Running database migrations on startup...")
                result = subprocess.run(
                    ["python", "-m", "alembic", "upgrade", "head"],
                    cwd=os.path.dirname(os.path.dirname(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    logger.info("Database migrations completed successfully")
                else:
                    logger.warning(f"Migration output: {result.stdout}\nErrors: {result.stderr}")
        except Exception as migration_error:
            logger.warning(f"Migration on startup failed (non-critical): {migration_error}")
            # Don't crash the app if migrations fail - they can be run manually
    except Exception as e:
        # Log error but don't crash - health endpoint will show DB status
        logger.error(f"Database initialization failed: {e}")

# Configure CORS for frontend (Azure + local) - MUST be first middleware
# Log CORS origins for debugging
logger.info(f"CORS allowed origins: {settings.cors_origins}")
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"Database URL: {settings.database_url_computed[:50]}...")  # Log first 50 chars only

# Custom middleware to ensure CORS headers on all responses (including errors)
class CORSHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # #region agent log
        import json
        import time
        try:
            with open("/Users/ryanmuenker/Desktop/School/DEVOPS/streaky group project/streaky/.cursor/debug.log", "a") as f:
                f.write(json.dumps({"id": f"log_{int(time.time() * 1000)}_cors_entry", "timestamp": int(time.time() * 1000), "location": "main.py:46", "message": "CORS middleware entry", "data": {"path": request.url.path, "method": request.method}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        except: pass
        # #endregion
        origin = request.headers.get("origin")
        logger.info(f"Request from origin: {origin}, Path: {request.url.path}, Method: {request.method}")
        
        response = None
        try:
            response = await call_next(request)
            # #region agent log
            try:
                with open("/Users/ryanmuenker/Desktop/School/DEVOPS/streaky group project/streaky/.cursor/debug.log", "a") as f:
                    f.write(json.dumps({"id": f"log_{int(time.time() * 1000)}_cors_success", "timestamp": int(time.time() * 1000), "location": "main.py:55", "message": "CORS middleware - request processed", "data": {"status_code": response.status_code if response else None}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
            except: pass
            # #endregion
        except Exception as e:
            logger.error(f"Error in request: {str(e)}", exc_info=True)
            # #region agent log
            try:
                with open("/Users/ryanmuenker/Desktop/School/DEVOPS/streaky group project/streaky/.cursor/debug.log", "a") as f:
                    f.write(json.dumps({"id": f"log_{int(time.time() * 1000)}_cors_exception", "timestamp": int(time.time() * 1000), "location": "main.py:62", "message": "CORS middleware - exception caught", "data": {"error": str(e)}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
            except: pass
            # #endregion
            # Create error response with CORS headers
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(e)}"}
            )
        
        # Add CORS headers if origin is allowed
        if response is not None:
            if origin and origin in settings.cors_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Expose-Headers"] = "*"
                logger.info(f"Added CORS headers for origin: {origin}")
                # #region agent log
                try:
                    with open("/Users/ryanmuenker/Desktop/School/DEVOPS/streaky group project/streaky/.cursor/debug.log", "a") as f:
                        f.write(json.dumps({"id": f"log_{int(time.time() * 1000)}_cors_headers_added", "timestamp": int(time.time() * 1000), "location": "main.py:72", "message": "CORS headers added to response", "data": {"origin": origin}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
                except: pass
                # #endregion
            else:
                logger.warning(f"Origin not allowed: {origin}, Allowed: {settings.cors_origins}")
        
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
app.include_router(categories.router)

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
            "categories": {
                "create": "POST /categories",
                "list": "GET /categories",
                "get": "GET /categories/{id}",
                "update": "PUT /categories/{id}",
                "delete": "DELETE /categories/{id}",
                "add_habit": "POST /categories/{id}/habits/{habit_id}",
                "remove_habit": "DELETE /categories/{id}/habits/{habit_id}"
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
