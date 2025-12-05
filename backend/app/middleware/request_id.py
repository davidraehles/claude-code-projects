"""
Request ID middleware for distributed tracing.

Injects unique request IDs into each HTTP request and response,
enabling correlation across distributed systems and logs.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import set_request_id, clear_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds unique request IDs to each request.

    Features:
    - Generates UUID for each request
    - Sets request ID in context for logging
    - Adds X-Request-ID header to response
    - Supports existing X-Request-ID from client
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and inject request ID.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response: Response with X-Request-ID header
        """
        # Check if request already has an ID (from upstream service)
        request_id = request.headers.get("X-Request-ID")

        if not request_id:
            # Generate new request ID
            request_id = str(uuid.uuid4())

        # Set request ID in context for logging
        set_request_id(request_id)

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        finally:
            # Clear request ID from context
            clear_request_id()
