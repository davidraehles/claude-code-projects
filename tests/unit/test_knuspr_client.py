import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.knuspr_mcp_client import (
    KnusprMCPClient,
    KnusprProduct,
    KnusprCountry,
    DeliverySlot,
    KnusprCart,
    ToolExecutionError,
    ConnectionError,
    ClientSession
)
from tenacity import RetryError
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

@pytest.fixture
def mock_mcp_session():
    """Fixture to provide a mocked mcp.ClientSession."""
    with patch('app.services.knuspr_mcp_client.ClientSession', autospec=True) as MockClientSession:
        mock_session_instance = MockClientSession.return_value
        mock_session_instance.call_tool = AsyncMock()

        def session_factory():
            @asynccontextmanager
            async def fake_session_context():
                yield mock_session_instance

            return fake_session_context()

        with patch('app.services.knuspr_mcp_client._create_mcp_session', side_effect=session_factory):
            yield mock_session_instance

@pytest.fixture
def client(mock_mcp_session):
    """Fixture to provide a KnusprMCPClient with a mocked MCP session."""
    # Ensure ROHLIK_MCP_URL is set for client initialization
    with patch('os.getenv', return_value="http://mock-mcp-url.com"):
        return KnusprMCPClient(
            login_email="test@example.com",
            login_password="password",
            country=KnusprCountry.CZECH_REPUBLIC
        )

@pytest.mark.asyncio
async def test_unit_normalization(client):
    """Test that Knuspr-specific units are normalized correctly."""
    assert client._normalize_knuspr_unit("ks") == "pcs"
    assert client._normalize_knuspr_unit("kus") == "pcs"
    assert client._normalize_knuspr_unit("bal") == "pkg"
    assert client._normalize_knuspr_unit("balení") == "pkg"
    assert client._normalize_knuspr_unit("g") == "g"
    assert client._normalize_knuspr_unit("unknown") == "unknown"

@pytest.mark.asyncio
async def test_authenticate_success(client, mock_mcp_session):
    """Test successful authentication."""
    mock_mcp_session.call_tool.return_value = {"session_token": "mock_token"}

    result = await client.authenticate()

    assert result is True
    assert client.authenticated is True
    assert client.session_token == "implicit-session"
    mock_mcp_session.call_tool.assert_called_once_with(
        "get_account_data",
        arguments={}
    )

@pytest.mark.asyncio
async def test_authenticate_failure_no_token(client, mock_mcp_session):
    """Test authentication failure when no session token is returned."""
    mock_mcp_session.call_tool.side_effect = ToolExecutionError("Auth failed", "AUTH_ERROR")

    result = await client.authenticate()

    assert result is False
    assert client.authenticated is False
    assert client.session_token is None
    mock_mcp_session.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_authenticate_tool_execution_error(client, mock_mcp_session):
    """Test authentication failure due to ToolExecutionError."""
    mock_mcp_session.call_tool.side_effect = ToolExecutionError("Auth failed", "AUTH_ERROR")

    result = await client.authenticate()

    assert result is False
    assert client.authenticated is False
    mock_mcp_session.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_authenticate_connection_error(client, mock_mcp_session):
    """Test authentication failure due to ConnectionError."""
    mock_mcp_session.call_tool.side_effect = ConnectionError("Connection lost")

    result = await client.authenticate()

    assert result is False
    assert client.authenticated is False
    mock_mcp_session.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_search_products_success(client, mock_mcp_session):
    """Test successful product search."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {
        "products": [
            {
                "product_id": "1", "name": "Apple", "quantity": 1, "unit": "pcs",
                "price": 1.0, "available": True, "category": "fruit"
            },
            {
                "product_id": "2", "name": "Red Apple", "quantity": 500, "unit": "g",
                "price": 2.5, "available": True, "category": "fruit"
            }
        ]
    }

    products = await client.search_products("apple")

    assert len(products) == 2
    assert products[0].name == "Apple"
    assert products[1].name == "Red Apple"
    mock_mcp_session.call_tool.assert_called_once_with(
        "search_products",
        arguments={
            "product_name": "apple",
            "country": "cz",
            "max_results": 10,
            "exact_match": False,
        }
    )

@pytest.mark.asyncio
async def test_search_products_exact_match(client, mock_mcp_session):
    """Test product search with exact match."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {
        "products": [
            {
                "product_id": "1", "name": "Exact Apple", "quantity": 1, "unit": "pcs",
                "price": 1.0, "available": True, "category": "fruit"
            }
        ]
    }

    products = await client.search_products("Exact Apple", exact_match=True)

    assert len(products) == 1
    assert products[0].name == "Exact Apple"
    mock_mcp_session.call_tool.assert_called_once_with(
        "search_products",
        arguments={
            "product_name": "Exact Apple",
            "country": "cz",
            "max_results": 10,
            "exact_match": True,
        }
    )

@pytest.mark.asyncio
async def test_search_products_unauthenticated(client, mock_mcp_session):
    """Test product search when unauthenticated, expecting re-authentication."""
    client.authenticated = False
    mock_mcp_session.call_tool.side_effect = [
        {"session_token": "new_mock_token"},
        {"products": []}
    ]

    products = await client.search_products("apple")

    assert len(products) == 0
    assert client.authenticated is True
    assert client.session_token == "implicit-session"
    assert mock_mcp_session.call_tool.call_count == 2

@pytest.mark.asyncio
async def test_search_products_tool_execution_error(client, mock_mcp_session):
    """Test product search failure due to ToolExecutionError."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.side_effect = ToolExecutionError("Search failed", "SEARCH_ERROR")

    with pytest.raises(RuntimeError, match="Knuspr product search failed: Search failed"):
        await client.search_products("apple")
    assert mock_mcp_session.call_tool.call_count == client.max_retries

@pytest.mark.asyncio
async def test_search_products_connection_error(client, mock_mcp_session):
    """Test product search failure due to ConnectionError."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.side_effect = ConnectionError("Connection lost")

    with pytest.raises(RuntimeError, match="Knuspr product search connection error: Connection lost"):
        await client.search_products("apple")
    assert mock_mcp_session.call_tool.call_count == client.max_retries

@pytest.mark.asyncio
async def test_create_cart_success(client, mock_mcp_session):
    """Test successful cart creation."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_items = [
        {"product_id": "prod1", "quantity": 2, "unit": "pcs"},
        {"product_id": "prod2", "quantity": 500, "unit": "g"}
    ]
    mock_mcp_session.call_tool.return_value = {
        "cart": {
            "cart_id": "cart123",
            "items": [
                {"product_id": "prod1", "name": "Product 1", "quantity": 2, "unit": "pcs", "price": 10.0, "available": True, "category": "cat1"},
                {"product_id": "prod2", "name": "Product 2", "quantity": 500, "unit": "g", "price": 5.0, "available": True, "category": "cat2"}
            ],
            "total_price": 25.0,
            "created_at": datetime.utcnow().isoformat()
        }
    }

    cart = await client.create_cart(mock_items)

    assert cart.cart_id == "cart123"
    assert len(cart.items) == 2
    assert cart.total_price == 25.0
    mock_mcp_session.call_tool.assert_called_once_with(
        "create_cart",
        arguments={
            "items": mock_items,
            "delivery_slot_id": None
        }
    )

@pytest.mark.asyncio
async def test_create_cart_empty_items(client):
    """Test cart creation with empty items list."""
    with pytest.raises(ValueError, match="Cart must contain at least one item"):
        await client.create_cart([])

@pytest.mark.asyncio
async def test_create_cart_tool_execution_error(client, mock_mcp_session):
    """Test cart creation failure due to ToolExecutionError."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_items = [{"product_id": "prod1", "quantity": 1, "unit": "pcs"}]
    mock_mcp_session.call_tool.side_effect = ToolExecutionError("Cart failed", "CART_ERROR")

    with pytest.raises(RuntimeError, match="Knuspr cart creation failed: Cart failed"):
        await client.create_cart(mock_items)
    assert mock_mcp_session.call_tool.call_count == client.max_retries

@pytest.mark.asyncio
async def test_get_delivery_slots_success(client, mock_mcp_session):
    """Test successful retrieval of delivery slots."""
    client.authenticated = True
    client.session_token = "mock_token"
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    mock_mcp_session.call_tool.return_value = {
        "delivery_slots": [
            {"slot_id": "slot1", "date": start_date.isoformat(), "time_window": "09-12", "price": 50.0, "available": True},
            {"slot_id": "slot2", "date": end_date.isoformat(), "time_window": "14-17", "price": 60.0, "available": True}
        ]
    }

    slots = await client.get_delivery_slots(start_date, end_date)

    assert len(slots) == 2
    assert slots[0].slot_id == "slot1"
    assert slots[1].slot_id == "slot2"
    mock_mcp_session.call_tool.assert_called_once_with(
        "get_delivery_slots",
        arguments={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "country": "cz",
        }
    )

@pytest.mark.asyncio
async def test_get_delivery_slots_invalid_date_range(client):
    """Test retrieval of delivery slots with invalid date range."""
    start_date = datetime.now()
    end_date = start_date - timedelta(days=1)
    with pytest.raises(ValueError, match="start_date must be before end_date"):
        await client.get_delivery_slots(start_date, end_date)

@pytest.mark.asyncio
async def test_select_delivery_slot_success(client, mock_mcp_session):
    """Test successful selection of a delivery slot."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {"success": True}

    result = await client.select_delivery_slot("cart123", "slot456")

    assert result is True
    mock_mcp_session.call_tool.assert_called_once_with(
        "select_delivery_slot",
        arguments={
            "cart_id": "cart123",
            "slot_id": "slot456",
        }
    )

@pytest.mark.asyncio
async def test_select_delivery_slot_failure(client, mock_mcp_session):
    """Test failed selection of a delivery slot."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {"success": False, "message": "Slot unavailable"}

    result = await client.select_delivery_slot("cart123", "slot456")

    assert result is False
    mock_mcp_session.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_get_cart_success(client, mock_mcp_session):
    """Test successful retrieval of a cart."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {
        "cart": {
            "cart_id": "cart123",
            "items": [
                {"product_id": "prod1", "name": "Product 1", "quantity": 2, "unit": "pcs", "price": 10.0, "available": True, "category": "cat1"}
            ],
            "total_price": 20.0,
            "created_at": datetime.utcnow().isoformat(),
            "delivery_slot": {"slot_id": "slot456", "date": datetime.utcnow().isoformat(), "time_window": "09-12", "price": 50.0, "available": True}
        }
    }

    cart = await client.get_cart("cart123")

    assert cart is not None
    assert cart.cart_id == "cart123"
    assert cart.delivery_slot is not None
    mock_mcp_session.call_tool.assert_called_once_with(
        "get_cart",
        arguments={
            "cart_id": "cart123",
        }
    )

@pytest.mark.asyncio
async def test_get_cart_not_found(client, mock_mcp_session):
    """Test retrieval of a non-existent cart."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {"cart": None}

    cart = await client.get_cart("nonexistent_cart")

    assert cart is None
    mock_mcp_session.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_close_success(client, mock_mcp_session):
    """Test successful client close and logout."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.return_value = {"success": True}

    await client.close()

    assert client.authenticated is False
    # The implementation just sets authenticated=False and session_token=None
    # It does not call logout tool
    mock_mcp_session.call_tool.assert_not_called()

@pytest.mark.asyncio
async def test_close_unauthenticated(client, mock_mcp_session):
    """Test client close when already unauthenticated."""
    client.authenticated = False

    await client.close()

    mock_mcp_session.call_tool.assert_not_called()
    assert client.authenticated is False

@pytest.mark.asyncio
async def test_retry_behavior_tool_execution_error(client, mock_mcp_session):
    """Test that methods retry on ToolExecutionError and eventually raise."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.side_effect = ToolExecutionError("Transient error", "TRANSIENT")

    with pytest.raises(RuntimeError, match="Knuspr product search failed: Transient error"):
        await client.search_products("test")

    assert mock_mcp_session.call_tool.call_count == client.max_retries

@pytest.mark.asyncio
async def test_retry_behavior_connection_error(client, mock_mcp_session):
    """Test that methods retry on ConnectionError and eventually raise."""
    client.authenticated = True
    client.session_token = "mock_token"
    mock_mcp_session.call_tool.side_effect = ConnectionError("Network hiccup")

    with pytest.raises(RuntimeError, match="Knuspr product search connection error: Network hiccup"):
        await client.search_products("test")

    assert mock_mcp_session.call_tool.call_count == client.max_retries
