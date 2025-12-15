# CI/CD Quick Start Guide

Get your CI/CD pipeline up and running in 5 minutes.

## Step 1: Configure Codecov (2 minutes)

1. Go to https://codecov.io
2. Sign in with GitHub
3. Click "Add new repository"
4. Select your repository
5. Copy the upload token
6. In GitHub:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `CODECOV_TOKEN`
   - Value: Paste the token
   - Click **Add secret**

## Step 2: Enable Branch Protection (2 minutes)

1. Go to **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Branch name pattern: `claude/main`
4. Check these boxes:
   - ☑ Require status checks to pass before merging
   - ☑ Require branches to be up to date before merging
5. Select status checks (search and select):
   - ☑ test (3.11)
   - ☑ test (3.12)
   - ☑ test (20.x)
   - ☑ test (22.x)
   - ☑ lint
6. Click **Create** (or **Save changes**)

## Step 3: Test the Pipeline (1 minute)

```bash
# Create a test branch
git checkout -b test/ci-pipeline

# Make a trivial change
echo "# CI Test" >> README.md

# Commit and push
git add README.md
git commit -m "test: verify CI pipeline"
git push origin test/ci-pipeline

# Watch it run!
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

## That's It!

Your CI/CD pipeline is now active. Every push and pull request will automatically:

- ✅ Run backend unit tests (Python 3.11, 3.12)
- ✅ Run frontend unit tests (Node.js 20.x, 22.x)
- ✅ Run frontend linting (ESLint + TypeScript)
- ✅ Upload coverage to Codecov
- ✅ Block merge if any check fails

## What Happens Next?

When you create a pull request, you'll see:

1. Status checks appear in the PR (usually within 30 seconds)
2. Workflows run in parallel (~15-20 minutes total)
3. Coverage reports appear as PR comments
4. Merge button is disabled until all checks pass
5. Once green, you can merge with confidence!

## Need Help?

- **Quick commands**: [WORKFLOWS_QUICK_REFERENCE.md](WORKFLOWS_QUICK_REFERENCE.md)
- **Troubleshooting**: [WORKFLOWS.md](WORKFLOWS.md#troubleshooting)
- **Detailed docs**: [README.md](README.md)

## Common Issues

**Workflows not running?**
- Check that your changes are in `backend/` or `frontend/` directories
- Workflows only trigger on changes to relevant paths

**Coverage upload fails?**
- Verify `CODECOV_TOKEN` is set correctly
- Check workflow logs for specific error

**Status checks not required?**
- Make sure you selected them in branch protection settings
- Status checks appear after first workflow run

---

**Time to complete:** ~5 minutes
**Difficulty:** Easy
**Status:** Ready to use immediately after setup
