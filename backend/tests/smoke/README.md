# Smoke Tests

Post-deployment validation tests for the AI Meal Planner backend.

## Overview

Smoke tests are lightweight tests that run against deployed environments (staging, production) to validate that:

1. The application is deployed correctly
2. All critical endpoints are accessible
3. Dependencies (database, Redis) are connected
4. Performance meets basic requirements
5. Configuration is correct

## Running Smoke Tests

### Against Staging Environment

```bash
# Set the staging API URL
export API_BASE_URL=https://staging-api.example.com

# Run smoke tests
pytest tests/smoke/ -v -m smoke
```

### Against Production Environment

```bash
# Set the production API URL
export API_BASE_URL=https://api.example.com

# Run smoke tests
pytest tests/smoke/ -v -m smoke
```

### Against Local Development

```bash
# Run smoke tests against local server
export API_BASE_URL=http://localhost:8000

# Start the server first
uvicorn app.main:app --reload

# In another terminal, run smoke tests
pytest tests/smoke/ -v -m smoke
```

## Test Organization

### `test_health_endpoints.py`

Tests for health check endpoints:
- `/health` - Comprehensive health status
- `/health/liveness` - Liveness probe
- `/health/readiness` - Readiness probe

**Key validations:**
- Endpoints are accessible
- Response format is correct
- Database and Redis status included
- Response times are acceptable

### `test_api_endpoints.py`

Tests for critical API endpoints:
- API root and documentation
- Authentication endpoints
- Recipe endpoints
- Meal plan endpoints
- Grocery cart endpoints

**Key validations:**
- Endpoints exist and return expected status codes
- Error handling works correctly
- CORS is configured
- Rate limiting is active

### `test_database_connectivity.py`

Tests for database and Redis connectivity:
- Database health status
- Redis health status
- Connection latencies
- Pool utilization

**Key validations:**
- Database is accessible
- Response times are acceptable
- Connection pools not exhausted
- Migrations are up to date

### `test_performance_baseline.py`

Basic performance validation tests:
- Response time baselines
- Concurrent request handling
- Resource usage patterns

**Key validations:**
- Health checks respond in < 1 second
- API docs load in < 3 seconds
- No memory leaks detected
- Handles concurrent requests

## Test Markers

Smoke tests use the following pytest markers:

- `@pytest.mark.smoke` - All smoke tests
- `@pytest.mark.health_check` - Health check tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.recipes` - Recipe endpoint tests
- `@pytest.mark.meal_plans` - Meal plan tests
- `@pytest.mark.grocery_cart` - Grocery cart tests
- `@pytest.mark.requires_db` - Tests requiring database
- `@pytest.mark.requires_redis` - Tests requiring Redis
- `@pytest.mark.slow` - Tests that take longer

## Environment Variables

### Required

- `API_BASE_URL` - Base URL of the deployed API (default: `http://localhost:8000`)

### Optional

- `SMOKE_TEST_EMAIL` - Test user email for auth tests (default: `smoketest@example.com`)
- `SMOKE_TEST_PASSWORD` - Test user password (default: `SmokeTest123!`)

## CI/CD Integration

Smoke tests are automatically run in the deployment pipeline:

1. After successful deployment to staging
2. Before marking deployment as complete
3. On manual trigger for production validation

See `.github/workflows/deploy-staging.yml` for integration details.

## Expected Results

### Passing Smoke Tests

All tests pass with status codes indicating:
- 200: Success
- 401/422: Expected auth failures
- 404: Endpoint not found (acceptable for some optional endpoints)

### Failing Smoke Tests

If smoke tests fail, the deployment should be investigated:
- Check service logs for errors
- Verify environment variables are set correctly
- Check database migrations ran successfully
- Verify network connectivity to dependencies

## Writing New Smoke Tests

When adding new critical endpoints, add corresponding smoke tests:

1. Create test function with `@pytest.mark.smoke` marker
2. Test basic accessibility (200 status code)
3. Validate response structure if applicable
4. Keep tests fast (< 5 seconds each)
5. Don't test detailed business logic (use integration tests for that)

### Example

```python
import pytest
from httpx import Client


@pytest.mark.smoke
@pytest.mark.my_feature
class TestMyFeature:
    """Smoke tests for my new feature."""

    def test_my_endpoint_accessible(self, client: Client) -> None:
        """Test that my endpoint is accessible."""
        response = client.get("/api/v1/my-endpoint")
        assert response.status_code == 200
```

## Troubleshooting

### Connection Refused

If you see "Connection refused" errors:
- Ensure the API server is running
- Verify `API_BASE_URL` is correct
- Check network connectivity

### Authentication Failures

If auth tests fail unexpectedly:
- Verify test credentials are set correctly
- Check that user exists in the database
- Review rate limiting configuration

### Timeout Errors

If tests timeout:
- Increase httpx client timeout in `conftest.py`
- Check server performance
- Review database query performance

## Best Practices

1. **Keep tests fast** - Smoke tests should complete in < 2 minutes
2. **Test critical paths only** - Don't duplicate integration tests
3. **Use appropriate assertions** - Focus on "is it working" not "is it correct"
4. **Handle optional features** - Some endpoints may not exist in all environments
5. **Document expectations** - Add clear docstrings explaining what's being tested
