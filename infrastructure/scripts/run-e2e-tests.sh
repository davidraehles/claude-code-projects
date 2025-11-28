#!/bin/bash

##############################################################################
# Playwright E2E Test Runner for Deployed App
#
# Runs E2E tests against deployed Vercel app with comprehensive reporting
# Usage: ./scripts/run-e2e-tests.sh [test-file] [--ui] [--debug]
##############################################################################

set -e

# Configuration
FRONTEND_URL="${FRONTEND_URL:-https://claude-code-projects.vercel.app}"
TEST_FILE="${1:-}"
UI_MODE="${2:-}"
DEBUG_MODE="${3:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Playwright E2E Test Runner${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Configuration:"
echo "  Frontend URL: $FRONTEND_URL"
echo "  Test File: ${TEST_FILE:-All tests}"
echo "  UI Mode: ${UI_MODE:-disabled}"
echo "  Debug Mode: ${DEBUG_MODE:-disabled}"
echo ""

# Verify app is accessible
echo -e "${YELLOW}Checking if app is accessible...${NC}"
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓ App is accessible${NC}"
else
    echo -e "${RED}✗ App is not accessible at $FRONTEND_URL${NC}"
    echo "  Please check the URL and try again"
    exit 1
fi
echo ""

# Set environment variables for tests
export NEXT_PUBLIC_API_URL="https://claude-code-projects-production.up.railway.app"
export FRONTEND_URL="$FRONTEND_URL"
export PLAYWRIGHT_TEST_BASE_URL="$FRONTEND_URL"

echo "Environment variables:"
echo "  NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL"
echo "  PLAYWRIGHT_TEST_BASE_URL: $FRONTEND_URL"
echo ""

# Build test command
TEST_CMD="npx playwright test"

if [ -n "$TEST_FILE" ]; then
    TEST_CMD="$TEST_CMD e2e/$TEST_FILE"
fi

if [ "$UI_MODE" = "--ui" ]; then
    TEST_CMD="$TEST_CMD --ui"
fi

if [ "$DEBUG_MODE" = "--debug" ]; then
    TEST_CMD="$TEST_CMD --debug"
fi

# Add verbose reporting
TEST_CMD="$TEST_CMD --reporter=html --reporter=list"

# Run tests
echo -e "${BLUE}Running tests...${NC}"
echo "Command: $TEST_CMD"
echo ""

if $TEST_CMD; then
    echo ""
    echo -e "${GREEN}✓ Tests completed successfully${NC}"
    echo ""
    echo "Reports generated:"
    echo "  HTML Report: playwright-report/index.html"
    echo ""
    echo "To view the report, run:"
    echo "  npx playwright show-report"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Tests failed${NC}"
    echo ""
    echo "Reports generated:"
    echo "  HTML Report: playwright-report/index.html"
    echo ""
    echo "To view the report, run:"
    echo "  npx playwright show-report"
    exit 1
fi
