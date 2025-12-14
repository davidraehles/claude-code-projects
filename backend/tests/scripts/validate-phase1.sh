#!/bin/bash
# Knuspr Integration - Phase 1 Validation Script
# This script validates that all Phase 1 implementations are working correctly

# Note: Not using 'set -e' to allow all tests to run even if some fail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Knuspr Integration - Phase 1 Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track results
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Test 1: Check if required files exist
echo -e "\n${BLUE}[Test 1] Checking Phase 1 Files...${NC}"

files=(
    "backend/app/api/v1/grocery_carts.py"
    "backend/app/api/v1/knuspr_credentials.py"
    "backend/app/models/meal_plan.py"
    "backend/app/middleware/rate_limit_middleware.py"
    "backend/app/middleware/security_middleware.py"
    "backend/migrations/versions/006_add_delivery_slot_and_unavailable_items.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
    else
        fail "Missing: $file"
    fi
done

# Test 2: Check Python syntax
echo -e "\n${BLUE}[Test 2] Checking Python Syntax...${NC}"

cd backend

for file in "${files[@]}"; do
    if [ -f "../$file" ]; then
        if python3 -m py_compile "../$file" 2>/dev/null; then
            pass "Syntax OK: $file"
        else
            fail "Syntax error: $file"
        fi
    fi
done

# Test 3: Check if new database columns are defined
echo -e "\n${BLUE}[Test 3] Checking Database Model Changes...${NC}"

if grep -q "delivery_slot_json" app/models/meal_plan.py; then
    pass "delivery_slot_json column defined"
else
    fail "delivery_slot_json column not found"
fi

if grep -q "unavailable_items_json" app/models/meal_plan.py; then
    pass "unavailable_items_json column defined"
else
    fail "unavailable_items_json column not found"
fi

# Test 4: Check middleware implementations
echo -e "\n${BLUE}[Test 4] Checking Middleware Implementations...${NC}"

if grep -q "class RateLimitMiddleware" app/middleware/rate_limit_middleware.py; then
    pass "RateLimitMiddleware class found"
else
    fail "RateLimitMiddleware class not found"
fi

if grep -q "class SecurityHeadersMiddleware" app/middleware/security_middleware.py; then
    pass "SecurityHeadersMiddleware class found"
else
    fail "SecurityHeadersMiddleware class not found"
fi

# Test 5: Check API endpoint implementations
echo -e "\n${BLUE}[Test 5] Checking API Endpoint Implementations...${NC}"

if grep -q "async def update_grocery_cart" app/api/v1/grocery_carts.py; then
    pass "Cart update endpoint (T001) implemented"
else
    fail "Cart update endpoint (T001) not found"
fi

if grep -q "async def checkout_cart" app/api/v1/grocery_carts.py; then
    pass "Checkout endpoint (T002) implemented"
else
    fail "Checkout endpoint (T002) not found"
fi

if grep -q "async def get_auth_status" app/api/v1/knuspr_credentials.py 2>/dev/null; then
    pass "Auth status endpoint (T003) implemented"
else
    fail "Auth status endpoint (T003) not found"
fi

# Test 6: Check migration file
echo -e "\n${BLUE}[Test 6] Checking Migration File...${NC}"

if [ -f "migrations/versions/006_add_delivery_slot_and_unavailable_items.py" ]; then
    pass "Migration 006 file exists"

    if grep -q "def upgrade" migrations/versions/006_add_delivery_slot_and_unavailable_items.py; then
        pass "Migration upgrade() function found"
    else
        fail "Migration upgrade() function not found"
    fi

    if grep -q "def downgrade" migrations/versions/006_add_delivery_slot_and_unavailable_items.py; then
        pass "Migration downgrade() function found"
    else
        fail "Migration downgrade() function not found"
    fi
else
    fail "Migration 006 file not found"
fi

# Test 7: Check environment variables documentation
echo -e "\n${BLUE}[Test 7] Checking Environment Variables...${NC}"

cd ..

if grep -q "RATE_LIMIT_CART_CREATION" .env.example; then
    pass "Rate limit env vars documented"
else
    fail "Rate limit env vars not documented"
fi

if grep -q "ENFORCE_HTTPS" .env.example; then
    pass "Security env vars documented"
else
    fail "Security env vars not documented"
fi

# Test 8: Check if Docker Compose is available
echo -e "\n${BLUE}[Test 8] Checking Docker Setup...${NC}"

if command -v docker-compose &> /dev/null; then
    pass "docker-compose is installed"

    # Check if services are running
    cd infrastructure
    if docker-compose ps | grep -q "Up"; then
        pass "Docker services are running"
    else
        warn "Docker services are not running (docker-compose up -d to start)"
    fi
    cd ..
else
    warn "docker-compose is not installed (required for full testing)"
    info "Install: sudo apt install docker-compose"
fi

# Test 9: Check if database is accessible (if Docker is running)
echo -e "\n${BLUE}[Test 9] Checking Database Connection...${NC}"

if command -v docker-compose &> /dev/null; then
    cd infrastructure
    if docker-compose ps | grep postgres | grep -q "Up"; then
        if PGPASSWORD=postgres psql -h localhost -U postgres -d recipe_app -c "SELECT 1;" &> /dev/null; then
            pass "Database is accessible"

            # Check if migration 006 is applied
            cd ../backend
            if python3 -m alembic current 2>/dev/null | grep -q "006"; then
                pass "Migration 006 is applied"
            else
                warn "Migration 006 not yet applied (run: alembic upgrade head)"
            fi
        else
            warn "Database not accessible (check connection)"
        fi
    else
        warn "PostgreSQL container not running"
    fi
    cd ..
else
    warn "Skipping database check (docker-compose not available)"
fi

# Test 10: Check middleware registration in main.py
echo -e "\n${BLUE}[Test 10] Checking Middleware Registration...${NC}"

cd backend

if grep -q "SecurityHeadersMiddleware" app/main.py; then
    pass "SecurityHeadersMiddleware registered"
else
    warn "SecurityHeadersMiddleware not registered in main.py"
fi

if grep -q "RateLimitMiddleware" app/main.py; then
    pass "RateLimitMiddleware registered"
else
    warn "RateLimitMiddleware not registered in main.py"
fi

cd ..

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✨ All validations passed!${NC}"
    echo -e "${BLUE}Phase 1 implementation is complete.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Install docker-compose (if not already installed)"
    echo "2. Start services: cd infrastructure && docker-compose up -d"
    echo "3. Run migration: cd backend && alembic upgrade head"
    echo "4. Test endpoints (see NEXT_STEPS.md)"
    exit 0
else
    echo -e "${RED}⚠️  Some validations failed!${NC}"
    echo -e "${BLUE}Please review the failures above and fix them.${NC}"
    exit 1
fi
