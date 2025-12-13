#!/bin/bash
# Security Middleware Test Script
# Tests rate limiting and security headers

set -e

API_URL="${API_URL:-http://localhost:8000}"
echo "Testing API at: $API_URL"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test security headers
test_security_headers() {
    echo -e "\n${YELLOW}Testing Security Headers...${NC}"

    response=$(curl -s -i "$API_URL/health")

    # Check for each security header
    headers=(
        "X-Content-Type-Options: nosniff"
        "X-Frame-Options: DENY"
        "X-XSS-Protection: 1; mode=block"
        "Referrer-Policy: strict-origin-when-cross-origin"
    )

    for header in "${headers[@]}"; do
        if echo "$response" | grep -qi "$header"; then
            echo -e "${GREEN}✓${NC} Found: $header"
        else
            echo -e "${RED}✗${NC} Missing: $header"
        fi
    done
}

# Function to test rate limit headers
test_rate_limit_headers() {
    echo -e "\n${YELLOW}Testing Rate Limit Headers...${NC}"

    response=$(curl -s -i "$API_URL/health")

    headers=(
        "X-RateLimit-Limit"
        "X-RateLimit-Remaining"
        "X-RateLimit-Reset"
    )

    for header in "${headers[@]}"; do
        if echo "$response" | grep -qi "$header"; then
            echo -e "${GREEN}✓${NC} Found: $header"
            # Extract and display value
            value=$(echo "$response" | grep -i "$header" | cut -d: -f2- | xargs)
            echo "  Value: $value"
        else
            echo -e "${RED}✗${NC} Missing: $header"
        fi
    done
}

# Function to test rate limiting (anonymous user)
test_rate_limiting() {
    echo -e "\n${YELLOW}Testing Rate Limiting (making 5 requests)...${NC}"

    success_count=0
    rate_limited_count=0

    for i in {1..5}; do
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")

        if [ "$http_code" = "200" ]; then
            ((success_count++))
            echo -e "${GREEN}✓${NC} Request $i: Success (200)"
        elif [ "$http_code" = "429" ]; then
            ((rate_limited_count++))
            echo -e "${YELLOW}!${NC} Request $i: Rate Limited (429)"
        else
            echo -e "${RED}✗${NC} Request $i: Unexpected status ($http_code)"
        fi

        sleep 0.1
    done

    echo -e "\nResults: $success_count successful, $rate_limited_count rate limited"

    # Health check should never be rate limited
    if [ $rate_limited_count -gt 0 ]; then
        echo -e "${RED}⚠${NC} Warning: Health check should not be rate limited!"
    else
        echo -e "${GREEN}✓${NC} Health check correctly exempted from rate limiting"
    fi
}

# Function to check application logs
check_logs() {
    echo -e "\n${YELLOW}Checking Application Logs...${NC}"

    if [ -f "logs/app.log" ]; then
        echo "Recent rate limit events:"
        grep -i "rate limit" logs/app.log | tail -5 || echo "No rate limit events found"
    else
        echo -e "${YELLOW}No log file found${NC}"
    fi
}

# Main test execution
echo -e "${YELLOW}Starting Security Middleware Tests${NC}"
echo "================================"

# Test 1: Security Headers
test_security_headers

# Test 2: Rate Limit Headers
test_rate_limit_headers

# Test 3: Rate Limiting Behavior
test_rate_limiting

# Test 4: Check logs (if available)
# check_logs

echo -e "\n${YELLOW}================================${NC}"
echo -e "${GREEN}Testing Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start Docker services: docker-compose up -d"
echo "2. Check logs: docker logs -f recipe-api"
echo "3. Test authenticated endpoints with JWT token"
echo "4. Monitor rate limit violations in logs"
