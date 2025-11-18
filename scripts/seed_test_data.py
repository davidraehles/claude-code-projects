"""
Seed test data for Phase 2 enhancements validation.

Creates users and recipes with various dietary tags for testing.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.user import User
from app.models.recipe import Recipe


def seed_test_data():
    """Seed database with test users and recipes."""
    db = SessionLocal()

    try:
        print("🌱 Seeding test data...")

        # Create test user
        test_user = db.query(User).filter_by(email="test@example.com").first()
        if not test_user:
            test_user = User(
                email="test@example.com",
                password_hash="$2b$12$8f0QVzCUAl4qwj8w1t7iMeD9prXxEZ6.nokFBxRKRnEU.gLY84YpO",  # Hashed "testpassword123"
                country="DE"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
        else:
            print(f"ℹ️  Test user already exists (ID: {test_user.id})")

        # Define test recipes with dietary tags
        test_recipes = [
            # Vegan recipes
            {
                "title": "Vegan Buddha Bowl",
                "ingredients": ["quinoa", "chickpeas", "kale", "tahini", "lemon"],
                "instructions": "Cook quinoa. Mix with roasted chickpeas, kale, tahini dressing.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 450, "protein": 15, "carbs": 65, "fat": 12},
                "prep_time": 15,
                "cook_time": 25
            },
            {
                "title": "Vegan Stir Fry",
                "ingredients": ["tofu", "broccoli", "bell peppers", "soy sauce", "ginger"],
                "instructions": "Stir fry tofu and vegetables with soy sauce and ginger.",
                "dietary_tags": ["vegan"],
                "nutrition": {"calories": 380, "protein": 18, "carbs": 35, "fat": 15},
                "prep_time": 10,
                "cook_time": 15
            },
            {
                "title": "Lentil Curry",
                "ingredients": ["red lentils", "coconut milk", "curry powder", "tomatoes", "onion"],
                "instructions": "Cook lentils with coconut milk, curry powder, and vegetables.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 420, "protein": 16, "carbs": 58, "fat": 14},
                "prep_time": 10,
                "cook_time": 30
            },

            # Vegetarian recipes (with dairy/eggs)
            {
                "title": "Vegetarian Pizza",
                "ingredients": ["pizza dough", "mozzarella cheese", "tomato sauce", "mushrooms", "bell peppers"],
                "instructions": "Top dough with sauce, cheese, and vegetables. Bake at 450°F.",
                "dietary_tags": ["vegetarian"],
                "nutrition": {"calories": 520, "protein": 20, "carbs": 65, "fat": 18},
                "prep_time": 15,
                "cook_time": 20
            },
            {
                "title": "Caprese Salad",
                "ingredients": ["tomatoes", "mozzarella", "basil", "olive oil", "balsamic vinegar"],
                "instructions": "Layer tomatoes and mozzarella. Drizzle with oil and vinegar.",
                "dietary_tags": ["vegetarian", "gluten_free"],
                "nutrition": {"calories": 280, "protein": 12, "carbs": 8, "fat": 22},
                "prep_time": 10,
                "cook_time": 0
            },

            # Gluten-free recipes
            {
                "title": "Grilled Salmon with Vegetables",
                "ingredients": ["salmon fillet", "asparagus", "lemon", "olive oil", "garlic"],
                "instructions": "Grill salmon and asparagus. Finish with lemon and garlic.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 480, "protein": 35, "carbs": 12, "fat": 32},
                "prep_time": 10,
                "cook_time": 20
            },
            {
                "title": "Quinoa Rice Bowl",
                "ingredients": ["quinoa", "brown rice", "vegetables", "olive oil"],
                "instructions": "Cook quinoa and rice. Mix with sautéed vegetables.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 390, "protein": 12, "carbs": 68, "fat": 8},
                "prep_time": 10,
                "cook_time": 35
            },

            # Regular recipes (no special tags)
            {
                "title": "Chicken Pasta",
                "ingredients": ["pasta", "chicken breast", "cream", "parmesan", "garlic"],
                "instructions": "Cook pasta. Sauté chicken. Mix with cream sauce.",
                "dietary_tags": [],
                "nutrition": {"calories": 620, "protein": 38, "carbs": 72, "fat": 18},
                "prep_time": 10,
                "cook_time": 25
            },
            {
                "title": "Beef Tacos",
                "ingredients": ["ground beef", "taco shells", "lettuce", "cheese", "salsa"],
                "instructions": "Cook beef. Assemble tacos with toppings.",
                "dietary_tags": [],
                "nutrition": {"calories": 550, "protein": 28, "carbs": 45, "fat": 28},
                "prep_time": 10,
                "cook_time": 15
            },
            {
                "title": "Spaghetti Carbonara",
                "ingredients": ["spaghetti", "bacon", "eggs", "parmesan", "black pepper"],
                "instructions": "Cook pasta. Mix with bacon, eggs, and cheese.",
                "dietary_tags": [],
                "nutrition": {"calories": 680, "protein": 32, "carbs": 78, "fat": 25},
                "prep_time": 10,
                "cook_time": 20
            },

            # Recipes for variety testing (additional)
            {
                "title": "Thai Green Curry (Vegan)",
                "ingredients": ["coconut milk", "green curry paste", "tofu", "vegetables", "basil"],
                "instructions": "Simmer coconut milk with curry paste. Add tofu and vegetables.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 460, "protein": 16, "carbs": 42, "fat": 26},
                "prep_time": 15,
                "cook_time": 25
            },
            {
                "title": "Mediterranean Chickpea Salad",
                "ingredients": ["chickpeas", "cucumbers", "tomatoes", "feta cheese", "olive oil"],
                "instructions": "Toss chickpeas with vegetables, feta, and dressing.",
                "dietary_tags": ["vegetarian", "gluten_free"],
                "nutrition": {"calories": 340, "protein": 14, "carbs": 38, "fat": 16},
                "prep_time": 15,
                "cook_time": 0
            },
            {
                "title": "Mushroom Risotto",
                "ingredients": ["arborio rice", "mushrooms", "vegetable broth", "parmesan", "white wine"],
                "instructions": "Cook rice slowly, adding broth. Stir in mushrooms and cheese.",
                "dietary_tags": ["vegetarian", "gluten_free"],
                "nutrition": {"calories": 520, "protein": 15, "carbs": 82, "fat": 14},
                "prep_time": 10,
                "cook_time": 35
            },
            {
                "title": "Black Bean Burrito Bowl",
                "ingredients": ["black beans", "rice", "avocado", "salsa", "cilantro"],
                "instructions": "Layer rice, beans, avocado, and salsa in bowl.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 490, "protein": 18, "carbs": 76, "fat": 14},
                "prep_time": 15,
                "cook_time": 20
            },
            {
                "title": "Greek Salad",
                "ingredients": ["cucumbers", "tomatoes", "red onion", "feta cheese", "olives"],
                "instructions": "Chop vegetables. Toss with feta and olives.",
                "dietary_tags": ["vegetarian", "gluten_free"],
                "nutrition": {"calories": 260, "protein": 10, "carbs": 12, "fat": 20},
                "prep_time": 10,
                "cook_time": 0
            },

            # More recipes to ensure enough for 21-meal plans
            {
                "title": "Vegan Tacos",
                "ingredients": ["black beans", "corn tortillas", "avocado", "salsa", "lettuce"],
                "instructions": "Fill tortillas with beans, avocado, and toppings.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 380, "protein": 14, "carbs": 62, "fat": 10},
                "prep_time": 10,
                "cook_time": 10
            },
            {
                "title": "Tomato Basil Pasta",
                "ingredients": ["pasta", "tomatoes", "basil", "garlic", "olive oil"],
                "instructions": "Cook pasta. Toss with fresh tomato sauce.",
                "dietary_tags": ["vegan"],
                "nutrition": {"calories": 420, "protein": 12, "carbs": 78, "fat": 8},
                "prep_time": 10,
                "cook_time": 15
            },
            {
                "title": "Roasted Vegetable Medley",
                "ingredients": ["zucchini", "bell peppers", "eggplant", "olive oil", "herbs"],
                "instructions": "Roast vegetables with olive oil and herbs.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 220, "protein": 5, "carbs": 32, "fat": 10},
                "prep_time": 15,
                "cook_time": 35
            },
            {
                "title": "Pesto Pasta",
                "ingredients": ["pasta", "basil pesto", "parmesan", "pine nuts", "olive oil"],
                "instructions": "Cook pasta. Toss with pesto and parmesan.",
                "dietary_tags": ["vegetarian"],
                "nutrition": {"calories": 580, "protein": 18, "carbs": 68, "fat": 26},
                "prep_time": 10,
                "cook_time": 15
            },
            {
                "title": "Vegetable Stir Fry",
                "ingredients": ["mixed vegetables", "soy sauce", "ginger", "garlic", "sesame oil"],
                "instructions": "Stir fry vegetables with sauce.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 280, "protein": 8, "carbs": 42, "fat": 10},
                "prep_time": 10,
                "cook_time": 12
            },
            {
                "title": "Chickpea Curry",
                "ingredients": ["chickpeas", "coconut milk", "curry powder", "spinach", "tomatoes"],
                "instructions": "Simmer chickpeas in curry sauce.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 410, "protein": 15, "carbs": 52, "fat": 16},
                "prep_time": 10,
                "cook_time": 25
            },
        ]

        # Create recipes
        recipes_created = 0
        for recipe_data in test_recipes:
            # Check if recipe already exists
            existing = db.query(Recipe).filter_by(
                user_id=test_user.id,
                title=recipe_data["title"]
            ).first()

            if not existing:
                recipe = Recipe(
                    user_id=test_user.id,
                    title=recipe_data["title"],
                    ingredients=recipe_data["ingredients"],
                    instructions=recipe_data["instructions"],
                    dietary_tags=recipe_data["dietary_tags"],
                    nutrition=recipe_data["nutrition"],
                    prep_time=recipe_data["prep_time"],
                    cook_time=recipe_data["cook_time"],
                    servings=2,
                    source_url=f"https://test.com/recipes/{recipe_data['title'].lower().replace(' ', '-')}",
                    source_type="html"
                )
                db.add(recipe)
                recipes_created += 1

        db.commit()

        # Summary
        total_recipes = db.query(Recipe).filter_by(user_id=test_user.id).count()
        vegan_count = db.query(Recipe).filter(
            Recipe.user_id == test_user.id,
            Recipe.dietary_tags.contains(["vegan"])
        ).count()
        vegetarian_count = db.query(Recipe).filter(
            Recipe.user_id == test_user.id,
            Recipe.dietary_tags.contains(["vegetarian"])
        ).count()
        gf_count = db.query(Recipe).filter(
            Recipe.user_id == test_user.id,
            Recipe.dietary_tags.contains(["gluten_free"])
        ).count()

        print(f"✅ Created {recipes_created} new recipes")
        print(f"\n📊 Test Data Summary:")
        print(f"   Total recipes: {total_recipes}")
        print(f"   Vegan recipes: {vegan_count}")
        print(f"   Vegetarian recipes: {vegetarian_count}")
        print(f"   Gluten-free recipes: {gf_count}")
        print(f"\n✅ Test data seeded successfully!")
        print(f"\nYou can now test with:")
        print(f"   User ID: {test_user.id}")
        print(f"   Email: {test_user.email}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_data()
