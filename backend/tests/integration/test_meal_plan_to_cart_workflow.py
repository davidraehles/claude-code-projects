"""
Integration tests for the full meal-plan-to-grocery-cart workflow (T192-T198).

Tests the complete end-to-end orchestration:
1. Fetch meal plan from database
2. Extract ingredients from recipes
3. Map ingredients to Knuspr products
4. Create Knuspr cart
5. Select delivery slot
6. Store cart in database
7. Return comprehensive cart summary
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.agents.cart_optimizer import CartOptimizerAgent
from app.services.knuspr_mcp_client import (
    KnusprMCPClient,
    KnusprCart,
    KnusprProduct,
    DeliverySlot,
    KnusprCountry,
)
from app.services.ingredient_mapper import IngredientMapper
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.models.recipe import Recipe
from app.events.bus import EventBus


@pytest.fixture
def mock_knuspr_client():
    """Mock Knuspr MCP client."""
    client = AsyncMock(spec=KnusprMCPClient)

    # Mock product search
    client.search_products.return_value = [
        KnusprProduct(
            product_id="prod_milk_1",
            name="Whole Milk 1L",
            quantity=1.0,
            unit="l",
            price=2.50,
            available=True,
            category="dairy",
            confidence=0.95
        ),
        KnusprProduct(
            product_id="prod_bread_1",
            name="Whole Wheat Bread 500g",
            quantity=500,
            unit="g",
            price=1.80,
            available=True,
            category="grains",
            confidence=0.88
        ),
        KnusprProduct(
            product_id="prod_eggs_1",
            name="Free Range Eggs (6 pack)",
            quantity=6,
            unit="pcs",
            price=3.20,
            available=True,
            category="dairy",
            confidence=0.92
        ),
    ]

    # Mock cart creation
    cart_items = [
        KnusprProduct(
            product_id="prod_milk_1",
            name="Whole Milk 1L",
            quantity=1.0,
            unit="l",
            price=2.50,
            available=True,
            category="dairy"
        ),
        KnusprProduct(
            product_id="prod_bread_1",
            name="Whole Wheat Bread 500g",
            quantity=500,
            unit="g",
            price=1.80,
            available=True,
            category="grains"
        ),
        KnusprProduct(
            product_id="prod_eggs_1",
            name="Free Range Eggs (6 pack)",
            quantity=6,
            unit="pcs",
            price=3.20,
            available=True,
            category="dairy"
        ),
    ]

    client.create_cart.return_value = KnusprCart(
        cart_id="knuspr_cart_12345",
        items=cart_items,
        total_price=7.50,
        delivery_slot=None,
        created_at=datetime.utcnow()
    )

    # Mock delivery slot selection
    delivery_slot = DeliverySlot(
        slot_id="slot_2024_001",
        date=datetime.utcnow() + timedelta(days=2),
        time_window="12:00-14:00",
        price=4.99,
        available=True
    )

    client.get_delivery_slots.return_value = [delivery_slot]
    client.select_delivery_slot.return_value = True
    client.get_domain.return_value = "https://www.knuspr.cz"
    client.close.return_value = None

    return client


@pytest.fixture
def mock_ingredient_mapper(mock_knuspr_client):
    """Mock ingredient mapper."""
    mapper = AsyncMock(spec=IngredientMapper)

    # Mock ingredient mapping
    mapper.map_ingredients_to_products.return_value = (
        [
            {
                "product_id": "prod_milk_1",
                "name": "Whole Milk 1L",
                "quantity": 1.0,
                "unit": "l",
                "price": 2.50,
                "category": "dairy",
                "available": True,
                "confidence": 0.95
            },
            {
                "product_id": "prod_bread_1",
                "name": "Whole Wheat Bread 500g",
                "quantity": 500,
                "unit": "g",
                "price": 1.80,
                "category": "grains",
                "available": True,
                "confidence": 0.88
            },
            {
                "product_id": "prod_eggs_1",
                "name": "Free Range Eggs (6 pack)",
                "quantity": 6,
                "unit": "pcs",
                "price": 3.20,
                "category": "dairy",
                "available": True,
                "confidence": 0.92
            },
        ],
        []  # No unmapped ingredients
    )

    # Mock categorization
    mapper.categorize_products.return_value = {
        "dairy": [
            {"name": "Whole Milk 1L", "quantity": 1.0, "unit": "l", "price": 2.50, "product_id": "prod_milk_1"},
            {"name": "Free Range Eggs (6 pack)", "quantity": 6, "unit": "pcs", "price": 3.20, "product_id": "prod_eggs_1"},
        ],
        "grains": [
            {"name": "Whole Wheat Bread 500g", "quantity": 500, "unit": "g", "price": 1.80, "product_id": "prod_bread_1"},
        ]
    }

    return mapper


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = MagicMock(spec=Session)

    # Mock meal plan query
    mock_meal_plan = MagicMock(spec=MealPlan)
    mock_meal_plan.id = 1
    mock_meal_plan.user_id = 1
    mock_meal_plan.total_recipes = 3
    mock_meal_plan.recipes = []

    db.query.return_value.filter.return_value.first.return_value = mock_meal_plan
    db.add = MagicMock()
    db.flush = MagicMock()
    db.commit = MagicMock()
    db.rollback = MagicMock()

    return db


@pytest.fixture
def mock_event_bus():
    """Mock event bus."""
    return AsyncMock(spec=EventBus)


@pytest.mark.asyncio
async def test_full_meal_plan_to_cart_workflow(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_db,
    mock_event_bus
):
    """Test complete workflow: meal plan → ingredients → products → cart."""

    # Initialize agent
    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    # Mock internal methods
    agent._extract_ingredients_from_meal_plan = AsyncMock(
        return_value=["milk", "bread", "eggs"]
    )
    agent._store_cart_in_database = AsyncMock()

    # Execute workflow
    result = await agent.create_cart_from_meal_plan(
        meal_plan_id=1,
        user_id=1,
        db=mock_db,
        credential_manager=None,
        delivery_preferences={
            "preferred_dates": [],
            "preferred_time_slot": "afternoon",
            "budget_optimization": False
        }
    )

    # Assertions
    assert result is not None
    assert result["cart_id"] == "knuspr_cart_12345"
    assert result["knuspr_url"] == "https://www.knuspr.cz/cart/knuspr_cart_12345"
    assert result["total_price"] == 7.50
    assert result["item_count"] == 3
    assert result["delivery_slot"] is not None
    assert result["delivery_slot"]["slot_id"] == "slot_2024_001"
    assert result["items_by_section"] is not None
    assert "dairy" in result["items_by_section"]
    assert "grains" in result["items_by_section"]

    # Verify event was published
    mock_event_bus.publish.assert_called_once()
    published_event = mock_event_bus.publish.call_args[0][0]
    assert published_event.event_type.value == "cart.created"
    assert published_event.payload["cart_id"] == "knuspr_cart_12345"


@pytest.mark.asyncio
async def test_workflow_handles_missing_meal_plan(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_event_bus
):
    """Test workflow error handling when meal plan is not found."""

    # Mock empty database response
    mock_db = MagicMock(spec=Session)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    # Expect error
    with pytest.raises(ValueError, match="Meal plan"):
        await agent.create_cart_from_meal_plan(
            meal_plan_id=999,
            user_id=1,
            db=mock_db,
            credential_manager=None
        )


@pytest.mark.asyncio
async def test_workflow_handles_no_ingredients(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_db,
    mock_event_bus
):
    """Test workflow error handling when meal plan has no ingredients."""

    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    # Mock empty ingredients
    agent._extract_ingredients_from_meal_plan = AsyncMock(return_value=[])

    # Expect error
    with pytest.raises(ValueError, match="no ingredients"):
        await agent.create_cart_from_meal_plan(
            meal_plan_id=1,
            user_id=1,
            db=mock_db,
            credential_manager=None
        )


@pytest.mark.asyncio
async def test_workflow_handles_unmapped_ingredients(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_db,
    mock_event_bus
):
    """Test workflow succeeds even when some ingredients are unmapped."""

    # Override ingredient mapper to return partial matches
    mock_ingredient_mapper.map_ingredients_to_products.return_value = (
        [
            {
                "product_id": "prod_milk_1",
                "name": "Whole Milk 1L",
                "quantity": 1.0,
                "unit": "l",
                "price": 2.50,
                "category": "dairy",
                "available": True,
                "confidence": 0.95
            },
        ],
        ["exotic ingredient", "rare spice"]  # Unmapped items
    )

    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    agent._extract_ingredients_from_meal_plan = AsyncMock(
        return_value=["milk", "exotic ingredient", "rare spice"]
    )
    agent._store_cart_in_database = AsyncMock()

    # Execute - should succeed with partial mapping
    result = await agent.create_cart_from_meal_plan(
        meal_plan_id=1,
        user_id=1,
        db=mock_db,
        credential_manager=None
    )

    assert result is not None
    assert result["item_count"] == 1  # Only mapped item
    assert len(result["unavailable_items"]) == 2
    assert "exotic ingredient" in result["unavailable_items"]


@pytest.mark.asyncio
async def test_workflow_publishes_events_on_success(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_db,
    mock_event_bus
):
    """Test that workflow publishes CART_CREATED event on success."""

    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    agent._extract_ingredients_from_meal_plan = AsyncMock(
        return_value=["milk", "bread", "eggs"]
    )
    agent._store_cart_in_database = AsyncMock()

    await agent.create_cart_from_meal_plan(
        meal_plan_id=1,
        user_id=1,
        db=mock_db,
        credential_manager=None
    )

    # Verify event published
    assert mock_event_bus.publish.called
    event = mock_event_bus.publish.call_args[0][0]
    assert event.event_type.value == "cart.created"
    assert event.user_id == 1


@pytest.mark.asyncio
async def test_workflow_publishes_events_on_failure(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_db,
    mock_event_bus
):
    """Test that workflow publishes CART_CREATION_FAILED event on error."""

    # Mock ingredient mapper to fail
    mock_ingredient_mapper.map_ingredients_to_products.side_effect = RuntimeError("Mapping failed")

    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    agent._extract_ingredients_from_meal_plan = AsyncMock(
        return_value=["milk", "bread", "eggs"]
    )

    with pytest.raises(RuntimeError):
        await agent.create_cart_from_meal_plan(
            meal_plan_id=1,
            user_id=1,
            db=mock_db,
            credential_manager=None
        )

    # Verify failure event published
    assert mock_event_bus.publish.called
    event = mock_event_bus.publish.call_args[0][0]
    assert event.event_type.value == "cart.creation.failed"
    assert event.user_id == 1


@pytest.mark.asyncio
async def test_workflow_selects_delivery_slot_by_preferences(
    mock_knuspr_client,
    mock_ingredient_mapper,
    mock_db,
    mock_event_bus
):
    """Test that workflow respects delivery slot preferences."""

    # Mock multiple delivery slots
    tomorrow = datetime.utcnow() + timedelta(days=1)
    day_after = datetime.utcnow() + timedelta(days=2)

    mock_knuspr_client.get_delivery_slots.return_value = [
        DeliverySlot(
            slot_id="morning_slot",
            date=tomorrow,
            time_window="08:00-10:00",
            price=5.99,
            available=True
        ),
        DeliverySlot(
            slot_id="afternoon_slot",
            date=tomorrow,
            time_window="14:00-16:00",
            price=4.99,
            available=True
        ),
        DeliverySlot(
            slot_id="evening_slot",
            date=day_after,
            time_window="18:00-20:00",
            price=3.99,
            available=True
        ),
    ]

    agent = CartOptimizerAgent(
        knuspr_client=mock_knuspr_client,
        ingredient_mapper=mock_ingredient_mapper,
        db=mock_db,
        event_bus=mock_event_bus
    )

    agent._extract_ingredients_from_meal_plan = AsyncMock(
        return_value=["milk", "bread", "eggs"]
    )
    agent._store_cart_in_database = AsyncMock()

    # Request afternoon slot
    result = await agent.create_cart_from_meal_plan(
        meal_plan_id=1,
        user_id=1,
        db=mock_db,
        credential_manager=None,
        delivery_preferences={
            "preferred_dates": [],
            "preferred_time_slot": "afternoon",
            "budget_optimization": False
        }
    )

    # Should select afternoon slot (by time preference, then earliest)
    assert result["delivery_slot"]["time_window"] in ["14:00-16:00", "18:00-20:00"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
