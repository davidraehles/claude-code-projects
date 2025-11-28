"""
Tests for enhanced meal planning features.

Tests the new dietary restriction filtering, recipe variety history,
and improved nutrition calculation features.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan, MealPlanRecipe
from app.agents.meal_architect import MealArchitectAgent


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test_meal_plans_enhanced.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create database session."""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
        country="DE"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_recipe(db_session, user_id, title, ingredients, dietary_tags=None, nutrition=None):
    """Helper function to create a test recipe."""
    recipe = Recipe(
        user_id=user_id,
        title=title,
        ingredients=ingredients,
        instructions=f"Cook {title.lower()}",
        prep_time=10,
        cook_time=20,
        servings=2,
        dietary_tags=dietary_tags,
        nutrition=nutrition,
        source_url=f"https://example.com/recipe-{title.replace(' ', '-').lower()}",
        source_type="html"
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe


class TestDietaryRestrictionFiltering:
    """Test suite for dietary restriction filtering."""

    def test_filter_vegan_recipes(self, db_session, test_user):
        """Test filtering vegan recipes using dietary tags."""
        # Create recipes with dietary tags
        vegan_recipe = create_recipe(
            db_session, test_user.id, "Vegan Buddha Bowl",
            ["quinoa", "chickpeas", "kale", "tahini"],
            dietary_tags=["vegan", "gluten_free"]
        )

        non_vegan_recipe = create_recipe(
            db_session, test_user.id, "Chicken Salad",
            ["chicken breast", "lettuce", "tomatoes"],
            dietary_tags=["gluten_free"]
        )

        # Generate meal plan with vegan restriction
        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=["vegan"],
            excluded_ingredients=None,
            min_recipes=1
        )

        # Should only include vegan recipe
        assert len(candidates) > 0
        recipe_ids = [r.id for r in candidates]
        assert vegan_recipe.id in recipe_ids
        assert non_vegan_recipe.id not in recipe_ids

    def test_filter_vegetarian_recipes_includes_vegan(self, db_session, test_user):
        """Test that vegetarian filter includes vegan recipes."""
        # Create recipes
        vegan_recipe = create_recipe(
            db_session, test_user.id, "Vegan Stir Fry",
            ["tofu", "broccoli", "soy sauce"],
            dietary_tags=["vegan"]
        )

        vegetarian_recipe = create_recipe(
            db_session, test_user.id, "Vegetarian Pizza",
            ["cheese", "tomato sauce", "mushrooms"],
            dietary_tags=["vegetarian"]
        )

        meat_recipe = create_recipe(
            db_session, test_user.id, "Beef Tacos",
            ["beef", "tortillas", "cheese"],
            dietary_tags=[]
        )

        # Generate with vegetarian restriction
        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=["vegetarian"],
            excluded_ingredients=None,
            min_recipes=2
        )

        recipe_ids = [r.id for r in candidates]

        # Should include vegan and vegetarian, exclude meat
        assert vegan_recipe.id in recipe_ids
        assert vegetarian_recipe.id in recipe_ids
        assert meat_recipe.id not in recipe_ids

    def test_filter_gluten_free_recipes(self, db_session, test_user):
        """Test filtering gluten-free recipes."""
        # Create recipes
        gf_recipe = create_recipe(
            db_session, test_user.id, "Rice Bowl",
            ["rice", "vegetables", "soy sauce"],
            dietary_tags=["gluten_free", "vegan"]
        )

        gluten_recipe = create_recipe(
            db_session, test_user.id, "Pasta Carbonara",
            ["pasta", "eggs", "bacon", "cheese"],
            dietary_tags=[]
        )

        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=["gluten_free"],
            excluded_ingredients=None,
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]
        assert gf_recipe.id in recipe_ids
        assert gluten_recipe.id not in recipe_ids

    def test_filter_multiple_dietary_restrictions(self, db_session, test_user):
        """Test filtering with multiple dietary restrictions."""
        # Create recipe matching all restrictions
        matching_recipe = create_recipe(
            db_session, test_user.id, "Quinoa Salad",
            ["quinoa", "vegetables", "olive oil"],
            dietary_tags=["vegan", "gluten_free"]
        )

        # Create recipes matching only one restriction
        vegan_only = create_recipe(
            db_session, test_user.id, "Vegan Bread",
            ["flour", "yeast", "water"],
            dietary_tags=["vegan"]
        )

        gf_only = create_recipe(
            db_session, test_user.id, "GF Chicken",
            ["chicken", "rice"],
            dietary_tags=["gluten_free"]
        )

        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=["vegan", "gluten_free"],
            excluded_ingredients=None,
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]

        # Should only include recipe matching ALL restrictions
        assert matching_recipe.id in recipe_ids
        assert vegan_only.id not in recipe_ids
        assert gf_only.id not in recipe_ids

    def test_fallback_to_ingredient_check(self, db_session, test_user):
        """Test fallback to ingredient checking when no dietary tags."""
        # Create recipe without dietary tags but vegan ingredients
        vegan_ingredients = ["quinoa", "chickpeas", "kale", "olive oil"]
        vegan_recipe = create_recipe(
            db_session, test_user.id, "Healthy Bowl",
            vegan_ingredients,
            dietary_tags=None  # No tags
        )

        # Create recipe with meat (should be filtered)
        meat_ingredients = ["chicken breast", "rice", "vegetables"]
        meat_recipe = create_recipe(
            db_session, test_user.id, "Chicken Rice",
            meat_ingredients,
            dietary_tags=None
        )

        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=["vegan"],
            excluded_ingredients=None,
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]

        # Should filter based on ingredients
        assert vegan_recipe.id in recipe_ids
        assert meat_recipe.id not in recipe_ids


class TestRecipeVarietyHistory:
    """Test suite for recipe variety history tracking."""

    def test_exclude_recently_used_recipes(self, db_session, test_user):
        """Test that recently used recipes are excluded from new meal plans."""
        # Create multiple recipes
        old_recipe = create_recipe(
            db_session, test_user.id, "Old Recipe",
            ["ingredient1", "ingredient2"]
        )

        new_recipe = create_recipe(
            db_session, test_user.id, "New Recipe",
            ["ingredient3", "ingredient4"]
        )

        # Create a recent meal plan with old_recipe
        recent_plan = MealPlan(
            user_id=test_user.id,
            name="Recent Plan",
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=6),
            num_people=2,
            status="ready"
        )
        db_session.add(recent_plan)
        db_session.commit()

        # Add old_recipe to the recent plan
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=recent_plan.id,
            recipe_id=old_recipe.id,
            day_number=1,
            meal_type="dinner",
            scheduled_date=recent_plan.start_date,
            servings=2
        )
        db_session.add(meal_plan_recipe)
        db_session.commit()

        # Get candidate recipes
        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=None,
            excluded_ingredients=None,
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]

        # Should exclude recently used recipe
        assert old_recipe.id not in recipe_ids
        assert new_recipe.id in recipe_ids

    def test_include_recipes_beyond_lookback_period(self, db_session, test_user):
        """Test that recipes beyond lookback period are included."""
        # Create recipe
        recipe = create_recipe(
            db_session, test_user.id, "Old Favorite",
            ["ingredient1", "ingredient2"]
        )

        # Create an old meal plan (15 days ago, beyond 14-day lookback)
        old_plan = MealPlan(
            user_id=test_user.id,
            name="Old Plan",
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() - timedelta(days=19),
            num_people=2,
            status="completed"
        )
        db_session.add(old_plan)
        db_session.commit()

        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=old_plan.id,
            recipe_id=recipe.id,
            day_number=1,
            meal_type="dinner",
            scheduled_date=old_plan.start_date,
            servings=2
        )
        db_session.add(meal_plan_recipe)
        db_session.commit()

        # Get candidate recipes
        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=None,
            excluded_ingredients=None,
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]

        # Should include recipe (beyond lookback period)
        assert recipe.id in recipe_ids


class TestImprovedNutritionCalculation:
    """Test suite for improved nutrition calculation."""

    def test_use_recipe_nutrition_data_when_available(self, db_session, test_user):
        """Test that recipe nutrition data is used when available."""
        recipe = create_recipe(
            db_session, test_user.id, "Test Recipe",
            ["ingredient1"],
            nutrition={"calories": 500}  # 500 cal per serving
        )

        agent = MealArchitectAgent(db_session)

        # Calculate for 2 servings (recipe has 2 servings default)
        calories = agent._calculate_recipe_calories(recipe, servings=2)

        # Should use recipe nutrition data
        assert calories == 500  # 500 * 2 / 2

    def test_intelligent_fallback_with_ingredients(self, db_session, test_user):
        """Test intelligent calorie estimation based on ingredients."""
        recipe = create_recipe(
            db_session, test_user.id, "Complex Recipe",
            ["chicken", "rice", "broccoli", "olive oil", "garlic"],
            nutrition=None  # No nutrition data
        )

        agent = MealArchitectAgent(db_session)

        # Calculate calories
        calories = agent._calculate_recipe_calories(recipe, servings=2)

        # Should estimate based on ingredients
        assert calories is not None
        assert calories > 0

        # Should be within reasonable bounds (300-1000 cal per serving)
        calories_per_serving = calories // 2
        assert 300 <= calories_per_serving <= 1000

    def test_cost_estimation_by_ingredient_category(self, db_session, test_user):
        """Test cost estimation based on ingredient categories."""
        recipe = create_recipe(
            db_session, test_user.id, "Budget Recipe",
            ["rice", "beans", "onion", "tomato"]
        )

        agent = MealArchitectAgent(db_session)

        # Calculate cost
        cost = agent._estimate_recipe_cost(recipe, servings=2)

        # Should estimate cost
        assert cost is not None
        assert cost > 0
        assert isinstance(cost, float)


class TestExcludedIngredients:
    """Test suite for excluded ingredients filtering."""

    def test_exclude_specific_ingredient(self, db_session, test_user):
        """Test excluding recipes with specific ingredients."""
        # Recipe with peanuts
        peanut_recipe = create_recipe(
            db_session, test_user.id, "Peanut Butter Cookies",
            ["peanut butter", "flour", "sugar", "eggs"]
        )

        # Recipe without peanuts
        safe_recipe = create_recipe(
            db_session, test_user.id, "Chocolate Cake",
            ["flour", "sugar", "cocoa", "eggs"]
        )

        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=None,
            excluded_ingredients=["peanut"],
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]

        # Should exclude recipe with peanuts
        assert peanut_recipe.id not in recipe_ids
        assert safe_recipe.id in recipe_ids

    def test_exclude_multiple_ingredients(self, db_session, test_user):
        """Test excluding recipes with multiple excluded ingredients."""
        # Recipe with dairy and eggs
        recipe_with_both = create_recipe(
            db_session, test_user.id, "Custard",
            ["milk", "eggs", "sugar"]
        )

        # Recipe with only dairy
        dairy_recipe = create_recipe(
            db_session, test_user.id, "Cheese Sauce",
            ["cheese", "milk", "butter"]
        )

        # Recipe with neither
        safe_recipe = create_recipe(
            db_session, test_user.id, "Fruit Salad",
            ["apple", "banana", "orange"]
        )

        agent = MealArchitectAgent(db_session)

        candidates = agent._get_candidate_recipes(
            user_id=test_user.id,
            dietary_restrictions=None,
            excluded_ingredients=["milk", "eggs"],
            min_recipes=1
        )

        recipe_ids = [r.id for r in candidates]

        # Should only include safe recipe
        assert recipe_with_both.id not in recipe_ids
        assert dairy_recipe.id not in recipe_ids
        assert safe_recipe.id in recipe_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
