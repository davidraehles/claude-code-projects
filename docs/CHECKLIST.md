# CI/CD Setup Checklist

Use this checklist to verify the CI/CD infrastructure is properly configured and operational.

## Initial Setup Checklist

### Files Created
- [x] `.github/workflows/backend-unit-tests.yml` - Backend unit test pipeline
- [x] `.github/workflows/frontend-unit-tests.yml` - Frontend unit test pipeline
- [x] `.github/workflows/frontend-lint.yml` - Frontend linting pipeline
- [x] `.codecov.yml` - Codecov configuration
- [x] `.github/WORKFLOWS.md` - Comprehensive documentation
- [x] `.github/SECRETS_SETUP.md` - Secrets setup guide
- [x] `.github/WORKFLOWS_QUICK_REFERENCE.md` - Quick reference
- [x] `.github/CI_CD_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- [x] `.github/README.md` - Directory overview
- [x] `.github/validate-workflows.sh` - Validation script

### Workflow Validation
- [x] All YAML files have valid syntax
- [x] All workflows have `name` field
- [x] All workflows have `on` triggers
- [x] All workflows have `jobs` section
- [x] All workflows have timeouts configured
- [x] All workflows use dependency caching
- [x] No hardcoded credentials in workflows
- [x] Path filters configured correctly

### Documentation Validation
- [x] All documentation files created
- [x] Step-by-step instructions provided
- [x] Troubleshooting sections included
- [x] Examples and code snippets provided
- [x] Links between documents work correctly

## GitHub Repository Configuration

### Secrets (Required Actions)

#### Codecov Token
- [ ] Sign up/login at [codecov.io](https://codecov.io)
- [ ] Connect your GitHub repository
- [ ] Copy the upload token
- [ ] Go to GitHub repo → Settings → Secrets → Actions
- [ ] Create new secret: `CODECOV_TOKEN`
- [ ] Paste the token value
- [ ] Test by running a workflow

#### Future Secrets (Document for Reference)
- [ ] `SENTRY_DSN` - Documented in SECRETS_SETUP.md
- [ ] `DATABASE_URL_TEST` - Documented in SECRETS_SETUP.md
- [ ] `REDIS_URL_TEST` - Documented in SECRETS_SETUP.md

### Branch Protection Rules

- [ ] Go to Settings → Branches → Add rule
- [ ] Branch name pattern: `claude/main`
- [ ] Enable: "Require status checks to pass before merging"
- [ ] Enable: "Require branches to be up to date before merging"
- [ ] Select required status checks:
  - [ ] `test (3.11)` - Backend Unit Tests (Python 3.11)
  - [ ] `test (3.12)` - Backend Unit Tests (Python 3.12)
  - [ ] `test (20.x)` - Frontend Unit Tests (Node 20.x)
  - [ ] `test (22.x)` - Frontend Unit Tests (Node 22.x)
  - [ ] `lint` - Frontend Linting
  - [ ] `test` - Playwright E2E Tests (if required)
- [ ] Enable: "Do not allow bypassing the above settings"
- [ ] Click "Create" or "Save changes"

### GitHub Actions Permissions

- [ ] Go to Settings → Actions → General
- [ ] Workflow permissions → "Read and write permissions"
- [ ] Enable "Allow GitHub Actions to create and approve pull requests"
- [ ] Click "Save"

## Testing & Verification

### Local Testing

#### Backend Unit Tests
- [ ] `cd backend`
- [ ] `pip install -r requirements.txt`
- [ ] `pytest tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80`
- [ ] Verify: Tests pass
- [ ] Verify: Coverage ≥ 80%
- [ ] Verify: `coverage.xml` generated

#### Frontend Unit Tests
- [ ] `cd frontend`
- [ ] `npm ci`
- [ ] `npm test -- --coverage`
- [ ] Verify: Tests pass
- [ ] Verify: Coverage ≥ 75%
- [ ] Verify: `coverage/` directory created

#### Frontend Linting
- [ ] `cd frontend`
- [ ] `npm ci`
- [ ] `npm run lint`
- [ ] `npx tsc --noEmit`
- [ ] Verify: No lint errors
- [ ] Verify: No TypeScript errors

### Workflow Testing

#### Test Backend Workflow
- [ ] Create test branch: `git checkout -b test/backend-ci`
- [ ] Make trivial change to `backend/app/main.py`
- [ ] Commit and push
- [ ] Go to Actions tab
- [ ] Verify: "Backend Unit Tests" workflow triggered
- [ ] Verify: Both Python 3.11 and 3.12 jobs run
- [ ] Verify: All steps complete successfully
- [ ] Verify: Coverage uploaded to Codecov (if token configured)
- [ ] Verify: Artifacts uploaded
- [ ] Clean up: `git checkout - && git branch -D test/backend-ci`

#### Test Frontend Unit Test Workflow
- [ ] Create test branch: `git checkout -b test/frontend-ci`
- [ ] Make trivial change to `frontend/package.json`
- [ ] Commit and push
- [ ] Go to Actions tab
- [ ] Verify: "Frontend Unit Tests" workflow triggered
- [ ] Verify: Both Node 20.x and 22.x jobs run
- [ ] Verify: All steps complete successfully
- [ ] Verify: Coverage threshold check passes
- [ ] Verify: Coverage uploaded to Codecov (if token configured)
- [ ] Verify: Artifacts uploaded
- [ ] Clean up: `git checkout - && git branch -D test/frontend-ci`

#### Test Frontend Linting Workflow
- [ ] Create test branch: `git checkout -b test/lint-ci`
- [ ] Make trivial change to `frontend/src/app/page.tsx`
- [ ] Commit and push
- [ ] Go to Actions tab
- [ ] Verify: "Frontend Linting" workflow triggered
- [ ] Verify: ESLint step runs
- [ ] Verify: TypeScript check runs
- [ ] Verify: Both steps pass
- [ ] Clean up: `git checkout - && git branch -D test/lint-ci`

#### Test Manual Workflow Dispatch
- [ ] Go to Actions tab
- [ ] Select "Backend Unit Tests"
- [ ] Click "Run workflow"
- [ ] Select branch: `claude/main`
- [ ] Click "Run workflow"
- [ ] Verify: Workflow starts and completes
- [ ] Repeat for "Frontend Unit Tests" and "Frontend Linting"

### Pull Request Testing

#### Create Test PR
- [ ] Create test branch: `git checkout -b test/pr-checks`
- [ ] Make changes to both backend and frontend
- [ ] Commit and push
- [ ] Create pull request to `claude/main`
- [ ] Verify: All required checks appear in PR
- [ ] Verify: PR cannot be merged until checks pass
- [ ] Verify: Status checks show as "Required"
- [ ] Wait for checks to complete
- [ ] Verify: All checks pass
- [ ] Verify: "Merge" button becomes available
- [ ] Close PR without merging (test only)

### Codecov Integration

- [ ] Go to [codecov.io](https://codecov.io)
- [ ] Navigate to your repository
- [ ] Verify: Coverage data appears after workflow runs
- [ ] Verify: Graphs show coverage trends
- [ ] Verify: PR comments appear with coverage diff
- [ ] Verify: Branch coverage is tracked

## Monitoring & Maintenance

### Weekly Checks
- [ ] Review workflow runs for failures
- [ ] Check for warnings in workflow logs
- [ ] Verify coverage trends are stable/improving
- [ ] Monitor CI minutes usage

### Monthly Checks
- [ ] Update actions to latest versions:
  - [ ] `actions/checkout@v4` → check for v5
  - [ ] `actions/setup-python@v5` → check for updates
  - [ ] `actions/setup-node@v4` → check for v5
  - [ ] `codecov/codecov-action@v4` → check for updates
- [ ] Review and update Python/Node versions in matrix
- [ ] Check for security advisories on dependencies
- [ ] Review CI minutes usage and optimize if needed

### Quarterly Checks
- [ ] Review and adjust coverage thresholds
- [ ] Update documentation with any changes
- [ ] Review and update timeout values
- [ ] Evaluate new GitHub Actions features
- [ ] Review artifact retention policies

## Troubleshooting Verification

### Test Common Scenarios

#### Coverage Below Threshold
- [ ] Temporarily lower threshold in workflow
- [ ] Verify: Workflow fails with clear error message
- [ ] Restore original threshold

#### Linting Failure
- [ ] Introduce lint error in frontend code
- [ ] Verify: Linting workflow fails
- [ ] Verify: PR comment appears (if PR)
- [ ] Verify: Lint report artifact uploaded
- [ ] Fix lint error

#### TypeScript Error
- [ ] Introduce TypeScript error
- [ ] Verify: Linting workflow fails at type check step
- [ ] Verify: Clear error message shown
- [ ] Fix error

#### Codecov Upload Failure
- [ ] Temporarily remove `CODECOV_TOKEN` secret
- [ ] Run workflow
- [ ] Verify: Workflow fails at Codecov upload step
- [ ] Verify: Error message is clear
- [ ] Restore secret

## Performance Verification

### Check Caching Works
- [ ] Run workflow for first time (cold cache)
- [ ] Note execution time
- [ ] Run workflow again immediately (warm cache)
- [ ] Verify: Second run is significantly faster
- [ ] Verify: Logs show "Cache restored" messages

### Check Matrix Parallelization
- [ ] Trigger backend workflow
- [ ] Go to Actions tab
- [ ] Expand workflow run
- [ ] Verify: Python 3.11 and 3.12 jobs run simultaneously
- [ ] Trigger frontend workflow
- [ ] Verify: Node 20.x and 22.x jobs run simultaneously

### Check Path Filtering
- [ ] Make change to `docs/` only
- [ ] Push change
- [ ] Verify: No CI workflows triggered
- [ ] Make change to `backend/`
- [ ] Verify: Only backend workflow triggered
- [ ] Make change to `frontend/`
- [ ] Verify: Only frontend workflows triggered

## Documentation Verification

### Test Links
- [ ] Open `.github/README.md`
- [ ] Click all links to other documents
- [ ] Verify: All links work correctly
- [ ] Verify: No broken internal references

### Test Commands
- [ ] Follow local testing commands in WORKFLOWS.md
- [ ] Follow gh CLI commands in WORKFLOWS_QUICK_REFERENCE.md
- [ ] Verify: All commands work as documented

### Test Troubleshooting
- [ ] Simulate an error from troubleshooting guide
- [ ] Follow documented solution
- [ ] Verify: Solution works as described

## Sign-Off

### Final Verification
- [ ] All workflows validated
- [ ] All secrets configured
- [ ] All branch protections set
- [ ] All tests passing
- [ ] All documentation complete
- [ ] All team members informed
- [ ] All monitoring in place

### Completion
- [ ] Implementation date: ___________
- [ ] Verified by: ___________
- [ ] Production ready: [ ] Yes [ ] No
- [ ] Issues found: [ ] None [ ] See notes below

### Notes
```
[Add any notes, issues, or observations here]
```

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0

This checklist should be reviewed and updated as the CI/CD infrastructure evolves.
