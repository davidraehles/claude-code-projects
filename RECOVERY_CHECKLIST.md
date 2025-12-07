# PR #43 CI/CD Recovery Checklist

**PR**: https://github.com/davidraehles/meal-planner/pull/43
**Status**: 🔴 4 CRITICAL FAILURES (Backend Unit Tests, Frontend Linting, Frontend Tests, Integration Tests)
**Root Cause**: GroceryAggregator refactoring broke 45 unit tests; Frontend has NextAuth/type issues

---

## Quick Summary

### What's Broken
- ❌ Backend Unit Tests: **45 failures** (GroceryAggregator service)
- ❌ Frontend Linting: **ESLint errors** (NextAuth imports, type issues)
- ❌ Frontend Tests: **45+ Jest failures** (type assertions, mocks)
- ❌ Vercel Deployment: **FAILED** (can't deploy - linting failure)

### Root Causes (in priority order)
1. **GroceryAggregator.normalize_units()** - Method signature mismatch (expects 3 params, gets 2)
2. **GroceryAggregator.db** - Tests expect db attribute, constructor doesn't set it properly
3. **parse_ingredient()** - Doesn't handle None, broken unit detection logic
4. **NextAuth imports** - JWT and DefaultSession not exported correctly
5. **Correlation ID middleware** - Error responses missing header
6. **Timestamp precision** - Flaky test in KnusprClient

---

## Phase 1: Backend Fixes (CRITICAL - Blocks Vercel)

### ✅ Task 1.1: Fix normalize_units() Signature [1-2 hours]
```bash
# Check current signature
grep -n "def normalize_units" backend/app/services/grocery_aggregator.py

# Expected: def normalize_units(self, quantity: float, unit: str) -> Tuple[float, str]
# Tests calling: normalize_units(quantity, unit, target_unit)  # EXTRA PARAM!

# Decision: Add target_unit parameter OR update tests to match
# Do NOT guess - read test file to understand intent
```

**Files**:
- `backend/app/services/grocery_aggregator.py:461`
- `backend/tests/unit/test_grocery_aggregator.py`

**Verification**:
```bash
cd backend
pytest tests/unit/test_grocery_aggregator.py::TestNormalizeUnits -xvs
# Should have 15+ tests passing
```

---

### ✅ Task 1.2: Fix GroceryAggregator.db Attribute [30-45 min]
```bash
# Problem: Tests expect self.aggregator.db but constructor doesn't initialize it

# Option A: Update tests to pass db_session
aggregator = GroceryAggregator(db_session=mock_db_session)

# Option B: Fix constructor to handle db properly
def __init__(self, db_session: Optional[Session | AsyncSession] = None):
    self.db_session = db_session  # Don't create confusing self.db
```

**Files**:
- `backend/app/services/grocery_aggregator.py:144`
- `backend/tests/unit/test_grocery_aggregator.py`

**Verification**:
```bash
pytest tests/unit/test_grocery_aggregator.py::TestAggregateFromMealPlan -xvs
# Should have 5+ tests passing
```

---

### ✅ Task 1.3: Add None Validation to parse_ingredient() [15 min]
```python
# In grocery_aggregator.py:350
def parse_ingredient(self, ingredient_string: Optional[str]) -> ParsedIngredient:
    if not ingredient_string or not ingredient_string.strip():
        raise ValueError("Ingredient string cannot be None or empty")
    # ... rest of method
```

**Verification**:
```bash
pytest tests/unit/test_grocery_aggregator.py::TestParseIngredient::test_parse_edge_cases -xvs
```

---

### ✅ Task 1.4: Fix Unit Detection in parse_ingredient() [2-3 hours]
```bash
# Problem: "4 large eggs" parses as qty=4, unit='whole', name='large eggs'
# Should be: qty=4, unit='large', name='eggs'

# Issue: Adjectives not extracted to unit field
# Solution: Review parsing regex, fix to handle adjective descriptors

grep -A 50 "def parse_ingredient" backend/app/services/grocery_aggregator.py
# Look for regex pattern that extracts quantity, unit, name
# Likely regex: something like r'(\d+\.?\d*)\s+(\w+)\s+(.*)'
```

**Files**:
- `backend/app/services/grocery_aggregator.py:350`

**Verification**:
```bash
pytest tests/unit/test_grocery_aggregator.py::TestParseIngredient::test_parse_simple_ingredients -xvs
```

---

### ✅ Task 1.5: Fix AggregatedIngredient Constructor [30 min]
```python
# Problem: Tests call AggregatedIngredient(name=..., quantity=..., unit=...)
# Missing required parameter: original_strings

# Solution A: Make parameter optional
@dataclass
class AggregatedIngredient:
    name: str
    quantity: float
    unit: str
    original_strings: List[str] = field(default_factory=list)

# Solution B: Update tests to pass original_strings
```

**Files**:
- `backend/app/services/grocery_aggregator.py`
- `backend/tests/unit/test_grocery_aggregator.py`

**Verification**:
```bash
pytest tests/unit/test_grocery_aggregator.py::TestAggregatedIngredient -xvs
```

---

### ✅ Task 1.6: Fix Correlation ID Error Header [1 hour]
```bash
# Problem: Error responses (5xx) don't include X-Correlation-ID header
# Test expects: response.headers['X-Correlation-ID']

# Solution: Ensure error response middleware includes correlation ID
# Check: backend/app/middleware/correlation_id.py
# Trace: How errors flow through middleware
```

**Files**:
- `backend/app/middleware/correlation_id.py`

**Verification**:
```bash
pytest tests/unit/test_correlation_id.py::TestCorrelationIdIntegration::test_error_handling_preserves_correlation_id -xvs
```

---

### ✅ Task 1.7: Fix Timestamp Precision Test (Flaky) [30 min]
```bash
# Problem: Timestamp precision - microseconds differ by 30ms between test setup and execution
# Expected: 2025-12-07T17:46:12.385310
# Actual:   2025-12-07T17:46:12.385340

# Solution: Use freezegun to freeze time in tests
# OR: Change assertion to allow small variance

# Install freezegun if not present:
pip install freezegun

# Then in test:
from freezegun import freeze_time

@freeze_time("2025-12-07T17:46:12.385310")
def test_get_delivery_slots_success():
    # Test with frozen time
```

**Files**:
- `backend/tests/unit/test_knuspr_client.py`

**Verification**:
```bash
pytest tests/unit/test_knuspr_client.py::test_get_delivery_slots_success -xvs
# Run 5 times to verify not flaky
```

---

### ✅ Phase 1 Verification: Backend Tests [1 hour]
```bash
cd backend
pytest tests/unit/ -v --tb=short

# Expected: 160 passed, 0 failed (was 160 passed, 45 failed)
# Then run integration tests:
pytest tests/integration/ -v --tb=short
```

---

## Phase 2: Frontend Fixes (AFTER Backend Passes)

### ✅ Task 2.1: Fix ESLint Linting [1-2 hours]
```bash
cd frontend
npm run lint

# Check for errors - likely:
# - NextAuth imports (JWT, DefaultSession)
# - Type errors in meal plan detail page
# - Unused imports

# Common fix:
# - Check NextAuth version in package.json
# - Verify correct imports:
#   import { getServerSession } from "next-auth"
#   import type { NextAuthOptions, Session } from "next-auth"
```

**Files to Check**:
- `frontend/src/app/api/auth/[...nextauth]/route.ts`
- `frontend/src/app/meal-plans/[id]/page.tsx`
- `frontend/src/contexts/AuthContext.tsx`

**Verification**:
```bash
cd frontend && npm run lint
# Should exit with code 0
```

---

### ✅ Task 2.2: Fix Jest Unit Tests [2-3 hours]
```bash
cd frontend
npm test

# Will show 45+ test failures
# Common issues:
# - Type assertion failures
# - Mock setup issues
# - Component initialization problems
# - Snapshot updates needed

# Debug single test:
npm test -- --testNamePattern="test name" --no-coverage
```

**Files to Check**:
- `frontend/__tests__/` - Test directory
- Check meal plan component tests

**Verification**:
```bash
cd frontend && npm test -- --passWithNoTests
# Should have 0 failures
```

---

### ✅ Task 2.3: Run Full Frontend Build [30 min]
```bash
cd frontend
npm run build

# Should complete without errors
# Check for TypeScript errors
npx tsc --noEmit

# Should exit with code 0
```

---

## Phase 3: Verification & Deployment

### ✅ Task 3.1: Full Local Test Suite [1 hour]
```bash
# Backend
cd backend
pytest tests/ -v --tb=short 2>&1 | tail -20
# Expected: All passed

# Frontend
cd frontend
npm test -- --passWithNoTests
npm run lint
npm run build

# All should succeed
```

---

### ✅ Task 3.2: Push Changes & Verify CI [30 min]
```bash
git add -A
git commit -m "fix: Resolve all CI failures in PR #43

- Fix GroceryAggregator normalize_units() signature
- Fix GroceryAggregator db initialization
- Add None handling to parse_ingredient()
- Fix unit detection in parse_ingredient()
- Fix AggregatedIngredient constructor
- Fix Correlation ID in error responses
- Fix timestamp precision in tests
- Fix NextAuth imports in frontend
- Fix Jest unit tests
- Fix ESLint linting"

git push origin fix/meal-plan-detail-page-and-grocery-list-nav
```

**Monitor**:
- Go to PR: https://github.com/davidraehles/meal-planner/pull/43
- Watch GitHub Actions tab
- All checks should turn ✅ GREEN

---

### ✅ Task 3.3: Verify Vercel Deployment [15 min]
```bash
# Check PR for Vercel status
# Click on Vercel preview link
# Verify:
# - Page loads without errors
# - No console errors
# - Meal plan detail page works
# - Grocery list navigation works
```

---

## 📋 Quick Reference: Test Commands

```bash
# Backend unit tests (should fix first)
cd backend && pytest tests/unit/test_grocery_aggregator.py -v

# Backend integration tests
cd backend && pytest tests/integration/ -v

# Frontend linting
cd frontend && npm run lint

# Frontend unit tests
cd frontend && npm test

# Frontend build
cd frontend && npm run build

# Run all tests
cd backend && pytest tests/ -v
cd frontend && npm test && npm run lint && npm run build
```

---

## 🎯 Success Criteria

- [ ] All backend unit tests pass (160+ passed, 0 failed)
- [ ] All backend integration tests pass
- [ ] Frontend linting passes (0 errors)
- [ ] Frontend unit tests pass (0 failures)
- [ ] Frontend builds successfully
- [ ] All GitHub CI checks show ✅ GREEN
- [ ] Vercel preview deployment succeeds
- [ ] PR is ready to merge

---

## ⏱️ Estimated Time

- **Phase 1** (Backend Fixes): 6-8 hours
- **Phase 2** (Frontend Fixes): 5-7 hours
- **Phase 3** (Verification): 2 hours
- **Total**: 13-17 hours (or 8-10 hours with parallelization)

---

## 🆘 If You Get Stuck

1. **GroceryAggregator Issues**: Read the test file to understand what interface it expects
2. **NextAuth Issues**: Check `node_modules/@types/next-auth` or online docs
3. **Flaky Tests**: Run test multiple times, use `freezegun` for time-dependent tests
4. **Type Errors**: Use TypeScript strict mode to identify issues: `npx tsc --noEmit --strict`

---

## 📝 Important Notes

1. **Decision Points**: Some fixes require deciding between updating code vs tests - read the original intent
2. **Test Dependencies**: Backend tests must pass BEFORE frontend can build successfully
3. **Git History**: These are fixes to existing commits, not new features - make sure commit message is clear
4. **PR Description**: Update PR with summary of fixes when submitting

---

**Full Analysis**: See `CI_CD_ROOT_CAUSE_ANALYSIS.md` for detailed technical breakdown
**PR Link**: https://github.com/davidraehles/meal-planner/pull/43
**Generated**: 2025-12-07
