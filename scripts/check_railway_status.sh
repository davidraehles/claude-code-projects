#!/bin/bash
# Check Railway service status and deployment info

echo "=========================================="
echo "Railway Service Status Check"
echo "=========================================="
echo ""

echo "1. Backend Health Check"
echo "   URL: https://claude-code-projects-production.up.railway.app/health"
HEALTH=$(curl -s https://claude-code-projects-production.up.railway.app/health)
echo "   Response: $HEALTH"
echo ""

echo "2. Backend Root Endpoint"
echo "   URL: https://claude-code-projects-production.up.railway.app/"
ROOT=$(curl -s https://claude-code-projects-production.up.railway.app/)
echo "   Response: $ROOT"
echo ""

echo "3. Test Current Code Version (Password Hashing)"
echo "   Testing register endpoint..."
REGISTER=$(curl -s -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"statuscheck@test.com","password":"testpassword123","country":"US"}')

if echo "$REGISTER" | grep -q "password cannot be longer than 72 bytes"; then
    echo "   ❌ OLD CODE DEPLOYED (bcrypt bug present)"
    echo "   Error: $(echo "$REGISTER" | grep -o '"message":"[^"]*' | cut -d'"' -f4)"
elif echo "$REGISTER" | grep -q "already registered"; then
    echo "   ✅ NEW CODE DEPLOYED (user already exists - this is good!)"
elif echo "$REGISTER" | grep -q "access_token"; then
    echo "   ✅ NEW CODE DEPLOYED (registration successful!)"
else
    echo "   Response: $REGISTER"
fi

echo ""
echo "4. Check when Railway last deployed"
echo "   (You need to check Railway dashboard for this)"
echo "   Visit: https://railway.app/dashboard"
echo ""
echo "=========================================="
