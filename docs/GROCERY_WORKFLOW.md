# Grocery Workflow

This document describes the "Meal Plan to Grocery Cart" workflow, which automates the process of converting a generated meal plan into a shopping cart on the Knuspr (Rohlik) platform.

## Workflow Description

The workflow is initiated by calling a dedicated API endpoint with a `meal_plan_id` and optional delivery preferences. The steps involved are:

1.  **Meal Plan Validation**: The system first validates the provided `meal_plan_id` to ensure it exists and belongs to the authenticated user.
2.  **Credential Retrieval**: Knuspr credentials for the user are securely retrieved. If not found, an error is returned.
3.  **Ingredient Extraction**: All unique ingredients from the meal plan's recipes are extracted.
4.  **Product Mapping**: The extracted ingredients are mapped to available Knuspr products using fuzzy matching and unit normalization. Unmapped ingredients are noted.
5.  **Cart Creation**: A shopping cart is created on the Knuspr platform with the mapped products.
6.  **Delivery Slot Selection**: Available delivery slots are fetched, and an optimal slot is selected based on user preferences (e.g., earliest or cheapest).
7.  **Cart Storage**: The created cart's details, including items and selected delivery slot, are stored in the application's database.
8.  **Response**: A summary of the created cart is returned to the user.

## API Endpoint: `POST /api/v1/workflows/meal-plan-with-groceries`

This endpoint initiates the grocery workflow.

### Request

*   **URL**: `/api/v1/workflows/meal-plan-with-groceries`
*   **Method**: `POST`
*   **Authentication**: Required (JWT Bearer Token)
*   **Request Body**: `application/json`

```json
{
  "meal_plan_id": 123,
  "delivery_preferences": {
    "preferred_dates": ["2025-12-01", "2025-12-02"],
    "preferred_time_slot": "afternoon",
    "budget_optimization": true
  }
}
```

#### Request Body Fields

*   `meal_plan_id` (integer, required): The ID of the meal plan to convert into a grocery cart.
*   `delivery_preferences` (object, optional):
    *   `preferred_dates` (array of strings, optional): A list of preferred delivery dates in `YYYY-MM-DD` format.
    *   `preferred_time_slot` (string, optional): The preferred time slot for delivery. Allowed values: `"morning"`, `"afternoon"`, `"evening"`. Default is `"afternoon"`.
    *   `budget_optimization` (boolean, optional): If `true`, the system will prioritize the cheapest available delivery slot. If `false` (default), it will prioritize the earliest available slot.

### Response

*   **Status Code**: `200 OK`
*   **Content Type**: `application/json`

```json
{
  "workflow_id": "mp-cart-123-knuspr-cart-abc123xyz",
  "status": "success",
  "message": "Successfully created grocery cart from meal plan",
  "result": {
    "cart_id": "knuspr-cart-abc123xyz",
    "knuspr_url": "https://knuspr.de/cart/abc123xyz",
    "total_price": 75.50,
    "item_count": 5,
    "delivery_slot": {
      "slot_id": "slot-2025-12-01-15",
      "date": "2025-12-01T00:00:00",
      "time_window": "15:00-18:00",
      "price": 4.90
    },
    "items_by_section": {
      "produce": [
        { "name": "Milk", "quantity": 1, "unit": "pcs", "price": 25.0 },
        { "name": "Eggs", "quantity": 6, "unit": "pcs", "price": 20.0 }
      ],
      "dairy": [
        { "name": "Knuspr Milk", "quantity": 1, "unit": "liter", "price": 1.50 }
      ]
    },
    "unavailable_items": [],
    "created_at": "2025-11-20T10:00:00.000000"
  }
}
```

#### Response Fields

*   `workflow_id` (string): A unique identifier for the initiated workflow.
*   `status` (string): The status of the workflow (e.g., `"success"`, `"failed"`).
*   `message` (string): A human-readable message describing the outcome.
*   `result` (object, optional): Contains the details of the created grocery cart if the workflow was successful.
    *   `cart_id` (string): The ID of the created Knuspr shopping cart.
    *   `knuspr_url` (string): A direct URL to the created shopping cart on the Knuspr website.
    *   `total_price` (number): The total estimated price of the items in the cart.
    *   `item_count` (integer): The total number of distinct items in the cart.
    *   `delivery_slot` (object, optional): Details of the selected delivery slot.
        *   `slot_id` (string): Unique identifier for the delivery slot.
        *   `date` (string): ISO formatted date of the delivery.
        *   `time_window` (string): Time range for the delivery (e.g., "15:00-18:00").
        *   `price` (number): Price of the delivery slot.
    *   `items_by_section` (object): A dictionary where keys are store sections (e.g., "produce", "dairy") and values are lists of product objects.
    *   `unavailable_items` (array of strings): A list of original ingredient strings that could not be mapped to any Knuspr products.
    *   `created_at` (string): ISO formatted timestamp of when the cart was created.

### Error Codes

*   `400 Bad Request`:
    *   `detail: "Meal plan {id} has no ingredients"`: The specified meal plan does not contain any recipes or ingredients to convert.
    *   `detail: "Knuspr credentials not found. Please configure Knuspr integration first."`: The user has not configured their Knuspr login credentials.
    *   `detail: "Invalid Knuspr credentials - authentication failed"`: The provided Knuspr credentials are not valid.
    *   `detail: "Failed to map any ingredients to Knuspr products"`: No ingredients from the meal plan could be successfully mapped to products on Knuspr.
*   `404 Not Found`:
    *   `detail: "Meal plan {id} not found"`: The specified `meal_plan_id` does not exist or does not belong to the authenticated user.
*   `409 Conflict`: (Not explicitly handled in current workflow, but could be for concurrent cart creation)
    *   `detail: "A grocery cart already exists for this meal plan"`
*   `500 Internal Server Error`:
    *   `detail: "Workflow failed: {error_message}"`: An unexpected error occurred during the workflow execution.
    *   `detail: "An unexpected error occurred while processing the workflow"`: A generic internal server error.

## Deployment Debugging Status

- Hypothesis 1: Railway is still running the upstream `@tomaspavlin/rohlik-mcp@3.0.0` stdio-only build (no SSE listener), so `/health` probes succeed but HTTP workflow calls 502.
- Hypothesis 2: Even if SSE were exposed, missing `ROHLIK_USERNAME/ROHLIK_PASSWORD` envs on Railway would make the MCP server exit early, producing 502s.

Before changing the deployment, **confirm** whether we should swap Railway to the local `/home/darae/workspaces/rohlik-mcp` fork with SSE support and secret envs propagated. Once confirmed, redeploy using `railway up --service rohlik-mcp --path /home/darae/workspaces/rohlik-mcp` after running `npm run build` there.
