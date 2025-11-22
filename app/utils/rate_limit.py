"""
Rate limiting utilities for API endpoints.

Provides simple in-memory and Redis-based rate limiting to prevent abuse
of expensive operations like MCP workflow calls.
"""

import logging
import time
from typing import Optional, Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window counter.

    Tracks request counts per identifier (e.g., user ID) within a time window.
    Falls back to in-memory if Redis is unavailable.
    """

    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 60,
        redis_client: Optional[object] = None
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = redis_client

        # In-memory fallback: dict of identifier -> list of (timestamp, count)
        self.memory_store: Dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed for given identifier.

        Args:
            identifier: User ID, API key, or other identifier string

        Returns:
            Tuple of (is_allowed: bool, metadata: dict with limit info)
            metadata includes: limit, remaining, reset_at
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Try Redis first if available
        if self.redis_client:
            return self._redis_is_allowed(identifier, current_time)

        # Fall back to in-memory
        return self._memory_is_allowed(identifier, current_time, window_start)

    def _memory_is_allowed(
        self,
        identifier: str,
        current_time: float,
        window_start: float
    ) -> Tuple[bool, Dict[str, any]]:
        """Check rate limit using in-memory store."""
        # Clean old entries
        self.memory_store[identifier] = [
            t for t in self.memory_store[identifier]
            if t > window_start
        ]

        request_count = len(self.memory_store[identifier])
        is_allowed = request_count < self.max_requests

        if is_allowed:
            self.memory_store[identifier].append(current_time)

        reset_at = datetime.fromtimestamp(
            self.memory_store[identifier][0] + self.window_seconds
            if self.memory_store[identifier]
            else current_time + self.window_seconds
        )

        return is_allowed, {
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - request_count - (1 if is_allowed else 0)),
            "reset_at": reset_at.isoformat()
        }

    def _redis_is_allowed(
        self,
        identifier: str,
        current_time: float
    ) -> Tuple[bool, Dict[str, any]]:
        """Check rate limit using Redis."""
        try:
            key = f"rate_limit:{identifier}"

            # Use Redis to count requests in window
            pipeline = self.redis_client.pipeline()
            pipeline.multi()
            pipeline.zadd(key, {str(current_time): current_time})
            pipeline.zremrangebyscore(key, 0, current_time - self.window_seconds)
            pipeline.zcard(key)
            pipeline.expire(key, self.window_seconds + 1)

            results = pipeline.execute()
            request_count = results[2]

            is_allowed = request_count <= self.max_requests

            reset_seconds = self.window_seconds
            reset_at = datetime.now() + timedelta(seconds=reset_seconds)

            return is_allowed, {
                "limit": self.max_requests,
                "remaining": max(0, self.max_requests - request_count),
                "reset_at": reset_at.isoformat()
            }
        except Exception as e:
            logger.warning(f"Redis rate limit failed, falling back to memory: {str(e)}")
            # Fall back to memory on Redis error
            window_start = current_time - self.window_seconds
            return self._memory_is_allowed(identifier, current_time, window_start)


class WorkflowRateLimiter:
    """
    Specialized rate limiter for expensive workflow operations.

    Prevents abuse of MCP calls by limiting requests per user.
    """

    # 10 requests per 5 minutes for workflow endpoint
    WORKFLOW_LIMIT = 10
    WORKFLOW_WINDOW = 300  # 5 minutes

    def __init__(self, redis_client: Optional[object] = None):
        """Initialize workflow rate limiter."""
        self.limiter = RateLimiter(
            max_requests=self.WORKFLOW_LIMIT,
            window_seconds=self.WORKFLOW_WINDOW,
            redis_client=redis_client
        )

    def check_limit(self, user_id: int) -> Tuple[bool, Dict[str, any]]:
        """
        Check if user can make a workflow request.

        Args:
            user_id: User ID making the request

        Returns:
            Tuple of (is_allowed: bool, metadata: dict)
        """
        return self.limiter.is_allowed(f"workflow_user_{user_id}")
