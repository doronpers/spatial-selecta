# Spatial Selecta 🎵

A website that automatically tracks and displays the latest music releases available in Dolby Atmos spatial audio format on Apple Music.

## Features

- **Weekly Updates**: Automatically refreshes music data every Friday at 3 PM ET
- **Format Filtering**: Filter by audio format (Dolby Atmos)
- **New Release Badges**: Highlights releases from the last 30 days
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Minimalist Interface**: Clean, typography-focused design following Dieter Rams' principles

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

2. Install dependencies:
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

```
spatial-selecta/
├── index.html      # Main HTML structure
├── styles.css      # Styling and responsive design
├── app.js          # JavaScript application logic
├── data.json       # Music releases data
├── package.json    # Project dependencies
└── README.md       # Documentation
```

## How It Works

1. **Data Loading**: The app loads music releases from `data.json`
2. **Display**: Tracks are displayed in a responsive grid with album art, artist info, and format badges
3. **Filtering**: Users can filter by platform and format in real-time
4. **Auto-refresh**: Data automatically refreshes every Friday at 3 PM ET to show latest releases
5. **Manual Refresh**: Users can manually refresh data using the refresh button

## Adding New Releases

To add new spatial audio releases, edit the `data.json` file with the following structure:

```json
{
  "id": 13,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2024-12-23",
  "albumArt": "🎵"
}
```

### Supported Formats
- Dolby Atmos

### Supported Platforms
- Apple Music

## Backend API

Spatial Selecta now includes a Python backend that automatically detects and tracks spatial audio releases using the Apple Music API.

### Features

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

2. Configure Apple Music API credentials:
```bash
cp .env.example .env
# Edit .env and add your Apple Music Developer Token
```

3. Run the backend:
```bash
uvicorn backend.main:app --reload --port 8000
```

4. Access API documentation at `http://localhost:8000/docs`

### API Endpoints

- `GET /api/tracks` - List all spatial audio tracks (with platform/format filtering)
- `GET /api/tracks/new` - Get recently released tracks
- `POST /api/refresh` - Manually trigger data refresh
- `GET /api/stats` - Get database statistics

## Future Enhancements

- ✅ Integration with Apple Music API for automatic data fetching
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