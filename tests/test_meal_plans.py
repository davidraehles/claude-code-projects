"""
Integration tests for Meal Plan API endpoints.

Tests the FastAPI meal plan endpoints including creation, listing, detail view,
deletion, and grocery cart generation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.recipe import Recipe


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test_meal_plans.db"
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


def create_test_recipes(db, user_id, count=21):
    """Helper function to create test recipes."""
    recipes = []
    recipe_names = [
        "Breakfast Oatmeal", "Scrambled Eggs", "Greek Yogurt Bowl",
        "Pasta Carbonara", "Chicken Salad", "Vegetable Stir Fry",
        "Grilled Salmon", "Beef Tacos", "Vegetable Curry",
        "Mushroom Risotto", "Chicken Soup", "Quinoa Bowl",
        "Fish and Chips", "Lentil Soup", "Turkey Sandwich",
        "Veggie Pizza", "Chicken Tikka", "Spaghetti Bolognese",
        "Caesar Salad", "Fried Rice", "Tomato Soup"
    ]

    for i in range(min(count, len(recipe_names))):
        recipe = Recipe(
            user_id=user_id,
            title=recipe_names[i],
            ingredients=["ingredient1", "ingredient2"],
            instructions=f"Cook {recipe_names[i].lower()}",
            prep_time=10,
            cook_time=20,
            servings=2,
            nutrition={"calories": 500},
            source_url=f"https://example.com/recipe-{i}",
            source_type="html"
        )
        db.add(recipe)
        recipes.append(recipe)

    db.commit()
    return recipes


class TestMealPlanAPI:
    """Test suite for Meal Plan API endpoints."""

    def test_create_meal_plan_simple(self, client, test_user):
        """Test creating a simple 3-day meal plan."""
        # Create recipes first
        db = TestingSessionLocal()
        create_test_recipes(db, test_user.id, 9)
        db.close()

        request_data = {
            "start_date": "2025-11-18",
            "num_days": 3,
            "num_people": 2,
            "meals_per_day": 3
        }

        response = client.post("/api/v1/meal-plans", json=request_data)

        assert response.status_code == 202
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["num_days"] == 3
        assert data["num_people"] == 2
        assert data["status"] == "ready"
        assert data["total_recipes"] == 9
        assert "id" in data

    def test_create_meal_plan_with_constraints(self, client, test_user):
        """Test creating a meal plan with dietary constraints."""
        # Create recipes first
        db = TestingSessionLocal()
        create_test_recipes(db, test_user.id, 21)
        db.close()

        request_data = {
            "start_date": "2025-11-20",
            "num_days": 7,
            "num_people": 4,
            "dietary_restrictions": ["vegetarian"],
            "target_calories_per_day": 2000,
            "target_budget": 50.0,
            "meals_per_day": 3
        }

        response = client.post("/api/v1/meal-plans", json=request_data)

        assert response.status_code == 202
        data = response.json()
        assert data["num_days"] == 7
        assert data["num_people"] == 4
        assert data["dietary_restrictions"] == ["vegetarian"]
        assert data["target_calories_per_day"] == 2000
        assert data["target_budget"] == 50.0
        assert data["total_recipes"] == 21

    def test_create_meal_plan_invalid_days(self, client, test_user):
        """Test creating a meal plan with invalid number of days."""
        request_data = {
            "start_date": "2025-11-18",
            "num_days": 50,  # Exceeds maximum of 30
            "num_people": 2
        }

        response = client.post("/api/v1/meal-plans", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_list_meal_plans_empty(self, client, test_user):
        """Test listing meal plans when none exist."""
        response = client.get("/api/v1/meal-plans")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_list_meal_plans_with_data(self, client, test_user):
        """Test listing meal plans with existing data."""
        # Create recipes and meal plan
        db = TestingSessionLocal()
        create_test_recipes(db, test_user.id, 9)
        db.close()

        request_data = {
            "start_date": "2025-11-18",
            "num_days": 3,
            "num_people": 2,
            "meals_per_day": 3
        }
        create_response = client.post("/api/v1/meal-plans", json=request_data)
        assert create_response.status_code == 202

        # List meal plans
        response = client.get("/api/v1/meal-plans")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["num_days"] == 3

    def test_get_meal_plan_detail(self, client, test_user):
        """Test getting detailed meal plan."""
        # Create recipes and meal plan
        db = TestingSessionLocal()
        create_test_recipes(db, test_user.id, 9)
        db.close()

        request_data = {
            "start_date": "2025-11-18",
            "num_days": 3,
            "num_people": 2,
            "meals_per_day": 3
        }
        create_response = client.post("/api/v1/meal-plans", json=request_data)
        meal_plan_id = create_response.json()["id"]

        # Get detailed view
        response = client.get(f"/api/v1/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        data = response.json()

        assert "meal_plan" in data
        assert "days" in data
        assert "statistics" in data
        assert len(data["days"]) == 3

    def test_get_meal_plan_not_found(self, client, test_user):
        """Test getting a non-existent meal plan."""
        response = client.get("/api/v1/meal-plans/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_meal_plan(self, client, test_user):
        """Test deleting a meal plan."""
        # Create recipes and meal plan
        db = TestingSessionLocal()
        create_test_recipes(db, test_user.id, 9)
        db.close()

        request_data = {
            "start_date": "2025-11-18",
            "num_days": 3,
            "num_people": 2,
            "meals_per_day": 3
        }
        create_response = client.post("/api/v1/meal-plans", json=request_data)
        meal_plan_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/meal-plans/{meal_plan_id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/v1/meal-plans/{meal_plan_id}")
        assert response.status_code == 404

    def test_generate_grocery_cart(self, client, test_user):
        """Test generating a grocery cart from a meal plan."""
        # Create recipes and meal plan
        db = TestingSessionLocal()
        create_test_recipes(db, test_user.id, 9)
        db.close()

        request_data = {
            "start_date": "2025-11-18",
            "num_days": 3,
            "num_people": 2,
            "meals_per_day": 3
        }
        create_response = client.post("/api/v1/meal-plans", json=request_data)
        meal_plan_id = create_response.json()["id"]

        # Generate grocery cart
        response = client.post(f"/api/v1/meal-plans/{meal_plan_id}/grocery-cart")
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "name" in data
        assert "total_items" in data
        assert data["status"] == "active"
        assert data["total_items"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
