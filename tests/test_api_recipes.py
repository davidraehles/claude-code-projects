"""
Integration tests for Recipe API endpoints.

Tests the FastAPI recipe endpoints including harvest, list, get, update, and delete.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.recipe import Recipe
from app.agents.recipe_harvester import RecipeScrapeResult
from datetime import datetime


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user_id():
    """Override auth dependency to return test user ID."""
    return 1


# Override dependencies
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create test client."""
    from app.api.dependencies import get_current_user_id
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
        country="DE"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_recipe(test_db, test_user):
    """Create a test recipe."""
    db = TestingSessionLocal()
    recipe = Recipe(
        user_id=test_user.id,
        title="Test Pasta Carbonara",
        ingredients=["400g spaghetti", "200g pancetta", "4 eggs"],
        instructions="Cook pasta. Fry pancetta. Mix with eggs.",
        prep_time=10,
        cook_time=20,
        servings=4,
        source_url="https://example.com/pasta",
        source_type="html"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    db.close()
    return recipe


class TestRecipeAPI:
    """Test suite for Recipe API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

    def test_list_recipes_empty(self, client, test_user):
        """Test listing recipes when none exist."""
        response = client.get("/api/v1/recipes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_list_recipes_with_data(self, client, test_recipe):
        """Test listing recipes with existing data."""
        response = client.get("/api/v1/recipes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test Pasta Carbonara"
        assert data["items"][0]["id"] == test_recipe.id

    def test_list_recipes_pagination(self, client, test_user):
        """Test recipe pagination."""
        # Create multiple recipes
        db = TestingSessionLocal()
        for i in range(15):
            recipe = Recipe(
                user_id=test_user.id,
                title=f"Recipe {i}",
                ingredients=["ingredient"],
                instructions="instructions",
                source_url=f"https://example.com/recipe-{i}",
                source_type="html"
            )
            db.add(recipe)
        db.commit()
        db.close()

        # Test first page
        response = client.get("/api/v1/recipes?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10

        # Test second page
        response = client.get("/api/v1/recipes?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 5

    def test_get_recipe_by_id(self, client, test_recipe):
        """Test getting a specific recipe by ID."""
        response = client.get(f"/api/v1/recipes/{test_recipe.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_recipe.id
        assert data["title"] == "Test Pasta Carbonara"
        assert len(data["ingredients"]) == 3

    def test_get_recipe_not_found(self, client, test_user):
        """Test getting a non-existent recipe."""
        response = client.get("/api/v1/recipes/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_recipe(self, client, test_recipe):
        """Test deleting a recipe."""
        response = client.delete(f"/api/v1/recipes/{test_recipe.id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/v1/recipes/{test_recipe.id}")
        assert response.status_code == 404

    def test_update_recipe(self, client, test_recipe):
        """Test updating a recipe."""
        update_data = {
            "title": "Updated Pasta Carbonara",
            "servings": 6
        }
        response = client.put(
            f"/api/v1/recipes/{test_recipe.id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Pasta Carbonara"
        assert data["servings"] == 6
        assert data["cook_time"] == 20  # Unchanged field

    @patch('app.api.v1.recipes.HTMLRecipeScraper')
    @patch('app.api.v1.recipes.get_event_bus')
    def test_harvest_recipe_success(self, mock_event_bus, mock_scraper_class, client, test_user):
        """Test successful recipe harvesting."""
        # Mock event bus
        mock_bus = MagicMock()
        mock_bus.publish = AsyncMock()
        mock_event_bus.return_value = mock_bus

        # Mock scraper
        mock_scraper = MagicMock()
        mock_scraper.close = AsyncMock()

        # Create mock async generator for scraper results
        async def mock_scrape_results():
            yield RecipeScrapeResult(
                title="Harvested Pasta",
                ingredients=["pasta", "eggs"],
                instructions="Cook and serve",
                prep_time=5,
                cook_time=10,
                servings=2,
                source_url="https://example.com/new-pasta",
                source_type="html"
            )

        mock_scraper.scrape = MagicMock(return_value=mock_scrape_results())
        mock_scraper_class.return_value = mock_scraper

        # Make request
        request_data = {
            "url": "https://example.com/new-pasta",
            "source_type": "html"
        }
        response = client.post("/api/v1/recipes/harvest", json=request_data)

        # Check response
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert data["success"] is True
        assert "queued" in data["message"].lower()

    def test_harvest_recipe_invalid_url(self, client, test_user):
        """Test harvesting with invalid URL."""
        request_data = {
            "url": "",  # Empty URL
            "source_type": "html"
        }
        response = client.post("/api/v1/recipes/harvest", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_filter_by_source_type(self, client, test_user):
        """Test filtering recipes by source type."""
        db = TestingSessionLocal()

        # Create recipes with different source types
        recipe1 = Recipe(
            user_id=test_user.id,
            title="HTML Recipe",
            ingredients=["a"],
            instructions="test",
            source_url="https://example.com/1",
            source_type="html"
        )
        recipe2 = Recipe(
            user_id=test_user.id,
            title="API Recipe",
            ingredients=["b"],
            instructions="test",
            source_url="https://example.com/2",
            source_type="api"
        )
        db.add_all([recipe1, recipe2])
        db.commit()
        db.close()

        # Filter by HTML
        response = client.get("/api/v1/recipes?source_type=html")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["source_type"] == "html"

        # Filter by API
        response = client.get("/api/v1/recipes?source_type=api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["source_type"] == "api"

    def test_duplicate_detection(self, client, test_recipe):
        """Test duplicate recipe detection."""
        # Try to get the existing recipe
        response = client.get("/api/v1/recipes")
        assert response.status_code == 200
        initial_count = response.json()["total"]

        # The duplicate detection happens in the background task
        # This test verifies the API accepts the request
        request_data = {
            "url": test_recipe.source_url,  # Same URL as existing recipe
            "source_type": "html"
        }
        response = client.post("/api/v1/recipes/harvest", json=request_data)
        assert response.status_code == 202  # Accepted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
