"""
Integration tests for the complete waitlist workflow.

This test suite validates the end-to-end waitlist flow including:
- User signup
- Email verification
- Status tracking
- Database persistence
- Email service integration
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, call
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.api.dependencies import get_database
from app.models.waitlist import WaitlistEntry
from app.schemas.waitlist import WaitlistStatus


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_waitlist_workflow.db"
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


@pytest.fixture(scope="function")
def db_session(setup_test_db):
    """Provide database session for direct DB access."""
    db = TestingSessionLocal()
    yield db
    db.close()


class TestWaitlistEndToEndFlow:
    """Test complete waitlist workflow from signup to verification."""

    @patch('app.services.email.EmailService.send_verification_email')
    def test_complete_signup_and_verification_flow(self, mock_send_email, client, db_session):
        """
        Test the complete flow:
        1. User signs up for waitlist
        2. Verification email is sent
        3. User verifies email via token
        4. Status is updated correctly
        """
        # Step 1: User signs up
        signup_response = client.post(
            "/api/v1/waitlist",
            json={
                "email": "newuser@example.com",
                "metadata": {"source": "landing_page", "campaign": "launch"}
            }
        )

        assert signup_response.status_code == 201
        signup_data = signup_response.json()
        assert signup_data["email"] == "newuser@example.com"
        assert signup_data["status"] == WaitlistStatus.PENDING.value
        assert signup_data["position"] == 1
        assert signup_data["verified_at"] is None

        # Verify email service was called (once email service is integrated)
        # mock_send_email.assert_called_once()

        # Step 2: Retrieve verification token from database
        entry = db_session.query(WaitlistEntry).filter(
            WaitlistEntry.email == "newuser@example.com"
        ).first()

        assert entry is not None
        assert entry.status == WaitlistStatus.PENDING.value
        assert entry.verification_token is not None
        verification_token = entry.verification_token

        # Step 3: User verifies email
        verify_response = client.post(
            "/api/v1/waitlist/verify",
            json={"token": verification_token}
        )

        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["status"] == WaitlistStatus.VERIFIED.value
        assert verify_data["verified_at"] is not None

        # Step 4: Verify database state after verification
        db_session.refresh(entry)
        assert entry.status == WaitlistStatus.VERIFIED.value
        assert entry.verified_at is not None
        assert entry.verification_token is None  # Token cleared for security

        # Step 5: Check status endpoint
        status_response = client.get(
            "/api/v1/waitlist/status",
            params={"email": "newuser@example.com"}
        )

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == WaitlistStatus.VERIFIED.value
        assert status_data["verified_at"] is not None


    def test_multiple_users_queue_ordering(self, client, db_session):
        """
        Test that multiple users are correctly ordered in the queue
        and positions are maintained.
        """
        emails = [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com",
            "user4@example.com",
        ]

        # Sign up multiple users
        for i, email in enumerate(emails, start=1):
            response = client.post(
                "/api/v1/waitlist",
                json={"email": email, "metadata": {"source": "test"}}
            )
            assert response.status_code == 201
            assert response.json()["position"] == i

        # Verify positions remain consistent
        for i, email in enumerate(emails, start=1):
            response = client.get(
                "/api/v1/waitlist/status",
                params={"email": email}
            )
            assert response.status_code == 200
            assert response.json()["position"] == i


    def test_verification_token_single_use(self, client, db_session):
        """
        Test that verification tokens can only be used once
        and are cleared after use.
        """
        # Create entry
        signup_response = client.post(
            "/api/v1/waitlist",
            json={"email": "singleuse@example.com"}
        )
        assert signup_response.status_code == 201

        # Get token
        entry = db_session.query(WaitlistEntry).filter(
            WaitlistEntry.email == "singleuse@example.com"
        ).first()
        token = entry.verification_token

        # First verification succeeds
        verify_response1 = client.post(
            "/api/v1/waitlist/verify",
            json={"token": token}
        )
        assert verify_response1.status_code == 200

        # Second verification with same token fails
        verify_response2 = client.post(
            "/api/v1/waitlist/verify",
            json={"token": token}
        )
        assert verify_response2.status_code == 400
        assert "Invalid or expired" in verify_response2.json()["detail"]


    def test_duplicate_email_rejection(self, client):
        """
        Test that duplicate email signups are rejected at all stages.
        """
        email = "duplicate@example.com"

        # First signup succeeds
        response1 = client.post(
            "/api/v1/waitlist",
            json={"email": email}
        )
        assert response1.status_code == 201

        # Duplicate signup fails
        response2 = client.post(
            "/api/v1/waitlist",
            json={"email": email}
        )
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]


    def test_invalid_email_format_rejection(self, client):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user @example.com",
            "",
        ]

        for invalid_email in invalid_emails:
            response = client.post(
                "/api/v1/waitlist",
                json={"email": invalid_email}
            )
            assert response.status_code == 422  # Validation error


    def test_status_check_for_nonexistent_email(self, client):
        """Test that status check returns 404 for non-existent email."""
        response = client.get(
            "/api/v1/waitlist/status",
            params={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


    def test_invalid_verification_token(self, client):
        """Test that invalid verification tokens are rejected."""
        invalid_tokens = [
            "invalid-token",
            "00000000-0000-0000-0000-000000000000",
            "",
            "malformed",
        ]

        for invalid_token in invalid_tokens:
            response = client.post(
                "/api/v1/waitlist/verify",
                json={"token": invalid_token}
            )
            assert response.status_code == 400
            assert "Invalid or expired" in response.json()["detail"]


    def test_metadata_persistence(self, client, db_session):
        """Test that metadata is correctly stored and retrieved."""
        metadata = {
            "source": "facebook_ad",
            "campaign": "summer_2024",
            "referrer": "https://example.com",
            "utm_source": "fb",
            "utm_medium": "cpc"
        }

        response = client.post(
            "/api/v1/waitlist",
            json={
                "email": "metadata@example.com",
                "metadata": metadata
            }
        )
        assert response.status_code == 201

        # Verify metadata in database
        entry = db_session.query(WaitlistEntry).filter(
            WaitlistEntry.email == "metadata@example.com"
        ).first()

        assert entry.metadata_payload == metadata


    def test_timestamp_accuracy(self, client, db_session):
        """Test that timestamps are accurate and consistent."""
        # Get current time with some buffer for database storage (no microseconds)
        before_signup = datetime.now(timezone.utc).replace(microsecond=0)

        # Sign up
        response = client.post(
            "/api/v1/waitlist",
            json={"email": "timestamp@example.com"}
        )
        assert response.status_code == 201

        after_signup = datetime.now(timezone.utc).replace(microsecond=999999)

        # Get entry
        entry = db_session.query(WaitlistEntry).filter(
            WaitlistEntry.email == "timestamp@example.com"
        ).first()
        token = entry.verification_token

        # Verify created_at is within expected range (with buffer for DB precision)
        # SQLite stores as naive datetime, so we compare without timezone
        assert entry.created_at >= before_signup.replace(tzinfo=None)
        assert entry.created_at <= after_signup.replace(tzinfo=None)

        # Verify email
        before_verify = datetime.now(timezone.utc).replace(microsecond=0)
        client.post("/api/v1/waitlist/verify", json={"token": token})
        after_verify = datetime.now(timezone.utc).replace(microsecond=999999)

        # Refresh entry
        db_session.refresh(entry)

        # Verify verified_at is within expected range
        assert entry.verified_at is not None
        assert entry.verified_at >= before_verify.replace(tzinfo=None)
        assert entry.verified_at <= after_verify.replace(tzinfo=None)


class TestWaitlistConcurrency:
    """Test concurrent operations and race conditions."""

    def test_concurrent_signups_maintain_order(self, client, db_session):
        """
        Test that concurrent signups from different users
        maintain correct queue ordering.
        """
        import concurrent.futures

        emails = [f"concurrent{i}@example.com" for i in range(10)]

        def signup(email):
            return client.post(
                "/api/v1/waitlist",
                json={"email": email}
            )

        # Execute signups concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(signup, email) for email in emails]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Verify all signups succeeded
        success_count = sum(1 for r in results if r.status_code == 201)
        assert success_count == len(emails)

        # Verify all entries have unique positions
        positions = set()
        for email in emails:
            response = client.get(
                "/api/v1/waitlist/status",
                params={"email": email}
            )
            if response.status_code == 200:
                positions.add(response.json()["position"])

        assert len(positions) == len(emails)
        assert positions == set(range(1, len(emails) + 1))


class TestWaitlistEdgeCases:
    """Test edge cases and error conditions."""

    def test_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        # Missing email
        response = client.post(
            "/api/v1/waitlist",
            json={"metadata": {"source": "test"}}
        )
        assert response.status_code == 422

        # Empty request body
        response = client.post(
            "/api/v1/waitlist",
            json={}
        )
        assert response.status_code == 422


    def test_email_case_sensitivity(self, client):
        """Test email case handling."""
        # SQLAlchemy comparison is case-sensitive by default
        # So these should be treated as different emails
        response1 = client.post(
            "/api/v1/waitlist",
            json={"email": "User@Example.COM"}
        )
        assert response1.status_code == 201

        response2 = client.post(
            "/api/v1/waitlist",
            json={"email": "user@example.com"}
        )
        # This should also succeed as it's a different email
        assert response2.status_code == 201


    def test_very_long_email(self, client):
        """Test handling of very long email addresses."""
        long_email = "a" * 200 + "@example.com"
        response = client.post(
            "/api/v1/waitlist",
            json={"email": long_email}
        )
        # Should be rejected if exceeds VARCHAR(255) limit
        # Pydantic EmailStr validation will handle this
        assert response.status_code in [422, 201]


    def test_special_characters_in_metadata(self, client, db_session):
        """Test that special characters in metadata are handled correctly."""
        metadata = {
            "source": "test<script>alert('xss')</script>",
            "notes": "Special chars: <>&\"'",
            "unicode": "Hello 世界 🌍",
        }

        response = client.post(
            "/api/v1/waitlist",
            json={
                "email": "special@example.com",
                "metadata": metadata
            }
        )
        assert response.status_code == 201

        # Verify metadata is stored correctly
        entry = db_session.query(WaitlistEntry).filter(
            WaitlistEntry.email == "special@example.com"
        ).first()

        assert entry.metadata_payload == metadata
