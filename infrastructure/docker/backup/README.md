# Database Backup Configuration

This directory contains configuration for the automated database backup service.

## Overview

The backup service runs as a Docker container that performs automated backups of the PostgreSQL database on a schedule defined in the crontab file.

## Files

- `crontab` - Cron schedule for automated backups
- `README.md` - This file

## Backup Schedule

The default backup schedule is:

- **Hourly**: Every hour (for RPO of 1 hour)
- **Daily**: Every day at 2:00 AM UTC
- **Weekly**: Every Sunday at 3:00 AM UTC
- **Monthly**: First day of month at 4:00 AM UTC

## Configuration

### Environment Variables

Configure these in your `.env` file or Railway environment:

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional - for local backups only
BACKUP_DIR=/backups
BACKUP_RETENTION=30  # Days to retain backups

# Optional - for S3 uploads
S3_BUCKET=my-backup-bucket
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## Usage

### Start Backup Service

```bash
cd infrastructure
docker-compose up -d db-backup
```

### View Backup Logs

```bash
docker logs -f recipe-db-backup
```

### List Backups

```bash
# Local backups
docker exec recipe-db-backup ls -lh /backups

# S3 backups (if configured)
aws s3 ls s3://my-backup-bucket/database-backups/
```

### Manual Backup

```bash
# Create a manual backup
docker exec recipe-db-backup /usr/local/bin/backup_database.sh manual_backup_$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup

```bash
# List available backups
docker exec recipe-db-backup ls -lh /backups

# Restore from local backup
docker exec -it recipe-db-backup /usr/local/bin/restore_database.sh /backups/backup_20250115_020000.sql.gz

# Restore from S3
docker exec -it recipe-db-backup /usr/local/bin/restore_database.sh s3://my-backup-bucket/database-backups/backup_20250115_020000.sql.gz
```

## Customizing Schedule

To modify the backup schedule, edit the `crontab` file and restart the backup service:

```bash
# Edit crontab
vim infrastructure/docker/backup/crontab

# Restart service
docker-compose restart db-backup
```

## Backup Storage

### Local Storage

Backups are stored in a Docker volume named `backup_data`. To access:

```bash
# View volume location
docker volume inspect infrastructure_backup_data

# Copy backup out of container
docker cp recipe-db-backup:/backups/backup_20250115_020000.sql.gz ./backup.sql.gz
```

### S3 Storage

If S3 is configured, backups are automatically uploaded to:

```
s3://{S3_BUCKET}/database-backups/
```

## Monitoring

### Check Backup Status

```bash
# View recent logs
docker exec recipe-db-backup tail -50 /backups/backup.log

# Check if cron is running
docker exec recipe-db-backup ps aux | grep crond

# List cron jobs
docker exec recipe-db-backup crontab -l
```

### Verify Backups

The backup script automatically verifies each backup after creation using `gzip -t`.

### Test Restore

It's recommended to test restore procedures monthly:

```bash
# Create a test database
docker-compose run --rm db psql -h db -U postgres -c "CREATE DATABASE test_restore;"

# Restore to test database
export DATABASE_URL="postgresql://postgres:postgres@db:5432/test_restore"
docker exec -e DATABASE_URL recipe-db-backup /usr/local/bin/restore_database.sh /backups/latest_backup.sql.gz

# Verify and clean up
docker-compose run --rm db psql -h db -U postgres -c "DROP DATABASE test_restore;"
```

## Troubleshooting

### Backups Not Running

1. Check cron daemon is running:
   ```bash
   docker exec recipe-db-backup ps aux | grep crond
   ```

2. Check cron logs:
   ```bash
   docker logs recipe-db-backup
   ```

3. Verify crontab syntax:
   ```bash
   docker exec recipe-db-backup crontab -l
   ```

### S3 Upload Failures

1. Verify AWS credentials:
   ```bash
   docker exec recipe-db-backup aws s3 ls s3://my-backup-bucket/
   ```

2. Check AWS CLI is installed:
   ```bash
   docker exec recipe-db-backup which aws
   ```

3. Review backup logs:
   ```bash
   docker exec recipe-db-backup cat /backups/backup.log
   ```

### Disk Space Issues

1. Check backup volume size:
   ```bash
   docker system df -v | grep backup_data
   ```

2. Manually clean old backups:
   ```bash
   docker exec recipe-db-backup find /backups -name "*.sql.gz" -mtime +30 -delete
   ```

3. Reduce BACKUP_RETENTION value

## Production Deployment

For Railway or other production environments:

1. **Set up S3 bucket**:
   ```bash
   aws s3 mb s3://ai-meal-planner-backups
   aws s3api put-bucket-versioning --bucket ai-meal-planner-backups --versioning-configuration Status=Enabled
   ```

2. **Configure environment variables** in Railway:
   - `S3_BUCKET`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

3. **Use Railway Cron** instead of Docker cron:
   - Create a separate Railway service for backups
   - Use Railway's built-in cron scheduling
   - Reference: https://docs.railway.app/reference/cron-jobs

4. **Set up monitoring**:
   - Configure alerts for backup failures
   - Monitor S3 bucket size and costs
   - Set up automated restore testing

## See Also

- [Database Migration Guide](../../../docs/DATABASE_MIGRATION_GUIDE.md)
- [Disaster Recovery Plan](../../../docs/DISASTER_RECOVERY_PLAN.md)
- [Backup Script](../../scripts/backup_database.sh)
- [Restore Script](../../scripts/restore_database.sh)
