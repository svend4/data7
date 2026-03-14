#!/bin/bash
###############################################################################
# Setup Automated Backup Cron Jobs
#
# This script sets up cron jobs for automated backups
#
# Usage: sudo ./setup-backup-cron.sh
#
# Backup Schedule:
#   - Full backup: Daily at 2:00 AM
#   - Database only: Every 6 hours
#   - Redis only: Every 12 hours
#   - Config: Weekly (Sunday 3:00 AM)
#
# Author: Data7 Team
# Version: 1.0
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root (use sudo)"
    exit 1
fi

# Get project directory
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT_DIR="$PROJECT_DIR/scripts"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"

log "Project directory: $PROJECT_DIR"
log "Backup script: $BACKUP_SCRIPT"

# Verify backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    error "Backup script not found: $BACKUP_SCRIPT"
    exit 1
fi

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"
log "Made backup script executable"

# Create cron jobs
CRON_FILE="/etc/cron.d/switchboard-backup"

log "Creating cron file: $CRON_FILE"

cat > "$CRON_FILE" << EOF
# Meta-Orchestrator Switchboard - Automated Backup Schedule
# Generated: $(date)

# Environment
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=admin@example.com

# Full backup - Daily at 2:00 AM
0 2 * * * root cd $PROJECT_DIR && $BACKUP_SCRIPT --type full --retention 30 >> /var/log/switchboard-backup.log 2>&1

# Database backup - Every 6 hours
0 */6 * * * root cd $PROJECT_DIR && $BACKUP_SCRIPT --type db --retention 7 >> /var/log/switchboard-backup.log 2>&1

# Redis backup - Every 12 hours
0 */12 * * * root cd $PROJECT_DIR && $BACKUP_SCRIPT --type redis --retention 7 >> /var/log/switchboard-backup.log 2>&1

# Configuration backup - Weekly (Sunday 3:00 AM)
0 3 * * 0 root cd $PROJECT_DIR && $BACKUP_SCRIPT --type config --retention 60 >> /var/log/switchboard-backup.log 2>&1
EOF

# Set permissions
chmod 644 "$CRON_FILE"
log "Cron file created with proper permissions"

# Create log file
touch /var/log/switchboard-backup.log
chmod 644 /var/log/switchboard-backup.log
log "Created log file: /var/log/switchboard-backup.log"

# Setup log rotation
LOGROTATE_FILE="/etc/logrotate.d/switchboard-backup"

log "Setting up log rotation: $LOGROTATE_FILE"

cat > "$LOGROTATE_FILE" << EOF
/var/log/switchboard-backup.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    postrotate
        systemctl reload cron > /dev/null 2>&1 || true
    endscript
}
EOF

chmod 644 "$LOGROTATE_FILE"
log "Log rotation configured"

# Reload cron
if systemctl is-active --quiet cron; then
    systemctl reload cron
    log "Cron service reloaded"
elif systemctl is-active --quiet crond; then
    systemctl reload crond
    log "Crond service reloaded"
else
    warn "Could not reload cron service. Please restart manually."
fi

# Summary
echo ""
log "✓ Automated backup setup complete!"
echo ""
log "Backup Schedule:"
log "  - Full backup:     Daily at 2:00 AM (retention: 30 days)"
log "  - Database backup: Every 6 hours (retention: 7 days)"
log "  - Redis backup:    Every 12 hours (retention: 7 days)"
log "  - Config backup:   Weekly, Sunday 3:00 AM (retention: 60 days)"
echo ""
log "Backup directory: /var/backups/switchboard"
log "Log file: /var/log/switchboard-backup.log"
echo ""
log "To view scheduled jobs:"
log "  crontab -l -u root | grep switchboard"
echo ""
log "To manually run a backup:"
log "  cd $PROJECT_DIR && sudo $BACKUP_SCRIPT"
echo ""

# Test backup script
read -p "Would you like to run a test backup now? (yes/no): " response
if [ "$response" = "yes" ]; then
    log "Running test backup..."
    cd "$PROJECT_DIR"
    "$BACKUP_SCRIPT" --type config
    log "Test backup complete!"
fi
