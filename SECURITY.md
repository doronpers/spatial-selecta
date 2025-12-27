# Security Documentation

This document outlines security measures implemented in SpatialSelects.com and best practices for deployment.

## Security Features Implemented

### 1. CORS Configuration
- **Development**: Allows localhost origins for local development
- **Production**: Requires explicit `ALLOWED_ORIGINS` environment variable
- **Security**: Wildcard (`*`) is blocked in production mode
- **Configuration**: Set `ENVIRONMENT=production` and `ALLOWED_ORIGINS=https://yourdomain.com`

### 2. Input Validation
All API endpoints validate and sanitize inputs:
- **Limit**: 1-1000 (prevents excessive data requests)
- **Offset**: 0-10000 (prevents deep pagination abuse)
- **Days**: 1-365 (prevents excessive date range queries)
- **Track ID**: Positive integers only
- **Platform/Format**: Whitelist validation (prevents injection)

### 3. Rate Limiting
- **Limit**: 100 requests per minute per IP address
- **Window**: 60 seconds
- **Storage**: In-memory (for single-instance deployments)
- **Note**: For distributed deployments, consider Redis-based rate limiting

### 4. Authentication
- **Protected Endpoint**: `/api/refresh` requires Bearer token authentication
- **Token**: Set via `REFRESH_API_TOKEN` environment variable
- **Usage**: `Authorization: Bearer <token>` header required
- **Generation**: Use `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 5. XSS Protection
- **Frontend**: All user-generated content is escaped using `escapeHtml()`
- **URL Validation**: Only `http://` and `https://` URLs allowed
- **Content Security Policy**: Configured in `index.html`

### 6. SQL Injection Prevention
- **ORM**: Uses SQLAlchemy ORM (parameterized queries)
- **No Raw SQL**: All database queries use ORM methods
- **Input Validation**: All inputs validated before database queries

### 7. Environment Variables
- **Secrets**: Never hardcoded in source code
- **Example File**: `.env.example` provided (no real secrets)
- **Gitignore**: `.env` files excluded from version control
- **Required Variables**: Documented in `.env.example`

## Security Checklist for Production Deployment

### Before Deployment

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure `ALLOWED_ORIGINS` with specific domains (no wildcards)
- [ ] Generate and set `REFRESH_API_TOKEN` (secure random string)
- [ ] Use strong database credentials in `DATABASE_URL`
- [ ] Ensure `.env` file is not committed to git
- [ ] Review and restrict CORS origins
- [ ] Enable HTTPS/TLS for all connections
- [ ] Set up proper firewall rules
- [ ] Configure rate limiting (consider Redis for distributed systems)
- [ ] Review and update all dependencies (`pip install -r requirements.txt --upgrade`)

### Environment Variables

Required for production:
```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
REFRESH_API_TOKEN=<generate-secure-token>
APPLE_MUSIC_DEVELOPER_TOKEN=<your-token>
DATABASE_URL=<your-database-url>
```

### API Security

#### Public Endpoints (No Authentication)
- `GET /api/tracks` - Rate limited
- `GET /api/tracks/new` - Rate limited
- `GET /api/tracks/{id}` - Rate limited
- `GET /api/stats` - Rate limited
- `GET /api/health` - Rate limited

#### Protected Endpoints (Authentication Required)
- `POST /api/refresh` - Requires `Authorization: Bearer <token>` header

#### Example: Calling Protected Endpoint
```bash
curl -X POST https://api.yourdomain.com/api/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_API_TOKEN"
```

## Known Security Considerations

### 1. Rate Limiting Storage
Current implementation uses in-memory storage. For distributed deployments:
- Consider Redis-based rate limiting
- Implement shared rate limit store across instances

### 2. Token Management
- `REFRESH_API_TOKEN` is a simple bearer token
- For production, consider implementing:
  - JWT tokens with expiration
  - Token rotation
  - Revocation mechanism

### 3. Database Security
- Use connection pooling
- Enable SSL/TLS for database connections
- Use read-only database users where possible
- Regular backups and access logging

### 4. Logging
- Avoid logging sensitive information (tokens, passwords)
- Implement log rotation
- Monitor for suspicious activity

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do NOT** create a public GitHub issue
2. Email security concerns privately
3. Include steps to reproduce
4. Allow time for fix before public disclosure

## Security Updates

- Regularly update dependencies: `pip install -r requirements.txt --upgrade`
- Monitor security advisories for FastAPI, SQLAlchemy, and other dependencies
- Review GitHub Dependabot alerts
- Keep Python and system packages updated

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)

