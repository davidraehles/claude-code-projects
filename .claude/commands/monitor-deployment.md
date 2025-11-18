# Monitor Deployment

Monitor Railway backend and Vercel frontend deployments after pushing code changes.

## What this does

This command monitors deployment status by:
1. Checking Railway backend health endpoint
2. Testing if new code is deployed (checking API endpoints)
3. Optionally checking Vercel frontend status
4. Providing real-time deployment progress

## Usage

After pushing code changes:
```bash
bash scripts/monitor_deployment.sh
```

Or monitor manually:
```bash
# Check backend health
curl https://claude-code-projects-production.up.railway.app/health

# Test if new code is deployed
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"test":"test"}'
```

## What to expect

- Backend redeploy takes 2-3 minutes
- Frontend redeploy takes 1-2 minutes
- Health check shows green when services are ready
- API endpoint changes indicate new code is live

## Troubleshooting

If deployment doesn't auto-trigger on Railway:
1. Check Railway dashboard for deployment status
2. Manually trigger deployment from Railway dashboard
3. Check build logs for errors

If Vercel doesn't auto-deploy:
1. Check Vercel dashboard for deployment status
2. Run `vercel --prod` to manually deploy
3. Ensure git integration is configured
