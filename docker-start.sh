#!/bin/bash
# Quick start script for Docker deployment of Spatial Selecta
# This script helps setup and start the application with Docker

set -e

echo "==================================================="
echo "   Spatial Selecta - Docker Quick Start"
echo "==================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not available."
    echo "Please install Docker Compose v2 or upgrade Docker."
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is available"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.docker" ]; then
        cp .env.docker .env
        echo "✓ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file with your configuration:"
        echo "   - POSTGRES_PASSWORD (required)"
        echo "   - APPLE_MUSIC_DEVELOPER_TOKEN (required)"
        echo "   - REFRESH_API_TOKEN (required)"
        echo "   - RATING_IP_SALT (required)"
        echo "   - ALLOWED_ORIGINS (required for production)"
        echo ""
        echo "Generate secure tokens with:"
        echo "   python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        echo ""
        read -p "Press Enter after you've configured .env, or Ctrl+C to exit..."
    else
        echo "Error: .env.docker template not found"
        exit 1
    fi
else
    echo "✓ .env file exists"
fi

# Check if SSL certificates exist
if [ ! -f "docker/ssl/fullchain.pem" ] || [ ! -f "docker/ssl/privkey.pem" ]; then
    echo ""
    echo "SSL certificates not found. Generating self-signed certificate..."
    if [ -f "docker/generate-ssl-cert.sh" ]; then
        ./docker/generate-ssl-cert.sh localhost
        echo "✓ SSL certificates generated"
    else
        echo "Error: SSL generation script not found"
        exit 1
    fi
else
    echo "✓ SSL certificates exist"
fi

echo ""
echo "Building Docker images..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check service status
echo ""
echo "Service Status:"
docker compose ps

echo ""
echo "==================================================="
echo "   Spatial Selecta is starting!"
echo "==================================================="
echo ""
echo "Access the application at:"
echo "  • HTTPS (recommended): https://localhost"
echo "  • HTTP (redirects to HTTPS): http://localhost"
echo ""
echo "Note: Self-signed certificates will show a browser warning."
echo "      Click 'Advanced' → 'Proceed' to continue."
echo ""
echo "Useful commands:"
echo "  • View logs: docker compose logs -f"
echo "  • Stop services: docker compose down"
echo "  • Restart services: docker compose restart"
echo "  • View status: docker compose ps"
echo ""
echo "For production deployment with Let's Encrypt, see:"
echo "  docs/DOCKER.md"
echo ""
