# API Documentation

Complete reference for the SpatialSelects.com backend API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://spatial-selecta-api.onrender.com` (or your custom domain)

## Authentication

Most endpoints are public. Protected endpoints require:

```
Authorization: Bearer <REFRESH_API_TOKEN>
```

Set `REFRESH_API_TOKEN` in environment variables for authentication.

## Track Endpoints

### List Tracks

Get all spatial audio tracks with optional filtering.

**Endpoint:** `GET /api/tracks`

**Query Parameters:**
- `platform` (optional): Filter by platform (`Apple Music`, `Amazon Music`)
- `format` (optional): Filter by format (`Dolby Atmos`, `360 Reality Audio`)
- `limit` (optional): Number of results (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

**Example:**
```bash
curl "https://spatial-selecta-api.onrender.com/api/tracks?platform=Apple%20Music&format=Dolby%20Atmos&limit=10"
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "format": "Dolby Atmos",
    "platform": "Apple Music",
    "release_date": "2023-01-15",
    "atmos_release_date": "2023-01-15",
    "album_art": "🎵",
    "music_link": "https://music.apple.com/...",
    "credits": [],
    "avg_immersiveness": null,
    "hall_of_shame": false
  }
]
```

### Get Recent Tracks

Get tracks released within a specified time period.

**Endpoint:** `GET /api/tracks/new`

**Query Parameters:**
- `days` (optional): Number of days to look back (default: 30, max: 365)

**Example:**
```bash
curl "https://spatial-selecta-api.onrender.com/api/tracks/new?days=7"
```

### Get Track by ID

Get a specific track by its ID.

**Endpoint:** `GET /api/tracks/{track_id}`

**Example:**
```bash
curl "https://spatial-selecta-api.onrender.com/api/tracks/1"
```

**Response:**
```json
{
  "id": 1,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "release_date": "2023-01-15",
  "atmos_release_date": "2023-01-15",
  "album_art": "🎵",
  "music_link": "https://music.apple.com/...",
  "credits": [],
  "avg_immersiveness": null,
  "hall_of_shame": false
}
```

## Refresh Endpoints

### Manual Refresh (Protected)

Manually trigger a scan for new spatial audio releases.

**Endpoint:** `POST /api/refresh`

**Authentication:** Required (Bearer token)

**Headers:**
```
Authorization: Bearer <REFRESH_API_TOKEN>
```

**Example:**
```bash
curl -X POST https://spatial-selecta-api.onrender.com/api/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_API_TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "message": "Refresh completed: 5 tracks added, 2 updated",
  "tracks_added": 5,
  "tracks_updated": 2,
  "timestamp": "2025-01-27T12:00:00Z"
}
```

### Public Sync (Rate Limited)

Public endpoint to trigger refresh. Rate limited to 1 request per hour per IP.

**Endpoint:** `POST /api/refresh/sync`

**Example:**
```bash
curl -X POST https://spatial-selecta-api.onrender.com/api/refresh/sync
```

**Response:**
```json
{
  "status": "success",
  "tracks_added": 3,
  "timestamp": "2025-01-27T12:00:00Z"
}
```

**Rate Limit:**
- 1 request per hour per IP address
- Returns `429 Too Many Requests` if exceeded

### Check Sync Status

Check if public sync is available (not rate limited).

**Endpoint:** `GET /api/refresh/status`

**Example:**
```bash
curl https://spatial-selecta-api.onrender.com/api/refresh/status
```

**Response:**
```json
{
  "can_refresh": true,
  "seconds_until_available": 0
}
```

Or if rate limited:
```json
{
  "can_refresh": false,
  "seconds_until_available": 1800
}
```

## Community Endpoints

### Rate a Track

Submit a community rating for a track's immersiveness.

**Endpoint:** `POST /api/tracks/{track_id}/rate`

**Body:**
```json
{
  "score": 8,
  "is_fake": false
}
```

**Parameters:**
- `score` (required): Rating from 1-10
- `is_fake` (optional): Boolean indicating if track is fake Atmos

**Example:**
```bash
curl -X POST https://spatial-selecta-api.onrender.com/api/tracks/1/rate \
  -H "Content-Type: application/json" \
  -d '{"score": 8, "is_fake": false}'
```

**Response:**
```json
{
  "track_id": 1,
  "avg_score": 8.5,
  "total_ratings": 3,
  "avg_immersiveness": 8.5,
  "hall_of_shame": false
}
```

## Engineer Endpoints

### List Engineers

Get list of mix engineers sorted by mix count.

**Endpoint:** `GET /api/engineers`

**Query Parameters:**
- `limit` (optional): Number of results (default: 50)
- `min_mixes` (optional): Minimum number of mixes (default: 1)

**Example:**
```bash
curl "https://spatial-selecta-api.onrender.com/api/engineers?limit=10&min_mixes=5"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Engineer Name",
    "mix_count": 25,
    "profile_image_url": "https://..."
  }
]
```

### Get Engineer Details

Get detailed information about a specific engineer.

**Endpoint:** `GET /api/engineers/{engineer_id}`

**Example:**
```bash
curl https://spatial-selecta-api.onrender.com/api/engineers/1
```

## Utility Endpoints

### Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /api/health`

**Example:**
```bash
curl https://spatial-selecta-api.onrender.com/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T12:00:00Z"
}
```

### Get Statistics

Get database statistics about tracks.

**Endpoint:** `GET /api/stats`

**Example:**
```bash
curl https://spatial-selecta-api.onrender.com/api/stats
```

**Response:**
```json
{
  "total_tracks": 150,
  "by_platform": {
    "Apple Music": 120,
    "Amazon Music": 30
  },
  "by_format": {
    "Dolby Atmos": 140,
    "360 Reality Audio": 10
  },
  "new_tracks_last_30_days": 25
}
```

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Example Error Response

```json
{
  "detail": "Track not found"
}
```

## Rate Limiting

- **Public endpoints**: No rate limiting (except `/api/refresh/sync`)
- **Protected endpoints**: No rate limiting (authentication required)
- **Sync endpoint**: 1 request per hour per IP address

## API Documentation (Interactive)

When running locally or in development, interactive API documentation is available:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These are automatically disabled in production (`ENVIRONMENT=production`).

## CORS

The API supports CORS for configured origins. Set `ALLOWED_ORIGINS` environment variable:

```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Important:**
- No wildcards (`*`) allowed in production
- Include protocol (`https://`)
- No trailing slashes
- Comma-separated for multiple origins

## Examples

### Get All Apple Music Dolby Atmos Tracks

```bash
curl "https://spatial-selecta-api.onrender.com/api/tracks?platform=Apple%20Music&format=Dolby%20Atmos"
```

### Get Tracks from Last 7 Days

```bash
curl "https://spatial-selecta-api.onrender.com/api/tracks/new?days=7"
```

### Trigger Manual Refresh

```bash
curl -X POST https://spatial-selecta-api.onrender.com/api/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Submit Track Rating

```bash
curl -X POST https://spatial-selecta-api.onrender.com/api/tracks/1/rate \
  -H "Content-Type: application/json" \
  -d '{"score": 9, "is_fake": false}'
```

## Support

For API issues or questions:
- Check interactive docs at `/docs` (development only)
- Review backend logs
- Open an issue on GitHub

