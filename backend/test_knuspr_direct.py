#!/usr/bin/env python3
"""
Direct test of Knuspr API to add cheese to cart.
This bypasses the meal plan requirement by directly testing the Knuspr client.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry

async def main():
    print("🧀 Direct Knuspr Integration Test - Adding Cheese")
    print("=" * 60)
    print()

    # Get credentials from .env
    email = os.getenv("ROHLIK_USERNAME")
    password = os.getenv("ROHLIK_PASSWORD")
    country = os.getenv("ROHLIK_COUNTRY", "DE")

    if not email or not password:
        print("❌ ROHLIK_USERNAME or ROHLIK_PASSWORD not set in backend/.env")
        print("   Please add your Rohlik/Knuspr credentials")
        return

    print(f"📧 Using credentials: {email}")
    print()

    # Create Knuspr client
    country_map = {
        "CZ": KnusprCountry.CZECH_REPUBLIC,
        "DE": KnusprCountry.GERMANY,
        "AT": KnusprCountry.AUSTRIA
    }
    knuspr_country = country_map.get(country.upper(), KnusprCountry.GERMANY)

    client = KnusprMCPClient(
        login_email=email,
        login_password=password,
        country=knuspr_country
    )

    print(f"🌍 Country: {country} ({knuspr_country.value})")

    try:
        # Step 1: Authenticate
        print("1️⃣  Authenticating with Knuspr...")
        auth_success = await client.authenticate()
        if not auth_success:
            print("❌ Authentication failed")
            return
        print("✅ Authenticated successfully")
        print()

        # Step 2: Search for cheese products
        print("2️⃣  Searching for cheese products...")

        cheese_searches = ["cheddar", "mozzarella", "gouda"]
        found_products = []

        for cheese in cheese_searches:
            print(f"   Searching for: {cheese}")
            products = await client.search_products(cheese, max_results=3)
            if products:
                product = products[0]  # Take first match
                found_products.append(product)
                print(f"   ✅ Found: {product.name}")
                print(f"      ID: {product.product_id}, Price: €{product.price}")
            else:
                print(f"   ⚠️  No products found for {cheese}")

        print()
        print(f"📦 Found {len(found_products)} cheese products")
        print()

        if not found_products:
            print("❌ No products found. Cannot proceed.")
            return

        # Step 3: Create cart
        print("3️⃣  Creating Knuspr cart...")
        cart = await client.create_cart()
        if not cart or not cart.cart_id:
            print("❌ Failed to create cart")
            return

        print(f"✅ Created cart: {cart.cart_id}")
        print()

        # Step 4: Add cheese products to cart
        print("4️⃣  Adding cheese to cart...")

        for product in found_products:
            print(f"   Adding: {product.name}")
            success = await client.add_product_to_cart(
                cart_id=cart.cart_id,
                product_id=product.product_id,
                quantity=1
            )
            if success:
                print(f"   ✅ Added to cart")
            else:
                print(f"   ❌ Failed to add")

        print()

        # Step 5: Get cart URL
        print("5️⃣  Getting cart URL...")
        cart_url = await client.get_cart_url(cart.cart_id)

        if cart_url:
            print("🎉 Success! Cheese added to your Knuspr cart!")
            print("=" * 60)
            print()
            print(f"🛒 Cart URL: {cart_url}")
            print()
            print("👉 Open this URL in your browser to see your cheese! 🧀")
            print()
            print(f"📦 Cart contains {len(found_products)} items:")
            for product in found_products:
                print(f"   - {product.name} (€{product.price})")
        else:
            print("⚠️  Cart created but URL not available")
            print(f"   Cart ID: {cart.cart_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

    print()
    print("Done! 🧀")

if __name__ == "__main__":
    asyncio.run(main())
