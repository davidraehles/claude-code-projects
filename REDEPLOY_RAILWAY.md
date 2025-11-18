# Railway Redeploy Instructions

## The Issue

Railway is still running OLD code (commit before 3ec12af).
The password hashing fix has been pushed to GitHub, but Railway hasn't auto-deployed it yet.

**Latest commit with fix**: `3ec12af - fix: Simplify bcrypt password hashing with SHA-256 pre-hash for long passwords`

---

## How to Manually Redeploy

### Option 1: Redeploy via Railway Dashboard (Fastest)

1. Go to: https://railway.app/project/786b11ae-cdbd-461b-9b96-01050878c6c4

2. Click on your **FastAPI service**

3. Click on the **"Deployments"** tab

4. Click **"Deploy"** button in the top right

5. This will trigger a fresh deployment from the latest code

---

### Option 2: Configure Auto-Deploy from claude/main

If Railway isn't watching the `claude/main` branch:

1. Go to your FastAPI service settings

2. Click **"Source"** or **"GitHub"** section

3. Make sure it's connected to **your GitHub repo**

4. Set the **Branch** to: `claude/main`

5. Enable **"Auto Deploy"**

6. Save settings

Now Railway will auto-deploy whenever you push to `claude/main`.

---

## Verify the Fix Deployed

After redeploying, wait 2-3 minutes, then test:

```bash
curl -X POST https://claude-code-projects-preview.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test-'$(date +%s)'@example.com","password":"testpassword123","country":"US"}'
```

**Success**: Should return `access_token` and `refresh_token`
**Failure**: Returns error about "72 bytes" (means old code still running)

---

## What Changed in the Fix

**Before** (buggy):
```python
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return bcrypt.hash(truncated_password)
```

**After** (correct):
```python
def hash_password(password: str) -> str:
    import hashlib

    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        # For very long passwords, pre-hash with SHA-256
        password = hashlib.sha256(password_bytes).hexdigest()

    return bcrypt.hash(password)
```

For normal passwords like "testpassword123" (15 bytes), it just calls `bcrypt.hash(password)` directly.
