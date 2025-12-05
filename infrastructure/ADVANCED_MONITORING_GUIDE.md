# Advanced Monitoring & Observability Guide

## Overview

This guide covers the advanced monitoring and observability features implemented in Phase 2 Workstream 5. These features provide comprehensive visibility into system performance, business metrics, and operational health.

## Table of Contents

1. [Grafana Dashboards](#grafana-dashboards)
2. [Alerting & Incident Management](#alerting--incident-management)
3. [Business Metrics](#business-metrics)
4. [Distributed Tracing](#distributed-tracing)
5. [Configuration](#configuration)
6. [Runbooks](#runbooks)

---

## Grafana Dashboards

### Dashboard 1: Business Metrics

**URL:** `http://localhost:3000/d/business-metrics-v1`

**Purpose:** Track key business KPIs and operational metrics.

**Panels:**
- Recipe harvest rate (by source: web, API, RSS, file)
- Meal plans generated (hourly, daily, weekly trends)
- Cart completion rate (created vs completed)
- User growth (new users per day, active users)
- Feature usage distribution
- Error rate (business impact)

**Use Cases:**
- Product managers: Track feature adoption
- Business analysts: Monitor conversion rates
- Executives: Review KPI summary

**Refresh Rate:** 30 seconds
**Default Time Range:** Last 6 hours

---

### Dashboard 2: API Health

**URL:** `http://localhost:3000/d/api-health-v1`

**Purpose:** Monitor API performance and health.

**Panels:**
- Request rate (req/sec, by endpoint, by status code)
- Latency percentiles (P50, P95, P99)
- Error rates (4xx, 5xx by endpoint)
- Circuit breaker state
- Rate limit violations
- Response size distribution
- Request volume by endpoint

**Use Cases:**
- On-call engineers: Diagnose performance issues
- DevOps: Monitor API health
- SREs: Track SLA compliance

**Links to Logs:** Click any panel to drill down to Loki logs

**Refresh Rate:** 30 seconds
**Default Time Range:** Last 1 hour

---

### Dashboard 3: Database Performance

**URL:** `http://localhost:3000/d/database-performance-v1`

**Purpose:** Monitor PostgreSQL database performance.

**Panels:**
- Query latency (P50, P95, P99)
- Query count by operation (SELECT, INSERT, UPDATE, DELETE)
- Slow queries (> 1 second)
- Connection pool usage (active, available)
- Transaction duration
- Database size
- Lock wait time
- Transaction commits vs rollbacks

**Use Cases:**
- DBAs: Optimize query performance
- Backend engineers: Identify slow queries
- SREs: Monitor database health

**Refresh Rate:** 30 seconds
**Default Time Range:** Last 1 hour

---

### Dashboard 4: Infrastructure

**URL:** `http://localhost:3000/d/infrastructure-v1`

**Purpose:** Monitor system resources and container health.

**Panels:**
- CPU usage (overall and by container)
- Memory usage (application, database, Redis)
- Disk usage (by volume)
- Network I/O (in/out)
- Container health and restart count
- Docker disk usage
- System load average
- Service health status

**Use Cases:**
- Platform engineers: Capacity planning
- DevOps: Resource optimization
- SREs: Infrastructure monitoring

**Refresh Rate:** 30 seconds
**Default Time Range:** Last 1 hour

---

### Dashboard 5: Application Internals

**URL:** `http://localhost:3000/d/application-internals-v1`

**Purpose:** Monitor application-specific metrics and internals.

**Panels:**
- Circuit breaker status (state, failures, success rate)
- Correlation ID tracking
- Middleware latency
- Event bus metrics (published, processed, dead letter)
- Cache hit rate
- Background task execution time
- AI agent performance

**Use Cases:**
- Backend engineers: Debug application logic
- Performance engineers: Optimize bottlenecks
- Architects: System design insights

**Refresh Rate:** 30 seconds
**Default Time Range:** Last 1 hour

---

### Dashboard 6: Alerting & Incidents

**URL:** `http://localhost:3000/d/alerting-incidents-v1`

**Purpose:** Track alerts, incidents, and system uptime.

**Panels:**
- Alerts firing now (by severity)
- Incidents in progress
- System uptime percentage
- Mean Time To Recovery (MTTR)
- Alert firing rate by severity
- Health check status
- Recent deployments
- Deployment success rate

**Use Cases:**
- Incident commanders: Manage active incidents
- On-call engineers: Respond to alerts
- SREs: Track reliability metrics

**Links:**
- Runbook collection
- PagerDuty incidents
- Alertmanager

**Refresh Rate:** 30 seconds
**Default Time Range:** Last 6 hours

---

## Alerting & Incident Management

### Alertmanager Configuration

**Location:** `/infrastructure/docker/alertmanager/alertmanager.yml`

### Alert Routing by Severity

#### Critical Alerts (P1)
- **Channels:** PagerDuty + Slack (#incident-response) + SMS
- **Escalation:** 15 minutes to backup engineer
- **Repeat Interval:** 15 minutes
- **Examples:** Service down, database unreachable, 90%+ error rate

#### High Severity (P2)
- **Channels:** PagerDuty + Slack (#incident-response)
- **Escalation:** 15 minutes to backup
- **Repeat Interval:** 1 hour
- **Examples:** High latency, circuit breaker open, elevated error rate

#### Medium Severity (P3)
- **Channels:** Slack (#alerts) only
- **Repeat Interval:** 6 hours
- **Examples:** Moderate latency increase, low cache hit rate

#### Low Severity (P4)
- **Channels:** Slack (#alerts) hourly digest
- **Repeat Interval:** 24 hours
- **Examples:** Informational alerts, low-priority warnings

### Slack Integration

#### Channels
- **#alerts:** All alert notifications (real-time)
- **#incident-response:** Critical and high severity incidents
- **#deployments:** Deployment notifications
- **#business-metrics:** Daily KPI summary (6 AM)

#### Message Templates

Templates are defined in `/infrastructure/docker/alertmanager/slack-template.yml`.

**Features:**
- Rich formatting with severity colors
- Actionable buttons (View Runbook, View Metrics, View Logs)
- Threaded conversations for organization
- @on-call mentions for urgent items

### PagerDuty Integration

#### Escalation Policy

1. **Primary On-Call:** Immediate notification
2. **Backup Engineer:** After 15 minutes (no response)
3. **Team Lead:** After 30 minutes (no resolution)

#### Service Keys (Environment Variables)

```bash
PAGERDUTY_CRITICAL_KEY=<your-critical-service-key>
PAGERDUTY_HIGH_KEY=<your-high-service-key>
```

#### Incident Grouping

Alerts are grouped by:
- Alert name
- Service
- Severity

Deduplication prevents duplicate incidents from multiple sources.

---

## Business Metrics

### Module Location

`/backend/app/monitoring/business_metrics.py`

### Metrics Categories

#### 1. Recipe Metrics

```python
from app.monitoring.business_metrics import track_recipe_harvest

@track_recipe_harvest('web')
async def harvest_from_web(url: str):
    # Automatically tracks harvest count and duration
    ...
```

**Metrics:**
- `recipes_harvested_total` (by source)
- `recipes_with_errors_total` (by source, error type)
- `recipe_harvest_duration_seconds` (histogram)
- `unique_recipes_count` (gauge)

#### 2. Meal Plan Metrics

```python
from app.monitoring.business_metrics import track_meal_plan_generation

@track_meal_plan_generation('ai_suggested')
async def generate_ai_meal_plan(user_id: int):
    # Tracks generation count and duration
    ...
```

**Metrics:**
- `meal_plans_generated_total` (by generation type)
- `meal_plans_completed_total`
- `meal_plan_generation_duration_seconds` (histogram)
- `user_satisfaction_score` (gauge)

#### 3. Cart Metrics

```python
from app.monitoring.business_metrics import (
    track_cart_creation,
    track_cart_completion,
    track_items_aggregated
)

track_cart_creation()
track_cart_completion()
track_items_aggregated(count=15)
```

**Metrics:**
- `carts_created_total`
- `carts_completed_total`
- `items_aggregated_total`
- `knuspr_integration_success_rate` (gauge)

#### 4. User Metrics

```python
from app.monitoring.business_metrics import (
    track_new_user,
    track_feature_usage
)

track_new_user()
track_feature_usage('recipe_search')
```

**Metrics:**
- `active_users_total` (daily, weekly, monthly)
- `new_users_total`
- `user_retention_rate` (30d, 60d, 90d)
- `feature_usage_total` (by feature)

#### 5. Error Metrics

```python
from app.monitoring.business_metrics import (
    track_user_facing_error,
    track_error_by_type
)

track_user_facing_error('/api/v1/recipes', 500)
track_error_by_type('validation')
```

**Metrics:**
- `error_rate_percent` (gauge)
- `error_by_type_total` (by error type)
- `user_facing_errors_total` (by endpoint, error code)

#### 6. Integration Metrics

```python
from app.monitoring.business_metrics import (
    track_knuspr_api_call,
    track_external_api_call,
    track_circuit_breaker_state_change
)

track_knuspr_api_call('success', 'add_to_cart', duration=0.5)
track_external_api_call('knuspr', 'success')
track_circuit_breaker_state_change('knuspr', 'closed', 'open')
```

**Metrics:**
- `knuspr_api_calls_total` (by status)
- `knuspr_api_latency_seconds` (summary)
- `external_api_calls_total` (by service, status)
- `circuit_breaker_state_changes_total`

### Periodic Updates

Business metrics are automatically updated every 5 minutes via background task:

```python
from app.monitoring.business_metrics import update_all_business_metrics

# Called from background scheduler
await update_all_business_metrics(db)
```

---

## Distributed Tracing

### Overview

Distributed tracing is implemented using OpenTelemetry and Jaeger.

**Jaeger UI:** `http://localhost:16686`

### Module Location

`/backend/app/monitoring/tracing.py`

### Configuration

Environment variables:

```bash
# Enable/disable tracing
TRACING_ENABLED=true

# Jaeger connection
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831
JAEGER_COLLECTOR_ENDPOINT=http://jaeger:14268/api/traces

# Sampling
TRACING_SAMPLING_RATE=0.1        # 10% base sampling
TRACING_SAMPLE_ERRORS=true       # Always sample errors
TRACING_SAMPLE_SLOW=true         # Always sample slow requests
TRACING_SLOW_THRESHOLD=1.0       # Threshold in seconds

# Features
TRACE_DB_QUERIES=true
TRACE_REDIS=true
TRACE_HTTP=true

# Development
TRACING_CONSOLE=false            # Console exporter for debugging
```

### Usage

#### 1. Trace Functions

```python
from app.monitoring.tracing import trace_function

@trace_function("process_recipe")
async def process_recipe(recipe_id: int):
    # Automatically traced
    ...
```

#### 2. Trace Database Queries

```python
from app.monitoring.tracing import trace_database_query

@trace_database_query("get_recipe_by_id")
async def get_recipe(db: Session, recipe_id: int):
    # Query automatically traced
    ...
```

#### 3. Trace External API Calls

```python
from app.monitoring.tracing import trace_external_api_call

@trace_external_api_call("knuspr", "add_to_cart")
async def add_item_to_knuspr(item_id: str):
    # API call automatically traced
    ...
```

#### 4. Trace Background Tasks

```python
from app.monitoring.tracing import trace_background_task

@trace_background_task("send_notification_email")
async def send_email(user_id: int, message: str):
    # Task automatically traced
    ...
```

#### 5. Manual Tracing with Context Manager

```python
from app.monitoring.tracing import TraceContext

async def complex_operation():
    async with TraceContext("processing_phase_1") as span:
        span.set_attribute("recipe.id", recipe_id)
        # ... processing ...

    async with TraceContext("processing_phase_2") as span:
        span.set_attribute("step", "validation")
        # ... validation ...
```

#### 6. Add Attributes to Current Span

```python
from app.monitoring.tracing import add_span_attribute, add_span_event

add_span_attribute("user.id", user_id)
add_span_event("cache_miss", {"key": cache_key})
```

#### 7. Link with Correlation IDs

```python
from app.monitoring.tracing import add_trace_correlation_id

# From middleware (Phase 2 WS1)
add_trace_correlation_id(request_id)
```

### Sampling Strategy

**Default:** 10% of successful requests
**Always Sampled:**
- All errors (5xx responses)
- All slow requests (> 1 second)

**Custom sampling** per endpoint in `/infrastructure/docker/jaeger/sampling-strategies.json`

### Trace Retention

- **Development (Memory):** 100,000 traces (~72 hours)
- **Production (Elasticsearch):** 30 days (recommended)

### Performance Impact

Target overhead: < 5% latency addition
Monitored via `PerformanceMonitor` class

---

## Configuration

### Environment Variables

Create `.env` file in `/infrastructure/`:

```bash
# PagerDuty
PAGERDUTY_CRITICAL_KEY=your-critical-integration-key
PAGERDUTY_HIGH_KEY=your-high-integration-key

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_WEBHOOK_INCIDENT=https://hooks.slack.com/services/YOUR/INCIDENT/URL
SLACK_WEBHOOK_ALERTS=https://hooks.slack.com/services/YOUR/ALERTS/URL
SLACK_WEBHOOK_BUSINESS=https://hooks.slack.com/services/YOUR/BUSINESS/URL
SLACK_WEBHOOK_DEPLOYMENTS=https://hooks.slack.com/services/YOUR/DEPLOY/URL

# Jaeger
JAEGER_MEMORY_MAX_TRACES=100000

# Tracing
TRACING_ENABLED=true
TRACING_SAMPLING_RATE=0.1
TRACING_SAMPLE_ERRORS=true
TRACING_SAMPLE_SLOW=true
TRACING_SLOW_THRESHOLD=1.0
```

### Starting Services

```bash
cd infrastructure
docker-compose up -d
```

### Service URLs

- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093
- **Jaeger UI:** http://localhost:16686
- **Loki:** http://localhost:3100

---

## Runbooks

### High Error Rate

**Alert:** `HighErrorRate`
**Severity:** Critical

**Steps:**
1. Check API Health dashboard for affected endpoints
2. Review recent deployments (last 1 hour)
3. Check Loki logs for error patterns
4. Review Jaeger traces for failed requests
5. If deployment-related, consider rollback
6. Escalate to backend team if not resolved in 15 minutes

### Database Slow Queries

**Alert:** `DatabaseSlowQueries`
**Severity:** High

**Steps:**
1. Open Database Performance dashboard
2. Identify slow queries (> 1 second)
3. Check connection pool usage
4. Review query execution plans
5. Check for missing indexes
6. Consider query optimization or caching

### Circuit Breaker Open

**Alert:** `CircuitBreakerOpen`
**Severity:** High

**Steps:**
1. Check Application Internals dashboard
2. Identify which service (Knuspr, etc.)
3. Review external API latency
4. Check for rate limiting
5. Verify external service status
6. Wait for automatic recovery or manual intervention

### Low Cart Completion Rate

**Alert:** `LowCartCompletionRate`
**Severity:** Medium

**Steps:**
1. Check Business Metrics dashboard
2. Review user flow in Jaeger traces
3. Check for errors in cart creation
4. Verify Knuspr integration health
5. Review user feedback/support tickets
6. Escalate to product team if persistent

---

## Testing Alerts

### Fire Test Alert

```bash
# Send test alert to Prometheus
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Or use Alertmanager API
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "high",
      "service": "test"
    },
    "annotations": {
      "summary": "This is a test alert",
      "description": "Testing alert routing and notifications"
    }
  }]'
```

### Verify Alert Routing

1. Check Slack channels for notification
2. Check PagerDuty for incident creation
3. Verify alert appears in Alerting dashboard
4. Confirm escalation policy (wait 15 min)

---

## Troubleshooting

### Grafana Shows No Data

1. Check Prometheus is running: `docker ps | grep prometheus`
2. Verify Prometheus targets: http://localhost:9090/targets
3. Check datasource config in Grafana
4. Verify metrics are being exported: http://localhost:8000/metrics

### Alerts Not Firing

1. Check Alertmanager is running
2. Verify Prometheus alertmanager config
3. Check alert rules: http://localhost:9090/alerts
4. Review Alertmanager logs: `docker logs recipe-alertmanager`

### Jaeger Shows No Traces

1. Check Jaeger is running: `docker ps | grep jaeger`
2. Verify tracing is enabled: `TRACING_ENABLED=true`
3. Check application logs for tracing errors
4. Verify sampling rate (may be low)
5. Trigger operations to generate traces

### High Tracing Overhead

1. Reduce sampling rate: `TRACING_SAMPLING_RATE=0.01`
2. Disable database tracing: `TRACE_DB_QUERIES=false`
3. Check PerformanceMonitor stats
4. Consider selective instrumentation

---

## Support

For issues or questions:
- **Documentation:** This guide
- **Runbooks:** https://github.com/your-org/runbooks
- **On-Call:** PagerDuty escalation
- **Team Slack:** #observability

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0
**Phase:** 2 Workstream 5
