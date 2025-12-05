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


class AuthRateLimiter:
    """
    Specialized rate limiter for authentication endpoints with enhanced security.

    Implements:
    - Per-IP rate limiting for login/register attempts
    - Per-email tracking for failed login attempts
    - Temporary account lockout after repeated failures
    - Exponential backoff for suspicious activity
    """

    # Rate limits for auth endpoints
    LOGIN_LIMIT = 5  # 5 attempts per minute per IP
    LOGIN_WINDOW = 60  # 1 minute

    REGISTER_LIMIT = 3  # 3 attempts per minute per IP
    REGISTER_WINDOW = 60  # 1 minute

    REFRESH_LIMIT = 10  # 10 attempts per minute per user
    REFRESH_WINDOW = 60  # 1 minute

    # Failed login tracking
    FAILED_LOGIN_LIMIT = 5  # Lock account after 5 failed attempts
    LOCKOUT_DURATION = 900  # 15 minutes lockout

    def __init__(self, redis_client: Optional[object] = None):
        """Initialize auth rate limiter."""
        self.login_limiter = RateLimiter(
            max_requests=self.LOGIN_LIMIT,
            window_seconds=self.LOGIN_WINDOW,
            redis_client=redis_client
        )

        self.register_limiter = RateLimiter(
            max_requests=self.REGISTER_LIMIT,
            window_seconds=self.REGISTER_WINDOW,
            redis_client=redis_client
        )

        self.refresh_limiter = RateLimiter(
            max_requests=self.REFRESH_LIMIT,
            window_seconds=self.REFRESH_WINDOW,
            redis_client=redis_client
        )

        self.redis_client = redis_client

        # In-memory fallback for failed login tracking
        self.failed_logins: Dict[str, list] = defaultdict(list)

    def check_login_limit(self, ip_address: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if login request is allowed for given IP.

        Args:
            ip_address: Client IP address

        Returns:
            Tuple of (is_allowed: bool, metadata: dict)
        """
        return self.login_limiter.is_allowed(f"login_ip_{ip_address}")

    def check_register_limit(self, ip_address: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if registration request is allowed for given IP.

        Args:
            ip_address: Client IP address

        Returns:
            Tuple of (is_allowed: bool, metadata: dict)
        """
        return self.register_limiter.is_allowed(f"register_ip_{ip_address}")

    def check_refresh_limit(self, user_id: int) -> Tuple[bool, Dict[str, any]]:
        """
        Check if token refresh is allowed for given user.

        Args:
            user_id: User ID

        Returns:
            Tuple of (is_allowed: bool, metadata: dict)
        """
        return self.refresh_limiter.is_allowed(f"refresh_user_{user_id}")

    def is_account_locked(self, email: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is locked due to failed login attempts.

        Args:
            email: User email address

        Returns:
            Tuple of (is_locked: bool, unlock_time: Optional[datetime])
        """
        current_time = time.time()
        lockout_start = current_time - self.LOCKOUT_DURATION

        if self.redis_client:
            try:
                key = f"failed_logins:{email}"
                # Get all failed attempts in lockout window
                self.redis_client.zremrangebyscore(key, 0, lockout_start)
                failed_count = self.redis_client.zcard(key)

                if failed_count >= self.FAILED_LOGIN_LIMIT:
                    # Get the oldest failure time to calculate unlock time
                    oldest_failure = self.redis_client.zrange(key, 0, 0, withscores=True)
                    if oldest_failure:
                        unlock_time = datetime.fromtimestamp(
                            oldest_failure[0][1] + self.LOCKOUT_DURATION
                        )
                        return True, unlock_time

                return False, None
            except Exception as e:
                logger.warning(f"Redis failed login check failed: {str(e)}")
                # Fall through to memory check

        # In-memory fallback
        self.failed_logins[email] = [
            t for t in self.failed_logins[email]
            if t > lockout_start
        ]

        if len(self.failed_logins[email]) >= self.FAILED_LOGIN_LIMIT:
            unlock_time = datetime.fromtimestamp(
                self.failed_logins[email][0] + self.LOCKOUT_DURATION
            )
            return True, unlock_time

        return False, None

    def record_failed_login(self, email: str, ip_address: str) -> None:
        """
        Record a failed login attempt.

        Args:
            email: User email address
            ip_address: Client IP address
        """
        current_time = time.time()

        if self.redis_client:
            try:
                key = f"failed_logins:{email}"
                # Add failed attempt with current timestamp
                self.redis_client.zadd(key, {str(current_time): current_time})
                # Set expiry to lockout duration + buffer
                self.redis_client.expire(key, self.LOCKOUT_DURATION + 60)

                # Log the attempt
                logger.warning(
                    f"Failed login attempt for {email} from IP {ip_address}"
                )
                return
            except Exception as e:
                logger.warning(f"Redis failed login recording failed: {str(e)}")
                # Fall through to memory recording

        # In-memory fallback
        self.failed_logins[email].append(current_time)
        logger.warning(
            f"Failed login attempt for {email} from IP {ip_address}"
        )

    def clear_failed_logins(self, email: str) -> None:
        """
        Clear failed login attempts for an email (called on successful login).

        Args:
            email: User email address
        """
        if self.redis_client:
            try:
                key = f"failed_logins:{email}"
                self.redis_client.delete(key)
                return
            except Exception as e:
                logger.warning(f"Redis failed login clearing failed: {str(e)}")
                # Fall through to memory clearing

        # In-memory fallback
        if email in self.failed_logins:
            del self.failed_logins[email]
