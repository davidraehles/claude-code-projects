"""
Ingredient to Knuspr Product Mapper

Maps recipe ingredients to Knuspr products with intelligent matching:
- Fuzzy matching for ingredient names (e.g., "canned beans" → "Organic Kidney Beans 400g")
- Quantity conversion (e.g., "2 cans" → "800g")
- Unit normalization (cups → grams, etc.)
- Fallback handling for unavailable items
"""

import logging
import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


# Unit conversion factors (normalized to grams or milliliters)
UNIT_CONVERSIONS = {
    # Volume conversions (to ml)
    "cup": 240,
    "cups": 240,
    "tbsp": 15,
    "tablespoon": 15,
    "tsp": 5,
    "teaspoon": 5,
    "ml": 1,
    "milliliter": 1,
    "l": 1000,
    "liter": 1000,

    # Weight conversions (to grams)
    "g": 1,
    "gram": 1,
    "kg": 1000,
    "kilogram": 1000,
    "oz": 28.35,
    "ounce": 28.35,
    "lb": 453.6,
    "pound": 453.6,

    # Count (pass through)
    "pcs": 1,
    "piece": 1,
    "pieces": 1,
    "can": 1,
    "cans": 1,
    "jar": 1,
    "jars": 1,
    "bunch": 1,
    "bunches": 1,
    "whole": 1,
}

# Ingredient category mappings
INGREDIENT_CATEGORIES = {
    "produce": ["carrot", "onion", "garlic", "tomato", "lettuce", "potato"],
    "dairy": ["milk", "cheese", "butter", "yogurt", "cream"],
    "meat": ["chicken", "beef", "pork", "lamb", "fish", "salmon"],
    "canned_goods": ["beans", "tomatoes", "corn", "peas", "lentils"],
    "frozen": ["peas", "mixed vegetables", "berries"],
    "grains": ["rice", "pasta", "bread", "flour"],
    "oils_vinegar": ["olive oil", "canola oil", "vinegar", "sesame oil"],
}


@dataclass
class ParsedIngredient:
    """Parsed ingredient with quantity and unit"""
    name: str
    quantity: float
    unit: str
    original: str


class IngredientMapper:
    """Maps recipe ingredients to Knuspr products"""

    def __init__(self, knuspr_client):
        """
        Initialize ingredient mapper.

        Args:
            knuspr_client: KnusprMCPClient instance for product searches
        """
        self.knuspr_client = knuspr_client
        self._product_cache: Dict[str, List] = {}

    def parse_ingredient_string(self, ingredient_str: str) -> ParsedIngredient:
        """
        Parse ingredient string into components.

        Examples:
            "2 cups flour" → ParsedIngredient(name="flour", quantity=2, unit="cups", ...)
            "1 can (400g) kidney beans" → ParsedIngredient(name="kidney beans", quantity=400, unit="g", ...)
            "3 cloves garlic" → ParsedIngredient(name="garlic", quantity=3, unit="pcs", ...)

        Args:
            ingredient_str: Raw ingredient string from recipe

        Returns:
            ParsedIngredient with extracted components
        """
        original = ingredient_str.strip()

        # Extract quantity and unit using regex
        # Pattern: [number] [unit]
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([a-z]+)?\s+(.+)$', original, re.IGNORECASE)

        if match:
            quantity = float(match.group(1))
            unit = (match.group(2) or "pcs").lower()
            name = match.group(3).lower().strip()
        else:
            # Fallback: treat as 1 unit of ingredient
            quantity = 1
            unit = "pcs"
            name = original.lower().strip()

        # Clean up common patterns (e.g., "canned", "fresh")
        name = self._clean_ingredient_name(name)

        return ParsedIngredient(
            name=name,
            quantity=quantity,
            unit=unit,
            original=original
        )

    def _clean_ingredient_name(self, name: str) -> str:
        """
        Clean ingredient name by removing descriptors.

        Examples:
            "fresh tomatoes" → "tomatoes"
            "canned beans" → "beans"
            "extra virgin olive oil" → "olive oil"

        Args:
            name: Raw ingredient name

        Returns:
            Cleaned ingredient name
        """
        # Remove common descriptors
        descriptors = [
            "fresh", "frozen", "canned", "dried", "raw", "cooked",
            "minced", "chopped", "diced", "sliced", "grated",
            "extra virgin", "pure", "whole", "ground", "powdered",
            "organic", "unsalted", "salted"
        ]

        words = name.split()
        cleaned = [w for w in words if w.lower() not in descriptors]
        return " ".join(cleaned) if cleaned else name

    def normalize_quantity(self, quantity: float, from_unit: str, to_unit: str = "g") -> float:
        """
        Convert quantity from one unit to another.

        Args:
            quantity: Original quantity
            from_unit: Original unit
            to_unit: Target unit (default: grams)

        Returns:
            Normalized quantity in target unit
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit == to_unit:
            return quantity

        # Get conversion factors
        from_factor = UNIT_CONVERSIONS.get(from_unit, 1)
        to_factor = UNIT_CONVERSIONS.get(to_unit, 1)

        if from_unit in ["pcs", "piece", "can", "jar"] or to_unit in ["pcs", "piece", "can", "jar"]:
            # Can't convert between weight/volume and count
            return quantity

        # Convert through base unit (grams)
        return (quantity * from_factor) / to_factor

    def _similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity (0-1).

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0 and 1
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    async def find_product(
        self,
        ingredient: ParsedIngredient,
        min_confidence: float = 0.75
    ) -> Optional[Dict]:
        """
        Find Knuspr product matching ingredient.

        Args:
            ingredient: Parsed ingredient
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            Product dict with keys: product_id, name, quantity, unit, price, confidence
            Or None if no good match found
        """
        # Search Knuspr for products
        products = await self.knuspr_client.search_products(
            ingredient.name,
            max_results=10,
            exact_match=False
        )

        if not products:
            logger.warning(f"No Knuspr products found for '{ingredient.name}'")
            return None

        # Score products by similarity to ingredient
        best_match = None
        best_score = 0

        for product in products:
            # Calculate similarity score
            similarity = self._similarity_score(ingredient.name, product.name)

            if similarity >= min_confidence and similarity > best_score:
                best_match = product
                best_score = similarity

        if best_match:
            logger.info(f"Matched '{ingredient.name}' to '{best_match.name}' (confidence: {best_score:.2f})")
            return {
                "product_id": best_match.product_id,
                "name": best_match.name,
                "quantity": best_match.quantity,
                "unit": best_match.unit,
                "price": best_match.price,
                "confidence": best_score
            }
        else:
            logger.warning(f"No good match found for '{ingredient.name}' (best score: {best_score:.2f})")
            return None

    async def map_ingredients_to_products(
        self,
        ingredients: List[str]
    ) -> Tuple[List[Dict], List[str]]:
        """
        Map a list of recipe ingredients to Knuspr products.

        Args:
            ingredients: List of ingredient strings from recipe

        Returns:
            Tuple of:
            - List of product dicts ready for cart creation
            - List of unmapped ingredient strings (unavailable items)
        """
        mapped_products = []
        unmapped_ingredients = []

        for ingredient_str in ingredients:
            try:
                # Parse ingredient
                parsed = self.parse_ingredient_string(ingredient_str)
                logger.debug(f"Parsed: {parsed}")

                # Find matching product
                product = await self.find_product(parsed)

                if product:
                    # Normalize quantity to product unit if possible
                    normalized_qty = self.normalize_quantity(
                        parsed.quantity,
                        parsed.unit,
                        product["unit"]
                    )

                    product["quantity"] = normalized_qty
                    mapped_products.append(product)
                else:
                    unmapped_ingredients.append(ingredient_str)
            except Exception as e:
                logger.error(f"Failed to map ingredient '{ingredient_str}': {str(e)}")
                unmapped_ingredients.append(ingredient_str)

        logger.info(f"Mapped {len(mapped_products)} / {len(ingredients)} ingredients")
        if unmapped_ingredients:
            logger.warning(f"Unmapped ingredients: {unmapped_ingredients}")

        return mapped_products, unmapped_ingredients

    def categorize_products(self, products: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group products by store category.

        Args:
            products: List of product dicts

        Returns:
            Dict mapping category names to product lists
        """
        categorized = {}

        for product in products:
            category = self._get_product_category(product["name"])
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(product)

        return categorized

    def _get_product_category(self, product_name: str) -> str:
        """
        Determine store category for a product.

        Args:
            product_name: Name of product

        Returns:
            Category name
        """
        name_lower = product_name.lower()

        for category, keywords in INGREDIENT_CATEGORIES.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category

        return "other"
