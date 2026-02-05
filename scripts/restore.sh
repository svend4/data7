#!/bin/bash
###############################################################################
# Meta-Orchestrator Switchboard - Restore Script
#
# This script restores backups created by backup.sh
#
# Usage: ./restore.sh [options] BACKUP_FILE
#
# Options:
#   -t, --type TYPE      Restore type: db, redis, config (auto-detect if not specified)
#   -f, --force          Force restore without confirmation
#   -v, --verbose        Verbose output
#   -h, --help           Show this help
#
# Examples:
#   ./restore.sh db_20260205_120000.sql.gz       # Restore database
#   ./restore.sh --force redis_20260205_120000.rdb.gz  # Restore Redis (no confirm)
#   ./restore.sh --verbose config_20260205_120000.tar.gz  # Restore config
#
# WARNING: This will OVERWRITE existing data. Use with caution!
#
# Author: Data7 Team
# Version: 1.0
# Date: 2026-02-05
###############################################################################

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

RESTORE_TYPE=""
BACKUP_FILE=""
FORCE=false
VERBOSE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================================
# Functions
# ============================================================================

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

vlog() {
    if [ "$VERBOSE" = true ]; then
        log INFO "$@"
    fi
}

show_help() {
    sed -n '2,/^$/p' "$0" | sed 's/^# //; s/^#//'
    exit 0
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log ERROR "Required command not found: $1"
        exit 1
    fi
}

# Auto-detect backup type from filename
detect_backup_type() {
    local file=$1

    if [[ $file == *"db_"* ]]; then
        echo "db"
    elif [[ $file == *"redis_"* ]]; then
        echo "redis"
    elif [[ $file == *"config_"* ]]; then
        echo "config"
    else
        echo "unknown"
    fi
}

# Confirm restore operation
confirm_restore() {
    if [ "$FORCE" = true ]; then
        return 0
    fi

    echo ""
    log WARN "⚠️  WARNING: This will OVERWRITE existing data!"
    log WARN "Backup file: $BACKUP_FILE"
    log WARN "Restore type: $RESTORE_TYPE"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " response

    if [ "$response" != "yes" ]; then
        log INFO "Restore cancelled by user"
        exit 0
    fi
}

# Decompress file if needed
decompress_file() {
    local file=$1

    if [[ $file == *.gz ]]; then
        vlog "Decompressing $file..."
        local decompressed="${file%.gz}"

        if [ ! -f "$decompressed" ]; then
            gunzip -k "$file"
        fi

        echo "$decompressed"
    else
        echo "$file"
    fi
}

# Restore PostgreSQL database
restore_database() {
    log INFO "Starting database restore..."

    local backup_file=$1

    # Decompress if needed
    backup_file=$(decompress_file "$backup_file")

    if [ ! -f "$backup_file" ]; then
        log ERROR "Backup file not found: $backup_file"
        return 1
    fi

    # Stop backend services
    log WARN "Stopping backend services..."
    docker-compose -f docker-compose.phase9.yml stop backend celery_worker

    # Drop and recreate database
    vlog "Dropping existing database..."
    docker-compose -f docker-compose.phase9.yml exec -T postgres \
        psql -U switchboard -d postgres -c "DROP DATABASE IF EXISTS switchboard_prod;"

    vlog "Creating new database..."
    docker-compose -f docker-compose.phase9.yml exec -T postgres \
        psql -U switchboard -d postgres -c "CREATE DATABASE switchboard_prod OWNER switchboard;"

    # Restore from backup
    vlog "Restoring database from backup..."
    cat "$backup_file" | docker-compose -f docker-compose.phase9.yml exec -T postgres \
        psql -U switchboard -d switchboard_prod

    if [ $? -eq 0 ]; then
        log INFO "✓ Database restored successfully"

        # Restart services
        log INFO "Restarting backend services..."
        docker-compose -f docker-compose.phase9.yml start backend celery_worker

        return 0
    else
        log ERROR "✗ Database restore failed"
        return 1
    fi
}

# Restore Redis data
restore_redis() {
    log INFO "Starting Redis restore..."

    local backup_file=$1

    # Decompress if needed
    backup_file=$(decompress_file "$backup_file")

    if [ ! -f "$backup_file" ]; then
        log ERROR "Backup file not found: $backup_file"
        return 1
    fi

    # Stop Redis
    log WARN "Stopping Redis..."
    docker-compose -f docker-compose.phase9.yml stop redis

    # Replace dump file
    vlog "Replacing Redis dump file..."
    docker cp "$backup_file" $(docker-compose -f docker-compose.phase9.yml ps -q redis):/data/dump.rdb

    # Start Redis
    log INFO "Starting Redis..."
    docker-compose -f docker-compose.phase9.yml start redis

    # Wait for Redis to start
    sleep 3

    # Verify
    if docker-compose -f docker-compose.phase9.yml exec -T redis redis-cli PING | grep -q PONG; then
        log INFO "✓ Redis restored successfully"
        return 0
    else
        log ERROR "✗ Redis restore failed"
        return 1
    fi
}

# Restore configuration
restore_config() {
    log INFO "Starting configuration restore..."

    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        log ERROR "Backup file not found: $backup_file"
        return 1
    fi

    # Extract to temporary directory
    local temp_dir=$(mktemp -d)
    vlog "Extracting to temporary directory: $temp_dir"

    tar -xzf "$backup_file" -C "$temp_dir"

    # Copy files back
    vlog "Restoring configuration files..."

    if [ -f "$temp_dir/.env.production" ]; then
        cp "$temp_dir/.env.production" .env.production
        log INFO "Restored .env.production"
    fi

    if [ -f "$temp_dir/docker-compose.phase9.yml" ]; then
        cp "$temp_dir/docker-compose.phase9.yml" docker-compose.phase9.yml
        log INFO "Restored docker-compose.phase9.yml"
    fi

    if [ -d "$temp_dir/monitoring" ]; then
        cp -r "$temp_dir/monitoring/"* monitoring/
        log INFO "Restored monitoring configuration"
    fi

    # Cleanup
    rm -rf "$temp_dir"

    log INFO "✓ Configuration restored successfully"
    log WARN "Please review .env.production and restart services"

    return 0
}

# Verify backup file integrity
verify_backup_file() {
    local file=$1

    if [ ! -f "$file" ]; then
        log ERROR "Backup file not found: $file"
        return 1
    fi

    # Check if file is empty
    if [ ! -s "$file" ]; then
        log ERROR "Backup file is empty: $file"
        return 1
    fi

    # Check compressed files
    if [[ $file == *.gz ]]; then
        if ! gzip -t "$file" 2>/dev/null; then
            log ERROR "Backup file is corrupted (gzip test failed): $file"
            return 1
        fi
    fi

    # Check tar archives
    if [[ $file == *.tar.gz ]] || [[ $file == *.tar ]]; then
        if ! tar -tzf "$file" &>/dev/null; then
            log ERROR "Backup file is corrupted (tar test failed): $file"
            return 1
        fi
    fi

    vlog "Backup file integrity OK: $file"
    return 0
}

# Create restore point before restore
create_restore_point() {
    log INFO "Creating restore point..."

    local restore_point_dir="/var/backups/switchboard/restore_points"
    mkdir -p "$restore_point_dir"

    local timestamp=$(date +"%Y%m%d_%H%M%S")

    # Quick backup of current state
    if [ "$RESTORE_TYPE" = "db" ]; then
        docker-compose -f docker-compose.phase9.yml exec -T postgres \
            pg_dump -U switchboard switchboard_prod | \
            gzip > "${restore_point_dir}/pre_restore_db_${timestamp}.sql.gz"

        log INFO "Restore point created: pre_restore_db_${timestamp}.sql.gz"
    fi

    if [ "$RESTORE_TYPE" = "redis" ]; then
        docker-compose -f docker-compose.phase9.yml exec -T redis \
            redis-cli BGSAVE
        sleep 2
        docker-compose -f docker-compose.phase9.yml exec -T redis \
            cat /data/dump.rdb | \
            gzip > "${restore_point_dir}/pre_restore_redis_${timestamp}.rdb.gz"

        log INFO "Restore point created: pre_restore_redis_${timestamp}.rdb.gz"
    fi
}

# ============================================================================
# Main Restore Logic
# ============================================================================

main() {
    log INFO "Starting restore process..."

    # Auto-detect type if not specified
    if [ -z "$RESTORE_TYPE" ]; then
        RESTORE_TYPE=$(detect_backup_type "$BACKUP_FILE")
        log INFO "Auto-detected restore type: $RESTORE_TYPE"
    fi

    if [ "$RESTORE_TYPE" = "unknown" ]; then
        log ERROR "Could not determine restore type. Please specify with --type"
        exit 1
    fi

    # Verify backup file
    if ! verify_backup_file "$BACKUP_FILE"; then
        exit 1
    fi

    # Show summary
    echo ""
    log INFO "Restore Summary:"
    log INFO "  Type: $RESTORE_TYPE"
    log INFO "  Backup file: $BACKUP_FILE"
    log INFO "  File size: $(du -h "$BACKUP_FILE" | cut -f1)"
    echo ""

    # Confirm
    confirm_restore

    # Create restore point
    create_restore_point

    # Perform restore
    local success=true

    case $RESTORE_TYPE in
        db)
            restore_database "$BACKUP_FILE" || success=false
            ;;
        redis)
            restore_redis "$BACKUP_FILE" || success=false
            ;;
        config)
            restore_config "$BACKUP_FILE" || success=false
            ;;
        *)
            log ERROR "Unknown restore type: $RESTORE_TYPE"
            exit 1
            ;;
    esac

    # Summary
    echo ""
    if [ "$success" = true ]; then
        log INFO "✓ Restore completed successfully!"
        exit 0
    else
        log ERROR "✗ Restore failed"
        log WARN "You can rollback using the restore point created earlier"
        exit 1
    fi
}

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            RESTORE_TYPE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        -*)
            log ERROR "Unknown option: $1"
            show_help
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# Check if backup file specified
if [ -z "$BACKUP_FILE" ]; then
    log ERROR "No backup file specified"
    show_help
fi

# ============================================================================
# Prerequisites Check
# ============================================================================

check_command docker-compose
check_command gunzip
check_command tar

# ============================================================================
# Run Main
# ============================================================================

main
