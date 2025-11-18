# Quick Summary: Deployment Issues & Solutions

**Status:** ✅ Production Ready - Login and authentication working

---

## What We Fixed

### 1. Password Hashing Bug ⚠️ CRITICAL

**Problem:** `bcrypt.hash()` throwing "72 bytes" error for 15-byte password

**Root Cause:** Unconfigured passlib bcrypt hasher

**Solution:**
```python
# Before (broken)
return bcrypt.hash(password)

# After (working)
return bcrypt.using(ident="2b", rounds=12).hash(password)
```

**File:** `app/api/v1/auth.py:86`

---

### 2. NextAuth "Not Found" Error 🔧

**Problem:** Login redirected to error page with `{"detail":"Not Found"}`

**Root Cause:** `vercel.json` proxied ALL `/api/*` to Railway, including NextAuth routes

**Solution:**
```json
// Before (broken)
"source": "/api/:path*"

// After (working)
"source": "/api/v1/:path*"
```

**File:** `meal-planner-ui/vercel.json`

---

### 3. Railway Environment Variables 🔑

**Problem:** Database connection errors despite setting `DATABASE_URL`

**Root Cause:** Typed `${{Postgres.DATABASE_URL}}` as literal text

**Solution:** Use Railway's **Reference** feature, not copy-paste

---

## Key Learnings

1. **Passlib requires explicit configuration** - `bcrypt.using()` not just `bcrypt.hash()`
2. **Vercel proxies must be specific** - Only proxy backend routes, not all `/api/*`
3. **Railway References inject at runtime** - Don't type variable syntax as literal text
4. **Two different secrets needed** - `JWT_SECRET_KEY` (backend) ≠ `NEXTAUTH_SECRET` (frontend)

---

## Production URLs

- **Frontend:** https://claude-code-projects.vercel.app
- **Backend:** https://claude-code-projects-production.up.railway.app
- **API Docs:** https://claude-code-projects-production.up.railway.app/api/docs

---

## Required Environment Variables

### Vercel (Frontend)
```bash
NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app
NEXTAUTH_SECRET=<openssl rand -base64 32>
NEXTAUTH_URL=https://claude-code-projects.vercel.app
```

### Railway (Backend)
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Use Reference!
JWT_SECRET_KEY=<openssl rand -hex 32>
APP_ENV=production
CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
```

---

## For More Details

See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for comprehensive instructions.
