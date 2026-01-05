# Contributing to SpatialSelects.com

Thank you for your interest in contributing to SpatialSelects.com! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Adding New Tracks](#adding-new-tracks)

## Code of Conduct

This project welcomes contributions from everyone. We expect all contributors to be respectful and constructive in their interactions.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your environment (browser, OS, etc.)

### Suggesting Enhancements

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Why this feature would be useful
- Any implementation ideas you have

### Adding Spatial Audio Tracks

One of the most valuable contributions is adding new spatial audio releases! See the [Adding New Tracks](#adding-new-tracks) section below.

### Code Contributions

We welcome code contributions for:
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage

## Development Setup

### Prerequisites

- **Node.js** (v16 or higher) - v14 has reached end-of-life
- **Python** 3.9+ (for backend)
- **Git** for version control

### Local Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/spatial-selecta.git
   cd spatial-selecta
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/doronpers/spatial-selecta.git
   ```

4. **Install frontend dependencies:**
   ```bash
   npm install
   ```

5. **Install backend dependencies (optional):**
   ```bash
   pip install -r requirements.txt
   ```

6. **Start development server:**
   ```bash
   npm start
   ```

7. **Start backend (optional):**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

For more detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).

## Making Changes

### Branching Strategy

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, focused commits

3. **Keep your branch up to date:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Commit Messages

Write clear, descriptive commit messages:

```
Add search functionality to track list

- Implement client-side search filtering
- Add search input to UI
- Update documentation
```

**Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issue numbers when applicable (#123)

## Submitting Changes

### Pull Request Process

1. **Ensure your changes work:**
   - Test locally in multiple browsers
   - Check responsive design on mobile
   - Verify no console errors

2. **Update documentation** if needed

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Screenshots (for UI changes)
   - Any related issue numbers

5. **Respond to feedback** from maintainers

### PR Checklist

Before submitting, ensure:
- [ ] Code follows the project's style guidelines
- [ ] Changes work locally without errors
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files are included
- [ ] PR description clearly explains the changes

## Style Guidelines

### JavaScript

- Use ES6+ features (arrow functions, const/let, template literals)
- Use descriptive variable and function names
- Keep functions small and focused
- Comment complex logic
- Use `escapeHtml()` for user-generated content

**Example:**
```javascript
function renderTracks() {
  const tracksHtml = tracks.map(track => {
    const titleSafe = escapeHtml(track.title);
    return `<div>${titleSafe}</div>`;
  }).join('');
}
```

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions
- Keep functions focused

**Example:**
```python
def get_tracks(db: Session, platform: str = None) -> List[Track]:
    """
    Retrieve tracks from database with optional filtering.
    
    Args:
        db: Database session
        platform: Optional platform filter
        
    Returns:
        List of Track objects
    """
    query = db.query(Track)
    if platform:
        query = query.filter(Track.platform == platform)
    return query.all()
```

### HTML/CSS

- Use semantic HTML elements
- Keep CSS organized and commented
- Maintain responsive design principles
- Follow existing naming conventions

## Adding New Tracks

### Track Data Format

All tracks must follow the standardized format in [docs/DATA_FORMAT.md](docs/DATA_FORMAT.md).

### Quick Guide

1. **Gather information:**
   - Song title, artist, album
   - Original release date
   - Dolby Atmos release date
   - Apple Music link (must include track ID)

2. **Find the next ID:**
   ```bash
   # Check highest ID in data.json
   cat data.json | grep '"id":' | tail -1
   ```

3. **Add track to `data.json`:**
   ```json
   {
     "id": 999,
     "title": "Song Title",
     "artist": "Artist Name",
     "album": "Album Name",
     "format": "Dolby Atmos",
     "platform": "Apple Music",
     "releaseDate": "2023-01-15",
     "atmosReleaseDate": "2023-01-15",
     "albumArt": "🎵",
     "musicLink": "https://music.apple.com/us/album/name/123456?i=789012"
   }
   ```

4. **Validate JSON:**
   ```bash
   # Check JSON is valid
   cat data.json | python -m json.tool > /dev/null && echo "Valid JSON"
   ```

5. **Test locally:**
   - Start dev server: `npm start`
   - Visit http://localhost:8080
   - Verify track appears correctly
   - Test the music link works

6. **Submit PR** with clear description

### Common Mistakes

- ❌ Missing track ID in Apple Music link (`?i=123456`)
- ❌ Wrong date format (use `YYYY-MM-DD`)
- ❌ Invalid JSON syntax (trailing commas)
- ❌ Duplicate IDs

See [docs/DATA_FORMAT.md](docs/DATA_FORMAT.md) for complete validation rules.

## Questions?

If you have questions:
- Check existing [documentation](docs/)
- Open a GitHub issue
- Review [closed issues](https://github.com/doronpers/spatial-selecta/issues?q=is%3Aissue+is%3Aclosed) for similar questions

## Recognition

Contributors will be recognized in the project. Thank you for helping make spatial audio more accessible!

## License

By contributing to SpatialSelects.com, you agree that your contributions will be licensed under the MIT License.
