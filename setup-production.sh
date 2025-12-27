#!/bin/bash
# Production Setup Script for SpatialSelects.com
# This script helps set up production environment variables

set -e

echo "=========================================="
echo "SpatialSelects.com Production Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  Warning: .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Exiting."
        exit 1
    fi
fi

# Generate secure refresh token
echo "Generating secure REFRESH_API_TOKEN..."
REFRESH_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Get domain from user
echo ""
read -p "Enter your production domain (e.g., yourdomain.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "Error: Domain is required"
    exit 1
fi

# Get Apple Music token
echo ""
read -p "Enter your Apple Music Developer Token (or press Enter to skip): " APPLE_TOKEN

# Get database URL
echo ""
echo "Database configuration:"
echo "1) PostgreSQL (recommended for production)"
echo "2) SQLite (development only)"
read -p "Choose option (1 or 2) [1]: " DB_CHOICE
DB_CHOICE=${DB_CHOICE:-1}

if [ "$DB_CHOICE" = "1" ]; then
    read -p "Enter PostgreSQL connection string (postgresql://user:pass@host/db): " DB_URL
    if [ -z "$DB_URL" ]; then
        DB_URL="postgresql://spatial_user:changeme@localhost/spatial_selecta"
        echo "Using default: $DB_URL"
    fi
else
    DB_URL="sqlite:///./spatial_selecta.db"
fi

# Create .env file
cat > .env << EOF
# Production Environment Configuration
# Generated on $(date)

# ============================================
# ENVIRONMENT CONFIGURATION
# ============================================
ENVIRONMENT=production

# ============================================
# CORS CONFIGURATION
# ============================================
ALLOWED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}

# ============================================
# API SECURITY
# ============================================
REFRESH_API_TOKEN=${REFRESH_TOKEN}

# ============================================
# APPLE MUSIC API CONFIGURATION
# ============================================
APPLE_MUSIC_DEVELOPER_TOKEN=${APPLE_TOKEN:-your_developer_token_here}
APPLE_MUSIC_USER_TOKEN=

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=${DB_URL}

# ============================================
# API CONFIGURATION
# ============================================
API_HOST=0.0.0.0
API_PORT=8000

# ============================================
# SCHEDULER CONFIGURATION
# ============================================
SCAN_INTERVAL_HOURS=48
EOF

echo ""
echo "✅ Production .env file created!"
echo ""
echo "📝 Next steps:"
echo "1. Review and edit .env file if needed"
echo "2. Set up your Apple Music Developer Token"
echo "3. Initialize database: python3 backend/setup.py"
echo "4. See DEPLOYMENT.md for hosting instructions"
echo ""
echo "🔐 Your REFRESH_API_TOKEN has been generated and saved"
echo "   Keep this secure and don't commit it to git!"

