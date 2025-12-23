# Copilot Instructions for Spatial Selecta

## Project Overview

Spatial Selecta is a website designed for people interested in immersive music and spatial audio mixes. The site provides information about spatial audio releases, artists, and mixing formats.

## Project Purpose

- Showcase immersive music and spatial audio content
- Provide release information for spatial audio mixes
- Help users discover new immersive audio experiences
- Educate about spatial audio formats (Dolby Atmos, Sony 360 Reality Audio, Auro-3D, etc.)

## Development Guidelines

### Code Style

- Follow industry-standard best practices for the web stack being used
- Write clean, readable, and maintainable code
- Use meaningful variable and function names
- Comment complex logic and business rules
- Keep functions focused and single-purpose

### Project Structure

- Organize code by feature or domain rather than file type
- Keep related files together
- Maintain clear separation between UI, business logic, and data layers
- Use consistent naming conventions across the project

### Testing

- Write tests for new features and bug fixes
- Ensure tests are clear and maintainable
- Test edge cases and error conditions
- Keep test coverage high for critical paths

### Documentation

- Document all public APIs and interfaces
- Include README files for major features
- Keep documentation up-to-date with code changes
- Add comments for complex business logic specific to spatial audio/music industry

### Accessibility

- Follow WCAG 2.1 guidelines
- Ensure keyboard navigation works properly
- Provide appropriate ARIA labels
- Test with screen readers when implementing new UI features

### Performance

- Optimize for fast load times
- Implement lazy loading for media content
- Minimize bundle sizes
- Consider mobile and lower-bandwidth users

### Audio/Music Specific Guidelines

- Handle multiple audio format metadata correctly
- Display spatial audio format information clearly (e.g., Dolby Atmos, 360RA)
- Respect audio copyright and licensing information
- Consider audio player UI/UX best practices
- Handle audio streaming and playback efficiently

### Git Workflow

- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Reference issue numbers in commit messages when applicable
- Create feature branches for new work

## Technology Preferences

- Use modern web standards and frameworks
- Prefer widely-adopted, well-maintained libraries
- Consider bundle size when adding dependencies
- Prioritize performance and user experience

## Security

- Never commit sensitive information (API keys, credentials)
- Sanitize user inputs
- Follow security best practices for the chosen stack
- Keep dependencies up-to-date

## When Making Changes

- Understand the existing code before modifying
- Make minimal, focused changes
- Run tests before committing
- Update documentation when changing behavior
- Consider backward compatibility
