# Railway Deployment Fixes

## Issues Identified

### 1. ✅ Alembic Migration "Multiple Head Revisions" - FIXED

**Status:** Already resolved! A merge migration exists at `1f5528e26798_merge_multiple_heads.py`

**What was the problem:**
Two migrations branched from `005_add_dietary_tags`:
- `006_add_delivery_slot_and_unavailable_items`
- `006_create_rate_limit_tables`

This created parallel branches that needed to be merged.

**Solution:**
The merge migration already exists. Railway will automatically apply it on next deployment via:
```bash
alembic upgrade head
```

This runs automatically through the `startCommand` in `railway.toml`.

**Verification:**
After Railway redeploys, check logs for:
```
Running migrations...
INFO  [alembic.runtime.migration] Running upgrade <revision> -> 1f5528e26798, merge_multiple_heads
```

---

### 2. ⚠️ Redis Configuration Error

**Error Message:**
```
wrong number of arguments for requirepass at line 2
```

**Root Cause:**
Railway's Redis service has a malformed configuration file. The error suggests there's a syntax error in the Redis config.

**Impact:**
- Application marks Redis as "degraded" but continues functioning
- Event bus features disabled (agent-to-agent communication)
- Rate limiting falls back to in-memory storage
- **Core features still work!** (Auth, recipes, meal plans, etc.)

---

## Recommended Solutions

### Solution 1: Remove Redis (Recommended for Now)

Redis is optional for your application. Core features work without it.

**Steps:**
1. In Railway dashboard → Your project → Redis service
2. Click "Settings" → "Remove Service"
3. In your backend service → Variables
4. Remove these variables if they exist:
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_DB`
   - `REDIS_URL`

**What you'll lose:**
- Event bus (agent communication) - not actively used
- Distributed rate limiting - falls back to in-memory

**What still works:**
- ✅ Authentication
- ✅ Recipe management
- ✅ Meal planning
- ✅ Waitlist
- ✅ All core API endpoints

---

### Solution 2: Fix Redis Configuration

If you want to keep Redis for future event bus features:

**Option A: Use Railway Redis Plugin**
1. Remove current Redis service
2. Add Redis via Railway's official plugin:
   - Dashboard → New → Database → Redis
3. Railway will automatically set `REDIS_URL` environment variable
4. Update [backend/app/events/bus.py](backend/app/events/bus.py#L31-L48) to use `REDIS_URL`:

```python
def __init__(self):
    """Initialize event bus with Redis connection."""
    # Try to use Railway's REDIS_URL first
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        # Parse Railway Redis URL
        self.redis_url = redis_url
    else:
        # Fall back to individual variables for local dev
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
```

**Option B: Debug Current Redis Service**
1. Check Railway logs for Redis service initialization
2. Look for config file generation errors
3. The issue is likely in how Railway is creating the `redis.conf` file
4. Contact Railway support if the plugin is generating bad config

---

## Additional Fixes Applied

### 3. ✅ Test User Seeding

**Added:** Automatic test user creation on startup

**Location:** [backend/app/main.py](backend/app/main.py) - `lifespan()` function

**How to enable:**
Set environment variable in Railway:
```
SEED_TEST_USER=true
```

**Test credentials:**
- Email: `test@example.com`
- Password: `testpassword123`

---

## Deployment Checklist

### Before Next Railway Deploy:

- [ ] **Alembic:** No action needed - merge migration exists
- [ ] **Redis:** Choose Option 1 or 2 above
- [ ] **Test User:** Add `SEED_TEST_USER=true` to Railway variables
- [ ] **CORS:** Verify `CORS_ORIGINS` includes your Vercel domain
- [ ] **API URL:** Verify Vercel has `NEXT_PUBLIC_API_URL=https://meal-planner.up.railway.app`

### After Deploy:

- [ ] Check Railway logs for successful migration
- [ ] Test signup at Vercel preview URL
- [ ] Verify test user login works
- [ ] Check health endpoint: `curl https://meal-planner.up.railway.app/health`

---

## Current Railway Configuration

**Backend URL:** `https://meal-planner.up.railway.app`

**Required Environment Variables:**
```bash
# Database (automatically set by Railway)
DATABASE_URL=postgresql://...

# Application
APP_ENV=production
SECRET_KEY=<random-string>
JWT_SECRET_KEY=<random-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1

# CORS
CORS_ORIGINS=https://meal-planner-8u0r0nx1t-the-raedical-cos-projects.vercel.app,https://your-domain.vercel.app

# Test User (optional)
SEED_TEST_USER=true

# Redis (optional - see solutions above)
# REDIS_URL=... OR remove completely
```

---

## Testing the Fix

### 1. Test Backend Health
```bash
curl -s https://meal-planner.up.railway.app/health | jq '.'
```

Expected: `status: "healthy"` or `"degraded"` (degraded is OK if Redis removed)

### 2. Test Migrations Applied
```bash
curl -s https://meal-planner.up.railway.app/health | jq '.components.database'
```

Should show: `status: "healthy"`

### 3. Test Signup
1. Go to Vercel preview URL: https://meal-planner-b2cj0bijb-the-raedical-cos-projects.vercel.app/signup
2. Create test account
3. Check browser console for detailed error logs (we added these)

### 4. Test Login
1. Go to: https://meal-planner-b2cj0bijb-the-raedical-cos-projects.vercel.app/login
2. Use test credentials:
   - Email: test@example.com
   - Password: testpassword123

---

## Summary

**Alembic:** ✅ Fixed (merge migration exists, will apply on next deploy)

**Redis:** ⚠️ Needs decision:
- Quick fix: Remove Redis service (app works without it)
- Proper fix: Use Railway Redis plugin with REDIS_URL

**Next Steps:**
1. Choose Redis option (recommend removal for now)
2. Add `SEED_TEST_USER=true` to Railway
3. Redeploy (migrations will apply automatically)
4. Test signup/login on Vercel

**Questions?** Check Railway deployment logs after redeploying.
