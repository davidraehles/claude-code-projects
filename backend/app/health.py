"""
Health check utilities for monitoring system dependencies.

Provides comprehensive health checks for:
- Database connectivity (PostgreSQL)
- Redis connectivity
- Circuit breaker state
- System resources (CPU, memory, disk)
- Aggregated dependency health
"""

import asyncio
import os
import psutil
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel
from sqlalchemy import text

from app.database import engine
from app.events.bus import get_event_bus
from app.logging_config import get_logger
from app.utils.circuit_breaker import get_all_circuit_breakers

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


async def check_circuit_breakers() -> ComponentHealth:
    """
    Check circuit breaker states and metrics.

    Returns:
        ComponentHealth: Circuit breaker health status
    """
    start_time = datetime.now()

    try:
        circuit_breakers = get_all_circuit_breakers()

        if not circuit_breakers:
            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                message="No circuit breakers registered",
                latency_ms=0.0,
                details={"count": 0},
            )

        # Aggregate circuit breaker states
        total_breakers = len(circuit_breakers)
        open_breakers = []
        half_open_breakers = []
        metrics_summary = {}

        for name, breaker in circuit_breakers.items():
            metrics = breaker.get_metrics()
            metrics_summary[name] = metrics

            if breaker.is_open:
                open_breakers.append(name)
            elif breaker.is_half_open:
                half_open_breakers.append(name)

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Determine status based on circuit breaker states
        if open_breakers:
            status = HealthStatus.DEGRADED
            message = f"{len(open_breakers)} circuit breaker(s) OPEN: {', '.join(open_breakers)}"
        elif half_open_breakers:
            status = HealthStatus.DEGRADED
            message = f"{len(half_open_breakers)} circuit breaker(s) HALF_OPEN: {', '.join(half_open_breakers)}"
        else:
            status = HealthStatus.HEALTHY
            message = f"All {total_breakers} circuit breaker(s) CLOSED"

        logger.debug("Circuit breaker health check completed", extra={"latency_ms": latency_ms})

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=round(latency_ms, 2),
            details={
                "total": total_breakers,
                "open": len(open_breakers),
                "half_open": len(half_open_breakers),
                "closed": total_breakers - len(open_breakers) - len(half_open_breakers),
                "metrics": metrics_summary,
            },
        )

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.error(
            "Circuit breaker health check failed",
            extra={"error": str(e), "latency_ms": latency_ms},
            exc_info=True,
        )

        return ComponentHealth(
            status=HealthStatus.DEGRADED,
            message=f"Circuit breaker check failed: {str(e)}",
            latency_ms=round(latency_ms, 2),
        )


async def check_system_resources() -> ComponentHealth:
    """
    Check system resource usage (CPU, memory, disk).

    Returns:
        ComponentHealth: System resource health status
    """
    start_time = datetime.now()

    try:
        # Get CPU usage (1 second average)
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Get memory usage
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)
        memory_percent = memory.percent

        # Get disk usage for root partition
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024 * 1024 * 1024)

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Determine status based on thresholds
        warnings = []
        if disk_percent > 90:
            warnings.append(f"Disk usage critical: {disk_percent}%")
        elif disk_percent > 85:
            warnings.append(f"Disk usage high: {disk_percent}%")

        if cpu_percent > 90:
            warnings.append(f"CPU usage critical: {cpu_percent}%")
        elif cpu_percent > 80:
            warnings.append(f"CPU usage high: {cpu_percent}%")

        if memory_mb > 2048:  # > 2GB
            warnings.append(f"Memory usage high: {memory_mb:.0f}MB")

        if warnings:
            status = HealthStatus.DEGRADED
            message = "; ".join(warnings)
        else:
            status = HealthStatus.HEALTHY
            message = "System resources healthy"

        logger.debug("System resource health check completed", extra={"latency_ms": latency_ms})

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=round(latency_ms, 2),
            details={
                "cpu_percent": round(cpu_percent, 1),
                "memory_mb": round(memory_mb, 1),
                "memory_percent": round(memory_percent, 1),
                "disk_percent": round(disk_percent, 1),
                "disk_free_gb": round(disk_free_gb, 2),
            },
        )

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.error(
            "System resource health check failed",
            extra={"error": str(e), "latency_ms": latency_ms},
            exc_info=True,
        )

        return ComponentHealth(
            status=HealthStatus.DEGRADED,
            message=f"System resource check failed: {str(e)}",
            latency_ms=round(latency_ms, 2),
        )


async def check_database_pool() -> ComponentHealth:
    """
    Check database connection pool health and metrics.

    Returns:
        ComponentHealth: Database pool health status
    """
    start_time = datetime.now()

    try:
        pool = engine.pool
        pool_size = pool.size()
        checked_out = pool.checkedout()
        overflow = pool.overflow()

        # Calculate pool usage percentage
        total_connections = pool_size + overflow
        usage_percent = (checked_out / total_connections * 100) if total_connections > 0 else 0

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Determine status based on pool usage
        if usage_percent > 90:
            status = HealthStatus.DEGRADED
            message = f"Connection pool usage critical: {usage_percent:.0f}%"
        elif usage_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Connection pool usage high: {usage_percent:.0f}%"
        else:
            status = HealthStatus.HEALTHY
            message = "Connection pool healthy"

        logger.debug("Database pool health check completed", extra={"latency_ms": latency_ms})

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=round(latency_ms, 2),
            details={
                "pool_size": pool_size,
                "checked_out": checked_out,
                "overflow": overflow,
                "usage_percent": round(usage_percent, 1),
            },
        )

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.error(
            "Database pool health check failed",
            extra={"error": str(e), "latency_ms": latency_ms},
            exc_info=True,
        )

        return ComponentHealth(
            status=HealthStatus.DEGRADED,
            message=f"Database pool check failed: {str(e)}",
            latency_ms=round(latency_ms, 2),
        )


async def check_redis_memory() -> ComponentHealth:
    """
    Check Redis memory usage and health.

    Returns:
        ComponentHealth: Redis memory health status
    """
    start_time = datetime.now()

    try:
        event_bus = get_event_bus()

        if not event_bus.redis_client:
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                message="Redis client not initialized",
                latency_ms=0.0,
            )

        # Get Redis info
        info = await event_bus.redis_client.info("memory")

        used_memory = info.get("used_memory", 0)
        used_memory_mb = used_memory / (1024 * 1024)
        maxmemory = info.get("maxmemory", 0)

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Determine status based on memory usage
        if maxmemory > 0:
            memory_percent = (used_memory / maxmemory) * 100
            if memory_percent > 90:
                status = HealthStatus.DEGRADED
                message = f"Redis memory usage critical: {memory_percent:.0f}%"
            elif memory_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Redis memory usage high: {memory_percent:.0f}%"
            else:
                status = HealthStatus.HEALTHY
                message = "Redis memory healthy"
        else:
            status = HealthStatus.HEALTHY
            message = "Redis memory healthy (no max limit)"
            memory_percent = 0.0

        logger.debug("Redis memory health check completed", extra={"latency_ms": latency_ms})

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=round(latency_ms, 2),
            details={
                "used_memory_mb": round(used_memory_mb, 2),
                "maxmemory_mb": round(maxmemory / (1024 * 1024), 2) if maxmemory > 0 else None,
                "memory_percent": round(memory_percent, 1) if maxmemory > 0 else None,
            },
        )

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.warning(
            "Redis memory health check failed",
            extra={"error": str(e), "latency_ms": latency_ms},
        )

        return ComponentHealth(
            status=HealthStatus.DEGRADED,
            message=f"Redis memory check failed: {str(e)}",
            latency_ms=round(latency_ms, 2),
        )


async def check_dependencies_deep() -> HealthCheckResponse:
    """
    Perform deep health check of all dependencies with detailed metrics.

    This endpoint performs more comprehensive checks than the standard health
    endpoint and may take longer to complete (up to 5 seconds).

    Returns:
        HealthCheckResponse: Detailed health status with all metrics
    """
    # Run all health checks concurrently with timeout
    try:
        results = await asyncio.wait_for(
            asyncio.gather(
                check_database(),
                check_database_pool(),
                check_redis(),
                check_redis_memory(),
                check_circuit_breakers(),
                check_system_resources(),
                return_exceptions=True,
            ),
            timeout=5.0,
        )

        database_health, pool_health, redis_health, redis_memory_health, breaker_health, system_health = results

        # Handle exceptions from individual checks
        components = {}

        if isinstance(database_health, Exception):
            components["database"] = ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Database check error: {str(database_health)}",
                latency_ms=0.0,
            )
        else:
            components["database"] = database_health

        if isinstance(pool_health, Exception):
            components["database_pool"] = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Pool check error: {str(pool_health)}",
                latency_ms=0.0,
            )
        else:
            components["database_pool"] = pool_health

        if isinstance(redis_health, Exception):
            components["redis"] = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Redis check error: {str(redis_health)}",
                latency_ms=0.0,
            )
        else:
            components["redis"] = redis_health

        if isinstance(redis_memory_health, Exception):
            components["redis_memory"] = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Redis memory check error: {str(redis_memory_health)}",
                latency_ms=0.0,
            )
        else:
            components["redis_memory"] = redis_memory_health

        if isinstance(breaker_health, Exception):
            components["circuit_breaker"] = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Circuit breaker check error: {str(breaker_health)}",
                latency_ms=0.0,
            )
        else:
            components["circuit_breaker"] = breaker_health

        if isinstance(system_health, Exception):
            components["system"] = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"System check error: {str(system_health)}",
                latency_ms=0.0,
            )
        else:
            components["system"] = system_health

        # Determine overall status
        # System is unhealthy if database is unhealthy
        # System is degraded if any component is degraded or unhealthy
        if components["database"].status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
        elif any(
            comp.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
            for comp in components.values()
        ):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        logger.info(
            "Deep health check completed",
            extra={
                "overall_status": overall_status,
                "component_count": len(components),
            },
        )

        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version="2.0.0",
            service="recipe-meal-planning-api",
            components=components,
        )

    except asyncio.TimeoutError:
        logger.error("Deep health check timed out after 5 seconds")

        return HealthCheckResponse(
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.now(),
            version="2.0.0",
            service="recipe-meal-planning-api",
            components={
                "timeout": ComponentHealth(
                    status=HealthStatus.UNHEALTHY,
                    message="Health check timed out after 5 seconds",
                    latency_ms=5000.0,
                )
            },
        )


async def get_dependency_details() -> Dict[str, Any]:
    """
    Get detailed dependency status and metrics.

    Returns:
        Dict with detailed dependency information
    """
    try:
        # Run deep health check
        health_response = await check_dependencies_deep()

        # Extract detailed metrics
        result = {
            "status": health_response.status,
            "timestamp": health_response.timestamp.isoformat(),
            "version": health_response.version,
            "dependencies": {},
        }

        for name, component in health_response.components.items():
            result["dependencies"][name] = {
                "status": component.status,
                "message": component.message,
                "latency_ms": component.latency_ms,
                "metrics": component.details or {},
            }

        return result

    except Exception as e:
        logger.error("Failed to get dependency details", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
