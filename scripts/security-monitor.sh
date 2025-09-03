#!/bin/bash
# Security Monitoring Script

set -e

LOG_FILE="/app/logs/security-monitor.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# Check file permissions
check_permissions() {
    log "Checking file permissions..."

    # Check SSL certificates
    if [ -f "/app/nginx/ssl/cert.pem" ]; then
        perms=$(stat -c "%a" /app/nginx/ssl/cert.pem 2>/dev/null || stat -f "%A" /app/nginx/ssl/cert.pem)
        if [ "$perms" != "600" ]; then
            log "WARNING: SSL certificate permissions are $perms, should be 600"
        fi
    fi

    # Check database permissions
    if [ -f "/app/data/stock_analysis.db" ]; then
        perms=$(stat -c "%a" /app/data/stock_analysis.db 2>/dev/null || stat -f "%A" /app/data/stock_analysis.db)
        if [ "$perms" != "600" ]; then
            log "WARNING: Database permissions are $perms, should be 600"
        fi
    fi
}

# Check running processes
check_processes() {
    log "Checking running processes..."

    # Check for root processes (should be minimal)
    root_processes=$(ps aux | grep root | grep -v grep | wc -l)
    if [ "$root_processes" -gt 5 ]; then
        log "WARNING: High number of root processes detected: $root_processes"
    fi
}

# Check disk usage
check_disk_usage() {
    log "Checking disk usage..."

    usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$usage" -gt 90 ]; then
        log "WARNING: Disk usage is ${usage}%, consider cleanup"
    fi
}

# Check SSL certificate expiration
check_ssl_expiry() {
    if [ -f "/app/nginx/ssl/cert.pem" ]; then
        expiry=$(openssl x509 -in /app/nginx/ssl/cert.pem -enddate -noout | cut -d= -f2)
        expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry" +%s 2>/dev/null)
        now_epoch=$(date +%s)
        days_left=$(( (expiry_epoch - now_epoch) / 86400 ))

        if [ "$days_left" -lt 30 ]; then
            log "WARNING: SSL certificate expires in $days_left days"
        fi
    fi
}

# Main monitoring function
main() {
    log "Starting security monitoring check"

    check_permissions
    check_processes
    check_disk_usage
    check_ssl_expiry

    log "Security monitoring check completed"
}

# Run main function
main "$@"
