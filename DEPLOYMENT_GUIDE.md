# 🚀 Stock Analysis Platform - Deployment Guide

## Quick Start (Local Development)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your API keys and secrets

# 2. Deploy locally
docker-compose up -d

# 3. Access your app
open http://localhost:5001

# 4. Check health
curl http://localhost:5001/health
```

## Production Deployment Options

### Option 1: DigitalOcean Droplet (Recommended for Beginners)

```bash
# 1. Create Ubuntu 22.04 droplet (2GB RAM, 1 CPU)
# 2. SSH into your droplet
ssh root@your-droplet-ip

# 3. Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone and deploy
git clone https://github.com/yourusername/stock_fundamental.git
cd stock_fundamental
cp .env.example .env
# Edit .env with production values

# 5. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 6. Access your application
# HTTP: http://your-droplet-ip
# Health: http://your-droplet-ip/health

# 7. Setup domain (optional)
# Point your domain to the droplet IP
```

### Option 2: AWS EC2 with Load Balancer

```bash
# 1. Launch EC2 instance (t3.medium, Ubuntu)
# 2. Configure security groups (ports 80, 443, 22)
# 3. SSH and install Docker
# 4. Deploy application
docker-compose -f docker-compose.prod.yml up -d

# 5. Setup Application Load Balancer
# - Create ALB with SSL certificate
# - Configure health checks
# - Point domain to ALB
```

### Option 3: Google Cloud Run (Serverless)

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/stock-analysis

# 2. Deploy to Cloud Run
gcloud run deploy stock-analysis \
  --image gcr.io/PROJECT-ID/stock-analysis \
  --platform managed \
  --port 5001 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

### Option 4: Heroku (Simple)

```bash
# 1. Install Heroku CLI
# 2. Create Heroku app
heroku create your-app-name

# 3. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# 4. Deploy
git push heroku main
```

## Port Configuration

### Local Development

- **Flask App**: `http://localhost:5001`
- **Health Check**: `http://localhost:5001/health`
- **Direct access** to Flask application

### Production Deployment

- **Nginx Proxy**: `http://yourdomain.com` (port 80)
- **SSL/HTTPS**: `https://yourdomain.com` (port 443)
- **Health Check**: `https://yourdomain.com/health`
- **Flask app runs internally** on port 5001, proxied through Nginx

### Port Mapping Summary

```
Local Development:
┌─────────────┐    ┌─────────────┐
│   Browser   │───▶│  Flask App  │
│             │    │  Port 5001  │
└─────────────┘    └─────────────┘

Production:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │───▶│   Nginx     │───▶│  Flask App  │
│             │    │ Port 80/443 │    │  Port 5001  │
└─────────────┘    └─────────────┘    └─────────────┘
```

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-super-secret-key-change-this

# API Keys
NEWS_API_KEY=your-news-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# Database
DATABASE_PATH=/app/data/stock_analysis.db

# SSL (for HTTPS)
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

## SSL Certificate Setup

### Using Let's Encrypt (Free)

```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/key.pem
```

## Monitoring & Maintenance

### Health Checks

- Application: `https://yourdomain.com/health`
- Nginx: Check logs in `./logs/nginx/`
- Prometheus: `http://your-server:9090`

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 /app/data/stock_analysis.db ".backup /app/backups/stock_analysis_$DATE.db"
find /app/backups -name "*.db" -mtime +30 -delete
```

### Logs

- Application logs: `./logs/app.log`
- Nginx logs: `./logs/nginx/`
- Docker logs: `docker-compose logs -f`

## Scaling Options

### Horizontal Scaling (Multiple Instances)

```yaml
# In docker-compose.prod.yml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: "0.5"
      memory: 512M
```

### Database Scaling

- For high traffic: Migrate to PostgreSQL
- Use connection pooling
- Implement database replication

## Troubleshooting

### Common Issues

1. **Port 80/443 already in use**

   ```bash
   sudo netstat -tulpn | grep :80
   sudo systemctl stop apache2  # or nginx
   ```

2. **SSL certificate errors**

   ```bash
   sudo certbot certificates
   sudo certbot renew
   ```

3. **Memory issues**

   ```bash
   docker stats
   # Increase instance size or optimize app
   ```

4. **Database locked**
   ```bash
   # Check database connections
   lsof /app/data/stock_analysis.db
   ```

## Performance Optimization

### Nginx Tuning

```nginx
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 100M;
```

### Flask Optimization

```python
# Use Gunicorn for production
gunicorn --bind 0.0.0.0:5001 --workers 4 app:app
```

### Database Optimization

- Use WAL mode for SQLite
- Implement connection pooling
- Add database indexes

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS with valid certificate
- [ ] Configure firewall (UFW/iptables)
- [ ] Regular security updates
- [ ] Monitor for vulnerabilities
- [ ] Backup encryption
- [ ] Rate limiting implementation

---

**🎯 Recommended Path:** Start with DigitalOcean for simplicity, then scale to AWS/GCP as needed.</content>
<parameter name="filePath">/Users/puneeth/repo/stock_fundamental/DEPLOYMENT_GUIDE.md
