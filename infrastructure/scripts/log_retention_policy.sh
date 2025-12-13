#!/bin/bash
#
# Log Retention Policy Script
# Manages log retention, rotation, and archival to S3
#
# This script should be run daily via cron: 0 2 * * * (2 AM daily)
#
# Retention policies:
# - Loki: 30 days (configured in loki-config.yml)
# - Prometheus: 30 days (configured in docker-compose.yml)
# - Application logs: 30 days (daily rotation, compress after 7 days)
# - Local archives: Delete after S3 upload (if S3 configured)
#

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
LOG_ARCHIVE_DIR="${LOG_ARCHIVE_DIR:-/var/log/recipe-app/archives}"
S3_BUCKET="${S3_BUCKET:-}"
AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
RETENTION_DAYS=30
COMPRESS_AFTER_DAYS=7
LOG_FILE="/var/log/log_retention.log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check if running in Docker container
if [ -f /.dockerenv ]; then
    log "Running inside Docker container"
    IS_DOCKER=true
else
    log "Running on host system"
    IS_DOCKER=false
fi

# Function to rotate and compress application logs
rotate_application_logs() {
    log "Starting application log rotation..."

    # Find logs older than COMPRESS_AFTER_DAYS and compress them
    if [ -d "/var/log/recipe-app" ]; then
        find /var/log/recipe-app -name "*.log" -type f -mtime +${COMPRESS_AFTER_DAYS} -not -name "*.gz" -exec gzip {} \; || true
        log "Compressed logs older than ${COMPRESS_AFTER_DAYS} days"
    else
        log "Application log directory /var/log/recipe-app does not exist"
    fi

    # Find compressed logs older than RETENTION_DAYS and delete them
    if [ -d "/var/log/recipe-app" ]; then
        local deleted_count=$(find /var/log/recipe-app -name "*.log.gz" -type f -mtime +${RETENTION_DAYS} -delete -print | wc -l)
        log "Deleted ${deleted_count} compressed logs older than ${RETENTION_DAYS} days"
    fi
}

# Function to clean up old backup archives
cleanup_old_backups() {
    log "Starting backup cleanup..."

    if [ ! -d "$BACKUP_DIR" ]; then
        log "Backup directory $BACKUP_DIR does not exist, skipping cleanup"
        return 0
    fi

    # Find and delete backups older than RETENTION_DAYS
    local deleted_count=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete -print | wc -l)
    log "Deleted ${deleted_count} backups older than ${RETENTION_DAYS} days"

    # Calculate backup directory size
    local backup_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    log "Current backup directory size: ${backup_size}"
}

# Function to archive logs to S3
archive_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3_BUCKET not configured, skipping S3 upload"
        return 0
    fi

    log "Starting S3 archive upload to s3://${S3_BUCKET}..."

    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        log "WARNING: AWS CLI not installed, skipping S3 upload"
        return 1
    fi

    # Create local archive directory if it doesn't exist
    mkdir -p "$LOG_ARCHIVE_DIR"

    # Archive compressed logs from the last 7 days to local directory first
    if [ -d "/var/log/recipe-app" ]; then
        find /var/log/recipe-app -name "*.log.gz" -type f -mtime -${COMPRESS_AFTER_DAYS} -mtime +1 -exec cp {} "$LOG_ARCHIVE_DIR/" \; || true
    fi

    # Upload local archives to S3
    if [ "$(ls -A $LOG_ARCHIVE_DIR 2>/dev/null)" ]; then
        local upload_date=$(date +%Y-%m-%d)
        aws s3 sync "$LOG_ARCHIVE_DIR" "s3://${S3_BUCKET}/logs/${upload_date}/" \
            --region "$AWS_REGION" \
            --storage-class STANDARD_IA \
            --quiet && {
            log "Successfully uploaded logs to S3"

            # Delete local archives after successful upload
            rm -f "$LOG_ARCHIVE_DIR"/*.gz
            log "Cleaned up local archive directory"
        } || {
            log "ERROR: Failed to upload logs to S3"
            return 1
        }
    else
        log "No local archives to upload to S3"
    fi

    # Upload database backups to S3
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR/*.sql.gz 2>/dev/null)" ]; then
        local backup_date=$(date +%Y-%m-%d)
        aws s3 sync "$BACKUP_DIR" "s3://${S3_BUCKET}/backups/${backup_date}/" \
            --region "$AWS_REGION" \
            --storage-class STANDARD_IA \
            --exclude "*" \
            --include "*.sql.gz" \
            --quiet && {
            log "Successfully uploaded database backups to S3"
        } || {
            log "ERROR: Failed to upload database backups to S3"
            return 1
        }
    fi
}

# Function to validate retention policy compliance
validate_retention() {
    log "Validating retention policy compliance..."

    # Check Loki retention (should be 30 days / 720h)
    if [ -f "/etc/loki/local-config.yaml" ]; then
        local loki_retention=$(grep "retention_period:" /etc/loki/local-config.yaml | head -1 | awk '{print $2}')
        if [ "$loki_retention" = "720h" ]; then
            log "✓ Loki retention is correctly set to 30 days (720h)"
        else
            log "✗ WARNING: Loki retention is $loki_retention, expected 720h"
        fi
    fi

    # Check Prometheus retention (should be 30d)
    if command -v docker &> /dev/null; then
        local prom_retention=$(docker inspect recipe-prometheus 2>/dev/null | grep -oP "storage.tsdb.retention.time=\K[^'\"]*" || echo "not found")
        if [ "$prom_retention" = "30d" ]; then
            log "✓ Prometheus retention is correctly set to 30 days"
        else
            log "✗ WARNING: Prometheus retention is $prom_retention, expected 30d"
        fi
    fi

    log "Retention policy validation complete"
}

# Function to generate retention report
generate_report() {
    log "Generating retention policy report..."

    local report_file="/tmp/log_retention_report_$(date +%Y%m%d).txt"

    cat > "$report_file" <<EOF
=================================================================
Log Retention Policy Report
Generated: $(date)
=================================================================

RETENTION POLICIES:
- Loki log retention: 30 days
- Prometheus metrics retention: 30 days
- Application logs: 30 days (compress after 7 days)
- Database backups: 30 days local, indefinite in S3

CURRENT STATUS:
EOF

    # Application logs
    if [ -d "/var/log/recipe-app" ]; then
        echo "" >> "$report_file"
        echo "Application Logs:" >> "$report_file"
        echo "  Total log files: $(find /var/log/recipe-app -name "*.log*" -type f | wc -l)" >> "$report_file"
        echo "  Compressed logs: $(find /var/log/recipe-app -name "*.log.gz" -type f | wc -l)" >> "$report_file"
        echo "  Total size: $(du -sh /var/log/recipe-app 2>/dev/null | cut -f1 || echo 'unknown')" >> "$report_file"
    fi

    # Database backups
    if [ -d "$BACKUP_DIR" ]; then
        echo "" >> "$report_file"
        echo "Database Backups:" >> "$report_file"
        echo "  Total backups: $(find $BACKUP_DIR -name "*.sql.gz" -type f | wc -l)" >> "$report_file"
        echo "  Total size: $(du -sh $BACKUP_DIR 2>/dev/null | cut -f1 || echo 'unknown')" >> "$report_file"
        echo "  Latest backup: $(ls -t $BACKUP_DIR/*.sql.gz 2>/dev/null | head -1 | xargs basename || echo 'none')" >> "$report_file"
    fi

    # S3 status
    echo "" >> "$report_file"
    if [ -n "$S3_BUCKET" ]; then
        echo "S3 Archive Status: Configured (bucket: $S3_BUCKET)" >> "$report_file"
    else
        echo "S3 Archive Status: Not configured" >> "$report_file"
    fi

    echo "" >> "$report_file"
    echo "=================================================================" >> "$report_file"

    cat "$report_file" | tee -a "$LOG_FILE"
    log "Report saved to $report_file"
}

# Main execution
main() {
    log "==================================================================="
    log "Starting log retention policy execution"
    log "==================================================================="

    # Rotate and compress application logs
    rotate_application_logs

    # Clean up old backups
    cleanup_old_backups

    # Archive to S3 if configured
    if [ -n "$S3_BUCKET" ]; then
        archive_to_s3 || log "WARNING: S3 archive failed, continuing..."
    fi

    # Validate retention policies
    validate_retention

    # Generate report
    generate_report

    log "==================================================================="
    log "Log retention policy execution completed successfully"
    log "==================================================================="
}

# Run main function
main "$@"
