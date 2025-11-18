# How to Check Railway Deployment Logs

## Current Status

✅ Service is running (health endpoint works)
❌ Auth endpoints failing (internal server error)

This usually means:
- Database connection issue
- Missing environment variable
- Python error in the code

---

## Check Logs in Railway Dashboard

### Step 1: Go to Railway Dashboard

https://railway.app/project/786b11ae-cdbd-461b-9b96-01050878c6c4

### Step 2: Click on FastAPI Service

### Step 3: Click on "Deployments" Tab

### Step 4: Click on the Latest Deployment (should show "Success")

### Step 5: View Logs

You'll see two types of logs:
1. **Build Logs** - Shows Docker build process
2. **Deploy Logs** - Shows runtime errors

**Click "Deploy" logs** to see runtime errors.

---

## What to Look For

### Common Errors:

#### 1. Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Fix**: Check DATABASE_URL is correctly set as reference

#### 2. Missing Environment Variable
```
KeyError: 'JWT_SECRET_KEY'
```
**Fix**: Check all required variables are set

#### 3. Import Error
```
ModuleNotFoundError: No module named 'xyz'
```
**Fix**: Check requirements.txt has all dependencies

#### 4. Redis Connection Error (Can be ignored)
```
⚠️ Warning: Could not connect to Redis event bus
Application will continue without event bus functionality
```
**This is OK** - App works without Redis in Phase 1

---

## Expected Successful Logs

You should see:
```
🚀 Starting Recipe & Meal Planning System...
📦 Creating database tables...
✅ Event bus connected (or warning if no Redis - that's OK)
✅ Application started successfully
```

Then:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## How to Get Logs via CLI

If you prefer CLI:

```bash
# In your terminal (requires interaction):
railway service  # Select FastAPI service
railway logs     # View logs
```

---

## Tell Me What You See

Please check the Deploy logs and tell me:

1. **Any RED errors?** (paste the error message)
2. **Database connection successful?**
3. **Application startup complete?**
4. **Any warnings about missing variables?**

This will help me diagnose exactly what's wrong!
