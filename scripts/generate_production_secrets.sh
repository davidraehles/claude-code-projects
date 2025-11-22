#!/bin/bash

##############################################################################
# Production Secrets Generation Script
# Generates all required security keys for production deployment
##############################################################################

set -e

echo "🔐 Production Secrets Generation"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

##############################################################################
# Generate Backend Secrets
##############################################################################

echo -e "${YELLOW}Backend Secrets:${NC}"
echo ""

# SECRET_KEY for FastAPI
echo "Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "  ${GREEN}SECRET_KEY=${SECRET_KEY}${NC}"
echo ""

# JWT_SECRET_KEY
echo "Generating JWT_SECRET_KEY..."
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "  ${GREEN}JWT_SECRET_KEY=${JWT_SECRET_KEY}${NC}"
echo ""

# KNUSPR_ENCRYPTION_KEY (Fernet)
echo "Generating KNUSPR_ENCRYPTION_KEY (Fernet)..."
KNUSPR_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo -e "  ${GREEN}KNUSPR_ENCRYPTION_KEY=${KNUSPR_ENCRYPTION_KEY}${NC}"
echo ""

##############################################################################
# Generate Frontend Secrets
##############################################################################

echo -e "${YELLOW}Frontend Secrets:${NC}"
echo ""

# NEXTAUTH_SECRET
echo "Generating NEXTAUTH_SECRET..."
NEXTAUTH_SECRET=$(openssl rand -base64 32)
echo -e "  ${GREEN}NEXTAUTH_SECRET=${NEXTAUTH_SECRET}${NC}"
echo ""

##############################################################################
# Output Summary
##############################################################################

echo -e "${YELLOW}Summary:${NC}"
echo ""
echo "Copy these values to Railway environment variables:"
echo ""
echo "Backend (.env):"
cat << EOF
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
KNUSPR_ENCRYPTION_KEY=${KNUSPR_ENCRYPTION_KEY}
EOF

echo ""
echo "Frontend (.env.production):"
cat << EOF
NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
EOF

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "1. Save these values in a secure location"
echo "2. Add them to Railway and Vercel environment variables"
echo "3. Never commit these values to Git"
echo "4. Rotate these keys every 90 days"
echo "5. Use different keys for dev/staging/production"
echo ""

# Optional: Save to .env.production.local for local testing
echo "Save to file? (y/n)"
read -r SAVE_TO_FILE

if [ "$SAVE_TO_FILE" = "y" ]; then
  OUTPUT_FILE=".env.production.secrets"
  cat > "$OUTPUT_FILE" << EOF
# Generated: $(date)
# WARNING: DO NOT COMMIT TO GIT

# Backend
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
KNUSPR_ENCRYPTION_KEY=${KNUSPR_ENCRYPTION_KEY}

# Frontend
NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
EOF

  echo -e "${GREEN}✅ Secrets saved to ${OUTPUT_FILE}${NC}"
  echo -e "${YELLOW}⚠️  Add to .gitignore to prevent accidental commits${NC}"
fi
