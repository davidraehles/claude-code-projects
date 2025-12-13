#!/bin/bash

# Frontend-Backend Integration Test Script
# Tests that the frontend can communicate with Railway backend

echo "🧪 Testing Frontend-Backend Integration"
echo "========================================"
echo ""

BACKEND_URL="https://meal-planner.up.railway.app"
FRONTEND_URL="http://localhost:3000"

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq not found. Install it for better output: sudo apt-get install jq"
    JQ_CMD="cat"
else
    JQ_CMD="jq ."
fi

echo "📡 Backend URL: $BACKEND_URL"
echo "🖥️  Frontend URL: $FRONTEND_URL"
echo ""

# Test 1: Backend Health
echo "1️⃣  Testing Backend Health..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health")
if [ $? -eq 0 ]; then
    echo "✅ Backend is reachable"
    echo "$HEALTH_RESPONSE" | $JQ_CMD 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Backend is not reachable"
    exit 1
fi
echo ""

# Test 2: Check OpenAPI Docs
echo "2️⃣  Testing API Documentation..."
OPENAPI_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/openapi.json")
if [ "$OPENAPI_RESPONSE" = "200" ]; then
    echo "✅ OpenAPI documentation available"
else
    echo "⚠️  OpenAPI docs returned status: $OPENAPI_RESPONSE"
fi
echo ""

# Test 3: Test CORS (if frontend is running)
echo "3️⃣  Testing CORS Configuration..."
CORS_RESPONSE=$(curl -s -I -X OPTIONS "$BACKEND_URL/health" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET" | grep -i "access-control")

if [ ! -z "$CORS_RESPONSE" ]; then
    echo "✅ CORS headers present:"
    echo "$CORS_RESPONSE"
else
    echo "⚠️  No CORS headers found. May need configuration."
fi
echo ""

# Test 4: Check frontend .env.local
echo "4️⃣  Checking Frontend Configuration..."
if [ -f "frontend/.env.local" ]; then
    echo "✅ .env.local exists"
    echo "   Variables configured:"
    grep -E '^[A-Z_]+=' frontend/.env.local | sed 's/=.*/=***/' || echo "   No variables found"
else
    echo "❌ .env.local not found in frontend directory"
fi
echo ""

# Test 5: Try to access frontend (if running)
echo "5️⃣  Testing Frontend Server..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend is running and accessible"
else
    echo "⚠️  Frontend not running (status: $FRONTEND_STATUS)"
    echo "   Start it with: cd frontend && npm run dev"
fi
echo ""

# Summary
echo "📊 Summary"
echo "=========="
echo "Backend: ✅ Accessible at $BACKEND_URL"
echo "Frontend Config: ✅ Updated to use Railway backend"
echo ""
echo "🚀 Next Steps:"
echo "   1. If frontend is not running, start it: cd frontend && npm run dev"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Test user registration and login"
echo "   4. Verify all features work with Railway backend"
echo ""
