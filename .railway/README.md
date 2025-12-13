# Railway PR Environments Setup

This directory contains configuration for Railway PR environments that automatically spin up isolated environments for each pull request.

## Architecture

Each PR environment includes:
- **Backend**: FastAPI application with auto-migrations
- **PostgreSQL**: Isolated database instance
- **Redis**: Cache and session storage

## Configuration Files

### `services.json`
Defines the services and their relationships for PR environments. Railway will automatically:
1. Create these services when a PR is opened
2. Link them together (backend → postgres, backend → redis)
3. Run migrations on deployment
4. Destroy them when the PR is closed

## Environment Variables

### Shared Variables (Required)
Set these in Railway dashboard under **Shared Variables** so they're available to all PR environments:

```bash
# Required for all services
JWT_SECRET_KEY=<generate-random-32-char-string>
NEXTAUTH_SECRET=<generate-random-32-char-string>
POSTGRES_PASSWORD=<generate-random-password>
REDIS_PASSWORD=<generate-random-password>

# Required for AI features
OPENAI_API_KEY=sk-...

# Optional: External services
KNUSPR_EMAIL=your-email@example.com
KNUSPR_PASSWORD=your-knuspr-password
```

### Service-Specific Variables
These are automatically set by Railway:
- `DATABASE_URL`: Postgres connection string (from postgres service)
- `REDIS_URL`: Redis connection string (from redis service)
- `PORT`: Application port (set by Railway)

## Setup Instructions

### 1. Enable PR Environments in Railway

1. Go to your Railway project
2. Navigate to **Settings → Environments**
3. Enable **PR Environments**
4. Set base environment to `production` (or `staging`)

### 2. Configure Shared Variables

In Railway dashboard:
1. Go to **Project → Variables**
2. Click **Shared Variables**
3. Add all the required variables listed above

Generate secrets:
```bash
# JWT_SECRET_KEY (32 chars)
openssl rand -base64 32

# NEXTAUTH_SECRET (32 chars)
openssl rand -base64 32

# POSTGRES_PASSWORD
openssl rand -base64 24

# REDIS_PASSWORD
openssl rand -base64 24
```

### 3. Configure Service References

The `services.json` uses Railway's reference syntax:
- `${{ Postgres.DATABASE_URL }}`: References the postgres service's DATABASE_URL
- `${{ Redis.REDIS_URL }}`: References the redis service's REDIS_URL
- `${{ shared.JWT_SECRET_KEY }}`: References shared variables

### 4. Test PR Environment

1. Create a test PR
2. Railway will automatically:
   - Deploy all 3 services
   - Run migrations
   - Provide a unique URL for the backend
3. Check deployment logs to verify:
   - Migrations ran successfully
   - Backend is healthy
   - Database connection works

## PR Environment Lifecycle

### When PR is Opened
1. Railway clones your services
2. Creates isolated postgres and redis instances
3. Deploys backend with migrations
4. Provides unique URLs (e.g., `https://backend-pr-123.up.railway.app`)

### When PR is Updated
1. Existing services are updated
2. Migrations run automatically
3. Zero-downtime deployment

### When PR is Closed/Merged
1. All services are automatically deleted
2. Volumes are cleaned up
3. No manual cleanup needed

## Accessing PR Environments

### Backend URL
Available in PR environment dashboard: `https://backend-pr-{number}.up.railway.app`

### Database Access
```bash
# Get DATABASE_URL from Railway dashboard
railway connect postgres --environment pr-{number}
```

### Redis Access
```bash
# Get REDIS_URL from Railway dashboard
railway connect redis --environment pr-{number}
```

## Frontend Integration

Update your frontend to use PR environment URLs:

### Option 1: Automatic Detection (Vercel)
If using Vercel for frontend, it can automatically detect Railway PR URLs:

```typescript
// frontend/.env.production
NEXT_PUBLIC_API_URL=${{ RAILWAY_PR_URL || 'https://meal-planner.up.railway.app' }}
```

### Option 2: Manual Configuration
In Vercel deployment settings, add:
```bash
NEXT_PUBLIC_API_URL=https://backend-pr-{number}.up.railway.app
```

### Option 3: GitHub Actions Integration
Add to `.github/workflows/preview-deploy.yml`:
```yaml
- name: Get Railway PR URL
  id: railway
  run: |
    RAILWAY_URL=$(railway status --json | jq -r '.url')
    echo "url=$RAILWAY_URL" >> $GITHUB_OUTPUT

- name: Deploy to Vercel Preview
  env:
    NEXT_PUBLIC_API_URL: ${{ steps.railway.outputs.url }}
  run: vercel deploy --build-env NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
```

## Monitoring PR Environments

### Health Checks
Each PR backend includes health endpoint:
```bash
curl https://backend-pr-{number}.up.railway.app/health
```

### Logs
View in Railway dashboard:
1. Select PR environment
2. Click on service (backend/postgres/redis)
3. View real-time logs

### Database State
Check migration status:
```bash
railway run --environment pr-{number} alembic current
```

## Cost Management

PR environments consume resources. To minimize costs:

1. **Set Timeouts**: Configure auto-shutdown for inactive PRs
2. **Limit Services**: Only spin up what's needed for testing
3. **Use Smaller Instances**: PR environments don't need production capacity

In Railway dashboard:
- Settings → Environments → PR Environments → Configure Limits
- Set max PR environments (e.g., 5)
- Set auto-delete after merge (e.g., 1 hour)

## Troubleshooting

### Migrations Fail
**Issue**: `alembic upgrade head` fails on PR deploy

**Solutions**:
1. Check DATABASE_URL is correctly set
2. Verify postgres service is running
3. Check migration files for syntax errors
4. View logs: Railway dashboard → backend service → Logs

### Backend Can't Connect to Postgres
**Issue**: `Connection refused` or `Host not found`

**Solutions**:
1. Verify service references in `services.json`
2. Check postgres service is healthy
3. Ensure `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
4. Test connection: `railway run psql $DATABASE_URL`

### Redis Connection Fails
**Issue**: Backend shows "Redis degraded"

**Solutions**:
1. This is often OK - Redis is optional for core functionality
2. Verify Redis service is running
3. Check `REDIS_URL` format: `redis://:password@host:6379`
4. Make sure Redis password matches in both services

### PR Environment URL Changes
**Issue**: URL changes between deployments

**Solutions**:
1. Use Railway's environment variables in frontend
2. Configure CORS to accept wildcard: `https://*.up.railway.app`
3. Update Vercel preview deployments automatically

## Best Practices

1. **Keep Migrations Fast**: PR deployments wait for migrations
2. **Use Seed Data**: Add test data in migrations for PR testing
3. **Set CORS Properly**: Allow Vercel preview domains
4. **Monitor Costs**: Review Railway usage weekly
5. **Clean Up**: Merge or close stale PRs regularly

## Example: Testing with PR Environment

```bash
# 1. Create PR
git checkout -b feature/new-endpoint
git push origin feature/new-endpoint
# Open PR on GitHub

# 2. Wait for Railway deployment (~2-3 min)
# Check PR comments for Railway deployment URL

# 3. Test the PR environment
PR_URL="https://backend-pr-42.up.railway.app"
curl $PR_URL/health

# 4. Create test user
curl -X POST $PR_URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123", "country": "US"}'

# 5. Test your new endpoint
curl $PR_URL/api/v1/your-new-endpoint

# 6. Merge PR
# Railway automatically destroys the PR environment
```

## Related Documentation

- [Railway PR Environments Docs](https://docs.railway.app/deploy/environments#pr-environments)
- [Railway Service References](https://docs.railway.app/deploy/variables#service-variables)
- [Railway Volumes](https://docs.railway.app/deploy/volumes)
- [PostgreSQL on Railway](https://docs.railway.app/databases/postgresql)
- [Redis on Railway](https://docs.railway.app/databases/redis)
