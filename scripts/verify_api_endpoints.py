import requests
import json
import time
import uuid
import sys
from datetime import date, timedelta

# Configuration
BASE_URL = "https://claude-code-projects-production.up.railway.app"
API_V1 = f"{BASE_URL}/api/v1"

# Test Data
TEST_EMAIL = f"test_verify_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_COUNTRY = "DE"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
YELLOW = "\033[93m"

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ️ {message}{RESET}")

def verify_auth():
    print_info(f"Testing Authentication (D006)...")

    # 1. Register
    register_url = f"{API_V1}/auth/register"
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "country": TEST_COUNTRY
    }

    print(f"Registering user: {TEST_EMAIL}")
    response = requests.post(register_url, json=register_data)

    if response.status_code != 201:
        print_error(f"Registration failed: {response.status_code} - {response.text}")
        return None

    print_success("Registration successful")
    tokens = response.json()
    access_token = tokens.get("access_token")

    if not access_token:
        print_error("No access token returned")
        return None

    # 2. Login
    login_url = f"{API_V1}/auth/login"
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    print("Logging in...")
    response = requests.post(login_url, json=login_data)

    if response.status_code != 200:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None

    print_success("Login successful")

    # 3. Get Me
    me_url = f"{API_V1}/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(me_url, headers=headers)

    if response.status_code != 200:
        print_error(f"Get Me failed: {response.status_code} - {response.text}")
        return None

    user_data = response.json()
    if user_data["email"] != TEST_EMAIL:
        print_error(f"Email mismatch: expected {TEST_EMAIL}, got {user_data['email']}")
        return None

    print_success("Get Me successful")

    return access_token

def verify_recipe_import(access_token):
    print_info(f"Testing Recipe Import (D007)...")

    url = f"{API_V1}/recipes/harvest"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Ottolenghi recipes for bulk import
    recipes = [
        "https://ottolenghi.co.uk/pages/recipes/roasted-aubergine-with-curried-yoghurt",
        "https://ottolenghi.co.uk/pages/recipes/cauliflower-pomegranate-and-pistachio-salad",
        "https://ottolenghi.co.uk/pages/recipes/sweet-potato-galettes",
        "https://ottolenghi.co.uk/pages/recipes/portobello-steaks-and-butter-bean-mash",
        "https://ottolenghi.co.uk/pages/recipes/confit-tandoori-chickpeas",
        "https://ottolenghi.co.uk/pages/recipes/spicy-berbere-ratatouille-with-coconut-salsa",
        "https://ottolenghi.co.uk/pages/recipes/braised-eggs-with-leek-and-zaatar",
        "https://ottolenghi.co.uk/pages/recipes/one-pan-pasta-with-harissa-bolognese",
        "https://ottolenghi.co.uk/pages/recipes/sticky-miso-bananas-with-lime-and-toasted-rice",
        "https://ottolenghi.co.uk/pages/recipes/tangerine-and-ancho-chilli-flan"
    ]

    success_count = 0

    for recipe_url in recipes:
        data = {
            "url": recipe_url,
            "source_type": "html"
        }

        print(f"Harvesting recipe from: {recipe_url}")
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 202:
            print_success(f"Accepted: {recipe_url.split('/')[-1]}")
            success_count += 1
        else:
            print_error(f"Failed: {recipe_url} - {response.status_code}")

        # Small delay to be nice to the server
        time.sleep(1)

    if success_count == 0:
        print_error("All recipe harvest requests failed")
        return False

    print_success(f"Successfully queued {success_count} recipes for harvest")

    # Wait for harvesting to complete (simple wait for now)
    print("Waiting 30 seconds for harvesting to complete...")
    time.sleep(30)

    return True

def verify_recipe_list(access_token):
    print_info(f"Testing Recipe List (D008)...")

    url = f"{API_V1}/recipes"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print_error(f"Recipe list failed: {response.status_code} - {response.text}")
        return False

    data = response.json()
    if "items" not in data or "total" not in data:
        print_error("Invalid response format for recipe list")
        return False

    print_success(f"Recipe list successful. Found {data['total']} recipes.")

    # Quality check
    print_info("Performing quality check on recipes...")
    for recipe in data['items']:
        print(f"Checking: {recipe['title']}")

        # Check source URL
        if not recipe.get('source_url'):
            print_error(f"  Missing source URL for {recipe['title']}")
        else:
            print_success(f"  Source URL present: {recipe['source_url']}")

        # Check ingredients
        if not recipe.get('ingredients') or len(recipe['ingredients']) == 0:
            print_error(f"  No ingredients found for {recipe['title']}")
        else:
            print_success(f"  Ingredients found: {len(recipe['ingredients'])}")

    return True

def verify_meal_plan_generation(access_token):
    print_info(f"Testing Meal Plan Generation (D009)...")

    # Note: The route prefix in main.py is /api/v1/meal-plans (hyphen), not /api/v1/meal_plans (underscore)
    url = f"{API_V1}/meal-plans"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Now that we have imported recipes, we can try a proper meal plan
    start_date = (date.today() + timedelta(days=1)).isoformat()

    data = {
        "start_date": start_date,
        "num_days": 3,
        "num_people": 2,
        "dietary_restrictions": [],
        "meals_per_day": 3
    }

    print("Generating meal plan (3 days, 3 meals)...")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 202:
        print_error(f"Meal plan generation failed: {response.status_code} - {response.text}")
        return False

    meal_plan = response.json()
    if "id" not in meal_plan:
        print_error("No meal plan ID returned")
        return False

    print_success(f"Meal plan generation successful. ID: {meal_plan['id']}")
    return True

def verify_user_preferences(access_token):
    print_info(f"Testing User Preferences (D010)...")

    url = f"{API_V1}/users/preferences"
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Get Preferences
    print("Getting preferences...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print_error(f"Get preferences failed: {response.status_code} - {response.text}")
        return False

    # 2. Update Preferences
    print("Updating preferences...")
    update_data = {
        "dietary_restrictions": ["vegetarian", "gluten-free"],
        "theme": "dark",
        "language": "en"
    }

    response = requests.put(url, json=update_data, headers=headers)

    if response.status_code != 200:
        print_error(f"Update preferences failed: {response.status_code} - {response.text}")
        return False

    updated_prefs = response.json()
    if updated_prefs["preferences"].get("theme") != "dark":
        print_error("Preferences not updated correctly")
        return False

    print_success("User preferences verification successful")
    return True

def main():
    print("🚀 Starting Backend API Verification (Phase D2)")
    print(f"Target: {BASE_URL}")
    print("-" * 50)

    # D006: Auth
    access_token = verify_auth()
    if not access_token:
        print_error("Authentication verification failed. Aborting subsequent tests.")
        sys.exit(1)

    # D007: Recipe Import
    if not verify_recipe_import(access_token):
        print_error("Recipe Import verification failed")

    # Wait a bit for background tasks (optional, but good for stability)
    time.sleep(2)

    # D008: Recipe List
    if not verify_recipe_list(access_token):
        print_error("Recipe List verification failed")

    # D009: Meal Plan Generation
    if not verify_meal_plan_generation(access_token):
        print_error("Meal Plan Generation verification failed")

    # D010: User Preferences
    if not verify_user_preferences(access_token):
        print_error("User Preferences verification failed")

    print("-" * 50)
    print_success("🎉 Verification Complete!")

if __name__ == "__main__":
    main()
