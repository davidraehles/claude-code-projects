"""
Database-Driven Rate Limiting Middleware for FastAPI.

Enhanced version that uses database-backed rate limiting configuration
with support for:
- Dynamic policy updates without code changes
- User-specific overrides
- Whitelisting for internal services
- Burst allowances
- Comprehensive metrics

This middleware replaces the hardcoded rate_limit_middleware.py with
a flexible, database-driven approach.
"""

import logging
import re
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.rate_limit import RateLimiter
from app.schemas.error import ErrorResponse, ErrorType
from app.config.rate_limit_config import rate_limit_config

logger = logging.getLogger(__name__)


class DatabaseDrivenRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting middleware with database-driven configuration.

    Applies dynamic rate limits based on endpoint patterns, user overrides,
    and whitelist entries stored in the database. Returns 429 Too Many Requests
    when limits are exceeded.
    """

    def __init__(
        self,
        app,
        redis_client: Optional[object] = None,
        enable_rate_limiting: bool = True,
    ):
        """
        Initialize database-driven rate limit middleware.

        Args:
            app: FastAPI application instance
            redis_client: Optional Redis client for distributed rate limiting
            enable_rate_limiting: Whether to enable rate limiting (disable for testing)
        """
        super().__init__(app)
        self.redis_client = redis_client
        self.enable_rate_limiting = enable_rate_limiting

        # Cache of rate limiter instances by configuration hash
        self._limiter_cache = {}

        logger.info(
            f"Database-driven rate limit middleware initialized: enabled={enable_rate_limiting}"
        )

    def _get_or_create_limiter(
        self, requests_per_window: int, window_seconds: int
    ) -> RateLimiter:
        """
        Get or create a rate limiter with the specified configuration.

        Caches limiter instances to avoid creating new objects for each request.

        Args:
            requests_per_window: Max requests allowed per window
            window_seconds: Time window in seconds

        Returns:
            RateLimiter instance
        """
        cache_key = f"{requests_per_window}_{window_seconds}"

        if cache_key not in self._limiter_cache:
            self._limiter_cache[cache_key] = RateLimiter(
                max_requests=requests_per_window,
                window_seconds=window_seconds,
                redis_client=self.redis_client,
            )

        return self._limiter_cache[cache_key]

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

    def _extract_user_id(self, request: Request) -> Optional[int]:
        """
        Extract user ID from request if authenticated.

        TODO: This should be integrated with actual authentication system.
        For now, we'll try to extract from request state if available.

        Args:
            request: FastAPI request object

        Returns:
            User ID or None if not authenticated
        """
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, "user") and request.state.user:
            return getattr(request.state.user, "id", None)

        # Try to get from JWT claims if available
        if hasattr(request.state, "user_id"):
            return request.state.user_id

        return None

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
            "/openapi.json",
            "/docs",
            "/redoc",
        ]

        return request.url.path in exempt_paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and apply database-driven rate limiting.

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

        # Extract client information
        client_ip = self._extract_client_ip(request)
        user_id = self._extract_user_id(request)
        endpoint = request.url.path

        try:
            # Get database session
            # Note: We need to get a fresh session for each request
            async for db in get_db():
                try:
                    # Get effective rate limit configuration
                    limit_config = await rate_limit_config.get_effective_limit(
                        endpoint=endpoint,
                        user_id=user_id,
                        ip_address=client_ip,
                        db=db,
                    )

                    # Skip rate limiting if whitelisted
                    if limit_config.get("is_whitelisted"):
                        logger.debug(
                            f"Skipping rate limit for whitelisted identifier: "
                            f"{limit_config['identifier']}"
                        )
                        return await call_next(request)

                    # Get or create rate limiter with the configured limits
                    base_requests = limit_config["requests_per_window"]
                    window_seconds = limit_config["window_seconds"]
                    burst_multiplier = limit_config["burst_multiplier"]

                    # Apply burst multiplier for the actual limit
                    effective_limit = int(base_requests * burst_multiplier)

                    limiter = self._get_or_create_limiter(effective_limit, window_seconds)

                    # Check rate limit
                    identifier = limit_config["identifier"]
                    is_allowed, metadata = limiter.is_allowed(identifier)

                    # Add rate limit headers to response
                    if is_allowed:
                        # Process request
                        response = await call_next(request)

                        # Add rate limit info headers
                        response.headers["X-RateLimit-Limit"] = str(metadata["limit"])
                        response.headers["X-RateLimit-Remaining"] = str(metadata["remaining"])
                        response.headers["X-RateLimit-Reset"] = metadata["reset_at"]
                        response.headers["X-RateLimit-Policy"] = limit_config["limit_type"]

                        return response
                    else:
                        # Rate limit exceeded
                        logger.warning(
                            f"Rate limit exceeded for {identifier} on {request.method} {endpoint}",
                            extra={
                                "client_ip": client_ip,
                                "user_id": user_id,
                                "method": request.method,
                                "path": endpoint,
                                "limit": metadata["limit"],
                                "limit_type": limit_config["limit_type"],
                            },
                        )

                        # Calculate retry after in seconds
                        from datetime import datetime

                        try:
                            reset_time = datetime.fromisoformat(metadata["reset_at"])
                            retry_after = max(
                                1, int((reset_time - datetime.now()).total_seconds())
                            )
                        except (ValueError, TypeError, KeyError):
                            retry_after = window_seconds

                        # Create error response
                        error_response = ErrorResponse(
                            error_type=ErrorType.RATE_LIMIT,
                            message="Rate limit exceeded. Please try again later.",
                            details={
                                "limit": metadata["limit"],
                                "remaining": 0,
                                "reset_at": metadata["reset_at"],
                                "retry_after": retry_after,
                                "limit_type": limit_config["limit_type"],
                                "policy": f"{base_requests} requests per {window_seconds}s "
                                f"(burst: {effective_limit})",
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
                                "X-RateLimit-Policy": limit_config["limit_type"],
                                "Retry-After": str(retry_after),
                            },
                        )
                finally:
                    # Ensure database session is closed
                    await db.close()

        except Exception as e:
            # Log error but don't block request if rate limiter fails
            logger.error(
                f"Rate limit check failed for {client_ip}: {str(e)}",
                extra={"client_ip": client_ip, "user_id": user_id, "error": str(e)},
                exc_info=True,
            )
            # Allow request through if rate limiter fails (fail open for availability)
            return await call_next(request)
