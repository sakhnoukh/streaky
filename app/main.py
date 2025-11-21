from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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

# Configure CORS for frontend (Azure + local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
                "metrics": "GET /metrics",
                "system": "GET /system"
            }
        }
    }
