"""
Unit tests for correlation ID middleware and utilities.

Tests:
- Correlation ID generation
- Client-provided correlation ID handling
- Context propagation
- Validation logic
- Header injection
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware.correlation_id import (
    CorrelationIdMiddleware,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    get_correlation_id_header,
)


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI app with correlation ID middleware."""
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/test")
    async def test_endpoint():
        correlation_id = get_correlation_id()
        return {"correlation_id": correlation_id}

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


class TestCorrelationIdMiddleware:
    """Test cases for CorrelationIdMiddleware."""

    def test_generates_correlation_id_when_not_provided(self, client: TestClient):
        """Test that middleware generates a correlation ID when not provided."""
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers

        # Verify it's a valid UUID
        correlation_id = response.headers["X-Correlation-ID"]
        uuid_obj = uuid.UUID(correlation_id)
        assert str(uuid_obj) == correlation_id

        # Verify it's available in the response body
        data = response.json()
        assert data["correlation_id"] == correlation_id

    def test_accepts_client_provided_correlation_id(self, client: TestClient):
        """Test that middleware accepts client-provided correlation ID."""
        client_correlation_id = str(uuid.uuid4())

        response = client.get("/test", headers={"X-Correlation-ID": client_correlation_id})

        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == client_correlation_id

        data = response.json()
        assert data["correlation_id"] == client_correlation_id

    def test_validates_correlation_id_format(self, client: TestClient):
        """Test that middleware validates correlation ID format."""
        # Invalid correlation ID (too long)
        invalid_id = "x" * 200

        response = client.get("/test", headers={"X-Correlation-ID": invalid_id})

        assert response.status_code == 200
        # Should generate new ID instead of using invalid one
        correlation_id = response.headers["X-Correlation-ID"]
        assert correlation_id != invalid_id
        assert len(correlation_id) < 128

        # Verify it's a valid UUID
        uuid_obj = uuid.UUID(correlation_id)
        assert str(uuid_obj) == correlation_id

    def test_accepts_alphanumeric_correlation_id(self, client: TestClient):
        """Test that middleware accepts alphanumeric correlation IDs."""
        custom_id = "request-12345-abcde"

        response = client.get("/test", headers={"X-Correlation-ID": custom_id})

        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == custom_id

        data = response.json()
        assert data["correlation_id"] == custom_id

    def test_rejects_empty_correlation_id(self, client: TestClient):
        """Test that middleware rejects empty correlation ID."""
        response = client.get("/test", headers={"X-Correlation-ID": ""})

        assert response.status_code == 200
        correlation_id = response.headers["X-Correlation-ID"]
        assert correlation_id != ""

        # Should generate new ID
        uuid_obj = uuid.UUID(correlation_id)
        assert str(uuid_obj) == correlation_id

    def test_rejects_correlation_id_with_special_characters(self, client: TestClient):
        """Test that middleware rejects correlation IDs with special characters."""
        invalid_id = "test<script>alert('xss')</script>"

        response = client.get("/test", headers={"X-Correlation-ID": invalid_id})

        assert response.status_code == 200
        correlation_id = response.headers["X-Correlation-ID"]
        assert correlation_id != invalid_id

        # Should generate new ID
        uuid_obj = uuid.UUID(correlation_id)
        assert str(uuid_obj) == correlation_id

    def test_context_propagation(self, client: TestClient):
        """Test that correlation ID is available throughout request context."""
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        data = response.json()
        assert data["correlation_id"] == response.headers["X-Correlation-ID"]


class TestCorrelationIdUtilities:
    """Test cases for correlation ID utility functions."""

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = str(uuid.uuid4())

        set_correlation_id(test_id)
        assert get_correlation_id() == test_id

        clear_correlation_id()
        assert get_correlation_id() is None

    def test_clear_correlation_id(self):
        """Test clearing correlation ID."""
        test_id = str(uuid.uuid4())

        set_correlation_id(test_id)
        assert get_correlation_id() == test_id

        clear_correlation_id()
        assert get_correlation_id() is None

    def test_get_correlation_id_when_not_set(self):
        """Test getting correlation ID when not set."""
        clear_correlation_id()
        assert get_correlation_id() is None

    def test_get_correlation_id_header(self):
        """Test getting correlation ID as headers dict."""
        test_id = str(uuid.uuid4())

        set_correlation_id(test_id)
        headers = get_correlation_id_header()

        assert headers == {"X-Correlation-ID": test_id}

        clear_correlation_id()

    def test_get_correlation_id_header_when_not_set(self):
        """Test getting correlation ID header when not set."""
        clear_correlation_id()
        headers = get_correlation_id_header()

        assert headers == {}


class TestCorrelationIdValidation:
    """Test cases for correlation ID validation logic."""

    def test_valid_uuid_correlation_id(self, client: TestClient):
        """Test that valid UUID correlation IDs are accepted."""
        valid_uuid = str(uuid.uuid4())

        response = client.get("/test", headers={"X-Correlation-ID": valid_uuid})

        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == valid_uuid

    def test_valid_alphanumeric_correlation_id(self, client: TestClient):
        """Test that valid alphanumeric correlation IDs are accepted."""
        valid_id = "abc123-def456-ghi789"

        response = client.get("/test", headers={"X-Correlation-ID": valid_id})

        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == valid_id

    def test_max_length_correlation_id(self, client: TestClient):
        """Test correlation ID max length validation."""
        # Just under max length (128 characters)
        valid_long_id = "a" * 127

        response = client.get("/test", headers={"X-Correlation-ID": valid_long_id})

        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == valid_long_id

        # Over max length
        invalid_long_id = "a" * 129

        response = client.get("/test", headers={"X-Correlation-ID": invalid_long_id})

        assert response.status_code == 200
        correlation_id = response.headers["X-Correlation-ID"]
        assert correlation_id != invalid_long_id
        assert len(correlation_id) < 128


class TestCorrelationIdIntegration:
    """Integration tests for correlation ID middleware."""

    def test_correlation_id_in_multiple_requests(self, client: TestClient):
        """Test that different requests get different correlation IDs."""
        response1 = client.get("/test")
        response2 = client.get("/test")

        correlation_id1 = response1.headers["X-Correlation-ID"]
        correlation_id2 = response2.headers["X-Correlation-ID"]

        assert correlation_id1 != correlation_id2

    def test_correlation_id_cleanup_between_requests(self, client: TestClient):
        """Test that correlation ID is cleaned up between requests."""
        # First request
        response1 = client.get("/test")
        correlation_id1 = response1.headers["X-Correlation-ID"]

        # Second request should have different ID
        response2 = client.get("/test")
        correlation_id2 = response2.headers["X-Correlation-ID"]

        assert correlation_id1 != correlation_id2

    def test_error_handling_preserves_correlation_id(self, client: TestClient):
        """Test that correlation ID is preserved even when errors occur."""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/error")
        async def error_endpoint():
            correlation_id = get_correlation_id()
            # Store correlation ID before raising error
            raise ValueError("Test error")

        client_error = TestClient(app, raise_server_exceptions=False)
        response = client_error.get("/error")

        # Should still have correlation ID in response
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"]


@pytest.mark.asyncio
async def test_async_context_safety():
    """Test that correlation ID is safe in async context."""
    import asyncio

    async def task_with_correlation_id(task_id: str):
        """Simulate async task with correlation ID."""
        set_correlation_id(f"task-{task_id}")
        await asyncio.sleep(0.01)  # Simulate async work
        return get_correlation_id()

    # Run multiple tasks concurrently
    results = await asyncio.gather(
        task_with_correlation_id("1"),
        task_with_correlation_id("2"),
        task_with_correlation_id("3"),
    )

    # Each task should have its own correlation ID preserved
    assert "task-1" in results
    assert "task-2" in results
    assert "task-3" in results
    assert len(set(results)) == 3  # All unique
