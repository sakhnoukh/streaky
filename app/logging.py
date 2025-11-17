import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger(__name__)

def setup_logging_middleware(app):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_time = f"{process_time:.2f}"

        logger.info(
            f"request_id={request_id} "
            f"path={request.url.path} "
            f"method={request.method} "
            f"status_code={response.status_code} "
            f"duration_ms={formatted_time}"
        )

        return response
