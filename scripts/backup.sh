#!/bin/bash

# Stock Analysis Platform Backup Script
# This script creates automated backups of user data and application state

set -e

# Configuration
BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
LOG_DIR="/app/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_RETENTION_DAYS=${RETENTION_DAYS:-30}
BACKUP_INTERVAL=${BACKUP_INTERVAL:-daily}

# Create backup directories
mkdir -p "$BACKUP_DIR/$BACKUP_INTERVAL"
mkdir -p "$LOG_DIR"

#!/bin/bash

# Stock Analysis Platform Backup Script
# This script creates automated backups of user data and application state

set -e

# Configuration
BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
LOG_DIR="/app/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_RETENTION_DAYS=${RETENTION_DAYS:-30}
BACKUP_INTERVAL=${BACKUP_INTERVAL:-daily}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create backup directories
mkdir -p "$BACKUP_DIR/$BACKUP_INTERVAL"
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_DIR/backup.log"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_DIR/backup.log"
}

error_exit() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_DIR/backup.log"
    exit 1
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $BACKUP_RETENTION_DAYS days"
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
}

# Backup SQLite database (if exists)
backup_database() {
    if [ -f "$DATA_DIR/stock_analysis.db" ]; then
        log "Backing up SQLite database"
        sqlite3 "$DATA_DIR/stock_analysis.db" ".backup '$BACKUP_DIR/$BACKUP_INTERVAL/database_$TIMESTAMP.db'" || error_exit "Database backup failed"

        # Also create a SQL dump for additional safety
        sqlite3 "$DATA_DIR/stock_analysis.db" .dump > "$BACKUP_DIR/$BACKUP_INTERVAL/database_dump_$TIMESTAMP.sql" || warn "SQL dump creation failed"
        log "Database SQL dump created"
    else
        log "No SQLite database found, skipping database backup"
    fi
}

# Backup application configuration and SSL certificates
backup_application_config() {
    log "Backing up application configuration"

    # Backup Docker configurations
    if [ -f "/app/docker-compose.yml" ]; then
        cp "/app/docker-compose.yml" "$BACKUP_DIR/$BACKUP_INTERVAL/"
    fi

    if [ -f "/app/docker-compose.prod.yml" ]; then
        cp "/app/docker-compose.prod.yml" "$BACKUP_DIR/$BACKUP_INTERVAL/"
    fi

    # Backup environment files (excluding sensitive data)
    if [ -f "/app/.env" ]; then
        # Create a sanitized version of .env for backup
        grep -v "SECRET\|PASSWORD\|KEY" "/app/.env" > "$BACKUP_DIR/$BACKUP_INTERVAL/env_backup_$TIMESTAMP.txt" 2>/dev/null || true
    fi

    # Backup nginx configuration and SSL certificates
    if [ -d "/app/nginx" ]; then
        cp -r "/app/nginx" "$BACKUP_DIR/$BACKUP_INTERVAL/"
        log "Nginx configuration and SSL certificates backed up"
    fi

    # Backup monitoring configuration
    if [ -d "/app/monitoring" ]; then
        cp -r "/app/monitoring" "$BACKUP_DIR/$BACKUP_INTERVAL/"
        log "Monitoring configuration backed up"
    fi

    # Backup scripts
    if [ -d "/app/scripts" ]; then
        cp -r "/app/scripts" "$BACKUP_DIR/$BACKUP_INTERVAL/"
        log "Scripts directory backed up"
    fi
}

# Backup user data and configurations
backup_user_data() {
    log "Backing up user data and configurations"

    # Create backup archive
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_INTERVAL/backup_$TIMESTAMP.tar.gz"

    # Create temporary directory for backup
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    # Copy data to temp directory
    if [ -d "$DATA_DIR" ]; then
        cp -r "$DATA_DIR" "$TEMP_DIR/"
    fi

    # Copy static files
    if [ -d "/app/static" ]; then
        cp -r "/app/static" "$TEMP_DIR/"
    fi

    # Add metadata
    echo "Backup created: $(date)" > "$TEMP_DIR/backup_info.txt"
    echo "Backup interval: $BACKUP_INTERVAL" >> "$TEMP_DIR/backup_info.txt"
    echo "Server: $(hostname)" >> "$TEMP_DIR/backup_info.txt"
    echo "Database backed up: $([ -f "$DATA_DIR/stock_analysis.db" ] && echo "Yes" || echo "No")" >> "$TEMP_DIR/backup_info.txt"

    # Create compressed archive
    tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" . || error_exit "Failed to create backup archive"

    log "Backup created: $BACKUP_FILE"
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    if [ -f "$backup_file" ]; then
        log "Verifying backup integrity: $backup_file"
        if tar -tzf "$backup_file" > /dev/null 2>&1; then
            log "Backup verification successful"
        else
            error_exit "Backup verification failed for $backup_file"
        fi
    fi
}

# Generate backup report
generate_backup_report() {
    local latest_backup=$(find "$BACKUP_DIR/$BACKUP_INTERVAL" -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    local backup_size="N/A"
    local db_size="N/A"

    if [ -n "$latest_backup" ] && [ -f "$latest_backup" ]; then
        backup_size=$(du -h "$latest_backup" | cut -f1)
    fi

    if [ -f "$DATA_DIR/stock_analysis.db" ]; then
        db_size=$(du -h "$DATA_DIR/stock_analysis.db" | cut -f1)
    fi

    cat > "$BACKUP_DIR/$BACKUP_INTERVAL/backup_report_$TIMESTAMP.txt" << EOF
Stock Analysis Platform - Backup Report
=======================================

Backup Details:
- Timestamp: $TIMESTAMP
- Backup Interval: $BACKUP_INTERVAL
- Latest Backup: $(basename "$latest_backup")
- Backup Size: $backup_size
- Database Size: $db_size
- Retention Policy: $BACKUP_RETENTION_DAYS days

System Information:
- Hostname: $(hostname)
- Server Time: $(date)
- Backup Directory: $BACKUP_DIR/$BACKUP_INTERVAL

Backup Contents:
- SQLite Database (if exists)
- Application Configuration
- Nginx Configuration & SSL Certificates
- Monitoring Configuration
- Scripts Directory
- User Data Directory
- Static Files

Next Scheduled Backup: $(date -v+1d +"%Y-%m-%d %H:%M:%S")

For restore instructions, see: /app/docs/backup-restore.md
EOF

    log "Backup report generated: $BACKUP_DIR/$BACKUP_INTERVAL/backup_report_$TIMESTAMP.txt"
}

# Send health check
health_check() {
    log "Backup process completed successfully"

    # Count total backups
    local total_backups=$(find "$BACKUP_DIR" -name "*.tar.gz" | wc -l)
    log "Total backups in system: $total_backups"

    # This could be extended to send notifications or update monitoring systems
}

# Main backup process
main() {
    log "Starting $BACKUP_INTERVAL backup process for Stock Analysis Platform"

    cleanup_old_backups
    backup_database
    backup_application_config
    backup_user_data
    generate_backup_report

    # Verify the latest backup
    LATEST_BACKUP=$(find "$BACKUP_DIR/$BACKUP_INTERVAL" -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    if [ -n "$LATEST_BACKUP" ]; then
        verify_backup "$LATEST_BACKUP"
    fi

    health_check
    log "Backup process completed successfully"
}

# Run main function
main "$@"
