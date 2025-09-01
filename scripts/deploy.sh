#!/bin/bash

# Production Deployment Script for Stock Analysis Platform
# This script handles deployment, scaling, and rollback operations

set -e

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="stock-analysis-prod"
BACKUP_DIR="./backups/pre-deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."

    # Check if docker and docker-compose are available
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    # Check if required files exist
    local required_files=("$COMPOSE_FILE" ".env" "Dockerfile.prod")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Required file $file not found"
            exit 1
        fi
    done

    # Check environment variables
    if [ -z "$SECRET_KEY" ]; then
        warn "SECRET_KEY environment variable not set"
    fi

    log "Pre-deployment checks completed"
}

# Create backup before deployment
create_backup() {
    log "Creating pre-deployment backup..."

    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"

    # Backup current data and configurations
    if [ -d "./data" ]; then
        tar -czf "$backup_file" ./data/ ./logs/ 2>/dev/null || true
        log "Backup created: $backup_file"
    else
        warn "No data directory found to backup"
    fi
}

# Deploy the application
deploy() {
    log "Starting deployment..."

    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" pull

    # Start services
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d

    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30

    # Check service health
    check_health

    log "Deployment completed successfully"
}

# Check service health
check_health() {
    log "Checking service health..."

    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log "Health check attempt $attempt/$max_attempts"

        # Check if all services are running
        if docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps | grep -q "Exit"; then
            error "Some services failed to start"
            show_logs
            exit 1
        fi

        # Check application health endpoint
        if curl -f http://localhost/health >/dev/null 2>&1; then
            log "Application health check passed"
            return 0
        fi

        sleep 10
        ((attempt++))
    done

    error "Health check failed after $max_attempts attempts"
    show_logs
    exit 1
}

# Show service logs
show_logs() {
    log "Showing recent service logs..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs --tail=50
}

# Rollback deployment
rollback() {
    log "Rolling back deployment..."

    # Stop current deployment
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down

    # Restore from backup if needed
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        local latest_backup=$(ls -t "$BACKUP_DIR"/*.tar.gz | head -1)
        if [ -f "$latest_backup" ]; then
            log "Restoring from backup: $latest_backup"
            tar -xzf "$latest_backup" -C ./
        fi
    fi

    # Restart with previous configuration
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d

    log "Rollback completed"
}

# Scale services
scale_services() {
    local service=$1
    local replicas=$2

    if [ -z "$service" ] || [ -z "$replicas" ]; then
        error "Usage: $0 scale <service> <replicas>"
        exit 1
    fi

    log "Scaling $service to $replicas replicas"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --scale "$service=$replicas"
}

# Show status
show_status() {
    log "Current deployment status:"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    echo ""
    log "Service health:"
    curl -s http://localhost/health || echo "Health check failed"
}

# Main function
main() {
    local command=$1

    case $command in
        "deploy")
            pre_deployment_checks
            create_backup
            deploy
            ;;
        "rollback")
            rollback
            ;;
        "scale")
            scale_services "$2" "$3"
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|scale|status|logs}"
            echo ""
            echo "Commands:"
            echo "  deploy              Deploy the application"
            echo "  rollback            Rollback to previous deployment"
            echo "  scale <service> <n> Scale a service to n replicas"
            echo "  status              Show deployment status"
            echo "  logs                Show service logs"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
