# Quick Start: Database Backup & Migration

## Database Migrations

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

Full guide: `/backend/docs/DATABASE_MIGRATION_GUIDE.md`

## Railway Backups Setup

### One-Time Setup
```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export S3_BUCKET_NAME="my-railway-backups"

# Run setup
./infrastructure/scripts/setup_railway_backups.sh --setup
```

### Daily Operations
```bash
# Create backup
./infrastructure/scripts/setup_railway_backups.sh --backup

# List backups
./infrastructure/scripts/setup_railway_backups.sh --list

# Restore
./infrastructure/scripts/setup_railway_backups.sh --restore hourly/backup.sql.gz
```

### Automated Backups (Cron)
```bash
# Add to crontab (runs hourly)
0 * * * * /path/to/setup_railway_backups.sh --backup >> /var/log/backup.log 2>&1
```

## Testing

```bash
cd backend
export TEST_DB_NAME=recipe_app_test
pytest tests/integration/test_db_backup_restore.py -v
```

## Documentation

- **DATABASE_MIGRATION_GUIDE.md** - Complete migration procedures (983 lines)
- **BACKUP_SETUP_README.md** - Full setup and usage guide (889 lines)
- **setup_railway_backups.sh** - Production backup script (1004 lines)
- **test_db_backup_restore.py** - Comprehensive tests (1003 lines)

## Emergency Procedures

### Restore Production Database
```bash
# 1. List backups
./infrastructure/scripts/setup_railway_backups.sh --list

# 2. Download latest
aws s3 cp s3://bucket/daily/railway_backup_TIMESTAMP.sql.gz ./

# 3. Restore
gunzip railway_backup_TIMESTAMP.sql.gz
psql $DATABASE_URL < railway_backup_TIMESTAMP.sql
```

### Rollback Migration
```bash
# Check current
alembic current

# Rollback one version
alembic downgrade -1

# Verify
alembic current
```

## Support

See `/backend/docs/BACKUP_SETUP_README.md` for:
- Troubleshooting
- AWS configuration
- Security best practices
- Performance optimization
