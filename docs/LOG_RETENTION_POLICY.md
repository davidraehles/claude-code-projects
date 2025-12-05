# Log Retention Policy

## Overview

This document describes the log retention policies for the AI Meal Planner application, including configuration details, query examples, and recovery procedures.

## Retention Windows

All log and metrics data is retained for **30 days** by default to balance operational needs with storage costs.

| Component | Retention Period | Configuration Location |
|-----------|-----------------|----------------------|
| **Loki Logs** | 30 days (720h) | `/infrastructure/docker/loki/loki-config.yml` |
| **Prometheus Metrics** | 30 days | `/infrastructure/docker-compose.yml` (Prometheus command) |
| **Application Logs** | 30 days | Managed by `log_retention_policy.sh` |
| **Database Backups** | 30 days local, indefinite in S3 | Managed by `log_retention_policy.sh` |
| **Compressed Logs** | Deleted after 30 days | Compressed after 7 days, deleted after 30 |

## Configuration Details

### 1. Loki Log Retention

**File:** `/infrastructure/docker/loki/loki-config.yml`

```yaml
limits_config:
  retention_period: 720h  # 30 days

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days

compactor:
  retention_enabled: true
  retention_delete_delay: 2h
```

**How to modify:**
1. Edit `loki-config.yml`
2. Change `retention_period` value (format: hours, e.g., `720h` for 30 days, `2160h` for 90 days)
3. Restart Loki container: `docker-compose restart loki`

### 2. Prometheus Metrics Retention

**File:** `/infrastructure/docker-compose.yml`

```yaml
prometheus:
  command:
    - '--storage.tsdb.retention.time=30d'
```

**How to modify:**
1. Edit `docker-compose.yml`
2. Change `--storage.tsdb.retention.time` value (format: days, e.g., `30d`, `90d`)
3. Restart Prometheus: `docker-compose restart prometheus`

### 3. Application Log Rotation

**Managed by:** `/infrastructure/scripts/log_retention_policy.sh`

**Policy:**
- Daily rotation of application logs
- Compress logs after 7 days (`.log` → `.log.gz`)
- Delete compressed logs after 30 days
- Optional S3 archival for long-term storage

**Schedule:** Runs daily at 2 AM via cron: `0 2 * * *`

### 4. Database Backup Retention

**Policy:**
- Keep local backups for 30 days
- Archive to S3 for indefinite retention (if configured)
- Automatic cleanup of old local backups

## Querying Historical Logs

### Loki Log Queries (Grafana Explore)

Access Grafana at `http://localhost:3000` and navigate to Explore.

#### Basic Queries

**All API logs:**
```logql
{service="recipe-meal-planning-api"}
```

**Error logs only:**
```logql
{service="recipe-meal-planning-api", level="error"}
```

**Logs for specific request:**
```logql
{request_id="<uuid>"}
```

**Logs for specific user:**
```logql
{user_id="<user-id>"}
```

**Logs from specific container:**
```logql
{container="recipe-api"}
```

#### Advanced Queries

**Error rate over time:**
```logql
sum(rate({service="recipe-meal-planning-api", level="error"}[5m]))
```

**Top 10 error messages:**
```logql
topk(10, sum by (message) (count_over_time({level="error"}[1h])))
```

**Logs matching pattern:**
```logql
{service="recipe-meal-planning-api"} |= "database"
```

**Logs NOT matching pattern:**
```logql
{service="recipe-meal-planning-api"} != "healthcheck"
```

**Filter by time range:**
Use the time picker in Grafana to select:
- Last 5 minutes
- Last 1 hour
- Last 24 hours
- Last 7 days
- Custom range

#### Structured Log Queries

**Parse JSON and filter:**
```logql
{service="recipe-meal-planning-api"} | json | status_code >= 500
```

**Query by HTTP method:**
```logql
{service="recipe-meal-planning-api", method="POST"}
```

**Query by status code:**
```logql
{service="recipe-meal-planning-api", status_code="500"}
```

**Slow requests (duration > 1s):**
```logql
{service="recipe-meal-planning-api"} | json | duration_ms > 1000
```

### Prometheus Metrics Queries

Access Prometheus at `http://localhost:9090`.

**Error rate:**
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

**Request latency (p95):**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Database query duration:**
```promql
rate(db_query_duration_seconds_sum[5m]) / rate(db_query_duration_seconds_count[5m])
```

## S3 Backup and Archival

### Configuration

Set these environment variables to enable S3 archival:

```bash
S3_BUCKET=my-recipe-app-logs
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_DEFAULT_REGION=us-east-1
```

### S3 Directory Structure

```
s3://my-recipe-app-logs/
├── logs/
│   ├── 2025-12-05/
│   │   ├── api.log.gz
│   │   └── worker.log.gz
│   └── 2025-12-06/
└── backups/
    ├── 2025-12-05/
    │   └── recipe_app_20251205_020000.sql.gz
    └── 2025-12-06/
```

### Nightly Upload Process

The `log_retention_policy.sh` script:
1. Compresses logs older than 7 days
2. Uploads compressed logs to S3 (organized by date)
3. Uploads database backups to S3
4. Deletes local archives after successful upload
5. Validates retention policies

### Manual S3 Upload

```bash
# Upload specific log file
aws s3 cp /var/log/recipe-app/api.log.gz \
    s3://my-recipe-app-logs/logs/$(date +%Y-%m-%d)/

# Upload all compressed logs
aws s3 sync /var/log/recipe-app \
    s3://my-recipe-app-logs/logs/$(date +%Y-%m-%d)/ \
    --exclude "*" --include "*.log.gz"

# Upload database backup
aws s3 cp /backups/recipe_app_backup.sql.gz \
    s3://my-recipe-app-logs/backups/$(date +%Y-%m-%d)/
```

## Recovery Procedures

### Recovering from S3

**Restore logs from S3:**
```bash
# List available log archives
aws s3 ls s3://my-recipe-app-logs/logs/ --recursive

# Download specific date's logs
aws s3 sync s3://my-recipe-app-logs/logs/2025-12-05/ \
    /var/log/recipe-app/restored/

# Decompress logs
gunzip /var/log/recipe-app/restored/*.gz
```

**Restore database backup from S3:**
```bash
# List available backups
aws s3 ls s3://my-recipe-app-logs/backups/ --recursive

# Download specific backup
aws s3 cp s3://my-recipe-app-logs/backups/2025-12-05/recipe_app_20251205_020000.sql.gz \
    /tmp/

# Restore database (see restore_database.sh)
/infrastructure/scripts/restore_database.sh /tmp/recipe_app_20251205_020000.sql.gz
```

### Querying Archived Logs

If you need to query logs older than 30 days:

1. **Download from S3:**
   ```bash
   aws s3 cp s3://my-recipe-app-logs/logs/2025-11-01/api.log.gz /tmp/
   gunzip /tmp/api.log.gz
   ```

2. **Query locally:**
   ```bash
   # Search for specific pattern
   grep "error" /tmp/api.log

   # Search for request ID
   grep "request_id.*abc-123" /tmp/api.log

   # Count errors
   grep -c "level.*error" /tmp/api.log
   ```

3. **Import into Loki (optional):**
   ```bash
   # Re-ingest old logs into Loki for querying
   # Note: This requires custom ingestion script
   # Contact DevOps for assistance
   ```

### Emergency Log Retention Extension

If you need to temporarily extend retention before a migration or audit:

**Extend Loki retention:**
```yaml
# Edit loki-config.yml
limits_config:
  retention_period: 2160h  # 90 days

# Restart Loki
docker-compose restart loki
```

**Extend Prometheus retention:**
```yaml
# Edit docker-compose.yml
command:
  - '--storage.tsdb.retention.time=90d'

# Restart Prometheus
docker-compose restart prometheus
```

**Pause log cleanup:**
```bash
# Disable cron job temporarily
# Comment out line in crontab
crontab -e
# Add # before: 0 2 * * * /infrastructure/scripts/log_retention_policy.sh
```

## Cost Optimization

### Storage Costs

**Local storage (30 days):**
- Estimated size: ~10 GB per month (varies by traffic)
- Cost: Included in infrastructure

**S3 storage (indefinite):**
- Storage class: STANDARD_IA (Infrequent Access)
- Estimated size: ~120 GB per year
- Estimated cost: ~$1.50/month (us-east-1)

### Reducing Retention Costs

1. **Reduce local retention to 14 days:**
   - Lower Loki retention to `336h`
   - Lower Prometheus retention to `14d`
   - Update `RETENTION_DAYS=14` in `log_retention_policy.sh`

2. **Use S3 Intelligent-Tiering:**
   ```bash
   # Change storage class to INTELLIGENT_TIERING
   # Edit log_retention_policy.sh, line with --storage-class
   ```

3. **Enable S3 lifecycle policies:**
   - Transition to Glacier after 90 days
   - Delete after 365 days
   - Configure via AWS Console or CLI

4. **Filter logs before storage:**
   - Only store ERROR and WARN level logs long-term
   - Discard DEBUG and INFO logs after 7 days

## Compliance and Auditing

### GDPR Considerations

- User data in logs (user_id) is retained for 30 days
- Request IDs can be used to trace user actions
- Implement log anonymization for long-term S3 storage
- Provide user data deletion script for GDPR requests

### Audit Trail

All retention policy executions are logged to `/var/log/log_retention.log`:

```bash
# View retention policy execution history
tail -f /var/log/log_retention.log

# Check last execution
grep "completed successfully" /var/log/log_retention.log | tail -1

# View daily reports
ls -lt /tmp/log_retention_report_*.txt
```

## Troubleshooting

### Logs are being deleted too soon

**Check retention configuration:**
```bash
# Verify Loki retention
docker exec recipe-loki cat /etc/loki/local-config.yaml | grep retention_period

# Verify Prometheus retention
docker inspect recipe-prometheus | grep retention.time

# Check retention script
grep RETENTION_DAYS /infrastructure/scripts/log_retention_policy.sh
```

### Logs are not being deleted

**Check cron job:**
```bash
# Verify cron is running
docker exec recipe-db-backup crontab -l

# Check log retention script output
cat /var/log/log_retention.log
```

### S3 upload failing

**Check AWS credentials:**
```bash
# Verify credentials are set
docker exec recipe-db-backup env | grep AWS

# Test AWS CLI
docker exec recipe-db-backup aws s3 ls s3://my-recipe-app-logs/
```

**Check network connectivity:**
```bash
# Test S3 endpoint
docker exec recipe-db-backup curl -I https://s3.amazonaws.com
```

### Disk space running out

**Check current usage:**
```bash
# Check Loki volume
docker exec recipe-loki df -h /loki

# Check Prometheus volume
docker exec recipe-prometheus df -h /prometheus

# Check backup volume
docker volume inspect backup_data
```

**Emergency cleanup:**
```bash
# Manually run retention script
docker exec recipe-db-backup /infrastructure/scripts/log_retention_policy.sh

# Delete old Loki chunks (dangerous - only if emergency)
docker exec recipe-loki rm -rf /loki/chunks/fake/*

# Compact Prometheus data
docker exec recipe-prometheus promtool tsdb compact /prometheus
```

## Maintenance Procedures

### Weekly

- Review log retention reports
- Check S3 upload success rate
- Verify disk space availability

### Monthly

- Audit retention policy compliance
- Review and optimize storage costs
- Test log recovery procedures

### Quarterly

- Review and update retention periods based on compliance requirements
- Test disaster recovery procedures
- Optimize log compression and archival

## References

- [Loki Retention Documentation](https://grafana.com/docs/loki/latest/operations/storage/retention/)
- [Prometheus Storage Documentation](https://prometheus.io/docs/prometheus/latest/storage/)
- [AWS S3 Lifecycle Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)

## Contact

For questions or issues with log retention:
- Check `/var/log/log_retention.log` for script execution logs
- Review Grafana dashboards for log volume trends
- Contact DevOps team for retention policy changes
