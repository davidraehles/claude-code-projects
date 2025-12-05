"""
Query Performance Testing Script

Measures database query counts and performance before/after optimizations.
Helps identify N+1 query problems and validate eager loading improvements.
"""

import sys
import os
import logging
from datetime import date, timedelta
from sqlalchemy import event, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models.user import User
from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.services.grocery_aggregator import GroceryAggregator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Query counter
query_count = 0
queries = []


def reset_query_counter():
    """Reset query counter and list."""
    global query_count, queries
    query_count = 0
    queries = []


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Count all queries executed."""
    global query_count, queries
    query_count += 1
    # Store query for debugging
    queries.append(statement[:200])  # First 200 chars


def setup_test_database():
    """Create test database with sample data."""
    # Use SQLite for testing
    engine = create_engine('sqlite:///./test_performance.db', echo=False)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test user
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed",
        country="DE"
    )
    session.add(user)
    session.flush()

    # Create test recipes
    recipes = []
    for i in range(10):
        recipe = Recipe(
            id=i + 1,
            user_id=1,
            title=f"Test Recipe {i + 1}",
            ingredients=[
                f"2 cups flour",
                f"1 cup sugar",
                f"3 eggs",
                f"1 tsp vanilla",
                f"1/2 cup butter"
            ],
            instructions=f"Instructions for recipe {i + 1}",
            source_url=f"https://example.com/recipe-{i + 1}",
            source_type="html"
        )
        recipe.servings = 4
        recipes.append(recipe)
        session.add(recipe)

    session.flush()

    # Create meal plan
    meal_plan = MealPlan(
        id=1,
        user_id=1,
        name="Test Week",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=6),
        num_people=2,
        status="ready",
        total_recipes=10
    )
    session.add(meal_plan)
    session.flush()

    # Add recipes to meal plan
    meal_types = ["breakfast", "lunch", "dinner"]
    for day in range(1, 8):
        for idx, meal_type in enumerate(meal_types):
            if (day - 1) * 3 + idx < 10:  # Use up to 10 recipes
                mpr = MealPlanRecipe(
                    meal_plan_id=1,
                    recipe_id=(day - 1) * 3 + idx + 1,
                    day_number=day,
                    meal_type=meal_type,
                    servings=2
                )
                session.add(mpr)

    session.commit()
    session.close()

    return engine


def test_grocery_aggregator_sync(engine):
    """Test synchronous grocery aggregator query count."""
    logger.info("\n" + "="*80)
    logger.info("Testing SYNC GroceryAggregator.aggregate_from_meal_plan()")
    logger.info("="*80)

    Session = sessionmaker(bind=engine)
    session = Session()

    aggregator = GroceryAggregator(session)

    # Reset counter
    reset_query_counter()

    # Run aggregation
    result = aggregator.aggregate_from_meal_plan_sync(meal_plan_id=1)

    session.close()

    logger.info(f"Total queries executed: {query_count}")
    logger.info(f"Aggregated ingredients: {len(result)}")

    # Show first few queries
    logger.info("\nFirst 5 queries:")
    for i, q in enumerate(queries[:5], 1):
        logger.info(f"  {i}. {q}")

    return query_count


def test_meal_plan_query_without_eager_loading(engine):
    """Test meal plan query WITHOUT eager loading (baseline)."""
    logger.info("\n" + "="*80)
    logger.info("Testing Meal Plan Query WITHOUT Eager Loading")
    logger.info("="*80)

    Session = sessionmaker(bind=engine)
    session = Session()

    reset_query_counter()

    # Query meal plan (no eager loading)
    meal_plan = session.query(MealPlan).filter(MealPlan.id == 1).first()

    # Access recipes (triggers N+1)
    for mpr in meal_plan.recipes:
        # Access recipe (triggers additional query per recipe)
        _ = mpr.recipe.title
        _ = mpr.recipe.ingredients

    session.close()

    logger.info(f"Total queries executed: {query_count}")
    logger.info("Expected: 1 (meal plan) + 1 (recipes join table) + N (recipe details) = N+2 queries")

    return query_count


def test_meal_plan_query_with_eager_loading(engine):
    """Test meal plan query WITH eager loading (optimized)."""
    logger.info("\n" + "="*80)
    logger.info("Testing Meal Plan Query WITH Eager Loading")
    logger.info("="*80)

    from sqlalchemy.orm import selectinload

    Session = sessionmaker(bind=engine)
    session = Session()

    reset_query_counter()

    # Query meal plan WITH eager loading
    meal_plan = (
        session.query(MealPlan)
        .options(
            selectinload(MealPlan.recipes)
            .selectinload(MealPlanRecipe.recipe)
        )
        .filter(MealPlan.id == 1)
        .first()
    )

    # Access recipes (already loaded, no additional queries)
    for mpr in meal_plan.recipes:
        _ = mpr.recipe.title
        _ = mpr.recipe.ingredients

    session.close()

    logger.info(f"Total queries executed: {query_count}")
    logger.info("Expected: 1 (meal plan) + 1 (meal_plan_recipes) + 1 (recipes) = 3 queries")

    return query_count


def test_grocery_cart_generation_without_optimization(engine):
    """Test grocery cart generation WITHOUT optimization."""
    logger.info("\n" + "="*80)
    logger.info("Testing Grocery Cart Generation WITHOUT Optimization")
    logger.info("="*80)

    Session = sessionmaker(bind=engine)
    session = Session()

    reset_query_counter()

    # Simulating the current meal_plans.py endpoint logic
    meal_plan = session.query(MealPlan).filter(MealPlan.id == 1).first()

    # Get all recipes (N+1 problem)
    meal_plan_recipes = (
        session.query(MealPlanRecipe)
        .filter(MealPlanRecipe.meal_plan_id == 1)
        .all()
    )

    # Iterate and access recipe data (triggers queries)
    for mpr in meal_plan_recipes:
        if mpr.recipe and mpr.recipe.ingredients:
            _ = mpr.recipe.title
            for ingredient in mpr.recipe.ingredients:
                pass

    session.close()

    logger.info(f"Total queries executed: {query_count}")
    logger.info("Expected: 1 (meal plan) + 1 (meal_plan_recipes) + N (recipes) = N+2 queries")

    return query_count


def test_grocery_cart_generation_with_optimization(engine):
    """Test grocery cart generation WITH optimization."""
    logger.info("\n" + "="*80)
    logger.info("Testing Grocery Cart Generation WITH Optimization")
    logger.info("="*80)

    from sqlalchemy.orm import selectinload

    Session = sessionmaker(bind=engine)
    session = Session()

    reset_query_counter()

    # Optimized query with eager loading
    meal_plan = (
        session.query(MealPlan)
        .options(
            selectinload(MealPlan.recipes)
            .selectinload(MealPlanRecipe.recipe)
        )
        .filter(MealPlan.id == 1)
        .first()
    )

    # Access recipes (already loaded)
    for mpr in meal_plan.recipes:
        if mpr.recipe and mpr.recipe.ingredients:
            _ = mpr.recipe.title
            for ingredient in mpr.recipe.ingredients:
                pass

    session.close()

    logger.info(f"Total queries executed: {query_count}")
    logger.info("Expected: 1 (meal plan) + 1 (meal_plan_recipes) + 1 (recipes) = 3 queries")

    return query_count


def main():
    """Run all performance tests."""
    logger.info("Setting up test database...")
    engine = setup_test_database()

    # Run tests
    results = {}

    # Test 1: GroceryAggregator (already optimized)
    results['aggregator_sync'] = test_grocery_aggregator_sync(engine)

    # Test 2: Meal plan query comparison
    results['meal_plan_no_eager'] = test_meal_plan_query_without_eager_loading(engine)
    results['meal_plan_with_eager'] = test_meal_plan_query_with_eager_loading(engine)

    # Test 3: Grocery cart generation comparison
    results['cart_gen_no_opt'] = test_grocery_cart_generation_without_optimization(engine)
    results['cart_gen_with_opt'] = test_grocery_cart_generation_with_optimization(engine)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("PERFORMANCE SUMMARY")
    logger.info("="*80)
    logger.info(f"\n1. GroceryAggregator (sync):")
    logger.info(f"   Queries: {results['aggregator_sync']}")
    logger.info(f"   Status: Already optimized with selectinload()")

    logger.info(f"\n2. Meal Plan Query:")
    logger.info(f"   Without eager loading: {results['meal_plan_no_eager']} queries")
    logger.info(f"   With eager loading: {results['meal_plan_with_eager']} queries")
    improvement_pct = ((results['meal_plan_no_eager'] - results['meal_plan_with_eager']) /
                      results['meal_plan_no_eager'] * 100)
    logger.info(f"   Improvement: {improvement_pct:.1f}% reduction")

    logger.info(f"\n3. Grocery Cart Generation:")
    logger.info(f"   Without optimization: {results['cart_gen_no_opt']} queries")
    logger.info(f"   With optimization: {results['cart_gen_with_opt']} queries")
    improvement_pct = ((results['cart_gen_no_opt'] - results['cart_gen_with_opt']) /
                      results['cart_gen_no_opt'] * 100)
    logger.info(f"   Improvement: {improvement_pct:.1f}% reduction")

    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS:")
    logger.info("="*80)
    logger.info("1. Add eager loading to meal_plans.py endpoints")
    logger.info("2. Add eager loading to grocery cart endpoints")
    logger.info("3. Consider adding indexes on foreign keys")
    logger.info("4. Use joinedload() for many-to-one relationships")
    logger.info("5. Use selectinload() for one-to-many relationships")

    # Cleanup
    os.remove('./test_performance.db')
    logger.info("\nTest database cleaned up.")


if __name__ == "__main__":
    main()
