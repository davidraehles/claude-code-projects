"""
Circuit Breaker pattern implementation for external API calls.

Provides fault tolerance and resilience by preventing cascading failures
when external services (like Knuspr API) are experiencing issues.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failure threshold exceeded, requests fail fast
- HALF_OPEN: Testing if service has recovered

The circuit breaker tracks failures over a sliding window and automatically
transitions between states based on success/failure thresholds.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 2  # Successes in half-open to close
    timeout_seconds: float = 60.0  # Time before trying half-open
    window_seconds: float = 60.0  # Rolling window for failure counting
    half_open_max_calls: int = 3  # Max concurrent calls in half-open state


@dataclass
class CircuitBreakerMetrics:
    """Metrics tracked by the circuit breaker."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0  # Requests rejected when circuit open
    state_transitions: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    current_state: CircuitState = CircuitState.CLOSED
    failure_timestamps: list = field(default_factory=list)
    half_open_successes: int = 0


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""

    def __init__(self, service_name: str, retry_after: float):
        """
        Initialize circuit breaker error.

        Args:
            service_name: Name of the service being protected
            retry_after: Seconds until circuit may close
        """
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker is OPEN for {service_name}. "
            f"Retry after {retry_after:.1f} seconds."
        )


class CircuitBreaker:
    """
    Circuit Breaker implementation for protecting external service calls.

    Usage:
        # Create circuit breaker for Knuspr API
        breaker = CircuitBreaker("knuspr_api")

        # Wrap API calls
        try:
            result = await breaker.call(knuspr_client.search_products, "milk")
        except CircuitBreakerError as e:
            logger.warning(f"Circuit open: {e}")
            # Handle gracefully, return cached data or error response
        except Exception as e:
            # API call failed, but circuit may still be closed
            logger.error(f"API error: {e}")

    The circuit breaker automatically tracks failures and successes,
    transitioning between states to prevent cascading failures.
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for this circuit breaker (e.g., "knuspr_api")
            config: Optional configuration, uses defaults if not provided
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.metrics = CircuitBreakerMetrics()
        self._state = CircuitState.CLOSED
        self._opened_at: Optional[float] = None
        self._lock = asyncio.Lock()

        logger.info(
            f"Circuit breaker '{name}' initialized",
            extra={
                "failure_threshold": self.config.failure_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            }
        )

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self._state == CircuitState.HALF_OPEN

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.

        Returns:
            Dictionary with current metrics and state
        """
        return {
            "name": self.name,
            "state": self._state.value,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "rejected_requests": self.metrics.rejected_requests,
            "state_transitions": self.metrics.state_transitions,
            "failure_rate": (
                self.metrics.failed_requests / self.metrics.total_requests
                if self.metrics.total_requests > 0
                else 0.0
            ),
            "last_failure_time": (
                datetime.fromtimestamp(self.metrics.last_failure_time).isoformat()
                if self.metrics.last_failure_time
                else None
            ),
            "last_success_time": (
                datetime.fromtimestamp(self.metrics.last_success_time).isoformat()
                if self.metrics.last_success_time
                else None
            ),
        }

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If func raises an exception (and circuit allows execution)
        """
        async with self._lock:
            self.metrics.total_requests += 1

            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.metrics.rejected_requests += 1
                    retry_after = self._get_retry_after()
                    logger.warning(
                        f"Circuit breaker '{self.name}' is OPEN, rejecting request",
                        extra={"retry_after": retry_after}
                    )
                    raise CircuitBreakerError(self.name, retry_after)

            # Limit concurrent requests in HALF_OPEN state
            if self._state == CircuitState.HALF_OPEN:
                if self.metrics.half_open_successes >= self.config.half_open_max_calls:
                    self.metrics.rejected_requests += 1
                    logger.debug(
                        f"Circuit breaker '{self.name}' is HALF_OPEN "
                        f"and at max concurrent calls, rejecting request"
                    )
                    raise CircuitBreakerError(self.name, 1.0)

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise

    async def _on_success(self) -> None:
        """Handle successful request."""
        async with self._lock:
            self.metrics.successful_requests += 1
            self.metrics.last_success_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self.metrics.half_open_successes += 1
                logger.debug(
                    f"Circuit breaker '{self.name}' success in HALF_OPEN state "
                    f"({self.metrics.half_open_successes}/{self.config.success_threshold})"
                )

                # Check if we should close the circuit
                if self.metrics.half_open_successes >= self.config.success_threshold:
                    self._transition_to_closed()

    async def _on_failure(self) -> None:
        """Handle failed request."""
        async with self._lock:
            current_time = time.time()
            self.metrics.failed_requests += 1
            self.metrics.last_failure_time = current_time

            # Track failure timestamp
            self.metrics.failure_timestamps.append(current_time)

            # Clean old failures outside the window
            window_start = current_time - self.config.window_seconds
            self.metrics.failure_timestamps = [
                ts for ts in self.metrics.failure_timestamps
                if ts > window_start
            ]

            recent_failures = len(self.metrics.failure_timestamps)

            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure",
                extra={
                    "recent_failures": recent_failures,
                    "threshold": self.config.failure_threshold,
                    "state": self._state.value,
                }
            )

            # Check if we should open the circuit
            if self._state == CircuitState.CLOSED:
                if recent_failures >= self.config.failure_threshold:
                    self._transition_to_open()
            elif self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self._opened_at:
            return True

        elapsed = time.time() - self._opened_at
        return elapsed >= self.config.timeout_seconds

    def _get_retry_after(self) -> float:
        """Calculate seconds until circuit may attempt reset."""
        if not self._opened_at:
            return 0.0

        elapsed = time.time() - self._opened_at
        remaining = max(0.0, self.config.timeout_seconds - elapsed)
        return remaining

    def _transition_to_open(self) -> None:
        """Transition circuit to OPEN state."""
        if self._state == CircuitState.OPEN:
            return

        self._state = CircuitState.OPEN
        self._opened_at = time.time()
        self.metrics.state_transitions += 1
        self.metrics.half_open_successes = 0

        logger.error(
            f"Circuit breaker '{self.name}' transitioned to OPEN",
            extra={
                "failed_requests": self.metrics.failed_requests,
                "timeout_seconds": self.config.timeout_seconds,
            }
        )

    def _transition_to_half_open(self) -> None:
        """Transition circuit to HALF_OPEN state."""
        if self._state == CircuitState.HALF_OPEN:
            return

        self._state = CircuitState.HALF_OPEN
        self.metrics.state_transitions += 1
        self.metrics.half_open_successes = 0

        logger.info(
            f"Circuit breaker '{self.name}' transitioned to HALF_OPEN",
            extra={"success_threshold": self.config.success_threshold}
        )

    def _transition_to_closed(self) -> None:
        """Transition circuit to CLOSED state."""
        if self._state == CircuitState.CLOSED:
            return

        self._state = CircuitState.CLOSED
        self._opened_at = None
        self.metrics.state_transitions += 1
        self.metrics.half_open_successes = 0
        self.metrics.failure_timestamps.clear()

        logger.info(
            f"Circuit breaker '{self.name}' transitioned to CLOSED",
            extra={"successful_requests": self.metrics.successful_requests}
        )

    async def reset(self) -> None:
        """
        Manually reset the circuit breaker to CLOSED state.

        This should be used cautiously, typically only for testing
        or administrative intervention.
        """
        async with self._lock:
            logger.warning(f"Circuit breaker '{self.name}' manually reset")
            self._transition_to_closed()


# Global registry of circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker by name.

    Args:
        name: Circuit breaker identifier
        config: Optional configuration (only used if creating new breaker)

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """
    Get all registered circuit breakers.

    Returns:
        Dictionary mapping names to CircuitBreaker instances
    """
    return _circuit_breakers.copy()
