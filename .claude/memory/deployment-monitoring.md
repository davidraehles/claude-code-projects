# Deployment Monitoring - Project Memory

## Overview
This document captures the deployment monitoring procedures and lessons learned for the multi-agent recipe app project.

## Deployment Architecture

### Backend (Railway)
- **URL**: https://claude-code-projects-production.up.railway.app
- **Framework**: FastAPI (Python)
- **Deployment**: Dockerfile-based
- **Health Check**: `/health` endpoint
- **Auto-deploy**: Triggered on git push (configured via Railway dashboard)

### Frontend (Vercel)
- **Framework**: Next.js
- **Deployment**: Automatic on git push
- **API Proxy**: Routes `/api/*` to Railway backend (configured in vercel.json)

### Database (Railway Postgres)
- **Managed by**: Railway
- **Access**: Via DATABASE_URL environment variable
- **Migrations**: Alembic

---

## Monitoring Procedures

### When to Monitor
Monitor deployments after:
- Pushing code changes to main branch
- Fixing critical bugs
- Deploying new features
- Environment variable changes

### How to Monitor

#### 1. Quick Health Check
```bash
curl https://claude-code-projects-production.up.railway.app/health
```
Expected: `{"status":"healthy","version":"1.0.0",...}`

#### 2. Verify New Code Deployed
Test an endpoint that changed. For auth fixes:
```bash
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","country":"US"}'
```

Old code shows specific error, new code shows different response.

#### 3. Automated Monitoring
```bash
bash scripts/quick_deploy_check.sh   # One-time check
bash scripts/monitor_deployment.sh   # Continuous monitoring
```

---

## Scripts Created

### `scripts/monitor_deployment.sh`
- **Purpose**: Continuous deployment monitoring
- **Features**: Health checks, API version detection, frontend status
- **Usage**: `bash scripts/monitor_deployment.sh`

### `scripts/quick_deploy_check.sh`
- **Purpose**: Quick one-time deployment verification
- **Features**: 5 attempts with 15s intervals
- **Usage**: `bash scripts/quick_deploy_check.sh`

### `scripts/seed_test_user.py`
- **Purpose**: Create/update test user in database
- **Credentials**: test@example.com / testpassword123
- **Usage**: `python scripts/seed_test_user.py`

### `scripts/test_auth_flow.sh`
- **Purpose**: End-to-end authentication testing
- **Tests**: Registration, login, token refresh, authenticated requests
- **Usage**: `bash scripts/test_auth_flow.sh`

---

## Common Deployment Issues

### Issue 1: Railway Not Auto-Deploying
**Symptoms**: Code pushed but old version still running

**Diagnosis**:
```bash
# Check if commit was pushed
git log origin/claude/main -1

# Check if Railway detects it
# (Visit Railway dashboard)
```

**Solutions**:
1. Wait 5-10 minutes (Railway may have delays)
2. Check Railway dashboard for deployment status
3. Manually trigger deployment from Railway UI
4. Verify webhook is configured in Railway settings

### Issue 2: Vercel Not Auto-Deploying
**Symptoms**: Frontend changes not visible

**Solutions**:
1. Check Vercel dashboard
2. Manual deploy: `cd meal-planner-ui && vercel --prod`
3. Verify git integration in Vercel settings

### Issue 3: Database Seeding Fails
**Symptoms**: seed_test_user.py errors

**Solutions**:
1. Verify DATABASE_URL: `echo $DATABASE_URL`
2. Get Railway Postgres URL from dashboard
3. Run with explicit URL: `DATABASE_URL="..." python scripts/seed_test_user.py`
4. Or use Railway CLI: `railway run python scripts/seed_test_user.py`

---

## Deployment Timeline

Typical deployment after git push:

```
0:00  - Git push completes
0:30  - Railway detects push
1:00  - Railway build starts
2:30  - Railway build completes
3:00  - Railway deployment starts
3:30  - Health check passes
4:00  - New code live ✅

0:30  - Vercel detects push
1:00  - Vercel build starts
2:30  - Vercel build completes
3:00  - Vercel deployment complete
3:30  - Frontend live ✅
```

**Total**: 4-5 minutes (can be up to 10 minutes with delays)

---

## Post-Deployment Checklist

After confirming deployment:

- [ ] Backend health check passes
- [ ] New code verified (test changed endpoints)
- [ ] Frontend loads correctly
- [ ] Test user seeded (if needed)
- [ ] End-to-end tests pass
- [ ] Manual smoke test (register, login, navigate)

---

## Monitoring Best Practices

### Always Monitor When:
1. Fixing critical bugs (like auth issues)
2. Making breaking API changes
3. Updating dependencies
4. Changing environment variables
5. Database schema changes

### Don't Need to Monitor:
1. Documentation changes
2. Test file changes
3. Minor refactoring (no behavior change)

### When in Doubt:
Run quick check: `bash scripts/quick_deploy_check.sh`

---

## Lessons Learned

### 2025-11-18: Auth Fixes Deployment
**Context**: Fixed 3 critical auth bugs (endpoint mismatch, password hashing, missing field)

**Observations**:
- Git push succeeded immediately
- Railway deployment took longer than expected (>5 minutes)
- Manual dashboard check confirmed deployment was queued
- Need better real-time deployment status visibility

**Actions Taken**:
- Created monitoring scripts for future deployments
- Documented deployment procedures
- Added this memory document

**Future Improvements**:
- Consider Railway CLI for deployment status
- Add Slack/Discord webhooks for deployment notifications
- Create dashboard for deployment status

---

## Tools & Commands Reference

### Git
```bash
git log -1 --stat                     # Check last commit
git log origin/claude/main -1         # Check remote
git push origin claude/main           # Push to remote
```

### Railway (API/curl)
```bash
curl https://claude-code-projects-production.up.railway.app/health
curl https://claude-code-projects-production.up.railway.app/
```

### Vercel CLI
```bash
vercel --version                      # Check version
vercel ls                             # List deployments
vercel --prod                         # Deploy to production
```

### Database
```bash
railway run python scripts/seed_test_user.py     # Seed user via Railway
DATABASE_URL="..." python scripts/seed_test_user.py  # Seed locally
```

---

## Quick Reference

### Is Backend Deployed?
```bash
bash scripts/quick_deploy_check.sh
```

### Is Frontend Deployed?
Visit your Vercel URL in browser or:
```bash
curl -I <your-vercel-url>
```

### Run Full Test Suite
```bash
bash scripts/test_auth_flow.sh
```

---

## Related Documents
- `DEPLOYMENT_STATUS.md` - Current deployment status
- `scripts/monitor_deployment.sh` - Monitoring script
- `.claude/commands/monitor-deployment.md` - Monitoring command docs
- `railway.toml` - Railway configuration
- `meal-planner-ui/vercel.json` - Vercel configuration

---

**Last Updated**: 2025-11-18 09:35 CET
**Maintained By**: Claude Code + David Raehles
**Status**: Active monitoring in progress
