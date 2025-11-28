"""
Models package for the recipe application.

Exports all SQLAlchemy models for easy import.
"""

from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import (
    Allergen,
    IngredientCategory,
    Ingredient,
    IngredientAllergen,
    SubstitutionRule,
)
from app.models.meal_plan import (
    MealPlan,
    MealPlanRecipe,
    GroceryCart,
    CartItem,
)

__all__ = [
    "User",
    "Recipe",
    "Allergen",
    "IngredientCategory",
    "Ingredient",
    "IngredientAllergen",
    "SubstitutionRule",
    "MealPlan",
    "MealPlanRecipe",
    "GroceryCart",
    "CartItem",
]
