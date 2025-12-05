# Monitoring & Observability Guide

This document provides comprehensive information about the monitoring and observability infrastructure for the AI Meal Planner application.

## Architecture Overview

The monitoring stack consists of:

1. **Prometheus** - Metrics collection and alerting
2. **Grafana** - Metrics visualization and dashboards
3. **Loki** - Log aggregation
4. **Promtail** - Log shipping from Docker containers
5. **Exporters** - PostgreSQL, Redis, and Node metrics exporters

## Components

### Prometheus (Port 9090)

**Purpose**: Collects and stores time-series metrics from the application and infrastructure.

**Configuration**: `/infrastructure/docker/prometheus/prometheus.yml`

**Scraped Services**:
- `recipe-api` (Port 8000) - FastAPI application metrics
- `postgres-exporter` (Port 9187) - PostgreSQL database metrics
- `redis-exporter` (Port 9121) - Redis cache metrics
- `node-exporter` (Port 9100) - System/host metrics

**Alerting**: `/infrastructure/docker/prometheus/alerts.yml`

**Key Alerts**:
- High error rate (>5% for 5 minutes)
- High latency (p95 >1s for 5 minutes)
- Database down (for 1 minute)
- Redis down (for 1 minute)
- High memory usage (>80% for 5 minutes)
- High CPU usage (>80% for 5 minutes)
- Low disk space (<10%)
- High failed authentication rate (>10%)
- Rate limit exceeded (>5%)
- High workflow failure rate (>10%)
- Slow database queries (avg >1s)
- Database connection pool exhaustion (>90%)
- API service unhealthy
- Agent system failures

**Access**: http://localhost:9090

### Grafana (Port 3000)

**Purpose**: Visualizes metrics and logs through interactive dashboards.

**Default Credentials**:
- Username: `admin`
- Password: `admin` (change in production via `GRAFANA_ADMIN_PASSWORD` env var)

**Dashboards**:

1. **API Overview** (`/var/lib/grafana/dashboards/api-overview.json`)
   - Request rate (requests/sec)
   - Error rate (%)
   - Request duration (p50, p95, p99)
   - Active requests
   - Status code distribution

2. **Database Monitoring** (`/var/lib/grafana/dashboards/database.json`)
   - Query duration (avg, p95, p99)
   - Connection pool usage
   - Slow queries (>1s)
   - Transaction rate (commits/rollbacks)
   - Active/waiting connections
   - Database status

3. **Business Metrics** (`/var/lib/grafana/dashboards/business-metrics.json`)
   - User registrations
   - Total recipes
   - Meal plans created
   - Grocery carts created
   - Recipe harvest statistics
   - Cart conversion rate
   - User activity
   - Workflow executions
   - AI agent activity

**Datasources**:
- Prometheus (default) - Metrics
- Loki - Logs

**Access**: http://localhost:3000

### Loki (Port 3100)

**Purpose**: Aggregates and indexes logs from all Docker containers.

**Configuration**: `/infrastructure/docker/loki/loki-config.yml`

**Features**:
- 30-day log retention
- Automatic compaction every 10 minutes
- Supports JSON log parsing
- Labels for service, environment, container

**Storage**: `/loki` volume (persistent)

**Access**: http://localhost:3100 (API endpoint)

### Promtail

**Purpose**: Scrapes logs from Docker containers and ships them to Loki.

**Configuration**: `/infrastructure/docker/promtail/promtail-config.yml`

**Log Sources**:
- All Docker containers (general)
- API container (with JSON parsing)
- PostgreSQL container (with PostgreSQL log parsing)
- Redis container (with Redis log parsing)

**Pipeline Stages**:
1. JSON parsing for structured logs
2. Timestamp extraction
3. Label extraction (level, logger, request_id, etc.)
4. Output formatting

**Labels Added**:
- `container` - Container name
- `container_id` - Container ID
- `service` - Service name
- `environment` - Environment (development/production)
- `level` - Log level (info, error, warning, debug)
- `logger` - Logger name
- `request_id` - Request ID (for tracing)

## Quick Start

### Starting the Stack

```bash
cd infrastructure
docker-compose up -d
```

### Accessing Services

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Loki API: http://localhost:3100

### Viewing Dashboards

1. Open Grafana at http://localhost:3000
2. Login with admin/admin
3. Navigate to Dashboards > Browse
4. Select one of the pre-configured dashboards:
   - API Overview
   - Database Monitoring
   - Business Metrics

### Querying Logs

**Via Grafana**:
1. Go to Explore (compass icon in sidebar)
2. Select "Loki" datasource
3. Use LogQL queries:
   ```logql
   # View all API logs
   {service="api"}

   # View error logs only
   {service="api"} |= "ERROR"

   # View logs for specific request
   {service="api"} | json | request_id="abc123"

   # View slow queries
   {service="postgres"} |~ "duration: [0-9]{4,}ms"
   ```

**Via Loki API**:
```bash
# Query logs (last 1 hour)
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={service="api"}' \
  --data-urlencode 'limit=100'
```

### Checking Alerts

**Via Prometheus UI**:
1. Go to http://localhost:9090/alerts
2. View active alerts and their status

**Via Grafana**:
1. Go to Alerting > Alert Rules
2. View configured alerts from Prometheus

## Configuration Details

### Prometheus Scrape Intervals

- Global: 15s
- API metrics: 10s
- Exporters: 15s
- Alert evaluation: 15s

### Log Retention

- Loki: 30 days (720 hours)
- Docker logs: 3 files x 10MB per container

### Metric Retention

- Prometheus: Default (15 days)
- To change: Add `--storage.tsdb.retention.time=30d` to Prometheus command

## Troubleshooting

### Prometheus Not Scraping Targets

1. Check target status: http://localhost:9090/targets
2. Verify service is running: `docker ps`
3. Check service logs: `docker logs recipe-prometheus`
4. Verify network connectivity: `docker exec recipe-prometheus ping api`

### Grafana Dashboards Not Loading

1. Check Grafana logs: `docker logs recipe-grafana`
2. Verify provisioning directory: `docker exec recipe-grafana ls /etc/grafana/provisioning/dashboards`
3. Verify datasource connectivity: Configuration > Data Sources

### Loki Not Receiving Logs

1. Check Loki logs: `docker logs recipe-loki`
2. Check Promtail logs: `docker logs recipe-promtail`
3. Verify Docker socket access: `docker exec recipe-promtail ls -l /var/run/docker.sock`
4. Test Loki API: `curl http://localhost:3100/ready`

### No Metrics Showing Up

1. Verify application is exposing metrics: `curl http://localhost:8000/metrics`
2. Check Prometheus config: `docker exec recipe-prometheus cat /etc/prometheus/prometheus.yml`
3. Reload Prometheus config: `curl -X POST http://localhost:9090/-/reload`

## Extending the Stack

### Adding New Dashboards

1. Create dashboard JSON in `/infrastructure/docker/grafana/dashboards/`
2. Restart Grafana: `docker-compose restart grafana`
3. Dashboard will auto-load via provisioning

### Adding New Alerts

1. Edit `/infrastructure/docker/prometheus/alerts.yml`
2. Add new alert rule under appropriate group
3. Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`
4. Verify alert: http://localhost:9090/alerts

### Adding New Exporters

1. Add exporter service to `docker-compose.yml`
2. Add scrape config to `prometheus.yml`
3. Restart Prometheus: `docker-compose restart prometheus`

## Production Considerations

### Security

1. **Change default passwords**:
   ```bash
   export GRAFANA_ADMIN_PASSWORD="strong-password"
   ```

2. **Enable HTTPS**: Configure reverse proxy (nginx/traefik) with SSL

3. **Restrict access**: Use firewall rules or VPN for monitoring ports

4. **Enable authentication**: Configure Prometheus/Grafana with proper auth

### High Availability

1. **Prometheus**: Use federation or Thanos for long-term storage
2. **Grafana**: Use external database (PostgreSQL/MySQL)
3. **Loki**: Configure S3/GCS for storage backend

### Performance

1. **Prometheus**: Increase retention only if needed (uses disk space)
2. **Loki**: Use object storage for large deployments
3. **Grafana**: Enable caching and use query optimization

### Alerting

1. **Add Alertmanager**: For routing alerts to Slack, PagerDuty, email
2. **Configure notification channels**: In Grafana settings
3. **Set up on-call rotation**: Use PagerDuty or similar

## Useful Queries

### PromQL (Prometheus)

```promql
# Request rate by endpoint
rate(http_requests_total[5m])

# Error rate percentage
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Database connection pool usage
db_connection_pool_active / db_connection_pool_size * 100

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### LogQL (Loki)

```logql
# All API errors
{service="api"} |= "ERROR"

# Requests slower than 1 second
{service="api"} | json | duration_ms > 1000

# Failed authentication attempts
{service="api"} | json | status_code="401"

# Database errors
{service="postgres"} |= "ERROR"

# Rate of errors per minute
rate({service="api"} |= "ERROR" [1m])
```

## Sentry Error Tracking

**Purpose**: Centralized error tracking and monitoring for production applications.

### Setup

1. **Create Sentry Account**:
   - Sign up at https://sentry.io
   - Create a new project for your application
   - Select "Python" as the platform

2. **Get DSN**:
   - Navigate to Settings > Projects > [Your Project] > Client Keys (DSN)
   - Copy the DSN URL

3. **Configure Environment**:
   ```bash
   # In .env or environment variables
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   APP_ENV=production
   LOG_LEVEL=INFO
   ```

4. **Install Dependencies**:
   ```bash
   cd backend
   pip install sentry-sdk[fastapi]
   ```

5. **Verify Integration**:
   - Check application logs for "Sentry error tracking initialized"
   - Trigger a test error
   - Verify error appears in Sentry dashboard

### Features

**Automatic Error Tracking**:
- Unhandled exceptions captured automatically
- Request context included (method, path, headers)
- User context tracking (user_id, email)
- Breadcrumbs for debugging
- Stack traces with local variables

**Sensitive Data Filtering**:
- Passwords, tokens, API keys automatically filtered
- PII protection enabled by default
- Customizable filtering in `before_send` hook

**Performance Monitoring**:
- Transaction tracking for API endpoints
- Database query performance
- Redis operation tracking
- Configurable sampling rates

**Integrations**:
- FastAPI (request/response tracking)
- SQLAlchemy (database query tracking)
- Redis (cache operation tracking)
- Logging (error log capture)

### Configuration

**Environment Variables**:
- `SENTRY_DSN` - Sentry project DSN (required)
- `APP_ENV` - Environment name (development/staging/production)
- `LOG_LEVEL` - Minimum log level to capture (INFO, WARNING, ERROR)

**Sample Rates**:
- Development: 100% (all events tracked)
- Production: 10% (10% of transactions tracked to reduce quota usage)

**Release Tracking**:
- Automatically tracks git commit SHA as release version
- Links errors to specific code versions
- Enables release-based filtering in Sentry

### Usage

**Manual Error Capture**:
```python
from app.monitoring.sentry_integration import capture_exception, capture_message

# Capture exception with context
try:
    risky_operation()
except Exception as e:
    capture_exception(e, user_id="123", operation="risky_operation")

# Capture message
capture_message("Important event occurred", level="info", user_id="123")
```

**User Context**:
```python
from app.monitoring.sentry_integration import set_user_context, clear_user_context

# Set user context for subsequent errors
set_user_context(user_id="123", email="user@example.com")

# Clear user context (e.g., on logout)
clear_user_context()
```

### Sentry Dashboard

**Access**: https://sentry.io/organizations/[org]/issues/

**Key Features**:
1. **Issues**: View and triage errors
2. **Performance**: Monitor transaction performance
3. **Releases**: Track errors by release version
4. **Alerts**: Configure error rate alerts
5. **Discover**: Query error data

### Alerts

**Recommended Alerts**:
1. **High Error Rate**: >10 errors in 5 minutes
2. **New Issue**: First occurrence of new error type
3. **Regression**: Reappearance of resolved issue
4. **Performance Degradation**: Endpoint latency >1s

**Setup**:
1. Go to Alerts > Create Alert Rule
2. Select metric (e.g., "errors")
3. Configure threshold and time window
4. Add notification channel (email, Slack, PagerDuty)

### Troubleshooting

**Sentry Not Capturing Errors**:
1. Verify `SENTRY_DSN` is set correctly
2. Check application logs for initialization message
3. Test with manual `capture_exception(Exception("test"))`
4. Verify network connectivity to sentry.io

**Too Many Events**:
1. Reduce `traces_sample_rate` in production
2. Add filters to `before_send` hook
3. Configure rate limits in Sentry project settings

**Sensitive Data Leaking**:
1. Review `before_send` filter in `sentry_integration.py`
2. Add additional sensitive field patterns
3. Enable PII scrubbing in Sentry project settings

### Best Practices

1. **Always set user context** when user is authenticated
2. **Clear user context** on logout
3. **Add custom context** to exceptions for debugging
4. **Review and triage issues** regularly
5. **Set up proper alerting** for critical errors
6. **Use releases** to track errors by version
7. **Monitor quota usage** to avoid overages

### Integration with Existing Monitoring

Sentry complements the existing monitoring stack:
- **Prometheus**: Metrics (request rate, latency)
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Sentry**: Error tracking and debugging

Use together for comprehensive observability:
1. **Prometheus**: Detect performance issues
2. **Grafana**: Visualize trends and patterns
3. **Loki**: Search logs for context
4. **Sentry**: Debug specific errors with full context

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Sentry Documentation](https://docs.sentry.io/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL Guide](https://grafana.com/docs/loki/latest/logql/)

## Support

For issues or questions:
1. Check container logs: `docker-compose logs [service]`
2. Review this documentation
3. Consult official documentation for the specific component
