#!/bin/bash

# Security Hardening Script for Stock Analysis Platform
# This script implements security best practices for Docker containers and the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root (for container security)
check_privileges() {
    if [ "$EUID" -eq 0 ]; then
        warn "Running as root - this should be avoided in production"
        warn "Consider using non-root user for better security"
    else
        log "Running as non-root user - good for security"
    fi
}

# Secure file permissions
secure_file_permissions() {
    log "Securing file permissions..."

    # Secure SSL certificates
    if [ -d "./nginx/ssl" ]; then
        chmod 600 ./nginx/ssl/*.pem 2>/dev/null || true
        chmod 755 ./nginx/ssl
        log "SSL certificate permissions secured"
    fi

    # Secure backup directory
    if [ -d "./backups" ]; then
        chmod 700 ./backups
        find ./backups -type f -exec chmod 600 {} \; 2>/dev/null || true
        log "Backup directory permissions secured"
    fi

    # Secure scripts
    if [ -d "./scripts" ]; then
        chmod 755 ./scripts/*.sh 2>/dev/null || true
        log "Script permissions secured"
    fi

    # Secure data directory
    if [ -d "./data" ]; then
        chmod 755 ./data
        find ./data -name "*.db" -exec chmod 600 {} \; 2>/dev/null || true
        log "Data directory permissions secured"
    fi
}

# Generate security headers configuration
generate_security_headers() {
    log "Generating security headers configuration..."

    cat > ./nginx/security-headers.conf << 'EOF'
# Security Headers Configuration
# Include this file in your nginx server blocks

# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;

# Enable XSS filtering
add_header X-XSS-Protection "1; mode=block" always;

# Referrer Policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;" always;

# HTTP Strict Transport Security (HSTS)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Prevent caching of sensitive content
add_header Cache-Control "no-cache, no-store, must-revalidate" always;
add_header Pragma "no-cache" always;
add_header Expires "0" always;
EOF

    log "Security headers configuration created: ./nginx/security-headers.conf"
}

# Create non-root user configuration
create_non_root_user() {
    log "Creating non-root user configuration..."

    cat > ./scripts/create-user.sh << 'EOF'
#!/bin/bash
# Create non-root user for running the application

set -e

# Create application user
groupadd -r stockapp 2>/dev/null || true
useradd -r -g stockapp -d /app -s /bin/bash stockapp 2>/dev/null || true

# Set ownership of application directory
chown -R stockapp:stockapp /app

# Create necessary directories with correct permissions
mkdir -p /app/data /app/backups /app/logs
chown -R stockapp:stockapp /app/data /app/backups /app/logs
chmod 755 /app/data /app/backups /app/logs

echo "Non-root user 'stockapp' created successfully"
EOF

    chmod +x ./scripts/create-user.sh
    log "Non-root user creation script created: ./scripts/create-user.sh"
}

# Generate Docker security configuration
generate_docker_security() {
    log "Generating Docker security configuration..."

    cat > ./scripts/docker-security.sh << 'EOF'
#!/bin/bash
# Docker Security Hardening Script

set -e

echo "Applying Docker security hardening..."

# Create Docker security options file
cat > docker-security.conf << 'SECURITY_EOF'
# Docker Security Configuration
# Add these options to your docker run commands or docker-compose.yml

# Security options for containers:
# --security-opt=no-new-privileges:true
# --security-opt=seccomp:unconfined (or use default profile)
# --cap-drop=ALL
# --cap-add=NET_BIND_SERVICE (if needed)
# --read-only
# --tmpfs /tmp:noexec,nosuid,size=100m

# For docker-compose.yml, add under service definition:
# security_opt:
#   - no-new-privileges:true
# cap_drop:
#   - ALL
# cap_add:
#   - NET_BIND_SERVICE
# read_only: true
# tmpfs:
#   - /tmp:noexec,nosuid,size=100m
#   - /var/run:noexec,nosuid,size=10m

echo "Docker security configuration created: docker-security.conf"
SECURITY_EOF

chmod +x docker-security.conf
echo "Docker security hardening applied"
EOF

    chmod +x ./scripts/docker-security.sh
    log "Docker security script created: ./scripts/docker-security.sh"
}

# Create environment security checklist
create_security_checklist() {
    log "Creating security checklist..."

    cat > ./docs/security-checklist.md << 'EOF'
# Security Checklist for Stock Analysis Platform

## Pre-Deployment Security Checks

### 1. SSL/TLS Configuration
- [ ] SSL certificates are properly installed
- [ ] Certificate chain is complete
- [ ] Private key permissions are 600
- [ ] Certificate expiration is monitored
- [ ] HSTS header is enabled
- [ ] SSL protocols are TLS 1.2/1.3 only

### 2. Container Security
- [ ] Non-root user is used in containers
- [ ] Minimal base images are used
- [ ] Security updates are applied
- [ ] Unnecessary packages are removed
- [ ] Container capabilities are dropped
- [ ] Read-only root filesystem where possible

### 3. Network Security
- [ ] Nginx is configured as reverse proxy
- [ ] Security headers are enabled
- [ ] Rate limiting is implemented
- [ ] Web Application Firewall (WAF) is considered
- [ ] Internal services are not exposed externally

### 4. Application Security
- [ ] Input validation is implemented
- [ ] SQL injection prevention is in place
- [ ] XSS protection is enabled
- [ ] CSRF protection is implemented
- [ ] Secure session management is used

### 5. Data Protection
- [ ] Database backups are encrypted
- [ ] Sensitive data is encrypted at rest
- [ ] Backup files have restricted permissions
- [ ] Database credentials are secured
- [ ] API keys are properly managed

### 6. Monitoring & Logging
- [ ] Security events are logged
- [ ] Log files are monitored
- [ ] Alert system is configured
- [ ] Regular security audits are scheduled

## Production Deployment Commands

```bash
# Run security hardening
./scripts/security-harden.sh

# Create non-root user
./scripts/create-user.sh

# Apply Docker security
./scripts/docker-security.sh

# Generate SSL certificates
./scripts/generate-ssl.sh

# Run backup
./scripts/backup.sh
```

## Security Best Practices

1. **Principle of Least Privilege**: Run services with minimal required permissions
2. **Defense in Depth**: Multiple layers of security controls
3. **Fail-Safe Defaults**: Deny by default, allow explicitly
4. **Regular Updates**: Keep all components updated
5. **Monitoring**: Continuous monitoring and alerting
6. **Backup Security**: Encrypt and secure backups

## Emergency Contacts

- Security Incident Response: [Contact Information]
- Infrastructure Team: [Contact Information]
- Development Team: [Contact Information]
EOF

    log "Security checklist created: ./docs/security-checklist.md"
}

# Create log rotation configuration
create_log_rotation() {
    log "Creating log rotation configuration..."

    cat > ./scripts/logrotate.conf << 'EOF'
/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 stockapp stockapp
    postrotate
        docker-compose restart nginx 2>/dev/null || true
    endscript
}

/app/logs/backup.log {
    weekly
    rotate 52
    compress
    delaycompress
    missingok
    notifempty
    create 644 stockapp stockapp
}
EOF

    log "Log rotation configuration created: ./scripts/logrotate.conf"
}

# Generate security monitoring script
create_security_monitor() {
    log "Creating security monitoring script..."

    cat > ./scripts/security-monitor.sh << 'EOF'
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
EOF

    chmod +x ./scripts/security-monitor.sh
    log "Security monitoring script created: ./scripts/security-monitor.sh"
}

# Main function
main() {
    log "Stock Analysis Platform - Security Hardening"
    log "==========================================="

    check_privileges
    secure_file_permissions
    generate_security_headers
    create_non_root_user
    generate_docker_security
    create_security_checklist
    create_log_rotation
    create_security_monitor

    log ""
    log "Security hardening completed successfully!"
    log ""
    info "Next steps:"
    info "1. Review and apply the security checklist: ./docs/security-checklist.md"
    info "2. Run the non-root user creation script: ./scripts/create-user.sh"
    info "3. Apply Docker security hardening: ./scripts/docker-security.sh"
    info "4. Set up log rotation with: ./scripts/logrotate.conf"
    info "5. Schedule security monitoring: ./scripts/security-monitor.sh"
}

# Run main function
main "$@"
