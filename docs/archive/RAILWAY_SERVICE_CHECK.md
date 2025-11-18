# Railway Service Configuration Check

## Current Status

✅ **Project Linked**: comfortable-patience (production)
⚠️ **Service**: Not selected (you have multiple services)

---

## What You Need to Do (Dashboard Method - Easier)

### Go to Railway Dashboard

Visit: https://railway.app/project/786b11ae-cdbd-461b-9b96-01050878c6c4

You should see your 3 services:
1. **GitHub Repo** (or similar)
2. **Postgres Docker**
3. **FastAPI** (from GitHub)

---

## For Each Service - Check Configuration

### Service 1: Postgres Docker ✅
**What to check**: Nothing - this is fine

**Expected**:
- Type: PostgreSQL
- Status: Running (green)
- Has DATABASE_URL variable

**Action**: Leave it alone!

---

### Service 2 & 3: FastAPI Services

You likely have **2 FastAPI services**. We need to identify the correct one:

#### The CORRECT FastAPI Service Should Have:

1. **Settings → Source**:
   - ✅ Repository: `davidraehles/claude-code-projects`
   - ✅ Branch: `claude/main`
   - ✅ Builder: Dockerfile

2. **Deployments → Latest Deployment**:
   - ✅ Commit: `0a36ffa` (our password fix)
   - ✅ Status: Success
   - ✅ Date: Today (Nov 18, 2025)

3. **Settings → Networking**:
   - ✅ Has a public domain
   - 📝 **Write down this URL!** (e.g., `https://web-production-xxxx.up.railway.app`)

#### Check Variables Tab:

Does it have these variables?
- [ ] `DATABASE_URL` (reference from Postgres)
- [ ] `JWT_SECRET_KEY` (generated secret)
- [ ] `SECRET_KEY` (generated secret)
- [ ] `APP_ENV` (production)
- [ ] `CORS_ORIGINS` (your Vercel URL)

---

## What to Report Back

Please tell me:

### For the GitHub-connected FastAPI service:

1. **Service Name**: ____________________
2. **Public URL**: ____________________
3. **Latest Commit**: ____________________ (should be 0a36ffa)
4. **Has DATABASE_URL?**: [ ] Yes [ ] No
5. **Has JWT_SECRET_KEY?**: [ ] Yes [ ] No
6. **Has SECRET_KEY?**: [ ] Yes [ ] No
7. **Deployment Status**: [ ] Success [ ] Failed [ ] Building

---

## If Variables Are Missing

### Add DATABASE_URL (Database Connection):
1. Click **Variables** tab
2. Click **"+ New Variable"**
3. Click **"Add Reference"**
4. Select your **Postgres Docker** service
5. Choose **`DATABASE_URL`**
6. Save

### Add Secret Keys:

Run this locally to generate:
```bash
bash scripts/generate_secrets.sh
```

Then add in Railway Variables:
- `JWT_SECRET_KEY` = (paste value)
- `SECRET_KEY` = (paste value)
- `APP_ENV` = `production`
- `CORS_ORIGINS` = (your Vercel URL, e.g., `https://your-app.vercel.app`)

### After Adding Variables:

Railway will automatically redeploy. Wait 2-3 minutes.

---

## Alternative: CLI Method (If You Want)

If you prefer using CLI, run this **in your terminal** (not via me):

```bash
# Select a service interactively
railway service

# After selecting, check variables
railway variables

# Check status
railway status
```

---

## What Happens Next

Once you tell me:
1. ✅ The public URL of the correct FastAPI service
2. ✅ Confirmation that variables are added
3. ✅ Deployment is successful

I will:
1. Test if the password fix is working on that URL
2. Help you update Vercel to point to the correct URL
3. Run full authentication tests
4. Help you clean up the old/duplicate services

---

## Quick Decision Tree

```
Do you see 2 FastAPI services?
├─ YES → Find the one connected to GitHub (claude/main branch)
│         └─ This is the CORRECT one
│
└─ NO (only 1 FastAPI) → That's the one!
                        └─ Make sure it's connected to GitHub
```

---

**Next Step**: Check the dashboard and tell me the **public URL** of your GitHub-connected FastAPI service! 🔍
