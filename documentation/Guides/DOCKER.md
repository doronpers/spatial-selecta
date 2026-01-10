# Docker Deployment Guide

This guide explains how to deploy Spatial Selecta using Docker and Docker Compose.

## Overview

The Docker setup includes:
- **Backend**: FastAPI Python application
- **Frontend**: Static HTML/CSS/JS served by nginx
- **Database**: PostgreSQL 15
- **Reverse Proxy**: Nginx with SSL support
- **SSL Certificates**: Self-signed for testing, Let's Encrypt for production

## Architecture

```
Internet
    ↓
Nginx Reverse Proxy (ports 80/443)
    ├── Frontend (nginx:8080) → Static files
    └── Backend (FastAPI:8000) → /api/* endpoints
            ↓
    PostgreSQL Database
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name (for production SSL)
- Apple Music Developer Token

## Quick Start (Development)

### 1. Clone the Repository

```bash
git clone https://github.com/doronpers/spatial-selecta.git
cd spatial-selecta
```

### 2. Configure Environment Variables

```bash
# Copy the Docker environment template
cp .env.docker .env

# Edit the .env file with your configuration
nano .env
```

**Required changes:**
- `POSTGRES_PASSWORD`: Set a secure database password
- `APPLE_MUSIC_DEVELOPER_TOKEN`: Your Apple Music API token
- `REFRESH_API_TOKEN`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `RATING_IP_SALT`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `ALLOWED_ORIGINS`: Your domain (e.g., `https://yourdomain.com`)

### 3. Generate SSL Certificates (Self-Signed for Testing)

```bash
# Generate self-signed certificate for localhost
./docker/generate-ssl-cert.sh localhost
```

For a custom domain:
```bash
./docker/generate-ssl-cert.sh yourdomain.com
```

### 4. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 5. Access the Application

- **HTTPS (recommended)**: https://localhost (or your domain)
- **HTTP**: http://localhost (redirects to HTTPS)
- **Backend API**: https://localhost/api/tracks

**Note**: Self-signed certificates will show a browser warning. Click "Advanced" → "Proceed" to continue.

## Production Deployment

### Using Let's Encrypt SSL Certificates

#### Option 1: Certbot (Automatic)

1. **Update docker-compose.yml**: Uncomment the certbot service
2. **Configure domain**: Update nginx.conf with your domain
3. **Get certificates**:

```bash
# Initial certificate generation
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    -d yourdomain.com \
    -d www.yourdomain.com \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email

# Update nginx SSL volume mounts in docker-compose.yml
# volumes:
#   - certbot_certs:/etc/letsencrypt:ro

# Restart nginx
docker-compose restart nginx
```

4. **Auto-renewal**: The certbot service runs daily to check for renewal

#### Option 2: External Certificates

If you have existing SSL certificates:

```bash
# Copy certificates to docker/ssl directory
cp /path/to/fullchain.pem ./docker/ssl/
cp /path/to/privkey.pem ./docker/ssl/

# Update permissions
chmod 644 ./docker/ssl/fullchain.pem
chmod 600 ./docker/ssl/privkey.pem

# Start services
docker-compose up -d
```

### Production Environment Variables

Ensure these are properly configured in `.env`:

```bash
ENVIRONMENT=production
POSTGRES_PASSWORD=<strong-random-password>
APPLE_MUSIC_DEVELOPER_TOKEN=<your-token>
REFRESH_API_TOKEN=<secure-random-token>
RATING_IP_SALT=<secure-random-salt>
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Generate secure random tokens for `REFRESH_API_TOKEN` and `RATING_IP_SALT`
- [ ] Set specific `ALLOWED_ORIGINS` (no wildcards)
- [ ] Use valid SSL certificates (Let's Encrypt or commercial)
- [ ] Keep Docker images updated
- [ ] Review nginx rate limiting settings
- [ ] Configure firewall rules (allow 80, 443)
- [ ] Set up regular database backups

## Docker Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f nginx

# Rebuild after code changes
docker-compose up -d --build
```

### Database Management

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U spatial_user -d spatial_selecta

# Backup database
docker-compose exec db pg_dump -U spatial_user spatial_selecta > backup.sql

# Restore database
docker-compose exec -T db psql -U spatial_user -d spatial_selecta < backup.sql

# View database logs
docker-compose logs db
```

### Debugging

```bash
# Check service health
docker-compose ps

# Execute command in backend container
docker-compose exec backend python --version

# Execute command in frontend container
docker-compose exec frontend sh

# View nginx configuration
docker-compose exec nginx cat /etc/nginx/nginx.conf

# Test nginx configuration
docker-compose exec nginx nginx -t

# View backend environment variables
docker-compose exec backend env
```

## Configuration

### Nginx Settings

The nginx configuration includes:

- **Client Max Body Size**: 10MB (configurable in `docker/nginx.conf`)
- **Rate Limiting**: 
  - API endpoints: 10 requests/second (burst 20)
  - General endpoints: 100 requests/second (burst 50)
- **SSL Configuration**: TLS 1.2 and 1.3
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Gzip Compression**: Enabled for text and JSON

To modify settings, edit `docker/nginx.conf` and restart nginx:

```bash
docker-compose restart nginx
```

### Upload Size Limits

To increase file upload limits, edit `docker/nginx.conf`:

```nginx
# Change this value
client_max_body_size 50M;  # Default is 10M
```

Then restart nginx:

```bash
docker-compose restart nginx
```

### Database Configuration

PostgreSQL settings are in `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: spatial_selecta
  POSTGRES_USER: spatial_user
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

To change database settings, update `.env` and restart:

```bash
docker-compose down
docker-compose up -d
```

## Volumes

The following volumes persist data:

- `postgres_data`: PostgreSQL database files
- `certbot_certs`: SSL certificates (if using Let's Encrypt)
- `certbot_www`: ACME challenge files

### Backup Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect spatial-selecta_postgres_data

# Backup volume
docker run --rm -v spatial-selecta_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_backup.tar.gz /data
```

## Networking

All services run on the `spatial-network` bridge network:

- Frontend: Internal port 8080
- Backend: Internal port 8000
- Database: Internal port 5432
- Nginx: External ports 80, 443

Services communicate using Docker DNS (service names).

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Stop the conflicting service or change ports in docker-compose.yml
```

### SSL Certificate Errors

```bash
# Check certificate files exist
ls -la ./docker/ssl/

# Verify certificate
openssl x509 -in ./docker/ssl/fullchain.pem -text -noout

# Check nginx SSL configuration
docker-compose exec nginx nginx -t
```

### Backend Won't Start

```bash
# Check backend logs
docker-compose logs backend

# Common issues:
# - Missing APPLE_MUSIC_DEVELOPER_TOKEN
# - Database connection failed (check db is healthy)
# - Port 8000 already in use
```

### Database Connection Failed

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec backend python -c "from backend.database import engine; engine.connect()"
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Test frontend directly (bypass nginx)
curl http://localhost:8080  # Uncomment ports in docker-compose.yml first

# Check nginx proxy configuration
docker-compose exec nginx cat /etc/nginx/nginx.conf | grep frontend
```

## Performance Tuning

### PostgreSQL

For high-traffic sites, tune PostgreSQL settings:

```yaml
# In docker-compose.yml, add:
db:
  command:
    - "postgres"
    - "-c"
    - "max_connections=200"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "work_mem=16MB"
```

### Nginx

Adjust worker processes and connections:

```nginx
# In docker/nginx.conf
worker_processes auto;  # Use all CPU cores
events {
    worker_connections 2048;  # Increase from 1024
}
```

### Backend

Scale backend instances:

```yaml
# In docker-compose.yml
backend:
  deploy:
    replicas: 3  # Run 3 backend instances
```

Then update nginx upstream:

```nginx
upstream backend {
    server backend:8000;
    # Add load balancing if using replicas
}
```

## Monitoring

### Health Checks

All services have health checks configured:

```bash
# Check health status
docker-compose ps

# Services should show (healthy)
```

### Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 nginx
```

### Metrics

Consider adding monitoring tools:

- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **cAdvisor**: Container metrics

## Updating

### Update Docker Images

```bash
# Pull latest base images
docker-compose pull

# Rebuild services
docker-compose up -d --build
```

### Update Application Code

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Or rebuild specific service
docker-compose up -d --build backend
```

### Update Dependencies

```bash
# For backend (Python)
# Update requirements.txt, then:
docker-compose build backend
docker-compose up -d backend

# For frontend (if using npm)
# Update package.json, then:
docker-compose build frontend
docker-compose up -d frontend
```

## Development vs Production

### Development Setup

```yaml
# Expose ports for debugging
ports:
  - "8000:8000"  # Backend
  - "8080:8080"  # Frontend
  - "5432:5432"  # Database

# Use volume mounts for live reload
volumes:
  - ./backend:/app/backend
  - ./index.html:/usr/share/nginx/html/index.html
```

### Production Setup

- Keep all ports internal (except 80, 443 on nginx)
- Use production environment variables
- Enable auto-restart policies
- Set up SSL certificates
- Configure backups
- Enable monitoring

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/doronpers/spatial-selecta/issues)
- Check the [main README](../README.md)
- Review [DEPLOYMENT.md](../docs/DEPLOYMENT.md)
