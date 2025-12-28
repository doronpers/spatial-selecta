# 🚀 Deploy to Render - Step by Step Guide

## Pre-Deployment Checklist

Before deploying, make sure you have:
- [x] ✅ Apple Music Developer Token ready
- [x] ✅ Code committed to GitHub
- [x] ✅ Render account created (free at render.com)

---

## Step 1: Push Code to GitHub

Make sure your code is committed and pushed:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## Step 2: Deploy via Render Blueprint

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in or create account

2. **Create New Blueprint**
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select `spatial-selecta` repository
   - Render will detect `render.yaml` automatically

3. **Review Configuration**
   - Render will show:
     - ✅ Backend Web Service (`spatial-selecta-api`)
     - ✅ Frontend Static Site (`spatial-selecta-frontend`)
     - ✅ PostgreSQL Database (`spatial-selecta-db`)
   - Click **"Apply"** to deploy

4. **Wait for Deployment** (2-5 minutes)
   - Backend will build and deploy
   - Database will be created
   - Frontend will deploy
   - **Note the URLs** that Render provides!

---

## Step 3: Set Environment Variables

After deployment completes, you MUST set 2 environment variables:

### 3.1 Set APPLE_MUSIC_DEVELOPER_TOKEN

1. Go to **Render Dashboard** → **`spatial-selecta-api`** service
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Set:
   - **Key:** `APPLE_MUSIC_DEVELOPER_TOKEN`
   - **Value:** Your Apple Music JWT token (paste it)
5. Click **"Save Changes"**

### 3.2 Set ALLOWED_ORIGINS

1. Still in **Environment** tab
2. Find your frontend URL (from `spatial-selecta-frontend` service)
   - Example: `https://spatial-selecta-frontend.onrender.com`
3. Click **"Add Environment Variable"**
4. Set:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** Your frontend URL (e.g., `https://spatial-selecta-frontend.onrender.com`)
   - **Important:** No trailing slash, include `https://`
5. Click **"Save Changes"**

### 3.3 Restart Backend Service

After setting environment variables:
1. Go to **"Manual Deploy"** tab
2. Click **"Clear build cache & deploy"** (or just restart)
3. Wait for deployment to complete

---

## Step 4: Initialize Database

1. Go to **`spatial-selecta-api`** → **"Shell"** tab
2. Run:
   ```bash
   python3 backend/setup.py
   ```
3. When prompted: **Enter `y`** to import tracks from `data.json` (optional but recommended)
4. Wait for completion

---

## Step 5: Verify Everything Works

### 5.1 Check Backend Health

```bash
curl https://spatial-selecta-api.onrender.com/api/health
```

Should return:
```json
{"status": "healthy", "timestamp": "..."}
```

### 5.2 Check Backend Logs

1. Go to **`spatial-selecta-api`** → **"Logs"** tab
2. Look for:
   - ✅ "Starting Spatial Selecta API..."
   - ✅ "Application started successfully"
   - ✅ "Background scheduler started - scanning every 48 hours"
   - ❌ **NO** warnings about missing tokens

### 5.3 Test API Endpoints

```bash
# Get stats
curl https://spatial-selecta-api.onrender.com/api/stats

# Get tracks
curl https://spatial-selecta-api.onrender.com/api/tracks?limit=5
```

### 5.4 Test Frontend

1. Visit your frontend URL: `https://spatial-selecta-frontend.onrender.com`
2. Open browser console (F12)
3. Should see: **"Loaded X tracks from API"**
4. **NO CORS errors** in console
5. Tracks should display in the grid

---

## Step 6: Test Manual Refresh (Optional)

To test the refresh endpoint:

1. Get your `REFRESH_API_TOKEN`:
   - Go to **`spatial-selecta-api`** → **"Environment"** tab
   - Find `REFRESH_API_TOKEN` (it was auto-generated)
   - Copy the value

2. Test refresh:
   ```bash
   curl -X POST https://spatial-selecta-api.onrender.com/api/refresh \
     -H "Authorization: Bearer YOUR_REFRESH_API_TOKEN"
   ```

Should return:
```json
{
  "status": "success",
  "message": "Refresh completed: X tracks added, Y updated",
  "tracks_added": 0,
  "tracks_updated": 0,
  "timestamp": "..."
}
```

---

## 🎉 Success Checklist

- [ ] Backend deploys successfully
- [ ] Frontend deploys successfully
- [ ] Database is created
- [ ] `APPLE_MUSIC_DEVELOPER_TOKEN` is set
- [ ] `ALLOWED_ORIGINS` is set
- [ ] Backend restarts with new env vars
- [ ] Database initialized
- [ ] Health endpoint returns 200
- [ ] Backend logs show no errors
- [ ] Frontend loads and displays tracks
- [ ] No CORS errors in browser console
- [ ] Filters work on frontend

---

## 🐛 Common Issues

### Issue: Backend won't start
**Check:**
- Environment variables are set correctly
- No typos in variable names
- Values don't have extra spaces

### Issue: CORS errors
**Fix:**
- Verify `ALLOWED_ORIGINS` matches frontend URL exactly
- No trailing slash
- Include `https://`
- Restart backend after changing

### Issue: "Apple Music Developer Token not configured"
**Fix:**
- Set `APPLE_MUSIC_DEVELOPER_TOKEN` in Environment tab
- Restart backend service

### Issue: Frontend shows "No releases found"
**Fix:**
- Initialize database: `python3 backend/setup.py`
- Import data: Enter `y` when prompted
- Or wait for scheduler to discover tracks (48 hours)

### Issue: Database connection errors
**Fix:**
- `DATABASE_URL` should auto-set
- Verify database service is running
- Check database name: `spatial_selecta`

---

## 📝 Next Steps After Deployment

1. **Set up custom domain** (optional)
   - Add domain in Render Dashboard
   - Update `ALLOWED_ORIGINS` to include custom domain
   - Configure DNS records

2. **Set up monitoring** (recommended)
   - UptimeRobot: Monitor `https://spatial-selecta-api.onrender.com/api/health`
   - Set up alerts for downtime

3. **Monitor logs**
   - Check backend logs regularly
   - Verify scheduler runs every 48 hours
   - Watch for any errors

---

## 🎯 Quick Reference

**Backend URL:** `https://spatial-selecta-api.onrender.com`  
**Frontend URL:** `https://spatial-selecta-frontend.onrender.com`  
**Health Check:** `https://spatial-selecta-api.onrender.com/api/health`  
**API Docs:** `https://spatial-selecta-api.onrender.com/docs`

---

**Ready to deploy?** Follow the steps above and you'll be live in ~10 minutes! 🚀


