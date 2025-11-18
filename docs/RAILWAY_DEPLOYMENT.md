# Railway Backend Deployment Guide

Complete guide to deploy the FastAPI backend to Railway with PostgreSQL and Redis.

## Why Railway + Vercel?

✅ **Perfect Match**:
- Railway hosts your backend API, database, and Redis
- Vercel hosts your Next.js frontend
- Frontend makes API calls to Railway's public URL
- CORS allows secure cross-origin communication

## Prerequisites

- [ ] GitHub repository with backend code
- [ ] Railway account (sign up at https://railway.app)
- [ ] Vercel deployment completed (or domain ready)

---

## Part 1: Deploy Backend to Railway

### Step 1: Create Railway Project

1. **Go to Railway**:
   - Visit [https://railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project"

2. **Deploy from GitHub**:
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Python and start building

### Step 2: Add PostgreSQL Database

1. **In your Railway project**:
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway creates a database and provides connection details

2. **Note the connection details**:
   Railway automatically sets these variables for you:
   - `PGHOST`
   - `PGPORT`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`

### Step 3: Add Redis

1. **In your Railway project**:
   - Click "+ New"
   - Select "Database" → "Redis"
   - Railway creates a Redis instance

2. **Note the Redis URL**:
   - Railway automatically sets `REDIS_URL`

### Step 4: Configure Environment Variables

In your Railway service (the Python app), add these environment variables:

#### Required Variables:

```bash
# Application Settings
APP_ENV=production
DEBUG=False

# Database (use Railway's provided variables)
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_NAME=${{Postgres.PGDATABASE}}

# Redis (use Railway's provided variable)
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
REDIS_DB=0

# API Configuration
API_HOST=0.0.0.0
API_PORT=${{PORT}}

# Security (IMPORTANT: Generate secure values!)
SECRET_KEY=<generate-secure-random-string>
JWT_SECRET_KEY=<generate-secure-random-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS - Your Vercel Frontend URL(s)
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com

# Logging
LOG_LEVEL=INFO
```

#### Generate Secure Keys:

```bash
# On your local machine:
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Run twice to get two different keys for SECRET_KEY and JWT_SECRET_KEY
```

### Step 5: Deploy

1. **Railway auto-deploys** when you push to GitHub
2. **First deployment** may take 3-5 minutes
3. **Check deployment logs** for any errors

### Step 6: Get Your Railway URL

1. In Railway dashboard:
   - Go to your service (Python app)
   - Click "Settings"
   - Under "Networking" → "Public Domain"
   - Click "Generate Domain"
   - Copy the URL (e.g., `https://your-app.up.railway.app`)

2. **Test your API**:
   ```bash
   curl https://your-app.up.railway.app/health
   # Should return: {"status":"healthy","version":"1.0.0",...}
   ```

---

## Part 2: Connect Vercel Frontend to Railway Backend

### Step 1: Update Vercel Environment Variables

1. **Go to Vercel Dashboard**:
   - Select your frontend project
   - Go to "Settings" → "Environment Variables"

2. **Update NEXT_PUBLIC_API_URL**:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://your-app.up.railway.app
   ```

3. **Save and Redeploy**:
   - Go to "Deployments"
   - Click "Redeploy" on the latest deployment

### Step 2: Update Railway CORS Settings

1. **In Railway**, update the `CORS_ORIGINS` variable to include your Vercel URL:
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-custom-domain.com
   ```

2. **Railway will auto-redeploy** with new CORS settings

---

## Part 3: Database Migrations

### Option A: Auto-create Tables (Development Only)

The app automatically creates tables when `APP_ENV=development`. For production:

### Option B: Manual Migration (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run alembic upgrade head
```

### Option C: Via Railway Dashboard

1. In Railway, go to your service
2. Click "Settings" → "Deploy"
3. Add a one-time migration command:
   ```bash
   python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

---

## Part 4: Testing the Full Stack

### Test Backend API

```bash
# Health check
curl https://your-railway-app.up.railway.app/health

# API docs
open https://your-railway-app.up.railway.app/api/docs
```

### Test Frontend → Backend Connection

1. **Visit your Vercel URL**
2. **Open browser console** (F12)
3. **Login/Signup** and check for API calls
4. **Check Network tab** - API requests should go to Railway URL

### Common Issues

#### Issue: "CORS error" in browser console
**Solution**:
- Verify `CORS_ORIGINS` in Railway includes your exact Vercel URL
- Make sure it starts with `https://` (no trailing slash)
- Redeploy Railway after changes

#### Issue: "Failed to fetch"
**Solution**:
- Check Railway service is running (green status)
- Test backend URL directly in browser
- Check Railway logs for errors

#### Issue: "Database connection error"
**Solution**:
- Verify Railway PostgreSQL is running
- Check `DB_*` variables are correctly referencing PostgreSQL
- Use Railway's template variables: `${{Postgres.PGHOST}}`

---

## Part 5: Custom Domain (Optional)

### Add Custom Domain to Railway

1. **In Railway Dashboard**:
   - Go to your service → Settings
   - Under "Networking" → "Custom Domain"
   - Add your domain (e.g., `api.yourdomain.com`)

2. **Configure DNS**:
   Add CNAME record in your DNS provider:
   ```
   Type: CNAME
   Name: api
   Value: <railway-provided-value>
   ```

3. **Update Vercel**:
   - Change `NEXT_PUBLIC_API_URL` to `https://api.yourdomain.com`
   - Redeploy

4. **Update Railway CORS**:
   - Update `CORS_ORIGINS` to include custom domain
   - Railway auto-redeploys

---

## Part 6: Monitoring & Maintenance

### View Logs

In Railway:
- Go to your service
- Click "Deployments" tab
- Click on latest deployment
- View real-time logs

### Monitor Resources

- Railway dashboard shows:
  - CPU usage
  - Memory usage
  - Network traffic
  - Database size

### Set Up Alerts

1. **In Railway**:
   - Go to project settings
   - Add webhook for deployment notifications
   - Integrate with Slack/Discord

### Prometheus Metrics

Your API exposes Prometheus metrics at `/metrics`:
```bash
curl https://your-railway-app.up.railway.app/metrics
```

---

## Environment Variables Quick Reference

| Variable | Example | Where to Set |
|----------|---------|--------------|
| `NEXT_PUBLIC_API_URL` | `https://api.railway.app` | **Vercel** |
| `CORS_ORIGINS` | `https://app.vercel.app` | **Railway** |
| `DB_HOST` | `${{Postgres.PGHOST}}` | **Railway** |
| `REDIS_HOST` | `${{Redis.REDIS_HOST}}` | **Railway** |
| `SECRET_KEY` | `<random-string>` | **Railway** |

---

## Deployment Checklist

### Backend (Railway):
- [ ] PostgreSQL database created
- [ ] Redis instance created
- [ ] All environment variables configured
- [ ] CORS_ORIGINS includes Vercel URL
- [ ] Database migrations run
- [ ] Backend deployment successful
- [ ] Health check endpoint returns 200
- [ ] API docs accessible at `/api/docs`

### Frontend (Vercel):
- [ ] NEXT_PUBLIC_API_URL points to Railway
- [ ] Frontend deployed successfully
- [ ] Can login/signup
- [ ] API calls work (check browser console)
- [ ] No CORS errors

### Integration:
- [ ] Frontend can fetch data from backend
- [ ] Authentication works end-to-end
- [ ] Recipes load on dashboard
- [ ] Meal plan generation works
- [ ] Grocery cart creation works

---

## Cost Estimates

### Railway (Hobby Plan - $5/month):
- 500 hours execution time
- PostgreSQL database (shared)
- Redis (shared)
- Good for MVP/small apps

### Railway (Pro Plan - Usage-based):
- Unlimited execution time
- Dedicated databases
- Better for production

### Vercel (Free):
- 100GB bandwidth
- Unlimited deployments
- Great for frontend hosting

---

## Rollback Instructions

### Rollback Railway Deployment

1. Go to Railway dashboard
2. Click "Deployments"
3. Find working deployment
4. Click "Redeploy"

### Rollback Vercel Deployment

1. Go to Vercel dashboard
2. Click "Deployments"
3. Find working deployment
4. Click "..." → "Promote to Production"

---

## CI/CD Setup

Railway automatically deploys when you push to GitHub:

### Automatic Deployments:
- **Push to main** → Railway deploys backend
- **Push to main** → Vercel deploys frontend
- Both happen in parallel

### Preview Deployments:
- **Pull requests** create preview environments
- Test before merging to main

---

## Security Checklist

- [ ] `SECRET_KEY` is cryptographically secure (32+ chars)
- [ ] `JWT_SECRET_KEY` is different from SECRET_KEY
- [ ] `DEBUG=False` in production
- [ ] CORS only allows your frontend domains
- [ ] Database uses SSL (Railway enables by default)
- [ ] API uses HTTPS (Railway provides by default)
- [ ] Environment variables not committed to git
- [ ] Rate limiting enabled (add if not present)

---

## Getting Help

- **Railway Docs**: https://docs.railway.app
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Railway Discord**: https://discord.gg/railway

---

## Quick Start Commands

```bash
# Generate secure keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Install Railway CLI
npm install -g @railway/cli

# Login and link
railway login
railway link

# View logs
railway logs

# Run migrations
railway run alembic upgrade head

# Open Railway dashboard
railway open
```

---

**You're ready to deploy!** 🚀

1. Push your code to GitHub
2. Create Railway project from GitHub repo
3. Add PostgreSQL + Redis
4. Set environment variables
5. Deploy!

Your full stack will be live in ~10 minutes.
