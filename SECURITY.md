# Security Documentation

This document outlines security measures implemented in SpatialSelects.com and best practices for deployment.

**Last Updated**: 2025-01-27  
**Status**: ✅ Hardened - See [SECURITY_REVIEW.md](SECURITY_REVIEW.md) for comprehensive security audit

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
- **Limit**: 100 requests per minute per IP address (configurable)
- **Window**: 60 seconds (configurable via `RATE_LIMIT_WINDOW`)
- **Storage**: In-memory with automatic cleanup (for single-instance deployments)
- **Memory Protection**: Bounded storage with aggressive cleanup (max 10,000 IPs)
- **IP Extraction**: Secure IP extraction with proxy support (`TRUST_PROXY` env var)
- **Note**: For distributed deployments, consider Redis-based rate limiting

### 4. Authentication
- **Protected Endpoint**: `/api/refresh` requires Bearer token authentication
- **Token**: Set via `REFRESH_API_TOKEN` environment variable
- **Usage**: `Authorization: Bearer <token>` header required
- **Generation**: Use `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Security**: Constant-time token comparison (prevents timing attacks)
- **Implementation**: Uses `hmac.compare_digest()` for secure comparison

### 5. XSS Protection
- **Frontend**: All user-generated content is escaped using `escapeHtml()`
- **URL Validation**: Only `http://` and `https://` URLs allowed
- **Content Security Policy**: Configured in `index.html` with `upgrade-insecure-requests`
- **Security Headers**: X-XSS-Protection header set on all responses
- **Input Sanitization**: Null bytes and control characters removed from inputs

### 6. SQL Injection Prevention
- **ORM**: Uses SQLAlchemy ORM (parameterized queries)
- **No Raw SQL**: All database queries use ORM methods
- **Input Validation**: All inputs validated before database queries

### 7. Environment Variables
- **Secrets**: Never hardcoded in source code
- **Example File**: `.env.example` provided (no real secrets)
- **Gitignore**: `.env` files excluded from version control
- **Required Variables**: Documented in `.env.example`

### 8. Security Headers
- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking
- **X-XSS-Protection**: `1; mode=block` - Legacy XSS protection
- **Referrer-Policy**: `strict-origin-when-cross-origin`
- **Strict-Transport-Security**: HSTS header (production only)
- **Content-Security-Policy**: Restricts resource loading (production only)
- **Server Header**: Removed to prevent information disclosure

### 9. Request Size Limits
- **Maximum Size**: 1MB per request
- **Protection**: Prevents DoS via large payloads
- **Response**: 413 status code for oversized requests

### 10. Error Handling
- **Client Messages**: Generic error messages (no stack traces)
- **Server Logging**: Full error details logged server-side only
- **Information Disclosure**: Prevented through proper exception handling

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

