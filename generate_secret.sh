#!/bin/bash

# Simple script to generate a secure secret key

echo "Generating secure secret key..."
echo ""

if command -v python3 &> /dev/null; then
    secret=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "Generated secret key:"
    echo ""
    echo "$secret"
    echo ""
    echo "Add this to your .env file:"
    echo "SECRET_KEY=$secret"
elif command -v openssl &> /dev/null; then
    secret=$(openssl rand -base64 32)
    echo "Generated secret key:"
    echo ""
    echo "$secret"
    echo ""
    echo "Add this to your .env file:"
    echo "SECRET_KEY=$secret"
else
    echo "Error: python3 or openssl required to generate secret"
    exit 1
fi
