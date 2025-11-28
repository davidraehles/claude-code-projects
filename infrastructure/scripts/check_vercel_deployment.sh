#!/bin/bash
#
# Vercel Deployment Monitor Script
# Checks latest deployment status and logs
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}  Vercel Deployment Monitor${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}Error: Vercel CLI not found${NC}"
    echo "Install with: npm install -g vercel"
    exit 1
fi

echo -e "${YELLOW}Checking latest deployment...${NC}"
echo ""

# Get latest deployment info
cd meal-planner-ui

echo -e "${BLUE}--- Deployment List (Recent) ---${NC}"
vercel ls 2>&1 | head -20 || echo "Unable to list deployments"
echo ""

echo -e "${BLUE}--- Latest Deployment Details ---${NC}"
LATEST_URL=$(vercel ls 2>&1 | grep -Eo 'https://[^ ]+\.vercel\.app' | head -1)

if [ -z "$LATEST_URL" ]; then
    echo -e "${RED}Could not find latest deployment URL${NC}"
    echo ""
    echo -e "${YELLOW}Trying to get production URL...${NC}"
    LATEST_URL="claude-code-projects.vercel.app"
fi

echo -e "${GREEN}Checking deployment: $LATEST_URL${NC}"
echo ""

# Get deployment details
echo -e "${BLUE}--- Deployment Info ---${NC}"
vercel inspect $LATEST_URL 2>&1 || echo "Could not fetch deployment info"
echo ""

# Get deployment logs
echo -e "${BLUE}--- Build Logs (Last 50 lines) ---${NC}"
vercel logs $LATEST_URL 2>&1 | tail -50 || echo "Could not fetch logs"

echo ""
echo -e "${BLUE}--- Checking for Errors ---${NC}"
ERROR_LOGS=$(vercel logs $LATEST_URL 2>&1 | grep -i "error\|fail\|exception" | head -20)
if [ -z "$ERROR_LOGS" ]; then
    echo -e "${GREEN}No errors found in logs${NC}"
else
    echo -e "${RED}Errors detected:${NC}"
    echo "$ERROR_LOGS"
fi

echo ""
echo -e "${BLUE}--- Environment Variables Check ---${NC}"
vercel env ls 2>&1 | head -20 || echo "Could not list environment variables"

echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo "Frontend URL: https://claude-code-projects.vercel.app"
echo "Backend URL: https://claude-code-projects-production.up.railway.app"
echo ""
echo "To view full logs:"
echo "  vercel logs https://claude-code-projects.vercel.app --limit 500"
echo ""
echo "To redeploy:"
echo "  cd meal-planner-ui && vercel --prod"
echo ""
