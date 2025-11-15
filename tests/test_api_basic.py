"""
Basic API smoke tests.

Tests that the FastAPI application starts and basic endpoints work.
"""

import pytest
from fastapi.testclient import TestClient


def test_app_imports():
    """Test that the app can be imported."""
    from app.main import app
    assert app is not None


def test_health_endpoint():
    """Test health check endpoint without database."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


def test_root_endpoint():
    """Test root endpoint without database."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"


def test_api_docs_available():
    """Test that API documentation is available."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/docs")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
