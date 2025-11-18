# Deployment Architecture

## Your Current Setup

```
┌─────────────────────────────────────────────────────────────┐
│                         VERCEL                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Next.js Frontend (meal-planner-ui)            │  │
│  │                                                        │  │
│  │  - Login/Signup pages                                 │  │
│  │  - Dashboard                                          │  │
│  │  - Meal planning UI                                   │  │
│  │                                                        │  │
│  │  Location: /meal-planner-ui/                         │  │
│  │  Framework: Next.js + React                          │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           │ API calls proxied via            │
│                           │ vercel.json rewrites             │
└───────────────────────────┼──────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       RAILWAY                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │      FastAPI Backend (Python)                         │  │
│  │                                                        │  │
│  │  - /api/v1/auth/* (login, register) ← BUG HERE       │  │
│  │  - /api/v1/recipes/*                                 │  │
│  │  - /api/v1/meal-plans/*                              │  │
│  │  - /health                                            │  │
│  │                                                        │  │
│  │  Location: /app/ (root of repo)                      │  │
│  │  Framework: FastAPI                                  │  │
│  │  Deployment: Dockerfile                              │  │
│  │  URL: claude-code-projects-production.up.railway.app │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           │ Database queries                 │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           PostgreSQL Database                         │  │
│  │                                                        │  │
│  │  - Users table (email, password_hash)                │  │
│  │  - Recipes table                                     │  │
│  │  - Meal plans table                                  │  │
│  │                                                        │  │
│  │  Type: Railway Postgres Plugin                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Service Breakdown

### 1. Vercel (Frontend Only)
**What's deployed**: Next.js application (`/meal-planner-ui/`)

**Configuration**:
- `meal-planner-ui/vercel.json`
- `meal-planner-ui/package.json`

**What it does**:
- Serves the user interface
- Proxies API calls to Railway backend
- Handles client-side routing

**Deploy triggers**:
- Automatic on git push
- Manual: `cd meal-planner-ui && vercel --prod`

**Files involved**:
```
meal-planner-ui/
├── src/
│   ├── app/
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx  ← FIXED (endpoint path)
│   │   └── dashboard/page.tsx
│   └── lib/
│       ├── api.ts
│       └── auth.ts
├── vercel.json  ← API proxy config
└── package.json
```

---

### 2. Railway - FastAPI Backend
**What's deployed**: Python FastAPI application (root `/app/`)

**Configuration**:
- `railway.toml` (deployment config)
- `Dockerfile` (build instructions)
- `requirements.txt` (Python dependencies)

**What it does**:
- Handles authentication (login, register)
- Manages recipes, meal plans
- Database operations
- **THIS IS WHERE THE BUG IS** ← auth.py line 73-80

**Deploy triggers**:
- Automatic on git push (should be)
- Manual: Railway dashboard → Redeploy button

**Files involved**:
```
/
├── app/
│   ├── main.py           ← FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py   ← PASSWORD HASHING BUG HERE
│   │       ├── recipes.py
│   │       └── users.py
│   ├── models/
│   │   └── user.py
│   └── database.py
├── Dockerfile            ← Railway uses this to build
├── requirements.txt      ← Python packages
└── railway.toml          ← Railway config
```

---

### 3. Railway - PostgreSQL
**What's deployed**: Managed PostgreSQL database

**What it does**:
- Stores user accounts
- Stores recipes
- Stores meal plans

**Access**: Via `DATABASE_URL` environment variable
**No code deployment needed**: It's just a database service

---

## Where Is The Bug?

```
❌ NOT in Vercel (frontend just calls the API)
❌ NOT in Postgres (database just stores data)
✅ IN RAILWAY FastAPI service

Specifically: /app/api/v1/auth.py line 73-80
```

## What Needs to Redeploy?

**To fix the password bug**:
- ✅ **Railway FastAPI service** ← THIS ONE
- ❌ Vercel (already has the fix)
- ❌ Postgres (nothing to deploy)

## How to Redeploy Railway FastAPI

### Method 1: Railway Dashboard (Easiest)
1. Go to: https://railway.app/dashboard
2. Find project: "claude-code-projects"
3. Click on: **FastAPI service** (the one with the Dockerfile icon)
4. Click: **"Deployments"** tab
5. Click: **"Deploy"** or three dots → **"Redeploy"**

### Method 2: Force via Git
```bash
git commit --allow-empty -m "trigger: force Railway redeploy"
git push origin claude/main
```

### Method 3: Railway CLI
```bash
railway up
```

## Verification After Deployment

```bash
# Run this to check if new code is deployed
bash scripts/check_railway_status.sh

# Expected output:
# ✅ NEW CODE DEPLOYED
```

---

## Current Status

**Vercel Frontend**: ✅ Up to date (endpoint fix deployed)
**Railway Backend**: ❌ Old code (password bug still present)
**Railway Postgres**: ✅ Running fine (not related to bug)

**Fix committed**: ✅ Commit 0a36ffa (2025-11-18 09:35)
**Fix pushed to GitHub**: ✅ Yes
**Fix deployed to Railway**: ❌ Not yet (waiting for deployment)

---

## Next Action

**Go to Railway dashboard and manually redeploy the FastAPI service.**

URL: https://railway.app/dashboard
