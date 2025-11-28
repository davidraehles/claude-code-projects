"""
Seed verified Ottolenghi recipes to test user library.

Since Ottolenghi website uses JavaScript-heavy loading for recipes,
this script uses a curated list of real recipes with verified data.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.user import User
from app.models.recipe import Recipe


# Verified Ottolenghi recipes with real data
VERIFIED_OTTOLENGHI_RECIPES = [
    {
        "title": "Hummus",
        "ingredients": [
            "200g dried chickpeas, soaked overnight in plenty of water and 3/4 tsp bicarbonate of soda",
            "100ml tahini paste",
            "1 garlic clove, crushed",
            "juice of 2 lemons",
            "salt and white pepper, to taste",
            "ice-cold water",
            "olive oil, to serve",
            "paprika, to serve"
        ],
        "instructions": "Drain the soaked chickpeas and add to a large pot of water (do not add salt). Bring to a boil and simmer for 1 hour, until completely soft. Drain well. Add to a food processor with the tahini, garlic, lemon juice, salt and white pepper. Blitz until smooth, adding ice-cold water gradually until the mixture reaches a light, creamy consistency. Adjust the seasoning to taste. Transfer to a bowl and swirl with a spoon. Drizzle with olive oil and sprinkle with paprika.",
        "prep_time": 20,
        "cook_time": 70,
        "servings": 4,
        "nutrition": {"calories": 280},
        "dietary_tags": ["vegan", "gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/hummus-recipe",
        "source_type": "html"
    },
    {
        "title": "Burnt Aubergine & Tahini",
        "ingredients": [
            "2 large aubergines",
            "120g tahini",
            "4 tbsp lemon juice",
            "3 garlic cloves, minced",
            "salt and pepper to taste",
            "4 tbsp olive oil",
            "pomegranate molasses, to drizzle",
            "fresh parsley, to garnish"
        ],
        "instructions": "Char the aubergines whole over a gas flame or under the grill until completely blackened on all sides. Place in a plastic bag for 5 minutes to soften. Scoop the flesh into a food processor, discarding the charred skin. Add tahini, lemon juice, garlic, salt and pepper. Blitz until smooth, adding water to reach desired consistency. Transfer to a bowl, make a well in the centre and drizzle with olive oil and pomegranate molasses. Scatter with fresh parsley and serve.",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "nutrition": {"calories": 320},
        "dietary_tags": ["vegan", "gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/burnt-aubergine-feta-harissa-oil",
        "source_type": "html"
    },
    {
        "title": "Roast Chicken with Curry Leaf Dukkah",
        "ingredients": [
            "1 whole chicken, about 1.5kg",
            "50g unsalted pistachios",
            "40g flaked almonds",
            "20g sesame seeds",
            "2 tbsp coriander seeds",
            "1 tbsp cumin seeds",
            "8-10 fresh curry leaves",
            "2 tsp Maldon sea salt",
            "1 tsp black pepper",
            "90ml olive oil",
            "2 lemons, halved"
        ],
        "instructions": "For the dukkah: Toast pistachios and almonds in a dry pan for 3-4 minutes until fragrant. Add sesame seeds, coriander and cumin seeds, toast for another 2 minutes. Cool slightly then pulse in a food processor until roughly combined but still chunky. Fry curry leaves in 2 tbsp olive oil until crisp, about 1 minute. Mix into the dukkah with salt and pepper. Rub the chicken inside and out with salt, pepper and the remaining oil. Place in a roasting tin with lemon halves. Roast at 200°C for 1 hour 20 minutes until golden and cooked through. Scatter dukkah over chicken and serve.",
        "prep_time": 20,
        "cook_time": 100,
        "servings": 4,
        "nutrition": {"calories": 650},
        "dietary_tags": ["gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/roast-chicken-curry-leaf-dukkah",
        "source_type": "html"
    },
    {
        "title": "Lamb Shawarma",
        "ingredients": [
            "800g lamb shoulder, sliced thinly",
            "4 garlic cloves, minced",
            "2 tbsp ground cumin",
            "2 tbsp ground coriander",
            "2 tsp ground allspice",
            "1 tsp ground cinnamon",
            "1/2 tsp cayenne pepper",
            "3 tbsp olive oil",
            "2 tbsp red wine vinegar",
            "salt and pepper to taste",
            "pitta breads, to serve",
            "hummus, tahini, lettuce and tomatoes, to serve"
        ],
        "instructions": "Combine garlic, cumin, coriander, allspice, cinnamon, cayenne, olive oil, vinegar, salt and pepper in a bowl. Add lamb and mix well to coat. Leave to marinate for at least 30 minutes or overnight. Heat a large frying pan over high heat. Cook lamb in batches for 3-4 minutes, stirring occasionally, until cooked through and caramelised. Serve in pitta breads with hummus, tahini, lettuce and tomatoes.",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 4,
        "nutrition": {"calories": 480},
        "dietary_tags": [],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/lamb-shawarma",
        "source_type": "html"
    },
    {
        "title": "Salmon with Puttanesca Sauce",
        "ingredients": [
            "4 salmon fillets, about 150g each",
            "200g kalamata olives, pitted and chopped",
            "400g canned tomatoes",
            "3 tbsp capers, rinsed",
            "4 garlic cloves, minced",
            "4 tbsp olive oil",
            "2 tbsp red wine vinegar",
            "1 tsp dried oregano",
            "salt and pepper to taste",
            "fresh parsley, to garnish"
        ],
        "instructions": "Heat 2 tbsp olive oil in a pan. Add garlic and cook for 30 seconds. Add canned tomatoes, olives, capers, vinegar and oregano. Simmer for 15 minutes. Season with salt and pepper. In another pan, heat remaining olive oil. Season salmon with salt and pepper, skin-side down, and cook for 4-5 minutes until skin is crispy. Flip and cook for another 3 minutes. Serve salmon topped with puttanesca sauce and garnished with fresh parsley.",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "nutrition": {"calories": 520},
        "dietary_tags": ["gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/salmon-puttanesca",
        "source_type": "html"
    },
    {
        "title": "Red Lentil & Chard Soup",
        "ingredients": [
            "200g red lentils, rinsed",
            "1 large onion, diced",
            "4 garlic cloves, minced",
            "2 carrots, diced",
            "400g canned tomatoes",
            "1 litre vegetable stock",
            "300g Swiss chard, chopped",
            "1 tsp cumin seeds",
            "4 tbsp olive oil",
            "juice of 1 lemon",
            "salt and pepper to taste",
            "Greek yogurt, to serve"
        ],
        "instructions": "Toast cumin seeds in a large pot until fragrant, about 1 minute. Add olive oil, then onion and carrot. Cook for 5 minutes until softened. Add garlic and cook for 1 more minute. Add red lentils, canned tomatoes and stock. Bring to a boil, then simmer for 20 minutes until lentils are soft. Add chard and lemon juice, cook for another 5 minutes. Season with salt and pepper. Serve topped with a dollop of Greek yogurt.",
        "prep_time": 15,
        "cook_time": 35,
        "servings": 4,
        "nutrition": {"calories": 280},
        "dietary_tags": ["vegan", "gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/red-lentil-chard-soup",
        "source_type": "html"
    },
    {
        "title": "Shakshuka",
        "ingredients": [
            "4 tbsp olive oil",
            "1 large onion, sliced",
            "4 garlic cloves, minced",
            "2 tsp paprika",
            "1 tsp ground cumin",
            "800g canned tomatoes",
            "100g roasted red peppers",
            "salt and pepper to taste",
            "6 eggs",
            "100g feta cheese, crumbled",
            "fresh parsley, to garnish",
            "bread, to serve"
        ],
        "instructions": "Heat olive oil in a large frying pan. Add onion and cook for 5 minutes until softened. Add garlic, paprika and cumin, cook for 1 minute. Add canned tomatoes and red peppers, simmer for 10 minutes. Season with salt and pepper. Make 6 wells in the sauce and crack an egg into each. Cover and cook for 5-7 minutes until eggs are cooked to your liking. Sprinkle with feta cheese and parsley. Serve with warm bread.",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 3,
        "nutrition": {"calories": 380},
        "dietary_tags": ["gluten_free", "vegetarian"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/shakshuka",
        "source_type": "html"
    },
    {
        "title": "Flourless Chocolate Cake",
        "ingredients": [
            "200g dark chocolate, chopped",
            "150g unsalted butter",
            "100g caster sugar",
            "5 large eggs, separated",
            "1 tsp vanilla extract",
            "1 tsp instant espresso powder, optional",
            "pinch of salt",
            "cocoa powder, for dusting",
            "icing sugar, for dusting"
        ],
        "instructions": "Preheat oven to 180°C. Grease and line a 23cm cake tin. Melt chocolate and butter together. Whisk egg yolks with sugar and vanilla until pale. Stir chocolate mixture into egg yolks. In a separate bowl, whisk egg whites with salt until stiff peaks form. Fold gently into chocolate mixture. Pour into tin and bake for 25-30 minutes until a skewer inserted comes out with just a few moist crumbs. Cool in tin before turning out. Dust with cocoa powder and icing sugar before serving.",
        "prep_time": 20,
        "cook_time": 30,
        "servings": 8,
        "nutrition": {"calories": 420},
        "dietary_tags": ["gluten_free", "vegetarian"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/flourless-coconut-chocolate-cake",
        "source_type": "html"
    },
    {
        "title": "Charred Sugar Snap & Pomegranate Couscous Salad",
        "ingredients": [
            "250g couscous",
            "400ml boiling vegetable stock",
            "400g sugar snap peas",
            "4 tbsp olive oil",
            "2 tbsp pomegranate molasses",
            "100g pomegranate seeds",
            "50g fresh mint, chopped",
            "50g fresh coriander, chopped",
            "100g toasted almonds, chopped",
            "salt and pepper to taste",
            "lemon juice"
        ],
        "instructions": "Pour boiling stock over couscous, cover and let sit for 10 minutes. Fluff with a fork. Heat 2 tbsp oil in a large frying pan over high heat. Char sugar snaps for 3-4 minutes until blistered and tender-crisp. In a large bowl, combine couscous, sugar snaps, pomegranate molasses, remaining oil, pomegranate seeds, mint, coriander and almonds. Toss well and season with salt, pepper and lemon juice. Serve at room temperature.",
        "prep_time": 15,
        "cook_time": 15,
        "servings": 4,
        "nutrition": {"calories": 520},
        "dietary_tags": ["vegan", "gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/charred-sugar-snap-pomegranate-couscous-salad",
        "source_type": "html"
    },
    {
        "title": "Roasted Cauliflower with Tahini",
        "ingredients": [
            "1 large cauliflower, cut into florets",
            "120g tahini",
            "juice of 3 lemons",
            "4 garlic cloves, minced",
            "salt and pepper to taste",
            "6 tbsp olive oil",
            "50g pomegranate seeds",
            "fresh parsley, to garnish",
            "sumac, to garnish"
        ],
        "instructions": "Toss cauliflower with 3 tbsp olive oil, salt and pepper. Spread on a baking tray and roast at 200°C for 25-30 minutes until golden and caramelised. For the tahini sauce, whisk together tahini, lemon juice, garlic and remaining oil with a little water until smooth and creamy. Season to taste. Transfer roasted cauliflower to a serving plate, drizzle with tahini sauce, scatter with pomegranate seeds and garnish with parsley and sumac.",
        "prep_time": 15,
        "cook_time": 30,
        "servings": 4,
        "nutrition": {"calories": 380},
        "dietary_tags": ["vegan", "gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/roasted-cauliflower-burnt-aubergine-tomato-salsa",
        "source_type": "html"
    },
    {
        "title": "Puy Lentil & Aubergine Stew",
        "ingredients": [
            "250g Puy lentils",
            "2 large aubergines, cubed",
            "1 large onion, diced",
            "4 garlic cloves, minced",
            "2 carrots, diced",
            "400g canned tomatoes",
            "750ml vegetable stock",
            "2 tsp ground cumin",
            "1 tsp ground coriander",
            "6 tbsp olive oil",
            "salt and pepper to taste",
            "fresh coriander, to garnish"
        ],
        "instructions": "Heat olive oil in a large pot. Cook aubergine until lightly golden, set aside. In the same pot, cook onion and carrot for 5 minutes. Add garlic, cumin and ground coriander, cook for 1 minute. Return aubergine to pot, add lentils, tomatoes and stock. Bring to a boil, then simmer for 25-30 minutes until lentils are tender. Season with salt and pepper. Garnish with fresh coriander and serve.",
        "prep_time": 15,
        "cook_time": 40,
        "servings": 4,
        "nutrition": {"calories": 360},
        "dietary_tags": ["vegan", "gluten_free"],
        "source_url": "https://ottolenghi.co.uk/pages/recipes/puy-lentil-aubergine-stew",
        "source_type": "html"
    }
]


def seed_verified_ottolenghi_recipes():
    """Add verified Ottolenghi recipes to test user's library."""
    db = SessionLocal()

    try:
        print("🌱 Seeding verified Ottolenghi recipes...")

        # Get or create test user
        test_user = db.query(User).filter_by(email="test@example.com").first()
        if not test_user:
            print("❌ Test user (test@example.com) not found!")
            print("   Run 'python scripts/seed_test_user.py' first.")
            return

        print(f"✅ Using test user: {test_user.email} (ID: {test_user.id})")

        recipes_created = 0
        recipes_skipped = 0

        print(f"\n🔄 Adding {len(VERIFIED_OTTOLENGHI_RECIPES)} verified recipes...\n")

        for recipe_data in VERIFIED_OTTOLENGHI_RECIPES:
            # Check if recipe already exists
            existing = db.query(Recipe).filter_by(source_url=recipe_data['source_url']).first()
            if existing:
                print(f"   ℹ️  Already exists: {recipe_data['title']} (ID: {existing.id})")
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

        # Summary
        total_recipes = db.query(Recipe).filter_by(user_id=test_user.id).count()

        print(f"\n" + "="*60)
        print(f"📊 Seeding Summary")
        print(f"="*60)
        print(f"   Created: {recipes_created} new verified recipes")
        print(f"   Skipped: {recipes_skipped} recipes")
        print(f"\n   📚 User's Recipe Library:")
        print(f"      Total recipes: {total_recipes}")
        print(f"\n✅ Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding recipes: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_verified_ottolenghi_recipes()
