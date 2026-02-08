"""Structured logging middleware for the Todo API."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add structured logging for all requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log structured information."""
        start_time = time.time()

        # Log incoming request
        self.logger.info({
            "event": "request_started",
            "method": request.method,
            "path": str(request.url.path),
            "query_params": str(dict(request.query_params)),
            "user_agent": request.headers.get("user-agent", ""),
            "request_id": getattr(request.state, "request_id", None)
        })

        try:
            response = await call_next(request)
        except Exception as e:
            # Log exceptions
            self.logger.error({
                "event": "request_failed",
                "method": request.method,
                "path": str(request.url.path),
                "error": str(e),
                "duration_ms": (time.time() - start_time) * 1000,
                "request_id": getattr(request.state, "request_id", None)
            })
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log completed request
        self.logger.info({
            "event": "request_completed",
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": duration * 1000,
            "request_id": getattr(request.state, "request_id", None)
        })

        return response