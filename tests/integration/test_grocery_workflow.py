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
import unittest.mock

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
        id=1, email="test@example.com", password_hash="hashed_password", country="DE"
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
            {"name": "Eggs", "amount": 6, "unit": "pcs"},
        ],
        instructions="Mix everything.",
        source_url="http://example.com/recipe",
        source_type="manual",
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
        total_recipes=1,
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
        servings=2,
    )
    db.add(mp_recipe)
    db.commit()

    db.refresh(meal_plan)
    db.close()
    return meal_plan


@pytest.fixture
def mock_knuspr_client():
    """Mock KnusprMCPClient to avoid external calls."""
    from app.services.knuspr_mcp_client import KnusprProduct, KnusprCart, DeliverySlot

    with unittest.mock.patch("app.api.v1.workflows.KnusprMCPClient") as MockClient:
        client_instance = MockClient.return_value

        # Use AsyncMock for async methods
        client_instance.authenticate = unittest.mock.AsyncMock(return_value=True)

        async def mock_search(ingredient_name, **kwargs):
            return [
                KnusprProduct(
                    product_id=f"prod_{ingredient_name}",
                    name=f"Knuspr {ingredient_name}",
                    quantity=1,
                    unit="pcs",
                    price=2.5,
                    available=True,
                    category="groceries",
                )
            ]

        client_instance.search_products = unittest.mock.AsyncMock(
            side_effect=mock_search
        )

        async def mock_create_cart(items, **kwargs):
            return KnusprCart(
                cart_id=f"cart-{datetime.now().timestamp()}",
                items=[
                    KnusprProduct(
                        product_id=item["product_id"],
                        name=f"Product {item['product_id']}",
                        quantity=item["quantity"],
                        unit=item.get("unit", "pcs"),
                        price=2.5,
                        available=True,
                        category="groceries",
                    )
                    for item in items
                ],
                total_price=sum(item["quantity"] * 2.5 for item in items),
                created_at=datetime.utcnow(),
            )

        client_instance.create_cart = unittest.mock.AsyncMock(
            side_effect=mock_create_cart
        )

        client_instance.get_delivery_slots = unittest.mock.AsyncMock(
            return_value=[
                DeliverySlot(
                    slot_id="slot-1",
                    date=datetime.now(),
                    time_window="Morning",
                    price=5.0,
                    available=True,
                )
            ]
        )

        client_instance.select_delivery_slot = unittest.mock.AsyncMock(
            return_value=True
        )

        client_instance.close = unittest.mock.AsyncMock(return_value=None)

        yield client_instance


@pytest.mark.asyncio
async def test_meal_plan_to_grocery_cart_workflow(
    client, test_user, test_meal_plan, mock_knuspr_client
):
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
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    # 2. Make the API call
    request_data = {
        "meal_plan_id": test_meal_plan.id,
        "delivery_preferences": {
            "preferred_time_slot": "morning",
            "budget_optimization": True,
        },
    }

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # 3. Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "workflow_id" in data
    assert data["result"]["cart_id"] is not None

    # 4. Verify database state
    db = TestingSessionLocal()
    cart = (
        db.query(GroceryCart)
        .filter(GroceryCart.meal_plan_id == test_meal_plan.id)
        .first()
    )
    assert cart is not None
    assert cart.user_id == test_user.id
    assert cart.status == "active"
    # The cart ID will be generated by the mock KnusprMCPClient
    assert cart.knuspr_cart_id.startswith("cart-")

    db.close()


@pytest.mark.asyncio
async def test_workflow_meal_plan_not_found(client, test_user):
    """Test error when meal plan doesn't exist."""
    db = TestingSessionLocal()
    cred_manager = CredentialManager()

    # Create credentials
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=1,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    # Try to create cart with non-existent meal plan
    request_data = {
        "meal_plan_id": 9999,
        "delivery_preferences": {"preferred_time_slot": "afternoon"},
    }

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # Should return 404
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_workflow_no_credentials(client, test_user, test_meal_plan):
    """Test error when user has no Knuspr credentials configured."""
    request_data = {
        "meal_plan_id": test_meal_plan.id,
        "delivery_preferences": {"preferred_time_slot": "morning"},
    }

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # Should return 400 - credentials not configured
    assert response.status_code == 400
    data = response.json()
    assert (
        "credentials not found" in data["detail"].lower()
        or "configure knuspr" in data["detail"].lower()
    )


@pytest.mark.asyncio
async def test_workflow_empty_meal_plan(client, test_user, mock_knuspr_client):
    """Test error when meal plan has no recipes."""
    db = TestingSessionLocal()

    # Create meal plan with no recipes
    meal_plan = MealPlan(
        id=2,
        user_id=test_user.id,
        name="Empty Plan",
        start_date=date.today(),
        end_date=date.today(),
        status="ready",
        total_recipes=0,  # No recipes
    )
    db.add(meal_plan)
    db.commit()
    meal_plan_id = meal_plan.id

    cred_manager = CredentialManager()
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=2,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    # Try to create cart
    request_data = {"meal_plan_id": meal_plan_id, "delivery_preferences": {}}

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # Should return 400 - no recipes
    assert response.status_code == 400
    data = response.json()
    assert "at least one recipe" in data["detail"].lower()


@pytest.mark.asyncio
async def test_workflow_with_all_delivery_preferences(
    client, test_user, test_meal_plan, mock_knuspr_client
):
    """Test workflow with all delivery preferences specified."""
    db = TestingSessionLocal()
    cred_manager = CredentialManager()

    # Create credentials
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=3,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    # Test with all delivery preferences
    request_data = {
        "meal_plan_id": test_meal_plan.id,
        "delivery_preferences": {
            "preferred_dates": [str(date.today())],
            "preferred_time_slot": "evening",
            "budget_optimization": False,
        },
    }

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # Should succeed
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] is not None


@pytest.mark.asyncio
async def test_workflow_without_delivery_preferences(
    client, test_user, test_meal_plan, mock_knuspr_client
):
    """Test workflow without delivery preferences (should use defaults)."""
    db = TestingSessionLocal()
    cred_manager = CredentialManager()

    # Create credentials
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=4,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    # Test without delivery preferences
    request_data = {"meal_plan_id": test_meal_plan.id}

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # Should succeed with default preferences
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] is not None


@pytest.mark.asyncio
async def test_workflow_response_structure(
    client, test_user, test_meal_plan, mock_knuspr_client
):
    """Test that workflow response has all required fields."""
    db = TestingSessionLocal()
    cred_manager = CredentialManager()

    # Create credentials
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=5,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    request_data = {
        "meal_plan_id": test_meal_plan.id,
        "delivery_preferences": {
            "preferred_time_slot": "afternoon",
            "budget_optimization": False,
        },
    }

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all required response fields
    assert "workflow_id" in data
    assert "status" in data
    assert "message" in data
    assert "result" in data

    result = data["result"]
    assert "cart_id" in result
    assert "knuspr_url" in result
    assert "total_price" in result
    assert "item_count" in result
    assert "delivery_slot" in result or result.get("delivery_slot") is None
    assert "items_by_section" in result
    assert "unavailable_items" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_workflow_invalid_meal_plan_id(client, test_user):
    """Test with invalid meal plan ID type."""
    db = TestingSessionLocal()
    cred_manager = CredentialManager()

    # Create credentials
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")

    credential = KnusprCredential(
        id=6,
        user_id=test_user.id,
        knuspr_email=encrypted_email,
        knuspr_password=encrypted_password,
        country="cz",
        is_active=True,
        last_verified_at=datetime.utcnow(),
    )
    db.add(credential)
    db.commit()
    db.close()

    # Try with invalid meal plan ID
    request_data = {"meal_plan_id": "invalid", "delivery_preferences": {}}

    response = client.post(
        "/api/v1/workflows/meal-plan-with-groceries", json=request_data
    )

    # Should return validation error
    assert response.status_code == 422  # Pydantic validation error
