"""
Unit tests for rate limiting functionality.

Tests the RateLimiter, AuthRateLimiter, and WorkflowRateLimiter classes.
"""

import pytest
import time
from datetime import datetime, timedelta

from app.utils.rate_limit import RateLimiter, AuthRateLimiter, WorkflowRateLimiter


class TestRateLimiter:
    """Test basic rate limiter functionality."""

    def test_rate_limiter_allows_within_limit(self):
        """Test that requests are allowed within rate limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        for i in range(5):
            is_allowed, metadata = limiter.is_allowed(f"test_user")
            assert is_allowed is True
            assert metadata["remaining"] >= 0

    def test_rate_limiter_blocks_over_limit(self):
        """Test that requests are blocked when exceeding rate limit."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        # Make 3 allowed requests
        for i in range(3):
            is_allowed, metadata = limiter.is_allowed("test_user")
            assert is_allowed is True

        # 4th request should be blocked
        is_allowed, metadata = limiter.is_allowed("test_user")
        assert is_allowed is False
        assert metadata["remaining"] == 0

    def test_rate_limiter_metadata(self):
        """Test that rate limiter returns correct metadata."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)

        is_allowed, metadata = limiter.is_allowed("test_user")

        assert "limit" in metadata
        assert "remaining" in metadata
        assert "reset_at" in metadata
        assert metadata["limit"] == 10
        assert isinstance(metadata["reset_at"], str)

    def test_rate_limiter_different_identifiers(self):
        """Test that different identifiers have separate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        # User 1 makes 2 requests (at limit)
        limiter.is_allowed("user_1")
        limiter.is_allowed("user_1")

        # User 2 should still be allowed
        is_allowed, metadata = limiter.is_allowed("user_2")
        assert is_allowed is True

        # User 1 should be blocked
        is_allowed, metadata = limiter.is_allowed("user_1")
        assert is_allowed is False

    def test_rate_limiter_window_expiry(self):
        """Test that rate limit resets after window expires."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # Make 2 requests (at limit)
        limiter.is_allowed("test_user")
        limiter.is_allowed("test_user")

        # Should be blocked
        is_allowed, _ = limiter.is_allowed("test_user")
        assert is_allowed is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        is_allowed, _ = limiter.is_allowed("test_user")
        assert is_allowed is True


class TestAuthRateLimiter:
    """Test authentication-specific rate limiting."""

    def test_login_rate_limit(self):
        """Test login endpoint rate limiting."""
        limiter = AuthRateLimiter()

        # Make requests up to limit
        for i in range(limiter.LOGIN_LIMIT):
            is_allowed, metadata = limiter.check_login_limit("192.168.1.1")
            assert is_allowed is True

        # Next request should be blocked
        is_allowed, metadata = limiter.check_login_limit("192.168.1.1")
        assert is_allowed is False

    def test_register_rate_limit(self):
        """Test registration endpoint rate limiting."""
        limiter = AuthRateLimiter()

        # Make requests up to limit
        for i in range(limiter.REGISTER_LIMIT):
            is_allowed, metadata = limiter.check_register_limit("192.168.1.1")
            assert is_allowed is True

        # Next request should be blocked
        is_allowed, metadata = limiter.check_register_limit("192.168.1.1")
        assert is_allowed is False

    def test_refresh_rate_limit(self):
        """Test token refresh endpoint rate limiting."""
        limiter = AuthRateLimiter()

        # Make requests up to limit
        for i in range(limiter.REFRESH_LIMIT):
            is_allowed, metadata = limiter.check_refresh_limit(123)
            assert is_allowed is True

        # Next request should be blocked
        is_allowed, metadata = limiter.check_refresh_limit(123)
        assert is_allowed is False

    def test_failed_login_tracking(self):
        """Test that failed login attempts are tracked."""
        limiter = AuthRateLimiter()

        # Record failed login attempts
        for i in range(limiter.FAILED_LOGIN_LIMIT - 1):
            limiter.record_failed_login("test@example.com", "192.168.1.1")
            is_locked, unlock_time = limiter.is_account_locked("test@example.com")
            assert is_locked is False

        # One more failure should lock the account
        limiter.record_failed_login("test@example.com", "192.168.1.1")
        is_locked, unlock_time = limiter.is_account_locked("test@example.com")
        assert is_locked is True
        assert unlock_time is not None
        assert isinstance(unlock_time, datetime)

    def test_failed_login_different_emails(self):
        """Test that failed logins are tracked separately per email."""
        limiter = AuthRateLimiter()

        # Record failures for email1
        for i in range(limiter.FAILED_LOGIN_LIMIT):
            limiter.record_failed_login("email1@example.com", "192.168.1.1")

        # email1 should be locked
        is_locked, _ = limiter.is_account_locked("email1@example.com")
        assert is_locked is True

        # email2 should not be locked
        is_locked, _ = limiter.is_account_locked("email2@example.com")
        assert is_locked is False

    def test_clear_failed_logins(self):
        """Test that failed login attempts can be cleared."""
        limiter = AuthRateLimiter()

        # Record failed attempts
        for i in range(limiter.FAILED_LOGIN_LIMIT):
            limiter.record_failed_login("test@example.com", "192.168.1.1")

        # Should be locked
        is_locked, _ = limiter.is_account_locked("test@example.com")
        assert is_locked is True

        # Clear failed logins
        limiter.clear_failed_logins("test@example.com")

        # Should no longer be locked
        is_locked, _ = limiter.is_account_locked("test@example.com")
        assert is_locked is False

    def test_account_lockout_expiry(self):
        """Test that account lockout expires after duration."""
        # Create limiter with short lockout for testing
        limiter = AuthRateLimiter()
        limiter.LOCKOUT_DURATION = 1  # 1 second lockout

        # Lock the account
        for i in range(limiter.FAILED_LOGIN_LIMIT):
            limiter.record_failed_login("test@example.com", "192.168.1.1")

        # Should be locked
        is_locked, _ = limiter.is_account_locked("test@example.com")
        assert is_locked is True

        # Wait for lockout to expire
        time.sleep(1.1)

        # Should no longer be locked
        is_locked, _ = limiter.is_account_locked("test@example.com")
        assert is_locked is False


class TestWorkflowRateLimiter:
    """Test workflow-specific rate limiting."""

    def test_workflow_rate_limit(self):
        """Test workflow endpoint rate limiting."""
        limiter = WorkflowRateLimiter()

        # Make requests up to limit
        for i in range(limiter.WORKFLOW_LIMIT):
            is_allowed, metadata = limiter.check_limit(123)
            assert is_allowed is True

        # Next request should be blocked
        is_allowed, metadata = limiter.check_limit(123)
        assert is_allowed is False

    def test_workflow_different_users(self):
        """Test that different users have separate workflow limits."""
        limiter = WorkflowRateLimiter()

        # User 1 exhausts their limit
        for i in range(limiter.WORKFLOW_LIMIT):
            limiter.check_limit(1)

        is_allowed, _ = limiter.check_limit(1)
        assert is_allowed is False

        # User 2 should still be allowed
        is_allowed, _ = limiter.check_limit(2)
        assert is_allowed is True


class TestRateLimitMetadata:
    """Test rate limit metadata and headers."""

    def test_metadata_structure(self):
        """Test that metadata has correct structure."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)

        is_allowed, metadata = limiter.is_allowed("test_user")

        # Check required fields
        assert "limit" in metadata
        assert "remaining" in metadata
        assert "reset_at" in metadata

        # Check types
        assert isinstance(metadata["limit"], int)
        assert isinstance(metadata["remaining"], int)
        assert isinstance(metadata["reset_at"], str)

        # Check values
        assert metadata["limit"] == 10
        assert 0 <= metadata["remaining"] <= 10

    def test_remaining_decrements(self):
        """Test that remaining count decrements correctly."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        for i in range(5):
            is_allowed, metadata = limiter.is_allowed("test_user")
            expected_remaining = 4 - i  # Starts at 4, goes to 0
            assert metadata["remaining"] == expected_remaining

    def test_reset_time_format(self):
        """Test that reset time is in ISO format."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)

        is_allowed, metadata = limiter.is_allowed("test_user")

        # Should be parseable as ISO datetime
        reset_at = metadata["reset_at"]
        parsed = datetime.fromisoformat(reset_at.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
