# Railway Cleanup & Configuration Guide

## Your Current Situation

You have **3 services** in Railway:
1. **GitHub Repo** - (unclear purpose)
2. **Postgres Docker** - Database ✅
3. **FastAPI (from GitHub)** - Your app but missing variables ⚠️

You also likely have an **OLD FastAPI service** that's still running at:
`https://claude-code-projects-production.up.railway.app`

---

## Step 1: Identify Which FastAPI Service to Use

### The CORRECT service should be:
- ✅ Connected to **your GitHub repository**
- ✅ Connected to **claude/main branch**
- ✅ Deploying from **Dockerfile**
- ✅ Has a public **URL** (something.railway.app)

### In Railway Dashboard:

Look at your **FastAPI service (from GitHub)** and check:

1. **Settings → Source**:
   - Repository: `davidraehles/claude-code-projects`
   - Branch: `claude/main`
   - Builder: Dockerfile

2. **Settings → Networking**:
   - Does it have a **public domain**?
   - What is the URL? (e.g., `web-production-xxxx.up.railway.app`)

3. **Deployments tab**:
   - What commit is deployed?
   - Should show: `0a36ffa` or later

---

## Step 2: Configure Environment Variables (CRITICAL!)

For your **FastAPI (from GitHub)** service:

### Go to: Variables tab

### Add these variables:

#### 1. Database Connection (Reference)
```
Variable Name: DATABASE_URL
Value: Click "Add Reference" → Select "Postgres Docker" → Choose DATABASE_URL
```

#### 2. Security Keys (Generated values)
Run this script to generate:
```bash
bash scripts/generate_secrets.sh
```

Then add:
```
JWT_SECRET_KEY=<generated-value>
SECRET_KEY=<generated-value>
```

#### 3. Application Settings
```
APP_ENV=production
CORS_ORIGINS=https://your-vercel-app.vercel.app
LOG_LEVEL=INFO
```

---

## Step 3: Get the Correct URL

After adding variables:

1. **In your FastAPI (from GitHub) service**
2. **Go to Settings → Networking**
3. **Copy the public URL** (e.g., `https://web-production-xxxx.up.railway.app`)

This is your **NEW backend URL**!

---

## Step 4: Update Vercel to Use New URL

Your Vercel frontend needs to point to the NEW Railway URL:

### In Vercel Dashboard:

1. Go to your **meal-planner-ui** project
2. Go to **Settings → Environment Variables**
3. Find: `NEXT_PUBLIC_API_URL`
4. Update to: **NEW Railway URL** from Step 3
5. **Redeploy Vercel** (Deployments → Redeploy)

---

## Step 5: Clean Up Old Services (Optional)

You have multiple services. Here's what to keep vs remove:

### KEEP These:
- ✅ **Postgres Docker** - Your database (don't touch!)
- ✅ **FastAPI (from GitHub)** - Your app (once configured)

### REVIEW/REMOVE These:
- ❓ **"GitHub Repo"** service - What is this?
  - If it's not doing anything, you can remove it
  - Settings → Danger Zone → Delete Service

- ❓ **Old FastAPI service** (if exists at claude-code-projects-production.up.railway.app)
  - If you have another FastAPI that's NOT connected to GitHub
  - This is the OLD one causing confusion
  - You can remove it AFTER the new one works

---

## Step 6: Test the New Service

After configuration:

### 1. Check Health Endpoint
```bash
# Replace with YOUR new Railway URL
curl https://web-production-xxxx.up.railway.app/health
```

Expected: `{"status":"healthy",...}`

### 2. Test Password Fix
```bash
# Replace with YOUR new Railway URL
curl -X POST https://web-production-xxxx.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"testpassword123","country":"US"}'
```

Expected: `{"access_token":...}` (SUCCESS!) or `{"detail":"Email already registered"}`
NOT expected: "password cannot be longer than 72 bytes" (OLD BUG)

---

## Visual Guide

### BEFORE (Confusing Setup):
```
Old FastAPI Service (template/old code)
  ↓
Running at: claude-code-projects-production.up.railway.app
  ↓
Vercel points here → WRONG! (has bug)

FastAPI (from GitHub) - No variables
  ↓
Not configured, maybe crashing
  ↓
Nobody is using it
```

### AFTER (Correct Setup):
```
FastAPI (from GitHub) + Environment Variables
  ↓
Connected to: Postgres Docker
  ↓
Running at: web-production-xxxx.up.railway.app
  ↓
Vercel points here → CORRECT! (has fix)
  ↓
✅ Working!
```

---

## Configuration Checklist

For your **FastAPI (from GitHub)** service:

### Variables Tab:
- [ ] `DATABASE_URL` (reference from Postgres Docker)
- [ ] `JWT_SECRET_KEY` (generated)
- [ ] `SECRET_KEY` (generated)
- [ ] `APP_ENV=production`
- [ ] `CORS_ORIGINS=<your-vercel-url>`

### Settings → Source:
- [ ] Repository: `davidraehles/claude-code-projects`
- [ ] Branch: `claude/main`
- [ ] Root Directory: (empty)
- [ ] Builder: Dockerfile

### Settings → Networking:
- [ ] Public domain enabled
- [ ] URL copied for Vercel

### Deployments:
- [ ] Latest deployment successful
- [ ] Commit: `0a36ffa` or later
- [ ] Build logs show no errors
- [ ] Runtime logs show "Application started"

---

## Common Questions

### Q: Which FastAPI service should I use?
**A**: The one connected to **your GitHub repository** with branch `claude/main`

### Q: What about the other FastAPI service?
**A**: If you have an old one, it's running old code. Once the new one works, you can delete the old one.

### Q: Will this delete my data?
**A**: No! Postgres Docker has your data. We're only reconfiguring which FastAPI service uses it.

### Q: What if I mess up?
**A**: Railway services can be deleted and recreated. Your data is safe in Postgres Docker as long as you don't delete that service.

---

## Next Steps After Configuration

1. **Add all environment variables** to FastAPI (from GitHub)
2. **Wait for redeploy** (1-2 minutes)
3. **Test new URL** with health check
4. **Update Vercel** NEXT_PUBLIC_API_URL
5. **Redeploy Vercel**
6. **Test full auth flow**

---

## Need Help?

Tell me:
1. What is the **URL** of your FastAPI (from GitHub) service?
2. Have you added the **DATABASE_URL reference**?
3. Have you added the **secret keys**?
4. Are there any **errors in deployment logs**?
