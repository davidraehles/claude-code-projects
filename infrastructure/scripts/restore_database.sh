#!/bin/bash
#
# Database Restore Script for Railway PostgreSQL
#
# This script restores a PostgreSQL database from a compressed backup file.
# It can restore from local backups or download from S3.
#
# Requirements:
#   - PostgreSQL client tools (psql, pg_restore)
#   - DATABASE_URL environment variable
#   - Backup file (local or S3)
#
# Usage:
#   ./restore_database.sh <backup-file>
#   ./restore_database.sh s3://bucket/path/to/backup.sql.gz
#
# WARNING: This will DROP and recreate the database!
#          Make sure you have a recent backup before restoring!
#
# Environment Variables:
#   DATABASE_URL      - PostgreSQL connection string (required)
#   BACKUP_DIR        - Directory for temporary files (default: /tmp/backups)
#   AWS_ACCESS_KEY_ID - AWS credentials (required if using S3)
#   AWS_SECRET_ACCESS_KEY - AWS credentials (required if using S3)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
LOG_FILE="${BACKUP_DIR}/restore.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

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

log_prompt() {
    echo -e "${BLUE}$@${NC}"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v psql &> /dev/null; then
        log_error "psql not found. Please install PostgreSQL client tools."
        exit 1
    fi

    if ! command -v gunzip &> /dev/null; then
        log_error "gunzip not found. Please install gzip."
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

confirm_restore() {
    local backup_file=$1

    log_warn "========================================"
    log_warn "WARNING: DATABASE RESTORE"
    log_warn "========================================"
    log_warn "This will restore the database from:"
    log_warn "  ${backup_file}"
    log_warn ""
    log_warn "This operation will:"
    log_warn "  1. DROP all existing tables and data"
    log_warn "  2. Restore from the backup file"
    log_warn "  3. Cannot be undone"
    log_warn ""
    log_warn "Database URL: ${DATABASE_URL}"
    log_warn "========================================"
    log_warn ""

    log_prompt "Are you sure you want to continue? (yes/no): "
    read -r confirmation

    if [ "$confirmation" != "yes" ]; then
        log_info "Restore cancelled by user"
        exit 0
    fi

    log_prompt "Please type 'RESTORE' in all caps to confirm: "
    read -r confirmation2

    if [ "$confirmation2" != "RESTORE" ]; then
        log_info "Restore cancelled by user"
        exit 0
    fi

    log_info "Restore confirmed. Proceeding..."
}

download_from_s3() {
    local s3_path=$1
    local local_file="${BACKUP_DIR}/$(basename "$s3_path")"

    log_info "Downloading backup from S3: ${s3_path}"

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install: pip install awscli"
        exit 1
    fi

    if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
        log_error "AWS credentials not configured"
        log_error "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
        exit 1
    fi

    mkdir -p "${BACKUP_DIR}"

    if aws s3 cp "${s3_path}" "${local_file}"; then
        log_info "Backup downloaded successfully"
        echo "${local_file}"
    else
        log_error "Failed to download backup from S3"
        exit 1
    fi
}

decompress_backup() {
    local compressed_file=$1
    local decompressed_file="${compressed_file%.gz}"

    log_info "Decompressing backup..."
    log_info "Input: ${compressed_file}"
    log_info "Output: ${decompressed_file}"

    if [ ! -f "${compressed_file}" ]; then
        log_error "Backup file not found: ${compressed_file}"
        exit 1
    fi

    # Verify file integrity before decompressing
    if ! gzip -t "${compressed_file}"; then
        log_error "Backup file is corrupted or invalid"
        exit 1
    fi

    # Decompress
    if gunzip -c "${compressed_file}" > "${decompressed_file}"; then
        log_info "Backup decompressed successfully"
        echo "${decompressed_file}"
    else
        log_error "Failed to decompress backup"
        exit 1
    fi
}

create_backup_before_restore() {
    log_info "Creating safety backup of current database..."

    local safety_backup="${BACKUP_DIR}/pre_restore_backup_${TIMESTAMP}.sql.gz"

    # Check if backup script exists
    if [ -f "$(dirname "$0")/backup_database.sh" ]; then
        if bash "$(dirname "$0")/backup_database.sh" "pre_restore_backup_${TIMESTAMP}"; then
            log_info "Safety backup created: ${safety_backup}"
        else
            log_warn "Failed to create safety backup"
            log_prompt "Continue without safety backup? (yes/no): "
            read -r continue_anyway

            if [ "$continue_anyway" != "yes" ]; then
                log_info "Restore cancelled"
                exit 0
            fi
        fi
    else
        log_warn "Backup script not found. Skipping safety backup."
    fi
}

restore_database() {
    local backup_file=$1

    log_info "Starting database restore..."
    log_info "Backup file: ${backup_file}"

    if [ ! -f "${backup_file}" ]; then
        log_error "Backup file not found: ${backup_file}"
        exit 1
    fi

    # Restore using psql
    # The backup file should contain DROP and CREATE statements
    if psql "${DATABASE_URL}" < "${backup_file}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_info "Database restored successfully"
    else
        log_error "Database restore failed"
        log_error "Check log file for details: ${LOG_FILE}"
        exit 1
    fi
}

validate_restore() {
    log_info "Validating database restore..."

    # Test database connectivity
    if ! psql "${DATABASE_URL}" -c "SELECT 1;" &>/dev/null; then
        log_error "Cannot connect to database after restore"
        exit 1
    fi

    # Check if tables exist
    local table_count=$(psql "${DATABASE_URL}" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

    if [ -z "$table_count" ] || [ "$table_count" -eq 0 ]; then
        log_warn "No tables found in database. This might be expected if restoring an empty backup."
    else
        log_info "Found ${table_count} table(s) in database"
    fi

    # Run a simple query to verify data integrity
    log_info "Running data integrity check..."

    # This is a basic check - customize based on your schema
    if psql "${DATABASE_URL}" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5;" &>/dev/null; then
        log_info "Data integrity check passed"
    else
        log_warn "Data integrity check failed"
    fi

    log_info "Validation completed"
}

cleanup_temp_files() {
    local keep_compressed=$1
    shift
    local files=("$@")

    log_info "Cleaning up temporary files..."

    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            # Don't delete the original compressed backup
            if [ "$file" != "$keep_compressed" ]; then
                log_info "Deleting temporary file: $(basename "$file")"
                rm -f "$file"
            fi
        fi
    done
}

print_summary() {
    local backup_file=$1

    log_info "========================================"
    log_info "Restore Summary"
    log_info "========================================"
    log_info "Backup File: ${backup_file}"
    log_info "Database URL: ${DATABASE_URL}"
    log_info "Timestamp: ${TIMESTAMP}"
    log_info "Log File: ${LOG_FILE}"
    log_info "========================================"
    log_info ""
    log_info "Next steps:"
    log_info "1. Verify application functionality"
    log_info "2. Run data validation queries"
    log_info "3. Check application logs for errors"
    log_info "4. Test critical user workflows"
    log_info "========================================"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        log_error "Usage: $0 <backup-file>"
        log_error ""
        log_error "Examples:"
        log_error "  $0 /path/to/backup.sql.gz"
        log_error "  $0 s3://bucket/database-backups/backup.sql.gz"
        exit 1
    fi

    local input_file=$1
    local backup_file=""
    local decompressed_file=""
    local temp_files=()

    log_info "========================================"
    log_info "Database Restore Script Starting"
    log_info "========================================"

    check_dependencies
    check_database_url

    # Determine if input is S3 path or local file
    if [[ "$input_file" == s3://* ]]; then
        backup_file=$(download_from_s3 "$input_file")
        temp_files+=("$backup_file")
    else
        backup_file="$input_file"

        if [ ! -f "$backup_file" ]; then
            log_error "Backup file not found: ${backup_file}"
            exit 1
        fi
    fi

    confirm_restore "$backup_file"

    mkdir -p "${BACKUP_DIR}"

    create_backup_before_restore

    # Decompress if needed
    if [[ "$backup_file" == *.gz ]]; then
        decompressed_file=$(decompress_backup "$backup_file")
        temp_files+=("$decompressed_file")
    else
        decompressed_file="$backup_file"
    fi

    restore_database "$decompressed_file"
    validate_restore

    cleanup_temp_files "$backup_file" "${temp_files[@]}"

    print_summary "$backup_file"

    log_info "========================================"
    log_info "Database Restore Completed Successfully"
    log_info "========================================"
}

# Run main function
main "$@"
