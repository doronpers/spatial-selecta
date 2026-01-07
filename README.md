# SpatialSelects.com 🎵

A website that automatically tracks and displays the latest music releases available in Dolby Atmos spatial audio format on Apple Music.

## Features

- **Automated Discovery**: Backend automatically scans for new spatial audio releases every 48 hours
- **Platform Filtering**: Filter by platform (Apple Music, Amazon Music) - implemented
- **Format Filtering**: Filter by audio format (Dolby Atmos, 360 Reality Audio) - implemented
- **New Release Badges**: Highlights releases from the last 30 days
- **Manual Sync**: Trigger on-demand track discovery from Apple Music
- **Engineer Index**: Explore top mix engineers and their portfolios (view available, data loading implemented)
- **Community Ratings**: Rate immersiveness and flag fake Atmos mixes (API endpoints available)
- **Hardware Guide**: Educational resources for optimal listening (view available)
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Minimalist Interface**: Clean, typography-focused design

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python 3.9+
- pytest (for testing)

### Design Philosophy

**"Good design is as little design as possible." - Dieter Rams**

This project adheres to a strict minimalist design system:
- **Honesty**: No decorative elements that don't serve a function.
- **Unobtrusive**: Content comes first; UI frames it.
- **Thorough**: precise execution of details (typography, spacing).
- **Environmentally Friendly**: Efficient code, minimal bandwidth usage.

### Installation

1. Clone the repository:

```bash
git clone https://github.com/doronpers/spatial-selecta.git
cd spatial-selecta
```

1. Install dependencies:

```bash
npm install
```

### Running Locally

Start the local development server:

```bash
npm start
```

The website will be available at `http://localhost:8080`

## Production Deployment

### Option 1: Docker (Recommended)

Deploy using Docker and Docker Compose with PostgreSQL, nginx, and SSL support:

```bash
# 1. Clone and configure
git clone https://github.com/doronpers/spatial-selecta.git
cd spatial-selecta
cp .env.docker .env

# 2. Edit .env with your Apple Music token and settings
# 3. Generate SSL certificate (self-signed for testing)
./docker/generate-ssl-cert.sh localhost

# 4. Start all services
docker-compose up -d

# 5. Visit https://localhost ✅
```

See [docs/DOCKER.md](docs/DOCKER.md) for detailed Docker deployment instructions.

### Option 2: Render.com

**Quick Deploy to Render.com:**

1. **Prerequisites:**
   - Get Apple Music Developer Token (see [docs/SETUP.md](docs/SETUP.md) for instructions)
   - Render.com account
   - Optional: Custom domain for production use

2. **Deploy:**  
   See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for step-by-step deployment instructions

**TL;DR:**

```bash
# 1. Deploy to Render using Blueprint (connect GitHub repo)
# 2. Add APPLE_MUSIC_DEVELOPER_TOKEN to Render environment
# 3. Optional: Add custom domain in Render dashboard
# 4. Optional: Update DNS records to point to Render
# 5. Visit your site URL ✅
```

## Project Structure

```text
spatialselects/
├── index.html      # Main HTML structure
├── styles.css      # Styling and responsive design
├── app.js          # JavaScript application logic
├── data.json       # Music releases data
├── package.json    # Project dependencies
└── README.md       # Documentation
```

## How It Works

1. **Backend Discovery**: Python backend automatically scans Apple Music playlists every 48 hours for spatial audio tracks
2. **Data Storage**: Discovered tracks are stored in a database (SQLite for development, PostgreSQL for production)
3. **API**: FastAPI backend provides REST endpoints for querying tracks
4. **Frontend Display**: Frontend loads tracks from the API (with fallback to `data.json`) and displays them in a responsive grid
5. **Filtering**: Users can filter by platform and format in real-time
6. **Manual Refresh**: Users can manually refresh data using the refresh button (reloads from API)

## Adding New Releases

**IMPORTANT**: All new tracks must follow the standardized format documented in [docs/DATA_FORMAT.md](docs/DATA_FORMAT.md).

To add new spatial audio releases, edit the `data.json` file with the following structure:

```json
{
  "id": 13,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2023-01-15",
  "atmosReleaseDate": "2023-01-15",
  "albumArt": "🎵",
  "musicLink": "https://music.apple.com/us/song/song-name/TRACK_ID"
}
```

**Key Requirements**:

- `musicLink` must be a valid Apple Music URL with correct IDs (see [docs/DATA_FORMAT.md](docs/DATA_FORMAT.md))
- `releaseDate` is the original song release date
- `atmosReleaseDate` is when the Dolby Atmos mix became available
- Both dates must be in YYYY-MM-DD format

For detailed instructions on finding correct Apple Music links and Atmos release dates, see [docs/DATA_FORMAT.md](docs/DATA_FORMAT.md).

### Supported Formats

- Dolby Atmos
- 360 Reality Audio

### Supported Platforms

- Apple Music
- Amazon Music

## Backend API

SpatialSelects.com includes a Python backend that automatically detects and tracks spatial audio releases using the Apple Music API.

### Backend Features

- **Apple Music API Integration**: Automatically detects Dolby Atmos tracks using the `audioVariants` API attribute
- **Automated Discovery**: Background scheduler runs every 48 hours to find new spatial audio releases
- **Comprehensive Discovery**: Scans curated playlists, new music charts, album releases, and search results
- **REST API**: Provides endpoints for querying spatial audio tracks with filtering
- **Database Storage**: Persistent storage of track metadata and discovery timestamps
- **Rate Limiting**: Built-in rate limiting for API protection
- **Security**: Security headers, input validation, and authentication for sensitive endpoints

### Backend Setup

**🚀 Deploy to Production (Recommended):**
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment instructions to Render.com

**Local Development:**
See [Setup Guide](docs/SETUP.md) for detailed setup instructions.

**Quick start:**

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

1. Configure Apple Music API credentials:

```bash
cp .env.example .env
# Edit .env and add your Apple Music Developer Token
# OR ensure your .p8 private key file is in the project root for automatic generation
```

1. Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

1. Access API documentation at `http://localhost:8000/docs`

### Testing

Run the automated test suite to ensure backend stability:

```bash
pytest tests/
```

### API Endpoints

**Track Endpoints:**
- `GET /api/tracks` - List all spatial audio tracks (with platform/format filtering, pagination)
  - Query parameters: `platform`, `format`, `limit`, `offset`
- `GET /api/tracks/new` - Get recently released tracks (default: last 30 days)
  - Query parameters: `days` (1-365)
- `GET /api/tracks/{track_id}` - Get specific track by ID

**Refresh Endpoints:**
- `POST /api/refresh` - Manually trigger data refresh (requires authentication token)
- `POST /api/refresh/sync` - Public endpoint to trigger refresh (rate limited: 1 per hour per IP)
- `GET /api/refresh/status` - Check if public refresh is available

**Community Endpoints:**
- `POST /api/tracks/{track_id}/rate` - Submit community rating for a track
  - Body: `{"score": 1-10, "is_fake": boolean}`

**Engineer Endpoints:**
- `GET /api/engineers` - List engineers sorted by mix count
  - Query parameters: `limit`, `min_mixes`
- `GET /api/engineers/{engineer_id}` - Get engineer details

**Utility Endpoints:**
- `GET /api/stats` - Get database statistics
- `GET /api/health` - Health check endpoint

**Authentication:**
- Protected endpoints require `Authorization: Bearer <token>` header
- Set `REFRESH_API_TOKEN` environment variable for authentication

## Future Enhancements

- Amazon Music API integration (currently manual data entry)
- User accounts and favorites
- Playlist creation
- Email notifications for new releases
- Search functionality (frontend search)
- Genre filtering
- Artist page views
- WebSocket support for real-time updates
- Improved credits scraping (currently basic implementation)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
