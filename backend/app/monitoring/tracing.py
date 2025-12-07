"""
Distributed Tracing Module

Implements OpenTelemetry-based distributed tracing for the Go, Cart! application.
Integrates with Jaeger for trace collection, storage, and visualization.

Features:
- Request tracing across the entire application stack
- Database query tracing
- External API call tracing
- Async task tracing
- Error context capture
- Configurable sampling strategies
"""

import os
from typing import Optional, Dict, Any, Callable
from functools import wraps
import time

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    AlwaysOn,
    AlwaysOff,
)


# ============================================================================
# CONFIGURATION
# ============================================================================

class TracingConfig:
    """Configuration for distributed tracing."""

    # Jaeger configuration
    JAEGER_AGENT_HOST = os.getenv("JAEGER_AGENT_HOST", "jaeger")
    JAEGER_AGENT_PORT = int(os.getenv("JAEGER_AGENT_PORT", "6831"))
    JAEGER_COLLECTOR_ENDPOINT = os.getenv(
        "JAEGER_COLLECTOR_ENDPOINT",
        "http://jaeger:14268/api/traces"
    )

    # Service information
    SERVICE_NAME = os.getenv("SERVICE_NAME", "ai-meal-planner-api")
    SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
    ENVIRONMENT = os.getenv("APP_ENV", "development")

    # Sampling configuration
    SAMPLING_RATE = float(os.getenv("TRACING_SAMPLING_RATE", "0.1"))  # 10% default
    SAMPLE_ERRORS = os.getenv("TRACING_SAMPLE_ERRORS", "true").lower() == "true"
    SAMPLE_SLOW_REQUESTS = os.getenv("TRACING_SAMPLE_SLOW", "true").lower() == "true"
    SLOW_REQUEST_THRESHOLD = float(os.getenv("TRACING_SLOW_THRESHOLD", "1.0"))  # seconds

    # Feature flags
    TRACE_DATABASE_QUERIES = os.getenv("TRACE_DB_QUERIES", "true").lower() == "true"
    TRACE_REDIS_OPERATIONS = os.getenv("TRACE_REDIS", "true").lower() == "true"
    TRACE_HTTP_CALLS = os.getenv("TRACE_HTTP", "true").lower() == "true"

    # Performance
    MAX_SPAN_ATTRIBUTES = int(os.getenv("TRACING_MAX_ATTRS", "128"))
    EXPORT_BATCH_SIZE = int(os.getenv("TRACING_BATCH_SIZE", "512"))
    EXPORT_TIMEOUT_MS = int(os.getenv("TRACING_TIMEOUT_MS", "30000"))

    # Development settings
    CONSOLE_EXPORTER = os.getenv("TRACING_CONSOLE", "false").lower() == "true"


# ============================================================================
# CUSTOM SAMPLER
# ============================================================================

class CustomSampler:
    """
    Custom sampling strategy that:
    - Always samples errors (5xx responses)
    - Always samples slow requests (> threshold)
    - Samples other requests based on configured rate
    """

    def __init__(
        self,
        base_rate: float = 0.1,
        sample_errors: bool = True,
        sample_slow: bool = True,
        slow_threshold: float = 1.0,
    ):
        self.base_sampler = TraceIdRatioBased(base_rate)
        self.sample_errors = sample_errors
        self.sample_slow = sample_slow
        self.slow_threshold = slow_threshold

    def should_sample(
        self,
        context,
        trace_id,
        name,
        kind=None,
        attributes=None,
        links=None,
    ):
        """Determine if a span should be sampled."""

        # Always sample errors
        if self.sample_errors and attributes:
            if attributes.get("http.status_code", 0) >= 500:
                return AlwaysOn().should_sample(
                    context, trace_id, name, kind, attributes, links
                )

        # Always sample slow requests
        if self.sample_slow and attributes:
            duration = attributes.get("http.duration", 0)
            if duration > self.slow_threshold:
                return AlwaysOn().should_sample(
                    context, trace_id, name, kind, attributes, links
                )

        # Use base sampling rate for others
        return self.base_sampler.should_sample(
            context, trace_id, name, kind, attributes, links
        )


# ============================================================================
# TRACER INITIALIZATION
# ============================================================================

def init_tracing(app) -> Optional[TracerProvider]:
    """
    Initialize OpenTelemetry tracing with Jaeger exporter.

    Args:
        app: FastAPI application instance

    Returns:
        TracerProvider instance or None if tracing is disabled
    """

    if os.getenv("TRACING_ENABLED", "true").lower() != "true":
        print("Distributed tracing is disabled")
        return None

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: TracingConfig.SERVICE_NAME,
        "service.version": TracingConfig.SERVICE_VERSION,
        "deployment.environment": TracingConfig.ENVIRONMENT,
    })

    # Create tracer provider with custom sampler
    sampler = ParentBased(
        root=CustomSampler(
            base_rate=TracingConfig.SAMPLING_RATE,
            sample_errors=TracingConfig.SAMPLE_ERRORS,
            sample_slow=TracingConfig.SAMPLE_SLOW_REQUESTS,
            slow_threshold=TracingConfig.SLOW_REQUEST_THRESHOLD,
        )
    )

    provider = TracerProvider(resource=resource, sampler=sampler)

    # Add Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=TracingConfig.JAEGER_AGENT_HOST,
        agent_port=TracingConfig.JAEGER_AGENT_PORT,
        collector_endpoint=TracingConfig.JAEGER_COLLECTOR_ENDPOINT,
    )

    provider.add_span_processor(
        BatchSpanProcessor(
            jaeger_exporter,
            max_queue_size=2048,
            max_export_batch_size=TracingConfig.EXPORT_BATCH_SIZE,
            export_timeout_millis=TracingConfig.EXPORT_TIMEOUT_MS,
        )
    )

    # Add console exporter for development
    if TracingConfig.CONSOLE_EXPORTER:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy if enabled
    if TracingConfig.TRACE_DATABASE_QUERIES:
        SQLAlchemyInstrumentor().instrument()

    # Instrument Redis if enabled
    if TracingConfig.TRACE_REDIS_OPERATIONS:
        RedisInstrumentor().instrument()

    # Instrument HTTPX for external API calls
    if TracingConfig.TRACE_HTTP_CALLS:
        HTTPXClientInstrumentor().instrument()

    print(f"Distributed tracing initialized: {TracingConfig.SERVICE_NAME}")
    print(f"Jaeger endpoint: {TracingConfig.JAEGER_COLLECTOR_ENDPOINT}")
    print(f"Sampling rate: {TracingConfig.SAMPLING_RATE * 100}%")

    return provider


# ============================================================================
# TRACER INSTANCE
# ============================================================================

tracer = trace.get_tracer(__name__)


# ============================================================================
# TRACING UTILITIES
# ============================================================================

def get_current_span() -> Optional[trace.Span]:
    """Get the currently active span."""
    return trace.get_current_span()


def add_span_attribute(key: str, value: Any):
    """Add an attribute to the current span."""
    span = get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add an event to the current span."""
    span = get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})


def record_exception(exception: Exception, attributes: Optional[Dict[str, Any]] = None):
    """Record an exception in the current span."""
    span = get_current_span()
    if span:
        span.record_exception(exception, attributes=attributes or {})
        span.set_status(Status(StatusCode.ERROR, str(exception)))


# ============================================================================
# DECORATORS
# ============================================================================

def trace_function(
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to trace a function execution.

    Usage:
        @trace_function("process_recipe")
        async def process_recipe(recipe_id: int):
            ...
    """
    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name, kind=kind) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function arguments as attributes
                if args:
                    span.set_attribute("args.count", len(args))
                if kwargs:
                    span.set_attribute("kwargs.count", len(kwargs))

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name, kind=kind) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def trace_database_query(operation: str):
    """
    Decorator to trace database queries.

    Usage:
        @trace_database_query("get_recipe_by_id")
        async def get_recipe(db: Session, recipe_id: int):
            ...
    """
    return trace_function(
        name=f"db.{operation}",
        kind=SpanKind.CLIENT,
        attributes={"db.system": "postgresql", "db.operation": operation}
    )


def trace_external_api_call(service: str, operation: str):
    """
    Decorator to trace external API calls.

    Usage:
        @trace_external_api_call("knuspr", "add_to_cart")
        async def add_item_to_knuspr_cart(item_id: str):
            ...
    """
    return trace_function(
        name=f"external.{service}.{operation}",
        kind=SpanKind.CLIENT,
        attributes={
            "peer.service": service,
            "external.api": service,
            "operation": operation
        }
    )


def trace_background_task(task_name: str):
    """
    Decorator to trace background tasks.

    Usage:
        @trace_background_task("send_notification_email")
        async def send_email(user_id: int, message: str):
            ...
    """
    return trace_function(
        name=f"task.{task_name}",
        kind=SpanKind.INTERNAL,
        attributes={"task.name": task_name, "task.type": "background"}
    )


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

class TraceContext:
    """
    Context manager for creating traced code blocks.

    Usage:
        async with TraceContext("processing_recipe") as span:
            span.set_attribute("recipe.id", recipe_id)
            # ... processing code ...
    """

    def __init__(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.kind = kind
        self.attributes = attributes or {}
        self.span = None

    def __enter__(self):
        self.span = tracer.start_span(self.name, kind=self.kind)
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()
        return False

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)


# ============================================================================
# MIDDLEWARE INTEGRATION
# ============================================================================

def add_trace_correlation_id(request_id: str):
    """
    Add correlation ID to current span.
    Links request ID from Phase 2 WS1 to distributed traces.
    """
    span = get_current_span()
    if span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("correlation.id", request_id)


def add_user_context(user_id: Optional[int] = None, username: Optional[str] = None):
    """Add user context to current span."""
    span = get_current_span()
    if span:
        if user_id:
            span.set_attribute("user.id", user_id)
        if username:
            span.set_attribute("user.name", username)


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

class PerformanceMonitor:
    """Monitor tracing overhead and performance impact."""

    def __init__(self):
        self.span_count = 0
        self.total_overhead_ms = 0.0

    def record_span(self, overhead_ms: float):
        """Record span processing overhead."""
        self.span_count += 1
        self.total_overhead_ms += overhead_ms

    def get_average_overhead(self) -> float:
        """Get average overhead per span in milliseconds."""
        if self.span_count == 0:
            return 0.0
        return self.total_overhead_ms / self.span_count

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "span_count": self.span_count,
            "total_overhead_ms": self.total_overhead_ms,
            "average_overhead_ms": self.get_average_overhead(),
        }


performance_monitor = PerformanceMonitor()


# ============================================================================
# SHUTDOWN
# ============================================================================

def shutdown_tracing():
    """Gracefully shutdown tracing and flush remaining spans."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, 'shutdown'):
        provider.shutdown()
        print("Tracing shutdown complete")
