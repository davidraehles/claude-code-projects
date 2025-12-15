#!/usr/bin/env python3
"""
Test script to add cheese to Knuspr cart using real credentials.
This script uses the backend API to create a cart and fill it with cheese items.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"
KNUSPR_EMAIL = os.getenv("ROHLIK_USERNAME")
KNUSPR_PASSWORD = os.getenv("ROHLIK_PASSWORD")

print("🧀 Testing Knuspr Integration - Adding Cheese to Cart")
print("=" * 60)
print()

# Step 1: Check backend health
print("1️⃣  Checking backend status...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    response.raise_for_status()
    print("✅ Backend is running")
    print(f"   Status: {response.json().get('status', 'unknown')}")
except Exception as e:
    print(f"❌ Backend is not reachable: {e}")
    print(f"   Make sure backend is running at {BACKEND_URL}")
    sys.exit(1)

print()

# Step 2: Login or register test user
print("2️⃣  Authenticating test user...")
test_email = "cheese-tester@example.com"
test_password = "CheeseTest123!"

# Try to register (will fail if user exists, that's ok)
try:
    register_response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "country": "DE"
        },
        timeout=10
    )
    if register_response.status_code in [200, 201]:
        print(f"✅ Registered new test user: {test_email}")
    elif register_response.status_code == 400:
        print(f"ℹ️  User already exists: {test_email}")
    else:
        print(f"⚠️  Registration response: {register_response.status_code}")
except Exception as e:
    print(f"⚠️  Registration failed (may already exist): {e}")

# Login
try:
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "email": test_email,
            "password": test_password
        },
        timeout=10
    )
    login_response.raise_for_status()
    jwt_token = login_response.json()["access_token"]
    print(f"✅ Logged in successfully")
except Exception as e:
    print(f"❌ Login failed: {e}")
    sys.exit(1)

print()

# Step 3: Create grocery cart with cheese
print("3️⃣  Creating grocery cart with cheese items...")
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

cheese_items = [
    {
        "name": "Cheddar Cheese",
        "quantity": "200g",
        "category": "dairy"
    },
    {
        "name": "Mozzarella",
        "quantity": "250g",
        "category": "dairy"
    },
    {
        "name": "Gouda",
        "quantity": "300g",
        "category": "dairy"
    }
]

try:
    # Create a minimal meal plan first (without recipes)
    meal_plan_response = requests.post(
        f"{API_BASE}/meal-plans",
        headers=headers,
        json={
            "name": "Cheese Shopping",
            "start_date": "2025-12-14",
            "end_date": "2025-12-14",
            "num_days": 1,
            "dietary_preferences": [],
            "recipes": []  # Empty recipes
        },
        timeout=10
    )

    if meal_plan_response.status_code in [200, 201]:
        meal_plan_id = meal_plan_response.json()["id"]
        print(f"✅ Created meal plan: {meal_plan_id}")
    else:
        print(f"⚠️  Could not create meal plan: {meal_plan_response.status_code}")
        print(f"   Response: {meal_plan_response.text[:200]}")
        # Try without recipes field
        meal_plan_response = requests.post(
            f"{API_BASE}/meal-plans",
            headers=headers,
            json={
                "name": "Cheese Shopping",
                "num_days": 1
            },
            timeout=10
        )
        meal_plan_response.raise_for_status()
        meal_plan_id = meal_plan_response.json()["id"]
        print(f"✅ Created meal plan (simplified): {meal_plan_id}")

    # Create grocery cart with cheese items
    cart_response = requests.post(
        f"{API_BASE}/grocery-carts",
        headers=headers,
        json={
            "meal_plan_id": meal_plan_id,
            "items": cheese_items
        },
        timeout=10
    )

    cart_response.raise_for_status()
    cart_data = cart_response.json()
    cart_id = cart_data.get("id")
    print(f"✅ Created cart: {cart_id}")
    print(f"   Items: {len(cheese_items)} cheese products")

except Exception as e:
    print(f"❌ Failed to create cart: {e}")
    if hasattr(e, 'response'):
        print(f"   Response: {e.response.text}")
    sys.exit(1)

print()

# Step 4: Fill Knuspr cart
print("4️⃣  Filling Knuspr cart with cheese...")
print(f"   Using credentials from .env: {KNUSPR_EMAIL}")

if not KNUSPR_EMAIL or not KNUSPR_PASSWORD:
    print("❌ ROHLIK_USERNAME or ROHLIK_PASSWORD not set in backend/.env")
    print("   Please add your Rohlik/Knuspr credentials to backend/.env:")
    print("   ROHLIK_USERNAME=your-email@example.com")
    print("   ROHLIK_PASSWORD=your-password")
    sys.exit(1)

try:
    fill_response = requests.post(
        f"{API_BASE}/workflows/carts/{cart_id}/fill-knuspr",
        headers=headers,
        json={
            "credentials": {
                "email": KNUSPR_EMAIL,
                "password": KNUSPR_PASSWORD,
                "country": "de"
            },
            "match_preferences": {
                "min_confidence": 0.6,
                "allow_substitutions": True,
                "prefer_organic": False
            }
        },
        timeout=120  # Knuspr API can be slow
    )

    print(f"   Response status: {fill_response.status_code}")

    if fill_response.status_code == 200:
        result = fill_response.json()

        print()
        print("🎉 Success! Cheese added to Knuspr cart!")
        print("=" * 60)
        print()

        print("📊 Results:")
        print(f"   ✅ Matched items: {len(result.get('matched_items', []))}")
        print(f"   ❌ Unmatched items: {len(result.get('unmatched_items', []))}")

        if result.get('knuspr_cart_url'):
            print(f"   🛒 Cart URL: {result['knuspr_cart_url']}")
            print()
            print(f"   👉 Open this URL to see your cheese cart! 🧀")

        print()
        if result.get('matched_items'):
            print("📦 Matched Items:")
            for item in result['matched_items']:
                print(f"   ✅ {item['name']} → {item['knuspr_product_name']}")
                print(f"      Product ID: {item['knuspr_product_id']}")

        if result.get('unmatched_items'):
            print()
            print("⚠️  Unmatched Items:")
            for item in result['unmatched_items']:
                print(f"   ❌ {item['name']}")

    else:
        print(f"❌ Failed to fill Knuspr cart")
        print(f"   Status: {fill_response.status_code}")
        print(f"   Response: {fill_response.text}")

except Exception as e:
    print(f"❌ Error filling Knuspr cart: {e}")
    if hasattr(e, 'response'):
        print(f"   Response: {e.response.text}")
    sys.exit(1)

print()
print("Done! 🧀")
