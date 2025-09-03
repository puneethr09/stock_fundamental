# SSL Certificate Information

This directory contains SSL certificates for the Stock Analysis Platform.

## Files

- `cert.pem` - SSL certificate
- `key.pem` - Private key
- `dhparam.pem` - Diffie-Hellman parameters

## Certificate Details

```
          Issuer: C=US, ST=State, L=City, O=Stock Analysis Platform, CN=localhost
              Not Before: Sep  1 11:05:04 2025 GMT
          Subject: C=US, ST=State, L=City, O=Stock Analysis Platform, CN=localhost
```

## Security Notes

- This is a self-signed certificate for development/testing
- For production, use certificates from a trusted CA (Let's Encrypt, etc.)
- Keep the private key (`key.pem`) secure and never commit to version control
- The certificate is valid for 365 days from Mon Sep  1 16:35:17 IST 2025

## Renewal

To renew the certificate, run:
```bash
./scripts/generate-ssl.sh
```
