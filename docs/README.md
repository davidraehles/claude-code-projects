# Documentation

## Quick Start

**New to this project?** Start here:
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment guide for Railway + Vercel

## Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
- **[DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)** - Current deployment status

## Archive

Historical troubleshooting notes are in [`archive/`](archive/) for reference.

## Key Learnings

### 1. Bcrypt Password Hashing

**Issue:** passlib's `bcrypt.hash()` requires explicit configuration

**Solution:**
```python
return bcrypt.using(ident="2b", rounds=12).hash(password)
```

### 2. Vercel NextAuth Proxy Conflict

**Issue:** Proxying `/api/*` to backend breaks NextAuth routes

**Solution:** Only proxy backend routes (`/api/v1/*`), not all `/api/*`

### 3. Railway Environment Variables

**Issue:** Typing `${{Service.VAR}}` as text doesn't work

**Solution:** Use Railway's **Reference** feature to inject variables

---

For detailed troubleshooting, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
