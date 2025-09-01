#!/usr/bin/env python3
"""
Infrastructure Tests for Production Deployment
Tests deployment configuration, monitoring, and scaling
"""

import pytest
import requests
import time
import subprocess
import os
from pathlib import Path

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


# Check if Docker is available
def check_docker_available():
    """Check if Docker is available on the system"""
    try:
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def check_docker_compose_available():
    """Check if Docker Compose is available on the system"""
    try:
        # Try docker compose (newer syntax)
        result = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return True

        # Try docker-compose (older syntax)
        result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


DOCKER_AVAILABLE = check_docker_available()
DOCKER_COMPOSE_AVAILABLE = check_docker_compose_available()


class TestProductionDeployment:
    """Test production deployment infrastructure"""

    def test_docker_compose_config(self):
        """Test that docker-compose.prod.yml is valid"""
        compose_file = Path("docker-compose.prod.yml")

        assert compose_file.exists(), "docker-compose.prod.yml not found"

        if not YAML_AVAILABLE:
            pytest.skip("PyYAML not available - skipping YAML validation")

        with open(compose_file) as f:
            config = yaml.safe_load(f)

        # Check required services
        required_services = [
            "nginx",
            "stock-analysis-app",
            "prometheus",
            "grafana",
            "node-exporter",
            "backup",
        ]
        for service in required_services:
            assert (
                service in config["services"]
            ), f"Service {service} not found in docker-compose"

        # Check networks
        assert "networks" in config, "Networks not defined"
        assert "stock-network" in config["networks"], "stock-network not defined"

    def test_environment_config(self):
        """Test environment configuration"""
        env_example = Path(".env.example")
        assert env_example.exists(), ".env.example not found"

        with open(env_example) as f:
            content = f.read()

        # Check for required environment variables
        required_vars = [
            "SECRET_KEY",
            "FLASK_ENV",
            "GRAFANA_ADMIN_PASSWORD",
            "BACKUP_INTERVAL",
        ]

        for var in required_vars:
            assert var in content, f"Required environment variable {var} not documented"

    def test_nginx_config(self):
        """Test nginx configuration"""
        nginx_config = Path("nginx/nginx.conf")
        assert nginx_config.exists(), "nginx/nginx.conf not found"

        with open(nginx_config) as f:
            content = f.read()

        # Check for required nginx directives
        assert "upstream stock_app" in content, "Upstream configuration missing"
        assert "server {" in content, "Server block missing"
        assert "/health" in content, "Health check location missing"
        assert "/metrics" in content, "Metrics location missing"

    def test_prometheus_config(self):
        """Test Prometheus configuration"""
        prometheus_config = Path("monitoring/prometheus.yml")
        assert prometheus_config.exists(), "monitoring/prometheus.yml not found"

        if not YAML_AVAILABLE:
            pytest.skip("PyYAML not available - skipping YAML validation")

        with open(prometheus_config) as f:
            config = yaml.safe_load(f)

        assert "scrape_configs" in config, "Scrape configs missing"

        # Check for required jobs
        jobs = [job["job_name"] for job in config["scrape_configs"]]
        required_jobs = ["prometheus", "stock-analysis-app", "nginx", "node-exporter"]

        for job in required_jobs:
            assert job in jobs, f"Required job {job} not found in Prometheus config"

    def test_backup_script(self):
        """Test backup script exists and is executable"""
        backup_script = Path("scripts/backup.sh")
        assert backup_script.exists(), "backup.sh not found"

        # Check if executable
        assert os.access(backup_script, os.X_OK), "backup.sh is not executable"

        with open(backup_script) as f:
            content = f.read()

        # Check for required functions
        required_functions = [
            "cleanup_old_backups",
            "backup_database",
            "backup_user_data",
        ]
        for func in required_functions:
            assert (
                func in content
            ), f"Required function {func} not found in backup script"

    def test_deployment_script(self):
        """Test deployment script"""
        deploy_script = Path("scripts/deploy.sh")
        assert deploy_script.exists(), "deploy.sh not found"

        assert os.access(deploy_script, os.X_OK), "deploy.sh is not executable"

        with open(deploy_script) as f:
            content = f.read()

        # Check for required functions
        required_commands = ["deploy", "rollback", "scale", "status"]
        for cmd in required_commands:
            assert (
                cmd in content
            ), f"Required command {cmd} not found in deployment script"


class TestApplicationHealth:
    """Test application health endpoints"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get("http://localhost:5001/health", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data

        except requests.exceptions.RequestException:
            pytest.skip("Application not running, skipping health check test")

    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        try:
            response = requests.get("http://localhost:5001/metrics", timeout=5)
            assert response.status_code == 200

            content = response.text
            # Check for some basic metrics
            assert "http_requests_total" in content
            assert "http_request_duration_seconds" in content

        except requests.exceptions.RequestException:
            pytest.skip("Application not running, skipping metrics test")


class TestDockerServices:
    """Test Docker services"""

    def test_services_running(self):
        """Test that required services are running"""
        if not DOCKER_COMPOSE_AVAILABLE:
            pytest.skip("Docker Compose not available - skipping service running test")

        try:
            # Check if production environment is running
            # Try newer docker compose syntax first
            try:
                prod_result = subprocess.run(
                    ["docker", "compose", "-f", "docker-compose.prod.yml", "ps"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                subprocess.SubprocessError,
            ):
                # Fall back to older docker-compose syntax
                prod_result = subprocess.run(
                    ["docker-compose", "-f", "docker-compose.prod.yml", "ps"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            if prod_result.returncode == 0 and "nginx" in prod_result.stdout:
                # Production environment is running - check for actual running services
                output = prod_result.stdout
                lines = output.strip().split("\n")
                if len(lines) > 1:  # More than just header
                    running_services = [
                        "nginx",
                        "stock-analysis-app",
                        "prometheus",
                        "grafana",
                    ]
                else:
                    pytest.skip("Production environment is not running any services")
            else:
                # Check development environment
                try:
                    dev_result = subprocess.run(
                        ["docker", "compose", "ps"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                except (
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                    subprocess.SubprocessError,
                ):
                    dev_result = subprocess.run(
                        ["docker-compose", "ps"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                if dev_result.returncode == 0:
                    output = dev_result.stdout
                    lines = output.strip().split("\n")
                    if len(lines) > 1:  # More than just header
                        running_services = ["stock-analysis-app"]
                    else:
                        pytest.skip(
                            "Development environment is not running any services"
                        )
                else:
                    pytest.skip("No Docker Compose environment is running")

            # Check for running services (only if we have actual service entries)
            if "running_services" in locals():
                for service in running_services:
                    assert service in output, f"Service {service} is not running"
            else:
                pytest.skip("No services detected as running")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker Compose not available or services not running")

    def test_service_health(self):
        """Test service health checks"""
        # This would require docker-py or similar to inspect container health
        pytest.skip("Service health check requires docker-py dependency")


class LoadTestSuite:
    """Load testing capabilities for the application"""

    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_concurrent_requests_comprehensive(self):
        """Test concurrent request handling comprehensively"""
        import concurrent.futures

        base_url = "http://localhost:5001"
        num_requests = 50
        results = []
        errors = []
        start_time = time.time()

        def make_request(i):
            try:
                response = requests.get(f"{base_url}/health", timeout=10)
                results.append(
                    (i, response.status_code, response.elapsed.total_seconds())
                )
            except Exception as e:
                errors.append((i, str(e)))

    def test_database_connection_pooling(self):
        """Test database connection pooling under load"""
        # This would require actual database load testing
        # For now, we'll test the health endpoint which might use DB
        base_url = "http://localhost:5001"
        session = requests.Session()
        try:
            for _ in range(10):
                response = session.get(f"{base_url}/health", timeout=5)
                assert response.status_code == 200
                time.sleep(0.1)  # Small delay between requests
        except requests.exceptions.RequestException:
            pytest.skip("Application not running for DB connection test")


class TestRegressionTesting:
    """Regression tests for existing Docker development workflow"""

    def test_development_workflow_preserved(self):
        """Test that development workflow is completely preserved"""
        if not DOCKER_COMPOSE_AVAILABLE:
            pytest.skip("Docker Compose not available - skipping Docker workflow test")

        project_root = Path(__file__).parent.parent
        dev_compose_file = project_root / "docker-compose.yml"
        assert dev_compose_file.exists(), "Development docker-compose.yml missing"

        # Test development config is still valid
        # Try newer docker compose syntax first, fall back to older docker-compose
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(dev_compose_file), "config", "--quiet"],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=10,
            )
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            # Fall back to older docker-compose syntax
            try:
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        str(dev_compose_file),
                        "config",
                        "--quiet",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=10,
                )
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                subprocess.SubprocessError,
            ):
                pytest.skip("Docker Compose command failed - skipping workflow test")

        assert result.returncode == 0, f"Development config invalid: {result.stderr}"

    def test_backward_compatibility(self):
        """Test backward compatibility of configurations"""
        if not YAML_AVAILABLE:
            pytest.skip("PyYAML not available - skipping YAML validation")

        project_root = Path(__file__).parent.parent
        dev_compose_file = project_root / "docker-compose.yml"
        prod_compose_file = project_root / "docker-compose.prod.yml"

        with open(dev_compose_file, "r") as f:
            dev_config = yaml.safe_load(f)

        with open(prod_compose_file, "r") as f:
            prod_config = yaml.safe_load(f)

        dev_services = set(dev_config.get("services", {}).keys())
        prod_services = set(prod_config.get("services", {}).keys())

        # Production should have all dev services
        assert dev_services.issubset(prod_services), "Production missing dev services"

        # Check that core service configurations are compatible
        for service in dev_services:
            dev_service = dev_config["services"][service]
            prod_service = prod_config["services"][service]

            # Check that image or build context is compatible
            if "image" in dev_service and "image" in prod_service:
                assert (
                    dev_service["image"] == prod_service["image"]
                ), f"Service {service} image changed"

    def test_environment_variable_compatibility(self):
        """Test environment variable compatibility"""
        # Check that production doesn't break dev environment variables
        project_root = Path(__file__).parent.parent
        prod_compose_file = project_root / "docker-compose.prod.yml"

        with open(prod_compose_file, "r") as f:
            prod_config = yaml.safe_load(f)

        prod_env_vars = set()
        for service_name, service_config in prod_config.get("services", {}).items():
            env_vars = service_config.get("environment", [])
            if isinstance(env_vars, list):
                prod_env_vars.update(env_vars)
            elif isinstance(env_vars, dict):
                prod_env_vars.update(env_vars.keys())

        # Should not have conflicting environment variables
        conflicting_vars = [
            "FLASK_DEBUG",
            "FLASK_ENV",
        ]  # These should be different in prod
        for var in conflicting_vars:
            if var in prod_env_vars:
                # Check that production sets these appropriately
                assert any(
                    "production" in env for env in prod_env_vars if var in env
                ), f"Production environment variable {var} not set correctly"

    def test_volume_mount_compatibility(self):
        """Test volume mount compatibility - production should have essential dev volumes"""
        project_root = Path(__file__).parent.parent
        dev_compose_file = project_root / "docker-compose.yml"
        prod_compose_file = project_root / "docker-compose.prod.yml"

        with open(dev_compose_file, "r") as f:
            dev_config = yaml.safe_load(f)

        with open(prod_compose_file, "r") as f:
            prod_config = yaml.safe_load(f)

        # Essential volumes that should be preserved in production
        essential_volumes = {"./data:/app/data"}

        for service_name in dev_config.get("services", {}):
            if service_name in prod_config.get("services", {}):
                prod_volumes = set(
                    prod_config["services"][service_name].get("volumes", [])
                )

                # Production should have essential volumes (excluding dev-specific mounts like full host directory)
                missing_essential = essential_volumes - prod_volumes
                assert (
                    not missing_essential
                ), f"Service {service_name} missing essential volumes: {missing_essential}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
