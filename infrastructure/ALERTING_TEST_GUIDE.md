# Alerting System Testing Guide

## Overview

This guide provides step-by-step instructions for testing the PagerDuty and Slack alerting integrations implemented in Phase 2 Workstream 5.

---

## Prerequisites

### 1. PagerDuty Setup

**Create Integration Keys:**

1. Log into PagerDuty
2. Navigate to **Services** > **Service Directory**
3. Create two services:
   - **AI Meal Planner - Critical (P1)**
   - **AI Meal Planner - High (P2)**
4. For each service:
   - Click **Integrations** tab
   - Add integration: **Events API V2**
   - Copy the **Integration Key**

**Set Environment Variables:**
```bash
export PAGERDUTY_CRITICAL_KEY="<critical-service-integration-key>"
export PAGERDUTY_HIGH_KEY="<high-service-integration-key>"
```

### 2. Slack Setup

**Create Webhook URLs:**

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Navigate to **Incoming Webhooks**
4. Activate incoming webhooks
5. Create webhooks for each channel:
   - #alerts
   - #incident-response
   - #business-metrics
   - #deployments

**Set Environment Variables:**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export SLACK_WEBHOOK_INCIDENT="https://hooks.slack.com/services/YOUR/INCIDENT/URL"
export SLACK_WEBHOOK_ALERTS="https://hooks.slack.com/services/YOUR/ALERTS/URL"
export SLACK_WEBHOOK_BUSINESS="https://hooks.slack.com/services/YOUR/BUSINESS/URL"
export SLACK_WEBHOOK_DEPLOYMENTS="https://hooks.slack.com/services/YOUR/DEPLOY/URL"
```

### 3. Update Environment Configuration

**Create/Update `.env` file:**
```bash
cd infrastructure
cat > .env << EOF
# PagerDuty
PAGERDUTY_CRITICAL_KEY=${PAGERDUTY_CRITICAL_KEY}
PAGERDUTY_HIGH_KEY=${PAGERDUTY_HIGH_KEY}

# Slack
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
SLACK_WEBHOOK_INCIDENT=${SLACK_WEBHOOK_INCIDENT}
SLACK_WEBHOOK_ALERTS=${SLACK_WEBHOOK_ALERTS}
SLACK_WEBHOOK_BUSINESS=${SLACK_WEBHOOK_BUSINESS}
SLACK_WEBHOOK_DEPLOYMENTS=${SLACK_WEBHOOK_DEPLOYMENTS}
EOF
```

### 4. Start Services

```bash
cd infrastructure
docker-compose up -d
```

**Verify Services are Running:**
```bash
docker ps | grep -E "prometheus|alertmanager|grafana"
```

---

## Test 1: Critical Alert (P1)

### Purpose
Test critical alert routing to PagerDuty and Slack #incident-response.

### Steps

1. **Fire Test Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "TestCriticalAlert",
         "severity": "critical",
         "service": "recipe-api",
         "endpoint": "/api/v1/recipes"
       },
       "annotations": {
         "summary": "Critical Test Alert",
         "description": "This is a test of the critical alert routing system",
         "impact": "Service degradation or outage",
         "runbook_url": "https://github.com/your-org/runbooks#high-error-rate"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Expected Results:**

   **PagerDuty (within 30 seconds):**
   - ✅ Incident created with severity "critical"
   - ✅ Notification sent to on-call engineer
   - ✅ Incident details include service and description
   - ✅ Links to Prometheus alert

   **Slack #incident-response (within 30 seconds):**
   - ✅ Message posted with red color
   - ✅ Title: "CRITICAL ALERT - TestCriticalAlert"
   - ✅ Rotating light emoji (🚨)
   - ✅ @on-call mentioned
   - ✅ Buttons: View Runbook, View Metrics, View Logs
   - ✅ Service and endpoint information

3. **Verify in Alertmanager:**
   - Open: http://localhost:9093
   - Check **Alerts** tab
   - Confirm alert is visible

4. **Verify in Grafana:**
   - Open: http://localhost:3000/d/alerting-incidents-v1
   - Confirm alert appears in "Active Alerts" table

5. **Resolve Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "TestCriticalAlert",
         "severity": "critical",
         "service": "recipe-api",
         "endpoint": "/api/v1/recipes"
       },
       "annotations": {
         "summary": "Critical Test Alert - RESOLVED",
         "description": "This alert has been resolved"
       },
       "endsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

6. **Expected Resolution Results:**
   - ✅ PagerDuty incident auto-resolves
   - ✅ Slack message updated with "RESOLVED" status
   - ✅ Green checkmark emoji
   - ✅ Duration shown

---

## Test 2: High Severity Alert (P2)

### Purpose
Test high severity alert routing to PagerDuty and Slack #incident-response.

### Steps

1. **Fire Test Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "TestHighSeverityAlert",
         "severity": "high",
         "service": "recipe-api"
       },
       "annotations": {
         "summary": "High Severity Test Alert",
         "description": "Database connection pool near capacity"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Expected Results:**

   **PagerDuty:**
   - ✅ Incident created with severity "error"
   - ✅ Escalation after 15 minutes (if no ack)

   **Slack #incident-response:**
   - ✅ Message posted with warning color (orange)
   - ✅ Title: "HIGH SEVERITY - TestHighSeverityAlert"
   - ✅ Warning emoji (⚠️)

3. **Test Escalation:**
   - Wait 15 minutes without acknowledging
   - ✅ Confirm backup engineer receives notification
   - Or acknowledge immediately to skip escalation

---

## Test 3: Medium Severity Alert (P3)

### Purpose
Test medium severity alert routing to Slack #alerts only (no PagerDuty).

### Steps

1. **Fire Test Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "TestMediumAlert",
         "severity": "medium",
         "service": "recipe-api"
       },
       "annotations": {
         "summary": "Medium Severity Test Alert",
         "description": "Moderate latency increase detected"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Expected Results:**

   **PagerDuty:**
   - ❌ No incident created

   **Slack #alerts:**
   - ✅ Message posted
   - ✅ Title: "MEDIUM - TestMediumAlert"
   - ✅ Bell emoji (🔔)
   - ✅ Lower urgency formatting

---

## Test 4: Low Severity Alert (P4)

### Purpose
Test low severity alert routing to Slack #alerts with hourly digest.

### Steps

1. **Fire Multiple Low Alerts:**
   ```bash
   for i in {1..5}; do
     curl -X POST http://localhost:9093/api/v1/alerts \
       -H "Content-Type: application/json" \
       -d '[{
         "labels": {
           "alertname": "TestLowAlert'$i'",
           "severity": "low",
           "service": "recipe-api"
         },
         "annotations": {
           "summary": "Low Severity Test Alert '$i'",
           "description": "Informational alert"
         },
         "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
       }]'
     sleep 2
   done
   ```

2. **Expected Results:**

   **Slack #alerts:**
   - ✅ Alerts grouped together
   - ✅ Single digest message (after 1 hour wait)
   - ✅ Information emoji (ℹ️)
   - ✅ Summary of all low alerts

---

## Test 5: Business Metrics Alert

### Purpose
Test business metric alerts routing to Slack #business-metrics.

### Steps

1. **Fire Business Metric Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "LowCartCompletionRate",
         "severity": "medium",
         "category": "business"
       },
       "annotations": {
         "summary": "Cart completion rate below threshold",
         "description": "Only 40% of carts are being completed",
         "current_value": "40%",
         "threshold": "50%",
         "impact": "Potential revenue loss"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Expected Results:**

   **Slack #business-metrics:**
   - ✅ Message posted
   - ✅ Chart emoji (📈)
   - ✅ Business-focused formatting
   - ✅ Current value and threshold
   - ✅ Business impact description
   - ✅ Link to Business Metrics dashboard

---

## Test 6: Deployment Alert

### Purpose
Test deployment notification routing to Slack #deployments.

### Steps

1. **Fire Deployment Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "DeploymentInProgress",
         "category": "deployment",
         "service": "recipe-api",
         "environment": "production",
         "version": "v1.2.3"
       },
       "annotations": {
         "summary": "Deployment of recipe-api v1.2.3 in progress",
         "description": "Deployment started",
         "health_status": "PASSED"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Expected Results:**

   **Slack #deployments:**
   - ✅ Message posted
   - ✅ Rocket emoji (🚀)
   - ✅ Service and version information
   - ✅ Environment (production)
   - ✅ Health check status

---

## Test 7: Alert Grouping

### Purpose
Test alert grouping and deduplication.

### Steps

1. **Fire Multiple Similar Alerts:**
   ```bash
   for i in {1..3}; do
     curl -X POST http://localhost:9093/api/v1/alerts \
       -H "Content-Type: application/json" \
       -d '[{
         "labels": {
           "alertname": "HighErrorRate",
           "severity": "critical",
           "service": "recipe-api"
         },
         "annotations": {
           "summary": "High error rate detected",
           "description": "Error rate at 8% (instance '$i')"
         },
         "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
       }]'
     sleep 5
   done
   ```

2. **Expected Results:**
   - ✅ Alerts grouped into single notification
   - ✅ Shows "3 firing alerts"
   - ✅ All instances listed in message
   - ✅ No duplicate PagerDuty incidents

---

## Test 8: Inhibition Rules

### Purpose
Test alert inhibition (suppressing lower severity when higher exists).

### Steps

1. **Fire Critical Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "ServiceDown",
         "severity": "critical",
         "service": "recipe-api"
       },
       "annotations": {
         "summary": "Service is down",
         "description": "API is not responding"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Fire Warning Alert for Same Service:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "HighLatency",
         "severity": "warning",
         "service": "recipe-api"
       },
       "annotations": {
         "summary": "High latency detected",
         "description": "Response time > 2s"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

3. **Expected Results:**
   - ✅ Critical alert fires normally
   - ✅ Warning alert is inhibited (not sent)
   - ✅ Only one notification received
   - ✅ Check Alertmanager UI to see inhibited alerts

---

## Test 9: Alert Repeat Interval

### Purpose
Test alert repeat notification timing.

### Steps

1. **Fire Persistent Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "PersistentTest",
         "severity": "high",
         "service": "test"
       },
       "annotations": {
         "summary": "Persistent test alert",
         "description": "Testing repeat interval"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Monitor Notifications:**
   - Initial notification: Immediate
   - Second notification: After 1 hour (high severity repeat interval)
   - Continue monitoring to confirm

3. **Expected Results:**
   - ✅ First notification sent immediately
   - ✅ Second notification after 1 hour
   - ✅ No notifications in between

---

## Test 10: Slack Message Formatting

### Purpose
Verify Slack message formatting and actionable buttons.

### Steps

1. **Fire Alert with All Features:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "FormattingTest",
         "severity": "critical",
         "service": "recipe-api",
         "endpoint": "/api/v1/meal-plans"
       },
       "annotations": {
         "summary": "Test of Slack message formatting",
         "description": "Verifying all formatting elements",
         "impact": "User-facing impact description",
         "runbook_url": "https://github.com/your-org/runbooks#test"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Verify in Slack:**
   - ✅ Title is bold and prominent
   - ✅ Emoji matches severity
   - ✅ Service and endpoint clearly displayed
   - ✅ Description is readable
   - ✅ Impact section highlighted
   - ✅ Three buttons present:
     - View Runbook (clickable)
     - View Metrics (opens Grafana)
     - View Logs (opens Loki)
   - ✅ Footer with Prometheus link

3. **Click Each Button:**
   - ✅ Runbook button opens GitHub
   - ✅ Metrics button opens Grafana dashboard
   - ✅ Logs button opens Loki explore

---

## Test 11: PagerDuty Escalation

### Purpose
Test PagerDuty escalation policy.

### Steps

1. **Fire Critical Alert:**
   ```bash
   curl -X POST http://localhost:9093/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '[{
       "labels": {
         "alertname": "EscalationTest",
         "severity": "critical",
         "service": "recipe-api"
       },
       "annotations": {
         "summary": "Testing escalation policy",
         "description": "Do not acknowledge this alert"
       },
       "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
     }]'
   ```

2. **Monitor Escalation:**
   - 0 min: Primary on-call notified
   - 15 min: Backup engineer notified (if no ack)
   - 30 min: Team lead notified (if still no ack)

3. **Verify:**
   - ✅ Check PagerDuty incident timeline
   - ✅ Confirm notifications to each level
   - ✅ Verify timing matches policy

4. **Test Early Acknowledgment:**
   - Acknowledge after 5 minutes
   - ✅ Escalation stops
   - ✅ No further notifications

---

## Troubleshooting

### No Alerts Received

**Check Alertmanager:**
```bash
# View Alertmanager logs
docker logs recipe-alertmanager

# Check Alertmanager API
curl http://localhost:9093/api/v1/alerts
```

**Check Prometheus:**
```bash
# View Prometheus logs
docker logs recipe-prometheus

# Check alerts in Prometheus
curl http://localhost:9090/api/v1/alerts
```

**Verify Configuration:**
```bash
# Check Alertmanager config
docker exec recipe-alertmanager cat /etc/alertmanager/alertmanager.yml

# Check environment variables
docker exec recipe-alertmanager env | grep -E "PAGERDUTY|SLACK"
```

### Slack Webhooks Not Working

**Test Webhook Directly:**
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Test message from Alertmanager"
  }'
```

**Common Issues:**
- Invalid webhook URL
- Webhook expired (regenerate in Slack)
- Channel permissions
- App not installed in workspace

### PagerDuty Not Receiving

**Test PagerDuty API:**
```bash
curl -X POST https://events.pagerduty.com/v2/enqueue \
  -H 'Content-Type: application/json' \
  -d '{
    "routing_key": "'$PAGERDUTY_CRITICAL_KEY'",
    "event_action": "trigger",
    "payload": {
      "summary": "Test incident",
      "severity": "critical",
      "source": "alertmanager"
    }
  }'
```

**Common Issues:**
- Invalid integration key
- Service disabled in PagerDuty
- Maintenance mode enabled
- Rate limiting

---

## Validation Checklist

After completing all tests, verify:

- [ ] Critical alerts trigger PagerDuty P1
- [ ] Critical alerts post to Slack #incident-response
- [ ] High alerts trigger PagerDuty P2
- [ ] Medium alerts post to Slack #alerts
- [ ] Low alerts are grouped hourly
- [ ] Business metrics post to #business-metrics
- [ ] Deployment alerts post to #deployments
- [ ] Alert grouping works correctly
- [ ] Inhibition rules suppress lower severity
- [ ] Repeat intervals are correct
- [ ] Slack formatting is correct
- [ ] Buttons work in Slack messages
- [ ] PagerDuty escalation policy works
- [ ] Resolved alerts update properly
- [ ] Alertmanager UI shows all alerts

---

## Production Readiness

Before enabling in production:

1. **Configure Real Integration Keys:**
   - PagerDuty production service keys
   - Slack production webhook URLs

2. **Set Up On-Call Schedule:**
   - Configure PagerDuty schedule
   - Add all team members
   - Test escalation paths

3. **Create Real Runbooks:**
   - Document all critical alerts
   - Add runbook URLs to alerts
   - Train team on runbook usage

4. **Test in Staging:**
   - Fire real alerts from staging
   - Verify all integrations work
   - Test full incident workflow

5. **Monitor Alert Volume:**
   - Start with higher thresholds
   - Tune based on actual traffic
   - Avoid alert fatigue

---

## Support

- **Alertmanager Docs:** https://prometheus.io/docs/alerting/latest/alertmanager/
- **PagerDuty Integration:** https://www.pagerduty.com/docs/guides/prometheus-integration-guide/
- **Slack Webhooks:** https://api.slack.com/messaging/webhooks

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0
