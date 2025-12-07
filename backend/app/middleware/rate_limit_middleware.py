"""
Rate Limiting Middleware for FastAPI.

Provides request rate limiting at the middleware level to protect
the API from abuse and ensure fair resource allocation.

Features:
- Per-IP rate limiting for all requests
- Configurable limits based on endpoint patterns
- Redis-backed distributed rate limiting (with in-memory fallback)
- Standard HTTP 429 responses with Retry-After header
- Integration with existing RateLimiter infrastructure

This middleware wraps the existing rate limiting utilities and applies
them automatically to all incoming requests.
"""

import logging
import re
from typing import Callable, Optional, Dict, Pattern

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.rate_limit import RateLimiter
from app.schemas.error import ErrorResponse, ErrorType

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces rate limits on incoming HTTP requests.

    Applies rate limits based on client IP address and endpoint patterns.
    Returns 429 Too Many Requests when limits are exceeded.
    """

    def __init__(
        self,
        app,
        redis_client: Optional[object] = None,
        default_limit: int = 100,  # 100 requests per minute by default
        default_window: int = 60,  # 1 minute window
        enable_rate_limiting: bool = True
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application instance
            redis_client: Optional Redis client for distributed rate limiting
            default_limit: Default max requests per window
            default_window: Default time window in seconds
            enable_rate_limiting: Whether to enable rate limiting (disable for testing)
        """
        super().__init__(app)
        self.redis_client = redis_client
        self.default_limit = default_limit
        self.default_window = default_window
        self.enable_rate_limiting = enable_rate_limiting

        # Create default rate limiter
        self.default_limiter = RateLimiter(
            max_requests=default_limit,
            window_seconds=default_window,
            redis_client=redis_client
        )

        # Endpoint-specific rate limiters with pre-compiled regex patterns
        self.endpoint_limiters: Dict[Pattern, RateLimiter] = {}
        # Cache for path-to-limiter mapping to avoid repeated pattern matching
        self._limiter_cache: Dict[str, RateLimiter] = {}
        self._configure_endpoint_limits()

        logger.info(
            f"Rate limit middleware initialized: "
            f"default={default_limit}/{default_window}s, "
            f"enabled={enable_rate_limiting}"
        )

    def _configure_endpoint_limits(self) -> None:
        """
        Configure rate limits for specific endpoints.

        Different endpoints can have different rate limits based on
        their resource intensity and security requirements.
        Patterns are pre-compiled at initialization for performance.
        """
        # Define endpoint patterns and their rate limit configurations
        patterns = [
            # Stricter limits for authentication endpoints (handled by AuthRateLimiter)
            # These are already protected, so we apply generous limits here
            (r"^/api/v1/auth/login$", 20, 60),       # 20 attempts per minute
            (r"^/api/v1/auth/register$", 10, 60),    # 10 attempts per minute
            # Stricter limits for expensive workflow operations
            (r"^/api/v1/workflows/.*$", 10, 300),    # 10 requests per 5 minutes
            # Moderate limits for search endpoints
            (r"^/api/v1/recipes/search$", 30, 60),   # 30 searches per minute
            # Generous limits for read-only endpoints
            (r"^/api/v1/recipes/\d+$", 60, 60),      # 60 requests per minute
        ]

        # Pre-compile regex patterns and create rate limiters
        for pattern_str, max_requests, window_seconds in patterns:
            compiled_pattern = re.compile(pattern_str)
            self.endpoint_limiters[compiled_pattern] = RateLimiter(
                max_requests=max_requests,
                window_seconds=window_seconds,
                redis_client=self.redis_client
            )

    def _get_limiter_for_path(self, path: str) -> RateLimiter:
        """
        Get the appropriate rate limiter for a given path.

        Uses caching to avoid repeated pattern matching for frequently accessed paths.

        Args:
            path: Request path

        Returns:
            RateLimiter instance
        """
        # Check cache first for performance
        if path in self._limiter_cache:
            return self._limiter_cache[path]

        # Check for endpoint-specific limiter
        limiter = None
        for pattern, candidate_limiter in self.endpoint_limiters.items():
            if re.match(pattern, path):
                limiter = candidate_limiter
                break

        # Use default limiter if no specific pattern matched
        if limiter is None:
            limiter = self.default_limiter

        # Cache the result
        self._limiter_cache[path] = limiter

        return limiter

    def _extract_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Handles proxy headers (X-Forwarded-For, X-Real-IP) for correct
        IP identification behind load balancers and reverse proxies.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address as string
        """
        # Check X-Forwarded-For header (standard for proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first (client)
            client_ip = forwarded_for.split(",")[0].strip()
            return client_ip

        # Check X-Real-IP header (alternative proxy header)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client host
        if request.client:
            return request.client.host

        # Default fallback
        return "unknown"

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """
        Check if rate limiting should be skipped for this request.

        Args:
            request: FastAPI request object

        Returns:
            True if rate limiting should be skipped
        """
        # Skip rate limiting for health checks and metrics
        exempt_paths = [
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/openapi.json"
        ]

        return request.url.path in exempt_paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and apply rate limiting.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response: Either the route response or 429 Too Many Requests
        """
        # Skip if rate limiting is disabled
        if not self.enable_rate_limiting:
            return await call_next(request)

        # Skip rate limiting for exempt paths
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        # Extract client identifier (IP address)
        client_ip = self._extract_client_ip(request)

        # Get appropriate rate limiter for this path
        limiter = self._get_limiter_for_path(request.url.path)

        # Check rate limit
        identifier = f"middleware_{client_ip}_{request.method}_{request.url.path}"

        try:
            is_allowed, metadata = limiter.is_allowed(identifier)

            # Add rate limit headers to response
            if is_allowed:
                # Process request
                response = await call_next(request)

                # Add rate limit info headers
                response.headers["X-RateLimit-Limit"] = str(metadata["limit"])
                response.headers["X-RateLimit-Remaining"] = str(metadata["remaining"])
                response.headers["X-RateLimit-Reset"] = metadata["reset_at"]

                return response
            else:
                # Rate limit exceeded
                logger.warning(
                    f"Rate limit exceeded for {client_ip} on {request.method} {request.url.path}",
                    extra={
                        "client_ip": client_ip,
                        "method": request.method,
                        "path": request.url.path,
                        "limit": metadata["limit"],
                    }
                )

                # Calculate retry after in seconds
                from datetime import datetime
                try:
                    reset_time = datetime.fromisoformat(metadata["reset_at"])
                    retry_after = max(1, int((reset_time - datetime.now()).total_seconds()))
                except (ValueError, TypeError, KeyError):
                    retry_after = limiter.window_seconds

                # Create error response
                error_response = ErrorResponse(
                    error_type=ErrorType.RATE_LIMIT,
                    message="Rate limit exceeded. Please try again later.",
                    details={
                        "limit": metadata["limit"],
                        "remaining": 0,
                        "reset_at": metadata["reset_at"],
                        "retry_after": retry_after
                    },
                    path=str(request.url.path),
                    request_id=request.headers.get("X-Request-ID"),
                )

                # Return 429 Too Many Requests
                return JSONResponse(
                    status_code=429,
                    content=error_response.model_dump(mode="json"),
                    headers={
                        "X-RateLimit-Limit": str(metadata["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": metadata["reset_at"],
                        "Retry-After": str(retry_after)
                    }
                )

        except Exception as e:
            # Log error but don't block request if rate limiter fails
            logger.error(
                f"Rate limit check failed for {client_ip}: {str(e)}",
                extra={"client_ip": client_ip, "error": str(e)},
                exc_info=True
            )
            # Allow request through if rate limiter fails (fail open)
            return await call_next(request)
