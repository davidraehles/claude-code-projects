# Monitoring & Observability Deployment Checklist

## Pre-Deployment Validation ✅

- [x] All YAML files validated (no syntax errors)
- [x] Bash script validated (no syntax errors)
- [x] 11 new alert rules added to Prometheus
- [x] 6 new alert rules added to Loki
- [x] Log label extraction configured (request_id, user_id)
- [x] 30-day retention configured for all components
- [x] Log retention script created and tested
- [x] Comprehensive documentation created

## Deployment Steps

### Step 1: Backup Current Configuration
```bash
cd /home/darae/claude-code-projects/infrastructure

# Backup current configs (in case rollback is needed)
cp docker/prometheus/alerts.yml docker/prometheus/alerts.yml.backup
cp docker/loki/loki-config.yml docker/loki/loki-config.yml.backup
cp docker/promtail/promtail-config.yml docker/promtail/promtail-config.yml.backup
cp docker-compose.yml docker-compose.yml.backup
```

### Step 2: Verify File Permissions
```bash
# Ensure log retention script is executable
chmod +x scripts/log_retention_policy.sh

# Verify permissions
ls -l scripts/log_retention_policy.sh
# Should show: -rwx--x--x (executable)
```

### Step 3: Create Required Directories
```bash
# Create Loki rules directory (should already exist)
mkdir -p docker/loki/rules

# Create log directories for retention script
mkdir -p /var/log/recipe-app
mkdir -p /var/log/recipe-app/archives
```

### Step 4: Restart Services
```bash
cd /home/darae/claude-code-projects/infrastructure

# Restart Prometheus to load new alert rules
docker-compose restart prometheus

# Wait for Prometheus to start
sleep 5

# Restart Loki to load new configuration
docker-compose restart loki

# Wait for Loki to start
sleep 5

# Restart Promtail to load new label extraction
docker-compose restart promtail

# Check all services are running
docker-compose ps
```

### Step 5: Verify Services Are Running
```bash
# Check Prometheus health
curl -f http://localhost:9090/-/healthy || echo "❌ Prometheus unhealthy"

# Check Loki health
curl -f http://localhost:3100/ready || echo "❌ Loki unhealthy"

# Check all containers are up
docker-compose ps | grep -E "(prometheus|loki|promtail)"
```

### Step 6: Verify Alert Rules Loaded
```bash
# Check Prometheus alerts via API
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].name'

# Expected output should include:
# - api_alerts
# - database_alerts
# - application_alerts
# - business_metrics_alerts
# - authentication_alerts
# - integration_alerts
# - backup_alerts
# - security_alerts
# - logging_alerts

# View in browser
open http://localhost:9090/alerts
# Should see all 31 alert rules listed
```

### Step 7: Verify Loki Alert Rules Loaded
```bash
# Check Loki rules via API
curl -s http://localhost:3100/loki/api/v1/rules | jq

# Expected output should show loki_error_alerts group with 6 rules
```

### Step 8: Test Log Queries in Grafana
```bash
# Open Grafana
open http://localhost:3000

# Navigate to: Explore > Select Loki datasource

# Test queries:
# 1. All API logs: {service="recipe-meal-planning-api"}
# 2. Error logs: {service="recipe-meal-planning-api", level="error"}
# 3. Verify labels: {service="recipe-meal-planning-api"} | json | request_id != ""

# Expected: Logs should appear with request_id and user_id labels extracted
```

### Step 9: Verify Prometheus Retention
```bash
# Check Prometheus retention setting
docker inspect recipe-prometheus | grep -i retention

# Expected output: --storage.tsdb.retention.time=30d
```

### Step 10: Test Log Retention Script
```bash
# Run script manually (dry run - won't delete anything on first run)
cd /home/darae/claude-code-projects/infrastructure
./scripts/log_retention_policy.sh

# Check output log
cat /var/log/log_retention.log

# Check generated report
ls -lt /tmp/log_retention_report_*.txt | head -1
cat /tmp/log_retention_report_$(date +%Y%m%d).txt
```

### Step 11: Setup Cron Job (Optional)
```bash
# If running on host system:
crontab -e

# Add this line:
0 2 * * * /home/darae/claude-code-projects/infrastructure/scripts/log_retention_policy.sh

# If using Docker (db-backup service already has cron):
# The backup service can run this script if added to crontab
# Edit: infrastructure/docker/backup/crontab
```

### Step 12: Configure S3 Archival (Optional)
```bash
# Create .env file or add to docker-compose.yml
cat >> .env <<EOF
S3_BUCKET=my-recipe-app-logs
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_DEFAULT_REGION=us-east-1
EOF

# Test AWS CLI access
docker exec recipe-db-backup aws s3 ls s3://my-recipe-app-logs/

# If successful, S3 archival will work automatically
```

## Post-Deployment Verification

### Checklist

- [ ] Prometheus is running and healthy
- [ ] Loki is running and healthy
- [ ] Promtail is running and shipping logs
- [ ] All 31 Prometheus alert rules loaded
- [ ] All 6 Loki alert rules loaded
- [ ] Log queries work in Grafana
- [ ] Labels (request_id, user_id) are extracted
- [ ] Prometheus retention is 30 days
- [ ] Loki retention is 30 days (720h)
- [ ] Log retention script runs without errors
- [ ] Daily report is generated
- [ ] No errors in service logs

### Verification Commands

```bash
# Run all checks at once
cd /home/darae/claude-code-projects/infrastructure

echo "Checking Prometheus..."
curl -f http://localhost:9090/-/healthy && echo "✓ Prometheus healthy" || echo "✗ Prometheus unhealthy"

echo "Checking Loki..."
curl -f http://localhost:3100/ready && echo "✓ Loki ready" || echo "✗ Loki not ready"

echo "Checking alert rules..."
ALERT_COUNT=$(curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules | length' | awk '{s+=$1} END {print s}')
echo "Loaded $ALERT_COUNT Prometheus alert rules (expected: 29+)"

echo "Checking Loki rules..."
curl -s http://localhost:3100/loki/api/v1/rules | jq '.data.groups[].name'

echo "Checking retention..."
docker inspect recipe-prometheus | grep -o "retention.time=[^']*" || echo "✗ Prometheus retention not set"

echo "All checks complete!"
```

## Rollback Procedure (If Needed)

If something goes wrong, rollback to previous configuration:

```bash
cd /home/darae/claude-code-projects/infrastructure

# Restore backup files
cp docker/prometheus/alerts.yml.backup docker/prometheus/alerts.yml
cp docker/loki/loki-config.yml.backup docker/loki/loki-config.yml
cp docker/promtail/promtail-config.yml.backup docker/promtail/promtail-config.yml
cp docker-compose.yml.backup docker-compose.yml

# Remove new files
rm -f docker/loki/rules/alerts.yml
rm -f scripts/log_retention_policy.sh

# Restart services
docker-compose restart prometheus loki promtail

# Verify services are running
docker-compose ps
```

## Monitoring After Deployment

### First 24 Hours
- [ ] Check alert status every 4 hours
- [ ] Monitor disk space usage
- [ ] Watch for any alert firing patterns
- [ ] Verify log queries are fast (<1s)

### First Week
- [ ] Review daily retention reports
- [ ] Check for any false positive alerts
- [ ] Tune alert thresholds if needed
- [ ] Verify S3 uploads (if configured)

### First Month
- [ ] Review all alert rules for relevance
- [ ] Check storage growth trends
- [ ] Adjust retention if needed
- [ ] Create Grafana dashboards

## Troubleshooting

### Alerts Not Loading
```bash
# Check Prometheus logs
docker logs recipe-prometheus | grep -i alert

# Validate alerts.yml syntax
python3 -c "import yaml; yaml.safe_load(open('docker/prometheus/alerts.yml'))"

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload
```

### Logs Not Appearing in Grafana
```bash
# Check Loki logs
docker logs recipe-loki | tail -50

# Check Promtail logs
docker logs recipe-promtail | tail -50

# Test Loki query directly
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={service="recipe-meal-planning-api"}' \
  | jq
```

### Retention Script Failing
```bash
# Check script logs
cat /var/log/log_retention.log

# Run script with debug mode
bash -x ./scripts/log_retention_policy.sh

# Check permissions
ls -l scripts/log_retention_policy.sh
```

## Success Metrics

After deployment, you should see:

✅ **Prometheus Dashboard** (http://localhost:9090)
- 29+ alert rules loaded
- No alerts firing (unless there are actual issues)
- Retention set to 30 days

✅ **Grafana Explore** (http://localhost:3000/explore)
- Logs from all services visible
- Labels extracted: request_id, user_id, service, level
- Log queries return results in <1 second

✅ **Loki** (http://localhost:3100)
- 6 log-based alert rules loaded
- Retention set to 720h (30 days)
- Storage growing steadily

✅ **Log Retention**
- Script runs daily at 2 AM
- Reports generated in /tmp/
- Old logs compressed after 7 days
- Logs deleted after 30 days

## Documentation References

- **Full Summary**: `/home/darae/claude-code-projects/infrastructure/MONITORING_OBSERVABILITY_COMPLETE.md`
- **Quick Reference**: `/home/darae/claude-code-projects/infrastructure/MONITORING_QUICK_REFERENCE.md`
- **Retention Policy**: `/home/darae/claude-code-projects/docs/LOG_RETENTION_POLICY.md`
- **Alert Rules**: `/home/darae/claude-code-projects/infrastructure/docker/prometheus/alerts.yml`
- **Loki Alerts**: `/home/darae/claude-code-projects/infrastructure/docker/loki/rules/alerts.yml`

## Contact

For issues during deployment:
1. Check service logs: `docker-compose logs <service>`
2. Verify configuration syntax: `python3 -c "import yaml; yaml.safe_load(open('file.yml'))"`
3. Review documentation in `/docs/LOG_RETENTION_POLICY.md`
4. Rollback if critical issues occur

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Status**: _____________
**Notes**: _____________
