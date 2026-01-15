# Spatial Selecta - Agent Guidelines

**Purpose**: Comprehensive guide for AI agents working on the SpatialSelects.com project.

**Last Updated**: 2026-01-13

---

## Project Overview

**Spatial Selecta** is a minimalist website that tracks and displays the latest music releases available in immersive spatial audio formats (Dolby Atmos, 360 Reality Audio) on Apple Music and Amazon Music.

### Purpose

- Inform users about new spatial audio releases
- Provide reviews and technical details about spatial audio mixes
- Enable discovery of immersive music across platforms
- Track release dates and format availability

### Key Features

- **Automated Discovery**: Backend scans Apple Music every 48 hours via scheduler
- **Platform Filtering**: Apple Music, Amazon Music
- **Format Filtering**: Dolby Atmos, 360 Reality Audio
- **Manual Refresh**: Users can trigger on-demand updates
- **REST API**: Programmatic access to spatial audio catalog
- **Responsive Design**: Mobile-first, minimalist interface

---

## Quick Reference

### Technology Stack

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Scheduler**: APScheduler (48-hour intervals)
- **API Integration**: Apple Music API for track discovery
- **Deployment**: Render.com (recommended) or VPS

### Project Structure

```
spatial-selecta/
├── index.html              # Main HTML structure
├── styles.css              # All styling and responsive design
├── app.js                  # Frontend application logic
├── data.json               # Fallback data store
├── backend/                # Python FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database configuration
│   ├── scheduler.py       # Background jobs
│   └── apple_music_client.py
├── Documentation/          # All documentation
└── tests/                 # Test suite
```

### Essential Documentation

- [`AGENT_KNOWLEDGE_BASE.md`](../../AGENT_KNOWLEDGE_BASE.md) - **READ THIS FIRST** (patent compliance, security, design philosophy)
- [`README.md`](../../README.md) - User-facing project overview
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) - Development setup and guidelines
- [`Documentation/DOCUMENTATION_INDEX.md`](../DOCUMENTATION_INDEX.md) - Complete doc catalog

---

## Core Agent Standards

> **CRITICAL**: All AI agents MUST read [`AGENT_KNOWLEDGE_BASE.md`](../../AGENT_KNOWLEDGE_BASE.md) before any tasks. It contains non-negotiable Patent, Security, and Design rules.

### A. No Corner-Cutting

**Complete Solutions**: Never provide "partial" or "placeholder" code unless explicitly requested for a quick prototype.

**Error Handling**: All new code must include:

- Robust error handling
- Appropriate logging
- Edge-case validation
- User-friendly error messages

**Documentation**: Every function, class, and module must have:

- Clear docstrings explaining purpose
- Comments explaining the "why," not just the "how"
- Type hints (Python) for clarity

### B. Robust & Capable Solutions

**Modern Practices**: Utilize modern, capable libraries and features:

- Python: Type hints, AsyncIO, Pydantic v2
- JavaScript: ES6+ features (arrow functions, async/await, template literals)
- Follow established project patterns

**Scalability**: Design solutions considering:

- Future growth and feature additions
- Performance at scale
- Maintainability over time
- Database query efficiency

**Standardization**: Adhere strictly to project standards:

- 88-character line length (Python)
- `black` formatting (Python)
- `flake8` linting (Python)
- `snake_case` for Python functions/vars, `PascalCase` for classes
- Security-first approach (escaping, validation, HTTPS)

### C. Thorough Planning & Verification

**Implementation Plans**: Before significant changes:

1. Provide detailed implementation plan for user review
2. Identify risks and edge cases
3. Consider impacts on existing functionality
4. Get approval before proceeding

**Verification First**: Every change must be verified:

- Run automated tests (create them if missing)
- Manual testing for UI changes
- Check responsive design on mobile
- Verify no console errors

**Zero Regressions**: You are responsible for ensuring:

- New features don't break existing functionality
- All tests pass before committing
- No degradation in performance or UX

---

## Agent Workflow

Follow this 5-step process for all tasks:

### 1. Research

- Fully understand existing context and constraints
- Read relevant documentation
- Review related code files
- Identify dependencies and potential impacts

### 2. Plan

- Draft comprehensive plan identifying:
  - What will change and why
  - Risks and edge cases
  - Testing approach
  - Documentation updates needed
- Get user approval for significant changes

### 3. Implement

- Write clean, efficient, well-tested code
- Follow established patterns and conventions
- Include proper error handling
- Add/update documentation

### 4. Verify

- Run full test suite: `pytest tests/`
- Run linting: `flake8 .`
- Run formatting: `black . --check`
- Manual testing for UI/UX changes
- Verify responsive design

### 5. Refine

- Address any feedback or failures immediately
- If tests fail, fix them thoroughly
- Update documentation to reflect changes
- Ensure all verification steps pass

---

## Coding Standards & Formatting

### Python Standards

**Formatting**:

- Line length: **88 characters** (enforced by `black`)
- Formatter: `black`
- Import sorting: `isort` with black profile

**Linting**:

- Linter: `flake8`
- Configuration in `.flake8`:

  ```ini
  [flake8]
  max-line-length = 88
  extend-ignore = E203, W503
  exclude = .git,__pycache__,venv,.venv
  ```

**Style**:

- `snake_case` for functions and variables
- `PascalCase` for classes
- Type hints for function parameters and returns
- Docstrings for all public functions/classes

**Commands**:

```bash
black .                    # Format code
isort .                    # Sort imports
flake8 .                   # Check linting
pytest tests/              # Run tests
```

### JavaScript Standards

**Style**:

- ES6+ features (arrow functions, const/let, template literals)
- Descriptive variable and function names
- Keep functions small and focused
- Comment complex logic

**Security**:

- Always use `escapeHtml()` for user-generated content
- Validate HTTPS URLs with `isValidHttpsUrl()`
- Never trust user input

**Example**:

```javascript
function renderTracks() {
  const tracksHtml = tracks.map(track => {
    const titleSafe = escapeHtml(track.title);
    const artistSafe = escapeHtml(track.artist);
    return `<div class="music-card">
      <h3>${titleSafe}</h3>
      <p>${artistSafe}</p>
    </div>`;
  }).join('');
}
```

### HTML/CSS Standards

**HTML**:

- Use semantic HTML5 elements (`<header>`, `<main>`, `<section>`, `<footer>`)
- Descriptive IDs and classes (kebab-case)
- Include ARIA labels for accessibility

**CSS**:

- Use CSS variables in `:root` for theming
- Follow BEM-like naming (`.music-card`, `.track-title`)
- Mobile-first responsive design
- Minimalist aesthetic - avoid unnecessary styling

---

## Development Guidelines

### Design Philosophy

> "Good design is as little design as possible." — Dieter Rams

Maintain minimalist aesthetic:

- **Honest**: No decorative elements without function
- **Unobtrusive**: Content first, UI frames it
- **Thorough**: Precise execution of typography and spacing
- **Consistent**: Uniform patterns throughout

### Adding New Features

When adding features:

1. Check if it aligns with minimalist philosophy
2. Ensure it doesn't break responsive design
3. Consider performance impact
4. Update documentation
5. Add tests

### Data Format Compliance

All track data must follow standardized format in [`Documentation/Reference/DATA_FORMAT.md`](../Reference/DATA_FORMAT.md):

Required fields:

- `id` (unique integer)
- `title`, `artist`, `album` (strings)
- `format` ("Dolby Atmos" | "360 Reality Audio")
- `platform` ("Apple Music" | "Amazon Music")
- `releaseDate`, `atmosReleaseDate` (YYYY-MM-DD format)
- `musicLink` (valid Apple Music HTTPS URL)

### Security Requirements

**Never log**:

- Raw audio bytes
- PII (Personal Identifiable Information)
- API keys or secrets

**Always validate**:

- User input (escape HTML)
- URLs (HTTPS only)
- Date formats (YYYY-MM-DD)
- API responses

**Use security features**:

- Rate limiting for public endpoints
- Authentication for protected endpoints
- CORS configuration (no wildcards in production)
- Content Security Policy headers

---

## Common Tasks

### Adding a New Track

1. Get track information (title, artist, album, dates, platform, format)
2. Find next available ID in `data.json`
3. Create track object following data format standards
4. Validate JSON syntax (no trailing commas)
5. Test locally: `npm start`
6. Verify track displays correctly

### Modifying Filters

1. Update HTML: Add `<option>` to appropriate `<select>` element
2. Update JavaScript: Add filter property to `currentFilters` object
3. Update `applyFilters()` logic to include new filter
4. Test filter functionality thoroughly

### Updating Styling

**Color Scheme**:

- Modify CSS variables in `:root` selector
- Maintain contrast ratios for accessibility
- Stay within monochrome palette with minimal accents

**Layout Changes**:

- Grid: Modify `grid-template-columns` in `.music-grid`
- Cards: Update `.music-card` and child elements
- Responsive: Adjust `@media` queries as needed

### Testing Checklist

Before committing:

- [ ] Page loads and displays tracks
- [ ] All filters work correctly
- [ ] Refresh button reloads data
- [ ] "New" badge appears for recent releases
- [ ] Responsive design works on mobile/tablet
- [ ] Empty state shows when no results
- [ ] No console errors
- [ ] All tests pass: `pytest tests/`
- [ ] Linting passes: `flake8 .`
- [ ] Formatting correct: `black . --check`

---

## What Agents Should Do

✅ **Always validate JSON** after editing `data.json`

✅ **Test filters** after modifying filter logic

✅ **Check responsive design** after CSS changes

✅ **Verify XSS protection** when adding user input handling

✅ **Maintain minimalist aesthetic** - avoid over-styling

✅ **Use template literals** for HTML generation

✅ **Escape all user content** with `escapeHtml()`

✅ **Keep functions small** and focused on single responsibility

✅ **Use descriptive names** for variables and functions

✅ **Comment timezone/date logic** - it's complex

✅ **Follow established patterns** in existing code

✅ **Update documentation** when making changes

✅ **Run full test suite** before committing

---

## What Agents Should NOT Do

❌ **Don't remove `escapeHtml()` calls** - security risk

❌ **Don't break filter logic** - core functionality

❌ **Don't add unnecessary dependencies** - keep it simple

❌ **Don't over-complicate architecture** - vanilla is intentional

❌ **Don't break responsive design** - mobile-first is critical

❌ **Don't hardcode configuration** - use settings/environment vars

❌ **Don't skip testing** - verification is mandatory

❌ **Don't commit without formatting** - run `black` first

❌ **Don't ignore linting errors** - fix them properly

❌ **Don't make assumptions** - ask for clarification when unsure

---

## Questions to Ask Before Major Changes

Before making significant architectural or design changes, ask:

1. **Does this maintain the minimalist design philosophy?**
2. **Will this work on mobile devices?**
3. **Is the data structure scalable?**
4. **Does this require new dependencies?**
5. **How will this affect performance?**
6. **Is this change reversible if needed?**
7. **Does this follow established patterns?**
8. **Have I updated relevant documentation?**

---

## Troubleshooting Guide

### Tracks Not Displaying

**Symptoms**: Empty grid, no error messages

**Common Causes**:

- Invalid JSON in `data.json`
- CORS issues (check browser console)
- Filter criteria too restrictive
- API endpoint unavailable

**Solutions**:

1. Validate JSON syntax (use JSONLint)
2. Check browser console for errors
3. Verify API URL detection is correct
4. Test with filters set to "all"
5. Check network tab for failed requests

### Filters Not Working

**Symptoms**: Changing filter doesn't update display

**Common Causes**:

- Event listeners not attached
- Filter logic incorrect
- Data structure mismatch

**Solutions**:

1. Verify `setupFilters()` is called on page load
2. Check `applyFilters()` logic
3. Ensure track objects have correct `platform`/`format` values
4. Check browser console for JavaScript errors

### Backend API Issues

**Symptoms**: 500 errors, connection failures

**Common Causes**:

- Missing environment variables
- Database connection issues
- Apple Music API token expired

**Solutions**:

1. Check backend logs for detailed errors
2. Verify all required environment variables set
3. Test database connection
4. Regenerate Apple Music token if expired
5. Check CORS configuration for frontend domain

---

## Additional Resources

### Documentation

- [Setup Guide](../Guides/SETUP.md) - Local development setup
- [Deployment Guide](../Guides/DEPLOYMENT.md) - Production deployment
- [API Reference](../Reference/API.md) - REST API endpoints
- [Data Format](../Reference/DATA_FORMAT.md) - Track data standards
- [Security Guide](../Reference/SECURITY.md) - Security best practices
- [Development Guide](../Guides/DEVELOPMENT.md) - Development workflow

### Configuration Files

- `.flake8` - Python linting configuration
- `pyproject.toml` - Python tool configuration (black, isort)
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.env.example` - Environment variables template

---

**Note to Agents**: Following these guidelines is mandatory for maintaining code quality, security, and design integrity. When in doubt, ask for clarification rather than making assumptions.
