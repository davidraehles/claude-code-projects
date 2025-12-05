# Disaster Recovery Plan - AI Meal Planner

## Executive Summary

This document outlines the disaster recovery procedures for the AI Meal Planner application. It defines recovery objectives, backup strategies, restoration procedures, and escalation protocols.

**Last Updated**: 2025-01-15
**Version**: 1.0
**Owner**: Backend Infrastructure Team

## Recovery Objectives

### Recovery Time Objective (RTO): 4 hours

The maximum acceptable time to restore full service functionality after a disaster.

**Breakdown by Service:**
- **Database**: 2 hours
- **Backend API**: 1 hour
- **Frontend**: 30 minutes
- **Verification & Testing**: 30 minutes

### Recovery Point Objective (RPO): 1 hour

The maximum acceptable amount of data loss measured in time.

**Implementation:**
- Automated backups every 1 hour
- Point-in-time recovery available for last 7 days
- Critical transactions logged for replay

## Backup Strategy

### Automated Backups

#### Schedule

- **Production Database**: Every 1 hour (automated)
- **Full Daily Backup**: Daily at 2:00 AM UTC
- **Weekly Archive**: Sundays at 3:00 AM UTC
- **Monthly Archive**: First day of month at 4:00 AM UTC

#### Retention Policy

- **Hourly Backups**: 24 hours (last 24 hourly backups)
- **Daily Backups**: 30 days
- **Weekly Backups**: 12 weeks (3 months)
- **Monthly Backups**: 12 months

#### Storage Locations

**Primary Backup Storage:**
- **Location**: AWS S3 (US-East-1)
- **Bucket**: `ai-meal-planner-backups`
- **Storage Class**: Standard-IA (Infrequent Access) for cost optimization
- **Encryption**: AES-256 server-side encryption
- **Versioning**: Enabled for 30 days

**Secondary Backup Storage (Disaster Recovery):**
- **Location**: AWS S3 (US-West-2) - Different region
- **Bucket**: `ai-meal-planner-backups-dr`
- **Replication**: Cross-region replication from primary
- **Storage Class**: Glacier for long-term retention

### Backup Types

#### Full Database Backup

Complete dump of entire PostgreSQL database including:
- All tables and data
- Indexes and constraints
- Sequences and triggers
- User-defined functions
- Schema definitions

**File Format**: Compressed SQL dump (`.sql.gz`)
**Average Size**: ~50-100MB (compressed)
**Estimated Restore Time**: 30-60 minutes

#### Incremental Backups

Railway PostgreSQL provides continuous archiving (WAL archiving) for point-in-time recovery.

**Retention**: 7 days
**Recovery Granularity**: Down to the second

### Backup Verification

#### Automated Verification (Daily)

- **Integrity Check**: Verify backup file is not corrupted (gzip -t)
- **Size Check**: Ensure backup size is within expected range
- **Test Restore**: Monthly test restore to staging environment

#### Manual Verification (Monthly)

- Full restore to isolated environment
- Data integrity validation queries
- Application functionality testing
- Performance benchmarking

## Disaster Scenarios

### Scenario 1: Database Corruption

**Trigger**: Data corruption detected, queries failing, inconsistent data

**Recovery Steps:**

1. **Immediate Actions (0-15 minutes)**
   - Put application in maintenance mode
   - Stop all write operations to database
   - Identify scope of corruption
   - Alert on-call engineer

2. **Assessment (15-30 minutes)**
   - Determine extent of corruption
   - Identify last known good backup
   - Check if point-in-time recovery is possible
   - Notify stakeholders

3. **Recovery (30 minutes - 2 hours)**
   - Create snapshot of corrupted database (for analysis)
   - Restore from latest clean backup
   - Apply transaction logs if using point-in-time recovery
   - Verify data integrity

4. **Validation (2-3 hours)**
   - Run integrity checks
   - Test critical workflows
   - Verify data consistency
   - Application smoke tests

5. **Return to Service (3-4 hours)**
   - Remove maintenance mode
   - Monitor error rates
   - Check application logs
   - Full functionality verification

### Scenario 2: Complete Database Loss

**Trigger**: Database instance unavailable, cannot connect, total data loss

**Recovery Steps:**

1. **Immediate Actions (0-15 minutes)**
   - Activate incident response team
   - Put application in maintenance mode
   - Determine cause (hardware failure, cloud provider issue, etc.)
   - Begin provisioning new database instance

2. **Database Provisioning (15-45 minutes)**
   - Create new Railway PostgreSQL instance
   - Configure same specifications as production
   - Set up network access and security
   - Update DATABASE_URL in application

3. **Data Restoration (45 minutes - 2 hours)**
   - Download latest backup from S3
   - Restore database from backup
   - Apply any available transaction logs
   - Verify restoration success

4. **Validation & Testing (2-3 hours)**
   - Run database integrity checks
   - Test application connectivity
   - Verify critical user workflows
   - Check data completeness

5. **Return to Service (3-4 hours)**
   - Update DNS/connection strings if needed
   - Remove maintenance mode
   - Monitor closely for issues
   - Post-incident review

### Scenario 3: Partial Data Loss (User Error)

**Trigger**: Accidental deletion, incorrect data modification, bad migration

**Recovery Steps:**

1. **Immediate Actions (0-5 minutes)**
   - Identify affected data/tables
   - Prevent further damage
   - Document the issue

2. **Assessment (5-15 minutes)**
   - Determine timestamp of data loss
   - Identify which backup to use
   - Assess impact on users

3. **Recovery (15-60 minutes)**
   - **Option A: Point-in-Time Recovery**
     - Use Railway's PITR to specific timestamp
     - Restore to before the incident

   - **Option B: Selective Restore**
     - Restore backup to temporary database
     - Extract affected tables/rows
     - Import into production database

4. **Validation (60-90 minutes)**
   - Verify recovered data
   - Check referential integrity
   - Test affected features

5. **Return to Normal (90-120 minutes)**
   - Communication to affected users
   - Monitor for any issues
   - Document incident

### Scenario 4: Cloud Provider Outage (Railway/AWS)

**Trigger**: Railway platform unavailable, cannot access services

**Recovery Steps:**

1. **Immediate Actions (0-30 minutes)**
   - Confirm Railway outage via status page
   - Activate disaster recovery plan
   - Notify stakeholders
   - Begin provisioning alternative infrastructure

2. **Alternative Infrastructure (30 minutes - 2 hours)**
   - Provision PostgreSQL on alternative cloud (AWS RDS, DigitalOcean, etc.)
   - Deploy backend to alternative platform (Heroku, AWS ECS, etc.)
   - Update environment variables and configuration

3. **Data Restoration (2-3 hours)**
   - Restore database from S3 backup
   - Update backend DATABASE_URL
   - Deploy latest backend version

4. **Frontend Update (3-3.5 hours)**
   - Update Vercel environment variables
   - Point API_URL to new backend
   - Redeploy frontend

5. **Validation & Return (3.5-4 hours)**
   - Full system testing
   - User acceptance testing
   - Remove maintenance mode
   - Monitor closely

### Scenario 5: Security Breach / Data Compromise

**Trigger**: Unauthorized access detected, data breach suspected

**Recovery Steps:**

1. **Immediate Actions (0-15 minutes)**
   - ISOLATE compromised systems immediately
   - Revoke all access tokens and API keys
   - Enable maintenance mode
   - Activate security incident response

2. **Forensic Analysis (15 minutes - 2 hours)**
   - Capture logs and evidence
   - Identify breach timeline
   - Determine data accessed/modified
   - Document for compliance/legal

3. **System Restoration (2-4 hours)**
   - Restore database to pre-breach state
   - Rotate all credentials and secrets
   - Update security rules and firewall
   - Patch vulnerabilities

4. **Security Hardening (Parallel Process)**
   - Review and update access controls
   - Implement additional monitoring
   - Enable 2FA for all admin access
   - Security audit of entire system

5. **Communication & Compliance (4-8 hours)**
   - Notify affected users (GDPR compliance)
   - Report to authorities if required
   - Document incident for insurance
   - Public communication if necessary

## Restoration Procedures

### Database Restoration from Backup

#### Using Automated Script (Recommended)

```bash
# 1. SSH into production server or use Railway CLI
railway login

# 2. Set environment variables
export DATABASE_URL='<new-database-url>'
export AWS_ACCESS_KEY_ID='<aws-key>'
export AWS_SECRET_ACCESS_KEY='<aws-secret>'

# 3. Run restore script
./infrastructure/scripts/restore_database.sh s3://ai-meal-planner-backups/database-backups/backup_20250115_020000.sql.gz

# 4. Follow prompts to confirm restoration

# 5. Verify restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM recipes;"
```

#### Manual Restoration

```bash
# 1. Download backup from S3
aws s3 cp s3://ai-meal-planner-backups/database-backups/backup_20250115_020000.sql.gz ./backup.sql.gz

# 2. Decompress backup
gunzip backup.sql.gz

# 3. Restore to database
psql $DATABASE_URL < backup.sql

# 4. Verify restoration
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "SELECT version();"  # Check PostgreSQL version
```

### Point-in-Time Recovery (PITR)

Railway PostgreSQL supports point-in-time recovery for the last 7 days.

```bash
# Using Railway CLI
railway postgres:recovery --time "2025-01-15 14:30:00 UTC"

# This creates a new database instance at the specified point in time
# Update DATABASE_URL to point to recovered database
```

### Application Restoration

#### Backend API

```bash
# 1. Verify DATABASE_URL is correct
echo $DATABASE_URL

# 2. Deploy latest backend version
cd backend
railway up

# 3. Run migrations if needed
railway run alembic upgrade head

# 4. Verify API health
curl https://api.ai-meal-planner.com/health
```

#### Frontend

```bash
# 1. Update Vercel environment variables if needed
vercel env pull

# 2. Redeploy frontend
vercel --prod

# 3. Verify frontend loads
curl -I https://ai-meal-planner.com
```

## Recovery Testing Schedule

### Monthly DR Drill (First Sunday of Each Month)

**Time**: 10:00 AM UTC
**Duration**: 2 hours
**Environment**: Staging

**Procedure:**
1. Create backup of staging database
2. Simulate disaster (delete database)
3. Restore from backup using DR procedures
4. Verify application functionality
5. Document timing and issues
6. Update DR plan based on findings

### Quarterly Full DR Test

**Frequency**: Every 3 months
**Duration**: 4 hours
**Environment**: Isolated production-like environment

**Procedure:**
1. Provision completely new infrastructure
2. Restore from production backup
3. Deploy all services from scratch
4. Full application testing
5. Performance validation
6. Team walkthrough and training

### Annual DR Simulation

**Frequency**: Once per year
**Duration**: Full day (8 hours)
**Participants**: All team members

**Procedure:**
1. Simulate realistic disaster scenario
2. Full team participation
3. Test all communication channels
4. Practice escalation procedures
5. Document lessons learned
6. Update DR plan comprehensively

## Escalation Contacts

### Primary On-Call Engineer

- **Role**: First responder for all incidents
- **Responsibility**: Initial assessment and basic recovery
- **Contact**: On-call rotation (PagerDuty)
- **Response Time**: 15 minutes

### Database Administrator

- **Name**: [To be assigned]
- **Email**: dba@ai-meal-planner.com
- **Phone**: [To be assigned]
- **Responsibility**: Complex database issues, PITR, corruption
- **Response Time**: 30 minutes

### Infrastructure Lead

- **Name**: [To be assigned]
- **Email**: infra@ai-meal-planner.com
- **Phone**: [To be assigned]
- **Responsibility**: Cloud infrastructure, multi-service outages
- **Response Time**: 30 minutes

### Security Team

- **Contact**: security@ai-meal-planner.com
- **Responsibility**: Security incidents, data breaches
- **Response Time**: 1 hour

### Executive Leadership

- **CTO**: [To be assigned]
- **CEO**: [To be assigned]
- **Contact**: Only for critical incidents affecting all users
- **Response Time**: 2 hours

### External Contacts

- **Railway Support**: support@railway.app (for platform issues)
- **AWS Support**: Enterprise support line (for S3/infrastructure)
- **Vercel Support**: support@vercel.com (for frontend issues)

## Incident Communication

### Internal Communication

- **Primary Channel**: Slack #incident-response
- **Video Bridge**: Google Meet (standing incident room)
- **Status Updates**: Every 30 minutes during active incident

### External Communication

- **Status Page**: status.ai-meal-planner.com
- **Twitter**: @AIMealPlanner
- **Email**: Automated alerts to all users for outages > 1 hour

### Communication Templates

#### Incident Start

```
Subject: [INCIDENT] Service Disruption - AI Meal Planner

We are currently experiencing issues with [service name].
Our team is actively investigating and working on a resolution.

Started: [timestamp]
Impact: [description]
Next Update: [timestamp + 30min]

Status: https://status.ai-meal-planner.com
```

#### Incident Update

```
Subject: [INCIDENT UPDATE] Service Disruption - AI Meal Planner

Update: [description of progress]

Current Status: [In Progress/Implementing Fix/Testing/etc.]
Estimated Resolution: [time]
Next Update: [timestamp + 30min]
```

#### Incident Resolution

```
Subject: [RESOLVED] Service Disruption - AI Meal Planner

The issue affecting [service name] has been resolved.

Root Cause: [brief description]
Resolution: [what was done]
Resolved: [timestamp]

We apologize for any inconvenience. A detailed post-mortem
will be published within 48 hours.
```

## Post-Incident Review

### Timeline (Within 48 Hours of Resolution)

1. **Incident Log Compilation** (2 hours after resolution)
   - Gather all logs, metrics, and communications
   - Create timeline of events

2. **Team Debrief** (24 hours after resolution)
   - What happened?
   - What went well?
   - What could be improved?
   - Action items

3. **Post-Mortem Document** (48 hours after resolution)
   - Detailed incident analysis
   - Root cause analysis
   - Prevention measures
   - Process improvements

### Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

**Date**: [YYYY-MM-DD]
**Duration**: [X hours, Y minutes]
**Severity**: [Critical/High/Medium/Low]
**Impact**: [Number of users affected, services down]

## Summary
[Brief description of what happened]

## Timeline
- [HH:MM] Event 1
- [HH:MM] Event 2
...

## Root Cause
[Detailed analysis of what caused the incident]

## Resolution
[What was done to resolve the incident]

## Impact
- Users affected: [number]
- Data lost: [amount/timeframe]
- Revenue impact: [$amount]
- SLA breach: [Yes/No]

## What Went Well
- [Item 1]
- [Item 2]

## What Could Be Improved
- [Item 1]
- [Item 2]

## Action Items
- [ ] [Action 1] - Owner: [Name] - Due: [Date]
- [ ] [Action 2] - Owner: [Name] - Due: [Date]

## Lessons Learned
[Key takeaways for future incidents]
```

## Maintenance and Review

### Monthly Review

- Verify backup integrity
- Review backup retention policies
- Check backup storage costs
- Update contact information
- Review recent incidents

### Quarterly Review

- Conduct full DR drill
- Update RTOs and RPOs if needed
- Review and update procedures
- Train new team members
- Evaluate new backup technologies

### Annual Review

- Comprehensive DR plan review
- Update all documentation
- Full team training
- Conduct disaster simulation
- Review and renew insurance/SLAs

## Appendices

### Appendix A: Backup Storage Locations

```
Primary S3 Bucket:
  Name: ai-meal-planner-backups
  Region: us-east-1
  Encryption: AES-256
  Versioning: Enabled

DR S3 Bucket:
  Name: ai-meal-planner-backups-dr
  Region: us-west-2
  Encryption: AES-256
  Replication: Enabled from primary
```

### Appendix B: Required Credentials

**For Database Backup/Restore:**
- DATABASE_URL (from Railway)
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

**For Railway Access:**
- Railway API token
- Railway project ID

**For Vercel Access:**
- Vercel API token
- Vercel project ID

### Appendix C: Monitoring and Alerts

**Critical Alerts:**
- Database connection failures
- Backup failures
- Disk space > 80%
- Query performance degradation
- Replication lag > 1 minute

**Alert Channels:**
- PagerDuty (primary)
- Slack #alerts (secondary)
- Email (tertiary)

### Appendix D: Useful Commands

```bash
# Check database size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# List all tables and sizes
psql $DATABASE_URL -c "\dt+ "

# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Verify backup file
gzip -t backup.sql.gz

# Check Railway service status
railway status

# View Railway logs
railway logs --tail 100
```

---

**Document Version**: 1.0
**Last Updated**: 2025-01-15
**Next Review**: 2025-04-15
**Owner**: Backend Infrastructure Team
