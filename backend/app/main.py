"""
FastAPI application entry point for Recipe & Meal Planning System.

Initializes the FastAPI app with middleware, routes, and event handlers.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.logging_config import setup_logging, get_logger
from app.health import (
    check_dependencies,
    check_liveness,
    check_readiness,
    check_dependencies_deep,
    get_dependency_details,
)
from app.schemas.error import ErrorResponse, ErrorType, AppException
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.csrf_middleware import CSRFMiddleware
from app.middleware.input_validation import InputValidationMiddleware

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# Initialize Sentry error tracking (if configured)
from app.monitoring.sentry_integration import init_sentry
init_sentry()


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage application lifecycle events.

    Startup:
        - Initialize database tables (dev only)
        - Connect to Redis event bus
        - Start background agent workers
        - Start metrics collection background task

    Shutdown:
        - Graceful shutdown with timeout
        - Close database connections
        - Disconnect from Redis
        - Flush metrics
        - Stop background tasks
    """
    import signal
    import asyncio
    from app.events.bus import get_event_bus
    from app.monitoring.metrics import update_db_pool_metrics, update_circuit_breaker_metrics
    from app.utils.circuit_breaker import get_all_circuit_breakers

    # Startup
    logger.info("Application startup initiated")

    # Create tables (in production, use Alembic migrations instead)
    if os.getenv("APP_ENV") == "development":
        logger.info("Creating database tables (development mode)")
        Base.metadata.create_all(bind=engine)

    # Initialize Redis event bus
    try:
        event_bus = get_event_bus()
        await event_bus.connect()
        logger.info("Event bus (Redis) connected successfully")
    except Exception as e:
        logger.warning("Could not connect to Redis event bus", extra={"error": str(e)})
        logger.info("Application will continue without event bus functionality")

    # Start background task for periodic metrics collection
    metrics_task = None
    shutdown_event = asyncio.Event()

    async def collect_metrics_periodically():
        """Collect DB pool and circuit breaker metrics every 15 seconds."""
        while not shutdown_event.is_set():
            try:
                # Update database pool metrics
                try:
                    pool = engine.pool
                    pool_size = pool.size()
                    checked_out = pool.checkedout()
                    overflow = pool.overflow()
                    update_db_pool_metrics(pool_size, checked_out, overflow)
                except Exception as e:
                    logger.debug(f"Failed to collect DB pool metrics: {e}")

                # Update circuit breaker metrics
                try:
                    circuit_breakers = get_all_circuit_breakers()
                    for name, breaker in circuit_breakers.items():
                        metrics_dict = breaker.get_metrics()
                        update_circuit_breaker_metrics(name, metrics_dict)
                except Exception as e:
                    logger.debug(f"Failed to collect circuit breaker metrics: {e}")

            except Exception as e:
                logger.error(f"Error in metrics collection: {e}", exc_info=True)

            # Wait 15 seconds or until shutdown
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=15.0)
            except asyncio.TimeoutError:
                pass

    # Start metrics collection task
    metrics_task = asyncio.create_task(collect_metrics_periodically())

    logger.info("Application startup completed successfully")

    yield

    # Shutdown - Graceful with timeout
    logger.info("Application shutdown initiated")

    # Signal metrics task to stop
    shutdown_event.set()

    # Wait for metrics task to complete (with timeout)
    if metrics_task:
        try:
            await asyncio.wait_for(metrics_task, timeout=5.0)
            logger.info("Metrics collection task stopped")
        except asyncio.TimeoutError:
            logger.warning("Metrics collection task did not stop in time, cancelling")
            metrics_task.cancel()
            try:
                await metrics_task
            except asyncio.CancelledError:
                pass

    # Disconnect from Redis event bus
    try:
        event_bus = get_event_bus()
        await event_bus.disconnect()
        logger.info("Event bus (Redis) disconnected")
    except Exception as e:
        logger.warning("Error during event bus shutdown", extra={"error": str(e)}, exc_info=True)

    # Close database connections
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.warning("Error closing database connections", extra={"error": str(e)}, exc_info=True)

    logger.info("Application shutdown completed")


# Initialize FastAPI application
app = FastAPI(
    title="Recipe & Meal Planning API",
    description="Multi-agent system for recipe harvesting, meal planning, and grocery shopping",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration (production-hardened)
def get_cors_origins():
    """
    Get CORS origins with secure defaults.

    In production, requires explicit CORS_ORIGINS configuration.
    In development, defaults to localhost for convenience.

    Returns:
        List of allowed origin patterns

    Raises:
        ValueError: If in production and CORS_ORIGINS not configured
    """
    origins_str = os.getenv("CORS_ORIGINS")

    if not origins_str:
        if os.getenv("APP_ENV") == "production":
            raise ValueError(
                "CORS_ORIGINS environment variable required in production. "
                "Set to comma-separated list of allowed origins: "
                "'https://example.com,https://app.example.com'"
            )
        # Development: allow localhost
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

    # Parse configured origins
    origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    # Reject empty list in production (configuration error)
    if not origins:
        if os.getenv("APP_ENV") == "production":
            raise ValueError(
                "CORS_ORIGINS is set but empty after parsing. "
                "Explicit origins required in production. "
                "Set to comma-separated list of allowed origins: "
                "'https://example.com,https://app.example.com'"
            )
        # Development: log warning and return localhost defaults
        logger.warning("CORS_ORIGINS is empty after parsing. Using localhost defaults for development.")
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

    # Reject wildcard in production
    if "*" in origins and os.getenv("APP_ENV") == "production":
        raise ValueError(
            "CORS wildcard '*' not allowed in production. "
            "Explicitly list allowed origins in CORS_ORIGINS environment variable."
        )

    return origins


cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-Correlation-ID", "X-CSRF-Token"],
    expose_headers=["X-Request-ID", "X-Correlation-ID", "X-CSRF-Token"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Request ID middleware for distributed tracing (FIRST - adds request ID to all requests)
app.add_middleware(RequestIdMiddleware)

# Correlation ID middleware for end-to-end request tracking (EARLY - after request ID)
app.add_middleware(CorrelationIdMiddleware)

# Input validation middleware (EARLY - validate and sanitize input)
app.add_middleware(InputValidationMiddleware)

# Security headers middleware (after input validation, before rate limiting)
from app.middleware.security_headers import SecurityHeadersMiddleware
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=os.getenv("APP_ENV") == "production",
    hsts_max_age=31536000  # 1 year
)

# Rate limiting middleware (BEFORE CSRF - blocks abusive requests early)
from app.middleware.rate_limit_middleware import RateLimitMiddleware
# Get Redis client for rate limiting if available
try:
    from app.events.bus import get_event_bus
    redis_client = get_event_bus().redis_client
except Exception:
    redis_client = None
    logger.warning("Redis not available for rate limiting, using in-memory fallback")

app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis_client,
    default_limit=int(os.getenv("RATE_LIMIT_DEFAULT", "100")),
    default_window=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
    enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
)

# CSRF protection middleware (AFTER rate limiting - exempt health, metrics, and docs endpoints)
app.add_middleware(CSRFMiddleware, exempt_paths=["/health", "/health/live", "/health/ready", "/metrics", "/api/docs", "/api/redoc", "/"])

# Prometheus metrics middleware (should be last to measure total request time)
from app.monitoring.middleware import PrometheusMiddleware
app.add_middleware(PrometheusMiddleware)


# Prometheus metrics endpoint
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

@app.get("/metrics", tags=["System"])
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        Metrics in Prometheus format
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Health check endpoints - Kubernetes/container orchestration
@app.get("/health/live", tags=["System"], response_model=dict)
async def liveness_probe():
    """
    Liveness probe for Kubernetes.

    Indicates if the process is running and responsive.
    Useful for restarting unhealthy containers.

    Returns:
        dict: Liveness status
    """
    return await check_liveness()


@app.get("/health/ready", tags=["System"])
async def readiness_probe():
    """
    Readiness probe for Kubernetes.

    Verifies all dependencies are ready before accepting traffic.

    Returns:
        HealthCheckResponse: Full dependency health check
    """
    return await check_readiness()


@app.get("/health", tags=["System"])
async def health_check():
    """
    Comprehensive health check endpoint for monitoring and load balancers.

    Returns full dependency status including database, Redis, etc.

    Returns:
        HealthCheckResponse: Aggregated health status
    """
    return await check_dependencies()


@app.get("/health/deep", tags=["System"])
async def deep_health_check():
    """
    Deep health check with comprehensive dependency metrics.

    Performs detailed checks on all system components including:
    - Database connection and pool metrics
    - Redis connectivity and memory usage
    - Circuit breaker states
    - System resources (CPU, memory, disk)

    Note: This endpoint may take up to 5 seconds to complete.

    Returns:
        HealthCheckResponse: Detailed health status with metrics
    """
    return await check_dependencies_deep()


@app.get("/health/dependencies", tags=["System"])
async def dependency_health():
    """
    Get detailed dependency status and metrics.

    Returns comprehensive information about all system dependencies
    including latency, error rates, and resource usage.

    Returns:
        dict: Detailed dependency health information
    """
    return await get_dependency_details()


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: Welcome message and documentation links
    """
    return {
        "message": "Recipe & Meal Planning API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Exception handlers for standardized error responses
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handler for application exceptions with proper error categorization.

    Args:
        request: The FastAPI request object
        exc: The AppException that was raised

    Returns:
        JSONResponse: Standardized error response
    """
    error_response = ErrorResponse(
        error_type=exc.error_type,
        message=exc.message,
        details=exc.details,
        path=str(request.url.path),
        request_id=request.headers.get("X-Request-ID"),
    )

    logger.warning(
        f"Application error: {exc.error_type}",
        extra={
            "error_id": error_response.error_id,
            "error_type": exc.error_type,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Logs errors and returns standardized 500 response.

    Args:
        request: The FastAPI request object
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response with 500 status
    """
    error_response = ErrorResponse(
        error_type=ErrorType.SERVER,
        message="Internal server error",
        details={"error": str(exc)} if os.getenv("APP_ENV") == "development" else None,
        path=str(request.url.path),
        request_id=request.headers.get("X-Request-ID"),
    )

    logger.error(
        "Unhandled exception",
        extra={
            "error_id": error_response.error_id,
            "path": str(request.url.path),
            "error": str(exc),
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(mode="json"),
    )


# Import and include routers
from app.api.v1 import recipes, ingredients, users, meal_plans, auth, grocery_carts, knuspr_credentials, workflows

app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["Recipes"])
app.include_router(ingredients.router, prefix="/api/v1/ingredients", tags=["Ingredients"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(meal_plans.router, prefix="/api/v1/meal-plans", tags=["Meal Plans"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(grocery_carts.router, tags=["Grocery Carts"])
app.include_router(knuspr_credentials.router, tags=["Knuspr Credentials"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"🌐 Starting server on {host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("APP_ENV") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
