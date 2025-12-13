# GitHub Actions & CI/CD Configuration

This directory contains all GitHub Actions workflows, configurations, and documentation for the AI Meal Planner project's CI/CD infrastructure.

## Quick Start

### New to the Project?

1. **Read the Quick Reference** - [WORKFLOWS_QUICK_REFERENCE.md](WORKFLOWS_QUICK_REFERENCE.md)
2. **Set up secrets** - Follow [SECRETS_SETUP.md](SECRETS_SETUP.md)
3. **Configure branch protection** - See [WORKFLOWS.md](WORKFLOWS.md#status-checks-for-pull-requests)

### Making Changes?

1. **Run tests locally** before pushing:
   ```bash
   # Backend
   cd backend && pytest tests/unit/ -v --cov=app

   # Frontend
   cd frontend && npm test -- --coverage && npm run lint && npx tsc --noEmit
   ```

2. **Push to your branch** - Workflows auto-trigger
3. **Check Actions tab** - Monitor workflow status
4. **Fix any failures** - Review logs and artifacts

## Documentation

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [WORKFLOWS_QUICK_REFERENCE.md](WORKFLOWS_QUICK_REFERENCE.md) | Quick commands and troubleshooting | Daily use, quick lookups |
| [WORKFLOWS.md](WORKFLOWS.md) | Comprehensive workflow documentation | Setup, deep dive, troubleshooting |
| [SECRETS_SETUP.md](SECRETS_SETUP.md) | Step-by-step secrets configuration | Initial setup, adding new secrets |
| [CI_CD_IMPLEMENTATION_SUMMARY.md](CI_CD_IMPLEMENTATION_SUMMARY.md) | Implementation details and decisions | Understanding the system, onboarding |
| [README.md](README.md) | This file - directory overview | First time here |

## Workflows

### Active Workflows

| Workflow | File | Status Check | Coverage | Docs |
|----------|------|--------------|----------|------|
| Backend Unit Tests | [backend-unit-tests.yml](workflows/backend-unit-tests.yml) | `test (3.11)`, `test (3.12)` | 80% | [📖](WORKFLOWS.md#1-backend-unit-tests) |
| Frontend Unit Tests | [frontend-unit-tests.yml](workflows/frontend-unit-tests.yml) | `test (20.x)`, `test (22.x)` | 75% | [📖](WORKFLOWS.md#2-frontend-unit-tests) |
| Frontend Linting | [frontend-lint.yml](workflows/frontend-lint.yml) | `lint` | N/A | [📖](WORKFLOWS.md#3-frontend-linting) |
| Playwright E2E Tests | [playwright.yml](workflows/playwright.yml) | `test` | N/A | [📖](WORKFLOWS.md#4-playwright-e2e-tests) |

All workflows are **required status checks** for merging to `claude/main`.

### Workflow Triggers

```
Push to claude/main → All workflows run (with path filters)
Pull Request → All workflows run (with path filters)
Manual Dispatch → Click "Run workflow" in Actions tab
```

## Files & Tools

### Configuration Files

- `.codecov.yml` - Codecov coverage reporting configuration (root directory)
- Path filters in each workflow (e.g., `paths: ['backend/**']`)

### Tools

- `validate-workflows.sh` - Validate workflow YAML syntax and best practices
  ```bash
  cd .github && ./validate-workflows.sh
  ```

## Required Secrets

### Currently Used

| Secret | Purpose | Setup Guide |
|--------|---------|-------------|
| `CODECOV_TOKEN` | Upload coverage reports | [SECRETS_SETUP.md](SECRETS_SETUP.md#codecov_token-recommended) |

### Future Use (Documented)

- `SENTRY_DSN` - Error tracking
- `DATABASE_URL_TEST` - Integration tests
- `REDIS_URL_TEST` - Integration tests

See [SECRETS_SETUP.md](SECRETS_SETUP.md) for complete setup instructions.

## Common Tasks

### View Workflow Status

```bash
# List all workflows
gh workflow list

# View recent runs
gh run list

# View specific workflow
gh run list --workflow=backend-unit-tests.yml
```

### Run Workflow Manually

```bash
# Via GitHub CLI
gh workflow run backend-unit-tests.yml --ref your-branch
gh workflow run frontend-unit-tests.yml --ref your-branch
gh workflow run frontend-lint.yml --ref your-branch
```

Or use the **Actions** tab → Select workflow → **Run workflow** button

### Debug Failed Workflow

1. Go to **Actions** tab
2. Click on failed workflow run
3. Expand failed step
4. Download artifacts (if available)
5. Run tests locally to reproduce

See [WORKFLOWS.md](WORKFLOWS.md#troubleshooting) for detailed troubleshooting.

### Update Workflow

1. Edit `.github/workflows/{workflow-name}.yml`
2. Validate syntax:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.github/workflows/{workflow-name}.yml'))"
   ```
3. Commit and push
4. Monitor first run in Actions tab

## Best Practices

### ✅ DO

- Run tests locally before pushing
- Keep coverage above thresholds (80% backend, 75% frontend)
- Fix lint errors immediately
- Review workflow logs when failures occur
- Update dependencies regularly
- Monitor CI minutes usage

### ❌ DON'T

- Skip tests with `[skip ci]` (unless absolutely necessary)
- Ignore failing status checks
- Commit broken code hoping CI will catch it
- Leave failing tests for later
- Hardcode secrets in workflow files
- Disable required status checks

## Troubleshooting

### Quick Fixes

| Issue | Solution |
|-------|----------|
| Coverage below threshold | Add tests, check with `--cov-report=term-missing` |
| Linting failures | Run `npm run lint -- --fix` locally |
| Workflow not triggering | Check path filters match your changes |
| Codecov upload fails | Verify `CODECOV_TOKEN` is set |
| Timeout | Increase timeout in workflow YAML |

See [WORKFLOWS.md](WORKFLOWS.md#troubleshooting) for comprehensive troubleshooting guide.

## Performance

### Expected Execution Times

| Workflow | Duration (cached) |
|----------|-------------------|
| Backend Unit Tests | ~1.5 min per version |
| Frontend Unit Tests | ~2 min per version |
| Frontend Linting | ~1 min |
| Playwright E2E | ~8-10 min |

**Total per PR:** ~15-20 minutes (parallel execution)

### Optimization Tips

1. **Use caching** - Already enabled for pip and npm
2. **Path filters** - Already configured, workflows only run when relevant files change
3. **Matrix strategy** - Already parallelized for multiple Python/Node versions
4. **Skip CI when needed** - Use `[skip ci]` in commit message for docs-only changes

## CI Minutes Budget

GitHub provides free CI minutes for public repositories.

**Free tier:** 2,000 minutes/month
**Estimated usage:** ~28 minutes per PR
**Capacity:** ~70 PRs per month

Monitor usage at: **Settings** → **Billing** → **Actions**

## Maintenance

### Weekly
- [ ] Review workflow logs for warnings
- [ ] Check for workflow failures

### Monthly
- [ ] Update dependencies in workflows (actions/setup-node, etc.)
- [ ] Review CI minutes usage
- [ ] Check Codecov dashboard for coverage trends

### Quarterly
- [ ] Review and update coverage thresholds
- [ ] Update Node.js/Python versions in matrix
- [ ] Review and update documentation

## Future Enhancements

Planned additions:

- [ ] Backend linting workflow (Black, isort, mypy, flake8)
- [ ] Backend integration tests (with database/Redis)
- [ ] Security scanning (Snyk, CodeQL, Trivy)
- [ ] Deployment workflows (staging, production)
- [ ] Performance testing (Lighthouse CI, load tests)
- [ ] Multi-browser E2E tests (Firefox, Safari)

See [WORKFLOWS.md](WORKFLOWS.md#future-enhancements) for details.

## Getting Help

1. **Check documentation** - Start with [WORKFLOWS_QUICK_REFERENCE.md](WORKFLOWS_QUICK_REFERENCE.md)
2. **Review logs** - Actions tab → Failed workflow → Expand steps
3. **Search issues** - Check for similar problems
4. **Ask for help** - Open issue with workflow run URL

## Resources

### Official Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)

### Third-Party Services
- [Codecov Documentation](https://docs.codecov.io)
- [Jest Documentation](https://jestjs.io/docs/cli)
- [Pytest Documentation](https://docs.pytest.org)
- [ESLint CLI](https://eslint.org/docs/user-guide/command-line-interface)

### Project-Specific
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [Project CLAUDE.md](../CLAUDE.md)

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0
**Maintained By:** Development Team

For questions or issues, please open a GitHub issue or consult the documentation above.
