#!/bin/bash

# SSL Certificate Generation Script for Stock Analysis Platform
# This script generates self-signed SSL certificates for development and testing

set -e

# Configuration
SSL_DIR="./nginx/ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"
DAYS_VALID=365

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

# Create SSL directory if it doesn't exist
create_ssl_directory() {
    if [ ! -d "$SSL_DIR" ]; then
        mkdir -p "$SSL_DIR"
        log "Created SSL directory: $SSL_DIR"
    fi
}

# Generate self-signed certificate
generate_self_signed_cert() {
    log "Generating self-signed SSL certificate..."

    # Certificate details
    SUBJECT="/C=US/ST=State/L=City/O=Stock Analysis Platform/CN=localhost"

    # Generate private key
    openssl genrsa -out "$KEY_FILE" 2048

    # Generate certificate signing request
    openssl req -new -key "$KEY_FILE" -out "$SSL_DIR/cert.csr" -subj "$SUBJECT"

    # Generate self-signed certificate
    openssl x509 -req -days $DAYS_VALID -in "$SSL_DIR/cert.csr" -signkey "$KEY_FILE" -out "$CERT_FILE"

    # Clean up CSR file
    rm "$SSL_DIR/cert.csr"

    log "SSL certificate generated successfully"
    log "Certificate: $CERT_FILE"
    log "Private Key: $KEY_FILE"
    log "Valid for: $DAYS_VALID days"
}

# Verify certificate
verify_certificate() {
    log "Verifying SSL certificate..."

    if openssl x509 -in "$CERT_FILE" -text -noout > /dev/null 2>&1; then
        log "Certificate verification successful"

        # Show certificate details
        echo "Certificate Details:"
        openssl x509 -in "$CERT_FILE" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)"
    else
        error "Certificate verification failed"
        exit 1
    fi
}

# Generate DH parameters for better security
generate_dh_params() {
    log "Generating Diffie-Hellman parameters..."

    openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048

    log "DH parameters generated: $SSL_DIR/dhparam.pem"
}

# Create certificate info file
create_cert_info() {
    cat > "$SSL_DIR/README.md" << EOF
# SSL Certificate Information

This directory contains SSL certificates for the Stock Analysis Platform.

## Files

- \`cert.pem\` - SSL certificate
- \`key.pem\` - Private key
- \`dhparam.pem\` - Diffie-Hellman parameters

## Certificate Details

\`\`\`
$(openssl x509 -in "$CERT_FILE" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)" | sed 's/^/  /')
\`\`\`

## Security Notes

- This is a self-signed certificate for development/testing
- For production, use certificates from a trusted CA (Let's Encrypt, etc.)
- Keep the private key (\`key.pem\`) secure and never commit to version control
- The certificate is valid for $DAYS_VALID days from $(date)

## Renewal

To renew the certificate, run:
\`\`\`bash
./scripts/generate-ssl.sh
\`\`\`
EOF

    log "Certificate information saved to: $SSL_DIR/README.md"
}

# Main function
main() {
    log "Stock Analysis Platform SSL Certificate Generation"
    log "=================================================="

    create_ssl_directory
    generate_self_signed_cert
    generate_dh_params
    verify_certificate
    create_cert_info

    log ""
    log "SSL setup completed successfully!"
    log ""
    warn "This is a self-signed certificate. Browsers will show security warnings."
    warn "For production, use certificates from Let's Encrypt or a trusted CA."
    log ""
    log "Next steps:"
    log "1. Update your /etc/hosts file to include: 127.0.0.1 stockanalysis.local"
    log "2. Access the application at: https://stockanalysis.local"
    log "3. Accept the self-signed certificate in your browser"
}

# Run main function
main "$@"
