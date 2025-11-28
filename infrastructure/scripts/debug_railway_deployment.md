# Railway Deployment Debug Checklist

## Issue: Old Code Still Running After Redeploy

The password hashing bug is still present, which means Railway is deploying old code.

---

## Step 1: Verify GitHub Connection

In Railway dashboard:

1. **Click your FastAPI service**
2. **Check the "Deployments" tab**:
   - Look at the most recent deployment
   - What is the **commit hash**?
   - What is the **commit message**?

3. **Expected commit** (our fix):
   ```
   Commit: 0a36ffa
   Message: "fix: Correct bcrypt password hashing to use string input"
   Date: 2025-11-18 09:35
   ```

4. **If you see a different commit**:
   - Railway is not pulling from the correct branch
   - Go to Settings → Source
   - Verify branch is set to `claude/main`

---

## Step 2: Check Source Configuration

In Railway dashboard → FastAPI service → **Settings** → **"Source"** section:

### What you should see:

```
Source Type: GitHub
Repository: davidraehles/claude-code-projects
Branch: claude/main  ← CHECK THIS!
Root Directory: (empty or /)
```

### If Source shows "Empty Service" or "No Source":

**You haven't connected GitHub yet!** Do this:

1. Click **"Connect Repo"** button
2. Authorize Railway to access your GitHub
3. Select: `davidraehles/claude-code-projects`
4. Select branch: `claude/main`
5. Click **"Connect"**

Railway will immediately start building from GitHub.

---

## Step 3: Check Build Configuration

In Railway dashboard → FastAPI service → **Settings** → **"Build"** section:

### Expected settings:

```
Builder: Dockerfile
Dockerfile Path: Dockerfile
Root Directory: (empty)
Build Command: (empty - Dockerfile handles it)
Watch Paths: (empty - watches all files)
```

---

## Step 4: Force Rebuild from Latest Code

If GitHub is connected but deploying wrong commit:

1. **Go to Settings → scroll to bottom**
2. **Find "Danger Zone"**
3. **Click "Clear Build Cache"**
4. **Go back to Deployments tab**
5. **Click "Deploy" → "Deploy Latest"**

This forces Railway to pull fresh code from GitHub.

---

## Step 5: Check Deployment Logs

In Railway dashboard → **Deployments** tab:

1. **Click the latest deployment**
2. **Look at Build logs**:
   - Does it show pulling from GitHub?
   - Does it show building Dockerfile?
   - Any errors?

3. **Look at Deploy logs**:
   - Does it show "Starting server..."?
   - Any Python errors?
   - Database connection successful?

---

## Quick Verification Commands

### Check what commit Railway deployed:

Look in Railway deployment details for:
```
Building commit: [COMMIT_HASH]
```

### Check what commit has our fix:

```bash
git log --oneline | grep "bcrypt"
```

Should show:
```
0a36ffa fix: Correct bcrypt password hashing to use string input
```

### Check if Railway is pulling from correct branch:

In Railway dashboard, the deployment should show:
```
Branch: claude/main
Commit: 0a36ffa (or later)
```

---

## Common Issues & Solutions

### Issue 1: Railway Not Connected to GitHub

**Symptom**: Deployments tab shows "Manual deployment" or old commits

**Solution**:
- Settings → Source → Connect to GitHub
- Select repo and branch
- Click Connect

### Issue 2: Wrong Branch Selected

**Symptom**: Deploying but from wrong branch (not claude/main)

**Solution**:
- Settings → Source → Change branch to `claude/main`
- Click Deploy Latest

### Issue 3: Cached Old Build

**Symptom**: GitHub connected but still deploying old code

**Solution**:
- Settings → Danger Zone → Clear Build Cache
- Deployments → Deploy Latest

### Issue 4: Dockerfile Not Found

**Symptom**: Build fails with "Dockerfile not found"

**Solution**:
- Verify Dockerfile exists at repo root
- Check "Root Directory" is empty in settings
- Dockerfile path should be just "Dockerfile"

---

## What to Report Back

Please check and report:

1. **Is GitHub connected?** (Yes/No)
   - Settings → Source → What does it say?

2. **What branch is selected?**
   - Should be: `claude/main`

3. **What commit is deployed?**
   - Deployments → Latest → Commit hash
   - Should be: `0a36ffa` or later

4. **Any errors in logs?**
   - Deployments → Click deployment → Any red errors?

---

## Next Steps

Once you verify the above, we'll know if:
- ✅ GitHub is connected → Just need to wait for build
- ❌ GitHub not connected → Need to connect it
- ❌ Wrong branch → Need to change to claude/main
- ❌ Build errors → Need to fix errors
