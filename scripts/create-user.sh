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
