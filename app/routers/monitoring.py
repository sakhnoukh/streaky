"""
Health check and monitoring endpoints
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
import psutil
import os

from app.db import SessionLocal
from app.config import settings
from app.models import Habit, Entry
from app.monitoring import get_metrics, CONTENT_TYPE_LATEST

router = APIRouter(tags=["Monitoring"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for Azure App Service and monitoring
    Checks database connectivity and returns service status
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        db_message = "Database connection successful"
    except Exception as e:
        db_status = "unhealthy"
        db_message = f"Database error: {str(e)}"
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": db_status,
                "message": db_message
            }
        )
    
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "database": {
            "status": db_status,
            "message": db_message,
            "type": "Azure SQL" if settings.AZURE_SQL_SERVER else "SQLite"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/healthz")
def kubernetes_health_check():
    """
    Simple health check for Kubernetes/container orchestration
    Returns 200 OK if service is running
    """
    return {"ok": True}


@router.get("/version")
def get_version():
    """
    Get application version and environment information
    """
    return {
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "python_version": os.sys.version,
        "deployed_at": os.getenv("DEPLOYMENT_TIME", "unknown")
    }


@router.get("/metrics")
def prometheus_metrics():
    """
    Prometheus metrics endpoint for scraping
    Returns metrics in Prometheus text format
    """
    return Response(content=get_metrics(), media_type=CONTENT_TYPE_LATEST)


@router.get("/business-metrics")
def get_business_metrics(db: Session = Depends(get_db)):
    """
    Get business metrics for monitoring dashboards (JSON format)
    """
    try:
        # Get database metrics
        total_habits = db.query(Habit).count()
        total_entries = db.query(Entry).count()
        
        # Get today's activity (this would need more sophisticated queries in production)
        from datetime import date
        today = date.today()
        entries_today = db.query(Entry).filter(Entry.date == today).count()
        
        return {
            "database": {
                "total_habits": total_habits,
                "total_entries": total_entries,
                "entries_today": entries_today
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


@router.get("/system")
def get_system_metrics():
    """
    Get system resource metrics for monitoring
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent": disk.percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system metrics: {str(e)}"
        )
