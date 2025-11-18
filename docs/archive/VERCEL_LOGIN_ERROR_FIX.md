# Fix: NextAuth Login Redirecting to Error Page

## Symptoms

- Signup works (or shows "email already registered")
- After login, redirected to black page with `{"detail":"Not Found"}`
- Error URL: `https://claude-code-projects.vercel.app/api/auth/error`

## Root Causes & Fixes

### Issue 1: NEXTAUTH_SECRET Not Set (MOST LIKELY)

NextAuth requires `NEXTAUTH_SECRET` to be set in Vercel environment variables.

**Check:**
```bash
# If you have Vercel CLI logged in:
cd meal-planner-ui
vercel env ls
```

**Fix:**

1. Generate a secret:
   ```bash
   openssl rand -base64 32
   ```

2. Add to Vercel:
   - Go to: https://vercel.com/the-raedical-cos-projects/claude-code-projects/settings/environment-variables
   - Click "Add New"
   - Name: `NEXTAUTH_SECRET`
   - Value: [paste the generated secret]
   - Environments: **Production**, **Preview**, **Development** (select all 3)
   - Click "Save"

3. Redeploy:
   - Go to Deployments tab
   - Click "..." on latest deployment → "Redeploy"

---

### Issue 2: NEXT_PUBLIC_API_URL Not Set or Wrong

The frontend needs to know where the backend is.

**Check:**
Look for `NEXT_PUBLIC_API_URL` in Vercel environment variables.

**Fix:**

1. Add to Vercel (if missing):
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://claude-code-projects-production.up.railway.app`
   - Environments: **Production**, **Preview**, **Development**

2. Redeploy

---

### Issue 3: NEXTAUTH_URL Not Set (Optional but Recommended)

NextAuth works better with explicit URL configuration.

**Fix:**

1. Add to Vercel:
   - Name: `NEXTAUTH_URL`
   - Value: `https://claude-code-projects.vercel.app`
   - Environments: **Production** only

Note: Vercel usually sets this automatically, but explicit is better.

---

## What I Fixed in the Code

Updated `/meal-planner-ui/src/app/api/auth/[...nextauth]/route.ts` to:

1. **Fetch user info after login**: Now calls `/api/v1/auth/me` to get user details
2. **Better error logging**: Console logs show what's failing
3. **Fallback handling**: If user fetch fails, still allows login with email as fallback

**Changes:**
- After getting login tokens, now fetches user profile
- Returns proper user ID from backend instead of hardcoded '1'
- Added error logging to help debug issues

---

## Testing After Fix

1. **Clear browser cookies** for your Vercel domain

2. **Try signup** (if not already registered):
   ```
   https://claude-code-projects.vercel.app/signup
   ```

3. **Try login**:
   ```
   https://claude-code-projects.vercel.app/login
   ```

4. **Expected behavior**:
   - Login form submits
   - Redirected to dashboard
   - Can see user info

5. **If still fails**, check Vercel function logs:
   - Go to Vercel dashboard → Deployments → Latest → "Functions" tab
   - Look for errors in `/api/auth/[...nextauth]` logs

---

## Required Environment Variables Summary

| Variable | Value | Where |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://claude-code-projects-production.up.railway.app` | Vercel |
| `NEXTAUTH_SECRET` | `[generated secret]` | Vercel |
| `NEXTAUTH_URL` | `https://claude-code-projects.vercel.app` | Vercel (optional) |

---

## Next Steps

1. Set `NEXTAUTH_SECRET` in Vercel (if not already set)
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Commit and push the updated NextAuth route
4. Redeploy Vercel
5. Test login flow

---

## Still Having Issues?

Check Vercel function logs for specific error messages:
1. Go to Vercel dashboard
2. Click on your deployment
3. Click "Functions" tab
4. Look for `/api/auth/[...nextauth]` route
5. Check logs for errors

Common errors:
- "No secret provided" → NEXTAUTH_SECRET not set
- "Fetch failed" → NEXT_PUBLIC_API_URL wrong or backend down
- "Invalid credentials" → Wrong email/password
