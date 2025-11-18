# Deployment Status & Monitoring

## Current Status

**Last Code Push**: 2025-11-18 09:25 CET (commit 2450bca)
**Railway Backend**: ⏳ Awaiting deployment
**Vercel Frontend**: ⏳ Pending

---

## Recent Changes (Commit 2450bca)

### Critical Authentication Fixes
1. ✅ Fixed signup endpoint path (/auth/signup → /auth/register)
2. ✅ Fixed password hashing bug in bcrypt
3. ✅ Added country field to signup request

### Scripts Added
- `scripts/seed_test_user.py` - Seed test user in database
- `scripts/test_auth_flow.sh` - End-to-end auth testing
- `scripts/monitor_deployment.sh` - Monitor deployment status
- `scripts/quick_deploy_check.sh` - Quick deployment verification

---

## How to Monitor Deployments

### Automatic Monitoring
```bash
# Run continuous monitoring
bash scripts/monitor_deployment.sh

# Quick one-time check
bash scripts/quick_deploy_check.sh
```

### Manual Checks

#### Railway Backend Status
```bash
# Check health endpoint
curl https://claude-code-projects-production.up.railway.app/health

# Test if new code is deployed (should NOT show password hashing error)
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","country":"US"}'

# OLD CODE returns: "password cannot be longer than 72 bytes"
# NEW CODE returns: {"access_token": "..."} or {"detail": "Email already registered"}
```

#### Vercel Frontend Status
```bash
# Check if frontend is accessible
curl -I <your-vercel-url>
```

---

## Deployment Workflows

### Railway Auto-Deployment
Railway should auto-deploy when commits are pushed to the main branch.

**If auto-deployment doesn't trigger:**
1. Check Railway dashboard: https://railway.app/dashboard
2. Look for deployment in progress
3. Check build logs for errors
4. Manually trigger deployment from Railway dashboard

**Common Issues:**
- Railway may have deployment delays (2-10 minutes)
- Check webhook is configured for the repository
- Verify branch is correctly set in Railway settings

### Vercel Auto-Deployment
Vercel should auto-deploy when commits are pushed.

**Manual Deployment:**
```bash
cd meal-planner-ui
vercel --prod
```

**Check Deployment:**
1. Visit Vercel dashboard: https://vercel.com/dashboard
2. Check deployment status
3. View deployment logs

---

## Post-Deployment Checklist

Once deployments complete:

### 1. Verify Backend
```bash
# Test registration (should work)
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"testpassword123","country":"US"}'
```

### 2. Seed Test User
```bash
# Run locally with production DATABASE_URL
DATABASE_URL="<railway-postgres-url>" python scripts/seed_test_user.py

# OR run directly on Railway (requires Railway CLI)
railway run python scripts/seed_test_user.py
```

### 3. Run End-to-End Tests
```bash
bash scripts/test_auth_flow.sh
```

### 4. Manual Testing
1. Visit frontend URL
2. Try registering new account
3. Try logging in with test@example.com / testpassword123
4. Verify redirect to dashboard works

---

## Troubleshooting

### Railway Deployment Not Triggered
**Symptoms**: Old code still running after push

**Solutions:**
1. Check Railway dashboard for deployment status
2. Verify git push succeeded: `git log origin/claude/main -1`
3. Check Railway webhook is configured
4. Manually redeploy from Railway dashboard
5. Check Railway logs for build errors

### Vercel Deployment Not Triggered
**Symptoms**: Frontend changes not visible

**Solutions:**
1. Check Vercel dashboard
2. Verify git integration is configured
3. Manual deploy: `cd meal-planner-ui && vercel --prod`
4. Check build logs for errors

### Database Connection Issues
**Symptoms**: Seeding script fails

**Solutions:**
1. Verify DATABASE_URL is correct
2. Check Railway Postgres is running
3. Verify database credentials
4. Test connection: `railway run python -c "from app.database import engine; print(engine)"`

---

## Expected Timeline

After code push:

1. **Git Push**: Immediate
2. **Railway Detection**: 0-2 minutes
3. **Railway Build**: 1-2 minutes
4. **Railway Deploy**: 30-60 seconds
5. **Vercel Detection**: 0-1 minute
6. **Vercel Build**: 1-2 minutes
7. **Vercel Deploy**: 30 seconds

**Total Expected**: 5-10 minutes for both services

---

## Last Updated
2025-11-18 09:30 CET

## Monitoring Commands

```bash
# Watch for Railway deployment
watch -n 10 "curl -s https://claude-code-projects-production.up.railway.app/health | grep -o '\"version\":\"[^\"]*'"

# Continuous deployment check
while true; do
  bash scripts/quick_deploy_check.sh
  sleep 30
done
```
