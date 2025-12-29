# Track Data Format Guide

Complete guide for the track data structure used in SpatialSelects.com.

## Overview

All tracks must follow a consistent format to ensure data accuracy and proper functionality, especially for Apple Music links and release date tracking.

## Required Fields

Each track entry must include the following fields:

```json
{
  "id": 1,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2023-01-15",
  "atmosReleaseDate": "2023-01-15",
  "albumArt": "🎵",
  "musicLink": "https://music.apple.com/us/album/album-name/1234567890?i=1234567891"
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
- **Description**: Audio format
- **Allowed Values**: `"Dolby Atmos"`, `"360 Reality Audio"`
- **Example**: `"Dolby Atmos"`

### `platform` (required)
- **Type**: String
- **Description**: Music platform
- **Allowed Values**: `"Apple Music"`, `"Amazon Music"`
- **Example**: `"Apple Music"`

### `releaseDate` (required)
- **Type**: String (ISO date format)
- **Description**: Original song release date
- **Format**: `YYYY-MM-DD`
- **Example**: `"2020-02-29"`
- **Rules**: Must be a valid date in ISO format

### `atmosReleaseDate` (required)
- **Type**: String (ISO date format)
- **Description**: Date when Dolby Atmos mix became available
- **Format**: `YYYY-MM-DD`
- **Example**: `"2023-01-15"`
- **Rules**: Must be a valid date in ISO format, can be same as `releaseDate`

### `albumArt` (optional)
- **Type**: String
- **Description**: Album art emoji or placeholder
- **Example**: `"🎵"` or `"🎤"`
- **Default**: `"🎵"`

### `musicLink` (required)
- **Type**: String (URL)
- **Description**: Direct link to the track on the platform
- **Format**: Valid HTTPS URL
- **Example**: `"https://music.apple.com/us/album/album-name/1234567890?i=1234567891"`
- **Rules**: Must be a valid HTTPS URL, must point to the correct track

## Optional Fields

### `credits` (optional)
- **Type**: Array of objects
- **Description**: Mix engineer credits
- **Example**: `[{"name": "Engineer Name", "role": "Mixing Engineer"}]`

### `avgImmersiveness` (optional)
- **Type**: Number
- **Description**: Average community rating (1-10)
- **Example**: `8.5`

### `hallOfShame` (optional)
- **Type**: Boolean
- **Description**: Flag for fake Atmos mixes
- **Example**: `false`
- **Default**: `false`

## Apple Music Link Format

### Finding the Correct Link

1. **Open Apple Music** (web or app)
2. **Navigate to the track**
3. **Right-click** (or long-press) → **Copy Link**
4. **Verify the link format**

### Link Structure

Apple Music links follow this format:

```
https://music.apple.com/{storefront}/album/{album-name}/{album-id}?i={track-id}
```

**Example:**
```
https://music.apple.com/us/album/after-hours/1500000000?i=1500000001
```

**Components:**
- `{storefront}`: Country code (e.g., `us`, `gb`, `ca`)
- `{album-name}`: URL-friendly album name (not critical)
- `{album-id}`: Numeric album ID (required)
- `{track-id}`: Numeric track ID (required, in query parameter)

### Important Notes

- **Album ID and Track ID are required** - the link won't work without them
- **Storefront should match your target audience** (usually `us`)
- **Test the link** - ensure it opens the correct track in Apple Music

## Date Format

### ISO 8601 Format

All dates must use ISO 8601 format: `YYYY-MM-DD`

**Valid Examples:**
- `"2023-01-15"`
- `"2020-02-29"` (leap year)
- `"2024-12-31"`

**Invalid Examples:**
- `"01/15/2023"` (wrong format)
- `"2023-1-5"` (missing leading zeros)
- `"2023-13-01"` (invalid month)
- `"2023-02-30"` (invalid date)

### Finding Release Dates

**Original Release Date (`releaseDate`):**
- Check album release date on Apple Music
- Use the original album release date, not re-release dates

**Atmos Release Date (`atmosReleaseDate`):**
- Check when the Dolby Atmos mix was added
- May be different from original release date
- If unknown, use original release date

## Complete Example

```json
{
  "id": 13,
  "title": "Blinding Lights",
  "artist": "The Weeknd",
  "album": "After Hours",
  "format": "Dolby Atmos",
  "platform": "Apple Music",
  "releaseDate": "2020-02-29",
  "atmosReleaseDate": "2023-01-15",
  "albumArt": "🌃",
  "musicLink": "https://music.apple.com/us/album/after-hours/1500000000?i=1500000001",
  "credits": [
    {
      "name": "Serban Ghenea",
      "role": "Mixing Engineer"
    }
  ],
  "avgImmersiveness": 8.5,
  "hallOfShame": false
}
```

## Validation Rules

### Required Field Validation

All required fields must be present and non-empty:
- `id`, `title`, `artist`, `album`, `format`, `platform`, `releaseDate`, `atmosReleaseDate`

### Date Validation

- Dates must be valid ISO format (`YYYY-MM-DD`)
- Dates must represent valid calendar dates
- `atmosReleaseDate` should be >= `releaseDate` (not enforced but recommended)

### URL Validation

- `musicLink` must be a valid HTTPS URL
- Must point to the correct platform (Apple Music or Amazon Music)
- Must include required IDs for Apple Music links

### Format/Platform Validation

- `format` must be one of: `"Dolby Atmos"`, `"360 Reality Audio"`
- `platform` must be one of: `"Apple Music"`, `"Amazon Music"`

## Adding Tracks to data.json

1. **Get all required information:**
   - Title, artist, album
   - Release dates
   - Apple Music link
   - Format and platform

2. **Find the next available ID:**
   - Check existing tracks in `data.json`
   - Use the highest ID + 1

3. **Create track object:**
   - Follow the format above
   - Validate all fields
   - Test the Apple Music link

4. **Add to data.json:**
   - Append to the array
   - Maintain valid JSON syntax
   - No trailing commas

5. **Verify:**
   - JSON is valid (use a JSON validator)
   - All required fields are present
   - Dates are valid
   - Link works

## Common Mistakes

### ❌ Wrong Date Format
```json
"releaseDate": "01/15/2023"  // Wrong!
```
✅ Correct:
```json
"releaseDate": "2023-01-15"
```

### ❌ Missing Track ID in Apple Music Link
```json
"musicLink": "https://music.apple.com/us/album/after-hours/1500000000"  // Missing ?i=
```
✅ Correct:
```json
"musicLink": "https://music.apple.com/us/album/after-hours/1500000000?i=1500000001"
```

### ❌ Invalid Format Value
```json
"format": "Dolby"  // Wrong!
```
✅ Correct:
```json
"format": "Dolby Atmos"
```

### ❌ Duplicate IDs
```json
{"id": 1, ...},
{"id": 1, ...}  // Duplicate!
```
✅ Correct:
```json
{"id": 1, ...},
{"id": 2, ...}
```

## API Response Format

When tracks are returned from the API, field names use snake_case:

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

**Note:** The frontend automatically converts between camelCase (data.json) and snake_case (API) formats.

## Support

For questions about track data format:
- See examples in `data.json`
- Check API responses for format
- Open an issue on GitHub

