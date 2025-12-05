# Correlation ID Flow Documentation

## Overview

Correlation IDs enable end-to-end request tracing across distributed systems by assigning a unique identifier to each request that persists through the entire call chain.

## Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT REQUEST                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ GET /api/v1/recipes
                                     │ Headers: X-Correlation-ID: abc-123 (optional)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CORRELATION ID MIDDLEWARE                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Extract X-Correlation-ID from headers                            │   │
│  │ 2. Validate format (UUID or alphanumeric, max 128 chars)           │   │
│  │ 3. Generate new UUID if missing/invalid                             │   │
│  │ 4. Set in async context (contextvars)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ correlation_id = "abc-123"
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOGGING FILTER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Automatically adds correlation_id to ALL log records:               │   │
│  │ {                                                                    │   │
│  │   "timestamp": "2025-12-05T10:30:00Z",                              │   │
│  │   "level": "INFO",                                                   │   │
│  │   "message": "Processing recipe request",                           │   │
│  │   "correlation_id": "abc-123",  ← AUTOMATIC                         │   │
│  │   "request_id": "req-456"                                            │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROUTE HANDLER / SERVICE                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ async def get_recipes():                                             │   │
│  │     # Correlation ID available anywhere via get_correlation_id()     │   │
│  │     correlation_id = get_correlation_id()                            │   │
│  │     logger.info("Fetching recipes")  ← Auto includes correlation_id  │   │
│  │     return recipes                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Need to call external API?
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL API CALL (Knuspr)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ correlation_id = get_correlation_id()                                │   │
│  │ logger.info("Calling Knuspr API",                                    │   │
│  │             extra={"correlation_id": correlation_id})                │   │
│  │                                                                       │   │
│  │ # Propagate to external service                                      │   │
│  │ headers = {"X-Correlation-ID": correlation_id}                       │   │
│  │ await knuspr_client.search_products(...)                             │   │
│  │                                                                       │   │
│  │ → External service receives same correlation ID                      │   │
│  │ → Can trace request across service boundaries                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Response
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CORRELATION ID MIDDLEWARE                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Add X-Correlation-ID to response headers                          │   │
│  │ 2. Clear correlation ID from context                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Response
                                     │ Headers: X-Correlation-ID: abc-123
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT RESPONSE                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Basic Usage (Automatic)

```python
# In any route handler or service
from app.logging_config import get_logger

logger = get_logger(__name__)

async def process_request():
    # Correlation ID automatically included in logs
    logger.info("Processing request")
    # Output: {"correlation_id": "abc-123", "message": "Processing request", ...}
```

### Manual Access

```python
from app.middleware.correlation_id import get_correlation_id

async def my_function():
    correlation_id = get_correlation_id()
    print(f"Current correlation ID: {correlation_id}")
```

### External API Calls

```python
from app.middleware.correlation_id import get_correlation_id_header

async def call_external_api():
    # Get headers with correlation ID
    headers = get_correlation_id_header()
    # {"X-Correlation-ID": "abc-123"}

    response = await http_client.get(
        "https://api.example.com/data",
        headers=headers
    )
```

### Background Tasks

```python
from app.middleware.correlation_id import set_correlation_id, clear_correlation_id
import uuid

async def background_task():
    # Set correlation ID for background task
    set_correlation_id(str(uuid.uuid4()))

    try:
        # Process task (logs will include correlation ID)
        await process_task()
    finally:
        # Clean up
        clear_correlation_id()
```

## Log Aggregation

All logs with the same correlation ID can be aggregated for debugging:

```bash
# Filter logs by correlation ID
cat app.log | jq 'select(.correlation_id == "abc-123")'

# Trace entire request flow
cat app.log | jq 'select(.correlation_id == "abc-123") | "\(.timestamp) \(.level) \(.message)"'
```

## Benefits

1. **End-to-End Tracing**: Track requests across multiple services
2. **Debugging**: Easily identify all logs related to a single request
3. **Error Investigation**: Trace error origins across service boundaries
4. **Performance Analysis**: Measure request latency across services
5. **Customer Support**: Provide correlation IDs to customers for incident tracking

## Integration with External Services

When making external API calls, always include the correlation ID:

```python
# Knuspr integration (already implemented)
async def search_products(ingredient: str):
    correlation_id = get_correlation_id()
    logger.info("Searching products", extra={"correlation_id": correlation_id})

    # Correlation ID passed to circuit breaker and logged
    return await knuspr_client.search_products(ingredient)
```

## Validation Rules

1. **Format**: Must be UUID or alphanumeric with hyphens
2. **Length**: Maximum 128 characters
3. **Security**: No special characters to prevent header injection
4. **Fallback**: Invalid IDs are rejected and new UUIDs generated

## Context Safety

Correlation IDs are stored in `contextvars`, making them:
- **Thread-safe**: Each thread has its own context
- **Async-safe**: Each async task has its own context
- **Isolated**: No cross-contamination between requests

## Headers

### Request Headers (Optional)
```
X-Correlation-ID: <client-provided-id>
```

### Response Headers (Always Present)
```
X-Correlation-ID: <correlation-id>
```

### CORS Configuration
Both request and response headers are exposed in CORS configuration.
