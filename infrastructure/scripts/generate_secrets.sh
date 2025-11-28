#!/bin/bash
# Generate secrets for Railway environment variables

echo "=========================================="
echo "Railway Environment Variable Secrets"
echo "=========================================="
echo ""
echo "Copy these values to Railway → FastAPI service → Variables tab:"
echo ""

JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "JWT_SECRET_KEY=$JWT_SECRET"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo ""
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to Railway dashboard"
echo "2. Click your FastAPI service"
echo "3. Go to 'Variables' tab"
echo "4. Add these two variables with the values above"
echo ""
