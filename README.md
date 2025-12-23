# Spatial Selecta 🎵

A website that automatically tracks and displays the latest music releases available in immersive spatial audio formats like Dolby Atmos on Apple Music and Amazon Music.

## Features

- **Weekly Updates**: Automatically refreshes music data every Friday at 3 PM ET
- **Platform Filtering**: Filter releases by platform (Apple Music, Amazon Music)
- **Format Filtering**: Filter by audio format (Dolby Atmos, 360 Reality Audio)
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
- 360 Reality Audio

### Supported Platforms
- Apple Music
- Amazon Music

## Future Enhancements

- Integration with Apple Music and Amazon Music APIs for automatic data fetching
- User accounts and favorites
- Playlist creation
- Email notifications for new releases
- Search functionality
- Genre filtering
- Artist page views

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.