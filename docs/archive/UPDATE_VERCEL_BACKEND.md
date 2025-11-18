# Update Vercel to Use Working Railway Backend

## Current Status

✅ **Railway Backend**: Working correctly at `https://claude-code-projects-production.up.railway.app`
✅ **Authentication**: Registration, login, and JWT tokens all working
❌ **Vercel Frontend**: Still pointing to old/broken backend

## What Needs to Change

Vercel frontend needs to use the correct Railway backend URL.

---

## Option 1: Update via Vercel Dashboard (Recommended)

### Step 1: Go to Vercel Project Settings

https://vercel.com/the-raedical-cos-projects/claude-code-projects/settings/environment-variables

### Step 2: Update NEXT_PUBLIC_API_URL

Find the `NEXT_PUBLIC_API_URL` environment variable and update it to:

```
https://claude-code-projects-production.up.railway.app
```

**Important**: Make sure this is set for **Production**, **Preview**, and **Development** environments.

### Step 3: Redeploy

After updating the environment variable:

1. Go to the **Deployments** tab
2. Find the latest deployment
3. Click the "..." menu → **Redeploy**
4. Wait for deployment to complete

---

## Option 2: Update via Vercel CLI

### Step 1: Login to Vercel

```bash
vercel login
```

### Step 2: Link to Project

```bash
cd meal-planner-ui
vercel link
```

Select:
- Scope: **the-raedical-cos-projects**
- Link to existing project: **Yes**
- Project name: **claude-code-projects**

### Step 3: Update Environment Variable

```bash
vercel env add NEXT_PUBLIC_API_URL production
```

When prompted, enter:
```
https://claude-code-projects-production.up.railway.app
```

Repeat for preview and development:
```bash
vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_API_URL development
```

### Step 4: Redeploy

```bash
vercel --prod
```

---

## Verification

After Vercel redeploys, test the signup page:

1. Go to: https://claude-code-projects-j5cj1eqbd-the-raedical-cos-projects.vercel.app/signup

2. Fill in:
   - Email: your-email@example.com
   - Password: testpassword123

3. Click "Sign Up"

4. **Expected**: Successful signup, redirected to dashboard

5. **If successful**: Try logging in at `/login` with the same credentials

---

## Current Vercel Deployment

- Production URL: `https://claude-code-projects-j5cj1eqbd-the-raedical-cos-projects.vercel.app`
- Project: `claude-code-projects`
- Scope: `the-raedical-cos-projects`

---

## What Was Fixed

The bcrypt password hashing bug is now resolved with:

1. **Explicit bcrypt dependency**: `bcrypt==4.0.1` in requirements.txt
2. **Configured bcrypt hasher**: `bcrypt.using(ident="2b", rounds=12).hash(password)`

See `BCRYPT_FIX_SUMMARY.md` for technical details.
