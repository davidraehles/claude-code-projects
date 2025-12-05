"""
Integration tests for authentication endpoints with rate limiting.

Tests the auth endpoints (login, register, refresh) with rate limiting enabled.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

from app.main import app
from app.database import Base
from app.api.dependencies import get_database


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_auth_rate_limit.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_database():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client."""
    return TestClient(app)


class TestRegisterRateLimiting:
    """Test rate limiting on registration endpoint."""

    def test_register_within_rate_limit(self, client):
        """Test that registration requests are allowed within rate limit."""
        # Register limit is 3 per minute per IP
        for i in range(3):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"user{i}@example.com",
                    "password": "testpassword123",
                    "country": "US"
                }
            )
            # First one succeeds, others may fail on email duplicate, but shouldn't be rate limited
            assert response.status_code in [201, 400]

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers

    def test_register_exceeds_rate_limit(self, client):
        """Test that registration requests are blocked when exceeding rate limit."""
        # Make 3 requests (at limit)
        for i in range(3):
            client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"ratelimit{i}@example.com",
                    "password": "testpassword123",
                    "country": "US"
                }
            )

        # 4th request should be rate limited
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "ratelimited@example.com",
                "password": "testpassword123",
                "country": "US"
            }
        )

        assert response.status_code == 429
        assert "Too many registration attempts" in response.json()["error"]

        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert response.headers["X-RateLimit-Remaining"] == "0"


class TestLoginRateLimiting:
    """Test rate limiting on login endpoint."""

    @pytest.fixture(autouse=True)
    def setup_user(self, client):
        """Create a test user before each test."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "correctpassword123",
                "country": "US"
            }
        )

    def test_login_within_rate_limit(self, client):
        """Test that login requests are allowed within rate limit."""
        # Login limit is 5 per minute per IP
        for i in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "logintest@example.com",
                    "password": "correctpassword123"
                }
            )

            # Should succeed
            assert response.status_code == 200

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers

    def test_login_exceeds_rate_limit(self, client):
        """Test that login requests are blocked when exceeding rate limit."""
        # Make 5 requests (at limit)
        for i in range(5):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": "logintest@example.com",
                    "password": "correctpassword123"
                }
            )

        # 6th request should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "correctpassword123"
            }
        )

        assert response.status_code == 429
        assert "Too many login attempts" in response.json()["error"]

    def test_failed_login_tracking(self, client):
        """Test that failed login attempts trigger account lockout."""
        # Make 5 failed login attempts
        for i in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "logintest@example.com",
                    "password": "wrongpassword"
                }
            )
            assert response.status_code == 401

        # 6th attempt should be locked out
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 403
        assert "Account temporarily locked" in response.json()["error"]
        assert "unlock_at" in response.json()

    def test_successful_login_clears_failures(self, client):
        """Test that successful login clears failed attempt counter."""
        # Make 3 failed attempts
        for i in range(3):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": "logintest@example.com",
                    "password": "wrongpassword"
                }
            )

        # Successful login should clear failures
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "correctpassword123"
            }
        )
        assert response.status_code == 200

        # Should be able to make more failed attempts without immediate lockout
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401  # Not locked


class TestRefreshRateLimiting:
    """Test rate limiting on token refresh endpoint."""

    @pytest.fixture
    def user_tokens(self, client):
        """Create a user and get their tokens."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "refreshtest@example.com",
                "password": "testpassword123",
                "country": "US"
            }
        )
        return response.json()

    def test_refresh_within_rate_limit(self, client, user_tokens):
        """Test that refresh requests are allowed within rate limit."""
        refresh_token = user_tokens["refresh_token"]

        # Refresh limit is 10 per minute per user
        for i in range(10):
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )

            assert response.status_code == 200

            # Update token for next iteration
            refresh_token = response.json()["refresh_token"]

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers

    def test_refresh_exceeds_rate_limit(self, client, user_tokens):
        """Test that refresh requests are blocked when exceeding rate limit."""
        refresh_token = user_tokens["refresh_token"]

        # Make 10 requests (at limit)
        for i in range(10):
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            refresh_token = response.json()["refresh_token"]

        # 11th request should be rate limited
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 429
        assert "Too many token refresh attempts" in response.json()["error"]


class TestRateLimitHeaders:
    """Test rate limit response headers."""

    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present in responses."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "headertest@example.com",
                "password": "testpassword123",
                "country": "US"
            }
        )

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_headers_format(self, client):
        """Test that rate limit headers have correct format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "headerformat@example.com",
                "password": "testpassword123",
                "country": "US"
            }
        )

        # Check that values are parseable
        limit = int(response.headers["X-RateLimit-Limit"])
        remaining = int(response.headers["X-RateLimit-Remaining"])
        reset_at = response.headers["X-RateLimit-Reset"]

        assert limit > 0
        assert remaining >= 0
        assert len(reset_at) > 0  # ISO format datetime string

    def test_rate_limit_headers_on_error(self, client):
        """Test that rate limit headers are present even on error responses."""
        # Try to register with duplicate email
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123",
                "country": "US"
            }
        )

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123",
                "country": "US"
            }
        )

        # Should fail with 400
        assert response.status_code == 400

        # But should still have rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
