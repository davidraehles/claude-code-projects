import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.agents.cart_optimizer import CartOptimizerAgent
from app.services.knuspr_mcp_client import KnusprCart, DeliverySlot
from app.events import EventType

@pytest.fixture
def mock_knuspr_client():
    client = AsyncMock()
    client.create_cart.return_value = MagicMock(spec=KnusprCart, cart_id="cart_123", total_price=100.0)
    client.get_delivery_slots.return_value = [
        MagicMock(spec=DeliverySlot, slot_id="slot_1", date=datetime.now(), time_window="12:00-14:00", price=5.0)
    ]
    return client

@pytest.fixture
def mock_ingredient_mapper():
    mapper = AsyncMock()
    mapper.map_ingredients_to_products.return_value = (
        [
            {"product_id": "p1", "name": "Milk", "quantity": 1, "unit": "l", "price": 2.5, "category": "dairy"}
        ],
        []
    )
    mapper.categorize_products = MagicMock(return_value={"dairy": [{"name": "Milk", "quantity": 1, "unit": "l", "price": 2.5}]})
    return mapper

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_event_bus():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_cart_success_emits_event_and_metrics(
    mock_knuspr_client, mock_ingredient_mapper, mock_db, mock_event_bus
):
    # Setup
    agent = CartOptimizerAgent(mock_knuspr_client, mock_ingredient_mapper, mock_db, mock_event_bus)

    # Mock internal methods
    agent._extract_ingredients_from_meal_plan = AsyncMock(return_value=["milk"])
    agent._store_cart_in_database = AsyncMock()

    # Mock metrics
    with patch("app.agents.cart_optimizer.cart_creation_total") as mock_total, \
         patch("app.agents.cart_optimizer.cart_creation_duration_seconds") as mock_duration, \
         patch("app.agents.cart_optimizer.cart_value_eur") as mock_value, \
         patch("app.agents.cart_optimizer.cart_items_count") as mock_count:

        # Execute
        result = await agent.create_cart_from_meal_plan(
            meal_plan_id="mp_123",
            user_id="user_456",
            db=mock_db,
            credential_manager=MagicMock()
        )

        # Verify Event Emission
        assert mock_event_bus.publish.called
        event = mock_event_bus.publish.call_args[0][0]
        assert event.event_type == EventType.CART_CREATED
        assert event.payload["cart_id"] == "cart_123"
        assert event.payload["meal_plan_id"] == "mp_123"

        # Verify Metrics
        mock_total.labels.assert_called_with(status="success")
        mock_total.labels.return_value.inc.assert_called()
        mock_duration.observe.assert_called()
        mock_value.observe.assert_called_with(100.0)
        mock_count.observe.assert_called_with(1)

@pytest.mark.asyncio
async def test_create_cart_failure_emits_event_and_metrics(
    mock_knuspr_client, mock_ingredient_mapper, mock_db, mock_event_bus
):
    # Setup
    agent = CartOptimizerAgent(mock_knuspr_client, mock_ingredient_mapper, mock_db, mock_event_bus)

    # Mock failure
    agent._extract_ingredients_from_meal_plan = AsyncMock(side_effect=Exception("DB Error"))

    # Mock metrics
    with patch("app.agents.cart_optimizer.cart_creation_total") as mock_total:

        # Execute
        with pytest.raises(Exception):
            await agent.create_cart_from_meal_plan(
                meal_plan_id="mp_123",
                user_id="user_456",
                db=mock_db,
                credential_manager=MagicMock()
            )

        # Verify Event Emission
        assert mock_event_bus.publish.called
        event = mock_event_bus.publish.call_args[0][0]
        assert event.event_type == EventType.CART_CREATION_FAILED
        assert event.payload["meal_plan_id"] == "mp_123"
        assert "DB Error" in event.payload["error"]

        # Verify Metrics
        mock_total.labels.assert_called_with(status="failure")
        mock_total.labels.return_value.inc.assert_called()
