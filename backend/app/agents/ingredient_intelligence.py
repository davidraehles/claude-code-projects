"""
Ingredient Intelligence Agent.

Provides ingredient classification, substitution recommendations,
and allergen checking capabilities.
"""

import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ingredient import (
    Ingredient,
    IngredientCategory,
    Allergen,
    SubstitutionRule,
)


class IngredientIntelligenceAgent:
    """
    Agent for ingredient intelligence operations.

    Features:
    - Ingredient classification and normalization
    - Substitution recommendations with quality scores
    - Allergen detection and checking
    - Ingredient matching with fuzzy search
    """

    def __init__(self, db_session: Session):
        """
        Initialize the Ingredient Intelligence Agent.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def normalize_ingredient_name(self, name: str) -> str:
        """
        Normalize ingredient name for matching.

        Args:
            name: Raw ingredient name

        Returns:
            Normalized name (lowercase, singular, trimmed)
        """
        normalized = name.lower().strip()

        # Remove common quantities and units (with optional 's')
        normalized = re.sub(r'\b\d+(\.\d+)?\s*(g|kg|ml|l|oz|lb|cups?|tbsps?|tsps?|pieces?)\b', '', normalized)

        # Remove adjectives like "fresh", "dried", "chopped"
        adjectives = r'\b(fresh|dried|chopped|sliced|diced|minced|grated|ground)\b'
        normalized = re.sub(adjectives, '', normalized)

        # Clean up extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized.strip()

    def find_ingredient(self, name: str) -> Optional[Ingredient]:
        """
        Find ingredient by name with fuzzy matching.

        Checks:
        1. Exact normalized name match
        2. Alias match
        3. Partial name match

        Args:
            name: Ingredient name to search for

        Returns:
            Matching Ingredient or None
        """
        normalized = self.normalize_ingredient_name(name)

        # 1. Try exact match
        ingredient = self.db.query(Ingredient).filter(
            Ingredient.normalized_name == normalized
        ).first()

        if ingredient:
            return ingredient

        # 2. Try partial match (contains)
        ingredient = self.db.query(Ingredient).filter(
            Ingredient.normalized_name.contains(normalized)
        ).first()

        if ingredient:
            return ingredient

        # 3. Try reverse partial match
        ingredient = self.db.query(Ingredient).filter(
            func.lower(Ingredient.name).contains(normalized)
        ).first()

        return ingredient

    def classify_ingredient(self, name: str) -> Dict[str, Any]:
        """
        Classify an ingredient and return its metadata.

        Args:
            name: Ingredient name

        Returns:
            Dict with ingredient classification data
        """
        ingredient = self.find_ingredient(name)

        if not ingredient:
            return {
                "found": False,
                "name": name,
                "normalized_name": self.normalize_ingredient_name(name),
                "category": None,
                "allergens": [],
                "nutrition": None,
            }

        return {
            "found": True,
            "id": ingredient.id,
            "name": ingredient.name,
            "normalized_name": ingredient.normalized_name,
            "category": ingredient.category.name if ingredient.category else None,
            "allergens": [a.name for a in ingredient.allergens] if ingredient.allergens else [],
            "nutrition_per_100g": ingredient.nutrition_per_100g,
            "seasonal_availability": ingredient.seasonal_availability,
            "base_unit": ingredient.base_unit,
            "is_common": ingredient.is_common,
        }

    def find_substitutes(
        self,
        ingredient_name: str,
        dietary_restrictions: Optional[List[str]] = None,
        min_quality_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find substitutes for an ingredient.

        Args:
            ingredient_name: Name of ingredient to substitute
            dietary_restrictions: List of dietary requirements
                (e.g., ["vegan", "gluten_free"])
            min_quality_score: Minimum quality score (0-1)

        Returns:
            List of substitution options with metadata
        """
        ingredient = self.find_ingredient(ingredient_name)

        if not ingredient:
            return []

        # Query substitution rules
        query = self.db.query(SubstitutionRule).filter(
            SubstitutionRule.ingredient_id == ingredient.id,
            SubstitutionRule.quality_score >= min_quality_score
        )

        # Apply dietary filters
        if dietary_restrictions:
            for restriction in dietary_restrictions:
                restriction_lower = restriction.lower()
                if restriction_lower in ["vegan", "is_vegan"]:
                    query = query.filter(SubstitutionRule.is_vegan == True)
                elif restriction_lower in ["vegetarian", "is_vegetarian"]:
                    query = query.filter(SubstitutionRule.is_vegetarian == True)
                elif restriction_lower in ["gluten_free", "is_gluten_free", "gluten-free"]:
                    query = query.filter(SubstitutionRule.is_gluten_free == True)
                elif restriction_lower in ["dairy_free", "is_dairy_free", "dairy-free"]:
                    query = query.filter(SubstitutionRule.is_dairy_free == True)

        # Order by quality score descending
        substitutions = query.order_by(SubstitutionRule.quality_score.desc()).all()

        results = []
        for sub in substitutions:
            results.append({
                "substitute_id": sub.substitute.id,
                "substitute_name": sub.substitute.name,
                "ratio": sub.ratio,
                "quality_score": sub.quality_score,
                "notes": sub.notes,
                "context": sub.context,
                "is_vegan": sub.is_vegan,
                "is_vegetarian": sub.is_vegetarian,
                "is_gluten_free": sub.is_gluten_free,
                "is_dairy_free": sub.is_dairy_free,
            })

        return results

    def check_allergens(self, ingredient_names: List[str]) -> Dict[str, Any]:
        """
        Check for allergens in a list of ingredients.

        Args:
            ingredient_names: List of ingredient names

        Returns:
            Dict with allergen information
        """
        allergens_found = {}
        ingredients_checked = []
        unknown_ingredients = []

        for name in ingredient_names:
            ingredient = self.find_ingredient(name)

            if not ingredient:
                unknown_ingredients.append(name)
                continue

            ingredients_checked.append({
                "name": ingredient.name,
                "id": ingredient.id
            })

            # Check allergens
            if ingredient.allergens:
                for allergen in ingredient.allergens:
                    if allergen.name not in allergens_found:
                        allergens_found[allergen.name] = {
                            "allergen": allergen.name,
                            "severity": allergen.severity,
                            "description": allergen.description,
                            "found_in": []
                        }

                    allergens_found[allergen.name]["found_in"].append(ingredient.name)

        return {
            "ingredients_checked": len(ingredients_checked),
            "unknown_ingredients": unknown_ingredients,
            "allergens_found": list(allergens_found.values()),
            "has_allergens": len(allergens_found) > 0,
        }

    def get_category_hierarchy(self, category_id: int) -> List[str]:
        """
        Get full category hierarchy path.

        Args:
            category_id: Category ID

        Returns:
            List of category names from root to leaf
        """
        hierarchy = []
        category = self.db.query(IngredientCategory).get(category_id)

        while category:
            hierarchy.insert(0, category.name)
            if category.parent_id:
                category = self.db.query(IngredientCategory).get(category.parent_id)
            else:
                break

        return hierarchy

    def search_ingredients(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for ingredients by name.

        Args:
            query: Search query
            category: Optional category filter
            limit: Max results to return

        Returns:
            List of matching ingredients
        """
        normalized_query = self.normalize_ingredient_name(query)

        # Build query
        db_query = self.db.query(Ingredient).filter(
            func.lower(Ingredient.name).contains(normalized_query)
        )

        # Apply category filter
        if category:
            cat = self.db.query(IngredientCategory).filter_by(name=category).first()
            if cat:
                db_query = db_query.filter(Ingredient.category_id == cat.id)

        # Execute query
        ingredients = db_query.limit(limit).all()

        results = []
        for ing in ingredients:
            results.append({
                "id": ing.id,
                "name": ing.name,
                "category": ing.category.name if ing.category else None,
                "allergens": [a.name for a in ing.allergens] if ing.allergens else [],
                "is_common": ing.is_common,
            })

        return results
