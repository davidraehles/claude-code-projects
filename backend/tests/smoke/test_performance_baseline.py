"""
Smoke tests for basic performance validation.

Ensures that deployed application meets basic performance requirements.
"""

import time
from typing import List

import pytest
from httpx import Client


@pytest.mark.smoke
@pytest.mark.slow
class TestPerformanceBaseline:
    """Test suite for basic performance validation."""

    def test_health_endpoint_response_time(self, client: Client) -> None:
        """
        Test that health endpoint responds within acceptable time.

        Args:
            client: HTTP client fixture
        """
        times: List[float] = []

        # Run 5 requests to get average
        for _ in range(5):
            start = time.time()
            response = client.get("/health")
            elapsed = time.time() - start

            assert response.status_code == 200
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert avg_time < 1.0, (
            f"Average health check time {avg_time:.2f}s exceeds 1.0s threshold"
        )
        assert max_time < 2.0, (
            f"Max health check time {max_time:.2f}s exceeds 2.0s threshold"
        )

    def test_api_docs_response_time(self, client: Client) -> None:
        """
        Test that API docs load within acceptable time.

        Args:
            client: HTTP client fixture
        """
        start = time.time()
        response = client.get("/docs")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 3.0, (
            f"API docs load time {elapsed:.2f}s exceeds 3.0s threshold"
        )

    def test_concurrent_health_checks(self, client: Client) -> None:
        """
        Test that multiple concurrent requests don't cause issues.

        Args:
            client: HTTP client fixture
        """
        import concurrent.futures

        def make_request() -> int:
            response = client.get("/health")
            return response.status_code

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(status == 200 for status in results), (
            f"Some concurrent requests failed: {results}"
        )

    def test_api_response_size_reasonable(self, client: Client) -> None:
        """
        Test that API responses are not excessively large.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/health")

        assert response.status_code == 200

        content_length = len(response.content)
        assert content_length < 100_000, (  # 100KB limit for health endpoint
            f"Health endpoint response size {content_length} bytes exceeds 100KB"
        )

    def test_openapi_schema_size_reasonable(self, client: Client) -> None:
        """
        Test that OpenAPI schema is not excessively large.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/openapi.json")

        assert response.status_code == 200

        content_length = len(response.content)
        assert content_length < 5_000_000, (  # 5MB limit for OpenAPI schema
            f"OpenAPI schema size {content_length} bytes exceeds 5MB"
        )


@pytest.mark.smoke
class TestMemoryAndResourceUsage:
    """Test suite for basic resource usage validation."""

    def test_no_memory_leaks_in_health_checks(self, client: Client) -> None:
        """
        Test that repeated health checks don't indicate memory leaks.

        Args:
            client: HTTP client fixture
        """
        # Make many requests to check for memory leaks
        response_times: List[float] = []

        for _ in range(50):
            start = time.time()
            response = client.get("/health")
            elapsed = time.time() - start

            assert response.status_code == 200
            response_times.append(elapsed)

        # Check that response times don't increase significantly
        first_ten_avg = sum(response_times[:10]) / 10
        last_ten_avg = sum(response_times[-10:]) / 10

        # Last 10 shouldn't be more than 2x slower than first 10
        assert last_ten_avg < first_ten_avg * 2, (
            f"Response time degradation detected: "
            f"first 10 avg={first_ten_avg:.3f}s, "
            f"last 10 avg={last_ten_avg:.3f}s"
        )

    def test_graceful_handling_of_rapid_requests(self, client: Client) -> None:
        """
        Test that service handles rapid sequential requests gracefully.

        Args:
            client: HTTP client fixture
        """
        # Make 20 rapid sequential requests
        for i in range(20):
            response = client.get("/health")
            assert response.status_code in [200, 429], (  # 429 = rate limited
                f"Request {i} failed with status {response.status_code}"
            )
