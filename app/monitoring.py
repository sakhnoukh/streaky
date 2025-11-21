"""
Application Insights integration for monitoring and telemetry
"""
import time
import logging
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Application Insights client (optional)
telemetry_client = None

try:
    if settings.APPINSIGHTS_INSTRUMENTATION_KEY or settings.APPINSIGHTS_CONNECTION_STRING:
        from applicationinsights import TelemetryClient
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        from opencensus.ext.azure import metrics_exporter
        
        # Initialize telemetry client
        if settings.APPINSIGHTS_INSTRUMENTATION_KEY:
            telemetry_client = TelemetryClient(settings.APPINSIGHTS_INSTRUMENTATION_KEY)
        
        # Configure Azure logging
        if settings.APPINSIGHTS_CONNECTION_STRING:
            azure_handler = AzureLogHandler(
                connection_string=settings.APPINSIGHTS_CONNECTION_STRING
            )
            logger.addHandler(azure_handler)
        
        logger.info("Application Insights initialized successfully")
except ImportError:
    logger.warning("Application Insights packages not installed. Monitoring disabled.")
except Exception as e:
    logger.error(f"Failed to initialize Application Insights: {e}")


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP requests and send telemetry to Application Insights
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Track request
        method = request.method
        path = request.url.path
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log request details
            logger.info(
                f"{method} {path} - {response.status_code} - {duration_ms:.2f}ms",
                extra={
                    "custom_dimensions": {
                        "method": method,
                        "path": path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "environment": settings.ENVIRONMENT
                    }
                }
            )
            
            # Send to Application Insights
            if telemetry_client:
                telemetry_client.track_request(
                    name=f"{method} {path}",
                    url=str(request.url),
                    success=response.status_code < 400,
                    duration=duration_ms,
                    response_code=response.status_code,
                    http_method=method,
                    properties={
                        "environment": settings.ENVIRONMENT,
                        "version": settings.VERSION
                    }
                )
                telemetry_client.flush()
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log exception
            logger.error(
                f"{method} {path} - ERROR - {duration_ms:.2f}ms: {str(e)}",
                exc_info=True,
                extra={
                    "custom_dimensions": {
                        "method": method,
                        "path": path,
                        "duration_ms": duration_ms,
                        "error": str(e),
                        "environment": settings.ENVIRONMENT
                    }
                }
            )
            
            # Track exception in Application Insights
            if telemetry_client:
                telemetry_client.track_exception()
                telemetry_client.flush()
            
            raise


def track_event(name: str, properties: Optional[dict] = None):
    """Track custom event in Application Insights"""
    if telemetry_client:
        telemetry_client.track_event(
            name,
            properties={
                "environment": settings.ENVIRONMENT,
                "version": settings.VERSION,
                **(properties or {})
            }
        )
        telemetry_client.flush()
    else:
        logger.info(f"Event: {name}", extra={"custom_dimensions": properties or {}})


def track_metric(name: str, value: float, properties: Optional[dict] = None):
    """Track custom metric in Application Insights"""
    if telemetry_client:
        telemetry_client.track_metric(
            name,
            value,
            properties={
                "environment": settings.ENVIRONMENT,
                "version": settings.VERSION,
                **(properties or {})
            }
        )
        telemetry_client.flush()
    else:
        logger.info(f"Metric: {name}={value}", extra={"custom_dimensions": properties or {}})
