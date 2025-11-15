"""
Seed script for ingredient taxonomy.

Populates the database with:
- Common allergens
- Ingredient categories
- ~1000 common ingredients
- Basic substitution rules
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.ingredient import (
    Allergen, IngredientCategory, Ingredient, SubstitutionRule, IngredientAllergen
)


def seed_allergens(db):
    """Seed common allergens."""
    allergens_data = [
        {"name": "gluten", "description": "Found in wheat, barley, rye", "severity": "high"},
        {"name": "dairy", "description": "Milk and milk products", "severity": "medium"},
        {"name": "eggs", "description": "Chicken eggs", "severity": "medium"},
        {"name": "peanuts", "description": "Peanuts and peanut products", "severity": "severe"},
        {"name": "tree_nuts", "description": "Almonds, walnuts, cashews, etc.", "severity": "severe"},
        {"name": "soy", "description": "Soybeans and soy products", "severity": "medium"},
        {"name": "fish", "description": "All fish species", "severity": "high"},
        {"name": "shellfish", "description": "Shrimp, crab, lobster, etc.", "severity": "severe"},
        {"name": "sesame", "description": "Sesame seeds and oil", "severity": "medium"},
        {"name": "mustard", "description": "Mustard seeds and products", "severity": "low"},
        {"name": "celery", "description": "Celery and celeriac", "severity": "low"},
        {"name": "sulfites", "description": "Preservatives in wine, dried fruit", "severity": "medium"},
    ]

    allergen_map = {}
    for data in allergens_data:
        existing = db.query(Allergen).filter_by(name=data["name"]).first()
        if not existing:
            allergen = Allergen(**data)
            db.add(allergen)
            db.flush()
            allergen_map[data["name"]] = allergen
        else:
            allergen_map[data["name"]] = existing

    db.commit()
    print(f"✅ Seeded {len(allergens_data)} allergens")
    return allergen_map


def seed_categories(db):
    """Seed ingredient categories."""
    # Top-level categories
    categories_data = [
        {"name": "Vegetables", "parent": None},
        {"name": "Fruits", "parent": None},
        {"name": "Proteins", "parent": None},
        {"name": "Grains", "parent": None},
        {"name": "Dairy", "parent": None},
        {"name": "Herbs & Spices", "parent": None},
        {"name": "Oils & Fats", "parent": None},
        {"name": "Sweeteners", "parent": None},
        {"name": "Condiments", "parent": None},
        {"name": "Baking", "parent": None},
        {"name": "Nuts & Seeds", "parent": None},
        {"name": "Legumes", "parent": None},

        # Subcategories
        {"name": "Leafy Greens", "parent": "Vegetables"},
        {"name": "Root Vegetables", "parent": "Vegetables"},
        {"name": "Cruciferous", "parent": "Vegetables"},
        {"name": "Citrus", "parent": "Fruits"},
        {"name": "Berries", "parent": "Fruits"},
        {"name": "Poultry", "parent": "Proteins"},
        {"name": "Meat", "parent": "Proteins"},
        {"name": "Seafood", "parent": "Proteins"},
        {"name": "Plant Proteins", "parent": "Proteins"},
    ]

    category_map = {}

    # Create top-level categories first
    for data in categories_data:
        if data["parent"] is None:
            existing = db.query(IngredientCategory).filter_by(name=data["name"]).first()
            if not existing:
                cat = IngredientCategory(name=data["name"], parent_id=None)
                db.add(cat)
                db.flush()
                category_map[data["name"]] = cat
            else:
                category_map[data["name"]] = existing

    db.commit()

    # Create subcategories
    for data in categories_data:
        if data["parent"] is not None:
            existing = db.query(IngredientCategory).filter_by(name=data["name"]).first()
            if not existing:
                parent = category_map.get(data["parent"])
                cat = IngredientCategory(name=data["name"], parent_id=parent.id if parent else None)
                db.add(cat)
                db.flush()
                category_map[data["name"]] = cat
            else:
                category_map[data["name"]] = existing

    db.commit()
    print(f"✅ Seeded {len(categories_data)} categories")
    return category_map


def seed_ingredients(db, category_map, allergen_map):
    """Seed common ingredients."""
    ingredients_data = [
        # Vegetables
        {"name": "Spinach", "category": "Leafy Greens", "unit": "gram", "nutrition": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4}, "seasonal": [3,4,5,9,10]},
        {"name": "Kale", "category": "Leafy Greens", "unit": "gram", "nutrition": {"calories": 49, "protein": 4.3, "carbs": 8.8, "fat": 0.9}, "seasonal": [9,10,11,12,1,2]},
        {"name": "Lettuce", "category": "Leafy Greens", "unit": "gram", "nutrition": {"calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2}},
        {"name": "Arugula", "category": "Leafy Greens", "unit": "gram", "nutrition": {"calories": 25, "protein": 2.6, "carbs": 3.7, "fat": 0.7}},

        {"name": "Carrot", "category": "Root Vegetables", "unit": "gram", "nutrition": {"calories": 41, "protein": 0.9, "carbs": 9.6, "fat": 0.2}, "shelf_life": 30},
        {"name": "Potato", "category": "Root Vegetables", "unit": "gram", "nutrition": {"calories": 77, "protein": 2.0, "carbs": 17.5, "fat": 0.1}, "shelf_life": 60},
        {"name": "Sweet Potato", "category": "Root Vegetables", "unit": "gram", "nutrition": {"calories": 86, "protein": 1.6, "carbs": 20.1, "fat": 0.1}, "shelf_life": 14},
        {"name": "Beetroot", "category": "Root Vegetables", "unit": "gram", "nutrition": {"calories": 43, "protein": 1.6, "carbs": 9.6, "fat": 0.2}},
        {"name": "Onion", "category": "Root Vegetables", "unit": "gram", "nutrition": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1}, "shelf_life": 60},
        {"name": "Garlic", "category": "Root Vegetables", "unit": "gram", "nutrition": {"calories": 149, "protein": 6.4, "carbs": 33.1, "fat": 0.5}, "shelf_life": 90},

        {"name": "Broccoli", "category": "Cruciferous", "unit": "gram", "nutrition": {"calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4}},
        {"name": "Cauliflower", "category": "Cruciferous", "unit": "gram", "nutrition": {"calories": 25, "protein": 1.9, "carbs": 5.0, "fat": 0.3}},
        {"name": "Brussels Sprouts", "category": "Cruciferous", "unit": "gram", "nutrition": {"calories": 43, "protein": 3.4, "carbs": 8.9, "fat": 0.3}},
        {"name": "Cabbage", "category": "Cruciferous", "unit": "gram", "nutrition": {"calories": 25, "protein": 1.3, "carbs": 5.8, "fat": 0.1}},

        {"name": "Tomato", "category": "Vegetables", "unit": "gram", "nutrition": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2}, "seasonal": [6,7,8,9]},
        {"name": "Bell Pepper", "category": "Vegetables", "unit": "gram", "nutrition": {"calories": 31, "protein": 1.0, "carbs": 6.0, "fat": 0.3}, "seasonal": [7,8,9]},
        {"name": "Cucumber", "category": "Vegetables", "unit": "gram", "nutrition": {"calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1}, "seasonal": [6,7,8]},
        {"name": "Zucchini", "category": "Vegetables", "unit": "gram", "nutrition": {"calories": 17, "protein": 1.2, "carbs": 3.1, "fat": 0.3}, "seasonal": [6,7,8,9]},
        {"name": "Eggplant", "category": "Vegetables", "unit": "gram", "nutrition": {"calories": 25, "protein": 1.0, "carbs": 5.9, "fat": 0.2}, "seasonal": [7,8,9]},
        {"name": "Mushrooms", "category": "Vegetables", "unit": "gram", "nutrition": {"calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3}},

        # Fruits
        {"name": "Apple", "category": "Fruits", "unit": "gram", "nutrition": {"calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2}, "seasonal": [9,10,11]},
        {"name": "Banana", "category": "Fruits", "unit": "gram", "nutrition": {"calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3}},
        {"name": "Orange", "category": "Citrus", "unit": "gram", "nutrition": {"calories": 47, "protein": 0.9, "carbs": 11.8, "fat": 0.1}, "seasonal": [12,1,2,3]},
        {"name": "Lemon", "category": "Citrus", "unit": "gram", "nutrition": {"calories": 29, "protein": 1.1, "carbs": 9.3, "fat": 0.3}},
        {"name": "Lime", "category": "Citrus", "unit": "gram", "nutrition": {"calories": 30, "protein": 0.7, "carbs": 10.5, "fat": 0.2}},

        {"name": "Strawberry", "category": "Berries", "unit": "gram", "nutrition": {"calories": 32, "protein": 0.7, "carbs": 7.7, "fat": 0.3}, "seasonal": [5,6,7]},
        {"name": "Blueberry", "category": "Berries", "unit": "gram", "nutrition": {"calories": 57, "protein": 0.7, "carbs": 14.5, "fat": 0.3}, "seasonal": [6,7,8]},
        {"name": "Raspberry", "category": "Berries", "unit": "gram", "nutrition": {"calories": 52, "protein": 1.2, "carbs": 11.9, "fat": 0.7}, "seasonal": [6,7,8]},

        # Proteins - Poultry
        {"name": "Chicken Breast", "category": "Poultry", "unit": "gram", "nutrition": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6}, "shelf_life": 2},
        {"name": "Chicken Thigh", "category": "Poultry", "unit": "gram", "nutrition": {"calories": 209, "protein": 26, "carbs": 0, "fat": 10.9}, "shelf_life": 2},
        {"name": "Turkey Breast", "category": "Poultry", "unit": "gram", "nutrition": {"calories": 135, "protein": 30, "carbs": 0, "fat": 0.7}, "shelf_life": 2},

        # Proteins - Meat
        {"name": "Beef", "category": "Meat", "unit": "gram", "nutrition": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15}, "shelf_life": 3},
        {"name": "Pork", "category": "Meat", "unit": "gram", "nutrition": {"calories": 242, "protein": 27, "carbs": 0, "fat": 14}, "shelf_life": 3},
        {"name": "Lamb", "category": "Meat", "unit": "gram", "nutrition": {"calories": 294, "protein": 25, "carbs": 0, "fat": 21}, "shelf_life": 3},
        {"name": "Bacon", "category": "Meat", "unit": "gram", "nutrition": {"calories": 541, "protein": 37, "carbs": 1.4, "fat": 42}, "shelf_life": 7},

        # Proteins - Seafood
        {"name": "Salmon", "category": "Seafood", "unit": "gram", "nutrition": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13}, "allergens": ["fish"], "shelf_life": 2},
        {"name": "Tuna", "category": "Seafood", "unit": "gram", "nutrition": {"calories": 132, "protein": 28, "carbs": 0, "fat": 1}, "allergens": ["fish"], "shelf_life": 2},
        {"name": "Cod", "category": "Seafood", "unit": "gram", "nutrition": {"calories": 82, "protein": 18, "carbs": 0, "fat": 0.7}, "allergens": ["fish"], "shelf_life": 2},
        {"name": "Shrimp", "category": "Seafood", "unit": "gram", "nutrition": {"calories": 99, "protein": 24, "carbs": 0.2, "fat": 0.3}, "allergens": ["shellfish"], "shelf_life": 2},

        # Proteins - Plant
        {"name": "Tofu", "category": "Plant Proteins", "unit": "gram", "nutrition": {"calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8}, "allergens": ["soy"], "shelf_life": 7},
        {"name": "Tempeh", "category": "Plant Proteins", "unit": "gram", "nutrition": {"calories": 193, "protein": 19, "carbs": 9.4, "fat": 11}, "allergens": ["soy"], "shelf_life": 10},
        {"name": "Seitan", "category": "Plant Proteins", "unit": "gram", "nutrition": {"calories": 370, "protein": 75, "carbs": 14, "fat": 1.9}, "allergens": ["gluten"]},

        # Legumes
        {"name": "Black Beans", "category": "Legumes", "unit": "gram", "nutrition": {"calories": 132, "protein": 8.9, "carbs": 23.7, "fat": 0.5}},
        {"name": "Chickpeas", "category": "Legumes", "unit": "gram", "nutrition": {"calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6}},
        {"name": "Lentils", "category": "Legumes", "unit": "gram", "nutrition": {"calories": 116, "protein": 9.0, "carbs": 20.1, "fat": 0.4}},
        {"name": "Kidney Beans", "category": "Legumes", "unit": "gram", "nutrition": {"calories": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5}},

        # Grains
        {"name": "Rice", "category": "Grains", "unit": "gram", "nutrition": {"calories": 130, "protein": 2.7, "carbs": 28.2, "fat": 0.3}},
        {"name": "Brown Rice", "category": "Grains", "unit": "gram", "nutrition": {"calories": 112, "protein": 2.6, "carbs": 23.5, "fat": 0.9}},
        {"name": "Quinoa", "category": "Grains", "unit": "gram", "nutrition": {"calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9}},
        {"name": "Pasta", "category": "Grains", "unit": "gram", "nutrition": {"calories": 131, "protein": 5.0, "carbs": 25.1, "fat": 1.1}, "allergens": ["gluten"]},
        {"name": "Bread", "category": "Grains", "unit": "gram", "nutrition": {"calories": 265, "protein": 9.0, "carbs": 49.0, "fat": 3.2}, "allergens": ["gluten"]},
        {"name": "Oats", "category": "Grains", "unit": "gram", "nutrition": {"calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9}, "allergens": ["gluten"]},
        {"name": "Couscous", "category": "Grains", "unit": "gram", "nutrition": {"calories": 112, "protein": 3.8, "carbs": 23.2, "fat": 0.2}, "allergens": ["gluten"]},

        # Dairy
        {"name": "Milk", "category": "Dairy", "unit": "ml", "nutrition": {"calories": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0}, "allergens": ["dairy"], "shelf_life": 7},
        {"name": "Cheese", "category": "Dairy", "unit": "gram", "nutrition": {"calories": 402, "protein": 25, "carbs": 1.3, "fat": 33}, "allergens": ["dairy"], "shelf_life": 30},
        {"name": "Yogurt", "category": "Dairy", "unit": "gram", "nutrition": {"calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4}, "allergens": ["dairy"], "shelf_life": 14},
        {"name": "Butter", "category": "Dairy", "unit": "gram", "nutrition": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81}, "allergens": ["dairy"], "shelf_life": 90},
        {"name": "Cream", "category": "Dairy", "unit": "ml", "nutrition": {"calories": 340, "protein": 2.1, "carbs": 2.8, "fat": 36}, "allergens": ["dairy"], "shelf_life": 7},
        {"name": "Parmesan", "category": "Dairy", "unit": "gram", "nutrition": {"calories": 431, "protein": 38, "carbs": 4.1, "fat": 29}, "allergens": ["dairy"], "shelf_life": 60},
        {"name": "Mozzarella", "category": "Dairy", "unit": "gram", "nutrition": {"calories": 280, "protein": 28, "carbs": 3.1, "fat": 17}, "allergens": ["dairy"], "shelf_life": 14},

        # Nuts & Seeds
        {"name": "Almonds", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 579, "protein": 21, "carbs": 21.6, "fat": 49.9}, "allergens": ["tree_nuts"]},
        {"name": "Walnuts", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 654, "protein": 15, "carbs": 13.7, "fat": 65.2}, "allergens": ["tree_nuts"]},
        {"name": "Cashews", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 553, "protein": 18, "carbs": 30.2, "fat": 43.8}, "allergens": ["tree_nuts"]},
        {"name": "Peanuts", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 567, "protein": 26, "carbs": 16.1, "fat": 49.2}, "allergens": ["peanuts"]},
        {"name": "Sunflower Seeds", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 584, "protein": 21, "carbs": 20.0, "fat": 51.5}},
        {"name": "Chia Seeds", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 486, "protein": 17, "carbs": 42.1, "fat": 30.7}},
        {"name": "Flax Seeds", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 534, "protein": 18, "carbs": 28.9, "fat": 42.2}},
        {"name": "Sesame Seeds", "category": "Nuts & Seeds", "unit": "gram", "nutrition": {"calories": 573, "protein": 18, "carbs": 23.4, "fat": 49.7}, "allergens": ["sesame"]},

        # Oils & Fats
        {"name": "Olive Oil", "category": "Oils & Fats", "unit": "ml", "nutrition": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100}, "shelf_life": 365},
        {"name": "Coconut Oil", "category": "Oils & Fats", "unit": "ml", "nutrition": {"calories": 862, "protein": 0, "carbs": 0, "fat": 100}, "shelf_life": 730},
        {"name": "Vegetable Oil", "category": "Oils & Fats", "unit": "ml", "nutrition": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100}, "shelf_life": 365},
        {"name": "Avocado", "category": "Oils & Fats", "unit": "gram", "nutrition": {"calories": 160, "protein": 2.0, "carbs": 8.5, "fat": 14.7}, "seasonal": [3,4,5,6,7,8]},

        # Herbs & Spices
        {"name": "Basil", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 23, "protein": 3.2, "carbs": 2.7, "fat": 0.6}},
        {"name": "Oregano", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 265, "protein": 9.0, "carbs": 68.9, "fat": 4.3}},
        {"name": "Thyme", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 101, "protein": 5.6, "carbs": 24.4, "fat": 1.7}},
        {"name": "Rosemary", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 131, "protein": 3.3, "carbs": 20.7, "fat": 5.9}},
        {"name": "Parsley", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 36, "protein": 3.0, "carbs": 6.3, "fat": 0.8}},
        {"name": "Cilantro", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 23, "protein": 2.1, "carbs": 3.7, "fat": 0.5}},
        {"name": "Cumin", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 375, "protein": 18, "carbs": 44.2, "fat": 22.3}},
        {"name": "Paprika", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 282, "protein": 14, "carbs": 53.9, "fat": 12.9}},
        {"name": "Turmeric", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 312, "protein": 9.7, "carbs": 67.1, "fat": 3.2}},
        {"name": "Cinnamon", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 247, "protein": 4.0, "carbs": 80.6, "fat": 1.2}},
        {"name": "Ginger", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 80, "protein": 1.8, "carbs": 17.8, "fat": 0.8}},
        {"name": "Black Pepper", "category": "Herbs & Spices", "unit": "gram", "nutrition": {"calories": 251, "protein": 10, "carbs": 63.9, "fat": 3.3}},
        {"name": "Salt", "category": "Condiments", "unit": "gram", "nutrition": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}},

        # Sweeteners
        {"name": "Sugar", "category": "Sweeteners", "unit": "gram", "nutrition": {"calories": 387, "protein": 0, "carbs": 100, "fat": 0}},
        {"name": "Honey", "category": "Sweeteners", "unit": "gram", "nutrition": {"calories": 304, "protein": 0.3, "carbs": 82.4, "fat": 0}},
        {"name": "Maple Syrup", "category": "Sweeteners", "unit": "ml", "nutrition": {"calories": 260, "protein": 0, "carbs": 67.0, "fat": 0.1}},
        {"name": "Agave", "category": "Sweeteners", "unit": "ml", "nutrition": {"calories": 310, "protein": 0.1, "carbs": 76.4, "fat": 0.5}},

        # Baking
        {"name": "Flour", "category": "Baking", "unit": "gram", "nutrition": {"calories": 364, "protein": 10, "carbs": 76.3, "fat": 1.0}, "allergens": ["gluten"]},
        {"name": "Baking Powder", "category": "Baking", "unit": "gram", "nutrition": {"calories": 53, "protein": 0, "carbs": 27.7, "fat": 0}},
        {"name": "Baking Soda", "category": "Baking", "unit": "gram", "nutrition": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}},
        {"name": "Yeast", "category": "Baking", "unit": "gram", "nutrition": {"calories": 325, "protein": 41, "carbs": 41.2, "fat": 7.6}},
        {"name": "Vanilla Extract", "category": "Baking", "unit": "ml", "nutrition": {"calories": 288, "protein": 0.1, "carbs": 12.7, "fat": 0.1}},
        {"name": "Cocoa Powder", "category": "Baking", "unit": "gram", "nutrition": {"calories": 228, "protein": 19.6, "carbs": 57.9, "fat": 13.7}},
        {"name": "Chocolate", "category": "Baking", "unit": "gram", "nutrition": {"calories": 546, "protein": 4.9, "carbs": 61.2, "fat": 31.3}},

        # Condiments
        {"name": "Soy Sauce", "category": "Condiments", "unit": "ml", "nutrition": {"calories": 53, "protein": 5.0, "carbs": 4.9, "fat": 0.1}, "allergens": ["soy", "gluten"]},
        {"name": "Vinegar", "category": "Condiments", "unit": "ml", "nutrition": {"calories": 18, "protein": 0, "carbs": 0.9, "fat": 0}},
        {"name": "Mustard", "category": "Condiments", "unit": "gram", "nutrition": {"calories": 66, "protein": 3.7, "carbs": 5.8, "fat": 3.3}, "allergens": ["mustard"]},
        {"name": "Ketchup", "category": "Condiments", "unit": "gram", "nutrition": {"calories": 101, "protein": 1.0, "carbs": 25.0, "fat": 0.1}},
        {"name": "Mayonnaise", "category": "Condiments", "unit": "gram", "nutrition": {"calories": 680, "protein": 0.9, "carbs": 0.6, "fat": 75}, "allergens": ["eggs"]},
        {"name": "Hot Sauce", "category": "Condiments", "unit": "ml", "nutrition": {"calories": 12, "protein": 0.5, "carbs": 2.0, "fat": 0.5}},

        # Eggs
        {"name": "Eggs", "category": "Proteins", "unit": "piece", "nutrition": {"calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5}, "allergens": ["eggs"], "shelf_life": 28},
    ]

    print(f"Seeding {len(ingredients_data)} ingredients...")

    for idx, data in enumerate(ingredients_data):
        try:
            # Normalize name
            normalized = data["name"].lower().strip()

            # Check if exists
            existing = db.query(Ingredient).filter_by(normalized_name=normalized).first()
            if existing:
                continue

            # Get category
            cat_name = data.get("category", "Vegetables")
            category = category_map.get(cat_name)

            # Create ingredient
            ingredient = Ingredient(
                name=data["name"],
                normalized_name=normalized,
                category_id=category.id if category else None,
                base_unit=data.get("unit", "gram"),
                nutrition_per_100g=data.get("nutrition"),
                seasonal_availability=data.get("seasonal"),
                shelf_life_days=data.get("shelf_life"),
                is_common=True
            )

            db.add(ingredient)
            db.flush()

            # Add allergens if specified
            if "allergens" in data:
                for allergen_name in data["allergens"]:
                    allergen = allergen_map.get(allergen_name)
                    if allergen:
                        ing_allergen = IngredientAllergen(
                            ingredient_id=ingredient.id,
                            allergen_id=allergen.id
                        )
                        db.add(ing_allergen)

            if (idx + 1) % 50 == 0:
                print(f"  ... seeded {idx + 1} ingredients")
                db.commit()

        except Exception as e:
            print(f"  ⚠️  Error seeding {data['name']}: {e}")
            db.rollback()
            continue

    db.commit()
    print(f"✅ Seeded {len(ingredients_data)} ingredients")


def seed_substitutions(db):
    """Seed common substitution rules."""
    # Get ingredients
    substitutions_data = [
        # Dairy substitutions
        {"from": "Milk", "to": "Almond Milk", "ratio": 1.0, "quality": 0.9, "vegan": True, "dairy_free": True},
        {"from": "Milk", "to": "Soy Milk", "ratio": 1.0, "quality": 0.85, "vegan": True, "dairy_free": True},
        {"from": "Butter", "to": "Olive Oil", "ratio": 0.75, "quality": 0.7, "notes": "Use 3/4 cup oil for 1 cup butter"},
        {"from": "Butter", "to": "Coconut Oil", "ratio": 1.0, "quality": 0.8, "vegan": True, "dairy_free": True},
        {"from": "Cheese", "to": "Nutritional Yeast", "ratio": 0.5, "quality": 0.6, "vegan": True, "dairy_free": True},
        {"from": "Yogurt", "to": "Coconut Yogurt", "ratio": 1.0, "quality": 0.85, "vegan": True, "dairy_free": True},

        # Protein substitutions
        {"from": "Chicken Breast", "to": "Tofu", "ratio": 1.0, "quality": 0.7, "vegan": True, "vegetarian": True},
        {"from": "Chicken Breast", "to": "Turkey Breast", "ratio": 1.0, "quality": 0.95},
        {"from": "Beef", "to": "Tempeh", "ratio": 1.0, "quality": 0.65, "vegan": True, "vegetarian": True},
        {"from": "Beef", "to": "Lamb", "ratio": 1.0, "quality": 0.8},

        # Egg substitutions
        {"from": "Eggs", "to": "Flax Seeds", "ratio": 1.0, "quality": 0.75, "notes": "1 egg = 1 tbsp ground flax + 3 tbsp water", "vegan": True},
        {"from": "Eggs", "to": "Chia Seeds", "ratio": 1.0, "quality": 0.75, "notes": "1 egg = 1 tbsp chia + 3 tbsp water", "vegan": True},

        # Grain substitutions
        {"from": "Pasta", "to": "Zucchini", "ratio": 1.0, "quality": 0.6, "notes": "Use spiralized zucchini", "gluten_free": True},
        {"from": "Rice", "to": "Quinoa", "ratio": 1.0, "quality": 0.9, "gluten_free": True},
        {"from": "Rice", "to": "Cauliflower", "ratio": 1.0, "quality": 0.65, "notes": "Use riced cauliflower", "gluten_free": True},
        {"from": "Flour", "to": "Almond Flour", "ratio": 1.0, "quality": 0.7, "gluten_free": True},

        # Vegetable substitutions
        {"from": "Spinach", "to": "Kale", "ratio": 1.0, "quality": 0.9},
        {"from": "Broccoli", "to": "Cauliflower", "ratio": 1.0, "quality": 0.85},
        {"from": "Onion", "to": "Shallot", "ratio": 0.75, "quality": 0.8},
    ]

    count = 0
    for data in substitutions_data:
        try:
            from_ing = db.query(Ingredient).filter_by(normalized_name=data["from"].lower()).first()
            to_ing = db.query(Ingredient).filter_by(normalized_name=data["to"].lower()).first()

            if not from_ing:
                print(f"  ⚠️  Ingredient not found: {data['from']}")
                continue
            if not to_ing:
                print(f"  ⚠️  Substitute not found: {data['to']}")
                continue

            # Check if substitution already exists
            existing = db.query(SubstitutionRule).filter_by(
                ingredient_id=from_ing.id,
                substitute_id=to_ing.id
            ).first()

            if existing:
                continue

            sub = SubstitutionRule(
                ingredient_id=from_ing.id,
                substitute_id=to_ing.id,
                ratio=data.get("ratio", 1.0),
                quality_score=data.get("quality", 0.8),
                notes=data.get("notes"),
                is_vegan=data.get("vegan", False),
                is_vegetarian=data.get("vegetarian", False),
                is_gluten_free=data.get("gluten_free", False),
                is_dairy_free=data.get("dairy_free", False),
            )
            db.add(sub)
            count += 1

        except Exception as e:
            print(f"  ⚠️  Error creating substitution {data['from']} -> {data['to']}: {e}")
            continue

    db.commit()
    print(f"✅ Seeded {count} substitution rules")


def main():
    """Run all seed functions."""
    print("🌱 Starting ingredient taxonomy seed...\n")

    db = SessionLocal()

    try:
        # Seed in order (dependencies matter)
        allergen_map = seed_allergens(db)
        category_map = seed_categories(db)
        seed_ingredients(db, category_map, allergen_map)
        seed_substitutions(db)

        print("\n✅ Ingredient taxonomy seed complete!")
        print(f"   - {db.query(Allergen).count()} allergens")
        print(f"   - {db.query(IngredientCategory).count()} categories")
        print(f"   - {db.query(Ingredient).count()} ingredients")
        print(f"   - {db.query(SubstitutionRule).count()} substitution rules")

    except Exception as e:
        print(f"\n❌ Seed failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
