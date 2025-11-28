import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry

async def main():
    load_dotenv()

    email = os.getenv("ROHLIK_USERNAME")
    password = os.getenv("ROHLIK_PASSWORD")

    if not email or not password:
        print("Error: ROHLIK_USERNAME or ROHLIK_PASSWORD not set in .env")
        return

    print(f"Initializing KnusprMCPClient for {email}...")
    client = KnusprMCPClient(
        login_email=email,
        login_password=password,
        country=KnusprCountry.CZECH_REPUBLIC # Or DE based on base url, but let's test connectivity first
    )

    try:
        print("Attempting authentication...")
        success = await client.authenticate()
        if success:
            print("✅ Authentication successful!")

            print("Searching for 'milk'...")
            products = await client.search_products("milk", max_results=3)
            print(f"Found {len(products)} products:")
            for p in products:
                print(f" - {p.name} ({p.price} {p.unit})")

        else:
            print("❌ Authentication failed.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
