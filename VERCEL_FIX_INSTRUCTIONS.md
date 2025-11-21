# Vercel Frontend Fix Instructions

**Date**: 2025-11-21
**Issue**: Form inputs not rendering on deployed Vercel site

## Root Cause Analysis

After investigating the frontend code, I found:
- ✅ All form inputs (password, date, etc.) ARE present in the JSX code
- ✅ UI components (Input, Button, Card) are properly implemented
- ✅ Build succeeds locally with no compilation errors
- ✅ Dependencies install successfully

**Conclusion**: The code is correct. The issue is with Vercel deployment configuration.

## Fixes Applied Locally

1. **Installed Dependencies**
   ```bash
   cd meal-planner-ui
   npm install
   ```
   - Created `node_modules/` directory
   - Installed 383 packages successfully

2. **Created Environment Configuration**
   - Created `.env.local` with required variables:
     ```env
     NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app
     NEXTAUTH_SECRET=[generated-using-openssl-rand-base64-32]
     NEXTAUTH_URL=https://claude-code-projects.vercel.app
     ```
   - Note: Generate your own NEXTAUTH_SECRET with `openssl rand -base64 32`

3. **Verified Build**
   ```bash
   npm run build
   ```
   - ✅ Compiled successfully in 3.4s
   - ✅ No TypeScript errors
   - ✅ All 11 pages generated

## Required Vercel Configuration

### Step 1: Set Root Directory

In Vercel Project Settings:
1. Go to **Settings** → **General**
2. Set **Root Directory**: `meal-planner-ui`
3. Click **Save**

### Step 2: Configure Environment Variables

In Vercel Project Settings → **Environment Variables**, add:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://claude-code-projects-production.up.railway.app` | Production, Preview, Development |
| `NEXTAUTH_SECRET` | `[Generate using: openssl rand -base64 32]` | Production, Preview, Development |
| `NEXTAUTH_URL` | `https://claude-code-projects.vercel.app` | Production |

**Important**: Make sure to select **All Environments** or at minimum **Production** for each variable.

### Step 3: Verify Build Settings

In **Settings** → **Build & Development Settings**:
- **Build Command**: `npm run build` (or leave as default)
- **Output Directory**: `.next` (or leave as default)
- **Install Command**: `npm install` (or leave as default)

### Step 4: Trigger Redeploy

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click **⋯** (three dots) → **Redeploy**
4. Select **"Use existing Build Cache"** → **No** (force fresh build)
5. Click **Redeploy**

## Verification Steps

After redeployment:

1. **Check Build Logs**
   - Deployment should show "Build succeeded"
   - No errors in build output

2. **Test the Site**
   - Navigate to: https://claude-code-projects.vercel.app/login
   - Verify password input field is visible
   - Verify "Sign In" button is visible

3. **Test Meal Planning Form**
   - Navigate to: https://claude-code-projects.vercel.app/generate
   - Verify date input field is visible
   - Verify all form fields render properly

4. **Check Browser Console**
   - Open DevTools (F12)
   - Check for JavaScript errors
   - Verify no network request failures

## Common Issues & Solutions

### Issue: "Environment variables not found"
**Solution**: Ensure all three environment variables are set in Vercel and marked for "Production" environment.

### Issue: "Build fails with module not found"
**Solution**:
- Clear build cache and redeploy
- Check that `Root Directory` is set to `meal-planner-ui`

### Issue: "Forms still not rendering"
**Solution**:
- Check browser console for JavaScript errors
- Verify NEXT_PUBLIC_API_URL is accessible from browser
- Check Network tab for failed CSS/JS file loads

### Issue: "Authentication doesn't work"
**Solution**:
- Verify NEXTAUTH_SECRET is set and not empty
- Verify NEXTAUTH_URL matches your Vercel domain exactly (including https://)
- Clear browser cookies and try again

## Why This Will Fix the Issues

The problems reported were:
1. ❌ Login page missing password input
2. ❌ Meal form missing date input
3. ❌ Navigation missing auth UI

These are NOT code issues. Looking at the source files:
- `src/app/login/page.tsx:85-93` - Password input IS in the code
- `src/app/generate/page.tsx:136-143` - Date input IS in the code
- `src/app/page.tsx:37-46` - Auth navigation IS in the code

The issue is that Vercel either:
- Isn't building from the correct directory (`meal-planner-ui`)
- Is missing environment variables causing runtime errors
- Had a failed build that's being cached

Following the steps above will ensure:
1. Vercel builds from the correct subdirectory
2. All required environment variables are available
3. A fresh build is deployed without cache issues

## Files Modified in This Commit

- `meal-planner-ui/.env.local` (created) - Local environment configuration
- `meal-planner-ui/node_modules/` (created) - Dependencies installed
- `VERCEL_FIX_INSTRUCTIONS.md` (this file) - Deployment fix guide

## Next Steps After Vercel Reconfiguration

Once the Vercel site is working:
1. Run the Playwright tests again to verify all UI elements render:
   ```bash
   npx playwright test e2e/deployed-app.spec.ts
   ```
2. Test authentication flow manually
3. Test meal plan generation flow
4. Verify Knuspr integration works

---

**Summary**: The frontend code is correct. The issue is Vercel configuration. Follow the steps above to fix the deployment.
