#!/bin/bash
# Stock Analysis Platform - Production Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: local, staging, production

set -e

# Handle command line arguments first
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [environment]"
    echo
    echo "Environments:"
    echo "  local      - Local development (default)"
    echo "  staging    - Staging environment"
    echo "  production - Production environment"
    echo
    echo "Examples:"
    echo "  $0              # Deploy to local"
    echo "  $0 production   # Deploy to production"
    echo "  $0 --help       # Show this help"
    exit 0
fi

# Set environment (default to local if not specified)
ENVIRONMENT=${1:-local}
PROJECT_NAME="stock-analysis-platform"
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo "Deploying $PROJECT_NAME to $ENVIRONMENT environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    print_status "Running pre-deployment checks..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your configuration before deploying!"
            exit 1
        else
            print_error ".env.example file not found!"
            exit 1
        fi
    fi

    print_status "Pre-deployment checks completed"
}

# Setup environment-specific configuration
setup_environment() {
    case $ENVIRONMENT in
        production)
            DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
            print_status "Using production configuration"
            ;;
        staging)
            DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
            print_status "Using staging configuration"
            ;;
        local)
            DOCKER_COMPOSE_FILE="docker-compose.yml"
            print_status "Using local development configuration"
            ;;
        *)
            print_error "Unknown environment: $ENVIRONMENT"
            print_status "Available environments: local, staging, production"
            exit 1
            ;;
    esac
}

# Deploy the application
deploy_application() {
    print_status "Starting deployment..."

    # Create necessary directories
    mkdir -p data logs backups

    # Pull latest images
    print_status "Pulling latest Docker images..."
    docker-compose -f $DOCKER_COMPOSE_FILE pull

    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose -f $DOCKER_COMPOSE_FILE down

    # Start services
    print_status "Starting services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d

    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30

    # Check health
    check_health
}

# Check application health
check_health() {
    print_status "Checking application health..."

    local health_url
    if [ "$ENVIRONMENT" = "local" ]; then
        health_url="http://localhost:5001/health"
    else
        health_url="http://localhost/health"
    fi

    # Try to connect to health endpoint
    if curl -f -s "$health_url" > /dev/null 2>&1; then
        print_status "Application is healthy!"
    else
        print_warning "Health check failed. Checking container status..."
        docker-compose -f $DOCKER_COMPOSE_FILE ps

        print_warning "You may need to check the logs:"
        echo "  docker-compose -f $DOCKER_COMPOSE_FILE logs -f stock-analysis-app"
    fi
}

# Show deployment information
show_deployment_info() {
    echo
    print_status "Deployment completed!"
    echo
    echo "Deployment Information:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Docker Compose File: $DOCKER_COMPOSE_FILE"
    if [ "$ENVIRONMENT" = "local" ]; then
        echo "  Application URL: http://localhost:5001"
        echo "  Health Check: http://localhost:5001/health"
    else
        echo "  Application URL: http://localhost (nginx proxy)"
        echo "  Health Check: http://localhost/health"
    fi
    echo
    echo "Useful Commands:"
    echo "  View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "  Stop app: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "  Restart app: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "  Update app: docker-compose -f $DOCKER_COMPOSE_FILE pull && docker-compose -f $DOCKER_COMPOSE_FILE up -d"
    echo
    print_status "Happy deploying!"
}

# Main deployment flow
main() {
    echo "Stock Analysis Platform Deployment Script"
    echo "========================================"
    echo

    pre_deployment_checks
    setup_environment
    deploy_application
    show_deployment_info
}

# Run main function
main
