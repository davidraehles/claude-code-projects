# Railway Fresh Setup Guide - Step by Step

Starting from scratch with your Railway project. Follow these steps in order.

---

## Overview

We'll create:
1. **PostgreSQL Database** (for data storage)
2. **FastAPI Service** (your backend, connected to GitHub)

Then configure them to work together.

---

## Step 1: Create PostgreSQL Database

### In Railway Dashboard:

1. Go to: https://railway.app/project/786b11ae-cdbd-461b-9b96-01050878c6c4
2. Click **"+ New Service"** button
3. Select **"Database"**
4. Choose **"PostgreSQL"**
5. Wait ~30 seconds for it to provision

✅ **Done!** Your database is ready.

**Note**: Railway automatically creates a `DATABASE_URL` variable in this service.

---

## Step 2: Create FastAPI Service from GitHub

### In Railway Dashboard:

1. Click **"+ New Service"** button again
2. Select **"GitHub Repo"**
3. If prompted, authorize Railway to access your GitHub
4. Search for: **`davidraehles/claude-code-projects`**
5. Click on your repository to select it

### Railway will ask about configuration:

- **Branch**: Select **`claude/main`**
- **Root Directory**: Leave empty (or `/`)
- Railway will auto-detect the **Dockerfile** ✅

6. Click **"Deploy"**

Railway will start building immediately. This takes 2-3 minutes.

---

## Step 3: Connect FastAPI to PostgreSQL

### In your FastAPI service:

1. Click on the **FastAPI service** (not Postgres)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** → **"Add Reference"**
4. Select your **PostgreSQL** service
5. Choose variable: **`DATABASE_URL`**
6. Click **"Add"**

✅ **Done!** FastAPI can now talk to the database.

---

## Step 4: Add Required Environment Variables

Still in the **FastAPI service** → **Variables** tab:

### Generate Secrets First

Run this on your local machine:
```bash
bash scripts/generate_secrets.sh
```

You'll get output like:
```
JWT_SECRET_KEY=abc123...
SECRET_KEY=xyz789...
```

### Add These Variables in Railway:

Click **"+ New Variable"** for each:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `JWT_SECRET_KEY` | (paste from script) | For JWT tokens |
| `SECRET_KEY` | (paste from script) | For app security |
| `APP_ENV` | `production` | Environment mode |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Your Vercel URL |

**Replace** `https://your-app.vercel.app` with your actual Vercel deployment URL.

### After Adding Variables:

Railway will automatically **redeploy** with the new variables. Wait 2-3 minutes.

---

## Step 5: Get Your Public URL

### In FastAPI service:

1. Go to **"Settings"** → **"Networking"**
2. Railway should have auto-generated a **public domain**
3. It looks like: `https://web-production-xxxx.up.railway.app`
4. **Copy this URL** - we'll need it!

If there's no domain:
- Click **"Generate Domain"**
- Railway will create one

---

## Step 6: Verify Deployment

### Check Health Endpoint

Replace `YOUR-URL` with your Railway URL:

```bash
curl https://YOUR-URL/health
```

**Expected response**:
```json
{"status":"healthy","version":"1.0.0","service":"recipe-meal-planning-api"}
```

### Test Password Fix (The Important One!)

```bash
curl -X POST https://YOUR-URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","country":"US"}'
```

**Expected response** (SUCCESS!):
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**NOT expected** (OLD BUG):
```json
{"error":"Internal server error","message":"password cannot be longer than 72 bytes..."}
```

If you get the access_token response, **THE PASSWORD FIX IS WORKING!** 🎉

---

## Step 7: Seed Test User

Now that the backend works, create a test user:

```bash
# Set the DATABASE_URL to your Railway Postgres URL
# You can find it in Railway → PostgreSQL service → Variables → DATABASE_URL

# Option 1: Using Railway CLI
railway run python scripts/seed_test_user.py

# Option 2: Using the register endpoint (if it works)
curl -X POST https://YOUR-URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","country":"US"}'
```

---

## Step 8: Update Vercel Frontend

Your frontend needs to point to the new Railway URL.

### In Vercel Dashboard:

1. Go to your **meal-planner-ui** project
2. Go to **Settings** → **Environment Variables**
3. Find: `NEXT_PUBLIC_API_URL`
4. Update value to: **Your new Railway URL** (from Step 5)
5. Click **"Save"**
6. Go to **Deployments** tab
7. Click **"Redeploy"** on the latest deployment

---

## Step 9: Test Full Authentication Flow

Once Vercel is redeployed:

### From Local Machine:

```bash
# Set the API URL
export API_URL=https://YOUR-RAILWAY-URL

# Run full test suite
bash scripts/test_auth_flow.sh
```

### From Browser:

1. Visit your Vercel app
2. Click **"Sign Up"**
3. Enter email and password
4. Should successfully register and log in
5. Should redirect to dashboard

---

## Final Checklist

### Railway Services:

- [ ] **PostgreSQL** service running (green status)
- [ ] **FastAPI** service running (green status)
- [ ] FastAPI connected to GitHub (`claude/main` branch)
- [ ] FastAPI has `DATABASE_URL` reference
- [ ] FastAPI has `JWT_SECRET_KEY`, `SECRET_KEY`, `APP_ENV`, `CORS_ORIGINS`
- [ ] FastAPI has public domain
- [ ] Latest deployment shows commit `0a36ffa` or later
- [ ] Health endpoint returns 200 OK
- [ ] Register endpoint works (no bcrypt error)

### Vercel:

- [ ] `NEXT_PUBLIC_API_URL` set to Railway URL
- [ ] Redeployed after changing URL
- [ ] Frontend can connect to backend

### Testing:

- [ ] Registration works
- [ ] Login works
- [ ] Dashboard loads
- [ ] No password hashing errors

---

## Common Issues

### Issue: Build Fails

**Check**:
- Dockerfile exists at repository root
- requirements.txt is valid
- Railway selected correct branch (`claude/main`)

**Solution**:
- View build logs in Railway → Deployments → Click failed build
- Check for missing dependencies or syntax errors

### Issue: App Crashes on Start

**Check**:
- All environment variables are set
- DATABASE_URL is correct
- Logs show database connection error?

**Solution**:
- Railway → Deployments → View runtime logs
- Verify DATABASE_URL reference is correct

### Issue: "Module not found" Error

**Possible cause**: Railway is using wrong Python version or missing deps

**Solution**:
- Check Dockerfile specifies correct Python version
- Verify requirements.txt includes all packages
- Clear build cache: Settings → Danger Zone → Clear Cache

---

## Success Indicators

✅ Railway shows both services as **"Active"** (green)
✅ FastAPI deployment shows **commit 0a36ffa**
✅ Health endpoint returns **200 OK**
✅ Register endpoint returns **access_token** (not bcrypt error)
✅ Vercel frontend can **register new users**
✅ Vercel frontend can **login**
✅ Dashboard loads after login

---

## What We'll Have When Done

```
┌─────────────────────────────────────┐
│         VERCEL (Frontend)           │
│   Next.js / React                   │
│   https://your-app.vercel.app       │
└─────────────┬───────────────────────┘
              │
              │ NEXT_PUBLIC_API_URL
              ↓
┌─────────────────────────────────────┐
│    RAILWAY (Backend + Database)     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  FastAPI Service            │   │
│  │  (GitHub: claude/main)      │   │
│  │  Commit: 0a36ffa ✅         │   │
│  │  https://web-xxx.railway... │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│             │ DATABASE_URL          │
│             ↓                       │
│  ┌─────────────────────────────┐   │
│  │  PostgreSQL Database        │   │
│  │  (Users, Recipes, etc.)     │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Time Estimate

- Step 1 (Postgres): 1 minute
- Step 2 (FastAPI): 3-4 minutes (includes build time)
- Step 3-4 (Variables): 2 minutes
- Step 5-6 (Testing): 1 minute
- Step 7 (Seed user): 1 minute
- Step 8 (Vercel update): 2 minutes

**Total: ~10-15 minutes** ⏱️

---

## Ready to Start?

Follow Steps 1-2 first (create services), then tell me:
1. ✅ PostgreSQL created
2. ✅ FastAPI created and building

I'll help you with the rest! 🚀
