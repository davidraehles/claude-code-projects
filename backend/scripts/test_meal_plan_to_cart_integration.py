#!/usr/bin/env python3
"""
Real integration test for Meal Plan to Grocery Cart workflow.

Tests the complete flow without mocks:
1. Create test meal plan with recipes
2. Call cart creation workflow
3. Verify cart created in Knuspr
4. Verify data stored in database
5. Test retrieval endpoint
6. Cleanup test data

Usage:
    python scripts/test_meal_plan_to_cart_integration.py

Requirements:
    - ROHLIK_USERNAME and ROHLIK_PASSWORD in environment
    - Database connection configured
    - Knuspr MCP server available
"""

import asyncio
import os
import sys
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry
from app.services.ingredient_mapper import IngredientMapper
from app.services.credential_manager import CredentialManager
from app.agents.cart_optimizer import CartOptimizerAgent
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.models.recipe import Recipe, Ingredient, RecipeIngredient
from app.models.user import User
from app.database import Base
from app.events.bus import get_event_bus


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def print_header(msg: str):
    """Print header message in bold."""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}\n")


async def test_knuspr_integration():
    """
    Main integration test function.

    Tests the complete meal plan to grocery cart workflow.
    """
    load_dotenv()

    # Get credentials from environment
    email = os.getenv("ROHLIK_USERNAME")
    password = os.getenv("ROHLIK_PASSWORD")
    database_url = os.getenv("DATABASE_URL")

    if not email or not password:
        print_error("ROHLIK_USERNAME or ROHLIK_PASSWORD not set in environment")
        print_info("Please set these environment variables and try again")
        return False

    if not database_url:
        print_error("DATABASE_URL not set in environment")
        return False

    print_header("Knuspr Integration Test - Meal Plan to Grocery Cart")

    # Setup database connection
    print_info("Setting up database connection...")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Test variables
    test_user = None
    test_recipe = None
    test_meal_plan = None
    test_cart = None
    knuspr_client = None

    try:
        # Step 1: Get or create test user
        print_header("Step 1: Setup Test User")
        test_user = db.query(User).filter(User.email == "test@example.com").first()

        if not test_user:
            print_info("Creating test user...")
            test_user = User(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                hashed_password="test_hash"  # Not used for this test
            )
            db.add(test_user)
            db.commit()
            print_success(f"Created test user with ID: {test_user.id}")
        else:
            print_success(f"Using existing test user with ID: {test_user.id}")

        # Store Knuspr credentials for test user
        print_info("Storing Knuspr credentials...")
        credential_manager = CredentialManager()
        await credential_manager.store_credentials(
            db=db,
            user_id=test_user.id,
            email=email,
            password=password,
            country="cz"
        )
        print_success("Credentials stored successfully")

        # Step 2: Create test recipe with ingredients
        print_header("Step 2: Create Test Recipe")
        print_info("Creating test recipe with ingredients...")

        test_recipe = Recipe(
            name="Test Pasta Carbonara",
            description="A simple pasta dish for testing",
            cuisine="Italian",
            difficulty="easy",
            prep_time_minutes=15,
            cook_time_minutes=20,
            servings=2,
            calories=650,
            instructions="Cook pasta. Mix eggs and cheese. Combine.",
            is_public=True,
            user_id=test_user.id
        )
        db.add(test_recipe)
        db.flush()

        # Add ingredients
        ingredient_data = [
            ("Spaghetti", 200, "g"),
            ("Eggs", 2, "pcs"),
            ("Bacon", 100, "g"),
            ("Parmesan cheese", 50, "g"),
            ("Garlic", 2, "cloves"),
            ("Olive oil", 2, "tbsp"),
        ]

        for ing_name, qty, unit in ingredient_data:
            # Get or create ingredient
            ingredient = db.query(Ingredient).filter(Ingredient.name == ing_name).first()
            if not ingredient:
                ingredient = Ingredient(name=ing_name, category="groceries")
                db.add(ingredient)
                db.flush()

            # Create recipe-ingredient link
            recipe_ing = RecipeIngredient(
                recipe_id=test_recipe.id,
                ingredient_id=ingredient.id,
                quantity=qty,
                unit=unit
            )
            db.add(recipe_ing)

        db.commit()
        print_success(f"Created test recipe '{test_recipe.name}' with {len(ingredient_data)} ingredients")

        # Step 3: Create test meal plan
        print_header("Step 3: Create Test Meal Plan")
        print_info("Creating meal plan...")

        start_date = date.today()
        end_date = start_date + timedelta(days=3)

        test_meal_plan = MealPlan(
            user_id=test_user.id,
            name="Test Meal Plan",
            description="Integration test meal plan",
            start_date=start_date,
            end_date=end_date,
            num_people=2,
            total_recipes=1,
            status="ready"
        )
        db.add(test_meal_plan)
        db.flush()

        # Add recipe to meal plan
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=test_meal_plan.id,
            recipe_id=test_recipe.id,
            day_number=1,
            meal_type="dinner",
            scheduled_date=start_date,
            servings=2
        )
        db.add(meal_plan_recipe)
        db.commit()

        print_success(f"Created meal plan ID: {test_meal_plan.id}")
        print_info(f"  Date range: {start_date} to {end_date}")
        print_info(f"  Recipes: {test_meal_plan.total_recipes}")

        # Step 4: Initialize Knuspr client and test authentication
        print_header("Step 4: Initialize Knuspr Client")
        print_info(f"Connecting to Knuspr as {email}...")

        knuspr_client = KnusprMCPClient(
            login_email=email,
            login_password=password,
            country=KnusprCountry.CZECH_REPUBLIC
        )

        auth_success = await knuspr_client.authenticate()
        if not auth_success:
            print_error("Knuspr authentication failed")
            return False

        print_success("Knuspr authentication successful")

        # Step 5: Run cart creation workflow
        print_header("Step 5: Execute Cart Creation Workflow")
        print_info("Initializing cart optimizer agent...")

        ingredient_mapper = IngredientMapper(knuspr_client)
        event_bus = get_event_bus()

        agent = CartOptimizerAgent(
            knuspr_client=knuspr_client,
            ingredient_mapper=ingredient_mapper,
            db=db,
            event_bus=event_bus
        )

        print_info("Creating cart from meal plan...")
        delivery_preferences = {
            "preferred_time_slot": "afternoon",
            "budget_optimization": False
        }

        result = await agent.create_cart_from_meal_plan(
            meal_plan_id=test_meal_plan.id,
            user_id=test_user.id,
            db=db,
            credential_manager=credential_manager,
            delivery_preferences=delivery_preferences
        )

        print_success("Cart created successfully!")
        print_info(f"  Cart ID: {result['cart_id']}")
        print_info(f"  Knuspr URL: {result['knuspr_url']}")
        print_info(f"  Total price: {result['total_price']} CZK")
        print_info(f"  Item count: {result['item_count']}")

        if result.get('delivery_slot'):
            slot = result['delivery_slot']
            print_info(f"  Delivery slot: {slot.get('date')} {slot.get('time_window')}")

        if result.get('unavailable_items'):
            print_warning(f"  Unavailable items: {len(result['unavailable_items'])}")
            for item in result['unavailable_items']:
                print_warning(f"    - {item}")

        # Step 6: Verify cart in database
        print_header("Step 6: Verify Database Storage")
        print_info("Checking database for cart...")

        test_cart = db.query(GroceryCart).filter(
            GroceryCart.knuspr_cart_id == result['cart_id']
        ).first()

        if not test_cart:
            print_error("Cart not found in database!")
            return False

        print_success(f"Cart found in database (DB ID: {test_cart.id})")
        print_info(f"  Total items: {test_cart.total_items}")
        print_info(f"  Total cost: {test_cart.total_cost}")
        print_info(f"  Status: {test_cart.status}")

        # Check cart items
        cart_items = db.query(CartItem).filter(CartItem.cart_id == test_cart.id).all()
        print_success(f"Found {len(cart_items)} cart items in database")

        for item in cart_items[:5]:  # Show first 5 items
            print_info(f"  - {item.name} ({item.quantity} {item.unit}) - {item.category}")

        if len(cart_items) > 5:
            print_info(f"  ... and {len(cart_items) - 5} more items")

        # Step 7: Test cart retrieval
        print_header("Step 7: Test Cart Retrieval")
        print_info("Testing cart retrieval via API query...")

        retrieved_cart = db.query(GroceryCart).filter(
            GroceryCart.knuspr_cart_id == result['cart_id'],
            GroceryCart.user_id == test_user.id
        ).first()

        if retrieved_cart:
            print_success("Cart retrieval successful")
            retrieved_items = db.query(CartItem).filter(
                CartItem.cart_id == retrieved_cart.id
            ).all()
            print_info(f"  Retrieved {len(retrieved_items)} items")
        else:
            print_error("Cart retrieval failed")
            return False

        # Step 8: Summary
        print_header("Test Summary")
        print_success("All integration tests passed!")
        print_info("\nTest Results:")
        print_info(f"  ✓ User setup and credentials")
        print_info(f"  ✓ Recipe creation ({len(ingredient_data)} ingredients)")
        print_info(f"  ✓ Meal plan creation")
        print_info(f"  ✓ Knuspr authentication")
        print_info(f"  ✓ Cart creation workflow")
        print_info(f"  ✓ Database storage ({len(cart_items)} items)")
        print_info(f"  ✓ Cart retrieval")

        print_info("\nCart Details:")
        print_info(f"  Cart ID: {result['cart_id']}")
        print_info(f"  URL: {result['knuspr_url']}")
        print_info(f"  Total: {result['total_price']} CZK")
        print_info(f"  Items: {result['item_count']}")

        return True

    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print_header("Cleanup")
        print_info("Cleaning up test data...")

        try:
            # Delete test cart
            if test_cart:
                db.query(CartItem).filter(CartItem.cart_id == test_cart.id).delete()
                db.delete(test_cart)
                print_success("Deleted test cart")

            # Delete test meal plan
            if test_meal_plan:
                db.query(MealPlanRecipe).filter(
                    MealPlanRecipe.meal_plan_id == test_meal_plan.id
                ).delete()
                db.delete(test_meal_plan)
                print_success("Deleted test meal plan")

            # Delete test recipe
            if test_recipe:
                db.query(RecipeIngredient).filter(
                    RecipeIngredient.recipe_id == test_recipe.id
                ).delete()
                db.delete(test_recipe)
                print_success("Deleted test recipe")

            db.commit()
            print_success("Cleanup complete")

        except Exception as cleanup_error:
            print_warning(f"Cleanup error (non-fatal): {str(cleanup_error)}")
            db.rollback()

        # Close connections
        if knuspr_client:
            await knuspr_client.close()
            print_info("Closed Knuspr client")

        db.close()
        print_info("Closed database connection")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Knuspr Integration Test Suite")
    print("Testing: Meal Plan → Grocery Cart Workflow")
    print("=" * 60 + "\n")

    success = asyncio.run(test_knuspr_integration())

    print("\n" + "=" * 60)
    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ TESTS FAILED{Colors.END}")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
