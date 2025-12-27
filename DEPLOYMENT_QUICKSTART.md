# Quick Start: Deploy SpatialSelects.com to Render.com

**Time Required:** 15-30 minutes (plus DNS propagation time)

## Prerequisites Checklist
- [ ] Render.com account (free tier works)
- [ ] GitHub repository: `doronpers/spatial-selecta` (you have this!)
- [ ] GoDaddy access for spatialselects.com
- [ ] Apple Music Developer Token (see below)

## Get Apple Music Token FIRST

**You need this before deployment:**

1. Join Apple Developer Program: https://developer.apple.com/programs/ ($99/year)
2. Create MusicKit Identifier: https://developer.apple.com/account/
3. Generate token following: https://developer.apple.com/documentation/applemusicapi/getting_keys_and_creating_tokens
4. Copy your token - you'll need it in Step 2

**Generate Refresh Token:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy this token too.

## Step 1: Deploy to Render (5 minutes)

1. Go to https://dashboard.render.com
2. Click **New** → **Blueprint**
3. Connect repository: `doronpers/spatial-selecta`
4. Click **Apply**
5. Wait for initial deployment

## Step 2: Add Environment Variables (2 minutes)

Go to `spatial-selecta-api` service → Settings → Environment:

Add:
```
APPLE_MUSIC_DEVELOPER_TOKEN = your_apple_token_here
```

Click **Save** (service will redeploy automatically)

## Step 3: Configure Custom Domain (5 minutes)

1. In Render, go to `spatial-selecta-frontend` service
2. Settings → Custom Domains → Add:
   - `spatialselects.com`
   - `www.spatialselects.com`
3. Copy the DNS records Render provides

## Step 4: Update GoDaddy DNS (5 minutes)

1. Log in to GoDaddy
2. My Products → spatialselects.com → DNS
3. Add/Update records (from Render):
   - **A record**: @ → Render IP address
   - **CNAME record**: www → `spatial-selecta-frontend.onrender.com`
4. Save changes

## Step 5: Wait & Verify (10-30 minutes)

**DNS Propagation:** 10-30 minutes
- Check: https://dnschecker.org/#A/spatialselects.com

**SSL Certificate:** Automatic after DNS
- Render provisions Let's Encrypt certificate automatically

**Test:**
- Visit: https://spatialselects.com ✅
- Should see your SpatialSelects.com website with tracks

## That's It! 🎉

Your site is live at **https://spatialselects.com**

## Next Steps
- Monitor logs in Render Dashboard
- Set calendar reminder to renew Apple Music token in 6 months
- Check backend health: https://spatial-selecta-api.onrender.com/api/health

## Need Help?
See full documentation: `GODADDY_DOMAIN_SETUP.md`
