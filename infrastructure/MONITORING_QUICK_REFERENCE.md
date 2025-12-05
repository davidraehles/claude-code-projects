# Monitoring & Observability - Quick Reference

## 🚀 Quick Start

### Restart Services
```bash
cd infrastructure
docker-compose restart prometheus loki promtail
```

### View Dashboards
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Loki**: http://localhost:3100

---

## 📊 Alert Rules (31 Total)

### New Alerts (11 rules)

| Alert Name | Severity | Threshold | Component |
|------------|----------|-----------|-----------|
| JWTTokenRefreshFailureHigh | Critical | >0.1/sec for 5m | Authentication |
| JWTTokenExpirationHigh | Warning | >0.5/sec for 5m | Authentication |
| KnusprAPIFailureHigh | Critical | >20% for 5m | Integrations |
| KnusprAPISlowResponse | Warning | P95 >3s for 5m | Integrations |
| DatabaseBackupFailed | Critical | No success in 24h | Backup |
| DatabaseBackupSlow | Warning | >30 min | Backup |
| BackupStorageLow | Warning | >80% usage | Backup |
| TLSCertificateExpiringSoon | Warning | <7 days | Security |
| TLSCertificateExpired | Critical | Expired | Security |
| HighErrorLogRate | Critical | >1 error/sec for 5m | Logging |
| ElevatedErrorLogRate | Warning | >0.5 error/sec for 10m | Logging |

### Existing Alerts (20 rules)
- API: HighErrorRate, HighLatency, RateLimitExceeded, etc.
- Database: SlowQueries, ConnectionPoolExhausted, HighErrorRate
- Infrastructure: HighMemory, HighCPU, LowDiskSpace
- Business: LowRecipeHarvestSuccess, NoUserActivity

---

## 🔍 Log Queries (Grafana)

### Basic Queries
```logql
# All API logs
{service="recipe-meal-planning-api"}

# Errors only
{service="recipe-meal-planning-api", level="error"}

# Specific request
{request_id="abc-123"}

# Specific user
{user_id="user-456"}
```

### Advanced Queries
```logql
# Error rate (last 5m)
sum(rate({service="recipe-meal-planning-api", level="error"}[5m]))

# Database errors
{service="recipe-meal-planning-api"} |= "database" |= "error"

# Slow requests (>1s)
{service="recipe-meal-planning-api"} | json | duration_ms > 1000

# Auth failures
{service="recipe-meal-planning-api"} |~ "authentication|login" |= "failed"
```

---

## 📦 Retention Policies

| Component | Retention | Config Location |
|-----------|-----------|----------------|
| Loki | 30 days | `/infrastructure/docker/loki/loki-config.yml` |
| Prometheus | 30 days | `/infrastructure/docker-compose.yml` |
| App Logs | 30 days | `/infrastructure/scripts/log_retention_policy.sh` |
| Backups | 30 days local, ∞ S3 | `/infrastructure/scripts/log_retention_policy.sh` |

### Log Lifecycle
1. **Day 0-7**: Uncompressed logs
2. **Day 7-30**: Compressed (.gz)
3. **Day 30+**: Deleted (or archived to S3)

---

## 🛠️ Common Tasks

### Check Alert Status
```bash
# View active alerts
curl http://localhost:9090/api/v1/alerts | jq

# View alert rules
open http://localhost:9090/alerts
```

### Query Logs
```bash
# Open Grafana Explore
open http://localhost:3000/explore

# Select: Loki data source
# Query: {service="recipe-meal-planning-api", level="error"}
```

### Run Log Retention
```bash
# Manual execution
./infrastructure/scripts/log_retention_policy.sh

# Check log
tail -f /var/log/log_retention.log

# View report
cat /tmp/log_retention_report_$(date +%Y%m%d).txt
```

### Check Retention Settings
```bash
# Loki
docker exec recipe-loki grep retention_period /etc/loki/local-config.yaml

# Prometheus
docker inspect recipe-prometheus | grep retention

# Disk usage
du -sh infrastructure/volumes/loki_data
du -sh infrastructure/volumes/prometheus_data
```

---

## 🚨 Troubleshooting

### Alerts Not Showing
```bash
# Check Prometheus is running
curl http://localhost:9090/-/healthy

# Restart Prometheus
docker-compose restart prometheus

# Check alerts file syntax
python3 -c "import yaml; yaml.safe_load(open('infrastructure/docker/prometheus/alerts.yml'))"
```

### Logs Not Appearing
```bash
# Check Loki is running
curl http://localhost:3100/ready

# Check Promtail is running
docker logs recipe-promtail

# Restart log stack
docker-compose restart loki promtail
```

### Storage Full
```bash
# Check disk usage
df -h

# Run retention script
./infrastructure/scripts/log_retention_policy.sh

# Clean old data manually
docker exec recipe-loki rm -rf /loki/chunks/fake/*
docker exec recipe-prometheus promtool tsdb compact /prometheus
```

---

## 📝 Configuration Files

| File | Purpose |
|------|---------|
| `/infrastructure/docker/prometheus/alerts.yml` | Prometheus alert rules (31 rules) |
| `/infrastructure/docker/prometheus/prometheus.yml` | Prometheus scrape config |
| `/infrastructure/docker/loki/loki-config.yml` | Loki retention and storage |
| `/infrastructure/docker/loki/rules/alerts.yml` | Loki log-based alerts (6 rules) |
| `/infrastructure/docker/promtail/promtail-config.yml` | Log shipping and label extraction |
| `/infrastructure/scripts/log_retention_policy.sh` | Automated log cleanup |
| `/docs/LOG_RETENTION_POLICY.md` | Full retention documentation |

---

## 🔐 S3 Archival (Optional)

### Setup
```bash
# Set environment variables
export S3_BUCKET=my-recipe-app-logs
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
export AWS_DEFAULT_REGION=us-east-1

# Add to docker-compose.yml or .env
```

### Manual Upload
```bash
# Upload logs
aws s3 sync /var/log/recipe-app \
  s3://my-recipe-app-logs/logs/$(date +%Y-%m-%d)/ \
  --exclude "*" --include "*.log.gz"

# Upload backups
aws s3 sync /backups \
  s3://my-recipe-app-logs/backups/$(date +%Y-%m-%d)/ \
  --exclude "*" --include "*.sql.gz"
```

### Restore from S3
```bash
# List backups
aws s3 ls s3://my-recipe-app-logs/backups/ --recursive

# Download backup
aws s3 cp s3://my-recipe-app-logs/backups/2025-12-05/backup.sql.gz /tmp/

# Restore
./infrastructure/scripts/restore_database.sh /tmp/backup.sql.gz
```

---

## 📈 Metrics to Monitor

### Critical
- Error rate > 5%
- P95 latency > 1s
- Database connection pool > 90%
- Backup failures
- Certificate expiration

### Warning
- Error rate > 1%
- High CPU/Memory (>80%)
- Disk space < 20%
- Slow API responses
- JWT refresh failures

### Info
- User activity trends
- Recipe harvest success
- Request volume
- Cache hit rate

---

## 🎯 Best Practices

1. **Review alerts weekly** - Tune thresholds based on actual traffic
2. **Test log queries monthly** - Ensure labels are being extracted
3. **Validate backups quarterly** - Test restore procedures
4. **Monitor storage growth** - Adjust retention if needed
5. **Document runbooks** - Add resolution steps for each alert
6. **Set up AlertManager** - Route alerts to appropriate teams
7. **Create dashboards** - Visualize key metrics in Grafana
8. **Enable S3 archival** - For compliance and long-term analysis

---

## 📞 Support

**Check status:**
```bash
docker-compose ps
curl http://localhost:9090/-/healthy
curl http://localhost:3100/ready
```

**View logs:**
```bash
docker logs recipe-prometheus
docker logs recipe-loki
docker logs recipe-promtail
```

**Restart everything:**
```bash
docker-compose restart
```

**Full documentation:**
- Alert details: `/infrastructure/docker/prometheus/alerts.yml`
- Log retention: `/docs/LOG_RETENTION_POLICY.md`
- Full summary: `/infrastructure/MONITORING_OBSERVABILITY_COMPLETE.md`

---

**Last Updated**: 2025-12-05
**Version**: 1.0
**Status**: ✅ Production Ready
