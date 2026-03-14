#!/bin/bash
###############################################################################
# Meta-Orchestrator Switchboard - Automated Backup Script
#
# This script creates full backups of:
# - PostgreSQL database
# - Redis data
# - Application configuration
# - User uploads (if any)
#
# Usage: ./backup.sh [options]
#
# Options:
#   -t, --type TYPE      Backup type: full, db, redis, config (default: full)
#   -d, --dir DIR        Backup directory (default: /var/backups/switchboard)
#   -r, --retention DAYS Keep backups for N days (default: 30)
#   -c, --compress       Compress backups (default: yes)
#   -v, --verbose        Verbose output
#   -h, --help           Show this help
#
# Examples:
#   ./backup.sh                    # Full backup with defaults
#   ./backup.sh --type db          # Database only
#   ./backup.sh --retention 90     # Keep 90 days
#
# Author: Data7 Team
# Version: 1.0
# Date: 2026-02-05
###############################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ============================================================================
# Configuration
# ============================================================================

# Default values
BACKUP_TYPE="full"
BACKUP_DIR="/var/backups/switchboard"
RETENTION_DAYS=30
COMPRESS=true
VERBOSE=false

# Timestamp for backup filenames
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE=$(date +"%Y-%m-%d")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

# Print colored message
log() {
    local level=$1
    shift
    local message="$@"

    case $level in
        INFO)
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# Verbose log (only if VERBOSE=true)
vlog() {
    if [ "$VERBOSE" = true ]; then
        log INFO "$@"
    fi
}

# Show help
show_help() {
    sed -n '2,/^$/p' "$0" | sed 's/^# //; s/^#//'
    exit 0
}

# Check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log ERROR "Required command not found: $1"
        exit 1
    fi
}

# Create backup directory
create_backup_dir() {
    local dir=$1

    if [ ! -d "$dir" ]; then
        vlog "Creating backup directory: $dir"
        mkdir -p "$dir"
    fi

    # Set permissions
    chmod 700 "$dir"
}

# Backup PostgreSQL database
backup_database() {
    log INFO "Starting database backup..."

    local backup_file="${BACKUP_DIR}/db_${TIMESTAMP}.sql"

    # Get database credentials from docker-compose environment
    if command -v docker-compose &> /dev/null; then
        vlog "Using docker-compose for database backup"

        docker-compose -f docker-compose.phase9.yml exec -T postgres \
            pg_dump -U switchboard switchboard_prod > "$backup_file"
    else
        # Fallback to direct pg_dump
        vlog "Using direct pg_dump"

        pg_dump -h localhost -U switchboard -d switchboard_prod > "$backup_file"
    fi

    if [ $? -eq 0 ]; then
        log INFO "Database backup created: $backup_file"

        # Compress if enabled
        if [ "$COMPRESS" = true ]; then
            vlog "Compressing database backup..."
            gzip "$backup_file"
            backup_file="${backup_file}.gz"
            log INFO "Compressed to: $backup_file"
        fi

        # Calculate size
        local size=$(du -h "$backup_file" | cut -f1)
        log INFO "Backup size: $size"
    else
        log ERROR "Database backup failed"
        return 1
    fi
}

# Backup Redis data
backup_redis() {
    log INFO "Starting Redis backup..."

    local backup_file="${BACKUP_DIR}/redis_${TIMESTAMP}.rdb"

    if command -v docker-compose &> /dev/null; then
        vlog "Using docker-compose for Redis backup"

        # Trigger Redis BGSAVE
        docker-compose -f docker-compose.phase9.yml exec -T redis \
            redis-cli BGSAVE

        # Wait for save to complete
        sleep 2

        # Copy dump file
        docker-compose -f docker-compose.phase9.yml exec -T redis \
            cat /data/dump.rdb > "$backup_file"
    else
        # Fallback to direct redis-cli
        vlog "Using direct redis-cli"

        redis-cli BGSAVE
        sleep 2
        cp /var/lib/redis/dump.rdb "$backup_file"
    fi

    if [ $? -eq 0 ]; then
        log INFO "Redis backup created: $backup_file"

        # Compress if enabled
        if [ "$COMPRESS" = true ]; then
            vlog "Compressing Redis backup..."
            gzip "$backup_file"
            backup_file="${backup_file}.gz"
            log INFO "Compressed to: $backup_file"
        fi

        local size=$(du -h "$backup_file" | cut -f1)
        log INFO "Backup size: $size"
    else
        log ERROR "Redis backup failed"
        return 1
    fi
}

# Backup configuration files
backup_config() {
    log INFO "Starting configuration backup..."

    local backup_file="${BACKUP_DIR}/config_${TIMESTAMP}.tar.gz"

    # Files/directories to backup
    local config_files=(
        ".env.production"
        "docker-compose.phase9.yml"
        "alembic.ini"
        "monitoring/prometheus/prometheus.yml"
        "monitoring/grafana/datasources/"
        "monitoring/grafana/dashboards/"
    )

    # Create tar archive
    vlog "Archiving configuration files..."
    tar -czf "$backup_file" "${config_files[@]}" 2>/dev/null || true

    if [ -f "$backup_file" ]; then
        log INFO "Configuration backup created: $backup_file"
        local size=$(du -h "$backup_file" | cut -f1)
        log INFO "Backup size: $size"
    else
        log WARN "Configuration backup had issues (some files may be missing)"
    fi
}

# Remove old backups
cleanup_old_backups() {
    log INFO "Cleaning up backups older than $RETENTION_DAYS days..."

    local count=$(find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS | wc -l)

    if [ $count -gt 0 ]; then
        vlog "Found $count old backup(s) to remove"
        find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
        log INFO "Removed $count old backup(s)"
    else
        vlog "No old backups to remove"
    fi
}

# Create backup manifest
create_manifest() {
    local manifest_file="${BACKUP_DIR}/manifest_${DATE}.txt"

    vlog "Creating backup manifest..."

    {
        echo "Backup Manifest"
        echo "==============="
        echo "Date: $(date)"
        echo "Type: $BACKUP_TYPE"
        echo ""
        echo "Files:"
        ls -lh "${BACKUP_DIR}"/*_${TIMESTAMP}* 2>/dev/null || echo "No files"
    } > "$manifest_file"

    vlog "Manifest created: $manifest_file"
}

# Verify backup integrity
verify_backup() {
    log INFO "Verifying backup integrity..."

    local all_good=true

    # Check database backup
    if [ "$BACKUP_TYPE" = "full" ] || [ "$BACKUP_TYPE" = "db" ]; then
        local db_backup=$(ls "${BACKUP_DIR}"/db_${TIMESTAMP}* 2>/dev/null | head -1)

        if [ -n "$db_backup" ] && [ -f "$db_backup" ]; then
            # Check if file is not empty
            if [ -s "$db_backup" ]; then
                vlog "Database backup OK: $db_backup"
            else
                log ERROR "Database backup is empty: $db_backup"
                all_good=false
            fi
        else
            log WARN "Database backup not found"
            all_good=false
        fi
    fi

    # Check Redis backup
    if [ "$BACKUP_TYPE" = "full" ] || [ "$BACKUP_TYPE" = "redis" ]; then
        local redis_backup=$(ls "${BACKUP_DIR}"/redis_${TIMESTAMP}* 2>/dev/null | head -1)

        if [ -n "$redis_backup" ] && [ -f "$redis_backup" ]; then
            if [ -s "$redis_backup" ]; then
                vlog "Redis backup OK: $redis_backup"
            else
                log ERROR "Redis backup is empty: $redis_backup"
                all_good=false
            fi
        else
            log WARN "Redis backup not found"
            all_good=false
        fi
    fi

    if [ "$all_good" = true ]; then
        log INFO "Backup verification passed"
        return 0
    else
        log ERROR "Backup verification failed"
        return 1
    fi
}

# Send notification (email or webhook)
send_notification() {
    local status=$1
    local message=$2

    # Email notification (if configured)
    if [ -n "${BACKUP_EMAIL:-}" ]; then
        echo "$message" | mail -s "Switchboard Backup: $status" "$BACKUP_EMAIL"
    fi

    # Webhook notification (if configured)
    if [ -n "${BACKUP_WEBHOOK:-}" ]; then
        curl -X POST "$BACKUP_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"status\":\"$status\",\"message\":\"$message\"}" \
            &> /dev/null || true
    fi
}

# ============================================================================
# Main Backup Logic
# ============================================================================

main() {
    log INFO "Starting backup process..."
    log INFO "Backup type: $BACKUP_TYPE"
    log INFO "Backup directory: $BACKUP_DIR"
    log INFO "Retention: $RETENTION_DAYS days"

    # Create backup directory
    create_backup_dir "$BACKUP_DIR"

    # Perform backup based on type
    local success=true

    case $BACKUP_TYPE in
        full)
            backup_database || success=false
            backup_redis || success=false
            backup_config || success=false
            ;;
        db)
            backup_database || success=false
            ;;
        redis)
            backup_redis || success=false
            ;;
        config)
            backup_config || success=false
            ;;
        *)
            log ERROR "Unknown backup type: $BACKUP_TYPE"
            exit 1
            ;;
    esac

    # Create manifest
    create_manifest

    # Cleanup old backups
    cleanup_old_backups

    # Verify backup
    if ! verify_backup; then
        success=false
    fi

    # Summary
    echo ""
    if [ "$success" = true ]; then
        log INFO "✓ Backup completed successfully!"
        send_notification "SUCCESS" "Backup completed successfully at $(date)"
        exit 0
    else
        log ERROR "✗ Backup completed with errors"
        send_notification "FAILED" "Backup failed at $(date)"
        exit 1
    fi
}

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BACKUP_TYPE="$2"
            shift 2
            ;;
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            log ERROR "Unknown option: $1"
            show_help
            ;;
    esac
done

# ============================================================================
# Prerequisites Check
# ============================================================================

# Check required commands
check_command docker-compose
check_command gzip
check_command tar
check_command find

# ============================================================================
# Run Main
# ============================================================================

main
