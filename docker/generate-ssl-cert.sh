#!/bin/bash
# Generate self-signed SSL certificates for local Docker testing
# For production, use Let's Encrypt or your certificate provider

set -e

CERT_DIR="./docker/ssl"
DOMAIN="${1:-localhost}"
DAYS=365

echo "Generating self-signed SSL certificate for $DOMAIN..."

# Create SSL directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Generate private key and certificate
openssl req -x509 -nodes -days $DAYS -newkey rsa:2048 \
    -keyout "$CERT_DIR/privkey.pem" \
    -out "$CERT_DIR/fullchain.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"

# Set proper permissions
chmod 600 "$CERT_DIR/privkey.pem"
chmod 644 "$CERT_DIR/fullchain.pem"

echo "SSL certificate generated successfully!"
echo "Certificate location: $CERT_DIR/fullchain.pem"
echo "Private key location: $CERT_DIR/privkey.pem"
echo ""
echo "Note: This is a self-signed certificate for testing only."
echo "For production, use Let's Encrypt or your certificate provider."
