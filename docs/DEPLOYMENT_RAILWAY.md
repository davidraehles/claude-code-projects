# Railway Deployment Guide

Complete guide for deploying the meal planner application on Railway.

## Table of Contents
- [Overview](#overview)
- [Service Configuration](#service-configuration)
- [Environment Variables](#environment-variables)
- [Deployment Process](#deployment-process)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Overview

The application deploys to Railway with a multi-service architecture:
- **Backend**: Python FastAPI application
- **PostgreSQL**: Database (postgres:15-alpine)
- **Redis**: Caching and sessions (redis:7-alpine)

### Architecture

```
Railway Project
├── backend (FastAPI)
│   ├── Healthcheck: /health
│   ├── Migrations: alembic upgrade head
│   └── Port: ${{PORT}}
├── postgres (Database)
│   └── Persistent volume: /var/lib/postgresql/data
└── redis (Cache)
    └── AOF persistence enabled
```

---

## Service Configuration

### Backend Service

**Build Configuration:**
```json
{
  "build": {
    "context": ".",
    "dockerfile": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "on-failure",
    "restartPolicyMaxRetries": 3
  }
}
```

**Environment Variables:**
- Database: `${{Postgres.PGUSER}}`, `${{Postgres.PGPASSWORD}}`, etc.
- Redis: `${{Redis.REDIS_HOST}}`, `${{Redis.REDIS_PORT}}`
- Port: `${{PORT}}` (Railway assigns automatically)
- Secrets: `SECRET_KEY`, `JWT_SECRET_KEY` (set in Railway dashboard)

### PostgreSQL Service

**Configuration:**
```json
{
  "image": "postgres:15-alpine",
  "volumes": [{
    "mountPath": "/var/lib/postgresql/data",
    "name": "postgres_data"
  }],
  "environment": {
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "${{POSTGRES_PASSWORD}}",
    "POSTGRES_DB": "recipe_app"
  }
}
```

### Redis Service

**Configuration:**
```json
{
  "image": "redis:7-alpine",
  "command": "redis-server --appendonly yes",
  "volumes": [{
    "mountPath": "/data",
    "name": "redis_data"
  }]
}
```

---

## Environment Variables

### Required Variables

Set these in Railway dashboard for the backend service:

```bash
# Database (auto-populated by Railway)
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_NAME=${{Postgres.PGDATABASE}}

# Redis (auto-populated by Railway)
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}

# Application
APP_ENV=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=${{PORT}}

# Security (GENERATE NEW KEYS!)
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
JWT_SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS (set to frontend URL)
CORS_ORIGINS=https://your-app.vercel.app

# Knuspr Integration (optional)
ROHLIK_USERNAME=your-email@example.com
ROHLIK_PASSWORD=your-password
ROHLIK_COUNTRY=DE

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=<your-sentry-dsn>  # optional
```

### Generate Secret Keys

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Deployment Process

### Initial Setup

1. **Create Railway Project**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link
```

2. **Configure Services**

Create `.railway/services.json`:
```json
{
  "services": {
    "backend": {
      "build": {
        "context": ".",
        "dockerfile": "backend/Dockerfile"
      },
      "deploy": {
        "startCommand": "cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
        "healthcheckPath": "/health",
        "healthcheckTimeout": 30
      }
    },
    "postgres": {
      "image": "postgres:15-alpine",
      "volumes": [{
        "mountPath": "/var/lib/postgresql/data"
      }]
    },
    "redis": {
      "image": "redis:7-alpine",
      "command": "redis-server --appendonly yes"
    }
  }
}
```

3. **Set Environment Variables**

Via Railway dashboard or CLI:
```bash
railway variables set SECRET_KEY=<your-secret-key>
railway variables set JWT_SECRET_KEY=<your-jwt-key>
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

4. **Deploy**
```bash
railway up
```

### Continuous Deployment

**Automatic Deploys:**
- Push to `claude/main` → Production deployment
- PR branches → Preview deployments (if configured)

**Manual Deploy:**
```bash
railway up
```

### Database Migrations

Migrations run automatically on deployment via:
```bash
alembic upgrade head
```

**Manual migrations:**
```bash
# Via Railway CLI
railway run alembic upgrade head

# Via Railway shell
railway run bash
cd backend && alembic upgrade head
```

---

## Monitoring

### Health Check

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T00:00:00Z",
  "version": "1.0.0"
}
```

### Logs

**Via Railway Dashboard:**
- Go to Project → Service → Deployments → View Logs

**Via CLI:**
```bash
# Backend logs
railway logs --service backend

# Follow logs
railway logs --service backend --follow

# PostgreSQL logs
railway logs --service postgres
```

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network I/O
- Request metrics

Access via Railway dashboard → Service → Metrics

---

## Troubleshooting

### Deployment Failures

**Check build logs:**
```bash
railway logs --service backend --deployment latest
```

**Common issues:**
1. **Missing dependencies**: Check `requirements.txt`
2. **Migration failures**: Check database connection
3. **Port binding**: Ensure using `${{PORT}}` variable

### Database Connection Issues

**Test connection:**
```bash
railway run psql ${{DATABASE_URL}}
```

**Reset database:**
```bash
railway run alembic downgrade base
railway run alembic upgrade head
```

### Service Crashes

**Check restart policy:**
```json
{
  "restartPolicyType": "on-failure",
  "restartPolicyMaxRetries": 3
}
```

**View crash logs:**
```bash
railway logs --service backend --tail 100
```

### Environment Variable Issues

**List all variables:**
```bash
railway variables
```

**Test variable access:**
```bash
railway run env | grep DB_
```

---

## PR Environment Configuration

Enable preview deployments for PRs:

```json
{
  "prEnvironments": {
    "autoLink": true,
    "autoClone": true,
    "autoRemove": true
  }
}
```

Each PR gets:
- Isolated backend instance
- Shared database (or separate if configured)
- Unique URL: `pr-{number}.railway.app`

---

## Rollback

**Via Railway Dashboard:**
1. Go to Deployments
2. Find previous working deployment
3. Click "Redeploy"

**Via CLI:**
```bash
# List deployments
railway deployments

# Rollback to specific deployment
railway redeploy <deployment-id>
```

---

## Cost Optimization

**Tips:**
1. Use hobby plan for development
2. Configure auto-sleep for preview environments
3. Monitor resource usage
4. Use Redis for caching to reduce database queries
5. Optimize Docker image size

**Resource Limits:**
```json
{
  "deploy": {
    "resources": {
      "cpu": 1,
      "memory": 512
    }
  }
}
```

---

## Security

**Best Practices:**
1. ✅ Use Railway's secret management
2. ✅ Never commit `.env` files
3. ✅ Generate unique keys per environment
4. ✅ Set CORS_ORIGINS to specific domains
5. ✅ Enable HTTPS only (Railway default)
6. ✅ Use strong database passwords
7. ✅ Regular security updates

**Audit:**
```bash
# Check for exposed secrets
git log --all -p | grep -i "password\|secret\|key"
```

---

## Useful Commands

```bash
# Connect to database
railway run psql ${{DATABASE_URL}}

# Run shell in backend
railway run bash

# Check service status
railway status

# View environment
railway variables

# Open in browser
railway open

# Link different project
railway link <project-id>

# Deploy specific service
railway up --service backend
```

---

## Files

**Configuration:**
- `.railway/services.json` - Service definitions
- `backend/Dockerfile` - Backend container
- `railway.toml` - Railway config (optional)

**Migrations:**
- `backend/migrations/` - Alembic migrations
- `backend/alembic.ini` - Alembic configuration

**Deployment:**
- Auto-deploy on push to main
- Healthcheck: `/health` endpoint
- Start command includes migrations
