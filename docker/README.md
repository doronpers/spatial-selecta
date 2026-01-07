# Docker Configuration Files

This directory contains Docker-related configuration files for Spatial Selecta.

## Files

### `nginx.conf`
Main nginx configuration for the reverse proxy. Includes:
- SSL/TLS configuration
- Rate limiting
- Security headers
- Backend API proxying
- Frontend static file serving
- Client max body size: 10MB (configurable)

### `nginx-frontend.conf`
Nginx configuration for the frontend container. Simple static file serving with:
- Gzip compression
- Cache headers
- Security headers

### `generate-ssl-cert.sh`
Script to generate self-signed SSL certificates for local testing.

Usage:
```bash
./generate-ssl-cert.sh [domain]
```

Example:
```bash
# Generate for localhost
./generate-ssl-cert.sh localhost

# Generate for custom domain
./generate-ssl-cert.sh yourdomain.com
```

### `ssl/` (created by generate-ssl-cert.sh)
Directory containing SSL certificates:
- `fullchain.pem`: SSL certificate
- `privkey.pem`: Private key

**Note**: This directory is in .gitignore. Never commit SSL certificates!

## Quick Start

1. Generate SSL certificates:
```bash
./docker/generate-ssl-cert.sh localhost
```

2. Configure environment:
```bash
cp .env.docker .env
# Edit .env with your settings
```

3. Start services:
```bash
docker-compose up -d
```

## Configuration

### Increasing Upload Size Limit

Edit `nginx.conf` and change:
```nginx
client_max_body_size 50M;  # Default is 10M
```

### Adjusting Rate Limits

Edit `nginx.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=20r/s;  # API limit
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=200r/s;  # General limit
```

### Enabling Backend Docs

Uncomment this section in `nginx.conf`:
```nginx
# location /docs {
#     proxy_pass http://backend;
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
# }
```

## Production SSL

For production, use Let's Encrypt:

1. Uncomment certbot service in docker-compose.yml
2. Run initial certificate generation:
```bash
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    -d yourdomain.com \
    --email your@email.com \
    --agree-tos
```

3. Update nginx SSL volume mounts to use certbot certificates

See [docs/DOCKER.md](../docs/DOCKER.md) for detailed instructions.
