# Development Guide

Architecture, code organization, and development guidelines for SpatialSelects.com.

## Architecture Overview

SpatialSelects.com consists of:

1. **Frontend**: Static HTML/CSS/JS website
2. **Backend**: Python FastAPI server with Apple Music API integration
3. **Database**: SQLite (development) or PostgreSQL (production)
4. **Scheduler**: Background job that runs every 48 hours

## Technology Stack

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: SQLite/PostgreSQL
- **Scheduler**: APScheduler for background jobs
- **API Integration**: Apple Music API

## Project Structure

```
spatial-selecta/
├── index.html              # Main HTML structure
├── styles.css              # Styling and responsive design
├── app.js                  # Frontend application logic
├── data.json               # Music releases data (fallback)
├── package.json            # Frontend dependencies
├── requirements.txt        # Backend Python dependencies
├── render.yaml             # Render.com deployment blueprint
├── backend/
│   ├── main.py            # FastAPI application and endpoints
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── database.py        # Database configuration
│   ├── scheduler.py       # Background job scheduler
│   └── apple_music_client.py  # Apple Music API client
└── docs/                   # Documentation
```

## Frontend Architecture

### Application State

- `allTracks`: Array of all loaded tracks
- `filteredTracks`: Array of tracks matching current filters
- `currentFilters`: Object with active filter selections
  - `platform`: 'all' | 'Apple Music' | 'Amazon Music'
  - `format`: 'all' | 'Dolby Atmos' | '360 Reality Audio'

### Key Functions

- `loadMusicData()`: Fetches tracks from API or fallback to data.json
- `applyFilters()`: Filters tracks based on current filter state
- `renderTracks()`: Renders filtered tracks to the DOM
- `setupFilters()`: Attaches event handlers to filter dropdowns

### API URL Detection

The frontend automatically detects the API URL:
- `file://` protocol → `http://localhost:8000`
- `localhost` or `127.0.0.1` → `http://localhost:8000`
- Production domains → `https://api.spatialselects.com`
- Render subdomains → Auto-detected backend URL

## Backend Architecture

### Key Components

1. **Apple Music API Client** (`apple_music_client.py`)
   - Authenticates with developer token
   - Queries tracks with `audioVariants` attribute
   - Monitors curated Spatial Audio playlists

2. **Background Scheduler** (`scheduler.py`)
   - Runs every 48 hours
   - Scans for new spatial audio releases
   - Updates existing tracks

3. **Database Layer** (`database.py`, `models.py`)
   - Stores track metadata
   - Tracks release dates and discovery timestamps
   - Maintains Apple Music IDs for deduplication

4. **API Endpoints** (`main.py`)
   - REST API for querying tracks
   - Filtering, pagination, and statistics
   - Manual refresh triggers

## Development Workflow

### Local Development

1. **Start Backend:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   python -m http.server 8080
   # or
   npm start
   ```

3. **Access:**
   - Frontend: http://localhost:8080
   - API Docs: http://localhost:8000/docs

### Code Style

**JavaScript:**
- Use ES6+ features (arrow functions, const/let, template literals)
- Use descriptive function and variable names
- Keep functions focused on single responsibility
- Comment complex logic

**Python:**
- Follow PEP 8 style guide
- Use type hints where appropriate
- Document functions with docstrings
- Keep functions focused

### Testing

**Manual Testing Checklist:**
- [ ] Page loads and displays tracks
- [ ] Filters work correctly
- [ ] Refresh button reloads data
- [ ] "New" badge appears for recent releases
- [ ] Responsive design works on mobile/tablet
- [ ] Empty state shows when filters return no results

**API Testing:**
- Use interactive docs at `/docs`
- Test all endpoints with curl
- Verify error handling

## Adding Features

### Adding a New Filter

1. Update HTML (`index.html`):
   - Add new `<option>` to the appropriate `<select>`

2. Update JavaScript (`app.js`):
   - Add filter property to `currentFilters`
   - Update `applyFilters()` logic
   - Add event listener

### Adding a New API Endpoint

1. Define schema (`schemas.py`):
   - Create Pydantic model for request/response

2. Create endpoint (`main.py`):
   - Add route decorator
   - Implement logic
   - Add validation and error handling

3. Update documentation:
   - Add to API docs
   - Update README if needed

### Adding a New Database Model

1. Define model (`models.py`):
   - Create SQLAlchemy model class
   - Define relationships

2. Create migration:
   - Use Alembic for schema changes
   - Test migration on development database

## Common Tasks

### Adding a New Track

1. Open `data.json`
2. Find the highest `id` value
3. Create new track object with `id: <highest + 1>`
4. Add to array (maintain JSON syntax)
5. Save file
6. Test by refreshing the page

### Updating Dependencies

**Frontend:**
```bash
npm update
```

**Backend:**
```bash
pip install -r requirements.txt --upgrade
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Debugging

### Frontend Issues

- Check browser console for errors
- Verify API URL detection
- Check network tab for failed requests
- Verify data.json format is valid JSON

### Backend Issues

- Check backend logs
- Verify environment variables are set
- Test API endpoints with curl
- Check database connectivity

### Common Issues

**CORS errors:**
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check protocol matches (http vs https)

**API not responding:**
- Verify backend is running
- Check port conflicts
- Verify API URL in frontend

**Database errors:**
- Check `DATABASE_URL` is correct
- Verify database is accessible
- Check user permissions

## Performance Considerations

- **Frontend**: Minimal JavaScript, no heavy frameworks
- **Backend**: Async endpoints, connection pooling
- **Database**: Indexed queries, efficient filtering
- **Caching**: Consider adding Redis for rate limiting

## Future Enhancements

- WebSocket support for real-time updates
- Search functionality
- User authentication
- Advanced filtering (genre, artist)
- Playlist creation
- Email notifications

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Apple Music API Documentation](https://developer.apple.com/documentation/applemusicapi)

