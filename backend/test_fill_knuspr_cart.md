# Fill Knuspr Cart API - Testing Documentation

## Overview

This document provides testing information for the newly implemented T016-T017 features:
- **T016**: `add_items_batch` method in `KnusprMCPClient`
- **T017**: `fill_knuspr_cart` endpoint in workflows API

## API Endpoint

### POST `/api/v1/workflows/carts/{cart_id}/fill-knuspr`

Fill a Knuspr cart with items from an existing grocery cart.

#### Request

**Path Parameters:**
- `cart_id` (integer): ID of the grocery cart to fill

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "credentials": {
    "email": "user@example.com",
    "password": "secure_password",
    "country": "de"
  },
  "match_preferences": {
    "min_confidence": 0.7,
    "allow_substitutions": true,
    "prefer_organic": false,
    "max_price_per_item": 10.0
  }
}
```

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "cart_id": 1,
  "knuspr_cart_url": "https://www.knuspr.de/cart/abc123",
  "matched_items": 15,
  "partial_matches": 3,
  "unmatched_items": ["rare spice", "exotic herb"],
  "matched_products": [
    {
      "name": "spaghetti",
      "knuspr_product_id": "12345",
      "knuspr_product_name": "Barilla Spaghetti 500g",
      "quantity": 400.0,
      "unit": "g",
      "confidence": 0.95
    }
  ],
  "progress": 100,
  "message": "Successfully added 15 items to Knuspr cart (3 partial matches)"
}
```

**Error Responses:**

- **404 Not Found**: Cart not found or doesn't belong to user
  ```json
  {
    "detail": "Cart 123 not found or does not belong to user"
  }
  ```

- **401 Unauthorized**: Authentication failed
  ```json
  {
    "detail": "Failed to authenticate with Knuspr. Please check your credentials."
  }
  ```

- **400 Bad Request**: Invalid request
  ```json
  {
    "detail": "Cart has no items to add to Knuspr"
  }
  ```

- **429 Too Many Requests**: Rate limit exceeded
  ```json
  {
    "detail": "Rate limit exceeded. Maximum 10 requests per 5 minutes. Reset at 2025-12-02T10:30:00Z"
  }
  ```

- **502 Bad Gateway**: Knuspr API error
  ```json
  {
    "detail": "Knuspr API error: Connection timeout"
  }
  ```

- **500 Internal Server Error**: Server error
  ```json
  {
    "detail": "An unexpected error occurred while filling the Knuspr cart"
  }
  ```

## Implementation Details

### T016: `add_items_batch` Method

**Location:** `backend/app/services/knuspr_mcp_client.py`

**Features:**
- Batches items into groups of 10 for efficient API calls
- Implements retry logic with exponential backoff (up to 3 retries)
- Returns detailed results: succeeded_items, failed_items, partial_matches
- Handles authentication within the batch operation
- Tracks match confidence scores (0.0-1.0)
- Creates Knuspr cart with all successfully matched items

**Method Signature:**
```python
async def add_items_batch(
    self,
    items: List[Dict[str, Any]],
    batch_size: int = 10,
    max_retries: int = 3
) -> BatchAddResult
```

**Confidence Thresholds:**
- `>= 0.8`: High confidence match (succeeded_items)
- `>= 0.5`: Partial match (partial_matches)
- `< 0.5`: Low confidence, retry or fail

### T017: `fill_knuspr_cart` Endpoint

**Location:** `backend/app/api/v1/workflows.py`

**Workflow:**
1. Validates cart ownership and retrieves cart items
2. Authenticates with Knuspr using provided credentials
3. Uses `KnusprMCPClient.add_items_batch()` to match and add items
4. Tracks progress: current_item, total_items, success_count, failure_count
5. Updates database with Knuspr cart URL and product mappings
6. Returns detailed results with matched/unmatched items

**Database Updates:**
- `GroceryCart.knuspr_cart_id`: Knuspr cart ID
- `GroceryCart.knuspr_synced_at`: Sync timestamp
- `CartItem.knuspr_product_id`: Matched Knuspr product ID
- `CartItem.knuspr_url`: Knuspr product URL

**Rate Limiting:**
- Maximum 10 requests per 5 minutes per user
- Prevents abuse of expensive MCP operations

## Testing Scenarios

### Scenario 1: Successful Cart Fill
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/carts/1/fill-knuspr" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "email": "test@example.com",
      "password": "password123",
      "country": "de"
    }
  }'
```

**Expected Result:**
- Status: 200 OK
- Most items matched with high confidence
- Knuspr cart URL returned
- Database updated with Knuspr cart ID

### Scenario 2: Partial Matches
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/carts/2/fill-knuspr" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "email": "test@example.com",
      "password": "password123",
      "country": "de"
    },
    "match_preferences": {
      "min_confidence": 0.5
    }
  }'
```

**Expected Result:**
- Status: 200 OK
- Some items have partial matches (0.5 <= confidence < 0.8)
- Partial matches included in response
- Success message indicates partial matches

### Scenario 3: Authentication Failure
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/carts/1/fill-knuspr" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "email": "invalid@example.com",
      "password": "wrongpassword",
      "country": "de"
    }
  }'
```

**Expected Result:**
- Status: 401 Unauthorized
- Error message: "Failed to authenticate with Knuspr. Please check your credentials."

### Scenario 4: Cart Not Found
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/carts/99999/fill-knuspr" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "email": "test@example.com",
      "password": "password123",
      "country": "de"
    }
  }'
```

**Expected Result:**
- Status: 404 Not Found
- Error message: "Cart 99999 not found or does not belong to user"

## Data Structures

### BatchItemResult
```python
@dataclass
class BatchItemResult:
    name: str
    quantity: float
    unit: str
    success: bool
    knuspr_product_id: Optional[str] = None
    knuspr_product_name: Optional[str] = None
    error_message: Optional[str] = None
    match_confidence: float = 0.0
    retry_count: int = 0
```

### BatchAddResult
```python
@dataclass
class BatchAddResult:
    total_items: int
    succeeded_items: List[BatchItemResult]
    failed_items: List[BatchItemResult]
    partial_matches: List[BatchItemResult]
    cart_id: Optional[str] = None
    cart_url: Optional[str] = None

    @property
    def success_count(self) -> int

    @property
    def failure_count(self) -> int

    @property
    def partial_count(self) -> int
```

## Error Handling Strategy

### Authentication Errors
- Caught during `knuspr_client.authenticate()`
- Returns 401 Unauthorized
- Does not update database

### Product Search Errors
- Retries up to 3 times with exponential backoff
- Tracks retry count in `BatchItemResult`
- After max retries, item added to `failed_items`

### Cart Creation Errors
- If cart creation fails, all items moved to `failed_items`
- No partial state saved
- Error logged and returned as 502 Bad Gateway

### Database Errors
- Transaction rolled back on failure
- Original cart state preserved
- Error logged and returned as 500 Internal Server Error

### Rate Limiting
- Checked before any API calls
- Returns 429 Too Many Requests
- Includes reset time in error message

## Logging

All operations are logged with appropriate levels:
- **INFO**: Authentication success, batch operations, cart creation
- **WARNING**: Failed matches, rate limit exceeded
- **ERROR**: API errors, database errors
- **DEBUG**: Individual product searches, batch processing

Log format includes:
- User ID
- Cart ID
- Operation type
- Success/failure counts
- Error messages

## Performance Considerations

### Batching
- Items processed in batches of 10
- Reduces API call overhead
- Improves response time for large carts

### Retry Logic
- Exponential backoff: 0.5s, 1.0s, 1.5s
- Prevents API throttling
- Improves success rate for transient errors

### Database Optimization
- Single commit after all operations
- Bulk updates for cart items
- Indexed queries on cart_id and user_id

## Security Considerations

### Credentials
- Credentials passed in request body (not stored in database by this endpoint)
- Use HTTPS in production to protect credentials in transit
- Consider using stored credentials from `KnusprCredential` table instead

### Authorization
- JWT token validation for user authentication
- Cart ownership verified before processing
- Rate limiting prevents abuse

### Input Validation
- Pydantic schemas validate all input
- Country code validated against enum
- Quantity and confidence values constrained

## Future Improvements

1. **WebSocket Support**: Real-time progress updates during batch operation
2. **Background Jobs**: Process large carts asynchronously using Celery
3. **Caching**: Cache product searches to reduce API calls
4. **Smart Matching**: Use ML model for better product matching
5. **Bulk Operations**: Support multiple carts in single request
6. **Stored Credentials**: Use `CredentialManager` to retrieve saved credentials
7. **Rollback Support**: Implement undo operation for failed cart fills
8. **Analytics**: Track match success rates and popular products

## Related Files

- `/home/darae/claude-code-projects/backend/app/services/knuspr_mcp_client.py`
- `/home/darae/claude-code-projects/backend/app/api/v1/workflows.py`
- `/home/darae/claude-code-projects/backend/app/schemas/grocery_cart.py`
- `/home/darae/claude-code-projects/backend/app/models/meal_plan.py` (GroceryCart, CartItem)
