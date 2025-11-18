# Fixed: NextAuth "Not Found" Error

## Root Cause

The `vercel.json` was configured to proxy **ALL** `/api/*` requests to the Railway backend:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",  // ❌ TOO BROAD
      "destination": "https://claude-code-projects-production.up.railway.app/api/:path*"
    }
  ]
}
```

This meant that requests to `/api/auth/signin`, `/api/auth/callback`, etc. were being sent to Railway instead of being handled by Vercel's NextAuth route handler.

Railway doesn't have those endpoints → returned `{"detail":"Not Found"}`

---

## The Fix

Changed the proxy to only forward backend API calls (`/api/v1/*`):

```json
{
  "rewrites": [
    {
      "source": "/api/v1/:path*",  // ✅ SPECIFIC
      "destination": "https://claude-code-projects-production.up.railway.app/api/v1/:path*"
    }
  ]
}
```

Now:
- `/api/auth/*` → Handled by Vercel (NextAuth)
- `/api/v1/*` → Proxied to Railway (FastAPI backend)

---

## Deployment

Committed to `claude/main`:
```
d749606 - fix: Exclude NextAuth routes from backend proxy - only proxy /api/v1/*
```

Vercel will auto-deploy from the GitHub push.

---

## Testing After Deployment

1. **Wait for Vercel deployment** (~1-2 minutes)
   - Check: https://vercel.com/the-raedical-cos-projects/claude-code-projects/deployments

2. **Test NextAuth endpoints**:
   ```bash
   # Should return providers info (not "Not Found")
   curl https://claude-code-projects.vercel.app/api/auth/providers

   # Should return CSRF token
   curl https://claude-code-projects.vercel.app/api/auth/csrf
   ```

3. **Test login flow**:
   - Go to: https://claude-code-projects.vercel.app/login
   - Enter credentials
   - Should redirect to dashboard (not error page)

---

## Environment Variables Still Needed

Make sure these are set in Vercel:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://claude-code-projects-production.up.railway.app` |
| `NEXTAUTH_SECRET` | `[generated secret from openssl rand -base64 32]` |
| `NEXTAUTH_URL` | `https://claude-code-projects.vercel.app` |

If not set, the deployment will still fail (but with different errors).

---

## How It Works Now

```
User Login Request
    ↓
┌───────────────────────────────────┐
│ https://claude-code-projects      │
│        .vercel.app/login          │
└───────────────────────────────────┘
    ↓
    Form Submit
    ↓
┌───────────────────────────────────┐
│ POST /api/auth/callback/credentials│  ← Handled by Vercel
│ (NextAuth on Vercel)              │
└───────────────────────────────────┘
    ↓
    Calls Backend API
    ↓
┌───────────────────────────────────┐
│ POST /api/v1/auth/login           │  ← Proxied to Railway
│ (FastAPI on Railway)              │
└───────────────────────────────────┘
    ↓
    Returns JWT tokens
    ↓
┌───────────────────────────────────┐
│ GET /api/v1/auth/me               │  ← Proxied to Railway
│ (FastAPI on Railway)              │
└───────────────────────────────────┘
    ↓
    Returns user info
    ↓
    NextAuth creates session
    ↓
    Redirect to /dashboard
```

Clean separation:
- **Vercel**: Handles NextAuth session management
- **Railway**: Handles authentication business logic + JWT
- **Proxy**: Only for `/api/v1/*` backend calls
