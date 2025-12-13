#!/bin/bash
#
# Database Backup Script for Railway PostgreSQL
#
# This script creates compressed backups of the PostgreSQL database
# and uploads them to a storage location. It's designed to run on
# Railway or any environment with access to the database.
#
# Requirements:
#   - PostgreSQL client tools (pg_dump)
#   - DATABASE_URL environment variable
#   - Write access to backup storage location
#
# Usage:
#   ./backup_database.sh [backup-name]
#
# Environment Variables:
#   DATABASE_URL      - PostgreSQL connection string (required)
#   BACKUP_DIR        - Directory to store backups (default: /tmp/backups)
#   BACKUP_RETENTION  - Days to retain backups (default: 30)
#   S3_BUCKET         - S3 bucket for backup storage (optional)
#   AWS_ACCESS_KEY_ID - AWS credentials (required if using S3)
#   AWS_SECRET_ACCESS_KEY - AWS credentials (required if using S3)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
BACKUP_RETENTION="${BACKUP_RETENTION:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${1:-backup_${TIMESTAMP}}"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Functions
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "INFO" "${GREEN}$@${NC}"
}

log_warn() {
    log "WARN" "${YELLOW}$@${NC}"
}

log_error() {
    log "ERROR" "${RED}$@${NC}"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump not found. Please install PostgreSQL client tools."
        exit 1
    fi

    if ! command -v gzip &> /dev/null; then
        log_error "gzip not found. Please install gzip."
        exit 1
    fi

    log_info "All dependencies satisfied"
}

check_database_url() {
    log_info "Checking database configuration..."

    if [ -z "${DATABASE_URL:-}" ]; then
        log_error "DATABASE_URL environment variable is not set"
        log_error "Please set DATABASE_URL to your PostgreSQL connection string"
        log_error "Example: postgresql://user:pass@host:5432/dbname"
        exit 1
    fi

    log_info "Database URL configured"
}

create_backup_directory() {
    if [ ! -d "${BACKUP_DIR}" ]; then
        log_info "Creating backup directory: ${BACKUP_DIR}"
        mkdir -p "${BACKUP_DIR}"
    fi
}

create_backup() {
    log_info "Starting database backup..."
    log_info "Backup file: ${BACKUP_FILE}"

    # Create backup using pg_dump
    # --no-owner: Don't output commands to set ownership
    # --no-acl: Don't output commands to set access privileges
    # --clean: Include commands to clean (drop) database objects before recreating them
    # --if-exists: Use IF EXISTS when dropping objects
    if pg_dump "${DATABASE_URL}" \
        --no-owner \
        --no-acl \
        --clean \
        --if-exists \
        --verbose \
        --file="${BACKUP_FILE}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_info "Database backup created successfully"
    else
        log_error "Database backup failed"
        exit 1
    fi
}

compress_backup() {
    log_info "Compressing backup..."

    if gzip -9 "${BACKUP_FILE}"; then
        local original_size=$(stat -f%z "${COMPRESSED_FILE}" 2>/dev/null || stat -c%s "${COMPRESSED_FILE}" 2>/dev/null)
        local size_mb=$((original_size / 1024 / 1024))
        log_info "Backup compressed successfully (${size_mb}MB)"
    else
        log_error "Backup compression failed"
        exit 1
    fi
}

upload_to_s3() {
    if [ -n "${S3_BUCKET:-}" ]; then
        log_info "Uploading backup to S3 bucket: ${S3_BUCKET}"

        if ! command -v aws &> /dev/null; then
            log_warn "AWS CLI not found. Skipping S3 upload."
            log_warn "Install AWS CLI to enable S3 backups: pip install awscli"
            return
        fi

        if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
            log_warn "AWS credentials not configured. Skipping S3 upload."
            log_warn "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
            return
        fi

        local s3_path="s3://${S3_BUCKET}/database-backups/${BACKUP_NAME}.sql.gz"

        if aws s3 cp "${COMPRESSED_FILE}" "${s3_path}" --storage-class STANDARD_IA; then
            log_info "Backup uploaded to S3: ${s3_path}"
        else
            log_error "Failed to upload backup to S3"
            # Don't exit - local backup still exists
        fi
    else
        log_info "S3_BUCKET not configured. Backup stored locally only."
    fi
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than ${BACKUP_RETENTION} days..."

    local deleted_count=0

    # Find and delete old local backups
    while IFS= read -r -d '' file; do
        log_info "Deleting old backup: $(basename "$file")"
        rm -f "$file"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime "+${BACKUP_RETENTION}" -print0)

    if [ $deleted_count -eq 0 ]; then
        log_info "No old backups to clean up"
    else
        log_info "Deleted ${deleted_count} old backup(s)"
    fi

    # Clean up old S3 backups if configured
    if [ -n "${S3_BUCKET:-}" ] && command -v aws &> /dev/null; then
        log_info "Cleaning up old S3 backups..."

        local cutoff_date=$(date -d "${BACKUP_RETENTION} days ago" +%Y-%m-%d 2>/dev/null || date -v-${BACKUP_RETENTION}d +%Y-%m-%d 2>/dev/null)

        if aws s3 ls "s3://${S3_BUCKET}/database-backups/" | \
           awk '{print $4}' | \
           while read -r filename; do
               if [ -n "$filename" ]; then
                   local file_date=$(echo "$filename" | grep -oE '[0-9]{8}' | head -1)
                   if [ -n "$file_date" ] && [ "$file_date" -lt "${cutoff_date//\-/}" ]; then
                       log_info "Deleting old S3 backup: $filename"
                       aws s3 rm "s3://${S3_BUCKET}/database-backups/$filename"
                   fi
               fi
           done; then
            log_info "S3 cleanup completed"
        else
            log_warn "S3 cleanup failed or no old backups found"
        fi
    fi
}

verify_backup() {
    log_info "Verifying backup integrity..."

    if gzip -t "${COMPRESSED_FILE}"; then
        log_info "Backup integrity verified successfully"
    else
        log_error "Backup integrity check failed!"
        exit 1
    fi
}

print_summary() {
    local backup_size=$(stat -f%z "${COMPRESSED_FILE}" 2>/dev/null || stat -c%s "${COMPRESSED_FILE}" 2>/dev/null)
    local size_mb=$((backup_size / 1024 / 1024))

    log_info "----------------------------------------"
    log_info "Backup Summary"
    log_info "----------------------------------------"
    log_info "Backup Name: ${BACKUP_NAME}"
    log_info "Backup File: ${COMPRESSED_FILE}"
    log_info "Backup Size: ${size_mb}MB"
    log_info "Timestamp: ${TIMESTAMP}"
    log_info "Retention: ${BACKUP_RETENTION} days"

    if [ -n "${S3_BUCKET:-}" ]; then
        log_info "S3 Bucket: ${S3_BUCKET}"
    else
        log_info "S3 Bucket: Not configured (local backup only)"
    fi

    log_info "----------------------------------------"
}

# Main execution
main() {
    log_info "========================================="
    log_info "Database Backup Script Starting"
    log_info "========================================="

    check_dependencies
    check_database_url
    create_backup_directory
    create_backup
    compress_backup
    verify_backup
    upload_to_s3
    cleanup_old_backups
    print_summary

    log_info "========================================="
    log_info "Database Backup Completed Successfully"
    log_info "========================================="
}

# Run main function
main "$@"
