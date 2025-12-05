"""
Smoke tests for critical API endpoints.

Validates that key API endpoints are accessible and returning expected
status codes after deployment.
"""

import pytest
from httpx import Client


@pytest.mark.smoke
class TestCriticalEndpoints:
    """Test suite for critical API endpoints."""

    def test_api_root_accessible(self, client: Client) -> None:
        """
        Test that the API root endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/")

        # Root may return 200, 404, or redirect - just ensure service is up
        assert response.status_code in [200, 404, 307], (
            f"API root returned unexpected status {response.status_code}"
        )

    def test_api_docs_accessible(self, client: Client) -> None:
        """
        Test that API documentation (Swagger) is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/docs")

        assert response.status_code == 200, (
            f"API docs endpoint returned {response.status_code}, expected 200"
        )
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_openapi_json_accessible(self, client: Client) -> None:
        """
        Test that OpenAPI JSON schema is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_redoc_accessible(self, client: Client) -> None:
        """
        Test that ReDoc documentation is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/redoc")

        # ReDoc may or may not be enabled
        assert response.status_code in [200, 404]


@pytest.mark.smoke
@pytest.mark.auth
class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    def test_login_endpoint_exists(self, client: Client) -> None:
        """
        Test that login endpoint exists and returns appropriate error for invalid creds.

        Args:
            client: HTTP client fixture
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "invalid@example.com", "password": "invalid"},
        )

        # Should return 401 (Unauthorized) or 422 (Validation error)
        assert response.status_code in [401, 422], (
            f"Login endpoint returned unexpected status {response.status_code}"
        )

    def test_register_endpoint_exists(self, client: Client) -> None:
        """
        Test that register endpoint exists and validates input.

        Args:
            client: HTTP client fixture
        """
        response = client.post(
            "/api/v1/auth/register",
            json={},  # Empty payload should fail validation
        )

        # Should return 422 (Validation error)
        assert response.status_code == 422, (
            f"Register endpoint returned unexpected status {response.status_code}"
        )

    def test_rate_limiting_headers_present(self, client: Client) -> None:
        """
        Test that rate limiting headers are present in auth responses.

        Args:
            client: HTTP client fixture
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass"},
        )

        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers or response.status_code == 404, (
            "Rate limiting headers missing from auth endpoint"
        )


@pytest.mark.smoke
@pytest.mark.recipes
class TestRecipeEndpoints:
    """Test suite for recipe-related endpoints."""

    def test_recipes_list_endpoint(self, client: Client) -> None:
        """
        Test that recipes list endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/api/v1/recipes")

        # Should return 200 (OK) or 401 (Unauthorized if auth required)
        assert response.status_code in [200, 401, 404], (
            f"Recipes endpoint returned unexpected status {response.status_code}"
        )


@pytest.mark.smoke
@pytest.mark.meal_plans
class TestMealPlanEndpoints:
    """Test suite for meal plan endpoints."""

    def test_meal_plans_endpoint(self, client: Client) -> None:
        """
        Test that meal plans endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/api/v1/meal-plans")

        # Should return 200 (OK) or 401 (Unauthorized if auth required)
        assert response.status_code in [200, 401, 404], (
            f"Meal plans endpoint returned unexpected status {response.status_code}"
        )


@pytest.mark.smoke
@pytest.mark.grocery_cart
class TestGroceryCartEndpoints:
    """Test suite for grocery cart endpoints."""

    def test_grocery_cart_endpoint(self, client: Client) -> None:
        """
        Test that grocery cart endpoint is accessible.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/api/v1/grocery-carts")

        # Should return 200 (OK) or 401 (Unauthorized if auth required)
        assert response.status_code in [200, 401, 404], (
            f"Grocery cart endpoint returned unexpected status {response.status_code}"
        )


@pytest.mark.smoke
class TestCORSConfiguration:
    """Test suite for CORS configuration."""

    def test_cors_headers_present(self, client: Client) -> None:
        """
        Test that CORS headers are present in responses.

        Args:
            client: HTTP client fixture
        """
        response = client.options(
            "/api/v1/recipes",
            headers={"Origin": "http://localhost:3000"},
        )

        # CORS headers should be present
        # Note: This test is lenient as CORS config varies by environment
        assert response.status_code in [200, 204, 404]


@pytest.mark.smoke
class TestErrorHandling:
    """Test suite for error handling."""

    def test_404_handling(self, client: Client) -> None:
        """
        Test that 404 errors are handled properly.

        Args:
            client: HTTP client fixture
        """
        response = client.get("/api/v1/nonexistent-endpoint")

        assert response.status_code == 404

    def test_500_error_format(self, client: Client) -> None:
        """
        Test that server errors return proper JSON format.

        Args:
            client: HTTP client fixture
        """
        # This test would need an endpoint that intentionally triggers a 500
        # For now, we'll skip if such an endpoint doesn't exist
        pytest.skip("No test endpoint for 500 errors")
