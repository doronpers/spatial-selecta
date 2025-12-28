# SpatialSelects.com 🎵

A website that automatically tracks and displays the latest music releases available in Dolby Atmos spatial audio format on Apple Music.

## Features

- **Automated Discovery**: Backend automatically scans for new spatial audio releases every 48 hours
- **Engineer Index**: Explore top mix engineers and their portfolios
- **Community Ratings**: Rate immersiveness and flag fake Atmos mixes
- **Hardware Guide**: Educational resources for optimal listening
- **Platform Filtering**: Filter by platform (Apple Music, Amazon Music)
- **Format Filtering**: Filter by audio format (Dolby Atmos, 360 Reality Audio)
- **New Release Badges**: Highlights releases from the last 30 days
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Minimalist Interface**: Clean, typography-focused design

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

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

**Quick Deploy to Render.com + GoDaddy Domain:**

1. **Prerequisites:**
   - Get Apple Music Developer Token ([instructions](GODADDY_DOMAIN_SETUP.md#apple-music-api-token-setup))
   - Render.com account
   - GoDaddy DNS access

2. **Deploy:**  
   See [Quick Start Guide](DEPLOYMENT_QUICKSTART.md) for step-by-step instructions

3. **Full Documentation:**  
   [Complete GoDaddy + Render Setup Guide](GODADDY_DOMAIN_SETUP.md)

**TL;DR:**

```bash
# 1. Deploy to Render using Blueprint (connect GitHub repo)
# 2. Add APPLE_MUSIC_DEVELOPER_TOKEN to Render environment
# 3. Add custom domains in Render: spatialselects.com + www
# 4. Update GoDaddy DNS with A and CNAME records from Render
# 5. Wait 10-30 minutes for DNS propagation
# 6. Visit https://spatialselects.com ✅
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

**IMPORTANT**: All new tracks must follow the standardized format documented in [TRACK_DATA_FORMAT.md](TRACK_DATA_FORMAT.md).

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

- `musicLink` must be a valid Apple Music URL with correct IDs (see [TRACK_DATA_FORMAT.md](TRACK_DATA_FORMAT.md))
- `releaseDate` is the original song release date
- `atmosReleaseDate` is when the Dolby Atmos mix became available
- Both dates must be in YYYY-MM-DD format

For detailed instructions on finding correct Apple Music links and Atmos release dates, see [TRACK_DATA_FORMAT.md](TRACK_DATA_FORMAT.md).

### Supported Formats

- Dolby Atmos
- 360 Reality Audio

### Supported Platforms

- Apple Music
- Amazon Music

## Backend API

SpatialSelects.com now includes a Python backend that automatically detects and tracks spatial audio releases using the Apple Music API.

### Backend Features

- **Apple Music API Integration**: Automatically detects Dolby Atmos tracks using the `audioVariants` API attribute
- **Automated Discovery**: Background scheduler runs every 48 hours to find new spatial audio releases
- **Playlist Monitoring**: Tracks curated Apple playlists like "Made for Spatial Audio"
- **REST API**: Provides endpoints for querying spatial audio tracks with filtering
- **Database Storage**: Persistent storage of track metadata and discovery timestamps

### Backend Setup

**🚀 Deploy to Production (Recommended):**
See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for easy deployment to Render.com (10 minutes, $7/month)

**Local Development:**
See [backend/README.md](backend/README.md) for detailed setup instructions.

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

### API Endpoints

- `GET /api/tracks` - List all spatial audio tracks (with platform/format filtering)
- `GET /api/tracks/new` - Get recently released tracks
- `POST /api/refresh` - Manually trigger data refresh
- `GET /api/stats` - Get database statistics

## Future Enhancements

- Apple Music API integration (Done)
- Amazon Music API integration
- User accounts and favorites
- Playlist creation
- Email notifications for new releases
- Search functionality
- Genre filtering
- Artist page views
- WebSocket support for real-time updates

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
