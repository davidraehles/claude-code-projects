#!/bin/bash

# Test script to add cheese to Knuspr cart
# This script creates a test cart and fills it with cheese

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
API_BASE="$BACKEND_URL/api/v1"

echo "🧀 Testing Knuspr Integration - Adding Cheese to Cart"
echo "====================================================="
echo ""
echo "Backend URL: $BACKEND_URL"
echo ""

# Check if backend is running
echo "1️⃣  Checking backend status..."
if ! curl -s "$BACKEND_URL/health" > /dev/null; then
    echo "❌ Backend is not reachable at $BACKEND_URL"
    echo "   Start with: docker-compose up -d"
    exit 1
fi
echo "✅ Backend is running"
echo ""

# Check if user is logged in (requires JWT token)
if [ -z "$JWT_TOKEN" ]; then
    echo "⚠️  No JWT_TOKEN environment variable set"
    echo ""
    echo "Please log in first:"
    echo "  1. Register or login via API"
    echo "  2. Set JWT_TOKEN=<your_token>"
    echo ""
    echo "Quick login (if you have credentials):"
    echo "  JWT_TOKEN=\$(curl -s -X POST \"$API_BASE/auth/login\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"email\":\"test@example.com\",\"password\":\"testpass\"}' | jq -r '.access_token')"
    echo ""
    exit 1
fi

echo "2️⃣  Creating test grocery cart with cheese..."

# Create a simple cart with cheese items
CART_RESPONSE=$(curl -s -X POST "$API_BASE/grocery-carts" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "items": [
            {
                "name": "Cheddar Cheese",
                "quantity": "200g",
                "category": "dairy",
                "unit": "g"
            },
            {
                "name": "Mozzarella",
                "quantity": "250g",
                "category": "dairy",
                "unit": "g"
            },
            {
                "name": "Parmesan",
                "quantity": "100g",
                "category": "dairy",
                "unit": "g"
            }
        ]
    }')

CART_ID=$(echo "$CART_RESPONSE" | jq -r '.id // empty')

if [ -z "$CART_ID" ]; then
    echo "❌ Failed to create cart"
    echo "Response: $CART_RESPONSE"
    exit 1
fi

echo "✅ Created cart ID: $CART_ID"
echo ""

echo "3️⃣  Filling Knuspr cart with cheese items..."
echo "   (This will use your KNUSPR credentials from .env)"
echo ""

# Note: The backend will use credentials from the .env file
# You can also pass them explicitly if needed
FILL_RESPONSE=$(curl -s -X POST "$API_BASE/workflows/carts/$CART_ID/fill-knuspr" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "credentials": {
            "email": "'"${KNUSPR_EMAIL}"'",
            "password": "'"${KNUSPR_PASSWORD}"'",
            "country": "de"
        },
        "match_preferences": {
            "min_confidence": 0.7,
            "allow_substitutions": true,
            "prefer_organic": false
        }
    }')

echo "Response:"
echo "$FILL_RESPONSE" | jq '.'
echo ""

# Check for success
SUCCESS=$(echo "$FILL_RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
    echo "🎉 Success! Cheese items added to Knuspr cart!"

    KNUSPR_URL=$(echo "$FILL_RESPONSE" | jq -r '.knuspr_cart_url // empty')
    MATCHED_COUNT=$(echo "$FILL_RESPONSE" | jq -r '.matched_items | length')
    UNMATCHED_COUNT=$(echo "$FILL_RESPONSE" | jq -r '.unmatched_items | length')

    echo ""
    echo "📊 Results:"
    echo "   ✅ Matched items: $MATCHED_COUNT"
    echo "   ❌ Unmatched items: $UNMATCHED_COUNT"

    if [ -n "$KNUSPR_URL" ]; then
        echo "   🛒 Knuspr cart: $KNUSPR_URL"
        echo ""
        echo "Open this URL to see your cart with cheese! 🧀"
    fi

    echo ""
    echo "📦 Matched Items:"
    echo "$FILL_RESPONSE" | jq -r '.matched_items[] | "   - \(.name) → \(.knuspr_product_name)"'

    if [ "$UNMATCHED_COUNT" -gt 0 ]; then
        echo ""
        echo "⚠️  Unmatched Items:"
        echo "$FILL_RESPONSE" | jq -r '.unmatched_items[] | "   - \(.name)"'
    fi
else
    echo "❌ Failed to fill Knuspr cart"
    ERROR=$(echo "$FILL_RESPONSE" | jq -r '.detail // .error // "Unknown error"')
    echo "Error: $ERROR"
fi

echo ""
echo "Done! 🧀"
