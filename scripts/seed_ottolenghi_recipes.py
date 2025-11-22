"""
Seed Ottolenghi recipes to test user library.

Scrapes recipes from https://ottolenghi.co.uk/pages/recipes and adds them
to the default test user's recipe library on Railway.
"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import json
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.user import User
from app.models.recipe import Recipe


# List of Ottolenghi recipe URLs discovered
OTTOLENGHI_RECIPES = [
    "https://ottolenghi.co.uk/pages/recipes/smoky-creamy-pasta-burnt-aubergine-tahini",
    "https://ottolenghi.co.uk/pages/recipes/burnt-aubergine-feta-harissa-oil",
    "https://ottolenghi.co.uk/pages/recipes/roasted-cauliflower-burnt-aubergine-tomato-salsa",
    "https://ottolenghi.co.uk/pages/recipes/cauliflower-soup-mustard-croutons",
    "https://ottolenghi.co.uk/pages/recipes/puy-lentil-aubergine-stew",
    "https://ottolenghi.co.uk/pages/recipes/couscous-grilled-cherry-tomatoes-fresh-herbs",
    "https://ottolenghi.co.uk/pages/recipes/charred-sugar-snap-pomegranate-couscous-salad",
    "https://ottolenghi.co.uk/pages/recipes/roast-chicken-curry-leaf-dukkah",
    "https://ottolenghi.co.uk/pages/recipes/lamb-shawarma",
    "https://ottolenghi.co.uk/pages/recipes/salmon-puttanesca",
    "https://ottolenghi.co.uk/pages/recipes/zaatar-salmon-tahini",
    "https://ottolenghi.co.uk/pages/recipes/puttanesca-style-salmon-bake",
    "https://ottolenghi.co.uk/pages/recipes/chermoula-marinated-sea-bass-olives-preserved-lemon",
    "https://ottolenghi.co.uk/pages/recipes/fish-prawn-pirao",
    "https://ottolenghi.co.uk/pages/recipes/ottolenghi-chicken-soup",
    "https://ottolenghi.co.uk/pages/recipes/red-lentil-chard-soup",
    "https://ottolenghi.co.uk/pages/recipes/irish-stew",
    "https://ottolenghi.co.uk/pages/recipes/chicken-parmesan-soup-pappardelle",
    "https://ottolenghi.co.uk/pages/recipes/spicy-chicken-cabbage-soup",
    "https://ottolenghi.co.uk/pages/recipes/cold-yoghurt-soup",
    "https://ottolenghi.co.uk/pages/recipes/chickpea-tomato-bread-soup",
    "https://ottolenghi.co.uk/pages/recipes/shakshuka",
    "https://ottolenghi.co.uk/pages/recipes/egg-sambal-shakshuka",
    "https://ottolenghi.co.uk/pages/recipes/vs-fluffy-pancakes",
    "https://ottolenghi.co.uk/pages/recipes/cheese-chorizo-spring-onion-pancakes",
    "https://ottolenghi.co.uk/pages/recipes/flourless-coconut-chocolate-cake",
    "https://ottolenghi.co.uk/pages/recipes/take-home-chocolate-cake",
    "https://ottolenghi.co.uk/pages/recipes/clementine-almond-syrup-cake",
    "https://ottolenghi.co.uk/pages/recipes/hummus-recipe",
    "https://ottolenghi.co.uk/pages/recipes/chickpea-chard-feta-puffs-green-harissa",
    "https://ottolenghi.co.uk/pages/recipes/butterbean-hummus-red-pepper-walnut-paste",
]


def extract_title_from_url(url: str) -> str:
    """Extract a human-readable title from the recipe URL."""
    slug = url.split("/")[-1]
    # Convert slug to title case
    title = slug.replace("-", " ").title()
    return title


def is_valid_recipe(recipe_data: Dict) -> bool:
    """Validate that recipe has substantial content, not just placeholders."""
    # Check if instructions are just placeholders
    if any(placeholder in recipe_data['instructions'].lower() for placeholder in [
        'visit the ottolenghi website',
        'follow the recipe steps',
        'see recipe on website'
    ]):
        return False

    # Check if ingredients are just placeholders
    if len(recipe_data['ingredients']) == 1 and any(phrase in recipe_data['ingredients'][0].lower() for phrase in [
        'see recipe on website',
        'ingredient 1'
    ]):
        return False

    # Check for minimum meaningful content
    if len(recipe_data['ingredients']) < 3:
        return False

    if len(recipe_data['instructions']) < 100:
        return False

    return True


def extract_recipe_data(url: str, html_content: str) -> Optional[Dict]:
    """Extract recipe data from HTML content using common recipe markup patterns."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Try to extract from JSON-LD structured data (most reliable)
    # Look for all JSON-LD scripts, not just the first one
    json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

    for json_ld in json_ld_scripts:
        try:
            data = json.loads(json_ld.string)

            # Handle case where data might be wrapped in an array
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Recipe':
                        data = item
                        break

            if data.get('@type') == 'Recipe':
                title = data.get('name', extract_title_from_url(url))

                # Extract ingredients
                ingredients = []
                ingredient_list = data.get('recipeIngredient', [])
                if ingredient_list:
                    ingredients = ingredient_list if isinstance(ingredient_list, list) else [ingredient_list]

                # If no ingredients from JSON-LD, create basic ones
                if not ingredients:
                    ingredients = [f"Ingredient {i+1}" for i in range(3)]

                # Extract instructions
                instructions = ""
                instructions_list = data.get('recipeInstructions', [])
                if isinstance(instructions_list, list):
                    # Handle both text and object formats
                    instruction_steps = []
                    for item in instructions_list:
                        if isinstance(item, dict):
                            instruction_steps.append(item.get('text', ''))
                        else:
                            instruction_steps.append(str(item))
                    instructions = " ".join(instruction_steps)
                else:
                    instructions = str(instructions_list)

                # If no instructions, use a default
                if not instructions or len(instructions) < 10:
                    instructions = "Follow the recipe steps as outlined on the website."

                # Extract times
                prep_time = None
                cook_time = None

                if 'prepTime' in data:
                    # Parse ISO 8601 duration (e.g., "PT15M")
                    prep_str = data.get('prepTime', '')
                    prep_time = parse_iso_duration(prep_str)

                if 'cookTime' in data:
                    cook_str = data.get('cookTime', '')
                    cook_time = parse_iso_duration(cook_str)

                # Extract servings
                servings = None
                yields = data.get('recipeYield')
                if yields:
                    if isinstance(yields, list):
                        servings_str = yields[0]
                    else:
                        servings_str = yields
                    # Try to extract number from "4 servings"
                    try:
                        servings = int(''.join(filter(str.isdigit, str(servings_str).split()[0])))
                    except:
                        servings = 2
                else:
                    servings = 2

                # Extract nutrition
                nutrition = {}
                nutrition_info = data.get('nutrition', {})
                if isinstance(nutrition_info, dict):
                    if 'calories' in nutrition_info:
                        nutrition['calories'] = nutrition_info['calories']
                    if 'carbohydrateContent' in nutrition_info:
                        nutrition['carbs'] = nutrition_info['carbohydrateContent']
                    if 'proteinContent' in nutrition_info:
                        nutrition['protein'] = nutrition_info['proteinContent']
                    if 'fatContent' in nutrition_info:
                        nutrition['fat'] = nutrition_info['fatContent']

                # Determine dietary tags based on recipe content
                dietary_tags = []
                recipe_text = (title + " " + instructions + " " + " ".join(ingredients)).lower()

                if any(word in recipe_text for word in ['vegan', 'plant-based']):
                    dietary_tags.append('vegan')
                elif any(word in recipe_text for word in ['vegetarian', 'no meat']):
                    dietary_tags.append('vegetarian')

                if any(word in recipe_text for word in ['gluten free', 'gluten-free', 'gf']):
                    dietary_tags.append('gluten_free')

                if any(word in recipe_text for word in ['dairy free', 'dairy-free']):
                    dietary_tags.append('dairy_free')

                return {
                    'title': title,
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'prep_time': prep_time or 15,
                    'cook_time': cook_time or 30,
                    'servings': servings,
                    'nutrition': nutrition,
                    'dietary_tags': dietary_tags,
                    'source_url': url,
                    'source_type': 'html'
                }
        except Exception as e:
            # Continue to next JSON-LD block if parsing fails
            continue

    # Fallback: Create basic recipe from URL
    return {
        'title': extract_title_from_url(url),
        'ingredients': ['See recipe on website for full ingredients list'],
        'instructions': 'Visit the Ottolenghi website for complete instructions.',
        'prep_time': 20,
        'cook_time': 30,
        'servings': 4,
        'nutrition': {'calories': 500},
        'dietary_tags': [],
        'source_url': url,
        'source_type': 'html'
    }


def parse_iso_duration(duration_str: str) -> Optional[int]:
    """Parse ISO 8601 duration string (e.g., 'PT15M' -> 15 minutes)."""
    if not duration_str:
        return None

    try:
        # Remove 'PT' prefix
        duration_str = duration_str.replace('PT', '')

        # Extract minutes
        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0])
            return minutes

        # Extract hours and convert to minutes
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0])
            return hours * 60
    except:
        pass

    return None


def fetch_recipe_page(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch a recipe page and return HTML content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"   ❌ Failed to fetch {url}: {e}")
        return None


def seed_ottolenghi_recipes():
    """Scrape Ottolenghi recipes and add them to test user's library."""
    db = SessionLocal()

    try:
        print("🌱 Seeding Ottolenghi recipes...")

        # Get or create test user
        test_user = db.query(User).filter_by(email="test@example.com").first()
        if not test_user:
            print("❌ Test user (test@example.com) not found!")
            print("   Run 'python scripts/seed_test_user.py' first.")
            return

        print(f"✅ Using test user: {test_user.email} (ID: {test_user.id})")

        recipes_created = 0
        recipes_skipped = 0

        print(f"\n🔄 Fetching {len(OTTOLENGHI_RECIPES)} recipes...")

        for idx, url in enumerate(OTTOLENGHI_RECIPES, 1):
            print(f"\n[{idx}/{len(OTTOLENGHI_RECIPES)}] Processing: {url.split('/')[-1]}")

            # Add a small delay to be respectful to the server
            if idx > 1:
                time.sleep(2)

            # Check if recipe already exists
            existing = db.query(Recipe).filter_by(source_url=url).first()
            if existing:
                print(f"   ℹ️  Recipe already exists (ID: {existing.id})")
                recipes_skipped += 1
                continue

            # Fetch recipe page
            html_content = fetch_recipe_page(url)
            if not html_content:
                recipes_skipped += 1
                continue

            # Extract recipe data
            recipe_data = extract_recipe_data(url, html_content)

            # Validate recipe has actual content, not placeholders
            if not is_valid_recipe(recipe_data):
                print(f"   ⏭️  Skipped: Recipe lacks sufficient content (no JSON-LD found)")
                recipes_skipped += 1
                continue

            # Create recipe
            try:
                recipe = Recipe(
                    user_id=test_user.id,
                    title=recipe_data['title'],
                    ingredients=recipe_data['ingredients'],
                    instructions=recipe_data['instructions'],
                    prep_time=recipe_data['prep_time'],
                    cook_time=recipe_data['cook_time'],
                    servings=recipe_data['servings'],
                    nutrition=recipe_data['nutrition'],
                    dietary_tags=recipe_data['dietary_tags'],
                    source_url=recipe_data['source_url'],
                    source_type=recipe_data['source_type']
                )
                db.add(recipe)
                db.commit()
                db.refresh(recipe)

                tags = f" ({', '.join(recipe_data['dietary_tags'])})" if recipe_data['dietary_tags'] else ""
                print(f"   ✅ Created: {recipe_data['title']}{tags}")
                recipes_created += 1
            except Exception as e:
                db.rollback()
                print(f"   ❌ Error creating recipe: {e}")
                recipes_skipped += 1

        # Summary - get total count only (dietary tags querying has JSON compatibility issues)
        total_recipes = db.query(Recipe).filter_by(user_id=test_user.id).count()

        print(f"\n" + "="*60)
        print(f"📊 Seeding Summary")
        print(f"="*60)
        print(f"   Created: {recipes_created} new Ottolenghi recipes")
        print(f"   Skipped: {recipes_skipped} recipes")
        print(f"\n   📚 User's Recipe Library:")
        print(f"      Total recipes: {total_recipes}")
        print(f"\n✅ Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding Ottolenghi recipes: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_ottolenghi_recipes()
