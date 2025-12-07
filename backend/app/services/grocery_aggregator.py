"""
Grocery Aggregator Service for meal plan ingredient aggregation and normalization.

Provides ingredient parsing, unit normalization, and aggregation from meal plans.
"""

import re
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass
from fractions import Fraction

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.models.meal_plan import MealPlan, MealPlanRecipe
from app.models.recipe import Recipe


# Conversion factors to standard units
VOLUME_TO_ML = {
    "cup": 240.0,
    "cups": 240.0,
    "tablespoon": 15.0,
    "tablespoons": 15.0,
    "tbsp": 15.0,
    "teaspoon": 5.0,
    "teaspoons": 5.0,
    "tsp": 5.0,
    "fluid ounce": 29.5735,
    "fluid ounces": 29.5735,
    "fl oz": 29.5735,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "ml": 1.0,
    "liter": 1000.0,
    "liters": 1000.0,
    "litre": 1000.0,
    "litres": 1000.0,
    "l": 1000.0,
    "pint": 473.176,
    "pints": 473.176,
    "quart": 946.353,
    "quarts": 946.353,
    "gallon": 3785.41,
    "gallons": 3785.41,
}

WEIGHT_TO_GRAMS = {
    "pound": 453.592,
    "pounds": 453.592,
    "lb": 453.592,
    "lbs": 453.592,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "oz": 28.3495,
    "gram": 1.0,
    "grams": 1.0,
    "g": 1.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "kg": 1000.0,
    "milligram": 0.001,
    "milligrams": 0.001,
    "mg": 0.001,
}

COUNT_UNITS = {
    "whole",
    "piece",
    "pieces",
    "item",
    "items",
    "count",
    "unit",
    "units",
    "clove",
    "cloves",
    "slice",
    "slices",
    "can",
    "cans",
    "package",
    "packages",
    "pinch",
    "pinches",
    "dash",
    "dashes",
}


@dataclass
class ParsedIngredient:
    """
    Structured representation of a parsed ingredient.

    Attributes:
        quantity: Numeric quantity (1.5, 2.0, etc.)
        unit: Unit of measurement (cups, grams, whole, etc.)
        name: Ingredient name (flour, olive oil, salt, etc.)
        original_text: Original ingredient string
    """

    quantity: Optional[float] = None
    unit: str = ""
    name: str = ""
    original_text: str = ""


@dataclass
class AggregatedIngredient:
    """
    Aggregated ingredient from multiple recipes with source tracking.

    Attributes:
        name: Ingredient name (normalized)
        quantity: Total aggregated quantity
        unit: Normalized unit (ml, g, count)
        recipe_ids: List of recipe IDs that use this ingredient
        original_strings: List of original ingredient strings
        category: Optional category (produce, dairy, pantry, etc.)
    """

    name: str
    quantity: float
    unit: str
    recipe_ids: List[int]
    original_strings: List[str]
    category: Optional[str] = None


class GroceryAggregator:
    """
    Service for aggregating and normalizing grocery lists from meal plans.

    Handles ingredient parsing, unit conversion, and aggregation across multiple
    recipes in a meal plan. Normalizes units to standard measurements for proper
    aggregation and comparison.

    Methods:
        aggregate_from_meal_plan: Generate aggregated grocery list from meal plan
        parse_ingredient: Parse ingredient string into structured data
        normalize_units: Convert to standard units (ml, g, count)
    """

    def __init__(self, db_session: Session | AsyncSession = None, db = None) -> None:
        """
        Initialize the GroceryAggregator service.

        Args:
            db_session: SQLAlchemy database session (sync or async)
            db: Alternative db parameter for test compatibility
        """
        # Support both db_session and db parameter names
        self.db_session = db_session or db
        self.db = self.db_session  # Alias for test compatibility
        self.is_async = isinstance(self.db_session, AsyncSession) if self.db_session else False

    def aggregate_from_meal_plan_sync(
        self, meal_plan_id: int
    ) -> List[AggregatedIngredient]:
        """
        Generate an aggregated grocery list from a meal plan (synchronous version).

        Fetches all recipes in the meal plan, parses ingredients, normalizes units,
        and aggregates quantities by ingredient name.

        Args:
            meal_plan_id: ID of the meal plan to aggregate

        Returns:
            List of AggregatedIngredient objects with normalized quantities and recipe tracking

        Raises:
            ValueError: If meal plan not found or has no recipes
        """
        # Fetch meal plan with recipes using synchronous session
        meal_plan = (
            self.db_session.query(MealPlan)
            .options(selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe))
            .filter(MealPlan.id == meal_plan_id)
            .first()
        )

        if not meal_plan:
            raise ValueError(f"Meal plan {meal_plan_id} not found")

        if not meal_plan.recipes:
            raise ValueError(f"Meal plan {meal_plan_id} has no recipes")

        # Aggregate ingredients
        aggregated: Dict[str, Dict[str, Any]] = {}

        for meal_plan_recipe in meal_plan.recipes:
            recipe = meal_plan_recipe.recipe
            servings_multiplier = (
                meal_plan_recipe.servings / recipe.servings if recipe.servings else 1.0
            )

            # Parse each ingredient in the recipe
            for ingredient_str in recipe.ingredients:
                try:
                    parsed = self.parse_ingredient(ingredient_str)
                    normalized_qty, normalized_unit = self.normalize_units(
                        parsed.quantity * servings_multiplier, parsed.unit
                    )

                    # Aggregate by normalized name
                    ingredient_key = parsed.name.lower().strip()

                    if ingredient_key in aggregated:
                        # Same ingredient found - aggregate quantities
                        existing = aggregated[ingredient_key]
                        if existing["unit"] == normalized_unit:
                            existing["quantity"] += normalized_qty
                            # Track multiple recipe sources
                            if recipe.id not in existing["recipe_ids"]:
                                existing["recipe_ids"].append(recipe.id)
                            existing["original_strings"].append(parsed.original_text)
                        else:
                            # Different units - keep separate with suffix
                            ingredient_key = f"{ingredient_key}_{normalized_unit}"
                            aggregated[ingredient_key] = {
                                "name": parsed.name,
                                "quantity": normalized_qty,
                                "unit": normalized_unit,
                                "recipe_ids": [recipe.id],
                                "original_strings": [parsed.original_text],
                            }
                    else:
                        aggregated[ingredient_key] = {
                            "name": parsed.name,
                            "quantity": normalized_qty,
                            "unit": normalized_unit,
                            "recipe_ids": [recipe.id],
                            "original_strings": [parsed.original],
                        }
                except Exception as e:
                    # Log parsing errors but continue processing
                    # In production, this would use proper logging
                    continue

        # Convert to list of AggregatedIngredient objects
        return [
            AggregatedIngredient(
                name=item["name"],
                quantity=item["quantity"],
                unit=item["unit"],
                recipe_ids=item["recipe_ids"],
                original_strings=item["original_strings"],
                category=None,  # Category detection can be added later
            )
            for item in aggregated.values()
        ]

    async def aggregate_from_meal_plan(
        self, meal_plan_id: int
    ) -> List[AggregatedIngredient]:
        """
        Generate an aggregated grocery list from a meal plan (async version).

        Fetches all recipes in the meal plan, parses ingredients, normalizes units,
        and aggregates quantities by ingredient name.

        Args:
            meal_plan_id: ID of the meal plan to aggregate

        Returns:
            List of AggregatedIngredient objects with normalized quantities and recipe tracking

        Raises:
            ValueError: If meal plan not found or has no recipes
        """
        # Fetch meal plan with recipes
        result = await self.db_session.execute(
            select(MealPlan)
            .options(selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe))
            .where(MealPlan.id == meal_plan_id)
        )
        meal_plan = result.scalar_one_or_none()

        if not meal_plan:
            raise ValueError(f"Meal plan {meal_plan_id} not found")

        if not meal_plan.recipes:
            raise ValueError(f"Meal plan {meal_plan_id} has no recipes")

        # Aggregate ingredients
        aggregated: Dict[str, Dict[str, Any]] = {}

        for meal_plan_recipe in meal_plan.recipes:
            recipe = meal_plan_recipe.recipe
            servings_multiplier = (
                meal_plan_recipe.servings / recipe.servings if recipe.servings else 1.0
            )

            # Parse each ingredient in the recipe
            for ingredient_str in recipe.ingredients:
                try:
                    parsed = self.parse_ingredient(ingredient_str)
                    normalized_qty, normalized_unit = self.normalize_units(
                        parsed.quantity * servings_multiplier, parsed.unit
                    )

                    # Aggregate by normalized name
                    ingredient_key = parsed.name.lower().strip()

                    if ingredient_key in aggregated:
                        # Same ingredient found - aggregate quantities
                        existing = aggregated[ingredient_key]
                        if existing["unit"] == normalized_unit:
                            existing["quantity"] += normalized_qty
                            # Track multiple recipe sources
                            if recipe.id not in existing["recipe_ids"]:
                                existing["recipe_ids"].append(recipe.id)
                            existing["original_strings"].append(parsed.original_text)
                        else:
                            # Different units - keep separate with suffix
                            ingredient_key = f"{ingredient_key}_{normalized_unit}"
                            aggregated[ingredient_key] = {
                                "name": parsed.name,
                                "quantity": normalized_qty,
                                "unit": normalized_unit,
                                "recipe_ids": [recipe.id],
                                "original_strings": [parsed.original_text],
                            }
                    else:
                        aggregated[ingredient_key] = {
                            "name": parsed.name,
                            "quantity": normalized_qty,
                            "unit": normalized_unit,
                            "recipe_ids": [recipe.id],
                            "original_strings": [parsed.original],
                        }
                except Exception as e:
                    # Log parsing errors but continue processing
                    # In production, this would use proper logging
                    continue

        # Convert to list of AggregatedIngredient objects
        return [
            AggregatedIngredient(
                name=item["name"],
                quantity=item["quantity"],
                unit=item["unit"],
                recipe_ids=item["recipe_ids"],
                original_strings=item["original_strings"],
                category=None,  # Category detection can be added later
            )
            for item in aggregated.values()
        ]

    def parse_ingredient(self, ingredient_string: Optional[str]) -> ParsedIngredient:
        """
        Parse an ingredient string into structured components.

        Extracts quantity, unit, and ingredient name using regex patterns.
        Handles various formats including fractions, ranges, and no quantity.

        Examples:
            "2 cups flour" -> ParsedIngredient(2.0, "cups", "flour", ...)
            "1 1/2 tablespoons olive oil" -> ParsedIngredient(1.5, "tablespoons", "olive oil", ...)
            "Salt to taste" -> ParsedIngredient(1.0, "pinch", "salt", ...)
            "3-4 carrots" -> ParsedIngredient(3.5, "whole", "carrots", ...)

        Args:
            ingredient_string: Raw ingredient string from recipe

        Returns:
            ParsedIngredient with quantity, unit, name, and original string

        Raises:
            ValueError: If ingredient_string is None or empty
        """
        if not ingredient_string or not ingredient_string.strip():
            raise ValueError("Ingredient string cannot be None or empty")

        original = ingredient_string.strip()

        # Pattern for mixed numbers (e.g., "1 1/2")
        mixed_number_pattern = r"(\d+)\s+(\d+)/(\d+)"
        # Pattern for fractions (e.g., "1/2")
        fraction_pattern = r"(\d+)/(\d+)"
        # Pattern for ranges (e.g., "2-3")
        range_pattern = r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)"
        # Pattern for decimal numbers (e.g., "2.5")
        decimal_pattern = r"(\d+\.?\d*)"

        quantity = 1.0
        unit = "whole"
        name = original

        # Try to match quantity at the start
        quantity_match = None

        # Check for mixed number (1 1/2)
        mixed_match = re.match(r"^\s*" + mixed_number_pattern, original)
        if mixed_match:
            whole = int(mixed_match.group(1))
            numerator = int(mixed_match.group(2))
            denominator = int(mixed_match.group(3))
            quantity = whole + (numerator / denominator)
            remaining = original[mixed_match.end() :].strip()
            quantity_match = True
        else:
            # Check for fraction (1/2)
            frac_match = re.match(r"^\s*" + fraction_pattern, original)
            if frac_match:
                numerator = int(frac_match.group(1))
                denominator = int(frac_match.group(2))
                quantity = numerator / denominator
                remaining = original[frac_match.end() :].strip()
                quantity_match = True
            else:
                # Check for range (2-3)
                range_match = re.match(r"^\s*" + range_pattern, original)
                if range_match:
                    low = float(range_match.group(1))
                    high = float(range_match.group(2))
                    quantity = (low + high) / 2
                    remaining = original[range_match.end() :].strip()
                    quantity_match = True
                else:
                    # Check for decimal number (2.5 or 2)
                    decimal_match = re.match(r"^\s*" + decimal_pattern, original)
                    if decimal_match:
                        quantity = float(decimal_match.group(1))
                        remaining = original[decimal_match.end() :].strip()
                        quantity_match = True

        if not quantity_match:
            # No quantity found - treat as 1 unit/pinch
            remaining = original
            # Check if it's a "to taste" or similar phrase
            if any(
                phrase in original.lower()
                for phrase in ["to taste", "as needed", "optional"]
            ):
                unit = "pinch"
                name = remaining.split()[0] if remaining else original

        # Extract unit from remaining string
        if quantity_match:
            # Common units pattern (known measurement units)
            unit_pattern = r"^(cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|pound|pounds|lb|lbs|ounce|ounces|oz|gram|grams|g|kilogram|kilograms|kg|milliliter|milliliters|ml|liter|liters|litre|litres|l|clove|cloves|piece|pieces|whole|slice|slices|can|cans|package|packages|pinch|pinches|dash|dashes)\b"

            unit_match = re.match(unit_pattern, remaining, re.IGNORECASE)
            if unit_match:
                unit = unit_match.group(1).lower()
                name = remaining[unit_match.end() :].strip()
            else:
                # No known unit - check for adjective descriptors (large, medium, small, etc.)
                adjective_pattern = r"^(large|medium|small|fresh|dried|ground|diced|chopped|minced|sliced|shredded|whole|halved|quartered|melted|grated|raw|cooked|roasted|toasted|blanched|crushed|beaten)\b"
                adjective_match = re.match(adjective_pattern, remaining, re.IGNORECASE)
                if adjective_match:
                    unit = adjective_match.group(1).lower()
                    name = remaining[adjective_match.end() :].strip()
                else:
                    # No unit or adjective specified - assume whole
                    unit = "whole"
                    name = remaining

        # Clean up name
        name = name.strip()
        if not name:
            name = original

        # Remove common suffixes like "(optional)", ", chopped", etc.
        name = re.sub(r"\s*\([^)]*\)\s*", "", name)  # Remove parentheses
        name = re.sub(r",.*$", "", name)  # Remove everything after comma
        name = name.strip()

        return ParsedIngredient(
            quantity=quantity, unit=unit, name=name, original_text=original
        )

    def normalize_units(self, quantity: float, unit: str, target_unit: Optional[str] = None) -> Tuple[float, str]:
        """
        Normalize quantity and unit to standard measurements or target unit.

        Converts various units to standard forms or specific target unit:
        - Volume units -> milliliters (ml) or target unit
        - Weight units -> grams (g) or target unit
        - Count units -> count or target unit

        Conversion factors:
        - Volume: 1 cup = 240ml, 1 tbsp = 15ml, 1 tsp = 5ml
        - Weight: 1 lb = 453.6g, 1 oz = 28.35g
        - Count: whole, piece, item -> count

        Args:
            quantity: Original quantity value
            unit: Original unit string
            target_unit: Optional target unit to convert to (e.g., "g", "ml", "count")

        Returns:
            Tuple of (normalized_quantity, normalized_unit)

        Examples:
            (2.0, "cups", "ml") -> (480.0, "ml")
            (1.0, "lb", "g") -> (453.592, "g")
            (3.0, "whole", "count") -> (3.0, "count")
        """
        if quantity < 0:
            raise ValueError(f"Quantity must be non-negative, got {quantity}")

        unit_lower = unit.lower().strip()

        # First normalize to standard unit
        normalized_quantity = quantity
        normalized_unit = unit_lower

        # Check volume conversions
        if unit_lower in VOLUME_TO_ML:
            conversion_factor = VOLUME_TO_ML[unit_lower]
            normalized_quantity = quantity * conversion_factor
            normalized_unit = "ml"
        # Check weight conversions
        elif unit_lower in WEIGHT_TO_GRAMS:
            conversion_factor = WEIGHT_TO_GRAMS[unit_lower]
            normalized_quantity = quantity * conversion_factor
            normalized_unit = "g"
        # Check count units
        elif unit_lower in COUNT_UNITS:
            normalized_quantity = quantity
            normalized_unit = "count"

        # If target_unit specified, try to convert to it
        if target_unit:
            target_lower = target_unit.lower().strip()

            # If already in target unit, return as-is
            if normalized_unit == target_lower:
                return (normalized_quantity, normalized_unit)

            # Try to convert to target unit
            # Normalize target unit first
            normalized_quantity_target = normalized_quantity
            normalized_unit_target = normalized_unit

            if target_lower in VOLUME_TO_ML:
                # Target is a volume unit
                if normalized_unit == "ml" or normalized_unit in VOLUME_TO_ML:
                    # Convert from ml to target volume unit
                    target_factor = VOLUME_TO_ML[target_lower]
                    if target_factor != 0:
                        normalized_quantity_target = normalized_quantity / target_factor
                    normalized_unit_target = target_lower
            elif target_lower in WEIGHT_TO_GRAMS:
                # Target is a weight unit
                if normalized_unit == "g" or normalized_unit in WEIGHT_TO_GRAMS:
                    # Convert from g to target weight unit
                    target_factor = WEIGHT_TO_GRAMS[target_lower]
                    if target_factor != 0:
                        normalized_quantity_target = normalized_quantity / target_factor
                    normalized_unit_target = target_lower
            elif target_lower in COUNT_UNITS or target_lower == "count":
                # Converting to count
                normalized_unit_target = target_lower if target_lower in COUNT_UNITS else "count"

            return (normalized_quantity_target, normalized_unit_target)

        return (normalized_quantity, normalized_unit)
