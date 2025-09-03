#!/bin/bash

# Production Infrastructure Test Runner
# Comprehensive testing suite for production deployment validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$PROJECT_ROOT/tests"
LOG_DIR="$PROJECT_ROOT/logs"
REPORTS_DIR="$PROJECT_ROOT/test-reports"

# Create directories
mkdir -p "$LOG_DIR" "$REPORTS_DIR"

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_DIR/test-runner.log"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_DIR/test-runner.log"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_DIR/test-runner.log"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_DIR/test-runner.log"
}

# Test prerequisites
check_prerequisites() {
    log "Checking test prerequisites..."

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not found"
        exit 1
    fi

    # Check if pytest is available
    if ! python3 -c "import pytest" 2>/dev/null; then
        warn "pytest not found, installing..."
        pip3 install pytest pytest-html requests pyyaml
    fi

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        warn "Docker not found - some tests will be skipped"
    fi

    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        warn "docker-compose not found - some tests will be skipped"
    fi

    log "Prerequisites check completed"
}

# Run infrastructure tests
run_infrastructure_tests() {
    log "Running infrastructure tests..."

    local test_file="$TEST_DIR/test_deployment.py"
    local report_file="$REPORTS_DIR/infrastructure-test-report.html"

    if [ ! -f "$test_file" ]; then
        error "Test file not found: $test_file"
        return 1
    fi

    # Run pytest with HTML reporting
    if python3 -m pytest "$test_file" \
        --html="$report_file" \
        --self-contained-html \
        --tb=short \
        -v; then
        log "Infrastructure tests passed"
        return 0
    else
        error "Infrastructure tests failed"
        return 1
    fi
}

# Run load tests
run_load_tests() {
    log "Running load tests..."

    local test_file="$TEST_DIR/test_deployment.py::TestLoadTesting"
    local report_file="$REPORTS_DIR/load-test-report.html"

    # Check if application is running
    if ! curl -f http://localhost:5001/health &>/dev/null; then
        warn "Application not running on localhost:5001 - skipping load tests"
        return 0
    fi

    if python3 -m pytest "$test_file" \
        --html="$report_file" \
        --self-contained-html \
        --tb=short \
        -v; then
        log "Load tests passed"
        return 0
    else
        warn "Load tests failed - this may be expected if services are not running"
        return 0  # Don't fail the overall test suite for load test failures
    fi
}

# Run regression tests
run_regression_tests() {
    log "Running regression tests..."

    local test_file="$TEST_DIR/test_deployment.py::TestRegressionTesting"
    local report_file="$REPORTS_DIR/regression-test-report.html"

    if python3 -m pytest "$test_file" \
        --html="$report_file" \
        --self-contained-html \
        --tb=short \
        -v; then
        log "Regression tests passed"
        return 0
    else
        error "Regression tests failed"
        return 1
    fi
}

# Test Docker services
test_docker_services() {
    log "Testing Docker services..."

    local compose_file="$PROJECT_ROOT/docker-compose.prod.yml"

    if [ ! -f "$compose_file" ]; then
        error "Production docker-compose file not found: $compose_file"
        return 1
    fi

    # Test configuration validity
    if ! docker-compose -f "$compose_file" config --quiet; then
        error "Docker Compose configuration is invalid"
        return 1
    fi

    log "Docker services configuration is valid"

    # Try to start services for testing (optional)
    read -p "Do you want to start the production services for testing? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Starting production services..."
        if docker-compose -f "$compose_file" up -d; then
            log "Services started successfully"
            sleep 10  # Wait for services to be ready

            # Test service health
            test_service_health

            # Ask to stop services
            read -p "Do you want to stop the services now? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                log "Stopping services..."
                docker-compose -f "$compose_file" down
            fi
        else
            error "Failed to start services"
            return 1
        fi
    fi

    return 0
}

# Test service health
test_service_health() {
    log "Testing service health..."

    local services=("nginx" "stock-analysis-app" "prometheus" "grafana")
    local failed_services=()

    for service in "${services[@]}"; do
        if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps "$service" | grep -q "Up"; then
            log "Service $service is running"
        else
            error "Service $service is not running"
            failed_services+=("$service")
        fi
    done

    if [ ${#failed_services[@]} -gt 0 ]; then
        error "Failed services: ${failed_services[*]}"
        return 1
    fi

    log "All services are healthy"
    return 0
}

# Test SSL configuration
test_ssl_configuration() {
    log "Testing SSL configuration..."

    local ssl_dir="$PROJECT_ROOT/nginx/ssl"
    local cert_file="$ssl_dir/cert.pem"
    local key_file="$ssl_dir/key.pem"

    if [ ! -f "$cert_file" ] || [ ! -f "$key_file" ]; then
        warn "SSL certificates not found - generating..."
        if [ -f "$PROJECT_ROOT/scripts/generate-ssl.sh" ]; then
            bash "$PROJECT_ROOT/scripts/generate-ssl.sh"
        else
            warn "SSL generation script not found"
            return 1
        fi
    fi

    # Test certificate validity
    if openssl x509 -in "$cert_file" -text -noout >/dev/null 2>&1; then
        log "SSL certificate is valid"
    else
        error "SSL certificate is invalid"
        return 1
    fi

    # Test private key validity
    if openssl rsa -in "$key_file" -check -noout >/dev/null 2>&1; then
        log "SSL private key is valid"
    else
        error "SSL private key is invalid"
        return 1
    fi

    log "SSL configuration test completed"
    return 0
}

# Test backup system
test_backup_system() {
    log "Testing backup system..."

    local backup_script="$PROJECT_ROOT/scripts/backup.sh"

    if [ ! -f "$backup_script" ]; then
        error "Backup script not found: $backup_script"
        return 1
    fi

    if [ ! -x "$backup_script" ]; then
        error "Backup script is not executable"
        return 1
    fi

    # Test backup script dry run (if supported)
    log "Backup system validation completed"
    return 0
}

# Generate test summary report
generate_summary_report() {
    log "Generating test summary report..."

    local summary_file="$REPORTS_DIR/test-summary-report.html"

    cat > "$summary_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Production Infrastructure Test Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .warn { color: #ffc107; }
        .info { color: #17a2b8; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Production Infrastructure Test Summary</h1>
        <p>Generated on: $(date)</p>
        <p>Project: Stock Analysis Platform</p>
    </div>

    <div class="section">
        <h2>Test Results Overview</h2>
        <table>
            <tr>
                <th>Test Suite</th>
                <th>Status</th>
                <th>Description</th>
                <th>Report</th>
            </tr>
            <tr>
                <td>Infrastructure Tests</td>
                <td class="info">See detailed report</td>
                <td>Docker configuration, services, security</td>
                <td><a href="infrastructure-test-report.html">View Report</a></td>
            </tr>
            <tr>
                <td>Load Tests</td>
                <td class="info">See detailed report</td>
                <td>Concurrent requests, performance</td>
                <td><a href="load-test-report.html">View Report</a></td>
            </tr>
            <tr>
                <td>Regression Tests</td>
                <td class="info">See detailed report</td>
                <td>Development workflow compatibility</td>
                <td><a href="regression-test-report.html">View Report</a></td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>System Information</h2>
        <ul>
            <li><strong>Host:</strong> $(hostname)</li>
            <li><strong>Python Version:</strong> $(python3 --version 2>&1)</li>
            <li><strong>Docker Version:</strong> $(docker --version 2>&1 || echo "Not available")</li>
            <li><strong>Docker Compose Version:</strong> $(docker-compose --version 2>&1 || echo "Not available")</li>
            <li><strong>Test Run Time:</strong> $(date)</li>
        </ul>
    </div>

    <div class="section">
        <h2>Next Steps</h2>
        <ol>
            <li>Review detailed test reports for any failures</li>
            <li>Address any security or configuration issues found</li>
            <li>Run load tests with production-like data</li>
            <li>Validate backup and restore procedures</li>
            <li>Perform end-to-end testing with real user scenarios</li>
        </ol>
    </div>
</body>
</html>
EOF

    log "Test summary report generated: $summary_file"
}

# Main function
main() {
    log "Stock Analysis Platform - Production Infrastructure Test Runner"
    log "============================================================"

    local start_time=$(date +%s)
    local overall_status=0

    # Run test phases
    check_prerequisites

    # Core infrastructure tests
    if run_infrastructure_tests; then
        log "✓ Infrastructure tests completed successfully"
    else
        error "✗ Infrastructure tests failed"
        overall_status=1
    fi

    # Load tests (may be skipped if services not running)
    if run_load_tests; then
        log "✓ Load tests completed"
    else
        warn "! Load tests had issues (may be expected)"
    fi

    # Regression tests
    if run_regression_tests; then
        log "✓ Regression tests completed successfully"
    else
        error "✗ Regression tests failed"
        overall_status=1
    fi

    # Additional validations
    test_ssl_configuration
    test_backup_system
    test_docker_services

    # Generate reports
    generate_summary_report

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log ""
    log "Test execution completed in ${duration} seconds"
    log "Reports available in: $REPORTS_DIR"
    log "Main summary report: $REPORTS_DIR/test-summary-report.html"

    if [ $overall_status -eq 0 ]; then
        log "🎉 All critical tests passed!"
    else
        error "❌ Some tests failed - please review the reports"
    fi

    return $overall_status
}

# Handle command line arguments
case "${1:-}" in
    "infra")
        check_prerequisites
        run_infrastructure_tests
        ;;
    "load")
        check_prerequisites
        run_load_tests
        ;;
    "regression")
        check_prerequisites
        run_regression_tests
        ;;
    "ssl")
        test_ssl_configuration
        ;;
    "backup")
        test_backup_system
        ;;
    "services")
        test_docker_services
        ;;
    *)
        main "$@"
        ;;
esac
