# Deployment Guide

Complete guide for deploying the FastAPI backend on Railway and Next.js frontend on Vercel.

**Production URLs:**
- Frontend: https://claude-code-projects.vercel.app
- Backend: https://claude-code-projects-production.up.railway.app
- API Docs: https://claude-code-projects-production.up.railway.app/api/docs

---

## Quick Start

```bash
# 1. Deploy Backend to Railway
railway link
railway up

# 2. Deploy Frontend to Vercel
cd meal-planner-ui
vercel --prod
```

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│              User Browser (Vercel)                 │
│   https://claude-code-projects.vercel.app          │
└────────────────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
    /api/auth/*              /api/v1/*
  (NextAuth on Vercel)   (Proxied to Railway)
                               │
                 ┌─────────────┴──────────────┐
                 ▼                            ▼
    ┌──────────────────────┐     ┌──────────────────────┐
    │  FastAPI Backend     │────▶│   PostgreSQL DB      │
    │    (Railway)         │     │    (Railway)         │
    └──────────────────────┘     └──────────────────────┘
```

**Stack:**
- Frontend: Next.js 14 + NextAuth.js
- Backend: FastAPI + SQLAlchemy + passlib/bcrypt
- Database: PostgreSQL 15
- Hosting: Vercel (frontend) + Railway (backend + DB)

---

## Railway Backend Setup

### 1. Create Services

In Railway dashboard, create:
1. **PostgreSQL** (from template)
2. **FastAPI** (from GitHub repo)

### 2. Environment Variables

Set in **FastAPI service**:

```bash
# Database (use Reference to Postgres service)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT Authentication
JWT_SECRET_KEY=<openssl rand -hex 32>

# Application
APP_ENV=production

# CORS
CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
```

**Critical:** Use Railway's **Reference** feature for `DATABASE_URL` (don't copy-paste the value).

### 3. Deploy

```bash
# Via CLI
railway up -d

# Or push to GitHub (auto-deploys)
git push origin main
```

### 4. Verify

```bash
# Health check
curl https://your-app.up.railway.app/health

# Test registration
curl -X POST https://your-app.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","country":"US"}'
```

---

## Vercel Frontend Setup

### 1. Connect GitHub

1. Go to Vercel dashboard
2. Import project from GitHub
3. Root directory: `meal-planner-ui`
4. Framework: Next.js (auto-detected)

### 2. Environment Variables

Set in Vercel project settings (all environments):

```bash
# Backend API
NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app

# NextAuth
NEXTAUTH_SECRET=<openssl rand -base64 32>
NEXTAUTH_URL=https://claude-code-projects.vercel.app
```

### 3. Configuration

Ensure `meal-planner-ui/vercel.json` has:

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

**Important:** Only proxy `/api/v1/*` (not `/api/*`) to avoid breaking NextAuth routes.

### 4. Deploy

```bash
cd meal-planner-ui
vercel --prod
```

---

## Common Issues & Fixes

### Issue 1: "password cannot be longer than 72 bytes"

**Symptom:** Registration fails even for short passwords

**Cause:** Incorrect bcrypt usage in passlib

**Fix:** Use configured hasher in `app/api/v1/auth.py`:

```python
def hash_password(password: str) -> str:
    import hashlib

    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        password = hashlib.sha256(password_bytes).hexdigest()

    return bcrypt.using(ident="2b", rounds=12).hash(password)
```

**Why:** `bcrypt.using()` creates a properly configured hasher.

---

### Issue 2: NextAuth "Not Found" Error

**Symptom:** Login redirects to `{"detail":"Not Found"}`

**Cause:** `vercel.json` proxies ALL `/api/*` to Railway

**Fix:** Change proxy to only `/api/v1/*`:

```json
"source": "/api/v1/:path*"  // Not "/api/:path*"
```

**Why:** NextAuth needs `/api/auth/*` to stay on Vercel.

---

### Issue 3: Railway DATABASE_URL Error

**Symptom:** Connection errors despite setting `DATABASE_URL`

**Cause:** Typed `${{Postgres.DATABASE_URL}}` as literal text

**Fix:** Use Railway's **Reference** feature:
1. Click "New Variable"
2. Select "Add Reference"
3. Choose: `Postgres` → `DATABASE_URL`

**Why:** References inject the actual value at runtime.

---

### Issue 4: Tables Don't Exist

**Symptom:** `relation "users" does not exist`

**Cause:** Database tables not created

**Quick Fix:**
```bash
# In Railway env vars
APP_ENV=development  # Auto-creates tables
```

**Proper Fix:**
```bash
railway run alembic upgrade head
```

---

### Issue 5: CORS Errors

**Symptom:** Browser CORS policy errors

**Cause:** Backend doesn't allow Vercel domain

**Fix:** Add to Railway env vars:
```bash
CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
```

---

## Verification Checklist

### Backend
- [ ] Health endpoint: `GET /health`
- [ ] API docs: `/api/docs`
- [ ] Register: `POST /api/v1/auth/register`
- [ ] Login: `POST /api/v1/auth/login`
- [ ] Auth: `GET /api/v1/auth/me`

### Frontend
- [ ] Landing page: `/`
- [ ] NextAuth: `/api/auth/providers`
- [ ] Signup: `/signup`
- [ ] Login: `/login`
- [ ] Dashboard: `/dashboard`

### Integration
- [ ] Can register from Vercel
- [ ] Can login with credentials
- [ ] Session persists
- [ ] Can call authenticated endpoints

---

## Quick Reference

### Generate Secrets

```bash
# JWT_SECRET_KEY (Railway)
openssl rand -hex 32

# NEXTAUTH_SECRET (Vercel)
openssl rand -base64 32
```

### Test Endpoints

```bash
BACKEND="https://claude-code-projects-production.up.railway.app"

# Register
curl -X POST "$BACKEND/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","country":"US"}'

# Login
curl -X POST "$BACKEND/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Railway CLI

```bash
# Link project
railway link

# Deploy
railway up -d

# View logs
railway logs

# Set variable
railway variables set KEY=value
```

---

## File Structure

```
claude-code-projects/
├── app/                     # FastAPI backend (Railway)
│   ├── api/v1/auth.py      # Authentication
│   ├── main.py             # FastAPI app + CORS
│   └── database.py         # SQLAlchemy
├── meal-planner-ui/        # Next.js frontend (Vercel)
│   ├── src/app/
│   │   ├── api/auth/[...nextauth]/route.ts  # NextAuth
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   └── vercel.json         # Proxy config
├── requirements.txt        # Python deps
├── Dockerfile             # Railway build
└── railway.toml          # Railway config
```

---

**Last Updated:** 2025-11-18
**Status:** ✅ Production Ready
