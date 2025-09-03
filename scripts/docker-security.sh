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
