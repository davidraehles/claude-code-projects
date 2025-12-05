# Security Incident Response Runbook

## Document Information

- **Version:** 1.0.0
- **Last Updated:** 2025-12-05
- **Owner:** Security Team
- **Review Cycle:** Quarterly
- **Classification:** Internal Use Only

## Table of Contents

1. [Overview](#overview)
2. [Severity Levels](#severity-levels)
3. [Response Procedures by Incident Type](#response-procedures-by-incident-type)
4. [Escalation Path](#escalation-path)
5. [Evidence Preservation](#evidence-preservation)
6. [Communication](#communication)
7. [Post-Incident Review](#post-incident-review)
8. [Contact Information](#contact-information)
9. [Tools and Resources](#tools-and-resources)

## Overview

This runbook provides comprehensive procedures for responding to security incidents in the AI Meal Planner application. All team members should be familiar with these procedures and know their roles during an incident.

### Key Principles

- **Act Quickly:** Time is critical in limiting damage
- **Document Everything:** Maintain detailed logs and timeline
- **Communicate Clearly:** Keep stakeholders informed
- **Learn and Improve:** Conduct thorough post-incident reviews
- **Preserve Evidence:** Maintain forensic integrity for investigation

### Incident Response Team

- **Incident Commander:** Coordinates overall response
- **Technical Lead:** Directs technical remediation
- **Communications Lead:** Manages internal/external communications
- **Legal/Compliance:** Ensures regulatory compliance
- **Documentation Lead:** Maintains incident timeline and evidence

## Severity Levels

### P1 - Critical (Response Time: <15 minutes)

**Characteristics:**
- Active data breach in progress
- Unauthorized access to production database
- Active exploitation of security vulnerability
- Complete service outage due to security incident
- Evidence of data exfiltration
- Ransomware or malware infection

**Impact:**
- Affects all users
- Sensitive data compromised (PII, credentials, payment info)
- Significant business disruption
- Potential legal/regulatory implications
- Reputational damage

**Initial Actions:**
1. Page on-call security engineer immediately
2. Activate incident response team within 5 minutes
3. Begin containment procedures immediately
4. Start detailed incident logging
5. Notify executive team within 15 minutes

### P2 - High (Response Time: <1 hour)

**Characteristics:**
- Unauthorized access to user account(s)
- Exploitation attempt detected but contained
- Significant rate of authentication failures
- Suspicious admin activity
- Potential vulnerability discovered in production
- Credential compromise suspected

**Impact:**
- Affects multiple users or sensitive data
- Moderate business disruption
- Potential for escalation to P1
- May require customer notification

**Initial Actions:**
1. Notify on-call engineer via Slack/PagerDuty
2. Assemble response team within 30 minutes
3. Begin investigation and containment
4. Document incident details
5. Notify management within 1 hour

### P3 - Medium (Response Time: <4 hours)

**Characteristics:**
- Rate limiting triggered excessively
- Suspicious but not malicious activity
- Configuration issues affecting security
- Failed security audit checks
- Unusual traffic patterns
- Non-critical vulnerability discovered

**Impact:**
- Limited user impact
- No immediate data exposure
- Requires monitoring and remediation
- Low escalation risk

**Initial Actions:**
1. Create incident ticket
2. Assign to on-call engineer
3. Begin investigation during business hours
4. Monitor for escalation
5. Document findings

### P4 - Low (Response Time: Next business day)

**Characteristics:**
- Missing security headers (non-critical)
- Minor configuration drift
- Potential vulnerability in non-production environment
- Security best practice violation
- Information disclosure (non-sensitive)

**Impact:**
- Minimal or no user impact
- No data exposure
- Standard remediation process

**Initial Actions:**
1. Create ticket in backlog
2. Prioritize in next sprint
3. Document issue and recommended fix
4. No immediate action required

## Response Procedures by Incident Type

### A. Unauthorized Access

**Detection Indicators:**
- Multiple failed login attempts from single source
- Successful login from unusual location/device
- Session activity not matching user patterns
- Access to resources outside normal scope
- API calls from unexpected sources

**Immediate Response (0-15 minutes):**

1. **Identify Compromised Account(s)**
   ```bash
   # Query recent login activity
   psql -c "SELECT user_id, ip_address, user_agent, created_at
            FROM user_sessions
            WHERE created_at > NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC;"

   # Check for suspicious patterns
   grep "Failed login" /var/log/app/auth.log | tail -100
   ```

2. **Revoke Sessions Immediately**
   ```bash
   # Via admin API
   curl -X POST https://api.example.com/api/v1/admin/users/{user_id}/revoke-sessions \
     -H "Authorization: Bearer ${ADMIN_TOKEN}"

   # Or via database
   psql -c "DELETE FROM user_sessions WHERE user_id = {compromised_user_id};"
   ```

3. **Change Critical Secrets**
   ```bash
   # Rotate API keys
   ./scripts/rotate_api_keys.sh

   # Update environment variables
   railway variables set JWT_SECRET=$(openssl rand -hex 32)

   # Restart services with new secrets
   railway up -d
   ```

4. **Review Access Logs (15-60 minutes)**
   ```bash
   # Extract logs with correlation IDs
   grep "user_id:{compromised_user_id}" /var/log/app/application.log \
     > /tmp/incident_$(date +%Y%m%d_%H%M%S).log

   # Check database query logs
   psql -c "SELECT query, query_start, usename
            FROM pg_stat_activity
            WHERE usename = 'compromised_user';"
   ```

5. **Notify Affected Users (1-24 hours)**
   - Use email template (see Communication section)
   - Force password reset on next login
   - Recommend enabling 2FA
   - Monitor account for 7 days

6. **Monitor for Further Access (Ongoing)**
   - Set up alerts for the compromised account
   - Monitor related accounts (same IP, similar patterns)
   - Review all API keys associated with account

### B. Data Exfiltration

**Detection Indicators:**
- Unusually large database queries
- Bulk data export operations
- High volume API calls
- Data transfer to unknown destinations
- Sentry alerts for unusual database activity

**Immediate Response (0-15 minutes):**

1. **Identify Data Accessed**
   ```bash
   # Check PostgreSQL query logs
   tail -1000 /var/log/postgresql/postgresql.log | grep "SELECT.*FROM users"

   # Review application logs for bulk operations
   grep "bulk_export\|data_export" /var/log/app/application.log

   # Check Sentry for database performance issues
   # https://sentry.io/organizations/meal-planner/issues/?query=transaction.op:db.sql
   ```

2. **Revoke Authentication Tokens**
   ```bash
   # Revoke all tokens for suspicious users
   psql -c "DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE last_login > NOW() - INTERVAL '1 hour');"

   # Invalidate API keys
   psql -c "UPDATE api_keys SET is_active = false WHERE user_id = {user_id};"
   ```

3. **Enable Enhanced Monitoring**
   ```bash
   # Increase log verbosity
   export LOG_LEVEL=DEBUG

   # Enable query logging in PostgreSQL
   psql -c "ALTER SYSTEM SET log_statement = 'all';"
   psql -c "SELECT pg_reload_conf();"

   # Enable Sentry trace sampling to 100%
   export SENTRY_TRACES_SAMPLE_RATE=1.0
   ```

4. **Contact Legal/Compliance (0-2 hours)**
   - Document extent of potential data exposure
   - Determine if breach notification is required
   - Review regulatory obligations (GDPR, CCPA, etc.)
   - Prepare for potential legal actions

5. **Breach Notification if Required (24-72 hours)**
   - GDPR: 72 hours from discovery
   - CCPA: As soon as practicable
   - Document:
     - Nature of breach
     - Categories of data affected
     - Number of individuals affected
     - Remediation steps taken
     - Contact point for inquiries

6. **Post-Incident Forensics**
   - Preserve all logs (minimum 90 days)
   - Reconstruct timeline of access
   - Identify attack vector
   - Assess full scope of compromise
   - Engage third-party forensics if necessary

### C. SQL Injection / RCE Attempt

**Detection Indicators:**
- SQL syntax in request parameters
- Command injection patterns in logs
- Unexpected application errors
- WAF/input validation alerts
- Sentry errors with suspicious patterns

**Immediate Response (0-15 minutes):**

1. **Block Source IP**
   ```bash
   # Add to firewall rules
   ufw deny from {attacker_ip}

   # Or via CloudFlare (if available)
   cf-cli firewall rules create --expression "ip.src == {attacker_ip}" --action block
   ```

2. **Increase Rate Limiting**
   ```bash
   # Temporarily reduce limits via admin API
   curl -X PUT https://api.example.com/api/v1/admin/rate-limits \
     -H "Authorization: Bearer ${ADMIN_TOKEN}" \
     -d '{"endpoint": "/api/v1/**", "limit": 10, "window": 300}'
   ```

3. **Review Application Logs (15-60 minutes)**
   ```bash
   # Extract suspicious requests
   grep -E "(\\'|\\\"|\\ OR\\ |UNION|SELECT.*FROM)" /var/log/app/access.log \
     > /tmp/sql_injection_attempt_$(date +%Y%m%d_%H%M%S).log

   # Check for command injection
   grep -E "(;|&&|\\||\\$\\(|\\`)" /var/log/app/access.log
   ```

4. **Patch Vulnerability (1-4 hours)**
   - Identify vulnerable endpoint
   - Apply input validation/sanitization
   - Review similar code patterns
   - Write test case for the vulnerability
   - Deploy fix to staging

   ```python
   # Example fix: Add input validation
   from pydantic import validator

   class RecipeSearch(BaseModel):
       query: str

       @validator("query")
       def validate_query(cls, v):
           # Remove SQL keywords and special characters
           forbidden = ["SELECT", "DROP", "INSERT", "DELETE", "UPDATE", "UNION"]
           if any(keyword in v.upper() for keyword in forbidden):
               raise ValueError("Invalid search query")
           return v
   ```

5. **Deploy Fix to Production (4-8 hours)**
   ```bash
   # Run tests
   pytest tests/ -v --cov=app

   # Deploy to staging
   git push origin fix/sql-injection-patch

   # After validation, deploy to production
   railway up -d --environment production
   ```

6. **Monitor Exploit Signatures (Ongoing)**
   ```bash
   # Set up alert for similar patterns
   # Add to monitoring/alerts.yml
   - alert: SQLInjectionAttempt
     expr: rate(http_requests_total{status="400"}[5m]) > 10
     annotations:
       summary: "Potential SQL injection attempt detected"
   ```

### D. DDoS Attack

**Detection Indicators:**
- Sudden spike in request volume
- High rate of 429 errors
- Increased server load/CPU usage
- Slow response times
- Multiple requests from same IP ranges

**Immediate Response (0-15 minutes):**

1. **Enable CloudFlare/WAF (if available)**
   ```bash
   # Activate "Under Attack" mode
   cf-cli security-level set high

   # Enable rate limiting at CDN level
   cf-cli rate-limit create --threshold 100 --period 60
   ```

2. **Increase Rate Limits Temporarily**
   ```bash
   # Reduce per-IP limits
   psql -c "UPDATE rate_limit_policies
            SET requests_per_window = 50
            WHERE endpoint_pattern = '^/api/v1/.*$';"

   # Restart application to pick up changes
   railway restart
   ```

3. **Monitor Performance Impact (Ongoing)**
   ```bash
   # Check server metrics
   docker stats

   # Monitor request latency
   curl https://api.example.com/metrics | grep http_request_duration

   # Check database performance
   psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
   ```

4. **Scale Infrastructure if Needed (15-60 minutes)**
   ```bash
   # Scale horizontally (Railway)
   railway scale web=5

   # Or vertically
   railway resources set --memory 4GB --cpu 2

   # Scale database read replicas
   railway addons create postgresql-read-replica
   ```

5. **Contact ISP if Persistent (1-4 hours)**
   - Provide attack details (source IPs, patterns)
   - Request upstream filtering
   - Document communication

6. **Analyze Attack Patterns (Post-incident)**
   ```bash
   # Extract attack characteristics
   awk '{print $1}' /var/log/app/access.log | sort | uniq -c | sort -rn | head -20

   # Identify bot patterns
   grep -E "bot|crawler|spider" /var/log/app/access.log | wc -l
   ```

### E. API Key / Credential Compromise

**Detection Indicators:**
- API key used from unexpected location
- Unusual usage patterns for API key
- Alert from secret scanning tools
- Credential found in public repository
- Third-party notification of exposure

**Immediate Response (0-15 minutes):**

1. **Revoke Compromised Credentials**
   ```bash
   # Revoke specific API key
   psql -c "UPDATE api_keys SET is_active = false, revoked_at = NOW()
            WHERE key_hash = '${compromised_key_hash}';"

   # Or via API
   curl -X DELETE https://api.example.com/api/v1/admin/api-keys/{key_id} \
     -H "Authorization: Bearer ${ADMIN_TOKEN}"
   ```

2. **Rotate All Related Credentials (15-60 minutes)**
   ```bash
   # Rotate database password
   ./scripts/rotate_db_password.sh

   # Rotate JWT secret
   railway variables set JWT_SECRET=$(openssl rand -hex 32)

   # Rotate API keys for external services
   railway variables set ANTHROPIC_API_KEY=${new_key}
   railway variables set KNUSPR_API_KEY=${new_key}

   # Rotate encryption keys
   railway variables set ENCRYPTION_KEY=$(openssl rand -hex 32)
   ```

3. **Audit Usage Logs (1-4 hours)**
   ```bash
   # Check all requests with compromised key
   grep "api_key_id:${key_id}" /var/log/app/access.log \
     > /tmp/compromised_key_usage_$(date +%Y%m%d_%H%M%S).log

   # Review Sentry for errors from key
   # Filter by user context: api_key_id = ${key_id}

   # Check correlation IDs for related requests
   grep "correlation_id:${correlation_id}" /var/log/app/application.log
   ```

4. **Create New Credentials (1-2 hours)**
   ```bash
   # Generate new API key for user
   curl -X POST https://api.example.com/api/v1/api-keys \
     -H "Authorization: Bearer ${USER_TOKEN}" \
     -d '{"name": "New Key - Post Incident", "scopes": ["read:recipes", "write:meal_plans"]}'

   # Document new credentials securely
   # Store in 1Password/Vault, not in plain text
   ```

5. **Update All Services (2-8 hours)**
   ```bash
   # Update frontend environment
   cd frontend
   vercel env add NEXT_PUBLIC_API_KEY

   # Update backend environment
   cd backend
   railway variables set API_KEY=${new_key}

   # Update CI/CD secrets
   gh secret set API_KEY --body "${new_key}"

   # Restart all services
   railway restart --all
   ```

6. **Monitor for Misuse (Ongoing - 7 days)**
   ```bash
   # Set up alerts for old key usage attempts
   # This should trigger 401 errors now

   # Create monitoring query
   SELECT COUNT(*)
   FROM audit_logs
   WHERE api_key_hash = '${old_key_hash}'
     AND created_at > NOW() - INTERVAL '24 hours';

   # Alert if count > 0
   ```

## Escalation Path

### Level 1: On-Call Engineer
- **Availability:** 24/7
- **Contact:** PagerDuty (primary), Slack #on-call-engineering (backup)
- **Responsibilities:**
  - Initial triage and assessment
  - Immediate containment actions
  - Escalate if severity is P1 or if unable to contain

### Level 2: Technical Lead / Security Lead
- **Availability:** 24/7 for P1, business hours for P2+
- **Contact:** Phone (stored in PagerDuty), Slack @tech-lead
- **Responsibilities:**
  - Coordinate technical response
  - Make architectural decisions
  - Approve significant changes
  - Determine if further escalation needed

### Level 3: CISO / VP Engineering
- **Availability:** 24/7 for P1, business hours for P2
- **Contact:** Phone (stored in PagerDuty), Email
- **Responsibilities:**
  - Overall incident command
  - Resource allocation
  - Executive communication
  - Determine if legal/PR escalation needed

### Level 4: Legal / PR / Executive Team
- **Availability:** 24/7 for data breaches, business hours otherwise
- **Contact:** Emergency contact list (see Contact Information section)
- **Responsibilities:**
  - Legal compliance
  - Customer/public communication
  - Regulatory notification
  - Media relations

### Escalation Triggers

**Automatic Escalation to Level 2:**
- Any P1 incident
- P2 incident not contained within 1 hour
- Multiple users affected
- Data exposure suspected

**Automatic Escalation to Level 3:**
- Confirmed data breach
- P1 incident lasting > 30 minutes
- Regulatory notification required
- Media inquiry received

**Automatic Escalation to Level 4:**
- PII/payment data compromised
- >1000 users affected
- Potential regulatory violation
- Media coverage or public disclosure

## Evidence Preservation

### Critical: Do NOT Delete or Modify Evidence

**Immediate Actions (Within 15 minutes):**

1. **Collect Logs Immediately**
   ```bash
   # Create evidence directory
   INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"
   mkdir -p /secure/evidence/${INCIDENT_ID}

   # Copy all relevant logs
   cp -r /var/log/app/* /secure/evidence/${INCIDENT_ID}/app_logs/
   cp -r /var/log/postgresql/* /secure/evidence/${INCIDENT_ID}/db_logs/
   cp -r /var/log/nginx/* /secure/evidence/${INCIDENT_ID}/web_logs/

   # Export Sentry events
   sentry-cli events export --org meal-planner --project backend \
     --since "1 hour ago" > /secure/evidence/${INCIDENT_ID}/sentry_events.json
   ```

2. **Database Backup Before Remediation**
   ```bash
   # Create point-in-time backup
   pg_dump -h localhost -U app_user meal_planner_db \
     > /secure/evidence/${INCIDENT_ID}/db_backup_$(date +%Y%m%d_%H%M%S).sql

   # Backup specific tables if needed
   pg_dump -h localhost -U app_user meal_planner_db \
     -t users -t user_sessions -t audit_logs \
     > /secure/evidence/${INCIDENT_ID}/db_critical_tables.sql
   ```

3. **Application Logs Export**
   ```bash
   # Export last 24 hours with full context
   journalctl -u meal-planner-api --since "24 hours ago" \
     > /secure/evidence/${INCIDENT_ID}/systemd_logs.txt

   # Export Docker logs if containerized
   docker logs meal-planner-backend \
     > /secure/evidence/${INCIDENT_ID}/docker_logs.txt 2>&1
   ```

4. **Network Traffic (if available)**
   ```bash
   # Capture current traffic (if incident ongoing)
   tcpdump -i eth0 -w /secure/evidence/${INCIDENT_ID}/traffic_capture.pcap

   # Export firewall logs
   cp /var/log/ufw.log /secure/evidence/${INCIDENT_ID}/firewall.log
   ```

5. **Timeline Reconstruction**
   ```bash
   # Create incident timeline file
   cat > /secure/evidence/${INCIDENT_ID}/timeline.md <<EOF
   # Incident Timeline: ${INCIDENT_ID}

   ## Detection
   - Time: $(date -Iseconds)
   - Detected by: [Name/System]
   - Initial indicator: [Description]

   ## Key Events
   - [Timestamp]: [Event description]

   ## Actions Taken
   - [Timestamp]: [Action and result]
   EOF
   ```

### Evidence Retention

- **Minimum Retention:** 90 days for all incidents
- **Extended Retention:** 1 year for P1/P2 incidents
- **Legal Hold:** Indefinite if legal action pending
- **Storage Location:** Secure, encrypted storage with access controls
- **Chain of Custody:** Document all access to evidence

## Communication

### Internal Communication

**Primary Channel: Slack #incident-response**

1. **Initial Alert** (Within 5 minutes of detection)
   ```
   @here SECURITY INCIDENT - [P1/P2/P3/P4]

   Incident ID: INC-20251205-143022
   Severity: P1
   Type: Unauthorized Access
   Status: INVESTIGATING

   Description: Multiple unauthorized access attempts detected on admin endpoints

   Incident Commander: @john.doe
   Current Actions: Revoking sessions, reviewing logs

   Next Update: 15 minutes
   ```

2. **Status Updates** (Every 15-30 minutes for P1, hourly for P2)
   ```
   UPDATE: INC-20251205-143022

   Time: 14:45 UTC
   Status: CONTAINING

   Progress:
   - ✅ All suspicious sessions revoked
   - ✅ Source IP blocked
   - 🔄 Reviewing access logs (50% complete)
   - ⏳ Preparing customer notification

   Next Update: 15:00 UTC
   ```

3. **Resolution Notification**
   ```
   RESOLVED: INC-20251205-143022

   Time: 16:30 UTC
   Duration: 2h 8m

   Summary: Unauthorized access attempt blocked. No data compromised.

   Actions Taken:
   - Sessions revoked
   - IPs blocked
   - Monitoring enhanced
   - Credentials rotated

   Next Steps:
   - Post-incident review scheduled for 2025-12-06 10:00 AM
   - Customer notification (if required): 2025-12-05 18:00 UTC
   ```

### External Communication

**Status Page Updates:**

1. **Initial Notice** (Within 1 hour of P1/P2)
   ```
   🟡 Investigating - Security Event

   We are investigating a potential security issue affecting our service.
   Our team is actively working to resolve this matter.

   We will provide updates every 30 minutes.

   Posted: Dec 5, 2025 14:45 UTC
   ```

2. **Customer Notification Template** (With legal review)
   ```
   Subject: Important Security Notice - AI Meal Planner

   Dear [Customer Name],

   We are writing to inform you about a security incident that may have
   affected your account on [Date].

   WHAT HAPPENED:
   [Brief description of incident]

   WHAT INFORMATION WAS INVOLVED:
   [Specific data categories]

   WHAT WE ARE DOING:
   [Actions taken and ongoing]

   WHAT YOU SHOULD DO:
   - Reset your password immediately
   - Enable two-factor authentication
   - Monitor your account for unusual activity
   - Review our security best practices: [URL]

   We take the security of your information very seriously and deeply
   apologize for any inconvenience this may cause.

   For questions, please contact: security@meal-planner.com

   Sincerely,
   AI Meal Planner Security Team
   ```

3. **Media Response Guidelines**
   - All media inquiries: Forward to PR team immediately
   - Do NOT comment on ongoing incidents
   - Do NOT speculate on impact or cause
   - Approved statement only from PR/Legal
   - Refer to status page for official updates

## Post-Incident Review

### Timeline: Within 48 hours of resolution

### Review Meeting Agenda (60-90 minutes)

1. **Incident Overview** (10 minutes)
   - What happened?
   - When was it detected?
   - What was the impact?

2. **Timeline Review** (20 minutes)
   - Detection to containment
   - Key decision points
   - Response effectiveness

3. **Root Cause Analysis** (20 minutes)
   - What was the root cause?
   - Why did it happen?
   - What controls failed?
   - Five Whys technique

4. **Response Evaluation** (15 minutes)
   - What went well?
   - What could be improved?
   - Were procedures followed?
   - Communication effectiveness

5. **Action Items** (20 minutes)
   - Preventive measures
   - Monitoring improvements
   - Training needs
   - Runbook updates
   - Assign owners and due dates

### Post-Incident Report Template

```markdown
# Post-Incident Review: [Incident ID]

## Executive Summary
- **Incident ID:** INC-YYYYMMDD-HHMMSS
- **Date:** YYYY-MM-DD
- **Severity:** P1/P2/P3/P4
- **Duration:** X hours Y minutes
- **Impact:** [Brief description]
- **Root Cause:** [Brief description]

## Incident Details

### Timeline
| Time (UTC) | Event | Action Taken |
|------------|-------|--------------|
| 14:30 | Initial detection | Alert triggered |
| 14:32 | Response began | On-call paged |
| 14:45 | Containment | Sessions revoked |
| 16:30 | Resolution | Monitoring restored |

### Root Cause
[Detailed analysis of what caused the incident]

### Impact Assessment
- **Users Affected:** [Number]
- **Data Exposed:** [Yes/No - Details]
- **Service Downtime:** [Duration]
- **Financial Impact:** [If applicable]

## Response Analysis

### What Went Well
- Quick detection via monitoring
- Effective containment procedures
- Good communication with stakeholders

### What Could Be Improved
- Faster escalation process
- Better documentation of steps
- Additional monitoring coverage

## Preventive Measures

### Immediate (Within 1 week)
- [ ] Implement additional monitoring for [specific area]
- [ ] Update firewall rules
- [ ] Rotate credentials

### Short-term (Within 1 month)
- [ ] Enhance input validation
- [ ] Add automated testing for vulnerability
- [ ] Update training materials

### Long-term (Within 3 months)
- [ ] Implement WAF
- [ ] Add intrusion detection system
- [ ] Conduct security audit

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Update rate limiting | @engineer | 2025-12-12 | Open |
| Schedule training | @manager | 2025-12-20 | Open |

## Lessons Learned
[Key takeaways and insights for future incidents]

## Approvals
- Technical Lead: ________________ Date: _______
- CISO: ________________ Date: _______
```

## Contact Information

### Emergency Contacts (24/7)

**On-Call Engineering:**
- Primary: PagerDuty rotation
- Backup: Slack #on-call-engineering
- Escalation: +1-XXX-XXX-XXXX (Tech Lead)

**Security Team:**
- Email: security@meal-planner.com
- Slack: #security-team
- Emergency: +1-XXX-XXX-XXXX

**Management:**
- Tech Lead: tech-lead@meal-planner.com | +1-XXX-XXX-XXXX
- CISO: ciso@meal-planner.com | +1-XXX-XXX-XXXX
- VP Engineering: vp-eng@meal-planner.com | +1-XXX-XXX-XXXX

**Legal/Compliance:**
- General Counsel: legal@meal-planner.com | +1-XXX-XXX-XXXX
- Compliance Officer: compliance@meal-planner.com | +1-XXX-XXX-XXXX

**External Resources:**
- Cloud Provider Support: support@railway.app
- Database Support: support@postgresql.org
- Security Vendor: vendor-support@example.com

### Business Hours Contacts

**Product Team:**
- Slack: #product-team
- Email: product@meal-planner.com

**Customer Success:**
- Slack: #customer-success
- Email: support@meal-planner.com

**Public Relations:**
- Email: pr@meal-planner.com
- Phone: +1-XXX-XXX-XXXX

## Tools and Resources

### Monitoring and Alerting
- **Sentry:** https://sentry.io/organizations/meal-planner/
- **Prometheus:** http://prometheus.internal:9090
- **Grafana:** http://grafana.internal:3000
- **Railway Dashboard:** https://railway.app/dashboard

### Logging
- **Application Logs:** `/var/log/app/`
- **Database Logs:** `/var/log/postgresql/`
- **Web Server Logs:** `/var/log/nginx/`
- **System Logs:** `journalctl -u meal-planner-*`

### Security Tools
- **OWASP ZAP:** For vulnerability scanning
- **SQLMap:** For SQL injection testing
- **Nmap:** For network reconnaissance
- **Wireshark:** For packet analysis

### Documentation
- **Runbooks:** `/docs/runbooks/`
- **Architecture:** `/docs/ARCHITECTURE.md`
- **API Documentation:** https://api.meal-planner.com/docs
- **Security Policy:** `/docs/SECURITY_POLICY.md`

### Scripts and Automation
- **Log Collection:** `/infrastructure/scripts/collect_incident_logs.sh`
- **Credential Rotation:** `/infrastructure/scripts/rotate_credentials.sh`
- **Database Backup:** `/infrastructure/scripts/backup_database.sh`
- **Service Restart:** `/infrastructure/scripts/restart_services.sh`

---

**Document Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-05 | Security Team | Initial version |

**Next Review Date:** 2026-03-05

**Questions or Feedback:** security@meal-planner.com
