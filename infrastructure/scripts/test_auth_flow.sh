#!/bin/bash
# Test authentication flow end-to-end
# Tests registration, login, and authenticated requests

set -e

API_URL="${API_URL:-https://claude-code-projects-production.up.railway.app}"
TEST_EMAIL="testuser_$(date +%s)@example.com"
TEST_PASSWORD="testpassword123"
TEST_COUNTRY="US"

echo "=========================================="
echo "Authentication Flow Test"
echo "=========================================="
echo ""
echo "API URL: $API_URL"
echo "Test Email: $TEST_EMAIL"
echo ""

# Test 1: Register new user
echo "1️⃣  Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"country\":\"$TEST_COUNTRY\"}" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$REGISTER_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" == "201" ]; then
    echo "   ✅ Registration successful (HTTP 201)"
    ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   Token: ${ACCESS_TOKEN:0:20}..."
else
    echo "   ❌ Registration failed (HTTP $HTTP_STATUS)"
    echo "   Response: $RESPONSE_BODY"
    exit 1
fi

echo ""

# Test 2: Login with credentials
echo "2️⃣  Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" == "200" ]; then
    echo "   ✅ Login successful (HTTP 200)"
    ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)
    echo "   Access Token: ${ACCESS_TOKEN:0:20}..."
    echo "   Refresh Token: ${REFRESH_TOKEN:0:20}..."
else
    echo "   ❌ Login failed (HTTP $HTTP_STATUS)"
    echo "   Response: $RESPONSE_BODY"
    exit 1
fi

echo ""

# Test 3: Get current user profile
echo "3️⃣  Testing authenticated request (get user profile)..."
USER_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$USER_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$USER_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" == "200" ]; then
    echo "   ✅ Authenticated request successful (HTTP 200)"
    echo "   User: $RESPONSE_BODY"
else
    echo "   ❌ Authenticated request failed (HTTP $HTTP_STATUS)"
    echo "   Response: $RESPONSE_BODY"
    exit 1
fi

echo ""

# Test 4: Refresh token
echo "4️⃣  Testing token refresh..."
REFRESH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$REFRESH_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$REFRESH_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" == "200" ]; then
    echo "   ✅ Token refresh successful (HTTP 200)"
    NEW_ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   New Access Token: ${NEW_ACCESS_TOKEN:0:20}..."
else
    echo "   ❌ Token refresh failed (HTTP $HTTP_STATUS)"
    echo "   Response: $RESPONSE_BODY"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All authentication tests passed!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ User registration working"
echo "  ✓ User login working"
echo "  ✓ Authenticated requests working"
echo "  ✓ Token refresh working"
echo ""
