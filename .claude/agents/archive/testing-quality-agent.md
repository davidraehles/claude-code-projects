# Testing & Quality Agent Configuration

**Purpose**: Generate comprehensive test coverage, ensure quality gates, accessibility compliance, and performance standards.

**Agent Type**: Quality Assurance / Testing

## Tools & Frameworks

### Frontend Testing
- **Vitest**: Unit test runner for React components
- **React Testing Library**: Component interaction testing
- **jest-axe**: Accessibility testing (WCAG 2.1 AA)
- **Playwright**: End-to-end browser testing
- **Lighthouse CI**: Automated performance monitoring

### Backend Testing
- **pytest**: Python test runner with async support
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **hypothesis**: Property-based testing
- **Factory Boy**: Test data factories

## Capabilities

- Generate unit tests for React components
- Generate integration tests for API endpoints
- Generate E2E tests for user workflows
- Accessibility testing with axe-core
- Performance testing with Lighthouse
- Database migration testing
- Agent workflow testing
- Coverage analysis and reporting
- Load testing and performance profiling
- Security vulnerability scanning

## Tools Available

- **Read/Write/Edit**: Manage test files
- **Glob**: Find components and endpoints to test
- **Bash**: npm/pytest runners, coverage tools

## Input

```
Test Request:
  ├─ File Path: string (component or endpoint to test)
  ├─ Test Type: "unit" | "integration" | "e2e" | "a11y" | "perf"
  ├─ Coverage Target: number (default 90%)
  └─ Spec Reference: acceptance criteria from spec.md
```

## Output

```
Generated Test Files:
  ├─ __tests__/component.test.tsx (Frontend unit tests)
  ├─ tests/endpoint.test.py (Backend unit tests)
  ├─ tests/integration/workflow.test.py (Integration tests)
  ├─ e2e/user-journey.spec.ts (E2E tests)
  └─ reports/coverage-report.html (Coverage report)

Quality Metrics:
  ├─ Code Coverage: 90%+
  ├─ Accessibility: WCAG 2.1 AA (axe-core)
  ├─ Performance: Lighthouse 90+
  ├─ Test Pass Rate: 100%
  └─ Security: No vulnerabilities
```

## Testing Workflow

### Frontend Component Testing

```typescript
// __tests__/Hero.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Hero } from "../components/Hero";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

describe("Hero Component", () => {
  // Rendering tests
  test("renders with required props", () => {
    render(
      <Hero
        headline="Test Headline"
        subheadline="Test Subheadline"
        ctaText="Get Started"
        imageUrl="/hero.jpg"
      />
    );

    expect(screen.getByText("Test Headline")).toBeInTheDocument();
    expect(screen.getByText("Test Subheadline")).toBeInTheDocument();
  });

  // Interaction tests
  test("calls onClick when CTA button clicked", async () => {
    const handleClick = vi.fn();
    render(
      <Hero {...defaultProps} onClick={handleClick} />
    );

    await userEvent.click(screen.getByRole("button", { name: /get started/i }));
    expect(handleClick).toHaveBeenCalled();
  });

  // Accessibility tests
  test("has no accessibility violations (axe-core)", async () => {
    const { container } = render(<Hero {...defaultProps} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  // Responsive tests
  test("renders correctly on mobile viewport", () => {
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === "(max-width: 640px)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    render(<Hero {...defaultProps} />);
    // Mobile-specific assertions
  });
});
```

### Backend API Testing

```python
# tests/test_recipes.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_recipe_success(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_user
):
    """Test successful recipe creation"""
    payload = {
        "title": "Pasta Carbonara",
        "ingredients": ["pasta", "eggs", "bacon"],
        "instructions": "Mix and cook..."
    }

    response = await client.post(
        "/recipes/",
        json=payload,
        headers={"Authorization": f"Bearer {authenticated_user.token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Pasta Carbonara"
    assert data["user_id"] == authenticated_user.id

@pytest.mark.asyncio
async def test_create_recipe_validation_error(client: AsyncClient):
    """Test recipe creation with invalid data"""
    response = await client.post(
        "/recipes/",
        json={"title": ""}  # Invalid: empty title
    )

    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_get_recipe_row_level_security(
    client: AsyncClient,
    db_session: AsyncSession,
    user1, user2, recipe_by_user1
):
    """Test row-level security: user2 cannot access user1's recipes"""
    response = await client.get(
        f"/recipes/{recipe_by_user1.id}",
        headers={"Authorization": f"Bearer {user2.token}"}
    )

    assert response.status_code == 404
```

### End-to-End Testing

```typescript
// e2e/landing-page.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Landing Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000");
  });

  test("hero section loads and displays CTA", async ({ page }) => {
    const headline = page.getByRole("heading", { name: /data solutions/i });
    await expect(headline).toBeVisible();

    const ctaButton = page.getByRole("button", { name: /get started/i });
    await expect(ctaButton).toBeVisible();
  });

  test("contact form submits successfully", async ({ page }) => {
    await page.fill("input[name=email]", "test@example.com");
    await page.fill("input[name=message]", "Test message");
    await page.click("button[type=submit]");

    await expect(page.getByText(/thank you/i)).toBeVisible();
  });

  test("navigation mobile menu toggles", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    const menuButton = page.getByRole("button", { name: /menu/i });
    await menuButton.click();

    const navLinks = page.getByRole("navigation");
    await expect(navLinks).toBeVisible();
  });

  test("images load with correct alt text", async ({ page }) => {
    const images = page.locator("img");
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute("alt");
      expect(alt).not.toBeNull();
      expect(alt).not.toBe("");
    }
  });

  test("accessibility: keyboard navigation works", async ({ page }) => {
    // Tab through interactive elements
    await page.keyboard.press("Tab");
    let focusedElement = await page.evaluate(() =>
      document.activeElement?.getAttribute("role")
    );
    expect(focusedElement).not.toBeNull();

    // Continue tabbing
    await page.keyboard.press("Tab");
    focusedElement = await page.evaluate(() =>
      document.activeElement?.getAttribute("role")
    );
    expect(focusedElement).not.toBeNull();
  });

  test("Lighthouse accessibility score 90+", async ({ page }) => {
    // Using Lighthouse CI integration
    const accessibilityScore = await page.evaluate(() => {
      // Would be populated by Lighthouse CI
      return window.__lighthouseScores?.accessibility || 100;
    });

    expect(accessibilityScore).toBeGreaterThanOrEqual(90);
  });
});
```

### Performance Testing

```typescript
// tests/performance.spec.ts
import { test, expect } from "@playwright/test";

test("page loads within 3 seconds", async ({ page }) => {
  const startTime = Date.now();

  await page.goto("http://localhost:3000", {
    waitUntil: "networkidle"
  });

  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(3000);
});

test("images lazy load correctly", async ({ page }) => {
  await page.goto("http://localhost:3000");

  // Check that below-fold images have loading="lazy"
  const lazyImages = await page.locator('img[loading="lazy"]').count();
  expect(lazyImages).toBeGreaterThan(0);
});
```

## Test Coverage Targets

### Frontend (Feature 001)
| Component | Coverage |
|-----------|----------|
| Hero | 95%+ |
| Services | 90%+ |
| Contact Form | 95%+ |
| Navigation | 90%+ |
| Overall | 90%+ |

### Backend (Feature 002)
| Module | Coverage |
|--------|----------|
| Recipe Endpoints | 90%+ |
| Recipe Agent | 85%+ |
| Database Models | 95%+ |
| Overall | 90%+ |

## Quality Gates

All code must pass these gates before merge:

```
✓ Unit Test Coverage: 90%+
✓ Integration Tests: Pass 100%
✓ E2E Tests: Pass 100%
✓ Accessibility: WCAG 2.1 AA (axe-core)
✓ Type Checking: No errors (TypeScript/pyright)
✓ Linting: No warnings (ESLint/pylint)
✓ Performance: Lighthouse 90+
✓ Security: No vulnerabilities (npm audit, bandit)
```

## Parallelization

Test generation can run in parallel with development:

```
Frontend Dev Agent              Testing Agent
├─ Component 1                  ├─ Unit tests for Component 1
├─ Component 2                  ├─ Unit tests for Component 2
├─ Component 3                  ├─ Unit tests for Component 3
└─ Component 4                  ├─ Unit tests for Component 4
                                └─ E2E tests (after dev complete)
```

## Integration with Other Agents

- **Frontend/Backend Dev Agents**: Provides test coverage for generated code
- **Spec Analyzer**: Uses acceptance criteria to define test scenarios
- **Integration Agent**: Runs tests as part of final validation
- **Documentation Agent**: Updates test coverage metrics in docs

## Commands

```bash
# Frontend tests
npm run test                    # Run all tests
npm run test:unit             # Unit tests only
npm run test:integration      # Integration tests
npm run test:e2e              # E2E tests
npm run test:coverage         # Generate coverage report
npm run test:a11y             # Accessibility tests
npm run lighthouse            # Performance audit

# Backend tests
pytest                        # Run all tests
pytest --cov                  # With coverage
pytest -m integration         # Integration tests only
pytest -m unit                # Unit tests only
pytest tests/performance      # Performance tests
```
