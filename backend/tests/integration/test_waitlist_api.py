"""
Integration tests for waitlist API endpoints.

Tests the waitlist endpoints (signup, verification, status check) with database persistence.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.api.dependencies import get_database
from app.models.waitlist import WaitlistEntry


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_waitlist.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_database():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def setup_test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(setup_test_db):
    """Create test client with overridden database."""
    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestWaitlistSignup:
    """Test waitlist signup endpoint."""

    def test_join_waitlist_success(self, client):
        """Test successful waitlist signup."""
        response = client.post(
            "/api/v1/waitlist",
            json={
                "email": "test@example.com",
                "metadata": {"source": "hero"}
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["status"] == "PENDING"
        assert data["position"] == 1
        assert "id" in data
        assert "created_at" in data

    def test_join_waitlist_duplicate_email(self, client):
        """Test that duplicate email is rejected."""
        # First signup
        client.post(
            "/api/v1/waitlist",
            json={
                "email": "test@example.com",
                "metadata": {"source": "hero"}
            }
        )
        # Duplicate signup
        response = client.post(
            "/api/v1/waitlist",
            json={
                "email": "test@example.com",
                "metadata": {"source": "hero"}
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_join_waitlist_invalid_email(self, client):
        """Test that invalid email is rejected."""
        response = client.post(
            "/api/v1/waitlist",
            json={
                "email": "invalid-email",
                "metadata": {"source": "hero"}
            }
        )
        assert response.status_code == 422

    def test_join_waitlist_missing_email(self, client):
        """Test that missing email is rejected."""
        response = client.post(
            "/api/v1/waitlist",
            json={"metadata": {"source": "hero"}}
        )
        assert response.status_code == 422

    def test_join_waitlist_position_ordering(self, client):
        """Test that queue position is calculated correctly."""
        # Add three users to the waitlist
        response1 = client.post(
            "/api/v1/waitlist",
            json={"email": "user1@example.com", "metadata": {"source": "hero"}}
        )
        assert response1.json()["position"] == 1

        response2 = client.post(
            "/api/v1/waitlist",
            json={"email": "user2@example.com", "metadata": {"source": "hero"}}
        )
        assert response2.json()["position"] == 2

        response3 = client.post(
            "/api/v1/waitlist",
            json={"email": "user3@example.com", "metadata": {"source": "hero"}}
        )
        assert response3.json()["position"] == 3


class TestWaitlistVerification:
    """Test email verification endpoint."""

    def test_verify_email_success(self, client):
        """Test successful email verification."""
        # Create waitlist entry
        signup_response = client.post(
            "/api/v1/waitlist",
            json={"email": "test@example.com", "metadata": {"source": "hero"}}
        )
        token = signup_response.json()["id"]  # In real scenario, token is sent in email

        # Get the actual token from database
        db = TestingSessionLocal()
        entry = db.query(WaitlistEntry).filter(
            WaitlistEntry.email == "test@example.com"
        ).first()
        actual_token = entry.verification_token
        db.close()

        # Verify email
        verify_response = client.post(
            "/api/v1/waitlist/verify",
            json={"token": actual_token}
        )
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["status"] == "VERIFIED"
        assert data["verified_at"] is not None

    def test_verify_email_invalid_token(self, client):
        """Test verification with invalid token."""
        response = client.post(
            "/api/v1/waitlist/verify",
            json={"token": "invalid-token-12345"}
        )
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]

    def test_verify_email_already_verified(self, client):
        """Test that already verified email cannot be verified again."""
        # Create and verify entry
        signup_response = client.post(
            "/api/v1/waitlist",
            json={"email": "test@example.com", "metadata": {"source": "hero"}}
        )

        db = TestingSessionLocal()
        entry = db.query(WaitlistEntry).filter(
            WaitlistEntry.email == "test@example.com"
        ).first()
        token = entry.verification_token
        db.close()

        # First verification
        client.post(
            "/api/v1/waitlist/verify",
            json={"token": token}
        )

        # Try to verify again with same token
        # After first verification, token is cleared for security
        # So second attempt returns generic error (prevents email enumeration)
        response = client.post(
            "/api/v1/waitlist/verify",
            json={"token": token}
        )
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]


class TestWaitlistStatus:
    """Test status check endpoint."""

    def test_get_status_pending(self, client):
        """Test getting status of pending entry."""
        client.post(
            "/api/v1/waitlist",
            json={"email": "test@example.com", "metadata": {"source": "hero"}}
        )
        response = client.get(
            "/api/v1/waitlist/status",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["status"] == "PENDING"

    def test_get_status_verified(self, client):
        """Test getting status of verified entry."""
        # Create entry
        client.post(
            "/api/v1/waitlist",
            json={"email": "test@example.com", "metadata": {"source": "hero"}}
        )

        # Get verification token
        db = TestingSessionLocal()
        entry = db.query(WaitlistEntry).filter(
            WaitlistEntry.email == "test@example.com"
        ).first()
        token = entry.verification_token
        db.close()

        # Verify
        client.post(
            "/api/v1/waitlist/verify",
            json={"token": token}
        )

        # Check status
        response = client.get(
            "/api/v1/waitlist/status",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "VERIFIED"

    def test_get_status_not_found(self, client):
        """Test getting status of non-existent entry."""
        response = client.get(
            "/api/v1/waitlist/status",
            params={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_status_invalid_email(self, client):
        """Test getting status with invalid email format."""
        response = client.get(
            "/api/v1/waitlist/status",
            params={"email": "invalid-email"}
        )
        assert response.status_code == 422
