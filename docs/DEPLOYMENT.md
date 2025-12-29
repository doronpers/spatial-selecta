# Deployment Guide

Complete guide for deploying SpatialSelects.com to production.

## Quick Start (Render.com - Recommended)

**Time Required:** 15-30 minutes (plus DNS propagation)

### Prerequisites

- [ ] Render.com account (free tier works)
- [ ] GitHub repository connected
- [ ] Apple Music Developer Token (see [Apple Music API Setup](#apple-music-api-setup))
- [ ] Domain name (optional, for custom domain)

### Step 1: Deploy via Render Blueprint (5 minutes)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Blueprint**
3. Connect repository: `doronpers/spatial-selecta`
4. Render will detect `render.yaml` automatically
5. Click **Apply**
6. Wait for initial deployment (2-5 minutes)

**Services Created:**
- ✅ Backend Web Service (`spatial-selecta-api`)
- ✅ Frontend Static Site (`spatial-selecta-frontend`)
- ✅ PostgreSQL Database (`spatial-selecta-db`)

### Step 2: Set Environment Variables (2 minutes)

Go to `spatial-selecta-api` service → **Settings** → **Environment**:

**Required Variables:**

1. **APPLE_MUSIC_DEVELOPER_TOKEN**
   - Value: Your Apple Music JWT token
   - Format: `eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6...`

2. **ALLOWED_ORIGINS**
   - Value: Your frontend URL(s), comma-separated
   - Example: `https://spatial-selecta-frontend.onrender.com`
   - For custom domain: `https://yourdomain.com,https://www.yourdomain.com`
   - **Important:** No wildcards, include `https://`, no trailing slashes

**Auto-Configured (no action needed):**
- ✅ `ENVIRONMENT=production`
- ✅ `DATABASE_URL` (auto-connected from database)
- ✅ `REFRESH_API_TOKEN` (auto-generated)
- ✅ `SCAN_INTERVAL_HOURS=48`

Click **Save Changes** (service will redeploy automatically).

### Step 3: Initialize Database (2 minutes)

1. Go to `spatial-selecta-api` → **Shell** tab
2. Run:
   ```bash
   python3 backend/setup.py
   ```
3. When prompted, enter `y` to import tracks from `data.json` (optional)

### Step 4: Verify Deployment

**Check Backend Health:**
```bash
curl https://spatial-selecta-api.onrender.com/api/health
```
Should return: `{"status": "healthy", ...}`

**Check Backend Logs:**
- Look for: "Application started successfully"
- Look for: "Background scheduler started"
- ⚠️ No warnings about missing tokens

**Test Frontend:**
- Visit: `https://spatial-selecta-frontend.onrender.com`
- Open browser console (F12)
- Should see: "Loaded X tracks from API"
- No CORS errors

### Step 5: Configure Custom Domain (Optional)

See [Custom Domain Setup](#custom-domain-setup) section below.

## Apple Music API Setup

### Get Apple Music Developer Token

1. **Join Apple Developer Program**
   - Visit https://developer.apple.com/programs/
   - Enroll ($99/year)

2. **Create MusicKit Identifier**
   - Go to https://developer.apple.com/account/
   - Navigate to "Certificates, Identifiers & Profiles"
   - Create a new "MusicKit Identifier"

3. **Generate Developer Token**
   - Follow: https://developer.apple.com/documentation/applemusicapi/getting_keys_and_creating_tokens
   - Create a private key (.p8 file)
   - Generate JWT token (valid for 6 months)
   - Copy the token for use in environment variables

### Generate Refresh Token

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy this token for `REFRESH_API_TOKEN` (though Render auto-generates it).

## Custom Domain Setup

### For Render.com Deployments

#### Step 1: Add Custom Domain in Render

1. Go to `spatial-selecta-frontend` service
2. **Settings** → **Custom Domains** → **Add Custom Domain**
3. Add both:
   - `yourdomain.com` (apex domain)
   - `www.yourdomain.com` (www subdomain)

#### Step 2: Get DNS Records from Render

Render will provide DNS records:

**For apex domain (yourdomain.com):**
- Type: `A`
- Name: `@`
- Value: `216.24.57.1` (example - use actual IP from Render)

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Value: `spatial-selecta-frontend.onrender.com`

#### Step 3: Update DNS at Your Registrar

**GoDaddy Example:**

1. Log in to GoDaddy
2. **My Products** → `yourdomain.com` → **DNS**
3. Add/Update records:
   - **A record**: `@` → Render IP address
   - **CNAME record**: `www` → `spatial-selecta-frontend.onrender.com`
4. Save changes

**Other Registrars:**
- Follow similar process
- Add A record for apex domain
- Add CNAME record for www subdomain

#### Step 4: Wait for DNS Propagation

- Usually takes 10-30 minutes
- Can take up to 48 hours
- Check status: https://dnschecker.org/#A/yourdomain.com

#### Step 5: SSL Certificate

- Render automatically provisions SSL certificate after DNS propagates
- Usually takes 1-5 minutes after DNS verification
- Your site will be accessible at `https://yourdomain.com`

#### Step 5: Update ALLOWED_ORIGINS

After custom domain is working:

1. Go to `spatial-selecta-api` → **Environment**
2. Update `ALLOWED_ORIGINS` to include your custom domain:
   ```
   https://yourdomain.com,https://www.yourdomain.com
   ```
3. Save and restart backend

## VPS Deployment

### Server Requirements

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- PostgreSQL (recommended) or SQLite
- Nginx (for reverse proxy)
- Domain name with DNS access

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv postgresql nginx -y

# Install Node.js (for frontend if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 2: Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/doronpers/spatial-selecta.git
sudo chown -R $USER:$USER spatial-selecta
cd spatial-selecta
```

### Step 3: Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Edit with production values
```

### Step 4: Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createdb spatial_selecta
sudo -u postgres createuser spatial_user
sudo -u postgres psql -c "ALTER USER spatial_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE spatial_selecta TO spatial_user;"

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://spatial_user:your_password@localhost/spatial_selecta

# Initialize database
python3 backend/setup.py
```

### Step 5: Systemd Service

Create `/etc/systemd/system/spatial-selecta.service`:

```ini
[Unit]
Description=SpatialSelects.com Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/spatial-selecta
Environment="PATH=/var/www/spatial-selecta/venv/bin"
ExecStart=/var/www/spatial-selecta/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable spatial-selecta
sudo systemctl start spatial-selecta
```

### Step 6: Nginx Configuration

Create `/etc/nginx/sites-available/spatial-selecta`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    root /var/www/spatial-selecta;
    index index.html;

    # Backend API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend files
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/spatial-selecta /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 7: SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Docker Deployment

### Dockerfile

The project includes a `Dockerfile`. Build and run:

```bash
# Build image
docker build -t spatial-selecta .

# Run container
docker run -d \
  --name spatial-selecta \
  -p 8000:8000 \
  --env-file .env \
  spatial-selecta
```

### Docker Compose

See `docker-compose.yml.example` for a complete setup with PostgreSQL.

## Post-Deployment Checklist

- [ ] Backend health check returns 200
- [ ] Frontend loads and displays tracks
- [ ] No CORS errors in browser console
- [ ] Database initialized with tables
- [ ] Scheduler running (check logs)
- [ ] SSL certificate active (if using custom domain)
- [ ] Environment variables set correctly
- [ ] API documentation accessible at `/docs`
- [ ] Manual refresh endpoint works
- [ ] Filters work on frontend

## Troubleshooting

### Backend won't start

**Check:**
- Environment variables are set correctly
- No typos in variable names
- Values don't have extra spaces
- Database is accessible

### CORS errors

**Fix:**
- Verify `ALLOWED_ORIGINS` matches frontend URL exactly
- No trailing slash
- Include `https://`
- Restart backend after changing

### "Apple Music Developer Token not configured"

**Fix:**
- Set `APPLE_MUSIC_DEVELOPER_TOKEN` in environment
- Restart backend service
- Verify token is not expired (valid for 6 months)

### Frontend shows "No releases found"

**Fix:**
- Initialize database: `python3 backend/setup.py`
- Import data: Enter `y` when prompted
- Or wait for scheduler to discover tracks (48 hours)

### Database connection errors

**Fix:**
- Verify `DATABASE_URL` is correct
- Check database service is running
- Verify database name matches: `spatial_selecta`
- Check user permissions

### DNS not resolving

**Fix:**
- Wait 10-30 minutes for propagation
- Check DNS records are correct
- Verify A record points to correct IP
- Verify CNAME record points to correct hostname

## Monitoring

### Health Checks

Set up monitoring for:
- Backend health: `https://your-api-url/api/health`
- Frontend availability
- Database connectivity

### Logs

**Render.com:**
- View logs in Render Dashboard → Service → Logs

**VPS:**
```bash
# Backend logs
sudo journalctl -u spatial-selecta -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Maintenance

### Renewing Apple Music Token

Tokens expire after 6 months:

1. Generate new token
2. Update `APPLE_MUSIC_DEVELOPER_TOKEN` in environment
3. Restart backend service

### Database Backups

**PostgreSQL:**
```bash
pg_dump spatial_selecta > backup_$(date +%Y%m%d).sql
```

**SQLite:**
```bash
cp spatial_selecta.db spatial_selecta.db.backup
```

### Updating Application

**Render.com:**
- Push to GitHub (auto-deploys)
- Or manually trigger deploy in Render Dashboard

**VPS:**
```bash
cd /var/www/spatial-selecta
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart spatial-selecta
```

## Cost Estimates

**Render.com:**
- Free tier: Limited resources, good for testing
- Starter plan: $7/month (backend) + $7/month (database) = $14/month
- Static site: Free

**VPS:**
- DigitalOcean/Linode: $6-12/month
- Plus domain: $10-15/year

## Next Steps

- See [Pre-Launch Checklist](CHECKLIST.md) for production readiness
- See [Security Guide](SECURITY.md) for security best practices
- See [API Documentation](API.md) for API usage

