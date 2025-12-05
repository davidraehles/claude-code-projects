"""
Unit tests for extended health check functionality.

Tests:
- Circuit breaker health checks
- System resource health checks
- Database pool health checks
- Redis memory health checks
- Deep health check orchestration
- Dependency details endpoint
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.health import (
    HealthStatus,
    ComponentHealth,
    HealthCheckResponse,
    check_circuit_breakers,
    check_system_resources,
    check_database_pool,
    check_redis_memory,
    check_dependencies_deep,
    get_dependency_details,
)
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


class TestCircuitBreakerHealthCheck:
    """Test cases for circuit breaker health checks."""

    @pytest.mark.asyncio
    async def test_no_circuit_breakers_registered(self):
        """Test health check when no circuit breakers are registered."""
        with patch("app.health.get_all_circuit_breakers", return_value={}):
            result = await check_circuit_breakers()

            assert result.status == HealthStatus.HEALTHY
            assert "No circuit breakers" in result.message
            assert result.details["count"] == 0

    @pytest.mark.asyncio
    async def test_all_circuit_breakers_closed(self):
        """Test health check when all circuit breakers are closed."""
        # Create mock circuit breakers in CLOSED state
        breaker1 = MagicMock(spec=CircuitBreaker)
        breaker1.is_open = False
        breaker1.is_half_open = False
        breaker1.get_metrics.return_value = {
            "state": "closed",
            "total_requests": 100,
            "failed_requests": 0,
        }

        breaker2 = MagicMock(spec=CircuitBreaker)
        breaker2.is_open = False
        breaker2.is_half_open = False
        breaker2.get_metrics.return_value = {
            "state": "closed",
            "total_requests": 50,
            "failed_requests": 0,
        }

        mock_breakers = {"api1": breaker1, "api2": breaker2}

        with patch("app.health.get_all_circuit_breakers", return_value=mock_breakers):
            result = await check_circuit_breakers()

            assert result.status == HealthStatus.HEALTHY
            assert "All 2 circuit breaker(s) CLOSED" in result.message
            assert result.details["total"] == 2
            assert result.details["open"] == 0
            assert result.details["half_open"] == 0
            assert result.details["closed"] == 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_open(self):
        """Test health check when a circuit breaker is open."""
        breaker1 = MagicMock(spec=CircuitBreaker)
        breaker1.is_open = True
        breaker1.is_half_open = False
        breaker1.get_metrics.return_value = {
            "state": "open",
            "total_requests": 100,
            "failed_requests": 10,
        }

        mock_breakers = {"failing_api": breaker1}

        with patch("app.health.get_all_circuit_breakers", return_value=mock_breakers):
            result = await check_circuit_breakers()

            assert result.status == HealthStatus.DEGRADED
            assert "1 circuit breaker(s) OPEN" in result.message
            assert "failing_api" in result.message
            assert result.details["open"] == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open(self):
        """Test health check when a circuit breaker is half-open."""
        breaker1 = MagicMock(spec=CircuitBreaker)
        breaker1.is_open = False
        breaker1.is_half_open = True
        breaker1.get_metrics.return_value = {
            "state": "half_open",
            "total_requests": 100,
            "failed_requests": 5,
        }

        mock_breakers = {"recovering_api": breaker1}

        with patch("app.health.get_all_circuit_breakers", return_value=mock_breakers):
            result = await check_circuit_breakers()

            assert result.status == HealthStatus.DEGRADED
            assert "1 circuit breaker(s) HALF_OPEN" in result.message
            assert "recovering_api" in result.message
            assert result.details["half_open"] == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_check_exception(self):
        """Test handling of exceptions during circuit breaker check."""
        with patch(
            "app.health.get_all_circuit_breakers",
            side_effect=Exception("Circuit breaker registry error"),
        ):
            result = await check_circuit_breakers()

            assert result.status == HealthStatus.DEGRADED
            assert "Circuit breaker check failed" in result.message


class TestSystemResourcesHealthCheck:
    """Test cases for system resource health checks."""

    @pytest.mark.asyncio
    async def test_healthy_system_resources(self):
        """Test health check with healthy system resources."""
        with patch("psutil.cpu_percent", return_value=50.0), patch(
            "psutil.virtual_memory"
        ) as mock_memory, patch("psutil.disk_usage") as mock_disk:

            # Mock memory info
            mock_memory.return_value = MagicMock(
                used=512 * 1024 * 1024,  # 512 MB
                percent=25.0,
            )

            # Mock disk info
            mock_disk.return_value = MagicMock(
                percent=50.0,
                free=100 * 1024 * 1024 * 1024,  # 100 GB
            )

            result = await check_system_resources()

            assert result.status == HealthStatus.HEALTHY
            assert "System resources healthy" in result.message
            assert result.details["cpu_percent"] == 50.0
            assert result.details["memory_mb"] == 512.0
            assert result.details["disk_percent"] == 50.0

    @pytest.mark.asyncio
    async def test_high_cpu_usage(self):
        """Test health check with high CPU usage."""
        with patch("psutil.cpu_percent", return_value=85.0), patch(
            "psutil.virtual_memory"
        ) as mock_memory, patch("psutil.disk_usage") as mock_disk:

            mock_memory.return_value = MagicMock(
                used=512 * 1024 * 1024,
                percent=25.0,
            )
            mock_disk.return_value = MagicMock(
                percent=50.0,
                free=100 * 1024 * 1024 * 1024,
            )

            result = await check_system_resources()

            assert result.status == HealthStatus.DEGRADED
            assert "CPU usage high" in result.message
            assert result.details["cpu_percent"] == 85.0

    @pytest.mark.asyncio
    async def test_critical_cpu_usage(self):
        """Test health check with critical CPU usage."""
        with patch("psutil.cpu_percent", return_value=95.0), patch(
            "psutil.virtual_memory"
        ) as mock_memory, patch("psutil.disk_usage") as mock_disk:

            mock_memory.return_value = MagicMock(
                used=512 * 1024 * 1024,
                percent=25.0,
            )
            mock_disk.return_value = MagicMock(
                percent=50.0,
                free=100 * 1024 * 1024 * 1024,
            )

            result = await check_system_resources()

            assert result.status == HealthStatus.DEGRADED
            assert "CPU usage critical" in result.message
            assert result.details["cpu_percent"] == 95.0

    @pytest.mark.asyncio
    async def test_high_disk_usage(self):
        """Test health check with high disk usage."""
        with patch("psutil.cpu_percent", return_value=50.0), patch(
            "psutil.virtual_memory"
        ) as mock_memory, patch("psutil.disk_usage") as mock_disk:

            mock_memory.return_value = MagicMock(
                used=512 * 1024 * 1024,
                percent=25.0,
            )
            mock_disk.return_value = MagicMock(
                percent=88.0,  # High disk usage
                free=10 * 1024 * 1024 * 1024,  # 10 GB
            )

            result = await check_system_resources()

            assert result.status == HealthStatus.DEGRADED
            assert "Disk usage high" in result.message
            assert result.details["disk_percent"] == 88.0

    @pytest.mark.asyncio
    async def test_high_memory_usage(self):
        """Test health check with high memory usage."""
        with patch("psutil.cpu_percent", return_value=50.0), patch(
            "psutil.virtual_memory"
        ) as mock_memory, patch("psutil.disk_usage") as mock_disk:

            mock_memory.return_value = MagicMock(
                used=2500 * 1024 * 1024,  # 2.5 GB
                percent=75.0,
            )
            mock_disk.return_value = MagicMock(
                percent=50.0,
                free=100 * 1024 * 1024 * 1024,
            )

            result = await check_system_resources()

            assert result.status == HealthStatus.DEGRADED
            assert "Memory usage high" in result.message
            assert result.details["memory_mb"] == 2500.0

    @pytest.mark.asyncio
    async def test_system_resources_check_exception(self):
        """Test handling of exceptions during system resource check."""
        with patch("psutil.cpu_percent", side_effect=Exception("psutil error")):
            result = await check_system_resources()

            assert result.status == HealthStatus.DEGRADED
            assert "System resource check failed" in result.message


class TestDatabasePoolHealthCheck:
    """Test cases for database pool health checks."""

    @pytest.mark.asyncio
    async def test_healthy_database_pool(self):
        """Test health check with healthy database pool."""
        with patch("app.health.engine") as mock_engine:
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedout.return_value = 3
            mock_pool.overflow.return_value = 0

            mock_engine.pool = mock_pool

            result = await check_database_pool()

            assert result.status == HealthStatus.HEALTHY
            assert "Connection pool healthy" in result.message
            assert result.details["pool_size"] == 10
            assert result.details["checked_out"] == 3
            assert result.details["usage_percent"] == 30.0

    @pytest.mark.asyncio
    async def test_high_database_pool_usage(self):
        """Test health check with high database pool usage."""
        with patch("app.health.engine") as mock_engine:
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedout.return_value = 9  # 90% usage
            mock_pool.overflow.return_value = 0

            mock_engine.pool = mock_pool

            result = await check_database_pool()

            assert result.status == HealthStatus.DEGRADED
            assert "Connection pool usage high" in result.message
            assert result.details["usage_percent"] == 90.0

    @pytest.mark.asyncio
    async def test_critical_database_pool_usage(self):
        """Test health check with critical database pool usage."""
        with patch("app.health.engine") as mock_engine:
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedout.return_value = 10  # 100% usage
            mock_pool.overflow.return_value = 0

            mock_engine.pool = mock_pool

            result = await check_database_pool()

            assert result.status == HealthStatus.DEGRADED
            assert "Connection pool usage critical" in result.message
            assert result.details["usage_percent"] == 100.0

    @pytest.mark.asyncio
    async def test_database_pool_with_overflow(self):
        """Test health check with database pool overflow."""
        with patch("app.health.engine") as mock_engine:
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedout.return_value = 8
            mock_pool.overflow.return_value = 5  # Overflow active

            mock_engine.pool = mock_pool

            result = await check_database_pool()

            # 8 / (10 + 5) = 53.3%
            assert result.status == HealthStatus.HEALTHY
            assert result.details["overflow"] == 5
            assert result.details["usage_percent"] == pytest.approx(53.3, rel=0.1)


class TestRedisMemoryHealthCheck:
    """Test cases for Redis memory health checks."""

    @pytest.mark.asyncio
    async def test_healthy_redis_memory(self):
        """Test health check with healthy Redis memory."""
        with patch("app.health.get_event_bus") as mock_get_bus:
            mock_bus = MagicMock()
            mock_redis = AsyncMock()
            mock_redis.info.return_value = {
                "used_memory": 50 * 1024 * 1024,  # 50 MB
                "maxmemory": 1024 * 1024 * 1024,  # 1 GB
            }
            mock_bus.redis_client = mock_redis
            mock_get_bus.return_value = mock_bus

            result = await check_redis_memory()

            assert result.status == HealthStatus.HEALTHY
            assert "Redis memory healthy" in result.message
            assert result.details["used_memory_mb"] == pytest.approx(50.0, rel=0.1)
            assert result.details["memory_percent"] == pytest.approx(4.9, rel=0.1)

    @pytest.mark.asyncio
    async def test_high_redis_memory(self):
        """Test health check with high Redis memory usage."""
        with patch("app.health.get_event_bus") as mock_get_bus:
            mock_bus = MagicMock()
            mock_redis = AsyncMock()
            mock_redis.info.return_value = {
                "used_memory": 850 * 1024 * 1024,  # 850 MB
                "maxmemory": 1024 * 1024 * 1024,  # 1 GB (83%)
            }
            mock_bus.redis_client = mock_redis
            mock_get_bus.return_value = mock_bus

            result = await check_redis_memory()

            assert result.status == HealthStatus.DEGRADED
            assert "Redis memory usage high" in result.message

    @pytest.mark.asyncio
    async def test_redis_client_not_initialized(self):
        """Test health check when Redis client is not initialized."""
        with patch("app.health.get_event_bus") as mock_get_bus:
            mock_bus = MagicMock()
            mock_bus.redis_client = None
            mock_get_bus.return_value = mock_bus

            result = await check_redis_memory()

            assert result.status == HealthStatus.DEGRADED
            assert "Redis client not initialized" in result.message

    @pytest.mark.asyncio
    async def test_redis_no_max_memory(self):
        """Test health check when Redis has no max memory limit."""
        with patch("app.health.get_event_bus") as mock_get_bus:
            mock_bus = MagicMock()
            mock_redis = AsyncMock()
            mock_redis.info.return_value = {
                "used_memory": 100 * 1024 * 1024,  # 100 MB
                "maxmemory": 0,  # No limit
            }
            mock_bus.redis_client = mock_redis
            mock_get_bus.return_value = mock_bus

            result = await check_redis_memory()

            assert result.status == HealthStatus.HEALTHY
            assert "no max limit" in result.message
            assert result.details["memory_percent"] is None


class TestDeepHealthCheck:
    """Test cases for deep health check orchestration."""

    @pytest.mark.asyncio
    async def test_deep_health_check_all_healthy(self):
        """Test deep health check when all components are healthy."""
        with patch("app.health.check_database") as mock_db, patch(
            "app.health.check_database_pool"
        ) as mock_pool, patch("app.health.check_redis") as mock_redis, patch(
            "app.health.check_redis_memory"
        ) as mock_redis_mem, patch(
            "app.health.check_circuit_breakers"
        ) as mock_breakers, patch(
            "app.health.check_system_resources"
        ) as mock_system:

            # All components healthy
            mock_db.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="DB OK", latency_ms=10.0
            )
            mock_pool.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Pool OK", latency_ms=5.0
            )
            mock_redis.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Redis OK", latency_ms=8.0
            )
            mock_redis_mem.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Redis Mem OK", latency_ms=7.0
            )
            mock_breakers.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Breakers OK", latency_ms=3.0
            )
            mock_system.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="System OK", latency_ms=12.0
            )

            result = await check_dependencies_deep()

            assert result.status == HealthStatus.HEALTHY
            assert len(result.components) == 6
            assert result.version == "2.0.0"

    @pytest.mark.asyncio
    async def test_deep_health_check_database_unhealthy(self):
        """Test deep health check when database is unhealthy."""
        with patch("app.health.check_database") as mock_db, patch(
            "app.health.check_database_pool"
        ) as mock_pool, patch("app.health.check_redis") as mock_redis, patch(
            "app.health.check_redis_memory"
        ) as mock_redis_mem, patch(
            "app.health.check_circuit_breakers"
        ) as mock_breakers, patch(
            "app.health.check_system_resources"
        ) as mock_system:

            # Database unhealthy
            mock_db.return_value = ComponentHealth(
                status=HealthStatus.UNHEALTHY, message="DB down", latency_ms=1000.0
            )
            mock_pool.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Pool OK", latency_ms=5.0
            )
            mock_redis.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Redis OK", latency_ms=8.0
            )
            mock_redis_mem.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Redis Mem OK", latency_ms=7.0
            )
            mock_breakers.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Breakers OK", latency_ms=3.0
            )
            mock_system.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="System OK", latency_ms=12.0
            )

            result = await check_dependencies_deep()

            # Overall status should be unhealthy if database is unhealthy
            assert result.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_deep_health_check_component_degraded(self):
        """Test deep health check when a component is degraded."""
        with patch("app.health.check_database") as mock_db, patch(
            "app.health.check_database_pool"
        ) as mock_pool, patch("app.health.check_redis") as mock_redis, patch(
            "app.health.check_redis_memory"
        ) as mock_redis_mem, patch(
            "app.health.check_circuit_breakers"
        ) as mock_breakers, patch(
            "app.health.check_system_resources"
        ) as mock_system:

            # System degraded
            mock_db.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="DB OK", latency_ms=10.0
            )
            mock_pool.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Pool OK", latency_ms=5.0
            )
            mock_redis.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Redis OK", latency_ms=8.0
            )
            mock_redis_mem.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="Redis Mem OK", latency_ms=7.0
            )
            mock_breakers.return_value = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message="1 breaker open",
                latency_ms=3.0,
            )
            mock_system.return_value = ComponentHealth(
                status=HealthStatus.HEALTHY, message="System OK", latency_ms=12.0
            )

            result = await check_dependencies_deep()

            # Overall status should be degraded
            assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_deep_health_check_timeout(self):
        """Test deep health check timeout handling."""
        import asyncio

        async def slow_check():
            await asyncio.sleep(10)  # Longer than 5 second timeout
            return ComponentHealth(
                status=HealthStatus.HEALTHY, message="Slow", latency_ms=10000.0
            )

        with patch("app.health.check_database", side_effect=slow_check):
            result = await check_dependencies_deep()

            # Should timeout and return unhealthy status
            assert result.status == HealthStatus.UNHEALTHY
            assert "timeout" in result.components
            assert result.components["timeout"].latency_ms == 5000.0


class TestDependencyDetails:
    """Test cases for dependency details endpoint."""

    @pytest.mark.asyncio
    async def test_get_dependency_details_success(self):
        """Test successful retrieval of dependency details."""
        with patch("app.health.check_dependencies_deep") as mock_deep:
            mock_deep.return_value = HealthCheckResponse(
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                version="2.0.0",
                service="test-service",
                components={
                    "database": ComponentHealth(
                        status=HealthStatus.HEALTHY,
                        message="DB OK",
                        latency_ms=10.0,
                        details={"pool_size": 10},
                    )
                },
            )

            result = await get_dependency_details()

            assert result["status"] == HealthStatus.HEALTHY
            assert "dependencies" in result
            assert "database" in result["dependencies"]
            assert result["dependencies"]["database"]["status"] == HealthStatus.HEALTHY
            assert result["dependencies"]["database"]["latency_ms"] == 10.0

    @pytest.mark.asyncio
    async def test_get_dependency_details_exception(self):
        """Test handling of exceptions in dependency details."""
        with patch(
            "app.health.check_dependencies_deep",
            side_effect=Exception("Health check error"),
        ):
            result = await get_dependency_details()

            assert result["status"] == "unhealthy"
            assert "error" in result
