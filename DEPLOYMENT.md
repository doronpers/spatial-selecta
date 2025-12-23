# Deployment Guide

This guide covers deploying Spatial Selecta to production, including DNS configuration and hosting setup.

## 🚀 Recommended: Deploy to Render (Easiest)

**For most users, we recommend deploying to Render.com** - it's the simplest option with no server management needed.

👉 **See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for step-by-step Render deployment guide**

**Why Render?**
- ✅ 10-minute setup (vs 2-4 hours for VPS)
- ✅ No server management
- ✅ Automatic SSL, deployments, scaling
- ✅ Built-in background job support
- ✅ $7-14/month (comparable to VPS)

---

## Alternative Options

If you need more control or want to learn server management, see the options below.

## Architecture Overview

Spatial Selecta consists of:
- **Frontend**: Static HTML/CSS/JS files served via web server
- **Backend API**: Python FastAPI application (port 8000)
- **Database**: SQLite (development) or PostgreSQL (production recommended)

## Pre-Deployment Checklist

### 1. Generate Production Secrets

```bash
# Generate secure refresh token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save this token - you'll need it for `REFRESH_API_TOKEN`.

### 2. Configure Production Environment

Create `.env` file with production values:

```bash
# Environment
ENVIRONMENT=production

# CORS - Replace with your actual domain(s)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Security - Use the token generated above
REFRESH_API_TOKEN=<generated-secure-token>

# Apple Music API
APPLE_MUSIC_DEVELOPER_TOKEN=<your-apple-music-token>
APPLE_MUSIC_USER_TOKEN=<optional-user-token>

# Database - Use PostgreSQL for production
DATABASE_URL=postgresql://user:password@localhost/spatial_selecta

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler
SCAN_INTERVAL_HOURS=48
```

### 3. Initialize Database

```bash
# For PostgreSQL
createdb spatial_selecta

# Initialize tables
python3 backend/setup.py
```

## Deployment Options

### Option 1: Traditional VPS/Server (Recommended)

#### Server Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- Node.js 14+ (for building if needed)
- PostgreSQL (recommended) or SQLite
- Nginx (for reverse proxy and static file serving)
- SSL certificate (Let's Encrypt recommended)

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv postgresql nginx -y

# Install Node.js (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### Step 2: Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/spatial-selecta
sudo chown $USER:$USER /var/www/spatial-selecta

# Clone repository
cd /var/www/spatial-selecta
git clone https://github.com/doronpers/spatial-selecta.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with production values

# Initialize database
python3 backend/setup.py
```

#### Step 3: Configure Systemd Service

Create `/etc/systemd/system/spatial-selecta.service`:

```ini
[Unit]
Description=Spatial Selecta Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/spatial-selecta
Environment="PATH=/var/www/spatial-selecta/venv/bin"
EnvironmentFile=/var/www/spatial-selecta/.env
ExecStart=/var/www/spatial-selecta/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable spatial-selecta
sudo systemctl start spatial-selecta
sudo systemctl status spatial-selecta
```

#### Step 4: Configure Nginx

Create `/etc/nginx/sites-available/spatial-selecta`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend - Static Files
    root /var/www/spatial-selecta;
    index index.html;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Frontend Routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health Check
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        access_log off;
    }

    # Static Assets Cache
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/spatial-selecta /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 5: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### Option 2: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check - verify status code is 200
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; r = requests.get('http://localhost:8000/api/health'); exit(0 if r.status_code == 200 else 1)"

# Run backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./spatial_selecta.db:/app/spatial_selecta.db  # For SQLite
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; r = requests.get('http://localhost:8000/api/health'); exit(0 if r.status_code == 200 else 1)"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: spatial_selecta
      POSTGRES_USER: spatial_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./:/var/www/spatial-selecta:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
```

### Option 3: Platform-as-a-Service (PaaS)

#### Render.com

1. **Create Web Service**:
   - Connect GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3
   - Add environment variables from `.env`

2. **Create Static Site**:
   - Connect same repository
   - Build Command: `echo "No build needed"`
   - Publish Directory: `.`
   - Add custom domain

#### Heroku

1. **Create `Procfile`**:
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy**:
```bash
heroku create spatial-selecta
heroku config:set ENVIRONMENT=production
heroku config:set ALLOWED_ORIGINS=https://yourdomain.com
heroku config:set REFRESH_API_TOKEN=<your-token>
# ... set other env vars
git push heroku main
```

#### Railway

1. Connect GitHub repository
2. Set environment variables
3. Railway auto-detects Python and runs the app

## DNS Configuration

### Step 1: Purchase Domain

Purchase a domain from a registrar (Namecheap, Google Domains, Cloudflare, etc.)

### Step 2: Configure DNS Records

#### For VPS/Server Deployment:

**A Record** (IPv4):
```
Type: A
Name: @ (or leave blank)
Value: <your-server-ip-address>
TTL: 3600 (or default)
```

**A Record** (for www subdomain):
```
Type: A
Name: www
Value: <your-server-ip-address>
TTL: 3600
```

**AAAA Record** (IPv6 - optional):
```
Type: AAAA
Name: @
Value: <your-server-ipv6-address>
TTL: 3600
```

#### For Cloudflare (Recommended):

1. Add site to Cloudflare
2. Update nameservers at your registrar
3. Configure DNS:
   - A record: `@` → Server IP
   - A record: `www` → Server IP
4. Enable SSL/TLS: Full (strict)
5. Enable Proxy (orange cloud) for DDoS protection

### Step 3: Verify DNS Propagation

```bash
# Check DNS records
dig yourdomain.com
nslookup yourdomain.com

# Check from multiple locations
# Use: https://www.whatsmydns.net/
```

## Post-Deployment

### 1. Verify Backend

```bash
# Check service status
sudo systemctl status spatial-selecta

# Check logs
sudo journalctl -u spatial-selecta -f

# Test API
curl https://yourdomain.com/api/health
```

### 2. Verify Frontend

- Visit `https://yourdomain.com`
- Check browser console for errors
- Verify API calls work

### 3. Test Authentication

```bash
# Test protected endpoint
curl -X POST https://yourdomain.com/api/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_API_TOKEN"
```

### 4. Monitor Logs

```bash
# Backend logs
sudo journalctl -u spatial-selecta -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 5. Set Up Monitoring

Consider:
- **Uptime monitoring**: UptimeRobot, Pingdom
- **Error tracking**: Sentry
- **Analytics**: Google Analytics, Plausible
- **Log aggregation**: Logtail, Papertrail

## Maintenance

### Update Application

```bash
cd /var/www/spatial-selecta
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart spatial-selecta
```

### Database Backups

```bash
# PostgreSQL
pg_dump spatial_selecta > backup_$(date +%Y%m%d).sql

# SQLite
cp spatial_selecta.db backup_$(date +%Y%m%d).db
```

### SSL Certificate Renewal

Let's Encrypt certificates auto-renew, but verify:

```bash
sudo certbot renew --dry-run
```

## Troubleshooting

### Backend Not Starting

```bash
# Check service status
sudo systemctl status spatial-selecta

# Check logs
sudo journalctl -u spatial-selecta -n 50

# Test manually
cd /var/www/spatial-selecta
source venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Nginx Errors

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U spatial_user -d spatial_selecta -h localhost

# Check database exists
psql -l | grep spatial_selecta
```

### CORS Errors

- Verify `ALLOWED_ORIGINS` in `.env` matches your domain
- Check browser console for exact error
- Ensure `ENVIRONMENT=production` is set

## Security Checklist

- [ ] SSL/TLS certificate installed and working
- [ ] `ENVIRONMENT=production` set
- [ ] `ALLOWED_ORIGINS` configured (no wildcards)
- [ ] `REFRESH_API_TOKEN` set and secure
- [ ] Database credentials secure
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Regular backups configured
- [ ] Monitoring set up
- [ ] Logs reviewed regularly

## Cost Estimates

### VPS Hosting
- **DigitalOcean**: $6-12/month (basic droplet)
- **Linode**: $5-10/month
- **Vultr**: $6-12/month
- **AWS EC2**: $10-20/month (t2.micro)

### Domain
- **.com**: $10-15/year
- **.io**: $30-40/year

### SSL Certificate
- **Let's Encrypt**: Free

### Total: ~$10-20/month for basic deployment

## Support

For deployment issues:
1. Check logs: `sudo journalctl -u spatial-selecta -n 100`
2. Review SECURITY.md for security configuration
3. Check GitHub Issues for known problems

