#!/usr/bin/env python3
"""
Simple test to add a known product to Rohlik/Knuspr cart.
Uses product IDs from the search results.
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
    print("🧀 Simple Cheese Cart Test")
    print("=" * 60)
    print()

    # Get credentials
    email = os.getenv("ROHLIK_USERNAME")
    password = os.getenv("ROHLIK_PASSWORD")
    country = os.getenv("ROHLIK_COUNTRY", "DE")

    if not email or not password:
        print("❌ Credentials not set")
        return

    print(f"📧 Email: {email}")
    print(f"🌍 Country: {country}")
    print()

    # Create client
    country_map = {"CZ": KnusprCountry.CZECH_REPUBLIC, "DE": KnusprCountry.GERMANY, "AT": KnusprCountry.AUSTRIA}
    knuspr_country = country_map.get(country.upper(), KnusprCountry.GERMANY)

    client = KnusprMCPClient(
        login_email=email,
        login_password=password,
        country=knuspr_country
    )

    try:
        # Step 1: Authenticate
        print("1️⃣  Authenticating...")
        auth_success = await client.authenticate()
        if not auth_success:
            print("❌ Authentication failed")
            return
        print("✅ Authenticated")
        print()

# Step 2: Add cheese products to cart
        # These are real Knuspr product IDs from Germany
        cheese_products = [
            {"product_id": 6272, "quantity": 1, "name": "Alnatura BIO Mozzarella"},
            {"product_id": 7012, "quantity": 1, "name": "Miil Gouda in Scheiben"},
            {"product_id": 27577, "quantity": 1, "name": "Alnatura BIO Cheddar"},
        ]

        print("2️⃣  Adding cheese products to cart...")
        print()

        for product in cheese_products:
            print(f"   Adding: {product['name']} (ID: {product['product_id']})")

        # Use the MCP add_to_cart tool directly
        result = await client._call_tool(
            "add_to_cart",
            products=[{"product_id": p["product_id"], "quantity": p["quantity"]} for p in cheese_products]
        )

        print()
        print(f"✅ {result}")
        print()
        print("🎉 Cheese products added to your Knuspr cart!")
        print()
        print(f"🛒 Cart URL: {client.get_domain()}")
        print("👉 Visit Knuspr.de and look for your cart to checkout!")

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
