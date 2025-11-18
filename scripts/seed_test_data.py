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

            # Additional recipes for better variety
            {
                "title": "Grilled Chicken Breast with Sweet Potato",
                "ingredients": ["chicken breast", "sweet potato", "olive oil", "rosemary", "garlic"],
                "instructions": "Grill chicken and roast sweet potatoes with herbs.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 520, "protein": 42, "carbs": 48, "fat": 12},
                "prep_time": 15,
                "cook_time": 30
            },
            {
                "title": "Tofu Scramble with Vegetables",
                "ingredients": ["firm tofu", "turmeric", "nutritional yeast", "spinach", "tomatoes"],
                "instructions": "Crumble and pan-fry tofu with turmeric and vegetables.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 240, "protein": 18, "carbs": 12, "fat": 14},
                "prep_time": 10,
                "cook_time": 15
            },
            {
                "title": "Tuna Salad",
                "ingredients": ["canned tuna", "mixed greens", "cherry tomatoes", "cucumber", "olive oil"],
                "instructions": "Mix tuna with fresh greens and vegetables.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 320, "protein": 32, "carbs": 15, "fat": 14},
                "prep_time": 10,
                "cook_time": 0
            },
            {
                "title": "Vegetarian Chili",
                "ingredients": ["kidney beans", "black beans", "tomatoes", "bell peppers", "onion"],
                "instructions": "Simmer beans and vegetables in spiced tomato sauce.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 380, "protein": 18, "carbs": 62, "fat": 6},
                "prep_time": 15,
                "cook_time": 40
            },
            {
                "title": "Teriyaki Salmon Bowl",
                "ingredients": ["salmon fillet", "brown rice", "broccoli", "teriyaki sauce", "sesame"],
                "instructions": "Bake salmon with teriyaki glaze. Serve over rice with broccoli.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 580, "protein": 38, "carbs": 48, "fat": 24},
                "prep_time": 15,
                "cook_time": 25
            },
            {
                "title": "Falafel Wrap",
                "ingredients": ["chickpeas", "whole wheat wrap", "tahini sauce", "lettuce", "tomatoes"],
                "instructions": "Make falafel patties. Serve in wrap with tahini sauce and veggies.",
                "dietary_tags": ["vegan"],
                "nutrition": {"calories": 450, "protein": 16, "carbs": 58, "fat": 18},
                "prep_time": 20,
                "cook_time": 20
            },
            {
                "title": "Egg White Omelet with Mushrooms",
                "ingredients": ["egg whites", "mushrooms", "spinach", "low-fat cheese", "olive oil"],
                "instructions": "Whisk egg whites. Cook with mushrooms and spinach.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 180, "protein": 24, "carbs": 8, "fat": 6},
                "prep_time": 10,
                "cook_time": 10
            },
            {
                "title": "Pad Thai (Vegetarian)",
                "ingredients": ["rice noodles", "peanut sauce", "tofu", "bell peppers", "peanuts"],
                "instructions": "Stir-fry noodles with peanut sauce and vegetables.",
                "dietary_tags": ["vegan"],
                "nutrition": {"calories": 520, "protein": 16, "carbs": 72, "fat": 16},
                "prep_time": 15,
                "cook_time": 20
            },
            {
                "title": "Baked Cod with Asparagus",
                "ingredients": ["cod fillet", "asparagus", "lemon", "garlic", "olive oil"],
                "instructions": "Bake cod and asparagus together with lemon and garlic.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 340, "protein": 40, "carbs": 12, "fat": 14},
                "prep_time": 10,
                "cook_time": 20
            },
            {
                "title": "Spinach and Feta Pie",
                "ingredients": ["spinach", "feta cheese", "phyllo dough", "olive oil", "dill"],
                "instructions": "Layer spinach and feta between phyllo sheets. Bake until crispy.",
                "dietary_tags": ["vegetarian"],
                "nutrition": {"calories": 480, "protein": 16, "carbs": 42, "fat": 28},
                "prep_time": 20,
                "cook_time": 35
            },
            {
                "title": "Vegetable Soup",
                "ingredients": ["mixed vegetables", "vegetable broth", "tomatoes", "herbs", "olive oil"],
                "instructions": "Simmer vegetables in broth with herbs.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 180, "protein": 6, "carbs": 36, "fat": 4},
                "prep_time": 15,
                "cook_time": 30
            },
            {
                "title": "Quinoa Stuffed Bell Peppers",
                "ingredients": ["bell peppers", "quinoa", "black beans", "corn", "cheese"],
                "instructions": "Stuff peppers with quinoa mixture. Bake until tender.",
                "dietary_tags": ["vegetarian", "gluten_free"],
                "nutrition": {"calories": 420, "protein": 16, "carbs": 58, "fat": 14},
                "prep_time": 15,
                "cook_time": 30
            },
            {
                "title": "Seared Scallops with Risotto",
                "ingredients": ["scallops", "arborio rice", "white wine", "parmesan", "butter"],
                "instructions": "Make risotto. Sear scallops and serve on top.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 620, "protein": 32, "carbs": 62, "fat": 24},
                "prep_time": 15,
                "cook_time": 40
            },
            {
                "title": "Black Bean and Sweet Potato Tacos",
                "ingredients": ["black beans", "sweet potato", "corn tortillas", "avocado", "salsa"],
                "instructions": "Roast sweet potatoes. Assemble tacos with beans and toppings.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 420, "protein": 12, "carbs": 68, "fat": 12},
                "prep_time": 15,
                "cook_time": 25
            },
            {
                "title": "Shrimp Scampi Pasta",
                "ingredients": ["shrimp", "pasta", "garlic", "white wine", "olive oil"],
                "instructions": "Cook pasta. Sauté shrimp in garlic and wine sauce.",
                "dietary_tags": [],
                "nutrition": {"calories": 520, "protein": 32, "carbs": 68, "fat": 12},
                "prep_time": 15,
                "cook_time": 20
            },
            {
                "title": "Miso Soup with Tofu",
                "ingredients": ["miso paste", "tofu", "seaweed", "green onions", "dashi"],
                "instructions": "Heat dashi. Add miso and tofu. Serve with seaweed.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 140, "protein": 12, "carbs": 10, "fat": 6},
                "prep_time": 10,
                "cook_time": 10
            },
            {
                "title": "Vegetable Frittata",
                "ingredients": ["eggs", "spinach", "mushrooms", "bell peppers", "cheese"],
                "instructions": "Beat eggs with vegetables. Cook in skillet until set.",
                "dietary_tags": ["vegetarian", "gluten_free"],
                "nutrition": {"calories": 320, "protein": 28, "carbs": 8, "fat": 20},
                "prep_time": 10,
                "cook_time": 20
            },
            {
                "title": "Coconut Curry Noodle Soup",
                "ingredients": ["rice noodles", "coconut milk", "curry paste", "vegetables", "basil"],
                "instructions": "Simmer noodles in coconut curry broth.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 380, "protein": 10, "carbs": 52, "fat": 16},
                "prep_time": 10,
                "cook_time": 20
            },
            {
                "title": "Herb-Roasted Turkey Breast",
                "ingredients": ["turkey breast", "rosemary", "thyme", "olive oil", "garlic"],
                "instructions": "Roast turkey breast with fresh herbs.",
                "dietary_tags": ["gluten_free"],
                "nutrition": {"calories": 380, "protein": 52, "carbs": 0, "fat": 18},
                "prep_time": 10,
                "cook_time": 45
            },
            {
                "title": "Vegan Chocolate Avocado Mousse",
                "ingredients": ["avocado", "cocoa powder", "maple syrup", "almond milk", "vanilla"],
                "instructions": "Blend avocado with cocoa and almond milk for dessert.",
                "dietary_tags": ["vegan", "gluten_free"],
                "nutrition": {"calories": 280, "protein": 4, "carbs": 28, "fat": 18},
                "prep_time": 10,
                "cook_time": 0
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
