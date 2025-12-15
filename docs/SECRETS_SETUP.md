# GitHub Actions Secrets Setup Guide

This document provides step-by-step instructions for setting up all required secrets for CI/CD workflows.

## Quick Reference

| Secret Name | Required? | Used By | Purpose |
|------------|-----------|---------|---------|
| `CODECOV_TOKEN` | Optional* | Backend & Frontend Unit Tests | Upload coverage reports |
| `SENTRY_DSN` | Future | Deployment workflows | Error tracking in production |
| `DATABASE_URL_TEST` | Future | Integration tests | Test database connection |
| `REDIS_URL_TEST` | Future | Integration tests | Test Redis connection |

*Optional but recommended for coverage tracking

## Setting Up Secrets

### Step 1: Access Repository Settings

1. Navigate to your GitHub repository
2. Click **Settings** tab
3. In left sidebar, go to **Secrets and variables** > **Actions**
4. Click **New repository secret**

### Step 2: Add Required Secrets

#### CODECOV_TOKEN (Recommended)

**Purpose:** Uploads test coverage reports to Codecov for tracking coverage trends.

**How to obtain:**

1. Go to [codecov.io](https://codecov.io)
2. Sign in with your GitHub account
3. Click **Add new repository**
4. Select your repository from the list
5. Copy the **Upload Token** shown on the setup page
6. In GitHub repository settings:
   - Name: `CODECOV_TOKEN`
   - Secret: Paste the token from Codecov
   - Click **Add secret**

**Testing:**
```bash
# After adding the secret, trigger a workflow
git push origin your-branch

# Check the workflow logs for:
# "Upload coverage reports to Codecov" step should succeed
```

**Note:** Without this token, coverage reports won't be uploaded to Codecov, but tests will still run successfully.

#### SENTRY_DSN (Future Use)

**Purpose:** Error tracking and monitoring in production environment.

**How to obtain:**

1. Go to [sentry.io](https://sentry.io)
2. Create an account or sign in
3. Create a new project:
   - Platform: **Python** (for backend) or **Next.js** (for frontend)
   - Give it a name (e.g., "ai-meal-planner-backend")
4. After creation, go to **Settings** > **Client Keys (DSN)**
5. Copy the **DSN** value
6. In GitHub repository settings:
   - Name: `SENTRY_DSN`
   - Secret: Paste the DSN from Sentry
   - Click **Add secret**

**Current Status:** Not yet used in workflows. Will be needed when deployment workflows are added.

#### DATABASE_URL_TEST (Future Use)

**Purpose:** Connection string for test database used in integration tests.

**Format:**
```
postgresql://username:password@hostname:5432/database_name
```

**How to set up:**

1. Create a test PostgreSQL database:
   ```bash
   # Using Docker
   docker run -d \
     --name meal-planner-test-db \
     -e POSTGRES_USER=testuser \
     -e POSTGRES_PASSWORD=testpass \
     -e POSTGRES_DB=meal_planner_test \
     -p 5433:5432 \
     postgres:16
   ```

2. Construct the connection string:
   ```
   postgresql://testuser:testpass@localhost:5433/meal_planner_test
   ```

3. In GitHub repository settings:
   - Name: `DATABASE_URL_TEST`
   - Secret: Paste the connection string
   - Click **Add secret**

**Note:** For GitHub Actions, you'll need a cloud-hosted database or use PostgreSQL service containers.

**Alternative (GitHub Actions service):**
```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: meal_planner_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

#### REDIS_URL_TEST (Future Use)

**Purpose:** Connection string for test Redis instance used in integration tests.

**Format:**
```
redis://hostname:6379/0
```

**How to set up:**

1. Create a test Redis instance:
   ```bash
   # Using Docker
   docker run -d \
     --name meal-planner-test-redis \
     -p 6380:6379 \
     redis:7-alpine
   ```

2. Construct the connection string:
   ```
   redis://localhost:6380/0
   ```

3. In GitHub repository settings:
   - Name: `REDIS_URL_TEST`
   - Secret: Paste the connection string
   - Click **Add secret**

**Alternative (GitHub Actions service):**
```yaml
services:
  redis:
    image: redis:7-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Verifying Secrets

### Check Secret Configuration

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. You should see all configured secrets listed (values are hidden)
3. Check the "Last updated" timestamp

### Test Secrets in Workflows

1. Trigger a workflow that uses secrets:
   ```bash
   # Manual trigger via GitHub CLI
   gh workflow run backend-unit-tests.yml

   # Or push to trigger automatically
   git commit --allow-empty -m "test: trigger CI"
   git push origin your-branch
   ```

2. Check workflow logs:
   - Go to **Actions** tab
   - Click on the workflow run
   - Expand steps that use secrets
   - Look for success messages (secrets themselves won't be shown)

### Common Issues

**Issue:** "Error: Codecov: API request failed"
**Solution:** Check that `CODECOV_TOKEN` is correctly configured and valid

**Issue:** "Error: Resource not accessible by integration"
**Solution:** Check repository permissions for GitHub Actions

**Issue:** Secret not found in workflow
**Solution:** Ensure secret name in workflow YAML matches exactly (case-sensitive)

## Security Best Practices

### DO:
- ✅ Use repository secrets for sensitive data
- ✅ Rotate secrets regularly (every 90 days recommended)
- ✅ Use environment-specific secrets (test vs production)
- ✅ Limit secret access to required workflows only
- ✅ Review secret usage in audit logs periodically

### DON'T:
- ❌ Commit secrets to version control
- ❌ Echo/print secrets in workflow logs
- ❌ Share secrets via insecure channels
- ❌ Reuse production secrets for testing
- ❌ Grant unnecessary permissions to secrets

## Environment Variables vs Secrets

**When to use Secrets:**
- API keys and tokens
- Database passwords
- Service credentials
- OAuth tokens
- Private keys

**When to use Variables (not secrets):**
- Public configuration values
- Non-sensitive URLs
- Feature flags
- Environment names (dev, staging, prod)

## Updating Secrets

To update an existing secret:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Find the secret in the list
3. Click **Update**
4. Enter the new value
5. Click **Update secret**

**Note:** Updating a secret immediately affects all workflow runs.

## Deleting Secrets

To remove a secret:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Find the secret in the list
3. Click **Remove**
4. Confirm deletion

**Warning:** Workflows using deleted secrets will fail.

## Secret Scopes

GitHub Actions supports three scopes for secrets:

1. **Repository secrets** - Available to all workflows in the repository (we use this)
2. **Environment secrets** - Available only to workflows deployed to specific environments
3. **Organization secrets** - Available to all repositories in the organization

For this project, we use **repository secrets** for simplicity.

## Monitoring Secret Usage

### Audit Logs

1. Go to **Settings** > **Audit log**
2. Filter by "secret" to see:
   - When secrets were created/updated/deleted
   - Who made changes
   - Which workflows accessed secrets

### Workflow Logs

Check workflow logs to see if secrets are being used correctly:
- Successful API calls indicate valid tokens
- Failed authentication suggests expired/invalid secrets

## Troubleshooting

### Codecov Upload Fails

**Error:**
```
Error: Codecov: Failed to properly upload report
```

**Solutions:**
1. Verify `CODECOV_TOKEN` is set correctly
2. Check Codecov.io repository is activated
3. Ensure coverage file exists before upload step
4. Check Codecov service status

### Secret Not Available in Workflow

**Error:**
```
Error: Secret CODECOV_TOKEN is not set
```

**Solutions:**
1. Verify secret name matches exactly (case-sensitive)
2. Check secret is set at repository level (not environment)
3. Ensure workflow has permission to access secrets
4. Re-add the secret if necessary

### Permission Denied

**Error:**
```
Error: Resource not accessible by integration
```

**Solutions:**
1. Check repository **Settings** > **Actions** > **General**
2. Ensure "Read and write permissions" is enabled for GITHUB_TOKEN
3. Update workflow permissions if needed:
   ```yaml
   permissions:
     contents: read
     pull-requests: write
   ```

## Next Steps

After setting up secrets:

1. ✅ Verify all required secrets are configured
2. ✅ Test workflows by triggering manually
3. ✅ Create a pull request to verify status checks
4. ✅ Monitor first few workflow runs for issues
5. ✅ Document any project-specific secrets in project README

## Additional Resources

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Codecov Documentation](https://docs.codecov.io/docs)
- [Sentry Documentation](https://docs.sentry.io/)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

## Support

For issues with secrets setup:

1. Check this documentation
2. Review GitHub Actions logs
3. Consult the main [WORKFLOWS.md](./WORKFLOWS.md) documentation
4. Open an issue with details of the problem
