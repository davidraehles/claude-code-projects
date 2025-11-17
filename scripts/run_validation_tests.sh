#!/bin/bash
# Automated Validation Test Suite for Phase 2 Enhancements
# Run this script to validate all enhancements in one go

set -e  # Exit on error

echo "========================================="
echo "Phase 2 Enhancements Validation Suite"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper function to run test
run_test() {
    local test_name=$1
    local test_command=$2

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${YELLOW}[TEST $TESTS_TOTAL]${NC} $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

run_test "Docker is running" "docker ps"
run_test "Database is accessible" "docker exec recipe-postgres psql -U postgres -c 'SELECT 1;'"
run_test "API is responding" "curl -f http://localhost:8000/health"
run_test "Redis is running" "docker exec recipe-redis redis-cli ping"

echo ""
echo "========================================="
echo "PART 1: Database Migration Tests"
echo "========================================="
echo ""

run_test "Apply migration 005" "docker exec recipe-api alembic upgrade head"
run_test "Verify dietary_tags column exists" "docker exec recipe-postgres psql -U postgres -d recipe_app -c '\d recipes' | grep dietary_tags"
run_test "Check migration history" "docker exec recipe-api alembic current | grep 005"

echo ""
echo "========================================="
echo "PART 2: Unit Test Suite"
echo "========================================="
echo ""

# Run enhanced tests
echo "Running enhanced test suite..."
if docker exec recipe-api pytest tests/test_meal_plans_enhanced.py -v --tb=short; then
    echo -e "${GREEN}✅ All enhanced tests passed${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Some enhanced tests failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Run original tests (regression check)
echo ""
echo "Running original tests (regression check)..."
if docker exec recipe-api pytest tests/test_meal_plans.py -v --tb=short; then
    echo -e "${GREEN}✅ All original tests passed (no regressions)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Some original tests failed (REGRESSION!)${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Run with coverage
echo ""
echo "Generating coverage report..."
docker exec recipe-api pytest tests/test_meal_plans_enhanced.py \
    --cov=app.agents.meal_architect \
    --cov-report=term \
    --cov-report=html \
    -q

echo ""
echo "========================================="
echo "PART 3: Feature Validation"
echo "========================================="
echo ""

# Test dietary filtering
echo "Testing dietary restriction filtering..."
VEGAN_TEST=$(cat <<'EOF'
from app.database import SessionLocal
from app.agents.meal_architect import MealArchitectAgent
from app.models.recipe import Recipe
from app.models.user import User

db = SessionLocal()

# Create test user if needed
user = db.query(User).filter_by(email="test@validation.com").first()
if not user:
    user = User(email="test@validation.com", password_hash="test", country="DE")
    db.add(user)
    db.commit()

# Create test recipes
vegan_recipe = Recipe(
    user_id=user.id,
    title="Vegan Test Recipe",
    ingredients=["quinoa", "beans"],
    instructions="Cook",
    dietary_tags=["vegan"],
    source_url="https://test.com/vegan-1",
    source_type="html"
)

meat_recipe = Recipe(
    user_id=user.id,
    title="Meat Test Recipe",
    ingredients=["chicken", "rice"],
    instructions="Cook",
    dietary_tags=[],
    source_url="https://test.com/meat-1",
    source_type="html"
)

db.add(vegan_recipe)
db.add(meat_recipe)
db.commit()

# Test filtering
agent = MealArchitectAgent(db)
candidates = agent._get_candidate_recipes(
    user_id=user.id,
    dietary_restrictions=["vegan"],
    excluded_ingredients=None,
    min_recipes=1
)

# Should only include vegan recipe
recipe_ids = [r.id for r in candidates]
assert vegan_recipe.id in recipe_ids, "Vegan recipe not found"
assert meat_recipe.id not in recipe_ids, "Meat recipe incorrectly included"

print("✅ Dietary filtering works correctly")
db.close()
EOF
)

if docker exec recipe-api python3 -c "$VEGAN_TEST" 2>&1; then
    echo -e "${GREEN}✅ Dietary filtering test passed${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Dietary filtering test failed${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""
echo "========================================="
echo "PART 4: Performance Check"
echo "========================================="
echo ""

# Check API response time
echo "Measuring API response time..."
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:8000/health)
echo "Health endpoint response time: ${RESPONSE_TIME}s"

if (( $(echo "$RESPONSE_TIME < 0.5" | bc -l) )); then
    echo -e "${GREEN}✅ Response time acceptable${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Response time slow (> 0.5s)${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""
echo "========================================="
echo "FINAL RESULTS"
echo "========================================="
echo ""
echo "Total Tests: $TESTS_TOTAL"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

# Calculate success rate
SUCCESS_RATE=$(echo "scale=1; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc)
echo "Success Rate: ${SUCCESS_RATE}%"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Phase 2 is production-ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review coverage report: open htmlcov/index.html"
    echo "2. Test manually via Swagger UI: http://localhost:8000/api/docs"
    echo "3. Proceed to Phase 2C or Phase 3"
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "1. Check logs: docker logs recipe-api"
    echo "2. Review test output for details"
    echo "3. Fix issues and re-run: ./scripts/run_validation_tests.sh"
    exit 1
fi
