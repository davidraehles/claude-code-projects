# ReAct Agent System: Example Workflows

This document demonstrates real-world workflows using the ReAct pattern agents and skills.

## Workflow 1: Implementing Landing Page Hero Section

### User Request

"Add a hero section to the landing page with smooth animations and accessibility features"

### Step-by-Step Execution

#### Step 1: Specification Analysis

```bash
/spec-analyze 001 "Hero section with animations"
```

**Router Agent Action:**
1. Reads `001-landing-page/spec.md`
2. Extracts hero section requirements
3. Identifies acceptance criteria:
   - Responsive design (320px+)
   - Smooth scroll animations
   - WCAG 2.1 AA accessibility
   - Lighthouse performance 90+
4. Creates specification document

**Output**: Detailed spec analysis with requirements, constraints, and test scenarios

---

#### Step 2: Task Decomposition

```bash
/task-decompose 001-001-01 "Can parallelize testing and documentation"
```

**Router Agent Action:**
1. Reads hero section task from `001-landing-page/tasks.md`
2. Creates subtasks:
   - Task 1.1: Generate Hero component (Frontend Dev)
   - Task 1.2: Add styling and animations (Frontend Dev)
   - Task 1.3: Generate tests (Testing Agent)
   - Task 1.4: Update documentation (Documentation Agent)
3. Identifies dependencies (1.1 before 1.2, but 1.3 & 1.4 can start after 1.1)
4. Creates parallelization plan

**Output**: Task decomposition with critical path analysis and parallelization strategy

---

#### Step 3: Component Generation

```bash
/gen-component Hero 001 "Main hero section with headline, subheadline, CTA, and background image with animations"
```

**Frontend Dev Agent Action:**
1. Generates `src/components/Hero.tsx`:
   - TypeScript with full type safety
   - React 18.x with hooks
   - Framer Motion animations
   - Next.js Image optimization
   - Accessibility features (ARIA, keyboard navigation)

2. Generates `src/__tests__/Hero.test.tsx`:
   - Unit tests with React Testing Library
   - Accessibility tests with jest-axe
   - Responsive design tests
   - Animation behavior tests
   - 95%+ coverage target

3. Generates `stories/Hero.stories.tsx`:
   - Storybook examples
   - Component prop documentation
   - Visual regression testing

**Output**: Fully typed, accessible, tested component ready for styling

---

#### Step 4: Parallel Execution (Starting after Step 3)

**Parallel Stream 1: Frontend Dev continues**

```bash
# No explicit command - agent continues with styling
# Working on src/components/Hero.module.css
```

Frontend Dev Agent:
- Adds Tailwind CSS classes
- Implements responsive grid
- Adds dark mode support
- Tests all breakpoints
- Performance optimizes images

**Parallel Stream 2: Testing & Accessibility**

```bash
/validate-a11y src/components/Hero.tsx
```

Testing Agent:
- Runs jest-axe accessibility scan
- Checks keyboard navigation
- Verifies color contrast
- Tests with screen readers
- Ensures WCAG 2.1 AA compliance

**Parallel Stream 3: Documentation**

```bash
/sync-artifacts 001 "Implemented Hero component with animations"
```

Documentation Agent:
- Updates `001-landing-page/spec.md` marking hero as [IMPLEMENTED]
- Updates `001-landing-page/tasks.md` task status to ✓ Complete
- Links to implementation files
- Updates CHANGELOG.md with new feature entry
- Creates or updates ADR if new patterns used

---

#### Step 5: Quality Validation

```bash
/commit-and-review "feat(landing-page): Add Hero component with animations"
```

Integration & Validation Agent:
1. Runs all quality gates:
   ```
   ✓ Type checking: tsc --noEmit (0 errors)
   ✓ Linting: npm run lint (0 warnings)
   ✓ Format check: prettier --check
   ✓ Unit tests: npm test (234/234 passing)
   ✓ Coverage: 95% (exceeds 90% target)
   ✓ Accessibility: axe-core (WCAG 2.1 AA pass)
   ✓ Performance: Lighthouse 92/100
   ```

2. Creates commit with conventional message
3. Generates merge readiness report

**Output**: Code ready for merge with all quality gates passed

---

### Timeline Comparison

```
Sequential Development:
  Task 1.1 (Component):      15 mins
  Task 1.2 (Styling):        20 mins (after 1.1)
  Task 1.3 (Testing):        20 mins (after 1.1)
  Task 1.4 (Documentation):  10 mins
  Task 1.5 (Validation):     10 mins
  ────────────────────────────────
  Total:                      60-70 mins

Parallel with ReAct:
  Phase 1: Component (15 mins)
  Phase 2: Styling + Testing + Docs (all parallel, 20 mins)
  Phase 3: Validation (5 mins)
  ────────────────────────────────
  Total:                      40 mins

Speedup: 1.5-1.75x faster ⚡
```

---

## Workflow 2: Implementing Recipe API Endpoint

### User Request

"Create API endpoint to get user's recipes with pagination and row-level security"

### Step-by-Step Execution

#### Step 1: Specification Analysis

```bash
/spec-analyze 002 "Recipe retrieval endpoint with pagination"
```

**Spec Analyzer Agent:**
- Reads `002-recipe-system/spec.md` and `data-model.md`
- Identifies Recipe entity and User relationships
- Extracts requirements:
  - GET /recipes endpoint
  - Pagination support (skip/limit)
  - Row-level security (user can only see own recipes)
  - Error handling (404, 403, 422)
  - Response format with metadata
- Test scenarios:
  - Successful retrieval
  - Pagination boundaries
  - Security (user2 can't access user1's recipes)
  - Error cases

---

#### Step 2: Data Model & Migration

Recipe entity already exists in `data-model.md`, so no new migration needed. If adding fields:

```bash
/gen-endpoint /recipes GET Recipe 002
```

**Backend Dev Agent:**
1. Creates `app/endpoints/recipes.py`:
   - FastAPI router with async/await
   - Pydantic V2 schemas (RecipeResponse)
   - Row-level security query filter
   - Pagination with skip/limit
   - Proper error responses

2. If schema change needed, creates migration:
   ```python
   # migrations/versions/20231114_add_recipe_fields.py
   def upgrade():
       # Add new columns
   def downgrade():
       # Remove columns
   ```

3. Generates comprehensive tests in `tests/test_recipes.py`:
   - Test successful retrieval
   - Test pagination
   - Test row-level security
   - Test error handling

---

#### Step 3: Test Generation

```bash
/gen-tests app/endpoints/recipes.py all
```

Testing Agent:
- Unit tests: Individual endpoint logic
- Integration tests: Database interaction
- E2E tests: Full user workflow
- Target: 90%+ coverage

---

#### Step 4: Validation & Review

```bash
/commit-and-review "feat(recipe-system): Add recipe retrieval endpoint with pagination"
```

Integration Agent:
- Type checking: pyright --strict ✓
- Linting: pylint app/ ✓
- Tests: pytest tests/test_recipes.py ✓
- Coverage: 92% ✓
- Database migrations: Valid and tested ✓
- Security: Row-level security verified ✓

---

### Timeline

```
Sequential: ~45 mins (endpoint + tests + validation)
Parallel: ~35 mins (tests run during development)
Speedup: 1.3x
```

---

## Workflow 3: Complete Feature: Services Section

### User Request

"Build the Services section with 6 service cards, responsive grid, and hover effects"

### Decomposition Strategy

```
Services Feature (Complex)
├── Component 1: ServiceCard (single card)
├── Component 2: ServicesGrid (layout 6 cards)
├── Component 3: ServiceModal (detail view)
├── Data: servicesData.ts (content)
└── Tests & Docs (all components)
```

### Parallel Execution Plan

**Wave 1: Parallel Component Generation**
```bash
# Run 3 agents in parallel
/gen-component ServiceCard 001 "Single service card with icon and description"
/gen-component ServicesGrid 001 "Grid layout for 6 services with responsive design"
/gen-component ServiceModal 001 "Modal showing service details"
```

**Wave 2: Parallel Testing** (starts after Wave 1)
```bash
/gen-tests src/components/ServiceCard.tsx
/gen-tests src/components/ServicesGrid.tsx
/gen-tests src/components/ServiceModal.tsx
```

**Wave 3: Validation** (after all tests pass)
```bash
/commit-and-review "feat(landing-page): Add Services section with 6 service cards"
```

### Timeline

```
Wave 1 (Parallel):     ServiceCard + ServicesGrid + ServiceModal  = 30 mins
Wave 2 (Parallel):     Tests for all 3 components                = 25 mins
Wave 3 (Sequential):   Validation                                 = 5 mins
────────────────────────────────────────────────────────────────
Total:                                                            60 mins

Sequential equivalent:
  ServiceCard + tests:      30 mins
  ServicesGrid + tests:     30 mins
  ServiceModal + tests:     25 mins
  Validation:                5 mins
  ──────────────────────────────────
  Total:                    90 mins

Speedup: 1.5x
```

---

## Workflow 4: Database Migration & Deployment

### User Request

"Add new fields to Recipe table for dietary tags and prepare for deployment"

### Step-by-Step

#### Step 1: Plan Changes

```bash
/spec-analyze 002 "Add dietary tags to recipes"
```

#### Step 2: Generate Migration

```bash
/gen-endpoint /recipes POST Recipe 002
# Includes migration for schema changes
```

Backend Dev Agent:
- Creates migration: `migrations/versions/20231114_add_dietary_tags.py`
- Updates ORM model: `app/models/recipe.py`
- Updates Pydantic schema: `app/schemas/recipe.py`
- Generates migration tests

#### Step 3: Validate Migration

```bash
/run-tests 002 integration
```

Tests verify:
- Migration applies cleanly
- Schema changes work
- Old data migrates correctly
- Rollback works if needed

#### Step 4: Full Build & Deploy Prep

```bash
/parallel-build both
```

Output:
- Frontend build: ✓ Success (142 KB)
- Backend build: ✓ Success (0 lint errors)
- Migrations: ✓ Valid and reversible
- Ready for deployment: ✓

---

## Workflow 5: Bug Fix with Regression Tests

### User Request

"Fix accessibility issue in contact form and ensure it doesn't regress"

### Step-by-Step

#### Step 1: Identify Issue

```bash
/validate-a11y src/components/ContactForm.tsx
```

Output: Finds missing `<label>` elements on form inputs

#### Step 2: Fix the Bug

Frontend Dev Agent:
- Adds missing `<label>` elements
- Verifies label association with inputs
- Tests keyboard navigation

#### Step 3: Generate Regression Test

```bash
/gen-tests src/components/ContactForm.tsx
```

Testing Agent:
- Creates test specifically for accessibility
- Tests label association
- Tests keyboard navigation
- Prevents future regressions

#### Step 4: Validate Fix

```bash
/validate-a11y src/components/ContactForm.tsx
```

Output: WCAG 2.1 AA pass ✓

#### Step 5: Commit

```bash
/commit-and-review "fix(landing-page): Add missing labels in contact form for accessibility"
```

---

## Workflow 6: Cross-Feature Integration Test

### User Request

"Ensure landing page contact form successfully submits to backend API"

### Step-by-Step

#### Step 1: E2E Test Generation

```bash
/gen-tests tests/e2e/contact-form-submission.ts e2e
```

Playwright Test:
```typescript
test("user submits contact form and receives confirmation", async () => {
  // 1. Navigate to landing page
  // 2. Scroll to contact section
  // 3. Fill form
  // 4. Submit
  // 5. Verify email received by backend
  // 6. Verify user sees thank you message
});
```

#### Step 2: Run Integration Test

```bash
/run-tests 001 e2e
```

Tests verify:
- Frontend form submission works
- Backend API receives data
- Email service sends confirmation
- User sees success message

---

## Common Patterns & Best Practices

### Pattern 1: Component + Tests + Docs in One Go

```bash
/gen-component ComponentName 001 "Description"
# Automatically generates tests and updates docs
```

### Pattern 2: API Endpoint Development

```bash
/gen-endpoint /path METHOD Entity 002
# Includes model, schema, migration, tests
```

### Pattern 3: Quality Assurance Checklist

```bash
/check-types 001
/validate-a11y src/components/Component.tsx
/run-tests 001
/performance-audit 001
```

### Pattern 4: Pre-Merge Preparation

```bash
/commit-and-review "feat: description"
# Runs all checks and prepares merge
```

### Pattern 5: Parallel Development

```bash
# Start 3 components in parallel
/gen-component Component1 001 "..."
/gen-component Component2 001 "..."
/gen-component Component3 001 "..."

# Then generate tests for all in parallel
/gen-tests src/components/Component1.tsx
/gen-tests src/components/Component2.tsx
/gen-tests src/components/Component3.tsx

# Validate all together
/commit-and-review "feat: Multiple components"
```

---

## Advanced Workflows

### Rollback on Failure

```bash
# If merge fails
git revert <commit-hash>
/sync-artifacts 001 "Reverted feature due to issues"
/update-task 001-001-01 blocked "Investigating issue..."
```

### Feature Branch Management

```bash
# Create feature branch
git checkout -b feature/hero-section

# Develop using ReAct workflows
/gen-component Hero 001 "..."
/gen-tests src/components/Hero.tsx
/commit-and-review

# Push to remote
git push origin feature/hero-section

# Create PR and merge after review
```

### Performance Optimization Sprint

```bash
/performance-audit 001
# Identifies bottlenecks

# Fix bottlenecks
/gen-component OptimizedComponent 001 "..."

# Verify improvement
/performance-audit 001
```

---

## Troubleshooting Workflows

### Test Failure

```
/run-tests 001 unit
# Shows failing test

# View error details
# Fix code or test

/run-tests 001 unit
# Verify fix
```

### Type Errors

```
/check-types 001
# Shows type errors

# Agent suggests fixes
# Fix types

/check-types 001
# Verify all types pass
```

### Merge Conflict

```
# Review conflicts
git status

# Resolve manually or rebase
git rebase main

# Re-run tests
/run-tests 001

# Validate
/commit-and-review
```

---

These workflows demonstrate the power of the ReAct agent system for parallel, efficient development while maintaining quality gates at every step.
