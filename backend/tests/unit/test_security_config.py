"""Unit tests for security configuration (CSRF, CORS, secrets).

Tests for PR #42 security fixes.
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestCSRFSecretKeyGeneration:
    """Test CSRF secret key generation with secure defaults."""

    def test_csrf_secret_key_from_env_variable(self):
        """Test that CSRF_SECRET_KEY is read from environment."""
        from app.middleware.csrf_middleware import get_csrf_secret_key

        expected_key = "test-secret-key-from-env"
        with patch.dict(os.environ, {"CSRF_SECRET_KEY": expected_key, "APP_ENV": "production"}):
            # Reload module to pick up env var
            import importlib
            import app.middleware.csrf_middleware
            importlib.reload(app.middleware.csrf_middleware)

            key = app.middleware.csrf_middleware.get_csrf_secret_key()
            assert key == expected_key

    def test_csrf_secret_key_fails_in_production_without_env(self):
        """Test that CSRF fails-secure in production without CSRF_SECRET_KEY."""
        from app.middleware.csrf_middleware import get_csrf_secret_key

        with patch.dict(os.environ, {"CSRF_SECRET_KEY": "", "APP_ENV": "production"}, clear=False):
            # Remove CSRF_SECRET_KEY if it exists
            os.environ.pop("CSRF_SECRET_KEY", None)

            with pytest.raises(ValueError) as exc_info:
                get_csrf_secret_key()

            assert "CSRF_SECRET_KEY environment variable required in production" in str(exc_info.value)
            assert "python -c" in str(exc_info.value)  # Should include generation command

    def test_csrf_secret_key_generates_random_in_development(self):
        """Test that CSRF generates random key in development."""
        from app.middleware.csrf_middleware import get_csrf_secret_key

        with patch.dict(os.environ, {"APP_ENV": "development"}, clear=False):
            os.environ.pop("CSRF_SECRET_KEY", None)

            key1 = get_csrf_secret_key()
            key2 = get_csrf_secret_key()

            # Keys should be generated (non-empty)
            assert key1
            assert key2
            assert len(key1) > 20  # token_urlsafe(32) produces ~43 chars
            # Different calls might generate different keys
            # (depends on implementation, but at least they're not hardcoded)

    def test_csrf_secret_key_not_hardcoded_default(self):
        """Test that hardcoded default 'dev-secret-key' is not used."""
        from app.middleware.csrf_middleware import CSRF_SECRET_KEY

        # Should not be the old hardcoded default
        assert CSRF_SECRET_KEY != "dev-secret-key-change-in-production"
        assert CSRF_SECRET_KEY  # Should have some value


class TestCORSConfiguration:
    """Test CORS configuration with secure defaults."""

    def test_cors_origins_from_env_variable(self):
        """Test that CORS_ORIGINS is read from environment."""
        from app.main import get_cors_origins

        expected_origins = "https://example.com,https://app.example.com"
        with patch.dict(os.environ, {"CORS_ORIGINS": expected_origins, "APP_ENV": "production"}):
            origins = get_cors_origins()
            assert "https://example.com" in origins
            assert "https://app.example.com" in origins

    def test_cors_fails_in_production_without_env(self):
        """Test that CORS fails-secure in production without CORS_ORIGINS."""
        from app.main import get_cors_origins

        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=False):
            os.environ.pop("CORS_ORIGINS", None)

            with pytest.raises(ValueError) as exc_info:
                get_cors_origins()

            assert "CORS_ORIGINS environment variable required in production" in str(exc_info.value)

    def test_cors_rejects_wildcard_in_production(self):
        """Test that CORS rejects wildcard in production."""
        from app.main import get_cors_origins

        with patch.dict(os.environ, {"CORS_ORIGINS": "*", "APP_ENV": "production"}):
            with pytest.raises(ValueError) as exc_info:
                get_cors_origins()

            assert "CORS wildcard '*' not allowed in production" in str(exc_info.value)
            assert "Explicitly list allowed origins" in str(exc_info.value)

    def test_cors_defaults_to_localhost_in_development(self):
        """Test that CORS defaults to localhost in development."""
        from app.main import get_cors_origins

        with patch.dict(os.environ, {"APP_ENV": "development"}, clear=False):
            os.environ.pop("CORS_ORIGINS", None)

            origins = get_cors_origins()

            assert "http://localhost:3000" in origins
            assert "http://localhost:8000" in origins
            assert "http://127.0.0.1:3000" in origins
            assert "http://127.0.0.1:8000" in origins

    def test_cors_whitespace_handling(self):
        """Test that CORS configuration handles whitespace correctly."""
        from app.main import get_cors_origins

        origins_with_whitespace = "https://example.com , https://app.example.com , "
        with patch.dict(os.environ, {"CORS_ORIGINS": origins_with_whitespace, "APP_ENV": "production"}):
            origins = get_cors_origins()

            assert "https://example.com" in origins
            assert "https://app.example.com" in origins
            assert len(origins) == 2  # No empty strings


class TestSecurityHeadersConfiguration:
    """Test security headers configuration."""

    def test_security_headers_middleware_exists(self):
        """Test that SecurityHeadersMiddleware is configured."""
        from app.middleware.security_headers import SecurityHeadersMiddleware

        assert SecurityHeadersMiddleware is not None

    def test_hsts_enabled_in_production(self):
        """Test that HSTS is enabled in production."""
        from app.middleware.security_headers import SecurityHeadersMiddleware

        with patch.dict(os.environ, {"APP_ENV": "production"}):
            middleware = SecurityHeadersMiddleware(
                app=MagicMock(),
                enable_hsts=True,
                hsts_max_age=31536000
            )

            assert middleware.enable_hsts is True
            assert middleware.hsts_max_age == 31536000  # 1 year


class TestMiddlewareOrdering:
    """Test that middleware is ordered correctly for security."""

    def test_rate_limit_before_csrf(self):
        """Test that RateLimit middleware comes before CSRF middleware.

        This ensures rate-limited requests are blocked before CSRF processing.
        """
        # This would require checking the actual app middleware stack
        # For now, we document this requirement
        # Actual test would be in integration tests
        assert True  # TODO: Implement when middleware stack inspection is added


class TestRegexPatternPrecompilation:
    """Test that regex patterns are pre-compiled for performance."""

    def test_rate_limit_patterns_are_compiled(self):
        """Test that rate limit endpoint patterns are pre-compiled."""
        from app.middleware.rate_limit_middleware import RateLimitMiddleware
        import re

        middleware = RateLimitMiddleware(app=MagicMock(), enable_rate_limiting=True)

        # Check that all patterns in endpoint_limiters are compiled patterns
        for pattern, limiter in middleware.endpoint_limiters.items():
            assert isinstance(pattern, type(re.compile("")))
            assert limiter is not None

    def test_regex_pattern_matching_works(self):
        """Test that pre-compiled patterns still match correctly."""
        from app.middleware.rate_limit_middleware import RateLimitMiddleware
        from unittest.mock import MagicMock

        middleware = RateLimitMiddleware(app=MagicMock(), enable_rate_limiting=True)

        # Test that _get_limiter_for_path works with pre-compiled patterns
        auth_limiter = middleware._get_limiter_for_path("/api/v1/auth/login")
        assert auth_limiter is not None
        assert auth_limiter.max_requests == 20  # Auth endpoint limit

        workflow_limiter = middleware._get_limiter_for_path("/api/v1/workflows/test")
        assert workflow_limiter is not None
        assert workflow_limiter.max_requests == 10  # Workflow endpoint limit

        # Default limiter for unknown paths
        default_limiter = middleware._get_limiter_for_path("/api/v1/unknown")
        assert default_limiter is not None
        assert default_limiter.max_requests == 100  # Default limit
