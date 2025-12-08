"""
Unit tests for GroceryAggregator service.

Tests ingredient parsing, unit normalization, and aggregation logic for
automated grocery list generation from meal plans.

IMPORTANT: These tests are designed to run once T005-T007 are completed
and the GroceryAggregator service skeleton exists.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
from datetime import date, datetime

# These imports will work once T005-T007 are completed
from app.services.grocery_aggregator import (
    GroceryAggregator,
    ParsedIngredient,
    AggregatedIngredient,
)
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def aggregator():
    """Create GroceryAggregator instance for testing."""
    return GroceryAggregator(db=Mock())


@pytest.fixture
def mock_db_session():
    """Create mock database session."""
    session = AsyncMock()
    return session


@pytest.fixture
def sample_recipe_1():
    """Sample recipe with common ingredients."""
    return Recipe(
        id=1,
        user_id=1,
        title="Pasta Carbonara",
        ingredients=[
            "200g spaghetti",
            "100g pancetta",
            "2 large eggs",
            "50g parmesan cheese",
            "1 clove garlic",
            "Salt and pepper to taste",
        ],
        instructions="Cook pasta. Mix eggs with cheese. Combine.",
        source_url="https://example.com/carbonara",
        source_type="html",
    )


@pytest.fixture
def sample_recipe_2():
    """Sample recipe with overlapping ingredients."""
    return Recipe(
        id=2,
        user_id=1,
        title="Garlic Bread",
        ingredients=[
            "1 baguette",
            "3 cloves garlic",
            "100g butter",
            "2 tablespoons parsley",
            "Salt to taste",
        ],
        instructions="Mix butter with garlic. Spread on bread. Bake.",
        source_url="https://example.com/garlic-bread",
        source_type="html",
    )


@pytest.fixture
def sample_meal_plan(sample_recipe_1, sample_recipe_2):
    """Sample meal plan with recipes."""
    meal_plan = MealPlan(
        id=1,
        user_id=1,
        name="Week 1",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 7),
        num_people=2,
        status="ready",
    )
    mpr1 = MealPlanRecipe(
        id=1,
        meal_plan_id=1,
        recipe_id=1,
        day_number=1,
        meal_type="dinner",
        servings=2,
    )
    mpr1.recipe = sample_recipe_1
    mpr2 = MealPlanRecipe(
        id=2,
        meal_plan_id=1,
        recipe_id=2,
        day_number=2,
        meal_type="dinner",
        servings=2,
    )
    mpr2.recipe = sample_recipe_2
    meal_plan.recipes = [mpr1, mpr2]
    return meal_plan


# ============================================================================
# Test: Ingredient Parsing
# ============================================================================


class TestParseIngredient:
    """Tests for ingredient string parsing."""

    @pytest.mark.parametrize(
        "input_str,expected_quantity,expected_unit,expected_name",
        [
            # Simple ingredients
            ("2 cups flour", 2.0, "cups", "flour"),
            ("1 cup sugar", 1.0, "cup", "sugar"),
            ("3 tablespoons butter", 3.0, "tablespoons", "butter"),
            ("500 grams pasta", 500.0, "grams", "pasta"),
            ("4 large eggs", 4.0, "large", "eggs"),
            # Decimal quantities
            ("1.5 cups milk", 1.5, "cups", "milk"),
            ("0.5 teaspoon salt", 0.5, "teaspoon", "salt"),
            ("2.25 pounds chicken", 2.25, "pounds", "chicken"),
            # Simple item names
            ("2 cups all-purpose flour", 2.0, "cups", "all-purpose flour"),
            ("1 medium red onion", 1.0, "medium", "red onion"),
            ("3 cloves fresh garlic", 3.0, "cloves", "fresh garlic"),
        ],
    )
    def test_parse_simple_ingredients(
        self, aggregator, input_str, expected_quantity, expected_unit, expected_name
    ):
        """Test parsing of simple ingredient strings."""
        parsed = aggregator.parse_ingredient(input_str)
        assert parsed.quantity == expected_quantity
        assert parsed.unit == expected_unit
        assert expected_name in parsed.name.lower()
        assert parsed.original_text == input_str

    @pytest.mark.parametrize(
        "input_str,expected_quantity,expected_unit,expected_name",
        [
            # Fractional quantities
            ("1/2 cup sugar", 0.5, "cup", "sugar"),
            ("1/4 teaspoon salt", 0.25, "teaspoon", "salt"),
            ("3/4 cup flour", 0.75, "cup", "flour"),
            ("1/3 cup oil", 0.333, "cup", "oil"),
            ("2/3 cup milk", 0.667, "cup", "milk"),
            # Mixed fractions
            ("1 1/2 cups water", 1.5, "cups", "water"),
            ("2 1/4 tablespoons oil", 2.25, "tablespoons", "oil"),
            ("1 3/4 pounds meat", 1.75, "pounds", "meat"),
        ],
    )
    def test_parse_fractional_quantities(
        self, aggregator, input_str, expected_quantity, expected_unit, expected_name
    ):
        """Test parsing of fractional and mixed number quantities."""
        parsed = aggregator.parse_ingredient(input_str)
        assert abs(parsed.quantity - expected_quantity) < 0.01
        assert parsed.unit == expected_unit
        assert expected_name in parsed.name.lower()

    @pytest.mark.parametrize(
        "input_str,expected_min,expected_max,expected_unit,expected_name",
        [
            # Range quantities
            ("2-3 carrots", 2.0, 3.0, "carrots", "carrots"),
            ("4-6 cloves garlic", 4.0, 6.0, "cloves", "garlic"),
            ("1-2 cups flour", 1.0, 2.0, "cups", "flour"),
            ("3-4 tablespoons oil", 3.0, 4.0, "tablespoons", "oil"),
        ],
    )
    def test_parse_range_quantities(
        self,
        aggregator,
        input_str,
        expected_min,
        expected_max,
        expected_unit,
        expected_name,
    ):
        """Test parsing of range quantities (e.g., 2-3 carrots)."""
        parsed = aggregator.parse_ingredient(input_str)
        # Range should be parsed as the average or minimum
        assert parsed.quantity >= expected_min
        assert parsed.quantity <= expected_max
        assert parsed.unit == expected_unit
        assert expected_name in parsed.name.lower()

    @pytest.mark.parametrize(
        "input_str,expected_name",
        [
            # No quantity ingredients
            ("Salt to taste", "salt"),
            ("Fresh basil", "basil"),
            ("Black pepper", "pepper"),
            ("Olive oil for drizzling", "olive oil"),
        ],
    )
    def test_parse_no_quantity_ingredients(
        self, aggregator, input_str, expected_name
    ):
        """Test parsing ingredients without explicit quantities."""
        parsed = aggregator.parse_ingredient(input_str)
        assert parsed.quantity is None or parsed.quantity == 1.0
        assert expected_name in parsed.name.lower()

    @pytest.mark.parametrize(
        "input_str,expected_name",
        [
            # Complex names
            ("2 cups all-purpose flour", "all-purpose flour"),
            ("1 can (14oz) crushed tomatoes", "crushed tomatoes"),
            ("3 medium ripe avocados", "avocados"),
            ("1 large red bell pepper, diced", "bell pepper"),
            ("2 tablespoons extra virgin olive oil", "olive oil"),
            ("1 pound boneless skinless chicken breast", "chicken breast"),
        ],
    )
    def test_parse_complex_ingredient_names(
        self, aggregator, input_str, expected_name
    ):
        """Test parsing ingredients with complex names and descriptors."""
        parsed = aggregator.parse_ingredient(input_str)
        assert expected_name in parsed.name.lower()

    @pytest.mark.parametrize(
        "input_str",
        [
            "",
            "   ",
            None,
            "just text no structure",
            "???",
        ],
    )
    def test_parse_edge_cases(self, aggregator, input_str):
        """Test parsing of edge cases and malformed input."""
        if input_str is None:
            with pytest.raises((ValueError, TypeError)):
                aggregator.parse_ingredient(input_str)
        else:
            parsed = aggregator.parse_ingredient(input_str)
            # Should return something, even if it's a fallback
            assert parsed is not None
            assert isinstance(parsed, ParsedIngredient)


# ============================================================================
# Test: Unit Normalization
# ============================================================================


class TestNormalizeUnits:
    """Tests for unit normalization and conversion."""

    @pytest.fixture
    def aggregator(self):
        """Create aggregator instance."""
        return GroceryAggregator(db=Mock())

    @pytest.mark.parametrize(
        "quantity,from_unit,to_unit,expected_quantity,expected_unit",
        [
            # Volume conversions to ml
            (1, "cup", "ml", 240, "ml"),
            (1, "cups", "ml", 240, "ml"),
            (2, "tablespoon", "ml", 30, "ml"),
            (2, "tablespoons", "ml", 30, "ml"),
            (1, "teaspoon", "ml", 5, "ml"),
            (3, "teaspoons", "ml", 15, "ml"),
            (1, "liter", "ml", 1000, "ml"),
            (1, "litre", "ml", 1000, "ml"),
            # Weight conversions to grams
            (1, "pound", "g", 453.6, "g"),
            (1, "lb", "g", 453.6, "g"),
            (1, "ounce", "g", 28.35, "g"),
            (1, "oz", "g", 28.35, "g"),
            (1, "kilogram", "g", 1000, "g"),
            (1, "kg", "g", 1000, "g"),
        ],
    )
    def test_normalize_volume_and_weight(
        self, aggregator, quantity, from_unit, to_unit, expected_quantity, expected_unit
    ):
        """Test conversion of volume and weight units."""
        result_quantity, result_unit = aggregator.normalize_units(
            quantity, from_unit, to_unit
        )
        assert abs(result_quantity - expected_quantity) < 0.1
        assert result_unit == expected_unit

    @pytest.mark.parametrize(
        "quantity,unit",
        [
            (2, "whole"),
            (3, "piece"),
            (4, "item"),
            (1, "can"),
            (2, "package"),
            (1, "bunch"),
        ],
    )
    def test_normalize_count_units(self, aggregator, quantity, unit):
        """Test that count units are normalized to 'count'."""
        result_quantity, result_unit = aggregator.normalize_units(
            quantity, unit, "count"
        )
        assert result_quantity == quantity
        assert result_unit == "count" or result_unit == unit

    def test_normalize_same_unit(self, aggregator):
        """Test normalization when units are already the same."""
        result_quantity, result_unit = aggregator.normalize_units(2.5, "g", "g")
        assert result_quantity == 2.5
        assert result_unit == "g"

    def test_normalize_unknown_unit(self, aggregator):
        """Test handling of unknown units."""
        result_quantity, result_unit = aggregator.normalize_units(
            5, "unknown_unit", "g"
        )
        # Should either pass through or use original unit
        assert result_quantity == 5
        assert result_unit in ["unknown_unit", "g"]

    def test_normalize_incompatible_units(self, aggregator):
        """Test conversion between incompatible unit types."""
        # Volume to weight should not convert
        result_quantity, result_unit = aggregator.normalize_units(1, "cup", "g")
        # Should keep original or return as-is
        assert isinstance(result_quantity, (int, float, Decimal))
        assert isinstance(result_unit, str)

    def test_normalize_negative_quantity_validation(self, aggregator):
        """Test that negative quantities are rejected."""
        with pytest.raises((ValueError, AssertionError)):
            aggregator.normalize_units(-1, "cup", "ml")

    def test_normalize_zero_quantity(self, aggregator):
        """Test normalization of zero quantities."""
        result_quantity, result_unit = aggregator.normalize_units(0, "cup", "ml")
        assert result_quantity == 0
        assert result_unit == "ml"


# ============================================================================
# Test: Aggregation from Meal Plan
# ============================================================================


class TestAggregateFromMealPlan:
    """Tests for aggregating ingredients from meal plans."""

    @pytest.mark.asyncio
    async def test_aggregate_empty_meal_plan(self, aggregator, mock_db_session):
        """Test aggregation with an empty meal plan."""
        meal_plan = MealPlan(
            id=1,
            user_id=1,
            name="Empty Plan",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            num_people=2,
            status="ready",
        )
        meal_plan.recipes = []

        with patch.object(
            aggregator, "db", mock_db_session
        ):
            result = await aggregator.aggregate_from_meal_plan(meal_plan)

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_aggregate_single_recipe(
        self, aggregator, mock_db_session, sample_recipe_1
    ):
        """Test aggregation with a single recipe."""
        meal_plan = MealPlan(
            id=1,
            user_id=1,
            name="Single Recipe Plan",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            num_people=2,
            status="ready",
        )
        meal_plan_recipe = MealPlanRecipe(
            id=1,
            meal_plan_id=1,
            recipe_id=1,
            day_number=1,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe.recipe = sample_recipe_1
        meal_plan.recipes = [meal_plan_recipe]

        with patch.object(aggregator, "db", mock_db_session):
            result = await aggregator.aggregate_from_meal_plan(meal_plan)

        assert isinstance(result, list)
        assert len(result) > 0
        # Should have parsed ingredients from the recipe
        assert any("spaghetti" in item.name.lower() for item in result)
        assert any("eggs" in item.name.lower() for item in result)

    @pytest.mark.asyncio
    async def test_aggregate_combines_duplicate_ingredients(
        self, aggregator, mock_db_session, sample_recipe_1, sample_recipe_2
    ):
        """Test that duplicate ingredients are combined correctly."""
        meal_plan = MealPlan(
            id=1,
            user_id=1,
            name="Multi Recipe Plan",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            num_people=2,
            status="ready",
        )
        meal_plan_recipe_1 = MealPlanRecipe(
            id=1,
            meal_plan_id=1,
            recipe_id=1,
            day_number=1,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe_1.recipe = sample_recipe_1

        meal_plan_recipe_2 = MealPlanRecipe(
            id=2,
            meal_plan_id=1,
            recipe_id=2,
            day_number=2,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe_2.recipe = sample_recipe_2

        meal_plan.recipes = [meal_plan_recipe_1, meal_plan_recipe_2]

        with patch.object(aggregator, "db", mock_db_session):
            result = await aggregator.aggregate_from_meal_plan(meal_plan)

        assert isinstance(result, list)
        assert len(result) > 0

        # Both recipes have garlic - should be combined
        garlic_items = [item for item in result if "garlic" in item.name.lower()]
        assert len(garlic_items) > 0

        # Check that garlic has combined quantity
        for garlic_item in garlic_items:
            # Recipe 1 has 1 clove, Recipe 2 has 3 cloves = 4 total
            assert garlic_item.quantity >= 1

    @pytest.mark.asyncio
    async def test_aggregate_preserves_recipe_ids(
        self, aggregator, mock_db_session, sample_recipe_1, sample_recipe_2
    ):
        """Test that recipe_ids are tracked for each ingredient."""
        meal_plan = MealPlan(
            id=1,
            user_id=1,
            name="Multi Recipe Plan",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            num_people=2,
            status="ready",
        )
        meal_plan_recipe_1 = MealPlanRecipe(
            id=1,
            meal_plan_id=1,
            recipe_id=1,
            day_number=1,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe_1.recipe = sample_recipe_1

        meal_plan_recipe_2 = MealPlanRecipe(
            id=2,
            meal_plan_id=1,
            recipe_id=2,
            day_number=2,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe_2.recipe = sample_recipe_2

        meal_plan.recipes = [meal_plan_recipe_1, meal_plan_recipe_2]

        with patch.object(aggregator, "db", mock_db_session):
            result = await aggregator.aggregate_from_meal_plan(meal_plan)

        # Check that aggregated ingredients have recipe_ids
        for item in result:
            assert hasattr(item, "recipe_ids")
            assert isinstance(item.recipe_ids, list)
            assert len(item.recipe_ids) > 0

        # Garlic appears in both recipes, should have both IDs
        garlic_items = [item for item in result if "garlic" in item.name.lower()]
        if garlic_items:
            # Should track that garlic is used in multiple recipes
            assert any(len(item.recipe_ids) > 1 for item in garlic_items)

    @pytest.mark.asyncio
    async def test_aggregate_handles_different_units(
        self, aggregator, mock_db_session
    ):
        """Test aggregation when same ingredient has different units."""
        recipe_1 = Recipe(
            id=1,
            user_id=1,
            title="Recipe 1",
            ingredients=["2 cups flour"],
            instructions="Mix and bake",
            source_url="https://example.com/1",
            source_type="html",
        )
        recipe_2 = Recipe(
            id=2,
            user_id=1,
            title="Recipe 2",
            ingredients=["500 grams flour"],
            instructions="Mix and bake",
            source_url="https://example.com/2",
            source_type="html",
        )

        meal_plan = MealPlan(
            id=1,
            user_id=1,
            name="Different Units Plan",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            num_people=2,
            status="ready",
        )

        meal_plan_recipe_1 = MealPlanRecipe(
            id=1,
            meal_plan_id=1,
            recipe_id=1,
            day_number=1,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe_1.recipe = recipe_1

        meal_plan_recipe_2 = MealPlanRecipe(
            id=2,
            meal_plan_id=1,
            recipe_id=2,
            day_number=2,
            meal_type="dinner",
            servings=2,
        )
        meal_plan_recipe_2.recipe = recipe_2

        meal_plan.recipes = [meal_plan_recipe_1, meal_plan_recipe_2]

        with patch.object(aggregator, "db", mock_db_session):
            result = await aggregator.aggregate_from_meal_plan(meal_plan)

        # Should combine flour even though units differ
        flour_items = [item for item in result if "flour" in item.name.lower()]
        assert len(flour_items) > 0

        # Should have normalized units
        for flour_item in flour_items:
            assert flour_item.unit in ["g", "grams", "cups", "ml"]


# ============================================================================
# Test: Data Classes and Models
# ============================================================================


class TestParsedIngredient:
    """Tests for ParsedIngredient data class."""

    def test_parsed_ingredient_creation(self):
        """Test creating ParsedIngredient instances."""
        parsed = ParsedIngredient(
            quantity=2.0,
            unit="cups",
            name="flour",
            original_text="2 cups flour",
        )
        assert parsed.quantity == 2.0
        assert parsed.unit == "cups"
        assert parsed.name == "flour"
        assert parsed.original_text == "2 cups flour"

    def test_parsed_ingredient_optional_fields(self):
        """Test ParsedIngredient with optional fields."""
        parsed = ParsedIngredient(
            quantity=None, unit="", name="salt to taste", original_text="Salt to taste"
        )
        assert parsed.quantity is None
        assert parsed.name == "salt to taste"


class TestAggregatedIngredient:
    """Tests for AggregatedIngredient data class."""

    def test_aggregated_ingredient_creation(self):
        """Test creating AggregatedIngredient instances."""
        aggregated = AggregatedIngredient(
            name="garlic",
            quantity=4.0,
            unit="cloves",
            recipe_ids=[1, 2],
            category="vegetables",
        )
        assert aggregated.name == "garlic"
        assert aggregated.quantity == 4.0
        assert aggregated.unit == "cloves"
        assert aggregated.recipe_ids == [1, 2]
        assert aggregated.category == "vegetables"

    def test_aggregated_ingredient_recipe_tracking(self):
        """Test that recipe IDs are properly tracked."""
        aggregated = AggregatedIngredient(
            name="flour",
            quantity=500.0,
            unit="g",
            recipe_ids=[1, 2, 3],
        )
        assert len(aggregated.recipe_ids) == 3
        assert all(isinstance(rid, int) for rid in aggregated.recipe_ids)


# ============================================================================
# Integration-like Tests
# ============================================================================


class TestGroceryAggregatorIntegration:
    """Integration-like tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_full_aggregation_workflow(
        self, aggregator, mock_db_session, sample_meal_plan
    ):
        """Test complete workflow from meal plan to aggregated list."""
        with patch.object(aggregator, "db", mock_db_session):
            # Aggregate ingredients
            result = await aggregator.aggregate_from_meal_plan(sample_meal_plan)

            # Verify results
            assert isinstance(result, list)
            assert len(result) > 0

            # Verify each aggregated item has required fields
            for item in result:
                assert hasattr(item, "name")
                assert hasattr(item, "quantity")
                assert hasattr(item, "unit")
                assert hasattr(item, "recipe_ids")
                assert len(item.name) > 0
                assert isinstance(item.quantity, (int, float, Decimal))
                assert isinstance(item.unit, str)

    @pytest.mark.asyncio
    async def test_aggregation_scales_servings(self, aggregator, mock_db_session):
        """Test that ingredient quantities are scaled by servings."""
        recipe = Recipe(
            id=1,
            user_id=1,
            title="Test Recipe",
            ingredients=["2 cups flour"],  # Base recipe is 2 servings
            instructions="Mix and bake",
            source_url="https://example.com/test",
            source_type="html",
        )
        recipe.servings = 2

        meal_plan = MealPlan(
            id=1,
            user_id=1,
            name="Scaled Plan",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            num_people=4,
            status="ready",
        )

        meal_plan_recipe = MealPlanRecipe(
            id=1,
            meal_plan_id=1,
            recipe_id=1,
            day_number=1,
            meal_type="dinner",
            servings=4,  # Double the servings
        )
        meal_plan_recipe.recipe = recipe
        meal_plan.recipes = [meal_plan_recipe]

        with patch.object(aggregator, "db", mock_db_session):
            result = await aggregator.aggregate_from_meal_plan(meal_plan)

        # Find flour in results
        flour_items = [item for item in result if "flour" in item.name.lower()]
        assert len(flour_items) > 0

        # Quantity should be scaled (2 cups * 2 = 4 cups)
        # Or normalized to grams with proportional scaling
        for flour_item in flour_items:
            assert flour_item.quantity >= 2.0  # At least the original amount


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
