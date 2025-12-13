#!/usr/bin/env python3
"""
Test script to verify Knuspr integration status.

This script tests what we CAN test without real Knuspr credentials:
1. Code structure and imports
2. Mock workflow execution
3. Database model structure
4. API endpoint availability

What we CANNOT test without credentials:
1. Real Knuspr authentication
2. Actual cart creation in Knuspr
3. Real product search
4. Delivery slot selection
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from app.agents.cart_optimizer import CartOptimizerAgent
        from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCart, KnusprProduct, DeliverySlot
        from app.services.ingredient_mapper import IngredientMapper
        from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
        from app.models.recipe import Recipe
        from app.events.bus import EventBus
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_mock_workflow():
    """Test workflow with mock data (no real Knuspr connection)."""
    print("\n🔍 Testing mock workflow...")
    try:
        from app.agents.cart_optimizer import CartOptimizerAgent
        from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCart, KnusprProduct, DeliverySlot
        from app.services.ingredient_mapper import IngredientMapper
        from app.events.bus import EventBus
        from unittest.mock import AsyncMock, MagicMock
        from datetime import datetime, timedelta
        
        # Create mock objects
        mock_knuspr_client = AsyncMock(spec=KnusprMCPClient)
        mock_ingredient_mapper = AsyncMock(spec=IngredientMapper)
        mock_db = MagicMock()
        mock_event_bus = AsyncMock(spec=EventBus)
        
        # Mock product search
        mock_knuspr_client.search_products.return_value = [
            KnusprProduct(
                product_id="prod_milk_1",
                name="Whole Milk 1L",
                quantity=1.0,
                unit="l",
                price=2.50,
                available=True,
                category="dairy",
                confidence=0.95
            )
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
            )
        ]
        mock_knuspr_client.create_cart.return_value = KnusprCart(
            cart_id="test_cart_123",
            items=cart_items,
            total_price=2.50,
            delivery_slot=None,
            created_at=datetime.utcnow()
        )
        
        # Mock delivery slot
        delivery_slot = DeliverySlot(
            slot_id="slot_test_001",
            date=datetime.utcnow() + timedelta(days=1),
            time_window="12:00-14:00",
            price=4.99,
            available=True
        )
        mock_knuspr_client.get_delivery_slots.return_value = [delivery_slot]
        mock_knuspr_client.select_delivery_slot.return_value = True
        mock_knuspr_client.get_domain.return_value = "https://www.knuspr.cz"
        
        # Mock ingredient mapping
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
                }
            ],
            []  # No unmapped ingredients
        )
        
        mock_ingredient_mapper.categorize_products.return_value = {
            "dairy": [
                {
                    "name": "Whole Milk 1L",
                    "quantity": 1.0,
                    "unit": "l",
                    "price": 2.50,
                    "product_id": "prod_milk_1"
                }
            ]
        }
        
        # Initialize agent
        agent = CartOptimizerAgent(
            knuspr_client=mock_knuspr_client,
            ingredient_mapper=mock_ingredient_mapper,
            db=mock_db,
            event_bus=mock_event_bus
        )
        
        # Mock internal methods
        agent._extract_ingredients_from_meal_plan = AsyncMock(return_value=["milk"])
        agent._store_cart_in_database = AsyncMock()
        
        # Execute workflow
        async def run_workflow():
            result = await agent.create_cart_from_meal_plan(
                meal_plan_id=1,
                user_id=1,
                delivery_preferences={
                    "preferred_dates": [],
                    "preferred_time_slot": "afternoon",
                    "budget_optimization": False
                }
            )
            return result
        
        result = asyncio.run(run_workflow())
        
        # Verify results
        assert result is not None
        assert result["cart_id"] == "test_cart_123"
        assert result["total_price"] == 2.50
        assert result["item_count"] == 1
        assert "dairy" in result["items_by_section"]
        
        print("✅ Mock workflow test passed")
        return True
        
    except Exception as e:
        print(f"❌ Mock workflow test failed: {e}")
        return False

def test_database_models():
    """Test that database models are properly defined."""
    print("\n🔍 Testing database models...")
    try:
        from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
        from app.models.recipe import Recipe
        
        # Test that models have required attributes
        assert hasattr(GroceryCart, 'user_id')
        assert hasattr(GroceryCart, 'meal_plan_id')
        assert hasattr(GroceryCart, 'knuspr_cart_id')
        assert hasattr(GroceryCart, 'total_cost')
        
        assert hasattr(CartItem, 'cart_id')
        assert hasattr(CartItem, 'name')
        assert hasattr(CartItem, 'quantity')
        assert hasattr(CartItem, 'category')
        assert hasattr(CartItem, 'knuspr_product_id')
        
        print("✅ Database models test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are available."""
    print("\n🔍 Testing API endpoints...")
    try:
        from app.api.v1 import grocery_carts
        
        # Check that key functions exist
        assert hasattr(grocery_carts, 'create_grocery_cart')
        assert hasattr(grocery_carts, 'get_grocery_cart')
        assert hasattr(grocery_carts, 'delete_grocery_cart')
        
        print("✅ API endpoints test passed")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def main():
    """Run all tests and report results."""
    print("🧪 Knuspr Integration Status Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Mock Workflow", test_mock_workflow),
        ("Database Models", test_database_models),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The Knuspr integration is properly structured.")
        print("\n🔐 What we CAN test (without real credentials):")
        print("   ✅ Code structure and imports")
        print("   ✅ Mock workflow execution")
        print("   ✅ Database model structure")
        print("   ✅ API endpoint availability")
        print("\n🔒 What we CANNOT test (requires real credentials):")
        print("   ❌ Real Knuspr authentication")
        print("   ❌ Actual cart creation in Knuspr")
        print("   ❌ Real product search")
        print("   ❌ Delivery slot selection")
        print("\n📝 To test real Knuspr integration, you need to:")
        print("   1. Set ROHLIK_USERNAME and ROHLIK_PASSWORD environment variables")
        print("   2. Run: python scripts/test_meal_plan_to_cart_integration.py")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
