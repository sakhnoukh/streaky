"""
Prometheus metrics integration for monitoring and telemetry
"""
import time
import logging
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest
CONTENT_TYPE_LATEST = 'text/plain; version=0.0.4; charset=utf-8'
from app.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'active_requests',
    'Number of active HTTP requests'
)

http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

# Business metrics
habits_created_total = Counter(
    'habits_created_total',
    'Total habits created'
)

entries_logged_total = Counter(
    'entries_logged_total',
    'Total entries logged',
    ['habit_id']
)

active_habits = Gauge(
    'active_habits',
    'Number of active habits'
)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP requests and expose Prometheus metrics
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        active_requests.inc()
        
        # Track request
        method = request.method
        path = request.url.path
        
        # Normalize path for metrics (remove IDs)
        endpoint = self._normalize_path(path)
        
        try:
            # Get request size if available
            request_size = 0
            if hasattr(request, '_body'):
                request_size = len(request._body) if request._body else 0
            
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Get response size
            response_size = 0
            if hasattr(response, 'body'):
                response_size = len(response.body) if response.body else 0
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if request_size > 0:
                http_request_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(request_size)
            
            if response_size > 0:
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
            
            # Track errors
            if response.status_code >= 400:
                error_type = 'client_error' if 400 <= response.status_code < 500 else 'server_error'
                http_errors_total.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()
            
            # Log request details
            logger.info(
                f"{method} {path} - {response.status_code} - {duration*1000:.2f}ms",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration * 1000,
                    "environment": settings.ENVIRONMENT
                }
            )
            
            active_requests.dec()
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Track exception
            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                error_type='exception'
            ).inc()
            
            # Log exception
            logger.error(
                f"{method} {path} - ERROR - {duration*1000:.2f}ms: {str(e)}",
                exc_info=True,
                extra={
                    "method": method,
                    "path": path,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "environment": settings.ENVIRONMENT
                }
            )
            
            active_requests.dec()
            raise
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for metrics by replacing IDs with placeholders
        e.g., /habits/123/entries -> /habits/{id}/entries
        """
        import re
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path, flags=re.IGNORECASE)
        return path


def track_event(name: str, properties: Optional[dict] = None):
    """Track custom event (logged for Prometheus)"""
    logger.info(f"Event: {name}", extra={"custom_dimensions": properties or {}})


def track_metric(name: str, value: float, properties: Optional[dict] = None):
    """Track custom metric (logged for Prometheus)"""
    logger.info(f"Metric: {name}={value}", extra={"custom_dimensions": properties or {}})


def track_habit_created():
    """Track habit creation"""
    habits_created_total.inc()


def track_entry_logged(habit_id: int):
    """Track entry logging"""
    entries_logged_total.labels(habit_id=str(habit_id)).inc()


def get_metrics():
    """Get Prometheus metrics in text format"""
    return generate_latest()
