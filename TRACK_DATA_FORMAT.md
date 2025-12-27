# Track Data Format Guide

This document describes the required format for adding new tracks to the Spatial Selecta database.

## Overview

All tracks must follow a consistent format to ensure data accuracy and proper functionality, especially for Apple Music links and release date tracking.

## Required Fields

Each track entry in `data.json` must include the following fields:

```json
{
  "id": 1,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "YYYY-MM-DD",
  "atmosReleaseDate": "YYYY-MM-DD",
  "albumArt": "🎵",
  "musicLink": "https://music.apple.com/us/...",
  "review": "Optional review text",
  "technicalDetails": "Optional technical details",
  "comparisonNotes": "Optional platform comparison notes"
}
```

## Field Specifications

### `id` (required)
- **Type**: Integer
- **Description**: Unique identifier for the track
- **Example**: `1`
- **Rules**: Must be a positive integer, unique across all tracks

### `title` (required)
- **Type**: String
- **Description**: The song title
- **Example**: `"Blinding Lights"`
- **Rules**: Must match the exact title on Apple Music

### `artist` (required)
- **Type**: String
- **Description**: The artist name
- **Example**: `"The Weeknd"`
- **Rules**: Must match the exact artist name on Apple Music

### `album` (required)
- **Type**: String
- **Description**: The album name
- **Example**: `"After Hours"`
- **Rules**: Must match the exact album name on Apple Music

### `format` (required)
- **Type**: String
- **Description**: The spatial audio format
- **Example**: `"Dolby Atmos"`
- **Allowed values**: `"Dolby Atmos"`, `"360 Reality Audio"`

### `platform` (required)
- **Type**: String
- **Description**: The streaming platform
- **Example**: `"Apple Music"`
- **Allowed values**: `"Apple Music"`, `"Amazon Music"`

### `releaseDate` (required)
- **Type**: String (ISO 8601 date format)
- **Description**: The original song release date
- **Format**: `YYYY-MM-DD`
- **Example**: `"2019-11-29"`
- **Rules**: Must be the actual date the song was originally released, not when the Atmos mix became available

### `atmosReleaseDate` (strongly recommended, required for new tracks)
- **Type**: String (ISO 8601 date format)
- **Description**: The date the Dolby Atmos/spatial audio mix was released
- **Format**: `YYYY-MM-DD`
- **Example**: `"2021-06-07"`
- **Rules**: 
  - **REQUIRED for all new tracks added to the system**
  - Optional for backwards compatibility with existing data
  - Must be the date when the Atmos mix became available on the platform
  - Can be the same as `releaseDate` if the song was released with Atmos from day one
  - Must be >= `releaseDate`
  - If unknown, use the album's Atmos release date or June 7, 2021 (Apple Music Spatial Audio launch)

### `albumArt` (required)
- **Type**: String (emoji)
- **Description**: Emoji representation for the album art
- **Example**: `"🌃"`
- **Rules**: Must be a single emoji character

### `musicLink` (required)
- **Type**: String (URL)
- **Description**: Direct link to the song on Apple Music
- **Format**: Must be a valid Apple Music HTTPS URL
- **Examples**:
  - Album link: `https://music.apple.com/us/album/album-name/ALBUM_ID`
  - Track link: `https://music.apple.com/us/song/song-name/TRACK_ID`
  - Album with track: `https://music.apple.com/us/album/song-name/ALBUM_ID?i=TRACK_ID`
- **Rules**: 
  - Must be a valid HTTPS URL (HTTP not allowed - Apple Music only uses HTTPS)
  - Must link to the correct song/album on Apple Music
  - Must use actual Apple Music IDs (not fabricated numbers)
  - Will be validated to prevent security issues

### `review` (optional)
- **Type**: String
- **Description**: Review of the spatial audio mix
- **Example**: `"The Dolby Atmos mix elevates this track..."`

### `technicalDetails` (optional)
- **Type**: String
- **Description**: Technical information about the mix
- **Example**: `"7.1.4 channel mix with discrete height channel information..."`

### `comparisonNotes` (optional)
- **Type**: String
- **Description**: Platform-specific notes or comparisons
- **Example**: `"Currently exclusive to Apple Music..."`

## How to Get Correct Apple Music Links

### Method 1: Search on Apple Music Website
1. Go to https://music.apple.com/
2. Search for the song and artist
3. Navigate to the song page
4. Copy the URL from your browser
5. The URL will contain the correct album/track IDs

### Method 2: Use Apple Music API
If you have API access:
1. Search for the track using the Apple Music API
2. The response will include the track ID and URL
3. Use the URL from the `attributes.url` field

### Method 3: Verify IDs
Apple Music URLs follow these patterns:
- `https://music.apple.com/us/album/ALBUM_NAME/ALBUM_ID`
- `https://music.apple.com/us/song/SONG_NAME/TRACK_ID`
- `https://music.apple.com/us/album/SONG_NAME/ALBUM_ID?i=TRACK_ID`

**Always verify the link opens the correct song in Apple Music before adding it!**

## How to Find Atmos Release Dates

Finding the exact Atmos release date can be challenging. Use these methods:

### Method 1: MusicBrainz
1. Search for the album on https://musicbrainz.org/
2. Look for releases marked as "Dolby Atmos" or "Spatial Audio"
3. Check the release date for that specific version

### Method 2: Web Search
Search for: `"[Song Name]" "[Artist]" "Dolby Atmos" release date`

### Method 3: Streaming Platform History
- Check when the Atmos badge first appeared on Apple Music
- Look for press releases or artist announcements

### Method 4: Make an Educated Guess
If the exact date is unknown:
- Use the album's Atmos release date
- Use June 7, 2021 (when Apple Music launched Spatial Audio) for older catalog releases
- For same-day releases, use the same date as `releaseDate`

## Validation

The system validates the following:
- All required fields are present
- `id` is a positive integer
- `releaseDate` and `atmosReleaseDate` are in YYYY-MM-DD format
- Both dates are valid dates
- `format` is one of the allowed values
- `platform` is one of the allowed values
- `musicLink` is a valid HTTPS URL (not javascript: or data: URLs)

## Examples

### Example 1: Song with Same Release Date
```json
{
  "id": 1,
  "title": "Anti-Hero",
  "artist": "Taylor Swift",
  "album": "Midnights",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2022-10-21",
  "atmosReleaseDate": "2022-10-21",
  "albumArt": "🌙",
  "musicLink": "https://music.apple.com/us/song/anti-hero/1650841515"
}
```

### Example 2: Song with Later Atmos Release
```json
{
  "id": 2,
  "title": "Blinding Lights",
  "artist": "The Weeknd",
  "album": "After Hours",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2019-11-29",
  "atmosReleaseDate": "2021-06-07",
  "albumArt": "🌃",
  "musicLink": "https://music.apple.com/us/album/blinding-lights-single/1488408555"
}
```

### Example 3: Track with Album Link
```json
{
  "id": 3,
  "title": "Kill Bill",
  "artist": "SZA",
  "album": "SOS",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2022-12-09",
  "atmosReleaseDate": "2022-12-09",
  "albumArt": "🆘",
  "musicLink": "https://music.apple.com/us/album/kill-bill/1657869377?i=1657869379"
}
```

## Common Mistakes to Avoid

1. **Using fabricated Apple Music IDs**: Always get the real ID from Apple Music
2. **Wrong release dates**: Use the original song release date, not when you added it
3. **Missing atmosReleaseDate**: This field is required, even if it's the same as releaseDate
4. **Invalid date formats**: Must be YYYY-MM-DD, not MM/DD/YYYY or other formats
5. **Non-HTTPS links**: All links must use HTTPS protocol
6. **Incorrect platform values**: Must exactly match "Apple Music" or "Amazon Music"
7. **Wrong emoji type**: albumArt must be an emoji string, not an image URL

## Backend Integration

When using the backend API to add tracks programmatically:
- The backend automatically extracts track information from Apple Music API
- It generates the `musicLink` using the `attributes.url` field from the API
- Release dates are parsed from the API response
- The backend validates all data before storing

For manual additions to data.json, follow this guide strictly to maintain data integrity.
