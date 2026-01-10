# Pre-Launch Checklist

Complete checklist for deploying SpatialSelects.com to production.

## 🔴 Critical Requirements (Must Complete)

### 1. Apple Music API Configuration
- [ ] **Obtain Apple Music Developer Token**
  - Join Apple Developer Program ($99/year)
  - Create MusicKit Identifier at https://developer.apple.com/account/
  - Generate JWT developer token (valid for 6 months)
  - Store token securely (DO NOT commit to git)

- [ ] **Configure Environment Variable**
  - Set `APPLE_MUSIC_DEVELOPER_TOKEN` in production environment
  - Verify token works: Test API connection in backend logs

**Status**: ⚠️ **REQUIRED** - Backend cannot discover tracks without this

### 2. Production Environment Variables
- [ ] **Generate Secure Refresh Token**
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  - Set `REFRESH_API_TOKEN` in production environment
  - Keep this token secret and secure

- [ ] **Set Environment Configuration**
  ```bash
  ENVIRONMENT=production
  ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  REFRESH_API_TOKEN=<generated-token>
  APPLE_MUSIC_DEVELOPER_TOKEN=<your-token>
  DATABASE_URL=<postgresql-url-from-hosting-provider>
  SCAN_INTERVAL_HOURS=48
  ```

**Status**: ⚠️ **REQUIRED** - Application won't work correctly without these

### 3. Database Setup
- [ ] **Create Production Database**
  - PostgreSQL (recommended) or SQLite
  - For Render: Create PostgreSQL database in dashboard
  - For VPS: Install PostgreSQL and create database

- [ ] **Initialize Database Tables**
  ```bash
  python3 backend/setup.py
  ```
  - Run this after first deployment
  - Optionally import existing `data.json` tracks

- [ ] **Verify Database Connection**
  - Check backend logs for successful connection
  - Test with: `curl https://your-api-url/api/stats`

**Status**: ⚠️ **REQUIRED** - No data can be stored without database

### 4. CORS Configuration
- [ ] **Set ALLOWED_ORIGINS**
  - Must include your frontend domain(s)
  - Format: `https://yourdomain.com,https://www.yourdomain.com`
  - NO wildcards (`*`) in production
  - Include Render subdomain if using: `https://your-app.onrender.com`

- [ ] **Test CORS**
  - Deploy frontend and backend
  - Open browser console
  - Verify no CORS errors when loading tracks

**Status**: ⚠️ **REQUIRED** - Frontend won't be able to fetch data without proper CORS

### 5. Frontend API URL Configuration
- [ ] **Verify API URL Detection**
  - Frontend automatically detects API URL based on hostname
  - For Render: Should auto-detect backend subdomain
  - For custom domains: May need manual configuration
  - Test in browser console: Check `API_URL` value

**Status**: ⚠️ **REQUIRED** - Frontend won't load data if API URL is wrong

## 🟡 Important Setup (Should Complete)

### 6. Deployment Platform Setup
- [ ] **Choose Deployment Platform**
  - **Render.com** (Recommended - easiest, $7-14/month)
  - VPS (DigitalOcean, Linode, etc. - $6-12/month)
  - Other PaaS (Heroku, Railway, etc.)

- [ ] **Deploy Backend API**
  - Follow [Deployment Guide](DEPLOYMENT.md#quick-start-rendercom---recommended) for Render
  - Or follow VPS deployment instructions
  - Verify health endpoint: `https://your-api-url/api/health`

- [ ] **Deploy Frontend**
  - Static site hosting (Render Static Site, Netlify, Vercel, GitHub Pages)
  - Or serve via nginx on same server as backend
  - Verify site loads and displays tracks

**Status**: ✅ **RECOMMENDED** - Can use Render blueprint (`render.yaml`) for one-click deploy

### 7. Domain Configuration (Optional but Recommended)
- [ ] **Purchase Domain**
  - Choose registrar (Namecheap, Google Domains, Cloudflare)
  - Cost: $10-15/year for .com

- [ ] **Configure DNS**
  - Add A/CNAME records pointing to hosting provider
  - For Render: Add custom domain in dashboard
  - Update `ALLOWED_ORIGINS` to include custom domain

- [ ] **SSL Certificate**
  - Render: Automatic SSL (free)
  - VPS: Use Let's Encrypt (free)
  - Verify HTTPS works

**Status**: 🟢 **OPTIONAL** - Site works on hosting provider subdomain

### 8. Initial Data Population
- [ ] **Import Existing Tracks**
  - Run `python3 backend/setup.py` after deployment
  - Choose 'y' to import from `data.json`
  - Or manually trigger first scan via API

- [ ] **Verify Data Display**
  - Check frontend shows tracks
  - Verify filters work
  - Test "New" badge appears for recent releases

**Status**: ✅ **RECOMMENDED** - Site will work but be empty without data

### 9. Background Scheduler Verification
- [ ] **Verify Scheduler Starts**
  - Check backend logs for: "Background scheduler started - scanning every 48 hours"
  - Scheduler runs automatically on Render paid plans
  - Free tier: Use external cron service (cron-job.org)

- [ ] **Test Manual Refresh**
  ```bash
  curl -X POST https://your-api-url/api/refresh \
    -H "Authorization: Bearer YOUR_REFRESH_API_TOKEN"
  ```
  - Verify tracks are discovered and added

**Status**: ✅ **RECOMMENDED** - Manual refresh works without scheduler

## 🟢 Nice to Have (Can Add Later)

### 10. Monitoring & Analytics
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Add error tracking (Sentry)
- [ ] Add analytics (Google Analytics, Plausible)

### 11. Performance Optimization
- [ ] Enable CDN for static assets
- [ ] Add caching headers
- [ ] Optimize images (if adding album art later)

### 12. Security Enhancements
- [ ] Review [Security Guide](SECURITY.md) checklist
- [ ] Set up rate limiting (already implemented)
- [ ] Regular security audits

## 📋 Quick Start Checklist (Minimum Viable Launch)

For a **minimum viable launch**, you need:

1. ✅ **Apple Music Developer Token** - Set `APPLE_MUSIC_DEVELOPER_TOKEN`
2. ✅ **Production Environment Variables** - Set all required env vars
3. ✅ **Database** - Create and initialize PostgreSQL/SQLite
4. ✅ **Backend Deployment** - Deploy API to hosting provider
5. ✅ **Frontend Deployment** - Deploy static site
6. ✅ **CORS Configuration** - Set `ALLOWED_ORIGINS` correctly
7. ✅ **API URL** - Verify frontend API URL detection
8. ✅ **Initial Data** - Import tracks or run first scan

**Estimated Time**: 30-60 minutes (with Render) or 2-4 hours (with VPS)

## 🔍 Pre-Launch Testing

Before going live, test:

- [ ] Backend health endpoint returns 200
- [ ] Frontend loads without errors
- [ ] Tracks display correctly
- [ ] Filters work (platform, format)
- [ ] Refresh button works
- [ ] API endpoints return data
- [ ] CORS allows frontend to fetch data
- [ ] Database queries work
- [ ] Scheduler starts (check logs)
- [ ] Manual refresh works (with auth token)

## 🚀 Deployment Options Summary

### Option 1: Render.com (Easiest - Recommended)
**Time**: 10-15 minutes  
**Cost**: $7-14/month  
**Steps**:
1. Push code to GitHub
2. Use `render.yaml` blueprint OR manually create services
3. Set environment variables
4. Initialize database via Shell
5. Done!

**See**: [Deployment Guide](DEPLOYMENT.md#quick-start-rendercom---recommended)

### Option 2: VPS (More Control)
**Time**: 2-4 hours  
**Cost**: $6-12/month  
**Steps**:
1. Set up Ubuntu server
2. Install Python, PostgreSQL, Nginx
3. Clone repository
4. Configure environment variables
5. Set up systemd service
6. Configure Nginx reverse proxy
7. Set up SSL with Let's Encrypt

**See**: [Deployment Guide](DEPLOYMENT.md#vps-deployment)

## 📝 Current Status

Based on code review:

✅ **Completed**:
- Backend API fully implemented
- Frontend UI complete
- Database models and schemas ready
- Scheduler implemented
- Apple Music client ready
- Deployment documentation complete
- Security features (rate limiting, CORS, auth) implemented

⚠️ **Needs Configuration**:
- Apple Music Developer Token (must obtain)
- Production environment variables (must set)
- Database initialization (must run)
- CORS origins (must configure)
- Frontend API URL (verify auto-detection)

❌ **Missing**:
- Actual deployment to hosting provider
- Domain configuration (optional)
- Monitoring setup (optional)

## 🎯 Next Steps

1. **Get Apple Music Developer Token** (if not already have)
2. **Choose hosting provider** (Render recommended)
3. **Deploy backend** following [Deployment Guide](DEPLOYMENT.md)
4. **Deploy frontend** to static hosting
5. **Configure environment variables**
6. **Initialize database**
7. **Test everything**
8. **Go live!** 🎉

