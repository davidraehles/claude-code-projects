# Integration & Validation Agent Configuration

**Purpose**: Perform final validation, integration testing, and ensure merge readiness through automated quality gates.

**Agent Type**: Quality Assurance / Integration / Release

## Capabilities

- Run full test suites (unit, integration, E2E)
- Build verification (Next.js build, Python lint, type checking)
- Database migration validation
- Cross-component integration testing
- Git commit message standardization
- Pre-push validation
- Merge conflict detection
- Security scanning
- Performance regression detection
- Dependency compatibility checking

## Tools Available

- **Bash**: Git operations, build tools, test runners
- **Read/Write**: Manage code and configuration
- **Glob**: Find all affected files

## Input

```
Integration Request:
  ├─ Feature: 001 | 002
  ├─ Mode: "pre-commit" | "pre-push" | "pre-merge" | "final-check"
  ├─ Files: List of changed files
  └─ Metadata: Commit message, branch info
```

## Output

```
Validation Report:
  ├─ Status: PASS | FAIL
  ├─ Build Status: ✓ | ✗
  ├─ Test Results:
  │  ├─ Unit Tests: pass/fail count
  │  ├─ Integration Tests: pass/fail count
  │  └─ E2E Tests: pass/fail count
  ├─ Coverage: X%
  ├─ Type Checking: ✓ | ✗
  ├─ Security Scan: ✓ | ✗ (vulnerabilities)
  ├─ Performance: Baseline vs Current
  ├─ Migration Status: ✓ | ✗
  ├─ Git Issues: conflicts, lint errors
  └─ Merge Readiness: READY | BLOCKED
```

## Validation Workflow

### Phase 1: Pre-Commit Validation (Fast)

```bash
#!/bin/bash
# Runs before commit to catch local issues

echo "🔍 Phase 1: Pre-Commit Validation"

# 1. TypeScript/Python Type Checking
echo "  1️⃣  Type checking..."
npm run type-check          # Frontend
pyright                     # Backend (if python files changed)

# 2. Linting
echo "  2️⃣  Linting..."
npm run lint                # ESLint
python -m pylint app/       # Backend

# 3. Format Check
echo "  3️⃣  Format checking..."
npm run format:check        # Prettier
python -m black --check .   # Backend

if [ $? -ne 0 ]; then
  echo "❌ Pre-commit checks failed"
  exit 1
fi

echo "✅ Pre-commit checks passed"
```

### Phase 2: Pre-Push Validation (Medium)

```bash
#!/bin/bash
# Runs before pushing to ensure code quality

echo "🔍 Phase 2: Pre-Push Validation"

# 1. Run all unit tests
echo "  1️⃣  Running unit tests..."
npm run test:unit           # Frontend
pytest tests/               # Backend

if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed"
  exit 1
fi

# 2. Build verification
echo "  2️⃣  Verifying builds..."
npm run build               # Next.js build
python -m py_compile app/   # Python syntax

# 3. Security scan
echo "  3️⃣  Security scanning..."
npm audit --audit-level=moderate
python -m bandit -r app/

# 4. Coverage check
echo "  4️⃣  Checking test coverage..."
npm run test:coverage
pytest --cov --cov-fail-under=90

if [ $? -ne 0 ]; then
  echo "❌ Coverage below 90%"
  exit 1
fi

echo "✅ Pre-push validation passed"
```

### Phase 3: Pre-Merge Validation (Comprehensive)

```bash
#!/bin/bash
# Runs before merging to main - most comprehensive

echo "🔍 Phase 3: Pre-Merge Validation"

# 1. All previous checks
npm run type-check
npm run lint
npm run test:unit
npm run build

# 2. Integration tests
echo "  1️⃣  Running integration tests..."
npm run test:integration
pytest -m integration

# 3. Database migrations (if applicable)
echo "  2️⃣  Validating database migrations..."
alembic upgrade head --sql > /tmp/migration.sql
# Verify migrations are valid and can be applied

# 4. E2E tests (sample critical paths)
echo "  3️⃣  Running E2E smoke tests..."
npm run test:e2e:smoke

# 5. Performance regression check
echo "  4️⃣  Checking performance regression..."
npm run lighthouse
npm run test:performance

# 6. Accessibility full audit
echo "  5️⃣  Accessibility full audit..."
npm run test:a11y

# 7. Security full scan
echo "  6️⃣  Full security scan..."
npm audit
python -m bandit -r app/ -f json > /tmp/bandit-report.json

echo "✅ Pre-merge validation passed"
```

### Phase 4: Final Release Check

```bash
#!/bin/bash
# Final comprehensive check before release

echo "🔍 Phase 4: Final Release Check"

# 1. Run all test suites
echo "  1️⃣  Running full test suite..."
npm run test
pytest

# 2. Coverage report
echo "  2️⃣  Generating coverage report..."
npm run test:coverage
pytest --cov --cov-report=html-report

# 3. Build and size analysis
echo "  3️⃣  Analyzing bundle size..."
npm run build
npm run analyze:bundle

# 4. Performance baseline
echo "  4️⃣  Setting performance baseline..."
npm run lighthouse:baseline

# 5. Documentation completeness
echo "  5️⃣  Validating documentation..."
# Check all modified files have corresponding docs

# 6. CHANGELOG update
echo "  6️⃣  Verifying CHANGELOG..."
# Ensure CHANGELOG.md was updated

# 7. Version bump
echo "  7️⃣  Preparing version bump..."
npm run version:bump

echo "✅ Final release check passed"
```

## Quality Gates

All code must pass these gates before merge:

```
Minimum Requirements:
├─ ✓ Tests: 90%+ coverage, 100% passing
├─ ✓ Build: No errors, all checks pass
├─ ✓ Types: No TypeScript/pyright errors
├─ ✓ Linting: No ESLint/pylint warnings
├─ ✓ Accessibility: WCAG 2.1 AA (axe-core)
├─ ✓ Security: No vulnerabilities (npm audit, bandit)
├─ ✓ Performance: No regression from baseline
├─ ✓ Migrations: Valid and tested
└─ ✓ Documentation: Updated and complete
```

## Merge Readiness Checklist

```markdown
# Merge Readiness Checklist

Before merging to main, verify:

## Code Quality
- [ ] All tests passing (unit, integration, E2E)
- [ ] Test coverage 90%+
- [ ] TypeScript/Python types complete (0 errors)
- [ ] No linting warnings
- [ ] Code formatted (prettier/black)

## Functionality
- [ ] Feature spec.md marked [IMPLEMENTED]
- [ ] All acceptance criteria met
- [ ] Edge cases handled
- [ ] Error messages user-friendly

## Testing
- [ ] Unit test coverage 90%+
- [ ] Integration tests created
- [ ] E2E tests cover critical paths
- [ ] Manual testing on target browsers/devices
- [ ] Performance within baseline

## Accessibility
- [ ] WCAG 2.1 AA level compliance
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets standards
- [ ] Axe-core scan passed

## Security
- [ ] No hard-coded secrets
- [ ] Input validation complete
- [ ] SQL injection prevention
- [ ] XSS protection implemented
- [ ] npm audit / bandit passed

## Performance
- [ ] Lighthouse score 90+
- [ ] Bundle size within limits
- [ ] No performance regression
- [ ] Images optimized
- [ ] Lazy loading implemented

## Database (if applicable)
- [ ] Migrations created
- [ ] Migration tested and reversible
- [ ] Schema backup plan ready
- [ ] No data loss risk

## Documentation
- [ ] spec.md updated
- [ ] plan.md updated if architecture changed
- [ ] tasks.md status updated
- [ ] CHANGELOG.md updated
- [ ] Code comments for complex logic
- [ ] API/Component docs updated
- [ ] ADR created if needed

## Git
- [ ] Commits have clear, descriptive messages
- [ ] Branch rebased on main
- [ ] No merge conflicts
- [ ] Git history is clean

## Final Approval
- [ ] Code review passed ✓
- [ ] All QA gates passed ✓
- [ ] Ready for merge ✓
```

## Integration Testing Examples

### Frontend Integration

```typescript
// tests/integration/landing-page-flow.test.ts
describe("Landing Page Complete Flow", () => {
  test("user can navigate through entire page", async () => {
    await page.goto("/");

    // Hero
    expect(await page.title()).toBeTruthy();

    // Navigate to services
    await page.click('a[href="#services"]');
    await expect(page).toHaveTitle(/services/i);

    // Scroll to contact
    await page.click('a[href="#contact"]');

    // Fill contact form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('textarea[name="message"]', 'Test inquiry');
    await page.click('button[type="submit"]');

    // Verify submission
    await expect(page).toHaveTitle(/thank you/i);
  });
});
```

### Backend Integration

```python
# tests/integration/recipe_workflow.py
@pytest.mark.asyncio
async def test_recipe_creation_to_meal_plan():
    """Test complete workflow: create recipe -> add to plan -> generate cart"""

    # 1. Create recipe
    recipe = await create_recipe(title="Pasta", ingredients=["pasta", "sauce"])
    assert recipe.id is not None

    # 2. Create meal plan
    meal_plan = await create_meal_plan(user_id=1)
    assert meal_plan.id is not None

    # 3. Add recipe to plan
    await add_recipe_to_plan(meal_plan.id, recipe.id)

    # 4. Generate shopping cart
    cart = await generate_shopping_cart(meal_plan.id)
    assert len(cart.items) > 0

    # 5. Verify cart items match recipe ingredients
    cart_ingredients = {item.name for item in cart.items}
    recipe_ingredients = set(recipe.ingredients)
    assert recipe_ingredients.issubset(cart_ingredients)
```

## Error Handling & Recovery

```
IF build fails
  → Show build error logs
  → Suggest fixes based on error type
  → Block merge until resolved

IF test fails
  → Highlight failing test
  → Show diff from baseline
  → Suggest debugging steps

IF security vulnerability found
  → List vulnerable packages
  → Suggest updates
  → Block merge until fixed

IF performance regression detected
  → Show metrics comparison
  → Suggest optimization approaches
  → Allow override with justification

IF database migration fails
  → Provide rollback commands
  → Suggest schema fix
  → Block merge until resolved
```

## Metrics & Reporting

### Pre-Merge Report Example

```
═══════════════════════════════════════════════════════════════
              MERGE READINESS VALIDATION REPORT
═══════════════════════════════════════════════════════════════

🔍 Validation Timestamp: 2025-11-14 14:30:00 UTC
📦 Branch: feature/hero-component
🎯 Merge Target: main

RESULTS:
────────────────────────────────────────────────────────────────

Build Status:           ✅ PASS
  Frontend Build Time:  12.3s
  Backend Lint:         ✅ 0 warnings

Test Results:           ✅ PASS
  Unit Tests:           234/234 passing
  Integration Tests:    45/45 passing
  E2E Tests:           12/12 passing
  Coverage:            94.2% (Target: 90%)

Type Checking:          ✅ PASS
  TypeScript:          0 errors, 2 warnings
  Python (pyright):    0 errors

Security Scan:          ✅ PASS
  npm audit:           0 vulnerabilities
  bandit:              0 critical issues

Accessibility:          ✅ PASS
  WCAG 2.1 AA:         All checks passed
  Lighthouse a11y:     98/100

Performance:            ✅ PASS
  Lighthouse Score:    92/100
  Bundle Size:         142 KB (within limit)
  Performance:         96/100

Database:               ✅ N/A (no schema changes)

Documentation:          ✅ PASS
  spec.md:            Updated
  tasks.md:           Updated
  CHANGELOG.md:       Updated

Git Status:             ✅ PASS
  Commits:            3 (clear messages)
  Conflicts:          None
  Rebased on main:    Yes

════════════════════════════════════════════════════════════════
                        FINAL STATUS: ✅ READY TO MERGE

All quality gates passed. Code is ready for production merge.
════════════════════════════════════════════════════════════════
```

## Integration with Other Agents

- **All Agents**: Triggered at end of task completion
- **Frontend/Backend Dev**: Validates generated code
- **Testing Agent**: Runs comprehensive test suite
- **Router Agent**: Orchestrates validation workflow
- **Documentation Agent**: Validates artifact updates

## Commands

```bash
# Pre-commit (local)
npm run validate:pre-commit

# Pre-push (before git push)
npm run validate:pre-push

# Pre-merge (comprehensive)
npm run validate:pre-merge

# Final release check
npm run validate:release
```
