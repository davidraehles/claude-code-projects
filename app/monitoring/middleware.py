"""
Prometheus middleware for FastAPI.

Automatically tracks HTTP request metrics.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.monitoring.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track Prometheus metrics for HTTP requests.

    Tracks:
    - Request count by method, endpoint, and status
    - Request duration by method and endpoint
    - Requests currently in progress
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and track metrics.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            Response: The HTTP response
        """
        # Extract method and path
        method = request.method
        path = request.url.path

        # Normalize path (replace IDs with placeholder)
        normalized_path = self._normalize_path(path)

        # Track requests in progress
        http_requests_in_progress.labels(method=method, endpoint=normalized_path).inc()

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Track metrics
            http_requests_total.labels(
                method=method,
                endpoint=normalized_path,
                status=response.status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)

            return response

        except Exception as e:
            # Track failed requests
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=normalized_path,
                status=500
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)

            raise e

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=normalized_path).dec()

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path by replacing IDs with placeholders.

        Args:
            path: Original path

        Returns:
            Normalized path

        Examples:
            /api/v1/recipes/123 -> /api/v1/recipes/{id}
            /api/v1/users/456/profile -> /api/v1/users/{id}/profile
        """
        import re

        # Replace numeric IDs
        normalized = re.sub(r'/\d+', '/{id}', path)

        # Replace UUIDs
        uuid_pattern = r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        normalized = re.sub(uuid_pattern, '/{id}', normalized)

        return normalized
