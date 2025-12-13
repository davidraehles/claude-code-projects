"""
Integration tests for the Meal Plan to Grocery Cart workflow using a simulated MCP session.

Tests the full flow without mocking the KnusprMCPClient class itself, but simulating the
lower-level MCP connection to avoid subprocess stability issues in the test environment.
This ensures the client's response parsing logic (including the fix for CallToolResult) is tested.
"""

import pytest
import asyncio
import os
import json
import logging
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# Set environment
os.environ["APP_ENV"] = "test"
os.environ["KNUSPR_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import date, datetime

from app.main import app
from app.database import Base, get_db
from app.api.dependencies import get_database
from app.models.user import User
from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart
from app.models.knuspr_credential import KnusprCredential
from app.services.credential_manager import CredentialManager
from app.services.knuspr_mcp_client import KnusprMCPClient

# DB Setup
TEST_DATABASE_URL = "sqlite:///./test_grocery_real_client.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
# Use scoped_session to keep session thread-local but accessible
TestingSessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user_id():
    return 1

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_database] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    TestingSessionLocal.remove()
    if os.path.exists("./test_grocery_real_client.db"):
        os.remove("./test_grocery_real_client.db")

@pytest.fixture
def client(test_db):
    from app.api.dependencies import get_current_user_id
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user(test_db):
    db = TestingSessionLocal()
    user = User(id=1, email="test@example.com", password_hash="pw", country="DE")
    db.add(user)
    db.commit()
    # Refresh to ensure it's available, but detached errors can happen if session closes.
    # In SQLite in-memory or single file, persistent objects are tricky across sessions if not carefully managed.
    db.refresh(user)
    # We don't close here, relies on scoped_session cleanup or test teardown
    return user

@pytest.fixture
def test_meal_plan(test_db, test_user):
    db = TestingSessionLocal()
    recipe = Recipe(
        id=1, user_id=test_user.id, title="Test Recipe",
        ingredients=["Milk", "Eggs"], instructions="Mix.",
        source_url="http://x.com", source_type="manual"
    )
    db.add(recipe)

    meal_plan = MealPlan(
        id=1, user_id=test_user.id, name="Plan",
        start_date=date.today(), end_date=date.today(),
        status="ready", total_recipes=1
    )
    db.add(meal_plan)

    mp_recipe = MealPlanRecipe(
        id=1, meal_plan_id=meal_plan.id, recipe_id=recipe.id,
        day_number=1, meal_type="breakfast", servings=2
    )
    db.add(mp_recipe)

    db.commit()
    db.refresh(meal_plan)
    return meal_plan

# Define Mock classes to simulate mcp library structures
class MockTextContent:
    def __init__(self, text):
        self.type = "text"
        self.text = text

class MockCallToolResult:
    def __init__(self, content):
        self.content = content
        self.isError = False

    def dict(self):
        return {"content": [c.__dict__ for c in self.content], "isError": False}

class MockMcpSession:
    async def initialize(self):
        pass

    async def call_tool(self, tool_name, arguments):
        # Simulate tool responses with JSON wrapped in TextContent
        if tool_name == "get_account_data":
            result = {"user_id": "user-123", "email": "test@example.com"}
        elif tool_name == "search_products":
            result = {
                "products": [
                    {
                        "product_id": f"prod_{arguments['product_name']}",
                        "name": f"Knuspr {arguments['product_name']}",
                        "quantity": 1,
                        "unit": "pcs",
                        "price": 2.99,
                        "available": True,
                        "category": "groceries",
                        "confidence": 0.95
                    }
                ]
            }
        elif tool_name == "create_cart":
            result = {
                "cart": {
                    "cart_id": "cart-123",
                    "items": arguments["items"],
                    "total_price": 10.0,
                    "created_at": datetime.utcnow().isoformat()
                }
            }
        elif tool_name == "get_delivery_slots":
            result = {
                "delivery_slots": [
                    {
                        "slot_id": "slot-1",
                        "date": datetime.utcnow().isoformat(),
                        "time_window": "08:00-10:00",
                        "price": 4.99,
                        "available": True
                    }
                ]
            }
        elif tool_name == "select_delivery_slot":
            result = {"success": True}
        else:
            result = {}

        # Wrap in CallToolResult structure
        return MockCallToolResult([MockTextContent(json.dumps(result))])

@asynccontextmanager
async def mock_mcp_session_factory():
    yield MockMcpSession()

@pytest.mark.asyncio
async def test_meal_plan_to_grocery_cart_workflow_real_client(
    client, test_user, test_meal_plan
):
    """
    Test the full workflow.
    Mocks the `_create_mcp_session` to return a MockMcpSession.
    This tests KnusprMCPClient's parsing logic (the fix) without real subprocesses.
    """
    # 1. Setup Credentials
    db = TestingSessionLocal()
    cred_manager = CredentialManager()
    encrypted_email = cred_manager.encrypt("test@knuspr.cz")
    encrypted_password = cred_manager.encrypt("password123")
    credential = KnusprCredential(
        id=1, user_id=test_user.id, knuspr_email=encrypted_email,
        knuspr_password=encrypted_password, country="cz", is_active=True,
        last_verified_at=datetime.utcnow()
    )
    db.add(credential)
    db.commit()

    # 2. Patch the session creator
    with patch("app.services.knuspr_mcp_client._create_mcp_session", side_effect=mock_mcp_session_factory):
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

        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert data["result"]["cart_id"] == "cart-123"

        # 3. Verify DB
        # Re-query using the same session factory or ensure data is committed
        cart = db.query(GroceryCart).filter(GroceryCart.meal_plan_id == test_meal_plan.id).first()
        assert cart is not None
        assert cart.knuspr_cart_id == "cart-123"

    db.close()
