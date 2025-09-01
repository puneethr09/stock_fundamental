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
import yaml
from pathlib import Path


class TestProductionDeployment:
    """Test production deployment infrastructure"""

    def test_docker_compose_config(self):
        """Test that docker-compose.prod.yml is valid"""
        compose_file = Path("docker-compose.prod.yml")

        assert compose_file.exists(), "docker-compose.prod.yml not found"

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
            response = requests.get("http://localhost:5000/health", timeout=5)
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
            response = requests.get("http://localhost:5000/metrics", timeout=5)
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
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.prod.yml", "ps"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            assert result.returncode == 0

            # Check for running services
            output = result.stdout
            running_services = ["nginx", "stock-analysis-app", "prometheus", "grafana"]

            for service in running_services:
                assert service in output, f"Service {service} is not running"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker Compose not available or services not running")

    def test_service_health(self):
        """Test service health checks"""
        # This would require docker-py or similar to inspect container health
        pytest.skip("Service health check requires docker-py dependency")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
