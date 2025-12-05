# Database Backup & Migration Setup Guide

Complete setup and usage guide for database backups, migrations, and disaster recovery procedures.

## Overview

This guide covers:
- Database migration procedures (Alembic)
- Automated Railway backups to AWS S3
- Backup/restore testing
- Disaster recovery procedures

## Files Created

### 1. DATABASE_MIGRATION_GUIDE.md (983 lines)
**Location:** `/backend/docs/DATABASE_MIGRATION_GUIDE.md`

Comprehensive guide for database migrations including:
- Creating new migrations (autogenerate vs manual)
- Testing migrations locally (Docker, local PostgreSQL, pytest)
- Deploying to environments (dev/staging/production)
- Rolling back migrations
- Troubleshooting common issues
- Performance considerations
- Emergency procedures

**Quick Reference:**
```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Check status
alembic current
```

### 2. setup_railway_backups.sh (1004 lines)
**Location:** `/infrastructure/scripts/setup_railway_backups.sh`

Production-ready backup script with:
- Hourly automated backups to S3
- Intelligent retention (24 hourly, 30 daily, 90 weekly, 365 yearly)
- Cross-region replication
- AES-256 encryption
- Slack/email notifications
- Integrity verification
- Point-in-time recovery support

**Commands:**
```bash
# Setup (one-time)
./infrastructure/scripts/setup_railway_backups.sh --setup

# Create backup
./infrastructure/scripts/setup_railway_backups.sh --backup

# List backups
./infrastructure/scripts/setup_railway_backups.sh --list

# Restore backup
./infrastructure/scripts/setup_railway_backups.sh --restore hourly/backup_20251205_120000.sql.gz

# Verify configuration
./infrastructure/scripts/setup_railway_backups.sh --verify

# Dry run (test without changes)
./infrastructure/scripts/setup_railway_backups.sh --backup --dry-run
```

### 3. test_db_backup_restore.py (1003 lines)
**Location:** `/backend/tests/integration/test_db_backup_restore.py`

Comprehensive test suite covering:
- Backup creation and verification
- S3 upload validation
- Restore to clean database
- Schema and data integrity checks
- Point-in-time recovery
- Performance benchmarks
- Edge cases and error handling

**Run tests:**
```bash
cd backend
pytest tests/integration/test_db_backup_restore.py -v
```

---

## Installation & Setup

### Prerequisites

1. **PostgreSQL Client Tools:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Verify
pg_dump --version
psql --version
```

2. **AWS CLI:**
```bash
# Install
pip install awscli

# Configure
aws configure
# Enter: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region

# Verify
aws sts get-caller-identity
```

3. **Python Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

### Step 1: Configure Environment Variables

Create or update `.env` file:

```bash
# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# AWS Configuration (Required for backups)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-backup-bucket-name

# Backup Retention (Optional - defaults shown)
BACKUP_RETENTION_HOURS=24
BACKUP_RETENTION_DAYS=30
BACKUP_RETENTION_WEEKS=90
BACKUP_RETENTION_YEARS=365

# Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
NOTIFICATION_EMAIL=ops@yourdomain.com

# Cross-Region Replication (Optional)
REPLICA_REGION=us-west-2

# Logging (Optional)
VERBOSE=false
```

### Step 2: Set Up AWS S3 Bucket

#### Option A: Automatic Setup (Recommended)

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export S3_BUCKET_NAME=my-railway-backups
export AWS_REGION=us-east-1

# Run setup
./infrastructure/scripts/setup_railway_backups.sh --setup
```

This will:
- Create S3 bucket with versioning
- Enable AES-256 encryption
- Configure lifecycle policies
- Set up cross-region replication (if configured)

#### Option B: Manual Setup

1. **Create S3 Bucket:**
```bash
aws s3api create-bucket \
    --bucket my-railway-backups \
    --region us-east-1

# Or for regions other than us-east-1:
aws s3api create-bucket \
    --bucket my-railway-backups \
    --region us-west-2 \
    --create-bucket-configuration LocationConstraint=us-west-2
```

2. **Enable Versioning:**
```bash
aws s3api put-bucket-versioning \
    --bucket my-railway-backups \
    --versioning-configuration Status=Enabled
```

3. **Enable Encryption:**
```bash
aws s3api put-bucket-encryption \
    --bucket my-railway-backups \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
```

4. **Configure Lifecycle Policy:**
```bash
# Create lifecycle.json
cat > lifecycle.json <<EOF
{
    "Rules": [
        {
            "Id": "HourlyBackupRetention",
            "Status": "Enabled",
            "Filter": {"Prefix": "hourly/"},
            "Expiration": {"Days": 1},
            "Transitions": [{"Days": 1, "StorageClass": "STANDARD_IA"}]
        },
        {
            "Id": "DailyBackupRetention",
            "Status": "Enabled",
            "Filter": {"Prefix": "daily/"},
            "Expiration": {"Days": 30},
            "Transitions": [
                {"Days": 7, "StorageClass": "STANDARD_IA"},
                {"Days": 30, "StorageClass": "GLACIER"}
            ]
        },
        {
            "Id": "WeeklyBackupRetention",
            "Status": "Enabled",
            "Filter": {"Prefix": "weekly/"},
            "Expiration": {"Days": 90},
            "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]
        },
        {
            "Id": "YearlyBackupRetention",
            "Status": "Enabled",
            "Filter": {"Prefix": "yearly/"},
            "Expiration": {"Days": 365},
            "Transitions": [{"Days": 90, "StorageClass": "GLACIER"}]
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket my-railway-backups \
    --lifecycle-configuration file://lifecycle.json
```

### Step 3: Configure IAM Permissions

Create IAM user with required permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketVersioning",
                "s3:PutBucketVersioning"
            ],
            "Resource": [
                "arn:aws:s3:::my-railway-backups",
                "arn:aws:s3:::my-railway-backups/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ses:FromAddress": "noreply@yourdomain.com"
                }
            }
        }
    ]
}
```

### Step 4: Set Up Cron Job for Automated Backups

#### On Railway (using Railway CLI)

1. **Add environment variables to Railway service:**
```bash
railway variables set AWS_ACCESS_KEY_ID=your_key
railway variables set AWS_SECRET_ACCESS_KEY=your_secret
railway variables set S3_BUCKET_NAME=my-railway-backups
```

2. **Create cron service (if Railway supports cron jobs):**

Railway doesn't directly support cron jobs, so you have two options:

**Option A: External Cron (Recommended)**

Use a cron service like **Render Cron Jobs**, **EasyCron**, or **AWS EventBridge**:

```bash
# AWS EventBridge Schedule
aws events put-rule \
    --name railway-db-backup-hourly \
    --schedule-expression "rate(1 hour)"

# AWS Lambda function to trigger backup
# See: https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html
```

**Option B: Railway Background Worker**

Create a background worker that runs the backup script on a schedule:

```python
# backup_worker.py
import schedule
import time
import subprocess
import os

def run_backup():
    print("Running backup...")
    subprocess.run([
        "/app/infrastructure/scripts/setup_railway_backups.sh",
        "--backup"
    ])

# Run hourly
schedule.every().hour.do(run_backup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Add to `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
backup: python backup_worker.py
```

#### On Traditional Server (Linux)

```bash
# Edit crontab
crontab -e

# Add hourly backup (runs at minute 0 of every hour)
0 * * * * /home/user/project/infrastructure/scripts/setup_railway_backups.sh --backup >> /var/log/railway_backup.log 2>&1

# Or use absolute paths
0 * * * * cd /home/user/project && ./infrastructure/scripts/setup_railway_backups.sh --backup >> /var/log/railway_backup.log 2>&1
```

**Verify cron job:**
```bash
# List cron jobs
crontab -l

# Check cron logs
tail -f /var/log/railway_backup.log

# Or system cron log
tail -f /var/log/syslog | grep CRON
```

### Step 5: Test Backup System

#### Test 1: Verify Configuration
```bash
./infrastructure/scripts/setup_railway_backups.sh --verify
```

Expected output:
```
=== Checking Dependencies ===
✓ All dependencies satisfied

=== Checking Environment Variables ===
✓ All required environment variables set

Testing AWS credentials...
Testing S3 bucket access...
Testing database connection...

✓ All systems operational
```

#### Test 2: Dry Run
```bash
./infrastructure/scripts/setup_railway_backups.sh --backup --dry-run --verbose
```

#### Test 3: Create Test Backup
```bash
./infrastructure/scripts/setup_railway_backups.sh --backup
```

#### Test 4: List Backups
```bash
./infrastructure/scripts/setup_railway_backups.sh --list
```

#### Test 5: Restore Test
```bash
# Restore to local test database
export TEST_DB_NAME=recipe_app_restore_test
./infrastructure/scripts/setup_railway_backups.sh --restore hourly/railway_backup_20251205_120000.sql.gz
```

### Step 6: Run Test Suite

```bash
cd backend

# Set test database
export TEST_DB_NAME=recipe_app_test

# Run all backup/restore tests
pytest tests/integration/test_db_backup_restore.py -v

# Run specific test class
pytest tests/integration/test_db_backup_restore.py::TestBackupFunctionality -v

# Run with coverage
pytest tests/integration/test_db_backup_restore.py --cov=app --cov-report=html
```

---

## Usage Guide

### Creating Database Migrations

See [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md) for comprehensive documentation.

**Quick example:**
```bash
cd backend

# 1. Update SQLAlchemy models
# Edit app/models/user.py, add new column

# 2. Create migration
alembic revision --autogenerate -m "add user preferences"

# 3. Review generated migration
# Edit migrations/versions/XXX_add_user_preferences.py

# 4. Test locally
alembic upgrade head

# 5. Test rollback
alembic downgrade -1
alembic upgrade head

# 6. Deploy to production
# (See migration guide for production procedures)
```

### Manual Backups

```bash
# One-time backup
./infrastructure/scripts/setup_railway_backups.sh --backup

# Backup with custom name
export BACKUP_NAME="pre_migration_backup"
./infrastructure/scripts/backup_database.sh

# Check backup in S3
aws s3 ls s3://my-railway-backups/hourly/
```

### Restoring from Backup

#### Scenario 1: Restore Latest Backup

```bash
# List available backups
./infrastructure/scripts/setup_railway_backups.sh --list

# Restore latest
./infrastructure/scripts/setup_railway_backups.sh --restore hourly/railway_backup_20251205_180000.sql.gz
```

#### Scenario 2: Point-in-Time Recovery

```bash
# Find backup from specific time
aws s3 ls s3://my-railway-backups/daily/ | grep 20251204

# Download backup
aws s3 cp s3://my-railway-backups/daily/railway_backup_20251204_000000.sql.gz ./

# Restore
gunzip railway_backup_20251204_000000.sql.gz
psql $DATABASE_URL < railway_backup_20251204_000000.sql
```

#### Scenario 3: Emergency Production Restore

```bash
#!/bin/bash
# emergency_restore.sh

set -euo pipefail

echo "=== EMERGENCY PRODUCTION RESTORE ==="
echo "WARNING: This will overwrite production database!"
read -p "Continue? (type YES): " confirm

if [ "$confirm" != "YES" ]; then
    exit 1
fi

# 1. Enable maintenance mode
echo "Enabling maintenance mode..."
# curl -X POST https://api.yourapp.com/admin/maintenance/enable

# 2. Backup current state (just in case)
echo "Creating safety backup..."
./infrastructure/scripts/backup_database.sh "emergency_safety_backup"

# 3. Download restore point
echo "Downloading backup from S3..."
aws s3 cp s3://my-railway-backups/daily/railway_backup_TIMESTAMP.sql.gz ./

# 4. Restore
echo "Restoring database..."
gunzip -c railway_backup_TIMESTAMP.sql.gz | psql $DATABASE_URL

# 5. Verify
echo "Verifying restore..."
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"

# 6. Disable maintenance mode
echo "Disabling maintenance mode..."
# curl -X POST https://api.yourapp.com/admin/maintenance/disable

echo "=== RESTORE COMPLETE ==="
```

---

## Monitoring & Alerts

### Slack Notifications

Set up Slack webhook:

1. Go to https://api.slack.com/apps
2. Create new app → Incoming Webhooks
3. Add to workspace, select channel
4. Copy webhook URL

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Backup script will send notifications on:
- Backup success
- Backup failure
- Restore operations

### Email Notifications

Using AWS SES:

```bash
# Verify email address
aws ses verify-email-identity --email-address ops@yourdomain.com

# Set in environment
export NOTIFICATION_EMAIL=ops@yourdomain.com
```

### CloudWatch Metrics (Optional)

Set up custom metrics:

```bash
# Log backup metrics to CloudWatch
aws cloudwatch put-metric-data \
    --namespace DatabaseBackups \
    --metric-name BackupDuration \
    --value 45.2 \
    --unit Seconds

# Create alarm
aws cloudwatch put-metric-alarm \
    --alarm-name backup-failure-alert \
    --metric-name BackupDuration \
    --namespace DatabaseBackups \
    --statistic Maximum \
    --period 3600 \
    --evaluation-periods 1 \
    --threshold 300 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions arn:aws:sns:region:account:topic
```

---

## Troubleshooting

### Common Issues

#### 1. "pg_dump: command not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Verify
which pg_dump
```

#### 2. "AWS credentials not configured"

**Solution:**
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### 3. "S3 bucket not found"

**Solution:**
```bash
# Create bucket
./infrastructure/scripts/setup_railway_backups.sh --setup

# Or manually
aws s3api create-bucket --bucket your-bucket-name --region us-east-1
```

#### 4. "Database connection failed"

**Solution:**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Railway users: Get database URL
railway variables get DATABASE_URL
```

#### 5. Backup script permission denied

**Solution:**
```bash
chmod +x infrastructure/scripts/setup_railway_backups.sh
chmod +x infrastructure/scripts/backup_database.sh
chmod +x infrastructure/scripts/restore_database.sh
```

#### 6. Cron job not running

**Solution:**
```bash
# Check cron is running
sudo service cron status

# Check cron logs
tail -f /var/log/syslog | grep CRON

# Verify crontab entry
crontab -l

# Test script manually
/full/path/to/setup_railway_backups.sh --backup
```

### Getting Help

1. **Check logs:**
```bash
# Backup logs
ls -ltr /tmp/railway_backups/logs/

# View latest log
tail -f /tmp/railway_backups/logs/backup_*.log
```

2. **Run with verbose mode:**
```bash
export VERBOSE=true
./infrastructure/scripts/setup_railway_backups.sh --backup
```

3. **Verify configuration:**
```bash
./infrastructure/scripts/setup_railway_backups.sh --verify
```

---

## Security Best Practices

1. **Never commit AWS credentials to git**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use IAM roles instead of access keys (when possible)**
   ```bash
   # On EC2 instances, attach IAM role with S3 permissions
   # No need for AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY
   ```

3. **Enable S3 bucket encryption**
   - Automatically done by setup script
   - Uses AES-256 encryption

4. **Restrict S3 bucket access**
   - Use bucket policies
   - Enable versioning
   - Enable MFA delete for production

5. **Secure DATABASE_URL**
   - Use Railway secrets or environment variables
   - Never log full DATABASE_URL

6. **Regular security audits**
   ```bash
   # Check S3 bucket permissions
   aws s3api get-bucket-acl --bucket my-railway-backups

   # Review IAM permissions
   aws iam list-user-policies --user-name backup-user
   ```

---

## Performance Optimization

### Large Database Backups

For databases >10GB:

1. **Use parallel dumps (PostgreSQL 12+):**
```bash
pg_dump -j 4 $DATABASE_URL --format=directory --file=backup_dir
```

2. **Use incremental backups:**
```bash
# First: Full backup
pg_basebackup -D /backup/base -F tar -z -P

# Then: WAL archiving for incremental backups
# Configure in postgresql.conf
```

3. **Compress during backup:**
```bash
pg_dump $DATABASE_URL | gzip -9 > backup.sql.gz
```

### Restore Performance

1. **Disable constraints during restore:**
```sql
BEGIN;
SET session_replication_role = replica;
-- Restore data
SET session_replication_role = DEFAULT;
COMMIT;
```

2. **Increase PostgreSQL memory:**
```sql
SET maintenance_work_mem = '2GB';
SET shared_buffers = '4GB';
```

3. **Parallel restore (directory format):**
```bash
pg_restore -j 4 -d $DATABASE_URL backup_dir
```

---

## Disaster Recovery Plan

See [DISASTER_RECOVERY_PLAN.md](../../docs/DISASTER_RECOVERY_PLAN.md) for complete procedures.

**Quick Recovery Steps:**

1. **Database failure:**
   ```bash
   ./infrastructure/scripts/setup_railway_backups.sh --list
   ./infrastructure/scripts/setup_railway_backups.sh --restore <latest-backup>
   ```

2. **Data corruption:**
   ```bash
   # Restore to point before corruption
   ./infrastructure/scripts/setup_railway_backups.sh --restore daily/railway_backup_TIMESTAMP.sql.gz
   ```

3. **Region failure:**
   ```bash
   # Use replica bucket in different region
   export S3_BUCKET_NAME=my-railway-backups-replica
   ./infrastructure/scripts/setup_railway_backups.sh --restore <backup-file>
   ```

---

## Cost Estimation

### AWS S3 Costs (Approximate)

**Assumptions:**
- Database size: 1GB
- Hourly backups (compressed 50%): 500MB each
- Retention: 24 hourly, 30 daily, 12 weekly, 1 yearly

**Monthly costs:**
- Storage: ~15GB x $0.023/GB = $0.35
- Requests: ~720 PUTs x $0.005/1000 = $0.004
- Data transfer: ~1GB x $0.09/GB = $0.09
- **Total: ~$0.45/month**

For larger databases (10GB), costs scale proportionally: ~$4.50/month

**Cost optimization:**
- Use STANDARD_IA for files >30 days old (50% savings)
- Use Glacier for weekly/yearly backups (90% savings)
- Enable intelligent tiering

---

## Additional Resources

- [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md) - Complete migration procedures
- [DISASTER_RECOVERY_PLAN.md](../../docs/DISASTER_RECOVERY_PLAN.md) - DR procedures
- [Railway Documentation](https://docs.railway.app/) - Railway platform docs
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/) - S3 best practices
- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html) - pg_dump details

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs in `/tmp/railway_backups/logs/`
3. Run `--verify` to check configuration
4. Contact DevOps team

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0
