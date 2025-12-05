# CI/CD Badge and Documentation Snippet

Add this section to your main project README.md to showcase the CI/CD setup.

---

## CI/CD Status

![Backend Unit Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-unit-tests.yml/badge.svg)
![Frontend Unit Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-unit-tests.yml/badge.svg)
![Frontend Linting](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-lint.yml/badge.svg)
![Playwright E2E](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/playwright.yml/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/claude/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)

## Development Workflow

### Running Tests Locally

Before pushing your code, run tests locally to catch issues early:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
pytest tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80
```

**Frontend:**
```bash
cd frontend
npm ci
npm test -- --coverage
npm run lint
npx tsc --noEmit
```

### Continuous Integration

All pull requests to `claude/main` require the following checks to pass:

- Backend Unit Tests (Python 3.11, 3.12) - 80% coverage required
- Frontend Unit Tests (Node.js 20.x, 22.x) - 75% coverage required
- Frontend Linting (ESLint + TypeScript)
- Playwright E2E Tests

See [.github/WORKFLOWS.md](.github/WORKFLOWS.md) for detailed CI/CD documentation.

### Code Quality Standards

- **Coverage Thresholds**: 80% backend, 75% frontend
- **Linting**: Zero errors, zero warnings
- **Type Safety**: Strict TypeScript mode
- **Testing**: Unit tests required for all features

For complete CI/CD documentation, see:
- [Workflows Documentation](.github/WORKFLOWS.md) - Comprehensive guide
- [Quick Reference](.github/WORKFLOWS_QUICK_REFERENCE.md) - Common commands
- [Secrets Setup](.github/SECRETS_SETUP.md) - Configuration guide

---

## Alternative Minimal Version (for shorter README)

## CI/CD

![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-unit-tests.yml/badge.svg)
![Lint](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-lint.yml/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/claude/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)

All PRs require passing tests (80% backend coverage, 75% frontend coverage) and linting checks.

See [.github/WORKFLOWS.md](.github/WORKFLOWS.md) for CI/CD documentation.

---

## Instructions

1. Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub username and repository name
2. Choose either the full version or minimal version based on your README structure
3. Copy the chosen snippet to your main README.md
4. Place it near the top (after project title/description) or in a "Development" section
