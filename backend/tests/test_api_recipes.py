"""
Integration tests for Recipe API endpoints.

Tests the FastAPI recipe endpoints including harvest, list, get, update, and delete.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import os

from app.main import app, lifespan
from app.database import Base, get_async_db
from app.models.user import User
from app.models.recipe import Recipe
from app.agents.recipe_harvester import RecipeScrapeResult
from datetime import datetime


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create async database engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session_factory(db_engine):
    """Create async session factory."""
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
        class_=AsyncSession
    )


@pytest_asyncio.fixture(scope="function")
async def test_db(db_engine):
    """Create test database and tables."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def override_get_current_user_id():
    """Override auth dependency to return test user ID."""
    return 1


@pytest_asyncio.fixture
async def client(test_db, db_session_factory):
    """Create test client."""
    from app.api.dependencies import get_current_user_id, get_async_database
    from app.database import get_async_db

    # Override database dependency
    async def override_get_async_db():
        async with db_session_factory() as session:
            yield session

    # CRITICAL: Override get_async_database because that is what the endpoint uses.
    # Overriding get_async_db is not enough because get_async_database calls it directly, not via Depends.
    app.dependency_overrides[get_async_database] = override_get_async_db
    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    # Use lifespan to ensure startup/shutdown events run (e.g. EventBus connection)
    # We mock the database engine in app.main to avoid connecting to real DB during lifespan
    # We also mock EventBus to avoid Redis connection issues during tests

    # Create a mock EventBus that looks healthy
    mock_bus = MagicMock()
    mock_bus.connect = AsyncMock()
    mock_bus.disconnect = AsyncMock()
    mock_bus.publish = AsyncMock()
    mock_bus.redis_client = MagicMock()
    # ping must be awaitable
    mock_bus.redis_client.ping = AsyncMock(return_value=True)

    # Patch the global _event_bus instance in the module
    # This ensures get_event_bus() returns our mock for all consumers
    with patch("app.main.engine", new_callable=MagicMock), \
         patch("app.events.bus._event_bus", mock_bus):

        async with lifespan(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as test_client:
                yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session_factory):
    """Create a test user."""
    async with db_session_factory() as db:
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            country="DE"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@pytest_asyncio.fixture
async def test_recipe(db_session_factory, test_user):
    """Create a test recipe."""
    async with db_session_factory() as db:
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
        await db.commit()
        await db.refresh(recipe)
        return recipe


class TestRecipeAPI:
    """Test suite for Recipe API endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

    @pytest.mark.asyncio
    async def test_list_recipes_empty(self, client, test_user):
        """Test listing recipes when none exist."""
        response = await client.get("/api/v1/recipes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["skip"] == 0
        assert data["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_recipes_with_data(self, client, test_recipe):
        """Test listing recipes with existing data."""
        response = await client.get("/api/v1/recipes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test Pasta Carbonara"
        assert data["items"][0]["id"] == test_recipe.id

    @pytest.mark.asyncio
    async def test_list_recipes_pagination(self, client, test_user, db_session_factory):
        """Test recipe pagination."""
        # Create multiple recipes
        async with db_session_factory() as db:
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
            await db.commit()

        # Test first page
        response = await client.get("/api/v1/recipes?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10

        # Test second page
        response = await client.get("/api/v1/recipes?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 5

    @pytest.mark.asyncio
    async def test_get_recipe_by_id(self, client, test_recipe):
        """Test getting a specific recipe by ID."""
        response = await client.get(f"/api/v1/recipes/{test_recipe.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_recipe.id
        assert data["title"] == "Test Pasta Carbonara"
        assert len(data["ingredients"]) == 3

    @pytest.mark.asyncio
    async def test_get_recipe_not_found(self, client, test_user):
        """Test getting a non-existent recipe."""
        response = await client.get("/api/v1/recipes/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_recipe(self, client, test_recipe):
        """Test deleting a recipe."""
        response = await client.delete(f"/api/v1/recipes/{test_recipe.id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = await client.get(f"/api/v1/recipes/{test_recipe.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_recipe(self, client, test_recipe):
        """Test updating a recipe."""
        update_data = {
            "title": "Updated Pasta Carbonara",
            "servings": 6
        }
        response = await client.put(
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
    @pytest.mark.asyncio
    async def test_harvest_recipe_success(self, mock_event_bus, mock_scraper_class, client, test_user):
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
        response = await client.post("/api/v1/recipes/harvest", json=request_data)

        # Check response
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert data["success"] is True
        assert "queued" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_harvest_recipe_invalid_url(self, client, test_user):
        """Test harvesting with invalid URL."""
        request_data = {
            "url": "",  # Empty URL
            "source_type": "html"
        }
        response = await client.post("/api/v1/recipes/harvest", json=request_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_filter_by_source_type(self, client, test_user, db_session_factory):
        """Test filtering recipes by source type."""
        async with db_session_factory() as db:
            # Create recipes with different source types
            recipe1 = Recipe(
                user_id=test_user.id,
                title="HTML Recipe",
                ingredients=["a"],
                instructions="Test instructions with at least 10 chars",
                source_url="https://example.com/1",
                source_type="html"
            )
            recipe2 = Recipe(
                user_id=test_user.id,
                title="API Recipe",
                ingredients=["b"],
                instructions="Test instructions with at least 10 chars",
                source_url="https://example.com/2",
                source_type="api"
            )
            db.add_all([recipe1, recipe2])
            await db.commit()

        # Filter by HTML
        response = await client.get("/api/v1/recipes?source_type=html")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["source_type"] == "html"

        # Filter by API
        response = await client.get("/api/v1/recipes?source_type=api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["source_type"] == "api"

    @pytest.mark.asyncio
    async def test_duplicate_detection(self, client, test_recipe):
        """Test duplicate recipe detection."""
        # Try to get the existing recipe
        response = await client.get("/api/v1/recipes")
        assert response.status_code == 200
        initial_count = response.json()["total"]

        # The duplicate detection happens in the background task
        # This test verifies the API accepts the request
        request_data = {
            "url": test_recipe.source_url,  # Same URL as existing recipe
            "source_type": "html"
        }
        response = await client.post("/api/v1/recipes/harvest", json=request_data)
        assert response.status_code == 202  # Accepted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
