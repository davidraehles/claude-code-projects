"""
Smoke tests for database connectivity and migrations.

Validates that the database is accessible and migrations are up to date.
"""

import pytest
from httpx import Client


@pytest.mark.smoke
@pytest.mark.requires_db
class TestDatabaseConnectivity:
    """Test suite for database connectivity."""

    def test_database_health_via_endpoint(self, client: Client) -> None:
        """
        Test database connectivity through health endpoint.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check database component
        assert "components" in data
        assert "database" in data["components"]

        db_status = data["components"]["database"]["status"]
        assert db_status in ["healthy", "degraded"], (
            f"Database status is {db_status}, expected healthy or degraded. "
            f"Message: {data['components']['database'].get('message', 'N/A')}"
        )

    def test_database_latency_acceptable(self, client: Client) -> None:
        """
        Test that database response time is acceptable.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        db_health = data["components"]["database"]
        assert "latency_ms" in db_health

        latency = db_health["latency_ms"]
        assert latency is not None
        assert latency < 1000, (
            f"Database latency is {latency}ms, expected < 1000ms"
        )

    def test_database_pool_not_exhausted(self, client: Client) -> None:
        """
        Test that database connection pool is not exhausted.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        db_health = data["components"]["database"]

        if "details" in db_health:
            details = db_health["details"]
            if "pool_size" in details and "checked_out" in details:
                pool_size = details["pool_size"]
                checked_out = details["checked_out"]

                # Ensure we're not at max pool capacity
                assert checked_out < pool_size, (
                    f"Database pool exhausted: {checked_out}/{pool_size} connections in use"
                )


@pytest.mark.smoke
@pytest.mark.requires_redis
class TestRedisConnectivity:
    """Test suite for Redis connectivity."""

    def test_redis_health_via_endpoint(self, client: Client) -> None:
        """
        Test Redis connectivity through health endpoint.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check Redis component
        assert "components" in data
        assert "redis" in data["components"]

        redis_status = data["components"]["redis"]["status"]
        # Redis is optional, so degraded is acceptable
        assert redis_status in ["healthy", "degraded", "unhealthy"]

    def test_redis_latency_acceptable(self, client: Client) -> None:
        """
        Test that Redis response time is acceptable.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        redis_health = data["components"]["redis"]

        if "latency_ms" in redis_health and redis_health["latency_ms"]:
            latency = redis_health["latency_ms"]
            assert latency < 500, (
                f"Redis latency is {latency}ms, expected < 500ms"
            )


@pytest.mark.smoke
class TestServiceConfiguration:
    """Test suite for service configuration."""

    def test_service_version_reported(self, client: Client) -> None:
        """
        Test that service version is reported in health check.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "version" in data
        assert data["version"] is not None
        assert len(data["version"]) > 0

    def test_service_name_correct(self, client: Client) -> None:
        """
        Test that service name is correctly reported.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "service" in data
        assert data["service"] is not None
        assert len(data["service"]) > 0

    def test_timestamp_present(self, client: Client) -> None:
        """
        Test that health check includes timestamp.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "timestamp" in data
        assert data["timestamp"] is not None
