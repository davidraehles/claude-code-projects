# Railway Deployment Error Fix

## Error Diagnosis

```
ValueError: invalid literal for int() with base 10: ''
```

**Issue**: The DATABASE_URL has an empty or malformed port number.

This happens when:
1. DATABASE_URL is not properly set as a reference
2. DATABASE_URL format is incorrect
3. Port is missing from the URL

---

## Solution: Fix DATABASE_URL Configuration

### In Railway Dashboard → FastAPI Service → Variables:

#### Option 1: Use Reference (Recommended)

1. **Remove** the current `DATABASE_URL` variable if it exists
2. Click **"+ New Variable"** → **"Add Reference"**
3. Select your **PostgreSQL** service
4. Choose: **`DATABASE_URL`**
5. Click **"Add"**

This automatically gets the correct URL from Postgres.

#### Option 2: Manual Configuration (If Reference Doesn't Work)

If you need to manually set it, the format should be:

```
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

Example:
```
postgresql://postgres:password123@containers-us-west-123.railway.app:5432/railway
```

**To get the correct values**:
1. Go to **PostgreSQL service** → **Variables** tab
2. Look for:
   - `PGUSER` (usually: postgres)
   - `PGPASSWORD`
   - `PGHOST`
   - `PGPORT` (usually: 5432 or similar)
   - `PGDATABASE` (usually: railway)

3. Construct the URL:
   ```
   postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}
   ```

---

## About Redis

### Do You Need Redis? (Probably Not Yet)

According to your spec, Redis is:
- ⏳ **Optional for Phase 1** (your current phase)
- ✅ **Required for Phase 2+** (event bus, caching)

### If You Created Redis Service:

**For Now**: You can ignore it. The app doesn't require Redis yet.

**For Later**: When you need it, add these variables:
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD` (if set)

Or as a reference from Redis service.

### If Redis Connection Is Failing:

Check `app/main.py` around line 45-52. It tries to connect to Redis but should handle failures gracefully:

```python
try:
    event_bus = get_event_bus()
    await event_bus.connect()
    print("✅ Event bus connected")
except Exception as e:
    print(f"⚠️  Warning: Could not connect to Redis event bus: {e}")
    print("   Application will continue without event bus functionality")
```

The app should continue running even if Redis fails.

---

## Step-by-Step Fix

### 1. Check Current Variables

In **FastAPI service** → **Variables** tab, what do you see?

- `DATABASE_URL` = ?

Is it:
- [ ] A reference (shows "Reference: PostgreSQL → DATABASE_URL")
- [ ] A raw value (shows `postgresql://...`)
- [ ] Empty or malformed

### 2. Fix DATABASE_URL

Follow **Option 1** above (use reference).

### 3. Remove Redis Variables (If Causing Issues)

If you have `REDIS_HOST`, `REDIS_PORT`, etc. and they're causing issues:
- **Remove them** for now
- The app will run without Redis (it's optional for Phase 1)

### 4. Verify Required Variables Are Set

Your FastAPI service should have:
- ✅ `DATABASE_URL` (reference from PostgreSQL)
- ✅ `JWT_SECRET_KEY` (generated secret)
- ✅ `SECRET_KEY` (generated secret)
- ✅ `APP_ENV` = `production`
- ✅ `CORS_ORIGINS` = Your Vercel URL (or `*` for now)

### 5. Trigger Redeploy

After fixing variables:
- Railway should auto-redeploy
- Or click **"Redeploy"** manually
- Wait 2-3 minutes

---

## How to Check DATABASE_URL Format

### In PostgreSQL Service:

1. Go to **PostgreSQL service** → **Connect** tab
2. Look for **"Database URL"** or **"Connection String"**
3. It should look like:
   ```
   postgresql://postgres:password@host.railway.app:5432/railway
   ```

### Copy This Exact URL

If reference doesn't work, copy this URL and paste it as `DATABASE_URL` in FastAPI service.

---

## About CORS_ORIGINS

The `CORS_ORIGINS` variable controls which frontend URLs can access your API.

### For Development/Testing:

```
CORS_ORIGINS=*
```

This allows all origins (not secure for production but fine for testing).

### For Production:

```
CORS_ORIGINS=https://your-app.vercel.app
```

Or multiple origins:
```
CORS_ORIGINS=https://your-app.vercel.app,https://custom-domain.com
```

**Important**: No spaces between URLs!

---

## Common Database Connection Issues

### Issue 1: Empty Port

**Error**: `ValueError: invalid literal for int() with base 10: ''`

**Cause**: DATABASE_URL is missing port or malformed

**Fix**: Use reference from PostgreSQL service

### Issue 2: Connection Refused

**Error**: `Connection refused` or `could not connect to server`

**Cause**:
- Wrong host/port
- Postgres service not running
- Network issue

**Fix**:
- Verify PostgreSQL service is running (green status)
- Check DATABASE_URL has correct host
- Wait a minute and try again

### Issue 3: Authentication Failed

**Error**: `password authentication failed`

**Cause**: Wrong username or password in DATABASE_URL

**Fix**: Use reference from PostgreSQL service (auto-updated)

---

## What to Report Back

Please check and tell me:

1. **DATABASE_URL in FastAPI service**:
   - [ ] Is it a reference? (shows "Reference: PostgreSQL → DATABASE_URL")
   - [ ] Is it a raw value? (shows `postgresql://...`)
   - [ ] What does it show?

2. **PostgreSQL service status**:
   - [ ] Running (green)
   - [ ] Failed (red)
   - [ ] Building (yellow)

3. **Do you have Redis service?**
   - [ ] Yes (and it's running)
   - [ ] Yes (but not running)
   - [ ] No

4. **After fixing, what's the deployment error?**
   - Check Railway → FastAPI service → Deployments → Latest → View Logs

---

## Quick Fix Commands

If you want to check from CLI:

```bash
# Check Railway status
railway status

# To view logs, first link to the FastAPI service:
# (run in your terminal, not via me - requires interaction)
railway service

# Then:
railway logs
```

---

## Expected Success

After fixing DATABASE_URL, the deployment should:

✅ Build successfully (1-2 min)
✅ Start successfully (shows "Application started")
✅ Health check passes
✅ No database connection errors in logs

---

Let me know what DATABASE_URL currently shows in your FastAPI service variables! 🔍
