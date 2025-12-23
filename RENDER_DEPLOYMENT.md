# Deploying Spatial Selecta to Render

This guide walks you through deploying Spatial Selecta to Render.com - the easiest and most cost-effective option for this project.

## Why Render?

- ✅ **Simple**: No server management needed
- ✅ **Affordable**: $7/month for production
- ✅ **Background Jobs**: Built-in support for schedulers
- ✅ **Free SSL**: Automatic HTTPS
- ✅ **Easy Deployments**: Connect GitHub, auto-deploy on push
- ✅ **Free Tier**: Available for testing

## Prerequisites

- GitHub account (free)
- Render account (free to sign up)
- Domain name (optional, $10-15/year)
- Apple Music Developer Token

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub

If not already done:

```bash
# Make sure everything is committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 1.2 Create Production Environment File

Create a `.env.production` file (don't commit this, it's just for reference):

```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app-name.onrender.com,https://yourdomain.com
REFRESH_API_TOKEN=<generate-with-python3 -c "import secrets; print(secrets.token_urlsafe(32))">
APPLE_MUSIC_DEVELOPER_TOKEN=<your-token>
DATABASE_URL=postgresql://...  # Render will provide this
```

## Step 2: Deploy Backend API

### 2.1 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `spatial-selecta` repository

### 2.2 Configure Backend Service

**Basic Settings:**
- **Name**: `spatial-selecta-api` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave blank (or `backend` if you want)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port $PORT
  ```

**Advanced Settings:**
- **Instance Type**: Free (for testing) or Starter ($7/month) for production
- **Auto-Deploy**: Yes (deploys on every push to main)

### 2.3 Add Environment Variables

Click **"Environment"** tab and add:

```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app-name.onrender.com,https://yourdomain.com
REFRESH_API_TOKEN=<your-generated-token>
APPLE_MUSIC_DEVELOPER_TOKEN=<your-apple-music-token>
APPLE_MUSIC_USER_TOKEN=<optional>
SCAN_INTERVAL_HOURS=48
```

**Important**: 
- Replace `your-app-name` with your actual Render service name
- Generate `REFRESH_API_TOKEN` using: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### 2.4 Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `spatial-selecta-db`
3. **Database**: `spatial_selecta`
4. **User**: `spatial_user` (or auto-generated)
5. **Region**: Same as your web service
6. **Plan**: Free (for testing) or Starter ($7/month) for production

**Copy the Internal Database URL** - you'll need this!

### 2.5 Connect Database to Backend

1. Go back to your Web Service settings
2. **Environment** tab → **Add Environment Variable**:
   ```
   DATABASE_URL=<paste-internal-database-url-from-render>
   ```

**Note**: Render provides an internal database URL that's secure and doesn't require SSL configuration.

### 2.6 Initialize Database

After first deployment, initialize the database:

1. Go to your Web Service → **Shell** tab
2. Run:
   ```bash
   python3 backend/setup.py
   ```
3. When prompted, enter `y` to import tracks from `data.json` (if you want)

### 2.7 Deploy

Click **"Manual Deploy"** → **"Deploy latest commit**

Wait 2-3 minutes for deployment to complete.

### 2.8 Verify Backend

1. Check **"Logs"** tab for any errors
2. Visit: `https://your-app-name.onrender.com/api/health`
3. Should see: `{"status": "healthy", "timestamp": "..."}`

## Step 3: Deploy Frontend (Static Site)

### 3.1 Create Static Site

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect your GitHub repository (same one)
3. **Name**: `spatial-selecta-frontend`

### 3.2 Configure Static Site

**Settings:**
- **Build Command**: Leave blank (no build needed)
- **Publish Directory**: `.` (root directory)
- **Branch**: `main`
- **Auto-Deploy**: Yes

### 3.3 Update Frontend API URL

Your frontend needs to know where the backend API is.

**Option A: Update app.js** (if backend and frontend are on different domains):

Edit `app.js` line 2-4:

```javascript
const API_URL = window.location.hostname.includes('onrender.com')
    ? 'https://your-backend-name.onrender.com/api'
    : '/api';
```

**Option B: Use same domain** (recommended - see Step 4)

### 3.4 Deploy Frontend

Click **"Manual Deploy"** → **"Deploy latest commit"**

Your frontend will be available at: `https://spatial-selecta-frontend.onrender.com`

## Step 4: Set Up Custom Domain (Optional)

### 4.1 Add Domain to Backend

1. Go to your Web Service → **Settings** → **Custom Domains**
2. Click **"Add Custom Domain"**
3. Enter: `api.yourdomain.com`
4. Follow DNS instructions (add CNAME record)

### 4.2 Add Domain to Frontend

1. Go to your Static Site → **Settings** → **Custom Domains**
2. Click **"Add Custom Domain"**
3. Enter: `yourdomain.com` and `www.yourdomain.com`
4. Follow DNS instructions

### 4.3 Update Environment Variables

After domains are configured, update `ALLOWED_ORIGINS`:

1. Backend Web Service → **Environment** tab
2. Update:
   ```
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```
3. Redeploy

### 4.4 DNS Configuration

At your domain registrar, add:

```
Type: CNAME
Name: api
Value: your-backend-name.onrender.com

Type: CNAME  
Name: @
Value: your-frontend-name.onrender.com

Type: CNAME
Name: www
Value: your-frontend-name.onrender.com
```

## Step 5: Set Up Background Scheduler

Your app uses APScheduler which needs to run continuously. Render handles this automatically!

### How It Works

- Your Web Service runs 24/7 (on paid plans)
- APScheduler starts automatically when the service starts
- Jobs run every 48 hours as configured

### Verify Scheduler

1. Check **Logs** tab in your Web Service
2. Look for: `"Background scheduler started - scanning every 48 hours"`
3. Wait 48 hours and check logs for scan completion

### Alternative: External Cron (Free Tier)

If using Render's free tier (which sleeps after inactivity):

1. Use a free cron service: [cron-job.org](https://cron-job.org)
2. Set up cron job to call: `POST https://your-api.onrender.com/api/refresh`
3. Set frequency: Every 48 hours
4. Add header: `Authorization: Bearer YOUR_REFRESH_API_TOKEN`

## Step 6: Post-Deployment Checklist

### ✅ Verify Everything Works

- [ ] Backend health check: `https://your-api.onrender.com/api/health`
- [ ] Frontend loads: `https://your-frontend.onrender.com`
- [ ] API endpoints work: `https://your-api.onrender.com/api/tracks`
- [ ] Database initialized (check logs)
- [ ] Scheduler running (check logs for startup message)
- [ ] Custom domain working (if configured)
- [ ] SSL certificate active (automatic on Render)

### ✅ Security Checklist

- [ ] `ENVIRONMENT=production` set
- [ ] `ALLOWED_ORIGINS` configured (no wildcards)
- [ ] `REFRESH_API_TOKEN` set and secure
- [ ] Database URL is internal (provided by Render)
- [ ] No secrets in code (all in environment variables)

## Step 7: Monitoring & Maintenance

### View Logs

- **Backend**: Web Service → **Logs** tab
- **Frontend**: Static Site → **Logs** tab

### Monitor Health

- Set up uptime monitoring: [UptimeRobot](https://uptimerobot.com) (free)
- Monitor: `https://your-api.onrender.com/api/health`

### Update Application

Just push to GitHub:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Render automatically deploys!

### Database Backups

Render automatically backs up PostgreSQL databases on paid plans.

Manual backup:
1. Web Service → **Shell** tab
2. Run: `pg_dump $DATABASE_URL > backup.sql`

## Troubleshooting

### Backend Won't Start

**Check logs** for errors:
- Missing environment variables?
- Database connection issues?
- Import errors?

**Common fixes:**
```bash
# Check environment variables are set
# Verify DATABASE_URL is correct
# Check Python version (should be 3.9+)
```

### Frontend Can't Connect to API

**CORS Error?**
- Check `ALLOWED_ORIGINS` includes frontend URL
- Verify no trailing slashes

**404 Error?**
- Check API URL in `app.js` is correct
- Verify backend is deployed and running

### Scheduler Not Running

**Free Tier Issue?**
- Free tier services sleep after inactivity
- Upgrade to Starter plan ($7/month) for 24/7 operation
- Or use external cron service (see Step 5)

**Check Logs:**
- Look for scheduler startup message
- Check for errors in scheduled jobs

### Database Connection Failed

**Verify:**
- `DATABASE_URL` is set correctly
- Using internal database URL (not external)
- Database service is running
- Database initialized: `python3 backend/setup.py`

## Cost Breakdown

### Free Tier (Testing)
- Web Service: Free (sleeps after inactivity)
- PostgreSQL: Free (90 days, then $7/month)
- Static Site: Free
- **Total**: $0 (limited functionality)

### Production (Recommended)
- Web Service: $7/month (Starter plan)
- PostgreSQL: $7/month (Starter plan)
- Static Site: Free
- **Total**: $14/month

### With Custom Domain
- Domain: $10-15/year (~$1/month)
- **Total**: ~$15/month

## Render vs VPS Comparison

| Feature | Render | VPS |
|---------|--------|-----|
| Setup Time | 10 minutes | 2-4 hours |
| Server Management | None | You manage |
| SSL Certificate | Automatic | Manual (Let's Encrypt) |
| Deployments | Automatic | Manual |
| Scaling | Automatic | Manual |
| Cost | $7-14/month | $6-12/month + time |
| Background Jobs | Built-in | You configure |
| Database | Managed | You manage |

## Next Steps

1. ✅ Deploy backend API
2. ✅ Deploy frontend
3. ✅ Set up custom domain (optional)
4. ✅ Verify everything works
5. ✅ Set up monitoring
6. ✅ Share your site! 🎉

## Support

- **Render Docs**: https://render.com/docs
- **Render Support**: support@render.com
- **Project Issues**: GitHub Issues

## Quick Reference

### Backend Service
- **URL**: `https://your-app-name.onrender.com`
- **Health**: `https://your-app-name.onrender.com/api/health`
- **Docs**: `https://your-app-name.onrender.com/docs`

### Frontend
- **URL**: `https://your-frontend-name.onrender.com`

### Environment Variables Needed
```
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.onrender.com
REFRESH_API_TOKEN=<generated-token>
APPLE_MUSIC_DEVELOPER_TOKEN=<your-token>
DATABASE_URL=<provided-by-render>
```

---

**That's it!** Your Spatial Selecta app is now live on Render. 🚀

