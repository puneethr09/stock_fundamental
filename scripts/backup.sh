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

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/backup.log"
}

# Error handling
error_exit() {
    log "ERROR: $1"
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
    else
        log "No SQLite database found, skipping database backup"
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

    # Add metadata
    echo "Backup created: $(date)" > "$TEMP_DIR/backup_info.txt"
    echo "Backup interval: $BACKUP_INTERVAL" >> "$TEMP_DIR/backup_info.txt"
    echo "Server: $(hostname)" >> "$TEMP_DIR/backup_info.txt"

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

# Send health check
health_check() {
    log "Backup process completed successfully"
    # This could be extended to send notifications or update monitoring systems
}

# Main backup process
main() {
    log "Starting $BACKUP_INTERVAL backup process"

    cleanup_old_backups
    backup_database
    backup_user_data

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
