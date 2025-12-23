# Backend API Documentation

## Architecture

The Spatial Selecta backend is built with the following components:

### Technology Stack
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database management
- **APScheduler**: Background job scheduler for periodic tasks
- **PostgreSQL/SQLite**: Database for storing spatial audio metadata

### Key Components

#### 1. Apple Music API Client (`apple_music_client.py`)
- Authenticates with Apple Music API using developer token
- Queries tracks/albums with `audioVariants` extended attribute
- Monitors curated Spatial Audio playlists
- Detects Dolby Atmos support in tracks

#### 2. Background Scheduler (`scheduler.py`)
- Runs periodic jobs every 48 hours
- Scans for new spatial audio releases
- Updates existing tracks when upgraded to Atmos
- Supports manual refresh triggers

#### 3. Database Layer (`database.py`, `models.py`)
- Stores spatial audio track metadata
- Tracks release dates, artists, albums
- Records when tracks were discovered
- Maintains Apple Music IDs for deduplication

#### 4. API Endpoints (`main.py`)
- `GET /api/tracks` - List all spatial audio tracks with filtering
- `GET /api/tracks/new` - Get recently released tracks
- `GET /api/tracks/{id}` - Get specific track details
- `POST /api/refresh` - Manually trigger data refresh
- `GET /api/stats` - Get database statistics
- `GET /api/health` - Health check endpoint

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip or pipenv
- Apple Music Developer Account (for API access)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your Apple Music Developer Token
```

3. **Get Apple Music Developer Token:**
   - Sign up for Apple Developer Program
   - Create a MusicKit identifier
   - Generate a developer token
   - Documentation: https://developer.apple.com/documentation/applemusicapi/getting_keys_and_creating_tokens

4. **Initialize the database:**
```bash
python -c "from backend.database import init_db; init_db()"
```

5. **Import existing data (optional):**
```bash
python -c "from backend.scheduler import import_existing_data_json; from backend.database import SessionLocal; db = SessionLocal(); import_existing_data_json(db, 'data.json'); db.close()"
```

### Running the Backend

**Development mode:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Apple Music API Integration

### How It Works

1. **Authentication**: Uses JWT developer token for API authentication
2. **Spatial Audio Detection**: Queries the `audioVariants` attribute to check for Dolby Atmos support
3. **Playlist Monitoring**: Polls curated Apple playlists like "Made for Spatial Audio"
4. **Automatic Updates**: Scheduler runs every 48 hours to detect new releases

### Monitored Playlists

The system monitors these Apple Music playlists for new spatial audio content:
- Made for Spatial Audio
- Hits in Spatial Audio  
- Jazz in Spatial Audio
- (More can be added in `apple_music_client.py`)

### API Rate Limits

Apple Music API has rate limits:
- 600 requests per minute per developer token
- Consider this when adding more playlists to monitor

## Amazon Music Support

### Current Status
Amazon Music does not provide a public API for detecting Dolby Atmos content.

### Workaround Options

1. **Manual Data Entry**: Continue updating `data.json` with Amazon Music releases
2. **Web Scraping** (Not recommended): Violates ToS and is fragile
3. **Third-party Aggregators**: Some services track Atmos releases

### Future Enhancement
Monitor for Amazon Music API announcements and integrate when available.

## Database Schema

### Tracks Table
```sql
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    artist VARCHAR(500) NOT NULL,
    album VARCHAR(500) NOT NULL,
    format VARCHAR(100) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    release_date DATETIME NOT NULL,
    album_art VARCHAR(10),
    apple_music_id VARCHAR(200) UNIQUE,
    amazon_music_id VARCHAR(200) UNIQUE,
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
```

## Deployment

### Using Docker (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t spatial-selecta-api .
docker run -p 8000:8000 --env-file .env spatial-selecta-api
```

### Using PostgreSQL

Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/spatial_selecta
```

### Monitoring

- Health check: `GET /api/health`
- View logs for scheduler activity
- Monitor API response times

## Troubleshooting

### Common Issues

**"Developer token not configured"**
- Ensure `APPLE_MUSIC_DEVELOPER_TOKEN` is set in `.env`
- Verify token is valid and not expired

**"No tracks found in playlist"**
- Check playlist IDs are correct
- Verify API token has necessary permissions

**Database errors**
- Ensure database file is writable
- Check SQLAlchemy connection string

## API Examples

### Get all Dolby Atmos tracks on Apple Music
```bash
curl "http://localhost:8000/api/tracks?platform=Apple%20Music&format=Dolby%20Atmos"
```

### Get tracks released in last 7 days
```bash
curl "http://localhost:8000/api/tracks/new?days=7"
```

### Manually trigger refresh
```bash
curl -X POST "http://localhost:8000/api/refresh"
```

### Get statistics
```bash
curl "http://localhost:8000/api/stats"
```

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Email notifications for new releases
- [ ] User authentication and personalized tracking
- [ ] Support for more streaming platforms
- [ ] Advanced filtering by genre, artist, etc.
- [ ] Integration with TIDAL and other platforms
