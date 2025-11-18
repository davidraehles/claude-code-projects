#!/bin/bash
#
# Quick Deployment Verification Script
# Tests both frontend and backend are working
#

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Deployment Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test Backend Health
echo -e "${YELLOW}1. Testing Backend Health...${NC}"
BACKEND_URL="https://claude-code-projects-production.up.railway.app"
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health")

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Test Frontend
echo -e "${YELLOW}2. Testing Frontend...${NC}"
FRONTEND_URL="https://claude-code-projects.vercel.app"
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")

if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
    echo "   HTTP Status: $FRONTEND_RESPONSE"
else
    echo -e "${RED}❌ Frontend returned HTTP $FRONTEND_RESPONSE${NC}"
    exit 1
fi
echo ""

# Test Backend API Endpoint
echo -e "${YELLOW}3. Testing Backend API...${NC}"
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/docs")

if [ "$API_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ API docs accessible${NC}"
    echo "   HTTP Status: $API_RESPONSE"
else
    echo -e "${RED}❌ API docs returned HTTP $API_RESPONSE${NC}"
    exit 1
fi
echo ""

# Test Login Page
echo -e "${YELLOW}4. Testing Login Page...${NC}"
LOGIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/login")

if [ "$LOGIN_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Login page accessible${NC}"
else
    echo -e "${RED}❌ Login page returned HTTP $LOGIN_RESPONSE${NC}"
    exit 1
fi
echo ""

# Test Dashboard (should redirect to login if not authenticated)
echo -e "${YELLOW}5. Testing Dashboard...${NC}"
DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/dashboard")

if [ "$DASHBOARD_RESPONSE" = "200" ] || [ "$DASHBOARD_RESPONSE" = "307" ]; then
    echo -e "${GREEN}✅ Dashboard accessible${NC}"
    echo "   HTTP Status: $DASHBOARD_RESPONSE"
else
    echo -e "${RED}❌ Dashboard returned HTTP $DASHBOARD_RESPONSE${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
echo "API Docs: $BACKEND_URL/api/docs"
echo ""
echo "Test credentials:"
echo "  Email: test@example.com"
echo "  Password: testpassword123"
echo ""
