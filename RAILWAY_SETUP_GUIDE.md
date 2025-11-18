# Railway Setup Guide - Connect FastAPI to GitHub & Postgres

## Step 1: Connect FastAPI Service to GitHub Repository

### In Railway Dashboard:

1. **Go to your Railway project**: https://railway.app/dashboard
   - You should see your new FastAPI service

2. **Click on the FastAPI service** (the one you just created from template)

3. **Connect to GitHub**:
   - Click **"Settings"** (gear icon) in the service
   - Scroll to **"Source"** section
   - Click **"Connect to GitHub"** or **"Change Source"**
   - Select your repository: **`davidraehles/claude-code-projects`**
   - Select branch: **`claude/main`** (or `main` if that's your main branch)
   - Click **"Connect"**

4. **Configure Build Settings**:
   - Still in Settings → **"Build"** section
   - **Builder**: Should auto-detect as "Dockerfile"
   - **Dockerfile Path**: `Dockerfile` (should be at root)
   - **Build Command**: Leave empty (Dockerfile handles it)
   - **Start Command**: Leave empty (Dockerfile has CMD)

5. **Set Root Directory** (if needed):
   - If your app is at the root, leave **"Root Directory"** blank
   - If Railway asks, the root should be `/` or empty

---

## Step 2: Connect FastAPI to PostgreSQL Database

### Option A: Use Existing Postgres Service

If you already have a Postgres service in Railway:

1. **In your FastAPI service Settings**:
   - Go to **"Variables"** tab
   - Look for **"Add Reference"** or **"New Variable"**

2. **Add DATABASE_URL from Postgres**:
   - Click **"Add Reference Variable"**
   - Select your **Postgres service**
   - Choose variable: **`DATABASE_URL`**
   - This will automatically link your FastAPI to Postgres

3. **The DATABASE_URL will look like**:
   ```
   postgresql://postgres:PASSWORD@containers-HOST:PORT/railway
   ```

### Option B: Create New Postgres Service

If you don't have Postgres yet:

1. **In your Railway project dashboard**:
   - Click **"+ New Service"**
   - Select **"Database"**
   - Choose **"PostgreSQL"**
   - Click **"Add PostgreSQL"**

2. **Wait for it to provision** (30 seconds)

3. **Connect FastAPI to new Postgres**:
   - Follow "Option A" steps above
   - Add DATABASE_URL reference from the new Postgres service

---

## Step 3: Configure Required Environment Variables

In your **FastAPI service** → **Variables** tab, add these:

### Required Variables:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `DATABASE_URL` | (Reference from Postgres) | Auto-set when you add reference |
| `JWT_SECRET_KEY` | (Generate secret) | See below for generation |
| `SECRET_KEY` | (Generate secret) | See below for generation |
| `APP_ENV` | `production` | Set environment |
| `CORS_ORIGINS` | Your Vercel URL | e.g., `https://your-app.vercel.app` |

### Generate Secrets:

Run this locally to generate secure keys:
```bash
# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste as variables in Railway.

### Optional Variables (can use defaults):

| Variable Name | Default Value | Notes |
|---------------|---------------|-------|
| `API_HOST` | `0.0.0.0` | Keep default |
| `API_PORT` | `8000` | Railway sets PORT automatically |
| `LOG_LEVEL` | `INFO` | Can set to `DEBUG` for troubleshooting |

---

## Step 4: Set Up Deployment Triggers

In **FastAPI service Settings** → **"Deploys"** section:

1. **Enable Auto Deploy**:
   - Toggle **"Auto Deploy"** to ON
   - This will redeploy when you push to GitHub

2. **Watch Settings**:
   - **Watch Paths**: Leave blank (watches all)
   - **Ignore Paths**: Can add `meal-planner-ui/**` to ignore frontend changes

---

## Step 5: Trigger First Deployment

After connecting GitHub:

1. **Railway should automatically detect and deploy**
   - Watch the **"Deployments"** tab
   - You'll see build logs in real-time

2. **Or manually trigger**:
   - Click **"Deploy"** button
   - Select **"Deploy Latest"**

3. **Monitor deployment**:
   ```bash
   # From your local terminal
   bash scripts/watch_deployment.sh
   ```

---

## Step 6: Configure Health Check (Important!)

In **FastAPI service Settings** → **"Health Check"** section:

1. **Health Check Path**: `/health`
2. **Health Check Timeout**: `100` seconds
3. **Restart Policy**: `On Failure`
4. **Max Retries**: `10`

This matches your `railway.toml` configuration.

---

## Step 7: Verify Everything Works

### Check 1: Service is Running
```bash
curl https://claude-code-projects-production.up.railway.app/health
```
Expected: `{"status":"healthy",...}`

### Check 2: Database Connection
```bash
curl https://claude-code-projects-production.up.railway.app/
```
Expected: `{"message":"Recipe & Meal Planning API",...}`

### Check 3: New Code Deployed (Password Fix)
```bash
bash scripts/check_railway_status.sh
```
Expected: `✅ NEW CODE DEPLOYED`

### Check 4: Full Auth Flow
```bash
bash scripts/test_auth_flow.sh
```
Expected: All tests pass ✅

---

## Troubleshooting

### Issue: Build Fails

**Check**:
- Dockerfile exists at repository root
- requirements.txt exists and is valid
- Railway has access to your GitHub repo

**View logs**:
- Railway dashboard → Deployments tab → Click failed deployment

### Issue: App Crashes on Startup

**Common causes**:
1. Missing DATABASE_URL
2. Database not accessible
3. Wrong Python version

**Check logs**:
- Railway dashboard → Deployments tab → Runtime logs

### Issue: Database Connection Error

**Fix**:
1. Verify Postgres service is running (green status)
2. Check DATABASE_URL is set in FastAPI service variables
3. Check DATABASE_URL format:
   ```
   postgresql://USER:PASSWORD@HOST:PORT/DATABASE
   ```

### Issue: Old Code Still Running After Deploy

**Try**:
1. Hard refresh: Click "Redeploy" in Railway
2. Check branch is correct (should be `claude/main`)
3. Check latest commit hash in Railway matches GitHub
4. Force rebuild: Railway Settings → "Clear Build Cache"

---

## Quick Reference: Railway Dashboard Navigation

```
Railway Project Dashboard
├── FastAPI Service (click here)
│   ├── Deployments (view build/deploy logs)
│   ├── Variables (set DATABASE_URL, secrets)
│   ├── Settings
│   │   ├── Source (GitHub connection)
│   │   ├── Build (Dockerfile settings)
│   │   ├── Deploy (auto-deploy settings)
│   │   └── Health Check (set /health endpoint)
│   └── Metrics (CPU, memory, requests)
│
└── PostgreSQL Service
    ├── Data (database tables)
    ├── Variables (DATABASE_URL is here)
    └── Metrics
```

---

## Expected Timeline

After connecting GitHub:

```
0:00 - GitHub connected, auto-deploy triggered
0:30 - Docker build starts
2:00 - Docker build completes
2:30 - Deployment starts
3:00 - Health check passes
3:30 - ✅ Service is live with new code!
```

---

## Verification Checklist

After setup, confirm:

- [ ] GitHub repository connected
- [ ] Branch set to `claude/main` (or your main branch)
- [ ] Postgres DATABASE_URL reference added
- [ ] JWT_SECRET_KEY and SECRET_KEY set
- [ ] CORS_ORIGINS set to Vercel URL
- [ ] Auto-deploy enabled
- [ ] Health check path set to `/health`
- [ ] Latest deployment successful
- [ ] Health endpoint returns 200 OK
- [ ] Password hashing bug fixed (no bcrypt error)
- [ ] Can register new users
- [ ] Can login with test user

---

## Next Steps After Setup

1. **Seed test user**:
   ```bash
   # Need Railway CLI for this, or do it via API
   railway run python scripts/seed_test_user.py
   ```

2. **Run full test suite**:
   ```bash
   bash scripts/test_auth_flow.sh
   ```

3. **Update Vercel frontend** (if needed):
   - Verify NEXT_PUBLIC_API_URL points to Railway URL
   - Redeploy Vercel: `cd meal-planner-ui && vercel --prod`

4. **Test end-to-end**:
   - Visit your Vercel app
   - Try signup/login
   - Verify dashboard loads

---

## Need Help?

Run this to check current status:
```bash
bash scripts/check_railway_status.sh
```

Watch deployment progress:
```bash
bash scripts/watch_deployment.sh
```

Check Railway logs in dashboard:
- Click service → Deployments → View Logs
