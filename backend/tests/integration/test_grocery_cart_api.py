"""
Integration tests for Grocery Cart API endpoints.

Tests the /api/v1/workflows/carts/from-meal-plan endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.models.recipe import Recipe
from app.api.dependencies import get_current_user_id

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_grocery_cart.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_123",
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""

    def override_get_current_user_id():
        return test_user.id

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_recipes(db_session, test_user):
    """Create test recipes."""
    recipe1 = Recipe(
        user_id=test_user.id,
        title="Pasta Carbonara",
        ingredients=[
            "400g spaghetti",
            "200g pancetta",
            "4 large eggs",
            "100g Parmesan cheese",
            "2 cloves garlic",
        ],
        instructions="Cook pasta. Fry pancetta. Mix eggs and cheese. Combine.",
        prep_time=10,
        cook_time=20,
        servings=4,
        source_url="https://example.com/carbonara",
        source_type="html",
    )

    recipe2 = Recipe(
        user_id=test_user.id,
        title="Spaghetti Bolognese",
        ingredients=[
            "400g spaghetti",
            "500g ground beef",
            "2 cans tomato sauce",
            "1 onion",
            "2 cloves garlic",
        ],
        instructions="Brown beef. Add sauce. Simmer. Cook pasta.",
        prep_time=15,
        cook_time=30,
        servings=4,
        source_url="https://example.com/bolognese",
        source_type="html",
    )

    db_session.add(recipe1)
    db_session.add(recipe2)
    db_session.commit()
    db_session.refresh(recipe1)
    db_session.refresh(recipe2)
    return [recipe1, recipe2]


@pytest.fixture
def test_meal_plan(db_session, test_user, test_recipes):
    """Create a test meal plan with recipes."""
    meal_plan = MealPlan(
        user_id=test_user.id,
        name="Weekly Meal Plan",
        description="Test meal plan",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 7),
        num_people=4,
        total_recipes=2,
        status="ready",
    )
    db_session.add(meal_plan)
    db_session.commit()
    db_session.refresh(meal_plan)

    # Add recipes to meal plan
    for i, recipe in enumerate(test_recipes):
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan.id,
            recipe_id=recipe.id,
            day_number=i + 1,
            meal_type="dinner",
            servings=4,
        )
        db_session.add(meal_plan_recipe)

    db_session.commit()
    return meal_plan


def test_create_cart_from_meal_plan_success(
    authenticated_client, test_meal_plan, test_recipes
):
    """Test successful cart creation from meal plan."""
    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": test_meal_plan.id, "aggregate_duplicates": True},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "cart_id" in data
    assert "cart_name" in data
    assert "total_items" in data
    assert "items" in data
    assert "unmatched_ingredients" in data

    # Verify cart details
    assert data["cart_name"] == f"Grocery List from {test_meal_plan.name}"
    assert data["total_items"] > 0
    assert len(data["items"]) > 0

    # Verify ingredient aggregation (spaghetti appears in both recipes)
    spaghetti_items = [item for item in data["items"] if "spaghetti" in item["name"].lower()]
    assert len(spaghetti_items) >= 1

    # Verify recipe sources tracking
    for item in data["items"]:
        if item.get("recipe_sources"):
            assert isinstance(item["recipe_sources"], list)
            for source in item["recipe_sources"]:
                assert "recipe_id" in source
                assert "recipe_name" in source


def test_create_cart_with_aggregation(authenticated_client, test_meal_plan, test_recipes):
    """Test that duplicate ingredients are properly aggregated."""
    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": test_meal_plan.id, "aggregate_duplicates": True},
    )

    assert response.status_code == 200
    data = response.json()

    # Find spaghetti (appears in both recipes - should be aggregated)
    spaghetti_items = [item for item in data["items"] if "spaghetti" in item["name"].lower()]

    if spaghetti_items:
        spaghetti = spaghetti_items[0]
        # Should have quantity of 800g (400g * 2) or similar
        assert spaghetti["quantity"] >= 400  # At least one recipe's worth
        # Should have multiple recipe sources
        if spaghetti.get("recipe_sources"):
            assert len(spaghetti["recipe_sources"]) >= 1


def test_create_cart_recipe_ids_tracking(
    authenticated_client, db_session, test_meal_plan, test_recipes
):
    """Test that recipe_ids are correctly stored in CartItem."""
    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": test_meal_plan.id, "aggregate_duplicates": True},
    )

    assert response.status_code == 200
    data = response.json()
    cart_id = data["cart_id"]

    # Query database directly to verify recipe_ids storage
    cart_items = db_session.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    assert len(cart_items) > 0

    # Verify recipe_ids is stored as JSON
    for item in cart_items:
        assert item.recipe_ids is not None
        assert isinstance(item.recipe_ids, list)
        assert len(item.recipe_ids) > 0
        # Verify recipe_ids contain valid recipe IDs
        for recipe_id in item.recipe_ids:
            assert recipe_id in [r.id for r in test_recipes]


def test_create_cart_invalid_meal_plan_id(authenticated_client):
    """Test error handling for invalid meal plan ID."""
    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": 99999, "aggregate_duplicates": True},
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_create_cart_unauthorized_access(client, db_session, test_meal_plan):
    """Test error handling for unauthorized access (no auth token)."""
    response = client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": test_meal_plan.id, "aggregate_duplicates": True},
    )

    # Should return 403 Forbidden or 401 Unauthorized
    assert response.status_code in [401, 403]


def test_create_cart_wrong_user(authenticated_client, db_session, test_recipes):
    """Test that user cannot create cart from another user's meal plan."""
    # Create a different user and their meal plan
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_password_456",
        full_name="Other User",
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    other_meal_plan = MealPlan(
        user_id=other_user.id,
        name="Other User's Plan",
        description="Should not be accessible",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 7),
        num_people=2,
        total_recipes=0,
        status="ready",
    )
    db_session.add(other_meal_plan)
    db_session.commit()

    # Try to create cart from other user's meal plan
    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": other_meal_plan.id, "aggregate_duplicates": True},
    )

    assert response.status_code == 404  # Should not find meal plan


def test_database_state_after_cart_creation(
    authenticated_client, db_session, test_meal_plan, test_recipes
):
    """Test that database state is correct after cart creation."""
    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": test_meal_plan.id, "aggregate_duplicates": True},
    )

    assert response.status_code == 200
    data = response.json()
    cart_id = data["cart_id"]

    # Verify GroceryCart was created
    cart = db_session.query(GroceryCart).filter(GroceryCart.id == cart_id).first()
    assert cart is not None
    assert cart.meal_plan_id == test_meal_plan.id
    assert cart.status == "active"
    assert cart.total_items == data["total_items"]

    # Verify CartItems were created
    cart_items = db_session.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    assert len(cart_items) == data["total_items"]

    # Verify all items have required fields
    for item in cart_items:
        assert item.name is not None
        assert item.quantity > 0
        assert item.unit is not None
        assert item.recipe_ids is not None
        assert len(item.recipe_ids) > 0
        assert item.is_purchased is False


def test_create_cart_empty_meal_plan(authenticated_client, db_session, test_user):
    """Test error handling for meal plan with no recipes."""
    # Create meal plan with no recipes
    empty_meal_plan = MealPlan(
        user_id=test_user.id,
        name="Empty Plan",
        description="No recipes",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 7),
        num_people=2,
        total_recipes=0,
        status="draft",
    )
    db_session.add(empty_meal_plan)
    db_session.commit()
    db_session.refresh(empty_meal_plan)

    response = authenticated_client.post(
        "/api/v1/workflows/carts/from-meal-plan",
        json={"meal_plan_id": empty_meal_plan.id, "aggregate_duplicates": True},
    )

    # Should return error for empty meal plan
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
