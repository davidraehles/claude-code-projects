# Redis Service Setup Guide for Railway

## When Do You Need Redis?

According to your project specs:

- ⏳ **Phase 1 (Current)**: Redis is **OPTIONAL** - Your app works without it
- ✅ **Phase 2+**: Redis is **REQUIRED** - For event bus and caching

### Current Status:
Your app is designed to work **without Redis** in Phase 1. The code in `app/main.py` handles Redis connection failures gracefully:

```python
try:
    event_bus = get_event_bus()
    await event_bus.connect()
    print("✅ Event bus connected")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to Redis event bus: {e}")
    print("   Application will continue without event bus functionality")
```

So you can skip Redis for now if you want!

---

## Option 1: Skip Redis (Recommended for Now)

### What You Get:
✅ User authentication (login/register)
✅ Recipe management
✅ Meal planning
✅ All Phase 1 features

### What You Don't Get (Phase 2 features):
⏳ Event bus for agent communication
⏳ Background task processing
⏳ Caching

### Decision:
**Skip Redis now, add it when you reach Phase 2.**

---

## Option 2: Add Redis Now (Optional)

If you want to set up Redis for future use:

### Step 1: Create Redis Service

In Railway dashboard:

1. Click **"+ New Service"**
2. Select **"Database"**
3. Choose **"Redis"**
4. Wait ~30 seconds for provisioning

### Step 2: Connect FastAPI to Redis

In your **FastAPI service** → **Variables** tab:

#### Option A: Use References (Recommended)

Add these as references:

```
REDIS_HOST=${{Redis.REDIS_PRIVATE_DOMAIN}}
REDIS_PORT=${{Redis.REDIS_PORT}}
```

Railway Redis doesn't require a password by default, but if it has one:
```
REDIS_PASSWORD=${{Redis.REDIS_PASSWORD}}
```

#### Option B: Manual Configuration

If references don't work, get values from **Redis service** → **Variables**:

```
REDIS_HOST=<from Redis.REDIS_PRIVATE_DOMAIN>
REDIS_PORT=6379
REDIS_DB=0
```

### Step 3: Verify Redis Connection

After redeployment, check logs for:

```
✅ Event bus connected
```

If you see:
```
⚠️ Warning: Could not connect to Redis event bus
```

The app will still work, just without event bus functionality.

---

## Redis Configuration Reference

### Required Variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `REDIS_HOST` | `${{Redis.REDIS_PRIVATE_DOMAIN}}` | Internal Railway hostname |
| `REDIS_PORT` | `6379` | Default Redis port |

### Optional Variables:

| Variable | Default | Notes |
|----------|---------|-------|
| `REDIS_DB` | `0` | Database number (0-15) |
| `REDIS_PASSWORD` | (none) | Only if Redis has password |

---

## Verify Redis is Working

### Check from FastAPI Service:

After deployment, look for this in logs:

```bash
# Using Railway CLI (in terminal):
railway service  # Select FastAPI service
railway logs

# Look for:
✅ Event bus connected
```

### Test Redis Connection:

If you have Railway CLI linked:

```bash
# Connect to Redis service
railway service  # Select Redis
railway run redis-cli

# In redis-cli:
ping  # Should return: PONG
```

---

## Troubleshooting Redis Connection

### Issue: "Could not connect to Redis event bus"

**Possible Causes:**
1. Redis service not running
2. Wrong REDIS_HOST or REDIS_PORT
3. Network/firewall issue

**Solutions:**
1. Check Redis service is running (green status)
2. Verify REDIS_HOST is `${{Redis.REDIS_PRIVATE_DOMAIN}}` (use private domain, not public)
3. Check logs for specific error

### Issue: "Connection refused"

**Cause**: Using public domain instead of private

**Fix**: Use `REDIS_PRIVATE_DOMAIN` not `REDIS_URL`

### Issue: "Authentication failed"

**Cause**: Redis requires password but not provided

**Fix**: Add `REDIS_PASSWORD=${{Redis.REDIS_PASSWORD}}`

---

## Current Architecture Without Redis

```
┌─────────────────────────┐
│   Vercel (Frontend)     │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  Railway FastAPI        │
│  - Authentication ✅    │
│  - Recipes ✅          │
│  - Meal Plans ✅       │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  Railway PostgreSQL     │
│  - User data           │
│  - Recipes             │
└─────────────────────────┘
```

This works perfectly for Phase 1!

---

## Future Architecture With Redis (Phase 2+)

```
┌─────────────────────────┐
│   Vercel (Frontend)     │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  Railway FastAPI        │
│  - Authentication ✅    │
│  - Recipes ✅          │
│  - Meal Plans ✅       │
│  - Event Bus ✅        │
└─────┬───────────┬───────┘
      │           │
      ↓           ↓
┌──────────┐  ┌──────────┐
│PostgreSQL│  │  Redis   │
│  (Data)  │  │ (Events) │
└──────────┘  └──────────┘
```

This enables Phase 2 features (agent communication, background jobs).

---

## My Recommendation

### For Now (Phase 1):
**Skip Redis** - Your app doesn't need it yet.

Focus on:
1. ✅ Verify authentication works
2. ✅ Test user registration/login
3. ✅ Update Vercel to use new Railway URL
4. ✅ Test end-to-end flow

### Later (Phase 2):
When you implement:
- Recipe Harvester agents
- Ingredient Intelligence agents
- Event bus communication

Then add Redis using the steps above.

---

## Current Variables (Phase 1 - No Redis)

Your FastAPI service should have:

```
API_HOST=0.0.0.0
API_PORT=8000
APP_ENV=production
CORS_ORIGINS=*
DATABASE_URL=${{Postgres.DATABASE_URL}}
DEBUG=False
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
JWT_SECRET_KEY=2N2kCQUyAfjeBgI1J1mJ_jDAncs7559shWCfUdR50EY
KNUSPR_API_KEY=
LOG_LEVEL=INFO
SECRET_KEY=8Y9nT01iokbKidWpfTr3OUs6K_eo9024wgLOdtG-Zj0
```

**No Redis variables needed!**

---

## Summary

- ✅ **Phase 1 (Now)**: Works without Redis
- ⏳ **Phase 2 (Later)**: Add Redis when needed
- 📖 **This guide**: Ready when you need it

---

## Questions?

- Want to add Redis now? Follow Option 2 steps above.
- Want to skip Redis? Just continue with current setup!
- Redis connection failing? Check troubleshooting section.

The choice is yours! 🚀
