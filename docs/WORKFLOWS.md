# GitHub Actions Workflows Documentation

This document describes the CI/CD workflows configured for the AI Meal Planner project.

## Overview

We have four main CI workflows that ensure code quality and prevent regressions:

1. **Backend Unit Tests** - Runs Python unit tests with coverage
2. **Frontend Unit Tests** - Runs Jest tests with coverage
3. **Frontend Linting** - Validates TypeScript and ESLint compliance
4. **Playwright E2E Tests** - Runs end-to-end browser tests

All workflows are required status checks for pull requests to `claude/main`.

## Workflows

### 1. Backend Unit Tests (`backend-unit-tests.yml`)

**Purpose:** Validates backend Python code with unit tests and coverage requirements.

**Triggers:**
- Push to `claude/main` (when backend files change)
- Pull requests to `claude/main` (when backend files change)
- Manual dispatch via GitHub UI

**Configuration:**
- Python versions: 3.11, 3.12
- Timeout: 10 minutes
- Coverage threshold: 80%
- Test command: `pytest backend/tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80`

**Artifacts:**
- `backend-coverage-report`: Coverage XML file
- `backend-test-results-py{version}`: pytest cache and results

**Required Secrets:**
- `CODECOV_TOKEN`: For uploading coverage reports to Codecov (only Python 3.11)

**Local Testing:**
```bash
cd backend
pip install -r requirements.txt
pytest tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80
```

### 2. Frontend Unit Tests (`frontend-unit-tests.yml`)

**Purpose:** Validates frontend React/Next.js code with Jest tests and coverage requirements.

**Triggers:**
- Push to `claude/main` (when frontend files change)
- Pull requests to `claude/main` (when frontend files change)
- Manual dispatch via GitHub UI

**Configuration:**
- Node.js versions: 20.x, 22.x (LTS)
- Timeout: 15 minutes
- Coverage threshold: 75%
- Test command: `npm test -- --coverage`

**Artifacts:**
- `frontend-coverage-report`: Coverage reports (lcov, JSON)
- `frontend-test-results-node{version}`: Test results and coverage

**Required Secrets:**
- `CODECOV_TOKEN`: For uploading coverage reports to Codecov (only Node 20.x)

**Local Testing:**
```bash
cd frontend
npm install
npm test -- --coverage
```

### 3. Frontend Linting (`frontend-lint.yml`)

**Purpose:** Enforces code style, linting rules, and TypeScript type safety.

**Triggers:**
- Push to `claude/main` (when frontend files change)
- Pull requests to `claude/main` (when frontend files change)
- Manual dispatch via GitHub UI

**Configuration:**
- Node.js version: LTS
- Timeout: 10 minutes
- Checks: ESLint + TypeScript type checking
- Fail on any errors (no warnings allowed)

**Features:**
- Automatically comments on PRs when linting fails
- Generates JSON lint report for debugging
- Shows summary in GitHub Actions UI

**Artifacts:**
- `frontend-lint-report`: ESLint JSON report

**Required Secrets:** None

**Local Testing:**
```bash
cd frontend
npm install
npm run lint
npx tsc --noEmit
```

### 4. Playwright E2E Tests (`playwright.yml`)

**Purpose:** Validates full application behavior through browser automation.

**Triggers:**
- Push to `main`, `master`, or `claude/main`
- Pull requests to `main`, `master`, or `claude/main`

**Configuration:**
- Node.js version: LTS
- Timeout: 60 minutes
- Test command: `npx playwright test`

**Artifacts:**
- `playwright-report`: HTML test report and trace files

**Required Secrets:** None (uses local test data)

**Local Testing:**
```bash
cd frontend
npm install
npx playwright install --with-deps
npx playwright test
```

## Required Secrets

To set up secrets in your GitHub repository:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Add the following secrets:

### Production Secrets

| Secret Name | Purpose | Where to Get | Used By |
|------------|---------|--------------|---------|
| `CODECOV_TOKEN` | Upload coverage reports | [codecov.io](https://codecov.io) after connecting repo | Backend & Frontend Unit Tests |
| `SENTRY_DSN` | Error tracking in production | [sentry.io](https://sentry.io) project settings | (Future: Deployment workflows) |
| `DATABASE_URL_TEST` | Test database connection | Set up test PostgreSQL instance | (Future: Integration tests) |
| `REDIS_URL_TEST` | Test Redis connection | Set up test Redis instance | (Future: Integration tests) |

### Setting Up Codecov

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token
5. Add as `CODECOV_TOKEN` secret in GitHub

**Note:** Codecov is optional. Workflows will still run without it, but coverage reports won't be uploaded.

## Running Workflows Manually

### Via GitHub UI

1. Go to **Actions** tab in your repository
2. Select the workflow you want to run
3. Click **Run workflow** button
4. Select branch and click **Run workflow**

### Via GitHub CLI

```bash
# Install GitHub CLI
# https://cli.github.com/

# Run backend unit tests
gh workflow run backend-unit-tests.yml

# Run frontend unit tests
gh workflow run frontend-unit-tests.yml

# Run frontend linting
gh workflow run frontend-lint.yml

# Run Playwright tests
gh workflow run playwright.yml
```

## Status Checks for Pull Requests

All workflows are configured as **required status checks** for merging PRs to `claude/main`.

To configure required status checks:

1. Go to **Settings** > **Branches**
2. Add branch protection rule for `claude/main`
3. Enable **Require status checks to pass before merging**
4. Select these status checks:
   - `test (3.11)` - Backend Unit Tests (Python 3.11)
   - `test (3.12)` - Backend Unit Tests (Python 3.12)
   - `test (20.x)` - Frontend Unit Tests (Node 20.x)
   - `test (22.x)` - Frontend Unit Tests (Node 22.x)
   - `lint` - Frontend Linting
   - `test` - Playwright E2E Tests

## Troubleshooting

### Coverage Threshold Failures

**Backend (80% threshold):**
```bash
# Check current coverage
cd backend
pytest tests/unit/ --cov=app --cov-report=term-missing

# Add tests for uncovered code
# Look for lines marked with "!" in the coverage report
```

**Frontend (75% threshold):**
```bash
# Check current coverage
cd frontend
npm test -- --coverage

# Add tests for uncovered components
# Check coverage/lcov-report/index.html for details
```

### Linting Failures

**ESLint errors:**
```bash
cd frontend
npm run lint

# Auto-fix where possible
npm run lint -- --fix
```

**TypeScript errors:**
```bash
cd frontend
npx tsc --noEmit

# Fix type errors in reported files
```

### Workflow Not Triggering

**Check path filters:**
- Backend workflows only run when `backend/**` files change
- Frontend workflows only run when `frontend/**` files change
- Ensure your changes match the path patterns

**Force trigger:**
- Use workflow_dispatch (Run workflow button in Actions tab)
- Push to `claude/main` branch directly

### Dependency Cache Issues

**Clear npm cache:**
```yaml
# In workflow file, change cache key:
cache-dependency-path: frontend/package-lock.json
# to
cache-dependency-path: frontend/package-lock.json-v2
```

**Clear pip cache:**
```yaml
# In workflow file, change cache key:
cache-dependency-path: backend/requirements.txt
# to
cache-dependency-path: backend/requirements.txt-v2
```

### Timeout Issues

If workflows timeout, you can adjust timeouts in the YAML files:

```yaml
jobs:
  test:
    timeout-minutes: 15  # Increase this value
```

### Artifact Upload Failures

**Check artifact sizes:**
- Maximum artifact size: 10GB per workflow run
- Individual artifacts should be < 100MB

**Check retention:**
- Default retention: 7 days
- Adjust `retention-days` in workflow YAML if needed

## Performance Optimization

### Dependency Caching

All workflows use caching to speed up dependency installation:

**Python (pip):**
```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'
    cache-dependency-path: backend/requirements.txt
```

**Node.js (npm):**
```yaml
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```

### Matrix Strategies

Workflows use matrix builds to run tests in parallel:

**Backend:** Python 3.11 and 3.12 run simultaneously
**Frontend:** Node 20.x and 22.x run simultaneously

### Path Filtering

Workflows only trigger when relevant files change:
- `paths: ['backend/**']` - Backend workflows
- `paths: ['frontend/**']` - Frontend workflows

This prevents unnecessary workflow runs and saves CI minutes.

## Best Practices

1. **Run tests locally** before pushing to catch issues early
2. **Keep coverage high** - aim for 80%+ backend, 75%+ frontend
3. **Fix lint errors immediately** - don't let them accumulate
4. **Check workflow status** before requesting PR reviews
5. **Use descriptive commit messages** to trigger appropriate workflows
6. **Monitor CI costs** - optimize workflows if minutes are high
7. **Update dependencies regularly** to avoid security issues

## CI Minutes Usage

GitHub provides free CI minutes for public repositories. For private repos:

- **Free tier:** 2,000 minutes/month
- **Pro tier:** 3,000 minutes/month
- **Team tier:** 10,000 minutes/month

Estimated usage per workflow run:
- Backend Unit Tests: ~2-3 minutes
- Frontend Unit Tests: ~3-5 minutes
- Frontend Linting: ~1-2 minutes
- Playwright E2E Tests: ~5-10 minutes

**Total per PR:** ~20-30 minutes (all checks combined)

## Future Enhancements

Planned workflow additions:

1. **Backend Linting** - Black, isort, mypy, flake8
2. **Backend Integration Tests** - Tests requiring database/Redis
3. **E2E Test Matrix** - Multiple browsers (Chrome, Firefox, Safari)
4. **Deployment Workflows** - Auto-deploy to staging/production
5. **Security Scanning** - Snyk, Dependabot, CodeQL
6. **Performance Testing** - Lighthouse CI for frontend
7. **Docker Build & Push** - Build and push images to registry

## Support

For issues with workflows:

1. Check workflow logs in Actions tab
2. Review this documentation
3. Consult the troubleshooting section
4. Open an issue with workflow run URL

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.io)
- [Jest CLI Options](https://jestjs.io/docs/cli)
- [Pytest Documentation](https://docs.pytest.org)
- [ESLint CLI](https://eslint.org/docs/user-guide/command-line-interface)
- [TypeScript Compiler Options](https://www.typescriptlang.org/docs/handbook/compiler-options.html)
