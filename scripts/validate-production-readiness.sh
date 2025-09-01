#!/bin/bash

# Production Deployment Validation Script
# Quick health check for production readiness

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"

# Status tracking
CHECKS_PASSED=0
CHECKS_TOTAL=0
ISSUES_FOUND=()

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
    ISSUES_FOUND+=("$1")
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
    ISSUES_FOUND+=("$1")
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO: $1${NC}"
}

check_result() {
    local result=$1
    local message=$2
    ((CHECKS_TOTAL++))
    if [ $result -eq 0 ]; then
        log "✓ $message"
        ((CHECKS_PASSED++))
    else
        error "✗ $message"
    fi
}

# Check if file exists
check_file_exists() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        check_result 0 "$description found"
        return 0
    else
        check_result 1 "$description missing: $file"
        return 1
    fi
}

# Check if directory exists
check_dir_exists() {
    local dir=$1
    local description=$2
    if [ -d "$dir" ]; then
        check_result 0 "$description found"
        return 0
    else
        check_result 1 "$description missing: $dir"
        return 1
    fi
}

# Check if command exists
check_command_exists() {
    local cmd=$1
    local description=$2
    if command -v "$cmd" &> /dev/null; then
        check_result 0 "$description available"
        return 0
    else
        check_result 1 "$description not found"
        return 1
    fi
}

# Main validation function
main() {
    log "Stock Analysis Platform - Production Readiness Check"
    log "==================================================="

    # Prerequisites check
    info "Checking prerequisites..."

    check_command_exists "docker" "Docker"
    check_command_exists "docker-compose" "Docker Compose"
    check_command_exists "openssl" "OpenSSL"
    check_command_exists "python3" "Python 3"

    # File structure validation
    info "Validating file structure..."

    check_file_exists "$COMPOSE_FILE" "Production docker-compose.yml"
    check_file_exists "$PROJECT_ROOT/Dockerfile" "Main Dockerfile"
    check_file_exists "$PROJECT_ROOT/Dockerfile.backup" "Backup Dockerfile"
    check_file_exists "$PROJECT_ROOT/nginx/nginx.conf" "Nginx configuration"
    check_file_exists "$PROJECT_ROOT/monitoring/prometheus.yml" "Prometheus configuration"
    check_file_exists "$PROJECT_ROOT/monitoring/alertmanager.yml" "Alertmanager configuration"
    check_file_exists "$PROJECT_ROOT/scripts/backup.sh" "Backup script"
    check_file_exists "$PROJECT_ROOT/scripts/security-harden.sh" "Security hardening script"
    check_file_exists "$PROJECT_ROOT/.env.example" "Environment template"

    check_dir_exists "$PROJECT_ROOT/nginx/ssl" "SSL certificates directory"
    check_dir_exists "$PROJECT_ROOT/monitoring/grafana/dashboards" "Grafana dashboards"
    check_dir_exists "$PROJECT_ROOT/monitoring/grafana/provisioning" "Grafana provisioning"
    check_dir_exists "$PROJECT_ROOT/data" "Application data directory"
    check_dir_exists "$PROJECT_ROOT/backups" "Backup directory"
    check_dir_exists "$PROJECT_ROOT/logs" "Logs directory"

    # SSL certificates validation
    info "Validating SSL certificates..."

    if [ -f "$PROJECT_ROOT/nginx/ssl/cert.pem" ] && [ -f "$PROJECT_ROOT/nginx/ssl/key.pem" ]; then
        # Test certificate validity
        if openssl x509 -in "$PROJECT_ROOT/nginx/ssl/cert.pem" -text -noout >/dev/null 2>&1; then
            check_result 0 "SSL certificate is valid"
        else
            check_result 1 "SSL certificate is invalid"
        fi

        # Test private key validity
        if openssl rsa -in "$PROJECT_ROOT/nginx/ssl/key.pem" -check -noout >/dev/null 2>&1; then
            check_result 0 "SSL private key is valid"
        else
            check_result 1 "SSL private key is invalid"
        fi
    else
        check_result 1 "SSL certificates not found"
    fi

    # Docker Compose validation
    info "Validating Docker Compose configuration..."

    if [ -f "$COMPOSE_FILE" ]; then
        if docker-compose -f "$COMPOSE_FILE" config --quiet 2>/dev/null; then
            check_result 0 "Docker Compose configuration is valid"
        else
            check_result 1 "Docker Compose configuration is invalid"
        fi

        # Check required services
        if grep -q "stock-analysis-app:" "$COMPOSE_FILE" && \
           grep -q "nginx:" "$COMPOSE_FILE" && \
           grep -q "prometheus:" "$COMPOSE_FILE" && \
           grep -q "grafana:" "$COMPOSE_FILE"; then
            check_result 0 "All required services defined"
        else
            check_result 1 "Missing required services in docker-compose"
        fi
    fi

    # Security configuration validation
    info "Validating security configuration..."

    # Check security hardening script
    if [ -x "$PROJECT_ROOT/scripts/security-harden.sh" ]; then
        check_result 0 "Security hardening script is executable"
    else
        check_result 1 "Security hardening script not executable"
    fi

    # Check backup script
    if [ -x "$PROJECT_ROOT/scripts/backup.sh" ]; then
        check_result 0 "Backup script is executable"
    else
        check_result 1 "Backup script not executable"
    fi

    # Check for security headers configuration
    if [ -f "$PROJECT_ROOT/nginx/security-headers.conf" ]; then
        check_result 0 "Security headers configuration found"
    else
        check_result 1 "Security headers configuration missing"
    fi

    # Environment validation
    info "Validating environment configuration..."

    if [ -f "$PROJECT_ROOT/.env" ]; then
        check_result 0 "Environment file exists"
        # Check for critical environment variables
        if grep -q "SECRET_KEY" "$PROJECT_ROOT/.env" && \
           grep -q "GRAFANA_ADMIN_PASSWORD" "$PROJECT_ROOT/.env"; then
            check_result 0 "Critical environment variables set"
        else
            check_result 1 "Critical environment variables missing"
        fi
    else
        warn "Environment file (.env) not found - using defaults"
        check_result 0 "Environment template available (.env.example)"
    fi

    # Monitoring configuration validation
    info "Validating monitoring configuration..."

    if [ -f "$PROJECT_ROOT/monitoring/alert_rules.yml" ]; then
        check_result 0 "Alert rules configuration found"
    else
        check_result 1 "Alert rules configuration missing"
    fi

    # Generate summary
    log ""
    log "Validation Summary"
    log "=================="
    log "Checks passed: $CHECKS_PASSED/$CHECKS_TOTAL"

    local success_rate=$((CHECKS_PASSED * 100 / CHECKS_TOTAL))
    log "Success rate: ${success_rate}%"

    if [ ${#ISSUES_FOUND[@]} -gt 0 ]; then
        log ""
        warn "Issues found:"
        for issue in "${ISSUES_FOUND[@]}"; do
            echo "  - $issue"
        done
        log ""
        if [ $success_rate -ge 80 ]; then
            log "🎯 Production readiness: GOOD (${success_rate}% success rate)"
            log "   Minor issues found - review and fix before deployment"
        else
            error "❌ Production readiness: POOR (${success_rate}% success rate)"
            error "   Major issues found - fix before proceeding with deployment"
            exit 1
        fi
    else
        log ""
        log "🎉 Production readiness: EXCELLENT (100% success rate)"
        log "   All checks passed - ready for deployment!"
    fi

    log ""
    info "Next steps:"
    info "1. Review any warnings or errors above"
    info "2. Run comprehensive tests: ./scripts/run-infrastructure-tests.sh"
    info "3. Start services: docker-compose -f docker-compose.prod.yml up -d"
    info "4. Monitor services: docker-compose -f docker-compose.prod.yml logs -f"
}

# Run main function
main "$@"
