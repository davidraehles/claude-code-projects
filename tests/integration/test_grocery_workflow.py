"""
Integration tests for the Meal Plan to Grocery Cart workflow.

Tests the full flow:
1. Create a Meal Plan (mock DB entry).
2. Generate Recipes (mock DB entries).
3. Call the new API endpoint `POST /api/v1/workflows/meal-plan-with-groceries`.
4. Verify that a Cart is created in the DB.
"""

import pytest
import asyncio
import os

# Set environment to test to avoid connecting to real DB on startup
os.environ["APP_ENV"] = "test"
# Set encryption key for CredentialManager
from cryptography.fernet import Fernet
os.environ["KNUSPR_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

from app.main import app
from app.database import Base, get_db
from app.api.dependencies import get_database
from app.models.user import User
from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart
from app.models.knuspr_credential import KnusprCredential
from app.services.credential_manager import CredentialManager

# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test_grocery_workflow.db"
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
app.dependency_overrides[get_database] = override_get_db


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
def test_meal_plan(test_db, test_user):
    """Create a test meal plan with recipes."""
    db = TestingSessionLocal()

    # Create a recipe
    recipe = Recipe(
        id=1,
        user_id=test_user.id,
        title="Test Recipe",
        ingredients=[
            {"name": "Milk", "amount": 1, "unit": "liter"},
            {"name": "Eggs", "amount": 6, "unit": "pcs"}
        ],
        instructions="Mix everything.",
        source_url="http://example.com/recipe",
        source_type="manual"
    )
    db.add(recipe)
    db.commit()

    # Create meal plan
    meal_plan = MealPlan(
        id=1,
        user_id=test_user.id,
        name="Weekly Plan",
        start_date=date.today(),
        end_date=date.today(),
        status="ready",
        total_recipes=1
    )
    db.add(meal_plan)
    db.commit()

    # Link recipe to meal plan
    mp_recipe = MealPlanRecipe(
        id=1,
        meal_plan_id=meal_plan.id,
        recipe_id=recipe.id,
        day_number=1,
        meal_type="breakfast",
        servings=2
    )
    db.add(mp_recipe)
    db.commit()

    db.refresh(meal_plan)
    db.close()
    return meal_plan


@pytest.mark.asyncio
async def test_meal_plan_to_grocery_cart_workflow(client, test_user, test_meal_plan):
    """
    Test the full workflow from meal plan to grocery cart.

    Uses real CredentialManager and KnusprMCPClient (which has internal mocks).
    """
    # 1. Setup Credentials
    db = TestingSessionLocal()
    cred_manager = CredentialManager()

    # Manually create credentials with ID to avoid SQLite autoincrement issues with BigInteger
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=1,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow()
    )
    db.add(credential)
    db.commit()
    db.close()

    # 2. Make the API call
    request_data = {
        "meal_plan_id": test_meal_plan.id,
        "delivery_preferences": {
            "preferred_time_slot": "morning",
            "budget_optimization": True
        }
    }

    response = client.post("/api/v1/workflows/meal-plan-with-groceries", json=request_data)

    # 3. Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "workflow_id" in data
    assert data["result"]["cart_id"] is not None

    # 4. Verify database state
    db = TestingSessionLocal()
    cart = db.query(GroceryCart).filter(GroceryCart.meal_plan_id == test_meal_plan.id).first()
    assert cart is not None
    assert cart.user_id == test_user.id
    assert cart.status == "active"
    # The cart ID will be generated by the mock KnusprMCPClient
    assert cart.knuspr_cart_id.startswith("cart-")

    db.close()
