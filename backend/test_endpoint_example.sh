#!/bin/bash
# Example curl commands to test the grocery cart API endpoint

# Set your API base URL
API_URL="http://localhost:8000"

# Step 1: Authenticate and get a token (you'll need actual credentials)
echo "Step 1: Login to get access token"
echo "curl -X POST \"$API_URL/api/v1/auth/login\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"email\": \"user@example.com\", \"password\": \"password\"}'"
echo ""

# Step 2: Create cart from meal plan (replace TOKEN and MEAL_PLAN_ID)
echo "Step 2: Create grocery cart from meal plan"
echo "curl -X POST \"$API_URL/api/v1/workflows/carts/from-meal-plan\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" \\"
echo "  -d '{
  \"meal_plan_id\": 1,
  \"aggregate_duplicates\": true
}'"
echo ""

# Example response structure:
cat <<EOF
Expected Response (200 OK):
{
  "cart_id": 1,
  "cart_name": "Grocery List from Weekly Meal Plan",
  "total_items": 12,
  "items": [
    {
      "id": null,
      "name": "spaghetti",
      "quantity": 800.0,
      "unit": "g",
      "category": null,
      "unit_price": null,
      "total_price": null,
      "recipe_sources": [
        {"recipe_id": 1, "recipe_name": "Pasta Carbonara"},
        {"recipe_id": 2, "recipe_name": "Spaghetti Bolognese"}
      ],
      "knuspr_product_id": null,
      "knuspr_url": null,
      "is_purchased": false
    }
  ],
  "unmatched_ingredients": []
}

Error Responses:
- 401 Unauthorized: Missing or invalid access token
- 404 Not Found: Meal plan not found or doesn't belong to user
- 400 Bad Request: Meal plan has no recipes
- 500 Internal Server Error: Unexpected error during processing
EOF
