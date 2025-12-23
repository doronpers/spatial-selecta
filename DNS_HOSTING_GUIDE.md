# DNS and Hosting Setup Guide

This guide explains the DNS and hosting changes needed to get Spatial Selecta online.

## Quick Overview

To get your site online, you need:
1. **Domain Name** - Purchase and configure DNS
2. **Hosting** - Server to run the application
3. **SSL Certificate** - HTTPS encryption (free with Let's Encrypt)
4. **DNS Records** - Point domain to your server

## Step-by-Step: Getting Online

### Step 1: Choose Hosting Provider

#### Option A: VPS (Virtual Private Server) - Recommended
**Best for**: Full control, cost-effective

**Providers**:
- **DigitalOcean**: $6-12/month (Droplet)
- **Linode**: $5-10/month
- **Vultr**: $6-12/month
- **AWS EC2**: $10-20/month (t2.micro)

**What you get**:
- Full server access
- Root privileges
- Can install anything
- Best for learning

#### Option B: Platform-as-a-Service (PaaS)
**Best for**: Easy deployment, managed infrastructure

**Providers**:
- **Render.com**: Free tier available, $7+/month
- **Railway**: $5+/month
- **Heroku**: $7+/month (Eco dyno)
- **Fly.io**: Free tier available

**What you get**:
- Automatic deployments
- Managed infrastructure
- Less control, easier setup

### Step 2: Purchase Domain Name

**Recommended Registrars**:
- **Cloudflare**: $8-10/year (.com), includes free DNS
- **Namecheap**: $10-15/year (.com)
- **Google Domains**: $12/year (.com)
- **Porkbun**: $8-10/year (.com)

**Domain Extensions**:
- `.com` - Most common ($10-15/year)
- `.io` - Tech-friendly ($30-40/year)
- `.dev` - Developer-focused ($15-20/year)

### Step 3: DNS Configuration

#### If Using VPS + Cloudflare (Recommended)

1. **Add Site to Cloudflare**:
   - Sign up at cloudflare.com
   - Add your domain
   - Cloudflare will scan existing DNS records

2. **Update Nameservers at Registrar**:
   - Copy nameservers from Cloudflare (e.g., `alice.ns.cloudflare.com`)
   - Go to your domain registrar
   - Update nameservers to Cloudflare's

3. **Configure DNS Records in Cloudflare**:
   ```
   Type: A
   Name: @
   Content: <your-server-ip>
   Proxy: Enabled (orange cloud) ✅
   TTL: Auto
   
   Type: A
   Name: www
   Content: <your-server-ip>
   Proxy: Enabled (orange cloud) ✅
   TTL: Auto
   ```

4. **Enable SSL/TLS**:
   - SSL/TLS → Overview → Full (strict)
   - Automatic HTTPS Rewrites: ON

#### If Using VPS + Direct DNS

1. **At Your Domain Registrar**:
   ```
   Type: A
   Name: @ (or leave blank)
   Value: <your-server-ip>
   TTL: 3600
   
   Type: A
   Name: www
   Value: <your-server-ip>
   TTL: 3600
   ```

2. **Wait for DNS Propagation** (5 minutes to 48 hours)
   - Check: https://www.whatsmydns.net/

#### If Using PaaS (Render/Railway/etc.)

1. **Add Custom Domain in PaaS Dashboard**:
   - Go to your service settings
   - Add custom domain: `yourdomain.com`
   - Add www subdomain: `www.yourdomain.com`

2. **Configure DNS at Registrar**:
   - PaaS will provide DNS records (usually CNAME)
   - Add CNAME record: `www` → `your-app.onrender.com`
   - Add A record: `@` → IP provided by PaaS

### Step 4: Server Setup (VPS Only)

#### Get Your Server IP

After creating a VPS:
- **DigitalOcean**: Dashboard → Droplets → Your droplet → IP address
- **Linode**: Dashboard → Linodes → Your linode → IP address

#### Initial Server Configuration

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install required software
apt install python3 python3-pip python3-venv postgresql nginx certbot python3-certbot-nginx -y

# Install Node.js (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
```

#### Deploy Application

```bash
# Create app directory
mkdir -p /var/www/spatial-selecta
cd /var/www/spatial-selecta

# Clone repository
git clone https://github.com/doronpers/spatial-selecta.git .

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Initialize database
python3 backend/setup.py
```

#### Configure Nginx

```bash
# Copy example config
cp nginx.conf.example /etc/nginx/sites-available/spatial-selecta

# Edit with your domain
nano /etc/nginx/sites-available/spatial-selecta
# Replace "yourdomain.com" with your actual domain

# Enable site
ln -s /etc/nginx/sites-available/spatial-selecta /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl restart nginx
```

#### Set Up SSL Certificate

```bash
# Get Let's Encrypt certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
certbot renew --dry-run
```

#### Set Up Systemd Service

```bash
# Create service file
nano /etc/systemd/system/spatial-selecta.service

# Paste configuration from DEPLOYMENT.md

# Enable and start
systemctl daemon-reload
systemctl enable spatial-selecta
systemctl start spatial-selecta
systemctl status spatial-selecta
```

### Step 5: Verify Everything Works

1. **Check DNS Propagation**:
   ```bash
   dig yourdomain.com
   nslookup yourdomain.com
   ```

2. **Test HTTPS**:
   ```bash
   curl https://yourdomain.com/api/health
   ```

3. **Visit Website**:
   - Open https://yourdomain.com in browser
   - Check browser console for errors
   - Verify API calls work

## DNS Record Types Explained

### A Record
- **Purpose**: Points domain to IPv4 address
- **Example**: `yourdomain.com` → `192.0.2.1`
- **Use**: Main domain and subdomains

### AAAA Record
- **Purpose**: Points domain to IPv6 address
- **Example**: `yourdomain.com` → `2001:db8::1`
- **Use**: IPv6 support (optional)

### CNAME Record
- **Purpose**: Alias one domain to another
- **Example**: `www.yourdomain.com` → `yourdomain.com`
- **Use**: Subdomains, PaaS deployments

### MX Record
- **Purpose**: Email routing
- **Not needed** for this application

## Common DNS Issues

### "Domain not resolving"
- **Check**: DNS propagation status
- **Wait**: Can take up to 48 hours (usually 5-30 minutes)
- **Verify**: Nameservers are correct

### "SSL certificate errors"
- **Check**: Certificate is installed correctly
- **Verify**: Domain matches certificate
- **Fix**: Re-run certbot if needed

### "Site loads but API doesn't work"
- **Check**: CORS configuration in `.env`
- **Verify**: `ALLOWED_ORIGINS` includes your domain
- **Check**: Nginx proxy configuration

## Cost Breakdown

### Minimum Setup (VPS)
- **Domain**: $10/year (.com)
- **VPS**: $6/month (DigitalOcean)
- **SSL**: Free (Let's Encrypt)
- **Total**: ~$82/year ($6.83/month)

### With Cloudflare
- **Domain**: $10/year
- **VPS**: $6/month
- **Cloudflare**: Free (includes CDN, DDoS protection)
- **SSL**: Free (Let's Encrypt or Cloudflare)
- **Total**: ~$82/year

### PaaS Option
- **Domain**: $10/year
- **Hosting**: $7/month (Render)
- **SSL**: Included
- **Total**: ~$94/year ($7.83/month)

## Quick Reference: DNS Checklist

- [ ] Domain purchased
- [ ] Nameservers updated (if using Cloudflare)
- [ ] A record created for `@` (root domain)
- [ ] A record created for `www` subdomain
- [ ] DNS propagation verified (check with dig/nslookup)
- [ ] SSL certificate installed
- [ ] HTTPS working (test in browser)
- [ ] CORS configured in `.env`
- [ ] Backend service running
- [ ] Nginx configured and running

## Next Steps After DNS Setup

1. **Monitor Logs**: `sudo journalctl -u spatial-selecta -f`
2. **Set Up Backups**: Database and application files
3. **Configure Monitoring**: Uptime checks, error tracking
4. **Review Security**: See SECURITY.md
5. **Test Everything**: All endpoints, frontend, API

## Getting Help

- **DNS Issues**: Check registrar's documentation
- **Server Issues**: See DEPLOYMENT.md troubleshooting
- **SSL Issues**: Let's Encrypt documentation
- **Application Issues**: Check logs and SECURITY.md

## Example Timeline

- **Day 1**: Purchase domain, set up VPS
- **Day 1**: Configure DNS records
- **Day 1-2**: Wait for DNS propagation
- **Day 2**: Deploy application
- **Day 2**: Install SSL certificate
- **Day 2**: Test and verify
- **Total**: 1-2 days to go live

