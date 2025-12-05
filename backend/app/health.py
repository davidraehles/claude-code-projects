"""
Health check utilities for monitoring system dependencies.

Provides comprehensive health checks for:
- Database connectivity (PostgreSQL)
- Redis connectivity
- Aggregated dependency health
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel
from sqlalchemy import text

from app.database import engine
from app.events.bus import get_event_bus
from app.logging_config import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status for a single component."""

    status: HealthStatus
    message: str
    latency_ms: float | None = None
    details: Dict[str, Any] | None = None


class HealthCheckResponse(BaseModel):
    """Comprehensive health check response."""

    status: HealthStatus
    timestamp: datetime
    version: str
    service: str
    components: Dict[str, ComponentHealth]


async def check_database() -> ComponentHealth:
    """
    Check database connectivity and responsiveness.

    Returns:
        ComponentHealth: Database health status
    """
    start_time = datetime.now()

    try:
        # Test database connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.debug("Database health check passed", extra={"latency_ms": latency_ms})

        return ComponentHealth(
            status=HealthStatus.HEALTHY,
            message="Database connection successful",
            latency_ms=round(latency_ms, 2),
            details={
                "engine": str(engine.url.drivername),
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
            },
        )

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.error(
            "Database health check failed",
            extra={"error": str(e), "latency_ms": latency_ms},
            exc_info=True,
        )

        return ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}",
            latency_ms=round(latency_ms, 2),
        )


async def check_redis() -> ComponentHealth:
    """
    Check Redis connectivity and responsiveness.

    Returns:
        ComponentHealth: Redis health status
    """
    start_time = datetime.now()

    try:
        event_bus = get_event_bus()

        # Check if Redis client exists and is connected
        if not event_bus.redis_client:
            logger.warning("Redis client not initialized")
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                message="Redis client not initialized",
                latency_ms=0.0,
            )

        # Test Redis connection with a ping
        await event_bus.redis_client.ping()

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.debug("Redis health check passed", extra={"latency_ms": latency_ms})

        return ComponentHealth(
            status=HealthStatus.HEALTHY,
            message="Redis connection successful",
            latency_ms=round(latency_ms, 2),
            details={
                "host": event_bus.redis_host,
                "port": event_bus.redis_port,
                "db": event_bus.redis_db,
            },
        )

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.warning(
            "Redis health check failed",
            extra={"error": str(e), "latency_ms": latency_ms},
        )

        # Redis is optional, so mark as degraded rather than unhealthy
        return ComponentHealth(
            status=HealthStatus.DEGRADED,
            message=f"Redis connection failed: {str(e)}",
            latency_ms=round(latency_ms, 2),
        )


async def check_dependencies() -> HealthCheckResponse:
    """
    Perform comprehensive health check of all dependencies.

    Returns:
        HealthCheckResponse: Aggregated health status
    """
    # Run all health checks concurrently
    database_health = await check_database()
    redis_health = await check_redis()

    # Aggregate component statuses
    components = {
        "database": database_health,
        "redis": redis_health,
    }

    # Determine overall status
    # System is unhealthy if any critical component (database) is unhealthy
    # System is degraded if any component is degraded or unhealthy
    if database_health.status == HealthStatus.UNHEALTHY:
        overall_status = HealthStatus.UNHEALTHY
    elif (
        database_health.status == HealthStatus.DEGRADED
        or redis_health.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
    ):
        overall_status = HealthStatus.DEGRADED
    else:
        overall_status = HealthStatus.HEALTHY

    logger.info(
        "Health check completed",
        extra={
            "overall_status": overall_status,
            "database_status": database_health.status,
            "redis_status": redis_health.status,
        },
    )

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        service="recipe-meal-planning-api",
        components=components,
    )


async def check_liveness() -> Dict[str, str]:
    """
    Simple liveness probe for Kubernetes/container orchestration.

    Verifies the process is running and responsive.

    Returns:
        dict: Liveness status
    """
    return {"status": "alive", "timestamp": datetime.now().isoformat()}


async def check_readiness() -> HealthCheckResponse:
    """
    Readiness probe for Kubernetes/container orchestration.

    Verifies all dependencies are ready before accepting traffic.

    Returns:
        HealthCheckResponse: Full dependency health check
    """
    return await check_dependencies()
