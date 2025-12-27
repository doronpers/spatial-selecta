# Spatial Selecta - Complete Setup Guide

This guide walks you through setting up the complete Spatial Selecta system with both frontend and backend components.

## Overview

Spatial Selecta automatically tracks and displays Dolby Atmos spatial audio releases from Apple Music. The system consists of:

1. **Frontend**: Static HTML/CSS/JS website for displaying tracks
2. **Backend**: Python FastAPI server with Apple Music API integration
3. **Database**: SQLite/PostgreSQL for storing track metadata
4. **Scheduler**: Background job that runs every 48 hours to detect new releases

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Port 8080)                     │
│                     HTML + CSS + JavaScript                      │
│                                                                   │
│  - Display spatial audio tracks in responsive grid              │
│  - Filter by format (Dolby Atmos)                               │
│  - Auto-refresh from backend API or fallback to data.json       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                       Backend API (Port 8000)                    │
│                          FastAPI + Python                        │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              REST API Endpoints                           │  │
│  │  • GET  /api/tracks      - List tracks with filtering     │  │
│  │  • GET  /api/tracks/new  - Get recent releases           │  │
│  │  • POST /api/refresh     - Manual data sync              │  │
│  │  • GET  /api/stats       - Database statistics           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Background Scheduler (APScheduler)                │  │
│  │  • Runs every 48 hours                                    │  │
│  │  • Scans for new spatial audio releases                   │  │
│  │  • Updates existing tracks upgraded to Atmos              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Apple Music API Client                            │  │
│  │  • Authenticates with developer token                     │  │
│  │  • Queries audioVariants attribute                        │  │
│  │  • Monitors curated Spatial Audio playlists               │  │
│  │    - "Made for Spatial Audio"                             │  │
│  │    - "Hits in Spatial Audio"                              │  │
│  │    - "Jazz in Spatial Audio"                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)                  │
│                                                                   │
│  Tracks Table:                                                   │
│  • id, title, artist, album                                      │
│  • format (Dolby Atmos)                                          │
│  • platform (Apple Music)                                        │
│  • release_date, discovered_at, updated_at                      │
│  • apple_music_id                                                │
│  • extra_metadata (JSON)                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Node.js** v14+ (for frontend development server)
- **Python** 3.9+ (for backend)
- **pip** (Python package manager)
- **Apple Music Developer Account** (for API access)

## Installation Steps

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

### 4. Configure Apple Music API

#### Get Apple Music Developer Token

1. **Join Apple Developer Program**
   - Visit https://developer.apple.com/programs/
   - Enroll in the Apple Developer Program ($99/year)

2. **Create MusicKit Identifier**
   - Go to https://developer.apple.com/account/
   - Navigate to "Certificates, Identifiers & Profiles"
   - Create a new "MusicKit Identifier"

3. **Generate Developer Token**
   - Follow the guide: https://developer.apple.com/documentation/applemusicapi/getting_keys_and_creating_tokens
   - Create a private key (.p8 file)
   - Generate JWT token using the key
   - Token is valid for 6 months

#### Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Apple Music API Configuration
APPLE_MUSIC_DEVELOPER_TOKEN=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEyMzQ1Njc4OTAifQ...
APPLE_MUSIC_USER_TOKEN=  # Optional, for user-specific data

# Database Configuration
DATABASE_URL=sqlite:///./spatial_selecta.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 5. Initialize Database

Run the setup script to create database tables and optionally import existing data:

```bash
python3 backend/setup.py
```

When prompted, enter `y` to import tracks from `data.json`.

### 6. Start the Backend Server

**Development mode (with auto-reload):**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Or using npm script:**
```bash
npm run backend
```

The backend API will be available at http://localhost:8000

**API Documentation:** http://localhost:8000/docs

### 7. Start the Frontend Server

In a new terminal:

```bash
npm start
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

Expected response:
```json
{
  "total_tracks": 7,
  "by_platform": {
    "Apple Music": 7
  },
  "by_format": {
    "Dolby Atmos": 7
  },
  "new_tracks_last_30_days": 7
}
```

### 3. Test Frontend

Open http://localhost:8080 in your browser. You should see:
- A grid of spatial audio tracks
- Platform and format filters
- "New" badges on recent releases
- Console log: "Loaded X tracks from API"

## Usage

### Manual Refresh

To manually trigger a scan for new spatial audio releases:

**Via Frontend:**
- Click the "Refresh" button

**Via API:**
```bash
curl -X POST http://localhost:8000/api/refresh
```

### Automatic Scanning

The backend automatically scans for new releases every 48 hours. Check logs to monitor:

```bash
# Backend logs will show:
INFO:backend.scheduler:Starting scheduled spatial audio scan...
INFO:backend.scheduler:Scheduled scan complete: X added, Y updated
```

### Filtering Tracks

**Via Frontend:**
- Use dropdown filters for platform and format

**Via API:**
```bash
# Get only Apple Music Dolby Atmos tracks
curl "http://localhost:8000/api/tracks?platform=Apple%20Music&format=Dolby%20Atmos"

# Get tracks from last 7 days
curl "http://localhost:8000/api/tracks/new?days=7"
```

## Production Deployment

### Option 1: Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Initialize database on first run
RUN python3 backend/setup.py < /dev/null || true

# Expose ports
EXPOSE 8000

# Run backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t spatial-selecta .
docker run -p 8000:8000 --env-file .env spatial-selecta
```

### Option 2: Traditional Server

1. **Install dependencies on server**
2. **Configure environment variables**
3. **Use systemd service for backend**

Create `/etc/systemd/system/spatial-selecta.service`:

```ini
[Unit]
Description=Spatial Selecta Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/spatial-selecta
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Serve frontend with nginx**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    root /var/www/spatial-selecta;
    index index.html;

    # Backend API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Using PostgreSQL (Recommended for Production)

Update `DATABASE_URL` in `.env`:

```bash
DATABASE_URL=postgresql://username:password@localhost/spatial_selecta
```

Create database:
```bash
createdb spatial_selecta
```

## Troubleshooting

### Backend won't start

**Error: "Apple Music Developer Token not configured"**
- Ensure `APPLE_MUSIC_DEVELOPER_TOKEN` is set in `.env`
- Verify token is valid (not expired)

**Error: "Database connection failed"**
- Check `DATABASE_URL` in `.env`
- Ensure database file is writable (SQLite)
- Ensure PostgreSQL is running and accessible

### Frontend not loading data

**Console: "Backend API not available, loading from data.json"**
- Verify backend is running on port 8000
- Check CORS configuration if using different domains
- Verify API_URL in app.js matches your setup

### No tracks discovered

**Backend logs: "No tracks found in playlist"**
- Verify Apple Music API token has correct permissions
- Check playlist IDs in `apple_music_client.py` are valid
- Test API access: `curl -H "Authorization: Bearer YOUR_TOKEN" https://api.music.apple.com/v1/catalog/us/playlists/pl.ba2404fbc4464b8ba2d60399189cf24e`

### Rate limiting

**Error: "429 Too Many Requests"**
- Apple Music API limit: 600 requests/minute
- Reduce playlist count in `apple_music_client.py`
- Add rate limiting delays

## Maintenance

### Updating Playlists

To monitor additional Apple Music playlists, edit `backend/apple_music_client.py`:

```python
SPATIAL_AUDIO_PLAYLISTS = [
    "pl.ba2404fbc4464b8ba2d60399189cf24e",  # Hits in Spatial Audio
    "pl.cc74a5aec23942da9cf083c6c4344aee",  # Pop in Spatial Audio
    "pl.your-new-playlist-id",  # Add new playlist ID
]
```

### Database Backup

**SQLite:**
```bash
cp spatial_selecta.db spatial_selecta.db.backup
```

**PostgreSQL:**
```bash
pg_dump spatial_selecta > backup.sql
```

### Renewing Apple Music Token

Developer tokens expire after 6 months. When expired:

1. Generate new token using same process
2. Update `.env` with new token
3. Restart backend

## Support

For issues or questions:
- GitHub Issues: https://github.com/doronpers/spatial-selecta/issues
- Documentation: See `backend/README.md` for backend details

## License

MIT License - See LICENSE file for details
