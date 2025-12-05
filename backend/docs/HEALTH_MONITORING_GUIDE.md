# Health Monitoring Guide

## Overview

The Recipe & Meal Planning API provides comprehensive health monitoring endpoints to track system dependencies, resource usage, and overall application health.

## Health Check Endpoints

### 1. Liveness Probe (`/health/live`)

**Purpose:** Kubernetes/container orchestration liveness check

**Use Case:** Determines if the application process is running and responsive

**Response Time:** <10ms

**Example Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-12-05T10:30:00Z"
}
```

**When to Use:**
- Kubernetes liveness probes
- Container health checks
- Process monitoring

---

### 2. Readiness Probe (`/health/ready`)

**Purpose:** Kubernetes/container orchestration readiness check

**Use Case:** Determines if the application is ready to accept traffic

**Response Time:** <1s

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00Z",
  "version": "1.0.0",
  "service": "recipe-meal-planning-api",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful",
      "latency_ms": 12.5
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful",
      "latency_ms": 8.2
    }
  }
}
```

**When to Use:**
- Kubernetes readiness probes
- Load balancer health checks
- Traffic routing decisions

---

### 3. Standard Health Check (`/health`)

**Purpose:** Basic dependency health monitoring

**Use Case:** Quick health check for monitoring systems

**Response Time:** <1s

**Status Levels:**
- `healthy`: All critical dependencies operational
- `degraded`: Non-critical issues detected (e.g., Redis down, circuit breaker open)
- `unhealthy`: Critical dependencies failed (e.g., database down)

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00Z",
  "version": "1.0.0",
  "service": "recipe-meal-planning-api",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful",
      "latency_ms": 12.5,
      "details": {
        "engine": "postgresql",
        "pool_size": 10,
        "checked_out": 3
      }
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful",
      "latency_ms": 8.2,
      "details": {
        "host": "localhost",
        "port": 6379,
        "db": 0
      }
    }
  }
}
```

**When to Use:**
- Basic monitoring
- Uptime checks
- Status dashboards

---

### 4. Deep Health Check (`/health/deep`) ⭐ NEW

**Purpose:** Comprehensive dependency and resource monitoring

**Use Case:** Detailed health analysis with metrics

**Response Time:** <5s (with timeout)

**Components Checked:**
1. **Database Connection** - Basic connectivity
2. **Database Pool** - Connection pool metrics
3. **Redis Connection** - Basic connectivity
4. **Redis Memory** - Memory usage metrics
5. **Circuit Breakers** - All breaker states
6. **System Resources** - CPU, memory, disk

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00Z",
  "version": "2.0.0",
  "service": "recipe-meal-planning-api",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful",
      "latency_ms": 12.5,
      "details": {
        "engine": "postgresql",
        "pool_size": 10,
        "checked_out": 3
      }
    },
    "database_pool": {
      "status": "healthy",
      "message": "Connection pool healthy",
      "latency_ms": 2.1,
      "details": {
        "pool_size": 10,
        "checked_out": 3,
        "overflow": 0,
        "usage_percent": 30.0
      }
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful",
      "latency_ms": 8.2,
      "details": {
        "host": "localhost",
        "port": 6379,
        "db": 0
      }
    },
    "redis_memory": {
      "status": "healthy",
      "message": "Redis memory healthy",
      "latency_ms": 15.3,
      "details": {
        "used_memory_mb": 125.5,
        "maxmemory_mb": 1024.0,
        "memory_percent": 12.3
      }
    },
    "circuit_breaker": {
      "status": "healthy",
      "message": "All 2 circuit breaker(s) CLOSED",
      "latency_ms": 3.2,
      "details": {
        "total": 2,
        "open": 0,
        "half_open": 0,
        "closed": 2,
        "metrics": {
          "knuspr_api": {
            "state": "closed",
            "total_requests": 1500,
            "successful_requests": 1495,
            "failed_requests": 5,
            "rejected_requests": 0,
            "failure_rate": 0.003
          }
        }
      }
    },
    "system": {
      "status": "healthy",
      "message": "System resources healthy",
      "latency_ms": 105.8,
      "details": {
        "cpu_percent": 45.2,
        "memory_mb": 512.3,
        "memory_percent": 32.1,
        "disk_percent": 58.7,
        "disk_free_gb": 125.4
      }
    }
  }
}
```

**When to Use:**
- Detailed monitoring dashboards
- Performance analysis
- Capacity planning
- Troubleshooting

---

### 5. Dependency Details (`/health/dependencies`) ⭐ NEW

**Purpose:** Structured dependency information

**Use Case:** Programmatic access to dependency status

**Response Time:** <5s (with timeout)

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00Z",
  "version": "2.0.0",
  "dependencies": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful",
      "latency_ms": 12.5,
      "metrics": {
        "engine": "postgresql",
        "pool_size": 10,
        "checked_out": 3
      }
    },
    "database_pool": {
      "status": "healthy",
      "message": "Connection pool healthy",
      "latency_ms": 2.1,
      "metrics": {
        "pool_size": 10,
        "checked_out": 3,
        "overflow": 0,
        "usage_percent": 30.0
      }
    }
    // ... other dependencies
  }
}
```

**When to Use:**
- API integrations
- Automated monitoring tools
- Custom dashboards

---

## Health Status Definitions

### Status: `healthy`
- All critical dependencies operational
- Resources within normal thresholds
- No circuit breakers open
- System ready for production traffic

### Status: `degraded`
- Non-critical issues detected
- Redis unavailable (optional dependency)
- Circuit breakers open (service degradation)
- High resource usage (warnings)
- System can continue operating with reduced functionality

### Status: `unhealthy`
- Critical dependencies failed
- Database unreachable
- Health check timeout
- System should not receive traffic

---

## Resource Thresholds

### CPU Usage
- **Healthy**: <80%
- **Warning**: 80-90%
- **Critical**: >90%

### Memory Usage
- **Healthy**: <1GB
- **Warning**: 1-2GB
- **Critical**: >2GB

### Disk Space
- **Healthy**: <85% used
- **Warning**: 85-90% used
- **Critical**: >90% used

### Database Pool
- **Healthy**: <80% utilization
- **Warning**: 80-90% utilization
- **Critical**: >90% utilization

### Redis Memory
- **Healthy**: <80% of max memory
- **Warning**: 80-90% of max memory
- **Critical**: >90% of max memory

---

## Circuit Breaker States

### CLOSED (Healthy)
- Normal operation
- Requests passing through
- Failure count below threshold

### HALF_OPEN (Degraded)
- Testing recovery
- Limited requests allowed
- Monitoring success rate

### OPEN (Degraded)
- Failing fast
- Service unavailable
- Preventing cascading failures

---

## Monitoring Integration

### Prometheus Metrics

All health data is available as Prometheus metrics at `/metrics`:

```
# Circuit breaker metrics
circuit_breaker_state{name="knuspr_api"} 0  # 0=closed, 1=half_open, 2=open
circuit_breaker_requests_total{name="knuspr_api"} 1500
circuit_breaker_failures_total{name="knuspr_api"} 5

# Database pool metrics
db_pool_size 10
db_pool_checked_out 3
db_pool_overflow 0

# System metrics
system_cpu_usage_percent 45.2
system_memory_usage_mb 512.3
system_disk_usage_percent 58.7
```

### Kubernetes Configuration

```yaml
# Liveness probe
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3

# Readiness probe
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

### Grafana Dashboard

Example queries for monitoring:

```promql
# Overall health status
health_check_status{endpoint="/health"}

# Response times
histogram_quantile(0.95, health_check_duration_seconds)

# Circuit breaker open count
sum(circuit_breaker_state == 2)

# Database pool usage
(db_pool_checked_out / (db_pool_size + db_pool_overflow)) * 100

# System CPU usage
system_cpu_usage_percent
```

---

## Troubleshooting

### Database Unhealthy

**Symptoms:** Database component shows unhealthy status

**Possible Causes:**
- Database server down
- Network connectivity issues
- Connection pool exhausted
- Authentication failure

**Resolution:**
1. Check database server status
2. Verify network connectivity
3. Review connection pool configuration
4. Check credentials and permissions

### Circuit Breaker Open

**Symptoms:** Circuit breaker component shows degraded, breaker is OPEN

**Possible Causes:**
- External service down
- High failure rate
- Network issues
- Timeout issues

**Resolution:**
1. Check external service status
2. Review recent error logs
3. Wait for automatic recovery (60s default)
4. Manual reset if needed (admin endpoint)

### High Resource Usage

**Symptoms:** System component shows degraded, high CPU/memory/disk

**Possible Causes:**
- Traffic spike
- Memory leak
- Disk full
- Inefficient queries

**Resolution:**
1. Review traffic patterns
2. Check for memory leaks
3. Clean up disk space
4. Optimize database queries
5. Scale horizontally if needed

---

## Best Practices

1. **Use appropriate endpoints:**
   - Liveness: Container health
   - Readiness: Traffic routing
   - Standard: Basic monitoring
   - Deep: Detailed analysis

2. **Set appropriate timeouts:**
   - Liveness: 2s
   - Readiness: 3s
   - Standard: 5s
   - Deep: 10s

3. **Monitor trends:**
   - Track health over time
   - Alert on degraded status
   - Review circuit breaker patterns

4. **Regular testing:**
   - Test health endpoints regularly
   - Simulate failures
   - Validate alerting

5. **Dashboard visualization:**
   - Create Grafana dashboards
   - Track key metrics
   - Set up alerts
