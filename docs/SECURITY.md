# Security Guide

Security measures, best practices, and hardening for SpatialSelects.com.

## Security Features

### 1. CORS Configuration

- **Development**: Allows localhost origins
- **Production**: Requires explicit `ALLOWED_ORIGINS` (no wildcards)
- **Configuration**: Set `ENVIRONMENT=production` and `ALLOWED_ORIGINS=https://yourdomain.com`

### 2. Input Validation

All API endpoints validate inputs:
- **Limit**: 1-1000 (prevents excessive requests)
- **Offset**: 0-10000 (prevents deep pagination)
- **Days**: 1-365 (prevents excessive date ranges)
- **Platform/Format**: Whitelist validation

### 3. Rate Limiting

- **Limit**: 100 requests per minute per IP
- **Window**: 60 seconds
- **Storage**: In-memory with automatic cleanup
- **Memory Protection**: Bounded storage (max 10,000 IPs)

### 4. Authentication

- **Protected Endpoint**: `/api/refresh` requires Bearer token
- **Token**: Set via `REFRESH_API_TOKEN` environment variable
- **Security**: Constant-time comparison using `hmac.compare_digest()`

### 5. XSS Protection

- **Frontend**: All content escaped using `escapeHtml()`
- **URL Validation**: Only HTTPS URLs allowed
- **Content Security Policy**: Configured in `index.html`
- **Security Headers**: X-XSS-Protection header set

### 6. SQL Injection Prevention

- **ORM**: Uses SQLAlchemy ORM (parameterized queries)
- **No Raw SQL**: All queries use ORM methods
- **Input Validation**: All inputs validated before queries

### 7. Security Headers

All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (production only)
- `Content-Security-Policy` (production only)
- Server header removed

### 8. Request Size Limits

- **Maximum Size**: 1MB per request
- **Protection**: Prevents DoS via large payloads
- **Response**: 413 status code for oversized requests

### 9. Error Handling

- **Client Messages**: Generic error messages (no stack traces)
- **Server Logging**: Full error details logged server-side only
- **Information Disclosure**: Prevented through proper exception handling

## Production Security Checklist

### Before Deployment

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `ALLOWED_ORIGINS` with specific domains (no wildcards)
- [ ] Generate and set `REFRESH_API_TOKEN` (secure random string)
- [ ] Use strong database credentials
- [ ] Ensure `.env` file is not committed to git
- [ ] Enable HTTPS/TLS for all connections
- [ ] Set up proper firewall rules
- [ ] Review and update all dependencies
- [ ] Configure rate limiting (consider Redis for distributed systems)

### Required Environment Variables

```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
REFRESH_API_TOKEN=<generate-secure-token>
APPLE_MUSIC_DEVELOPER_TOKEN=<your-token>
DATABASE_URL=<your-database-url>
```

### API Security

**Public Endpoints (Rate Limited):**
- `GET /api/tracks`
- `GET /api/tracks/new`
- `GET /api/tracks/{id}`
- `GET /api/stats`
- `GET /api/health`

**Protected Endpoints (Authentication Required):**
- `POST /api/refresh` - Requires `Authorization: Bearer <token>`

## Known Security Considerations

### 1. Rate Limiting Storage

Current implementation uses in-memory storage. For distributed deployments:
- Consider Redis-based rate limiting
- Implement shared rate limit store across instances

### 2. Token Management

`REFRESH_API_TOKEN` is a simple bearer token. For production, consider:
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

## Security Updates

- Regularly update dependencies: `pip install -r requirements.txt --upgrade`
- Monitor security advisories for FastAPI, SQLAlchemy, and other dependencies
- Review GitHub Dependabot alerts
- Keep Python and system packages updated

## Reporting Security Issues

If you discover a security vulnerability:
1. **Do NOT** create a public GitHub issue
2. Email security concerns privately
3. Include steps to reproduce
4. Allow time for fix before public disclosure

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)

