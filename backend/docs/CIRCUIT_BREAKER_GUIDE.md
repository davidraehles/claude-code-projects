# Circuit Breaker Pattern - Developer Guide

## Overview

The circuit breaker pattern prevents cascading failures when external services (like Knuspr API) experience issues. It acts like an electrical circuit breaker, stopping requests when a service is detected as failing and periodically testing for recovery.

## Quick Start

### Using the Protected Knuspr Client

The easiest way to use circuit breakers is through the protected Knuspr client:

```python
from app.services.knuspr_with_circuit_breaker import get_protected_knuspr_client
from app.utils.circuit_breaker import CircuitBreakerError

# Create protected client
client = get_protected_knuspr_client(
    login_email="user@example.com",
    login_password="password"
)

# All methods are automatically protected
try:
    products = await client.search_products("milk")
except CircuitBreakerError as e:
    # Circuit is open, service is down
    logger.warning(f"Service unavailable: {e}")
    # Return cached data or show friendly error
    return {"error": "Service temporarily unavailable", "retry_after": e.retry_after}
```

### Creating Custom Circuit Breakers

For other external services:

```python
from app.utils.circuit_breaker import get_circuit_breaker, CircuitBreakerConfig

# Configure circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,      # Open after 5 failures
    success_threshold=2,      # Close after 2 successes
    timeout_seconds=60.0,     # Retry after 60 seconds
    window_seconds=60.0,      # Count failures over 60 seconds
    half_open_max_calls=3     # Max test calls in half-open state
)

# Get or create circuit breaker
breaker = get_circuit_breaker("my_service", config)

# Wrap service calls
async def call_external_api(data):
    try:
        result = await breaker.call(external_service.make_request, data)
        return result
    except CircuitBreakerError as e:
        logger.warning(f"Circuit open: {e}")
        return None  # Handle gracefully
```

## Circuit States

### CLOSED (Normal Operation)
- All requests pass through
- Failures are counted
- Opens after reaching failure threshold

### OPEN (Failing Fast)
- All requests are rejected immediately
- No calls to external service
- Transitions to HALF_OPEN after timeout

### HALF_OPEN (Testing Recovery)
- Limited requests allowed
- Tests if service has recovered
- Closes on success, reopens on failure

## State Transition Diagram

```
    CLOSED
      |
      | failure_threshold exceeded
      v
     OPEN
      |
      | timeout_seconds elapsed
      v
   HALF_OPEN
      |     |
      |     | any failure
      |     v
      |    OPEN
      |
      | success_threshold met
      v
    CLOSED
```

## Configuration Guide

### Recommended Settings by Service Type

#### High-Availability Services (e.g., Redis, Database)
```python
CircuitBreakerConfig(
    failure_threshold=10,     # More tolerant
    success_threshold=3,
    timeout_seconds=30.0,     # Quick recovery attempt
    window_seconds=60.0
)
```

#### External APIs (e.g., Knuspr, Payment Gateways)
```python
CircuitBreakerConfig(
    failure_threshold=5,      # Standard
    success_threshold=2,
    timeout_seconds=60.0,     # Wait before retry
    window_seconds=60.0
)
```

#### Slow/Unstable Services
```python
CircuitBreakerConfig(
    failure_threshold=3,      # Less tolerant
    success_threshold=3,      # More cautious recovery
    timeout_seconds=120.0,    # Longer wait
    window_seconds=30.0       # Shorter window
)
```

## Monitoring

### Prometheus Metrics

The circuit breaker exposes the following metrics:

```prometheus
# Current state (0=closed, 1=half_open, 2=open)
circuit_breaker_state{name="knuspr_api"} 0

# Request counters
circuit_breaker_requests_total{name="knuspr_api", result="success"} 1523
circuit_breaker_requests_total{name="knuspr_api", result="failure"} 7
circuit_breaker_requests_total{name="knuspr_api", result="rejected"} 142

# State transitions
circuit_breaker_state_transitions_total{name="knuspr_api", from_state="closed", to_state="open"} 2
```

### Viewing Metrics

```python
from app.utils.circuit_breaker import get_circuit_breaker

breaker = get_circuit_breaker("knuspr_api")
metrics = breaker.get_metrics()

print(f"State: {metrics['state']}")
print(f"Success rate: {1 - metrics['failure_rate']:.2%}")
print(f"Total requests: {metrics['total_requests']}")
print(f"Rejected requests: {metrics['rejected_requests']}")
```

### Setting Up Alerts

#### Grafana Alert: Circuit Open
```
ALERT CircuitBreakerOpen
  IF circuit_breaker_state == 2
  FOR 2m
  ANNOTATIONS {
    summary = "Circuit breaker {{ $labels.name }} is OPEN",
    description = "The circuit breaker has been open for 2 minutes"
  }
```

#### Grafana Alert: High Rejection Rate
```
ALERT HighCircuitBreakerRejectionRate
  IF rate(circuit_breaker_requests_total{result="rejected"}[5m]) > 10
  ANNOTATIONS {
    summary = "High rejection rate for {{ $labels.name }}",
    description = "Circuit breaker rejecting >10 requests/sec"
  }
```

## Error Handling Best Practices

### 1. Always Catch CircuitBreakerError

```python
from app.utils.circuit_breaker import CircuitBreakerError

try:
    result = await breaker.call(service_function)
except CircuitBreakerError as e:
    # Circuit is open
    logger.warning(f"Circuit breaker {e.service_name} is open")
    # Return cached data, default value, or user-friendly error
    return get_cached_result() or default_value
except Exception as e:
    # Service error (circuit may still be closed)
    logger.error(f"Service error: {e}")
    # Handle service-specific error
```

### 2. Provide Retry Information

```python
try:
    result = await breaker.call(service_function)
except CircuitBreakerError as e:
    return {
        "error": "Service temporarily unavailable",
        "retry_after_seconds": e.retry_after,
        "message": "Please try again in a few moments"
    }
```

### 3. Use Fallback Strategies

```python
async def get_products_with_fallback(query: str):
    try:
        # Try primary service
        return await breaker.call(knuspr_client.search_products, query)
    except CircuitBreakerError:
        # Fallback to cached results
        logger.warning("Using cached product results")
        return await cache.get_products(query)
```

## Testing

### Unit Tests

```python
import pytest
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures():
    config = CircuitBreakerConfig(failure_threshold=3)
    breaker = CircuitBreaker("test", config)

    async def failing_function():
        raise Exception("Service error")

    # Trigger failures
    for _ in range(3):
        with pytest.raises(Exception):
            await breaker.call(failing_function)

    # Circuit should now be open
    assert breaker.is_open

    # Next call should be rejected
    with pytest.raises(CircuitBreakerError):
        await breaker.call(failing_function)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_knuspr_circuit_breaker_integration():
    from app.services.knuspr_with_circuit_breaker import get_protected_knuspr_client

    client = get_protected_knuspr_client(email, password)

    # Get metrics before
    metrics_before = client.get_circuit_metrics()

    # Make request
    try:
        products = await client.search_products("test")
    except CircuitBreakerError:
        pass

    # Get metrics after
    metrics_after = client.get_circuit_metrics()

    # Verify metrics updated
    assert metrics_after['total_requests'] > metrics_before['total_requests']
```

## Manual Operations

### Resetting a Circuit Breaker

⚠️ **Caution:** Only use in controlled situations (testing, emergency recovery)

```python
from app.utils.circuit_breaker import get_circuit_breaker

breaker = get_circuit_breaker("knuspr_api")
await breaker.reset()  # Manually close the circuit
```

### Checking All Circuit Breakers

```python
from app.utils.circuit_breaker import get_all_circuit_breakers

breakers = get_all_circuit_breakers()
for name, breaker in breakers.items():
    metrics = breaker.get_metrics()
    print(f"{name}: {metrics['state']} - {metrics['failure_rate']:.2%} failure rate")
```

## Troubleshooting

### Circuit Constantly Opening

**Symptoms:** Circuit transitions to OPEN frequently

**Possible Causes:**
1. Service is genuinely unstable
2. Failure threshold too low
3. Network issues
4. Timeout too aggressive

**Solutions:**
1. Investigate external service health
2. Increase `failure_threshold`
3. Increase `window_seconds` for longer averaging
4. Check network connectivity

### Circuit Never Opens

**Symptoms:** Requests keep failing but circuit stays CLOSED

**Possible Causes:**
1. Errors not being raised/caught properly
2. Success responses on failed requests
3. Failure threshold too high

**Solutions:**
1. Ensure exceptions are properly raised
2. Verify error detection logic
3. Decrease `failure_threshold`
4. Check metrics to see if failures are being counted

### Slow Recovery

**Symptoms:** Circuit stays OPEN for too long after service recovers

**Possible Causes:**
1. `timeout_seconds` too long
2. `success_threshold` too high
3. Service slow to respond in HALF_OPEN state

**Solutions:**
1. Decrease `timeout_seconds`
2. Decrease `success_threshold`
3. Increase `half_open_max_calls` for faster testing

## Performance Considerations

### Memory Usage
- Each circuit breaker maintains a sliding window of failure timestamps
- Memory scales with `window_seconds` and request rate
- Old timestamps are automatically cleaned up

### Lock Contention
- Circuit breaker uses asyncio.Lock for thread safety
- Minimal contention under normal load
- Consider multiple circuit breakers for different endpoints

### Overhead
- State checks: O(1) - very fast
- Failure tracking: O(n) where n = failures in window
- Negligible impact on request latency

## References

- [Circuit Breaker Pattern - Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

## Support

For issues or questions:
1. Check circuit breaker metrics at `/metrics`
2. Review logs for CircuitBreakerError occurrences
3. Verify external service health
4. Adjust configuration based on service characteristics
