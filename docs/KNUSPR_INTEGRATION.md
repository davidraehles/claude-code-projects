# Knuspr/Rohlik Integration Guide

Complete guide for the Knuspr/Rohlik grocery delivery integration in the meal planner app.

## Table of Contents
- [Overview](#overview)
- [MCP Tools Reference](#mcp-tools-reference)
- [Implementation Status](#implementation-status)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Testing](#testing)

---

## Overview

The meal planner integrates with Knuspr/Rohlik grocery delivery service through:
- **Backend Service**: `KnusprMCPClient` - Python wrapper for Rohlik MCP server
- **Agent**: `CartOptimizerAgent` - Converts meal plans to grocery carts
- **MCP Server**: [rohlik-mcp](https://github.com/davidraehles/rohlik-mcp) - Node.js MCP server
- **API**: Full REST API for cart management

### Architecture

```
Meal Plan → CartOptimizerAgent → KnusprMCPClient → Rohlik MCP Server → Knuspr API
```

---

## MCP Tools Reference

All 17 MCP tools are available via `KnusprMCPClient`:

### 🛒 Cart Management

#### search_products(query, max_results=10)
Search for products by name.
```python
products = await client.search_products("milk", max_results=5)
# Returns: List of product dictionaries
```

#### create_cart(items)
Create a shopping cart.
```python
cart = await client.create_cart([
    {"product_id": 6272, "quantity": 2, "unit": "pcs"}
])
# Returns: KnusprCart with cart_id, total_price
```

#### get_cart_content()
Get current cart contents.
```python
cart = await client.get_cart_content()
# Returns: Dict with items, total_price, can_order status
```

#### remove_from_cart(product_ids)
Remove products from cart.
```python
result = await client.remove_from_cart([6272, 7012])
```

### 🚚 Delivery

#### get_delivery_slots(start_date, end_date)
Get available delivery slots.
```python
from datetime import datetime, timedelta
start = datetime.utcnow()
end = start + timedelta(days=7)
slots = await client.get_delivery_slots(start, end)
# Returns: List[KnusprDeliverySlot]
```

#### select_delivery_slot(cart_id, slot_id)
Choose delivery slot.
```python
await client.select_delivery_slot(cart.cart_id, slot.slot_id)
```

#### get_delivery_info()
Get delivery service information.
```python
info = await client.get_delivery_info()
```

### 👤 Personalization

#### get_frequent_items()
Get user's frequently ordered items.
```python
frequent = await client.get_frequent_items()
# Returns: Top items by order frequency
```

#### get_meal_suggestions(meal_type, items_count=10)
Get meal-specific suggestions.
```python
suggestions = await client.get_meal_suggestions(
    meal_type="dinner",  # breakfast, lunch, dinner, snack, baking, drinks, healthy
    items_count=15
)
```

#### get_shopping_list(shopping_list_id)
Get saved shopping list.
```python
items = await client.get_shopping_list("list_12345")
```

#### get_shopping_scenarios()
Get usage examples and scenarios.
```python
scenarios = await client.get_shopping_scenarios()
```

### 📦 Orders

#### get_order_history(limit=None)
Get past orders.
```python
history = await client.get_order_history(limit=10)
```

#### get_order_detail(order_id)
Get order details.
```python
order = await client.get_order_detail("1009694022")
```

#### get_upcoming_orders()
Get scheduled deliveries.
```python
upcoming = await client.get_upcoming_orders()
```

### 🔐 Account

#### get_account_data()
Get user account info.
```python
account = await client.get_account_data()
```

#### get_premium_info()
Get subscription status.
```python
premium = await client.get_premium_info()
```

#### get_reusable_bags_info()
Get bag credits.
```python
bags = await client.get_reusable_bags_info()
```

#### get_announcements()
Get service notifications.
```python
announcements = await client.get_announcements()
```

---

## Implementation Status

### ✅ Complete (December 2025)

**MCP Tools Integration**
- All 17 MCP tools wrapped in KnusprMCPClient
- Type hints and docstrings for all methods
- Proper parameter handling (meal_suggestions, shopping_list)
- Error handling and authentication management

**CartOptimizerAgent**
- Full workflow: meal plan → ingredients → products → cart → delivery
- Delivery slot selection
- Budget optimization
- Cart storage in PostgreSQL
- Event publishing for cart operations

**API Endpoints**
- `POST /api/v1/carts/create` - Create cart from meal plan
- `GET /api/v1/carts/{cart_id}` - Get cart details
- Full CRUD operations

**Testing**
- Integration tests with mocks
- Real API testing (rate limit verified)
- Tool parameter validation

### Configuration

#### Environment Variables

```bash
# backend/.env
ROHLIK_USERNAME=your-email@example.com
ROHLIK_PASSWORD=your-password
ROHLIK_COUNTRY=DE  # CZ, DE, etc.

# Optional: custom MCP server location
ROHLIK_MCP_URL=/path/to/rohlik-mcp-temp/dist/index.js
```

#### MCP Server Setup

1. Clone rohlik-mcp server:
```bash
git clone https://github.com/davidraehles/rohlik-mcp.git rohlik-mcp-temp
cd rohlik-mcp-temp
npm install
npm run build
```

2. Server runs automatically via stdio when KnusprMCPClient is used

---

## Usage Examples

### CartOptimizerAgent Integration

```python
class CartOptimizerAgent:
    def __init__(self, knuspr_client, ...):
        self.knuspr_client = knuspr_client  # All 17 tools available!

    async def create_cart_from_meal_plan(self, meal_plan_id, user_id):
        # Get user preferences
        frequent = await self.knuspr_client.get_frequent_items()
        premium = await self.knuspr_client.get_premium_info()

        # Create cart
        cart = await self.knuspr_client.create_cart(items)

        # Verify
        cart_content = await self.knuspr_client.get_cart_content()

        return cart
```

### Common Patterns

**Check Premium for Free Delivery**
```python
premium = await client.get_premium_info()
has_free_delivery = premium.get('premiumLimits', {}).get('unlimited', False)
```

**Smart Reorder**
```python
frequent = await client.get_frequent_items()
products = [{"product_id": item['id'], "quantity": 1}
            for item in frequent['top_items'][:10]]
cart = await client.create_cart(products)
```

**Budget-Aware Cart**
```python
cart = await client.create_cart(items)
cart_content = await client.get_cart_content()

if cart_content['total_price'] > budget:
    expensive = sorted(cart_content['items'],
                      key=lambda x: x['price'], reverse=True)
    to_remove = [item['cart_id'] for item in expensive[:5]]
    await client.remove_from_cart(to_remove)
```

---

## Testing

### Run All Tests
```bash
python3 test_all_mcp_tools.py
```

### Test Specific Tools
```bash
python3 test_add_cheese_simple.py
```

### Check Available Tools
```bash
cd rohlik-mcp-temp && grep -E 'name: "' src/tools/*.ts
```

### Test Results

- ✅ search_products - Working (found 10 milk products)
- ✅ get_cart_content - Working (retrieved cart with 3 items)
- ✅ get_frequent_items - Working (92 items from 5 orders)
- ✅ get_meal_suggestions - Working (dinner suggestions)
- ✅ get_shopping_scenarios - Working
- ✅ get_delivery_slots - Working
- ⚠️ Rate limiting expected after multiple consecutive calls (HTTP 429)

---

## Error Handling

```python
from app.services.knuspr_mcp_client import ToolExecutionError, ConnectionError

try:
    cart = await client.create_cart(items)
except ToolExecutionError as e:
    logger.error(f"Tool failed: {e.message}")
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
```

### Rate Limiting

Implement exponential backoff:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def robust_search(query):
    return await client.search_products(query)
```

---

## Files

**Implementation:**
- `backend/app/services/knuspr_mcp_client.py` - MCP client wrapper
- `backend/app/agents/cart_optimizer.py` - Cart optimization agent
- `backend/app/services/ingredient_mapper.py` - Product mapping
- `backend/app/api/v1/endpoints/grocery_carts.py` - REST API

**Tests:**
- `test_all_mcp_tools.py` - Comprehensive tool testing
- `test_add_cheese_simple.py` - Simple cart test
- `backend/tests/integration/test_cart_optimizer.py` - Agent tests

**Documentation:**
- This file - Complete integration guide
- `docs/deployment.md` - Deployment configuration
