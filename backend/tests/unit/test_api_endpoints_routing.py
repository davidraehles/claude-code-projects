import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock, AsyncMock

from app.api.v1.grocery_carts import router as grocery_carts_router
from app.api.v1.knuspr_credentials import router as knuspr_credentials_router
from app.api.dependencies import get_database, get_current_user_id
from app.api.v1.knuspr_credentials import get_credential_manager

# --- Fixtures ---

@pytest.fixture(autouse=True)
def cleanup_overrides(app):
    """Clean up dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(grocery_carts_router)
    app.include_router(knuspr_credentials_router)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_user_id():
    return 1

@pytest.fixture
def mock_credential_manager():
    manager = MagicMock()
    # Setup mock return values for credential manager methods
    # Use AsyncMock for awaitable methods

    mock_cred = MagicMock()
    mock_cred.is_active = True
    mock_cred.country = "cz"
    mock_cred.to_dict.return_value = {"knuspr_email": "test@example.com"}
    mock_cred.last_verified_at = None
    mock_cred.verification_error = None

    manager.save_credentials = AsyncMock(return_value=mock_cred)
    manager.delete_credentials = AsyncMock(return_value=True)
    manager.verify_credentials = AsyncMock(return_value=True)

    return manager

# --- Test Grocery Carts API ---

def test_create_grocery_cart_no_trailing_slash(client, app, mock_db, mock_user_id):
    """Test POST /api/v1/grocery-carts works without trailing slash"""

    # Override dependencies
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user_id] = lambda: mock_user_id

    payload = {
        "meal_plan_id": 1,
        "delivery_preferences": {
             "preferred_dates": ["2023-01-01"],
             "preferred_time_slot": "morning"
        }
    }

    # Direct request to the endpoint without trailing slash
    response = client.post("/api/v1/grocery-carts", json=payload, follow_redirects=False)

    assert response.status_code == 200
    data = response.json()
    assert "cart_id" in data
    assert "item_count" in data
    # Assert structure, not exact values from mock to avoid fragility

def test_get_grocery_cart(client, app, mock_db, mock_user_id):
    """Test GET /api/v1/grocery-carts/{id}"""

    app.dependency_overrides[get_database] = lambda: mock_db
    # Not using user_id in endpoint currently, but good practice if auth is added

    cart_id = 1
    response = client.get(f"/api/v1/grocery-carts/{cart_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["cart_id"] == cart_id
    assert data["knuspr_url"] == f"https://knuspr.cz/cart/{cart_id}"

def test_trailing_slash_redirects_to_no_slash(client, app, mock_db, mock_user_id):
    """Test that requests with trailing slash redirect to non-trailing slash (307)."""
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user_id] = lambda: mock_user_id

    payload = {
        "meal_plan_id": "test-plan-1"
    }

    # Attempt POST with trailing slash
    response = client.post("/api/v1/grocery-carts/", json=payload, follow_redirects=False)

    # Expect 307 Redirect (FastAPI default behavior when redirect_slashes=True)
    # The previous issue was that it redirected TO the slash version.
    # Now it should redirect FROM slash TO no-slash.
    assert response.status_code == 307
    assert response.headers["location"] == "http://testserver/api/v1/grocery-carts"

# --- Test Knuspr Credentials API ---

def test_save_knuspr_credentials_no_trailing_slash(client, app, mock_db, mock_user_id, mock_credential_manager):
    """Test POST /api/v1/knuspr-credentials works without trailing slash"""

    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user_id] = lambda: mock_user_id
    app.dependency_overrides[get_credential_manager] = lambda: mock_credential_manager

    payload = {
        "knuspr_email": "test@example.com",
        "knuspr_password": "password123",
        "country": "cz"
    }

    response = client.post("/api/v1/knuspr-credentials", json=payload, follow_redirects=False)

    assert response.status_code == 201
    data = response.json()
    assert data["has_credentials"] is True

def test_get_knuspr_credentials_no_trailing_slash(client, app, mock_db, mock_user_id):
    """Test GET /api/v1/knuspr-credentials works without trailing slash"""

    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user_id] = lambda: mock_user_id

    # Improved mock setup for chained calls
    mock_credential = MagicMock()
    mock_credential.is_active = True
    mock_credential.country = "cz"
    mock_credential.to_dict.return_value = {"knuspr_email": "test@example.com"}
    mock_credential.last_verified_at = None
    mock_credential.verification_error = None

    # Mocking db.query(KnusprCredential).filter(...).first()
    # The code uses: db.query(KnusprCredential).filter(...).first()

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_credential

    response = client.get("/api/v1/knuspr-credentials", follow_redirects=False)

    assert response.status_code == 200
    data = response.json()
    assert data["has_credentials"] is True

def test_delete_knuspr_credentials_no_trailing_slash(client, app, mock_db, mock_user_id, mock_credential_manager):
    """Test DELETE /api/v1/knuspr-credentials works without trailing slash"""

    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user_id] = lambda: mock_user_id
    app.dependency_overrides[get_credential_manager] = lambda: mock_credential_manager

    response = client.delete("/api/v1/knuspr-credentials", follow_redirects=False)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_verify_knuspr_credentials(client, app, mock_db, mock_user_id, mock_credential_manager):
    """Test POST /api/v1/knuspr-credentials/verify"""

    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user_id] = lambda: mock_user_id
    app.dependency_overrides[get_credential_manager] = lambda: mock_credential_manager

    # Need to mock the query to find credentials first
    mock_credential = MagicMock()
    mock_credential.is_active = True
    mock_credential.verification_error = None
    mock_credential.last_verified_at = None

    # The endpoint queries DB twice: once to check existence, once to get updated record
    mock_db.query.return_value.filter.return_value.first.return_value = mock_credential

    response = client.post("/api/v1/knuspr-credentials/verify", follow_redirects=False)

    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
