# GitHub Actions Workflows - Quick Reference

## Workflow Status Badges

Add these badges to your README.md to show workflow status:

```markdown
![Backend Unit Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-unit-tests.yml/badge.svg)
![Frontend Unit Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-unit-tests.yml/badge.svg)
![Frontend Linting](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-lint.yml/badge.svg)
![Playwright Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/playwright.yml/badge.svg)
```

## Quick Commands

### Run Workflows Manually

```bash
# Backend unit tests
gh workflow run backend-unit-tests.yml --ref your-branch

# Frontend unit tests
gh workflow run frontend-unit-tests.yml --ref your-branch

# Frontend linting
gh workflow run frontend-lint.yml --ref your-branch

# Playwright E2E tests
gh workflow run playwright.yml --ref your-branch
```

### View Workflow Status

```bash
# List all workflows
gh workflow list

# View specific workflow runs
gh run list --workflow=backend-unit-tests.yml

# View logs from latest run
gh run view --log
```

### Local Testing Commands

#### Backend Unit Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80
```

#### Frontend Unit Tests
```bash
cd frontend
npm ci
npm test -- --coverage
```

#### Frontend Linting
```bash
cd frontend
npm ci
npm run lint
npx tsc --noEmit
```

#### Playwright E2E Tests
```bash
cd frontend
npm ci
npx playwright install --with-deps
npx playwright test
```

## Workflow Triggers

| Workflow | Push to `claude/main` | Pull Request | Manual | Path Filter |
|----------|----------------------|--------------|--------|-------------|
| Backend Unit Tests | ✅ | ✅ | ✅ | `backend/**` |
| Frontend Unit Tests | ✅ | ✅ | ✅ | `frontend/**` |
| Frontend Linting | ✅ | ✅ | ✅ | `frontend/**` |
| Playwright E2E | ✅ | ✅ | ❌ | all files |

## Coverage Requirements

| Workflow | Threshold | Enforced By |
|----------|-----------|-------------|
| Backend Unit Tests | 80% | pytest --cov-fail-under=80 |
| Frontend Unit Tests | 75% | Custom check in workflow |

## Workflow Matrix

### Backend Unit Tests
- Python: 3.11, 3.12
- OS: ubuntu-latest
- Total jobs: 2

### Frontend Unit Tests
- Node.js: 20.x, 22.x
- OS: ubuntu-latest
- Total jobs: 2

### Frontend Linting
- Node.js: LTS
- OS: ubuntu-latest
- Total jobs: 1

## Artifacts

| Workflow | Artifact Name | Contains | Retention |
|----------|---------------|----------|-----------|
| Backend Unit Tests | `backend-coverage-report` | coverage.xml | 7 days |
| Backend Unit Tests | `backend-test-results-py{version}` | pytest cache | 7 days |
| Frontend Unit Tests | `frontend-coverage-report` | coverage/ directory | 7 days |
| Frontend Unit Tests | `frontend-test-results-node{version}` | coverage + junit.xml | 7 days |
| Frontend Linting | `frontend-lint-report` | eslint-report.json | 7 days |
| Playwright Tests | `playwright-report` | HTML report | 30 days |

## Required Secrets

| Secret | Required | Used By |
|--------|----------|---------|
| `CODECOV_TOKEN` | Optional | Backend & Frontend Unit Tests |
| `SENTRY_DSN` | Future | Deployment workflows |
| `DATABASE_URL_TEST` | Future | Integration tests |
| `REDIS_URL_TEST` | Future | Integration tests |

## Troubleshooting Checklist

### Workflow Not Triggering

- [ ] Changes match path filter (`backend/**` or `frontend/**`)
- [ ] Pushing to correct branch (`claude/main`)
- [ ] Workflow file is in `.github/workflows/`
- [ ] YAML syntax is valid

### Test Failures

- [ ] Run tests locally first
- [ ] Check test logs in Actions tab
- [ ] Verify all dependencies are installed
- [ ] Check for environment-specific issues

### Coverage Below Threshold

- [ ] Run coverage locally: `pytest --cov=app --cov-report=term-missing`
- [ ] Add tests for uncovered code
- [ ] Check coverage report in artifacts
- [ ] Verify coverage threshold is reasonable

### Linting Failures

- [ ] Run `npm run lint` locally
- [ ] Run `npx tsc --noEmit` locally
- [ ] Fix errors before pushing
- [ ] Use `npm run lint -- --fix` for auto-fixes

## Performance Tips

1. **Use caching** - All workflows cache dependencies
2. **Path filters** - Only run when relevant files change
3. **Matrix strategy** - Parallel execution for multiple versions
4. **Artifacts** - Upload only necessary files
5. **Timeouts** - Set appropriate timeouts to avoid hanging

## Common Issues & Solutions

### Issue: "Coverage upload failed"
**Solution:** Verify `CODECOV_TOKEN` is set in repository secrets

### Issue: "Module not found"
**Solution:** Ensure `npm ci` or `pip install -r requirements.txt` completed successfully

### Issue: "Timeout after 10 minutes"
**Solution:** Increase timeout in workflow YAML or optimize tests

### Issue: "ESLint: No files matching the pattern"
**Solution:** Check working directory is set correctly in workflow

### Issue: "Python version not found"
**Solution:** Ensure Python version in matrix matches available versions

## Workflow Modification

To modify a workflow:

1. Edit `.github/workflows/{workflow-name}.yml`
2. Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/{workflow-name}.yml'))"`
3. Commit and push changes
4. Monitor first workflow run for issues

## Status Check Configuration

To make workflows required for PR merge:

1. Go to **Settings** > **Branches**
2. Add/Edit branch protection rule for `claude/main`
3. Enable **Require status checks to pass before merging**
4. Select:
   - `test (3.11)` - Backend Unit Tests
   - `test (3.12)` - Backend Unit Tests
   - `test (20.x)` - Frontend Unit Tests
   - `test (22.x)` - Frontend Unit Tests
   - `lint` - Frontend Linting
   - `test` - Playwright E2E

## Useful Links

- [Workflows Documentation](./WORKFLOWS.md) - Comprehensive documentation
- [Secrets Setup Guide](./SECRETS_SETUP.md) - Step-by-step secret configuration
- [GitHub Actions Logs](https://github.com/YOUR_USERNAME/YOUR_REPO/actions) - View workflow runs
- [Codecov Dashboard](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO) - Coverage reports

## Emergency Procedures

### Disable a Failing Workflow

1. Comment out the entire workflow file
2. Or rename file extension from `.yml` to `.yml.disabled`
3. Commit and push
4. Fix issues, then re-enable

### Skip CI for a Commit

```bash
git commit -m "docs: update README [skip ci]"
```

### Force Re-run Failed Workflow

1. Go to Actions tab
2. Click on failed workflow run
3. Click **Re-run failed jobs** or **Re-run all jobs**

## Maintenance Schedule

- [ ] **Weekly**: Review workflow logs for warnings
- [ ] **Monthly**: Update dependencies in workflows
- [ ] **Quarterly**: Review and update coverage thresholds
- [ ] **Annually**: Review and update Node.js/Python versions

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0
