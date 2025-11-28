#!/bin/bash
#
# Diagnose and Fix Vercel Deployment Failures
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Deployment Failure Diagnosis${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check what commit is deployed
echo -e "${YELLOW}1. Checking deployed version...${NC}"
DEPLOYED_COMMIT=$(vercel inspect https://claude-code-projects.vercel.app 2>&1 | grep -i "commit" | head -1)
echo "Deployed: $DEPLOYED_COMMIT"
echo ""

# Check latest local commit
LATEST_LOCAL=$(git log --oneline -1)
echo "Latest local: $LATEST_LOCAL"
echo ""

# List last 5 commits
echo -e "${YELLOW}2. Recent commits:${NC}"
git log --oneline -5
echo ""

# Common deployment issues to check
echo -e "${YELLOW}3. Checking for common issues...${NC}"
echo ""

# Check if .env.production exists
if [ -f "meal-planner-ui/.env.production" ]; then
    echo -e "${GREEN}✅ .env.production exists${NC}"
else
    echo -e "${RED}❌ .env.production missing${NC}"
fi

# Check if node_modules is in .gitignore
if grep -q "node_modules" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ node_modules in .gitignore${NC}"
else
    echo -e "${YELLOW}⚠️  node_modules not in .gitignore${NC}"
fi

# Check if vercel.json exists in meal-planner-ui
if [ -f "meal-planner-ui/vercel.json" ]; then
    echo -e "${GREEN}✅ vercel.json exists${NC}"
    echo "  Contents:"
    cat meal-planner-ui/vercel.json | head -20
else
    echo -e "${YELLOW}⚠️  No vercel.json (using auto-detection)${NC}"
fi

echo ""

# Check if package.json has correct build script
echo -e "${YELLOW}4. Checking package.json scripts...${NC}"
if grep -q '"build":' meal-planner-ui/package.json; then
    BUILD_SCRIPT=$(grep '"build":' meal-planner-ui/package.json)
    echo -e "${GREEN}✅ Build script found:${NC}"
    echo "  $BUILD_SCRIPT"
else
    echo -e "${RED}❌ No build script in package.json${NC}"
fi

echo ""

# Suggested fixes
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Suggested Actions${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "If deployments are failing, try:"
echo ""
echo "1. Check Vercel dashboard for specific error"
echo "2. Verify environment variables are set in Vercel"
echo "3. Check that all dependencies are in package.json"
echo "4. Try manual deployment:"
echo "   cd meal-planner-ui && vercel --prod"
echo ""
echo "5. Check build logs:"
echo "   vercel logs https://claude-code-projects.vercel.app"
echo ""
