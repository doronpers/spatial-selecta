# Setup Guide

Complete guide for setting up SpatialSelects.com for local development.

## Overview

SpatialSelects.com consists of:
- **Frontend**: Static HTML/CSS/JS website
- **Backend**: Python FastAPI server with Apple Music API integration
- **Database**: SQLite (development) or PostgreSQL (production)
- **Scheduler**: Background job that runs every 48 hours to detect new releases

## Prerequisites

- **Node.js** v14+ (for frontend development server)
- **Python** 3.9+ (for backend)
- **pip** (Python package manager)
- **Apple Music Developer Account** (for API access) - Optional for local dev without API features

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/doronpers/spatial-selecta.git
cd spatial-selecta
```

### 2. Install Frontend Dependencies

```bash
npm install
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Apple Music API (Optional for Local Dev)

#### Get Apple Music Developer Token

1. **Join Apple Developer Program**
   - Visit https://developer.apple.com/programs/
   - Enroll in the Apple Developer Program ($99/year)

2. **Create MusicKit Identifier**
   - Go to https://developer.apple.com/account/
   - Navigate to "Certificates, Identifiers & Profiles"
   - Create a new "MusicKit Identifier"

3. **Generate Developer Token**
   - Follow: https://developer.apple.com/documentation/applemusicapi/getting_keys_and_creating_tokens
   - Create a private key (.p8 file)
   - Generate JWT token (valid for 6 months)

#### Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Apple Music API Configuration
APPLE_MUSIC_DEVELOPER_TOKEN=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEyMzQ1Njc4OTAifQ...

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./spatial_selecta.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development

# CORS (for local development)
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### 5. Initialize Database

Run the setup script to create database tables:

```bash
python3 backend/setup.py
```

When prompted, enter `y` to import tracks from `data.json` (optional).

### 6. Start the Backend Server

**Development mode (with auto-reload):**
```bash
uvicorn backend.main:app --reload --port 8000
```

The backend API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 7. Start the Frontend Server

In a new terminal, use one of these options:

**Option 1: Using npm (if configured)**
```bash
npm start
```

**Option 2: Using Python HTTP server**
```bash
python -m http.server 8080
```

**Option 3: Using Node.js http-server**
```bash
npx http-server -p 8080
```

The website will be available at http://localhost:8080

## Verifying the Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-23T19:00:00.000000"
}
```

### 2. Check Database Statistics

```bash
curl http://localhost:8000/api/stats
```

### 3. Test Frontend

Open http://localhost:8080 in your browser. You should see:
- A grid of spatial audio tracks
- Platform and format filters
- "New" badges on recent releases
- Console log: "Loaded X tracks from API" (or from data.json fallback)

## Environment Variables Reference

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `APPLE_MUSIC_DEVELOPER_TOKEN` | Apple Music JWT token | `eyJhbGciOiJFUzI1NiIs...` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `https://yourdomain.com,https://www.yourdomain.com` |
| `REFRESH_API_TOKEN` | Secure token for refresh endpoint | Generated with `secrets.token_urlsafe(32)` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host/db` |
| `ENVIRONMENT` | Environment mode | `production` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `SCAN_INTERVAL_HOURS` | Scheduler interval | `48` |
| `API_HOST` | Backend host | `0.0.0.0` |
| `API_PORT` | Backend port | `8000` |
| `APPLE_MUSIC_USER_TOKEN` | User-specific token | None |

## Troubleshooting

### Backend won't start

**Error: "Apple Music Developer Token not configured"**
- This is a warning, not fatal. Backend will start but won't discover new tracks.
- Set `APPLE_MUSIC_DEVELOPER_TOKEN` in `.env` to enable API features.

**Error: "Database connection failed"**
- Check `DATABASE_URL` in `.env`
- Ensure database file is writable (SQLite)
- Ensure PostgreSQL is running (if using PostgreSQL)

### Frontend not loading data

**Console: "Failed to fetch" or "ERR_NAME_NOT_RESOLVED"**
- Verify backend is running on port 8000
- Check API URL detection in browser console
- For `file://` protocol: Use a local HTTP server instead

**Console: CORS errors**
- Check `ALLOWED_ORIGINS` includes your frontend URL
- Restart backend after changing environment variables

### No tracks discovered

**Backend logs: "No tracks found"**
- Verify Apple Music API token has correct permissions
- Check playlist IDs in `backend/apple_music_client.py` are valid
- Test API access manually

### Rate limiting

**Error: "429 Too Many Requests"**
- Apple Music API limit: 600 requests/minute
- Reduce playlist count or add rate limiting delays

## Using PostgreSQL (Optional)

For production-like local development:

1. Install PostgreSQL:
   ```bash
   # macOS
   brew install postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql
   ```

2. Create database:
   ```bash
   createdb spatial_selecta
   ```

3. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://username:password@localhost/spatial_selecta
   ```

4. Initialize database:
   ```bash
   python3 backend/setup.py
   ```

## Next Steps

- See [Deployment Guide](DEPLOYMENT.md) for production deployment
- See [API Documentation](API.md) for backend API details
- See [Development Guide](DEVELOPMENT.md) for architecture and development guidelines

