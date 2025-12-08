# Go, Cart! Deployment Guide

## Production Deployment

### Backend (Railway)
```bash
cd backend
railway login
railway link  # Link to your project
railway up    # Deploy from current directory
```

**Environment Variables** (Railway dashboard):
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-64-char-secret
KNUSPR_CLIENT_ID=...
KNUSPR_CLIENT_SECRET=...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=app-password
FROM_EMAIL=noreply@gocart.app
BASE_URL=https://your-app.railway.app
SENTRY_DSN=...
```

### Frontend (Vercel)
```bash
cd frontend
npm install -i
vercel --prod
```

**Environment Variables** (Vercel dashboard):
```
NEXTAUTH_SECRET=your-64-char-secret
NEXTAUTH_URL=https://gocart.app
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```

## Local Development
See [`quickstart.md`](quickstart.md)

## Pre-Deployment Checklist
```bash
# Backend
cd backend
pytest tests/ -v                    # ✅ All tests pass
alembic upgrade head               # ✅ DB migrations applied
python scripts/verify_db_config.py # ✅ DB connection OK
python scripts/verify_knuspr_mcp.py # ✅ Knuspr integration OK

# Frontend
cd frontend
npm run build                      # ✅ No build errors
npm run lighthouse                 # ✅ 95+ scores
```

## Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Monitoring
- **API Docs**: `https://your-app.railway.app/api/docs`
- **Health Check**: `GET /health`
- **Prometheus Metrics**: `GET /metrics`
- **Sentry**: Error tracking (if DSN configured)

## Rollback Procedures
```bash
# Railway (Backend)
railway rollback

# Vercel (Frontend)  
vercel rollback <deployment-url>
```

## DNS & Custom Domain
```
Vercel: Add domain in project settings
Railway: Add domain in service settings
```

**CNAME Record**: `gocart.app → cname.vercel-dns.com`

## Post-Deployment Verification
```bash
# Test waitlist signup
curl -X POST https://your-app.railway.app/api/v1/waitlist/join \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Test meal plan generation (requires auth)
curl -X POST https://your-app.railway.app/api/v1/meal-plans \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"servings": 2, "days": 7}'
```

## Troubleshooting
| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check Railway logs: `railway logs` |
| DB connection failed | Verify `DATABASE_URL` format |
| Knuspr 401 | Check client credentials |
| Build timeout | Increase Vercel build timeout |
| Service Worker not working | Requires HTTPS (production only) |