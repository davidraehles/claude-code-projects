"""
Correlation ID middleware for distributed tracing and request correlation.

Provides end-to-end request tracking across distributed systems by:
- Generating UUID-based correlation IDs for each request
- Supporting client-provided correlation IDs (X-Correlation-ID header)
- Propagating correlation IDs through async context (contextvars)
- Auto-including correlation IDs in all structured logs
- Forwarding correlation IDs to external API calls
- Including correlation IDs in response headers

Usage:
    # In main.py
    app.add_middleware(CorrelationIdMiddleware)

    # In any async function (service, route handler, etc.)
    from app.middleware.correlation_id import get_correlation_id

    correlation_id = get_correlation_id()  # Get current correlation ID
    logger.info("Processing request", extra={"correlation_id": correlation_id})

    # When making external API calls
    headers = {"X-Correlation-ID": get_correlation_id()}
    response = await client.get(url, headers=headers)
"""

import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.logging_config import (
    get_logger,
    set_correlation_id as set_correlation_id_context,
    clear_correlation_id as clear_correlation_id_context,
    get_correlation_id as get_correlation_id_context,
)

logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages correlation IDs for distributed tracing.

    Features:
    - Generates UUID v4 for each request (or accepts client-provided ID)
    - Stores correlation ID in async-safe context (contextvars)
    - Adds X-Correlation-ID header to responses
    - Automatically propagates to logging context
    - Validates correlation ID format (UUID format)

    The correlation ID is accessible anywhere in the request lifecycle via
    get_correlation_id() function, making it ideal for:
    - Log correlation across services
    - External API call tracking
    - Error tracking and debugging
    - Performance monitoring and profiling
    """

    CORRELATION_ID_HEADER = "X-Correlation-ID"
    MAX_CORRELATION_ID_LENGTH = 128  # Prevent header injection attacks

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and inject correlation ID.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response: Response with X-Correlation-ID header
        """
        # Extract or generate correlation ID
        correlation_id = self._extract_or_generate_correlation_id(request)

        # Set correlation ID in async-safe context
        set_correlation_id_context(correlation_id)

        # Log correlation ID for request (debug level to avoid spam)
        logger.debug(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": str(request.url.path),
                "client_provided": self.CORRELATION_ID_HEADER
                in request.headers,
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers[self.CORRELATION_ID_HEADER] = correlation_id

            return response

        except Exception as e:
            # Log error with correlation ID
            logger.error(
                "Request failed with exception",
                extra={
                    "correlation_id": correlation_id,
                    "error": str(e),
                },
                exc_info=True,
            )

            # Create error response with correlation ID header
            error_response = JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error": str(e),
                },
            )
            error_response.headers[self.CORRELATION_ID_HEADER] = correlation_id
            return error_response

        finally:
            # Clear correlation ID from context
            clear_correlation_id_context()

    def _extract_or_generate_correlation_id(self, request: Request) -> str:
        """
        Extract correlation ID from request headers or generate a new one.

        Args:
            request: FastAPI request object

        Returns:
            str: Correlation ID (UUID format)
        """
        # Check if request has correlation ID header
        correlation_id = request.headers.get(self.CORRELATION_ID_HEADER)

        if correlation_id:
            # Validate client-provided correlation ID
            if not self._is_valid_correlation_id(correlation_id):
                logger.warning(
                    "Invalid correlation ID format from client, generating new one",
                    extra={
                        "invalid_correlation_id": correlation_id[:50],  # Truncate for safety
                    },
                )
                correlation_id = self._generate_correlation_id()
        else:
            # Generate new correlation ID
            correlation_id = self._generate_correlation_id()

        return correlation_id

    def _generate_correlation_id(self) -> str:
        """
        Generate a new correlation ID using UUID v4.

        Returns:
            str: UUID v4 string
        """
        return str(uuid.uuid4())

    def _is_valid_correlation_id(self, correlation_id: str) -> bool:
        """
        Validate correlation ID format.

        Checks:
        - Not empty
        - Not too long (prevents header injection)
        - Valid UUID format (flexible - accepts any reasonable format)

        Args:
            correlation_id: Correlation ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not correlation_id:
            return False

        # Check length (prevent header injection attacks)
        if len(correlation_id) > self.MAX_CORRELATION_ID_LENGTH:
            return False

        # Try to parse as UUID (most strict validation)
        try:
            uuid.UUID(correlation_id)
            return True
        except ValueError:
            # If not UUID, check if it's a reasonable string
            # (alphanumeric + hyphens, no control characters)
            if correlation_id.replace("-", "").isalnum():
                return True
            return False


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID from context.

    This function can be called from anywhere in the async call stack
    during request processing (route handlers, services, utilities, etc.).

    Returns:
        Optional[str]: Current correlation ID or None if not in request context

    Example:
        from app.middleware.correlation_id import get_correlation_id

        async def my_service_function():
            correlation_id = get_correlation_id()
            logger.info("Processing", extra={"correlation_id": correlation_id})

            # Pass to external API calls
            headers = {"X-Correlation-ID": correlation_id}
            await http_client.get(url, headers=headers)
    """
    return get_correlation_id_context()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current context.

    This is typically called by the middleware, but can be used
    for testing or special cases (background tasks, etc.).

    Args:
        correlation_id: Correlation ID to set

    Example:
        # In a background task
        set_correlation_id(str(uuid.uuid4()))
        try:
            await process_background_job()
        finally:
            clear_correlation_id()
    """
    set_correlation_id_context(correlation_id)


def clear_correlation_id() -> None:
    """
    Clear the correlation ID from the current context.

    Typically called by middleware cleanup, but useful for testing
    or background tasks that set their own correlation ID.
    """
    clear_correlation_id_context()


def get_correlation_id_header() -> dict[str, str]:
    """
    Get headers dict with current correlation ID.

    Convenience function for adding correlation ID to external API calls.

    Returns:
        dict: Headers dictionary with X-Correlation-ID

    Example:
        from app.middleware.correlation_id import get_correlation_id_header

        async def call_external_api():
            headers = get_correlation_id_header()
            response = await http_client.get(url, headers=headers)
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        return {"X-Correlation-ID": correlation_id}
    return {}
