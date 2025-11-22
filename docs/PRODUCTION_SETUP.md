# Phase 4: Production Infrastructure Setup Guide

**Status**: Ready for Production
**Last Updated**: 2025-11-22
**Target**: Production Release v1.0

---

## Overview

This guide covers all infrastructure, secrets management, and deployment configuration needed to run the meal planner application in production.

The application consists of:
- **Backend**: FastAPI + PostgreSQL + Redis (Railway)
- **Frontend**: Next.js (Vercel)
- **Integration**: Knuspr MCP Client (Local or Remote SSE)

---

## 1. Backend (Railway) Environment Variables

### Database Configuration

```bash
# PostgreSQL credentials (provided by Railway)
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_NAME=recipe_app
```

**Setup Steps**:
1. Create a PostgreSQL plugin in Railway
2. Copy the credentials from the Railway dashboard
3. Set these variables in Railway environment

### Security Keys (REQUIRED - Generate New Keys)

```bash
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=<generate-random-secure-key>
JWT_SECRET_KEY=<generate-random-secure-jwt-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1

# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
KNUSPR_ENCRYPTION_KEY=<generate-fernet-key>
```

**Generation Commands**:
```bash
# Generate SECRET_KEY and JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate KNUSPR_ENCRYPTION_KEY (Fernet)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Redis Configuration

```bash
# Redis credentials (provided by Railway)
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
REDIS_DB=0
```

**Setup Steps**:
1. Create a Redis plugin in Railway
2. Copy the credentials from the Railway dashboard
3. Set these variables in Railway environment

### Application Settings

```bash
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=${{PORT}}  # Railway provides this automatically

# CORS Configuration - Set to your frontend domain(s)
CORS_ORIGINS=https://your-vercel-deployment.vercel.app,https://custom-domain.com
```

### Knuspr MCP Configuration

**Option A: Local MCP Server (Recommended for MVP)**
```bash
# Uses local stdio connection to Node.js MCP server
# Ensure rohlik-mcp server is running on the same container
ROHLIK_MCP_URL=  # Leave empty to use local stdio mode
ROHLIK_USERNAME=<knuspr-account-email>
ROHLIK_PASSWORD=<knuspr-account-password>
ROHLIK_BASE_URL=https://www.knuspr.de
```

**Option B: Remote MCP Server (Scalable)**
```bash
# Uses SSE (Server-Sent Events) for remote MCP connection
ROHLIK_MCP_URL=https://mcp-server.your-domain.com
ROHLIK_USERNAME=<knuspr-account-email>
ROHLIK_PASSWORD=<knuspr-account-password>
ROHLIK_BASE_URL=https://www.knuspr.de
```

**Important**: These credentials should be encrypted and stored securely per-user, not in environment variables.

### Complete Backend Environment Template

```bash
# === DATABASE ===
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_NAME=recipe_app

# === REDIS ===
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
REDIS_DB=0

# === SECURITY (GENERATE NEW) ===
SECRET_KEY=<generated-secure-key>
JWT_SECRET_KEY=<generated-jwt-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
KNUSPR_ENCRYPTION_KEY=<generated-fernet-key>

# === APPLICATION ===
APP_ENV=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=${{PORT}}
LOG_LEVEL=INFO

# === CORS ===
CORS_ORIGINS=https://your-app.vercel.app

# === MCP (choose A or B above) ===
ROHLIK_MCP_URL=
ROHLIK_USERNAME=
ROHLIK_PASSWORD=
ROHLIK_BASE_URL=https://www.knuspr.de
```

---

## 2. Frontend (Vercel) Environment Variables

### API Configuration

```bash
# Backend API URL (Railway deployment)
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

### Authentication (REQUIRED - Generate New Key)

```bash
# Generate with: openssl rand -base64 32
NEXTAUTH_SECRET=<generated-secret>

# Your Vercel deployment URL
NEXTAUTH_URL=https://your-app.vercel.app
```

**Generation Command**:
```bash
openssl rand -base64 32
```

### Complete Frontend Environment Template

```bash
# === API ===
NEXT_PUBLIC_API_URL=https://your-railway-deployment.up.railway.app

# === NEXTAUTH (GENERATE NEW) ===
NEXTAUTH_SECRET=<generated-secret>
NEXTAUTH_URL=https://your-vercel-app.vercel.app
```

---

## 3. Railway Deployment Configuration

### Health Check Configuration

The `railway.toml` is already configured:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**No changes needed** - this is production-ready.

### Deploy Steps

1. **Connect GitHub Repository**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Connect your GitHub repo

2. **Add Services**
   - PostgreSQL: Click "Add" → Provision PostgreSQL
   - Redis: Click "Add" → Provision Redis
   - (Backend app auto-detects Dockerfile)

3. **Configure Environment Variables**
   - Use the template above
   - Railway will display service variable placeholders (e.g., `${{Postgres.PGHOST}}`)
   - Copy-paste these into the environment section

4. **Set Domains**
   - Railway assigns a default domain: `your-app.up.railway.app`
   - Optionally add custom domain in Project Settings

5. **Deploy**
   - Click "Deploy" or enable auto-deploy from main branch
   - Monitor health checks in deployment logs

---

## 4. Vercel Deployment Configuration

### Deploy Steps

1. **Connect GitHub Repository**
   - Go to vercel.com
   - Click "New Project"
   - Select your GitHub repo
   - Vercel auto-detects Next.js

2. **Configure Environment Variables**
   - In Project Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` and `NEXTAUTH_*` variables
   - Use the template above

3. **Build Settings**
   - Framework: Next.js (auto-detected)
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

4. **Deploy**
   - Click "Deploy"
   - Vercel builds and deploys automatically
   - Get your deployment URL from Vercel dashboard

---

## 5. Secrets Management Best Practices

### Key Rotation

**Schedule**: Every 90 days or immediately if compromised

**Steps**:
1. Generate new `JWT_SECRET_KEY` and `SECRET_KEY`
2. Update Railway environment variables
3. Restart the service
4. No frontend changes needed (auth is stateless)

### Credential Storage

**User Credentials** (Knuspr):
- ✅ Encrypted with `KNUSPR_ENCRYPTION_KEY` before database storage
- ✅ Decrypted only when needed for MCP calls
- ✅ Never logged or exposed in errors
- ✅ Per-user, not global

**Application Secrets**:
- ✅ Stored in Railway environment (not in code)
- ✅ Never committed to Git
- ✅ Rotated regularly
- ✅ Different keys for dev/staging/production

### Audit Trail

Implement logging for:
- User authentication failures
- Knuspr credential access
- MCP client errors
- Cart generation failures

See logging configuration in sections below.

---

## 6. Monitoring & Error Tracking

### Structured Logging

The application uses Python's built-in logging with structured JSON output for production:

```python
import logging
import json

logger = logging.getLogger(__name__)

# Structured log example
logger.info(json.dumps({
    'event': 'cart_generated',
    'user_id': user_id,
    'meal_plan_id': meal_plan_id,
    'cart_id': cart_id,
    'duration_ms': elapsed_ms
}))
```

**Log Level Configuration**:
```bash
LOG_LEVEL=INFO  # Production setting (not DEBUG)
```

### Health Check Endpoint

The application exposes `/health` for monitoring:

```bash
# Railway uses this for health checks
curl https://your-api.up.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-11-22T10:30:00Z",
  "services": {
    "database": "ok",
    "redis": "ok"
  }
}
```

### Error Tracking (Optional)

To add error tracking (Sentry, DataDog, etc.):

1. **Install client**:
   ```bash
   pip install sentry-sdk
   ```

2. **Configure in `app/main.py`**:
   ```python
   import sentry_sdk

   sentry_sdk.init(
       dsn=os.getenv("SENTRY_DSN"),
       environment=os.getenv("APP_ENV"),
       traces_sample_rate=0.1,
   )
   ```

3. **Add environment variable to Railway**:
   ```bash
   SENTRY_DSN=https://your-key@sentry.io/your-project-id
   ```

---

## 7. Database Migrations

The application uses SQLAlchemy ORM with Alembic for migrations.

### Initial Setup

After deploying to Railway:

```bash
# SSH into Railway pod
railway shell

# Run migrations
alembic upgrade head
```

### Adding Schema Changes

```bash
# Create migration locally
alembic revision --autogenerate -m "Add new column"

# Apply locally to test
alembic upgrade head

# Commit migration files to Git
git add alembic/versions/
git commit -m "Add migration"

# Deploy to Railway
# (Migrations run automatically in health check startup)
```

---

## 8. MCP Server Deployment Strategy

### Option A: Local MCP Server (Current MVP)

**Pros**:
- ✅ Simple setup
- ✅ No external dependencies
- ✅ Works with Railway stdio

**Cons**:
- ❌ Scales poorly with multiple instances
- ❌ Node.js server must run on same container

**Setup**:
```bash
# In Railway Dockerfile
RUN npm install -g rohlik-mcp
CMD ["sh", "-c", "rohlik-mcp &  && uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
```

### Option B: Remote MCP Server (Recommended for Scale)

**Pros**:
- ✅ Scales independently
- ✅ Separate infrastructure
- ✅ SSE/HTTP protocol

**Cons**:
- ❌ Additional infrastructure
- ❌ Network latency

**Setup**:
1. Deploy MCP server to separate Railway project/service
2. Expose ROHLIK_MCP_URL (e.g., `https://mcp-server.your-domain.com`)
3. Backend connects via SSE

**Deployment Example**:
```bash
# Separate Railway service for MCP
# Dockerfile: FROM node:18
# CMD: ["node", "dist/index.js"]
# Port: 3000
# ROHLIK_MCP_URL: https://mcp-server.up.railway.app
```

---

## 9. Production Checklist

### Pre-Launch

- [ ] Generate all security keys (SECRET_KEY, JWT_SECRET_KEY, KNUSPR_ENCRYPTION_KEY, NEXTAUTH_SECRET)
- [ ] Set up PostgreSQL and Redis on Railway
- [ ] Configure all environment variables on Railway
- [ ] Configure CORS_ORIGINS to match Vercel deployment URL
- [ ] Set NEXTAUTH_URL to your Vercel deployment
- [ ] Set NEXT_PUBLIC_API_URL to your Railway deployment
- [ ] Test health check: `curl https://your-api.up.railway.app/health`
- [ ] Deploy to Vercel
- [ ] Test authentication flow end-to-end
- [ ] Test meal plan generation
- [ ] Test Knuspr credentials setup and cart workflow
- [ ] Verify error handling and user-friendly error messages

### Post-Launch

- [ ] Monitor application logs for errors
- [ ] Set up 24/7 uptime monitoring
- [ ] Configure error alerts (Sentry, email, Slack)
- [ ] Document runbook for on-call engineers
- [ ] Set up automated backups for PostgreSQL
- [ ] Implement log retention policy (e.g., 30 days)
- [ ] Schedule quarterly security key rotation
- [ ] Test disaster recovery procedures

### Ongoing

- [ ] Weekly log review for anomalies
- [ ] Monthly performance metrics review
- [ ] Quarterly security audit
- [ ] Annual disaster recovery drill
- [ ] Keep dependencies updated (security patches)

---

## 10. Troubleshooting Common Issues

### Health Check Fails

**Symptoms**: `502 Bad Gateway`, deployment keeps restarting

**Solutions**:
```bash
# Check logs
railway logs

# Check database connectivity
railway shell
python -c "from app.db import engine; engine.connect()"

# Check Redis connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping
```

### MCP Server Connection Error

**Symptoms**: "Failed to connect to MCP server" in logs

**Solutions**:
```bash
# If using local mode (stdio)
# Ensure Node.js is installed: apt-get install nodejs npm
# Ensure rohlik-mcp is running: ps aux | grep rohlik

# If using remote SSE mode
# Test endpoint: curl https://mcp-server.your-domain.com/health
# Check ROHLIK_MCP_URL is set correctly
```

### High Memory Usage

**Symptoms**: Container restarts, OOM killer in logs

**Solutions**:
```bash
# Reduce MAX_WORKERS in deployment
API_WORKERS=2  # Default is 4

# Monitor memory usage
railway logs | grep memory
```

### Slow Meal Plan Generation

**Symptoms**: Requests timeout after 30+ seconds

**Solutions**:
```bash
# Increase request timeout in frontend
# Vercel timeout: 60 seconds (check your plan)
# Railway health check timeout: already set to 100s

# Optimize backend queries
# Check database performance logs
```

---

## 11. Support & Escalation

### Critical Issues (Immediate Action)

- [ ] Health checks failing (service down)
- [ ] High error rate (>5%)
- [ ] Database connection issues
- [ ] Security breach or suspicious activity

**Action**: Page on-call engineer immediately

### Important Issues (Within 1 Hour)

- [ ] Performance degradation (>2x normal response time)
- [ ] Specific feature failures (cart generation, auth)
- [ ] Knuspr API integration failures

**Action**: Create incident ticket, notify team

### Minor Issues (Within 24 Hours)

- [ ] Typos or minor UI issues
- [ ] Non-critical feature requests
- [ ] Documentation updates

---

## Quick Start Command Reference

```bash
# Generate security keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Fernet key for encryption
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate NextAuth secret
openssl rand -base64 32

# SSH into Railway container
railway shell

# View logs
railway logs

# Restart service
railway service restart

# Set environment variable
railway variable set KEY=VALUE
```

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [NextAuth.js Documentation](https://next-auth.js.org)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)

