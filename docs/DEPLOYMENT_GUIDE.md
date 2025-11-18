# Deployment Guide: Multi-Agent Recipe App

Complete guide for deploying the FastAPI backend on Railway and Next.js frontend on Vercel.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Railway Backend Setup](#railway-backend-setup)
3. [Vercel Frontend Setup](#vercel-frontend-setup)
4. [Common Issues & Solutions](#common-issues--solutions)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│         https://claude-code-projects.vercel.app             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├──► /api/auth/*  (NextAuth - Vercel)
                              │
                              └──► /api/v1/*    (Proxied to Railway)
                                        │
                         ┌──────────────┴───────────────┐
                         ▼                              ▼
            ┌─────────────────────┐       ┌─────────────────────┐
            │   FastAPI Backend   │       │   PostgreSQL DB     │
            │      (Railway)      │◄──────┤     (Railway)       │
            └─────────────────────┘       └─────────────────────┘
```

**Stack:**
- **Frontend**: Next.js 14 (App Router) + NextAuth.js
- **Backend**: FastAPI + SQLAlchemy + passlib/bcrypt
- **Database**: PostgreSQL 15
- **Hosting**: Vercel (frontend) + Railway (backend + DB)

---

## Railway Backend Setup

### 1. Create Services

Create two Railway services:
1. **PostgreSQL** (from template)
2. **FastAPI** (from GitHub repo)

### 2. Environment Variables

Set in the **FastAPI service**:

```bash
# Database (use Reference to Postgres service)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT Authentication
JWT_SECRET_KEY=<generate with: openssl rand -hex 32>

# Application
APP_ENV=production

# CORS (optional but recommended)
CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
```

**Important**: Use Railway's **Reference** feature for `DATABASE_URL`, not copy-paste!

### 3. Deployment Configuration

Ensure `railway.toml` is configured:

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

### 4. Deploy & Verify

```bash
# Deploy from local (or let GitHub auto-deploy)
railway up -d --service <service-id> --environment production

# Test health endpoint
curl https://your-app.up.railway.app/health

# Test authentication
curl -X POST https://your-app.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","country":"US"}'
```

---

## Vercel Frontend Setup

### 1. Connect GitHub Repo

1. Go to Vercel dashboard
2. Import project from GitHub
3. Select `claude-code-projects` repo
4. Root directory: `meal-planner-ui`
5. Framework: Next.js (auto-detected)

### 2. Environment Variables

Set in Vercel project settings:

```bash
# Backend API (Railway URL)
NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app

# NextAuth Configuration
NEXTAUTH_SECRET=<generate with: openssl rand -base64 32>
NEXTAUTH_URL=https://claude-code-projects.vercel.app
```

**Apply to**: Production, Preview, Development (all 3 environments)

### 3. Configuration Files

Ensure `vercel.json` proxies only backend routes:

```json
{
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "https://claude-code-projects-production.up.railway.app/api/v1/:path*"
    }
  ]
}
```

**Critical**: Only proxy `/api/v1/*`, NOT `/api/*` (NextAuth needs `/api/auth/*`)

### 4. Deploy & Verify

```bash
# Deploy via Vercel CLI (or auto-deploy from GitHub)
cd meal-planner-ui
vercel --prod

# Test NextAuth
curl https://claude-code-projects.vercel.app/api/auth/providers

# Test login flow
# Visit: https://claude-code-projects.vercel.app/login
```

---

## Common Issues & Solutions

### Issue 1: "password cannot be longer than 72 bytes"

**Symptoms:** Registration fails with error for short passwords (e.g., "testpassword123")

**Root Cause:** Incorrect bcrypt usage in passlib

**Solution:**

1. Add explicit bcrypt dependency to `requirements.txt`:
   ```txt
   bcrypt==4.0.1
   passlib[bcrypt]==1.7.4
   ```

2. Use configured hasher in `app/api/v1/auth.py`:
   ```python
   def hash_password(password: str) -> str:
       import hashlib

       password_bytes = password.encode('utf-8')

       if len(password_bytes) > 72:
           # Pre-hash with SHA-256 for very long passwords
           password = hashlib.sha256(password_bytes).hexdigest()

       # Use explicit bcrypt configuration
       return bcrypt.using(ident="2b", rounds=12).hash(password)
   ```

**Why it works:** `bcrypt.using()` creates a properly configured hasher that avoids internal passlib issues.

---

### Issue 2: NextAuth returns {"detail":"Not Found"}

**Symptoms:** Login redirects to error page with "Not Found" message

**Root Cause:** `vercel.json` proxies ALL `/api/*` requests to Railway, including NextAuth routes

**Solution:**

Change `vercel.json` to only proxy backend routes:

```json
{
  "rewrites": [
    {
      "source": "/api/v1/:path*",  // ✅ Specific
      "destination": "https://your-backend.railway.app/api/v1/:path*"
    }
  ]
}
```

**Why it works:** NextAuth routes (`/api/auth/*`) stay on Vercel, only backend API routes (`/api/v1/*`) get proxied.

---

### Issue 3: Railway DATABASE_URL Error

**Symptoms:**
- Error: `database "railway  ← As a REFERENCE" does not exist`
- Connection errors despite correct DATABASE_URL

**Root Cause:**
1. Typed `${{Postgres.DATABASE_URL}}` as literal text instead of using Reference
2. Set individual `DB_*` variables incorrectly (e.g., `DB_HOST` = full connection string)

**Solution:**

1. **Delete** all individual `DB_*` variables (DB_HOST, DB_NAME, DB_USER, etc.)
2. **Add** `DATABASE_URL` using Railway's **Reference** feature:
   - Click "New Variable"
   - Select "Add Reference"
   - Choose: `Postgres` → `DATABASE_URL`

**Why it works:** Railway's References inject the actual connection string at runtime.

---

### Issue 4: Tables Don't Exist

**Symptoms:** Error: `relation "users" does not exist`

**Root Cause:** Database tables not created

**Solution:**

**Option 1** (Quick - Development):
```bash
# Set in Railway environment variables
APP_ENV=development
```
This auto-creates tables on startup.

**Option 2** (Proper - Production):
```bash
# Run Alembic migrations
railway run alembic upgrade head
```

---

### Issue 5: CORS Errors from Frontend

**Symptoms:** Browser console shows CORS policy errors

**Root Cause:** Backend doesn't allow requests from Vercel domain

**Solution:**

Add to Railway environment variables:
```bash
CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
```

Redeploy Railway service.

**Why it works:** FastAPI CORS middleware (`app/main.py:85`) reads `CORS_ORIGINS` to allow specific domains.

---

## Verification Checklist

### Backend (Railway)

- [ ] Health endpoint returns 200: `/health`
- [ ] API docs accessible: `/api/docs`
- [ ] Registration works: `POST /api/v1/auth/register`
- [ ] Login works: `POST /api/v1/auth/login`
- [ ] Authenticated requests work: `GET /api/v1/auth/me`

### Frontend (Vercel)

- [ ] Landing page loads: `/`
- [ ] NextAuth providers endpoint works: `/api/auth/providers`
- [ ] Signup form works: `/signup`
- [ ] Login form works: `/login`
- [ ] Dashboard accessible after login: `/dashboard`

### Integration

- [ ] Can register new user from Vercel frontend
- [ ] Can login with registered credentials
- [ ] Session persists across page refreshes
- [ ] Can make authenticated API calls to Railway backend

---

## Quick Reference

### Generate Secrets

```bash
# For JWT_SECRET_KEY (Railway)
openssl rand -hex 32

# For NEXTAUTH_SECRET (Vercel)
openssl rand -base64 32
```

### Test Endpoints

```bash
# Railway Backend
BACKEND_URL="https://claude-code-projects-production.up.railway.app"

# Register
curl -X POST "$BACKEND_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","country":"US"}'

# Login
curl -X POST "$BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get user (requires access_token from login)
curl -X GET "$BACKEND_URL/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### Useful Railway Commands

```bash
# Link to project
railway link -p 786b11ae-cdbd-461b-9b96-01050878c6c4

# Check status
railway status

# View logs
railway logs

# Deploy
railway up -d

# Set environment variable
railway variables set KEY=value
```

---

## Project Structure

```
claude-code-projects/
├── app/                          # FastAPI backend
│   ├── api/v1/auth.py           # Authentication endpoints
│   ├── main.py                  # FastAPI app + CORS config
│   ├── database.py              # SQLAlchemy setup
│   └── models/user.py           # User model
├── meal-planner-ui/             # Next.js frontend
│   ├── src/app/
│   │   ├── api/auth/[...nextauth]/route.ts  # NextAuth config
│   │   ├── login/page.tsx       # Login page
│   │   └── signup/page.tsx      # Signup page
│   └── vercel.json              # Vercel proxy config
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Railway deployment
└── railway.toml                 # Railway config
```

---

## Support

For issues not covered here:
- Check Railway logs: `railway logs`
- Check Vercel function logs: Dashboard → Deployments → Functions
- Review `app/main.py:app/main.py` CORS configuration
- Review `meal-planner-ui/vercel.json` proxy configuration

---

**Last Updated:** 2025-11-18
**Version:** 1.0
**Status:** ✅ Production Ready
