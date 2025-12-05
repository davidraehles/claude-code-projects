# Monitoring & Observability - Quick Start

## 🚀 Start Services

```bash
cd infrastructure
docker-compose up -d
```

## 📊 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |
| Jaeger UI | http://localhost:16686 | - |
| API Metrics | http://localhost:8000/metrics | - |

## 📈 Dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| Business Metrics | http://localhost:3000/d/business-metrics-v1 | KPIs, recipes, carts, users |
| API Health | http://localhost:3000/d/api-health-v1 | Latency, errors, rate limits |
| Database | http://localhost:3000/d/database-performance-v1 | Queries, connections, performance |
| Infrastructure | http://localhost:3000/d/infrastructure-v1 | CPU, memory, disk, containers |
| Application | http://localhost:3000/d/application-internals-v1 | Circuit breakers, cache, tasks |
| Alerts | http://localhost:3000/d/alerting-incidents-v1 | Active alerts, incidents, MTTR |

## 🔔 Alert Severity

| Level | Channels | Escalation |
|-------|----------|------------|
| **Critical (P1)** | PagerDuty + Slack #incident-response + SMS | Immediate → 15min backup → 30min lead |
| **High (P2)** | PagerDuty + Slack #incident-response | 15min backup → 30min lead |
| **Medium (P3)** | Slack #alerts | None |
| **Low (P4)** | Slack #alerts (hourly digest) | None |

## 🧪 Quick Test

```bash
# Fire test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "high",
      "service": "test"
    },
    "annotations": {
      "summary": "Test alert",
      "description": "Testing alert system"
    }
  }]'

# Check in Alertmanager
open http://localhost:9093

# Check in Grafana
open http://localhost:3000/d/alerting-incidents-v1
```

## 🔍 Common Commands

```bash
# Check service status
docker ps | grep -E "grafana|prometheus|alertmanager|jaeger"

# View logs
docker logs recipe-alertmanager
docker logs recipe-jaeger

# Restart services
docker-compose restart alertmanager
docker-compose restart jaeger

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check active alerts
curl http://localhost:9090/api/v1/alerts
```

## 📖 Documentation

- **Full Guide:** `/infrastructure/ADVANCED_MONITORING_GUIDE.md`
- **Runbooks:** `/docs/RUNBOOKS.md`
- **Test Guide:** `/infrastructure/ALERTING_TEST_GUIDE.md`
- **Summary:** `/infrastructure/PHASE2_WS5_IMPLEMENTATION_SUMMARY.md`

## 🆘 Emergency Contacts

- **On-Call:** PagerDuty escalation
- **Slack:** #alerts, #incident-response
- **Runbooks:** https://github.com/your-org/runbooks

## ⚙️ Configuration

Environment variables in `.env`:
```bash
PAGERDUTY_CRITICAL_KEY=your-key
PAGERDUTY_HIGH_KEY=your-key
SLACK_WEBHOOK_URL=your-webhook
SLACK_WEBHOOK_INCIDENT=your-webhook
SLACK_WEBHOOK_ALERTS=your-webhook
SLACK_WEBHOOK_BUSINESS=your-webhook
SLACK_WEBHOOK_DEPLOYMENTS=your-webhook
```

## 🔧 Troubleshooting

### No Data in Grafana
```bash
# Check Prometheus
curl http://localhost:9090/targets
curl http://localhost:8000/metrics
```

### No Alerts
```bash
# Check Alertmanager
docker logs recipe-alertmanager
curl http://localhost:9093/api/v1/alerts
```

### No Traces
```bash
# Check Jaeger
docker logs recipe-jaeger
# Trigger some requests
curl http://localhost:8000/health
```

---

**Version:** 1.0.0
**Date:** 2025-12-05
