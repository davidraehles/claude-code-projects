"""
Smoke tests for health check endpoints.

Validates that health, liveness, and readiness endpoints are accessible
and returning expected responses.
"""

import pytest
from httpx import Client


@pytest.mark.smoke
@pytest.mark.health_check
class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_health_endpoint_accessible(self, client: Client) -> None:
        """
        Test that the /health endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200, (
            f"Health endpoint returned {response.status_code}, "
            f"expected 200. Response: {response.text}"
        )

    def test_health_endpoint_returns_json(self, client: Client) -> None:
        """
        Test that the /health endpoint returns valid JSON.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "status" in data, "Health response missing 'status' field"
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in data, "Health response missing 'timestamp' field"
        assert "service" in data, "Health response missing 'service' field"
        assert "components" in data, "Health response missing 'components' field"

    def test_health_includes_database_status(self, client: Client) -> None:
        """
        Test that health check includes database component.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")
        data = response.json()

        assert "components" in data
        assert "database" in data["components"], "Database component missing from health check"

        db_health = data["components"]["database"]
        assert "status" in db_health
        assert "message" in db_health
        assert "latency_ms" in db_health

    def test_health_includes_redis_status(self, client: Client) -> None:
        """
        Test that health check includes Redis component.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")
        data = response.json()

        assert "components" in data
        assert "redis" in data["components"], "Redis component missing from health check"

        redis_health = data["components"]["redis"]
        assert "status" in redis_health
        assert "message" in redis_health

    def test_liveness_endpoint(self, client: Client) -> None:
        """
        Test that the /health/liveness endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health/liveness")

        assert response.status_code == 200, (
            f"Liveness endpoint returned {response.status_code}, "
            f"expected 200"
        )

        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_endpoint(self, client: Client) -> None:
        """
        Test that the /health/readiness endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health/readiness")

        assert response.status_code == 200, (
            f"Readiness endpoint returned {response.status_code}, "
            f"expected 200"
        )

        data = response.json()
        assert "status" in data
        assert "components" in data

    def test_health_response_time(self, client: Client) -> None:
        """
        Test that health endpoint responds within acceptable time.

        Args:
            client: HTTP client fixture
        """
        import time

        start_time = time.time()
        response = client.get("/health")
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 5.0, (
            f"Health endpoint took {elapsed_time:.2f}s to respond, "
            f"expected < 5.0s"
        )
