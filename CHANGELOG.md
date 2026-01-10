# Changelog

All notable changes to SpatialSelects.com will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CONTRIBUTING.md with comprehensive contribution guidelines
- LICENSE file (MIT License)
- CHANGELOG.md to track project changes

## [1.0.0] - 2024-01-01

### Added

- Initial release of SpatialSelects.com
- Frontend website with responsive design
- Track listing with filtering by platform and format
- Python FastAPI backend with Apple Music API integration
- Automated discovery of Dolby Atmos tracks every 48 hours
- Database storage (SQLite for dev, PostgreSQL for production)
- REST API endpoints for track querying
- Manual sync button for on-demand updates
- Engineer index view (data loading implemented)
- Hardware guide view
- Community rating system (API endpoints)
- "New" badge for releases within last 30 days
- Platform filtering (Apple Music, Amazon Music)
- Format filtering (Dolby Atmos, 360 Reality Audio)
- Security features:
  - Content Security Policy
  - Input validation and HTML escaping
  - HTTPS URL validation
  - Rate limiting for public endpoints
- Comprehensive documentation:
  - README.md with quick start guide
  - Documentation/Guides/DEVELOPMENT.md for architecture and development
  - Documentation/Guides/SETUP.md for detailed setup instructions
  - Documentation/Guides/DEPLOYMENT.md for production deployment
  - Documentation/Reference/DATA_FORMAT.md for track data specifications
  - Documentation/Reference/API.md for API endpoint documentation
  - Documentation/Reference/SECURITY.md for security guidelines
  - backend/README.md for backend-specific docs
- Deployment configuration:
  - Render.com blueprint (render.yaml)
  - Docker support (Dockerfile)
  - Docker Compose example
  - Nginx configuration example
  - Production setup script
- Environment configuration templates:
  - .env.example for development
  - .env.production.example for production
- Data fallback system (data.json when API unavailable)
- Automatic API URL detection (localhost vs production)
- Error handling and user-friendly error messages
- Loading states and visual feedback
- Minimalist, typography-focused design
- Mobile-responsive layout

### Backend Features

- Apple Music API client with developer token authentication
- Spatial audio detection via `audioVariants` attribute
- Monitoring of curated Spatial Audio playlists
- Background scheduler with APScheduler
- SQLAlchemy ORM for database management
- Track deduplication using Apple Music IDs
- Timestamp tracking for discovery and updates
- Pagination support for API endpoints
- Health check endpoint
- Statistics endpoint
- Community rating endpoints
- Engineer query endpoints
- Refresh status checking with rate limiting

### Developer Experience

- Local development with hot reload
- Interactive API documentation at /docs
- Clear project structure
- Code organization by feature
- Validation for dates, URLs, and track data
- Helpful error messages for common issues
- File protocol detection and guidance

## Release Types

### Major Version (X.0.0)

- Significant architectural changes
- Breaking API changes
- Major feature additions

### Minor Version (0.X.0)

- New features
- Enhancements to existing features
- Non-breaking API changes

### Patch Version (0.0.X)

- Bug fixes
- Documentation updates
- Performance improvements
- Security patches

## Categories

### Added

New features and capabilities

### Changed

Changes to existing functionality

### Deprecated

Features that will be removed in future releases

### Removed

Features that have been removed

### Fixed

Bug fixes

### Security

Security improvements and vulnerability fixes

---

## Future Roadmap

Planned enhancements for future releases:

- Amazon Music API integration
- User accounts and favorites
- Playlist creation
- Email notifications for new releases
- Frontend search functionality
- Genre filtering
- Artist page views
- WebSocket support for real-time updates
- Improved credits scraping
- More comprehensive test coverage
- Performance optimizations
- Additional spatial audio format support
