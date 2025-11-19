# Production Deployment Guide

This document outlines the steps to deploy the Multi-Agent Recipe App to production using Railway (Backend) and Vercel (Frontend).

## 1. Backend Deployment (Railway)

The backend is a FastAPI application with PostgreSQL and Redis.

### Prerequisites
- Railway account
- GitHub repository connected

### Steps
1. **Create Project**: Create a new project in Railway from the GitHub repository.
2. **Add Services**:
   - **PostgreSQL**: Add a PostgreSQL database service.
   - **Redis**: Add a Redis service.
   - **FastAPI**: Connect your GitHub repo.
3. **Environment Variables**:
   Configure the following variables in the FastAPI service:
   ```bash
   # Database (Use Railway Reference)
   DATABASE_URL=${{Postgres.DATABASE_URL}}

   # Redis (Use Railway Reference)
   REDIS_HOST=${{Redis.REDIS_HOST}}
   REDIS_PORT=${{Redis.REDIS_PORT}}
   REDIS_PASSWORD=${{Redis.REDIS_PASSWORD}}

   # Application
   APP_ENV=production
   DEBUG=False
   LOG_LEVEL=info

   # Security
   SECRET_KEY=<generate-random-key>
   JWT_SECRET_KEY=<generate-random-key>

   # CORS (Critical for Frontend Access)
   CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
   ```
4. **Build Command**: Railway automatically detects the `Dockerfile`.
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Verification
- Check health endpoint: `https://<your-railway-app>.up.railway.app/health`
- Verify CORS headers:
  ```bash
  curl -I -H "Origin: https://claude-code-projects.vercel.app" \
       -H "Access-Control-Request-Method: GET" \
       https://<your-railway-app>.up.railway.app/health
  ```

## 2. Frontend Deployment (Vercel)

The frontend is a Next.js application.

### Prerequisites
- Vercel account
- GitHub repository connected

### Steps
1. **Import Project**: Import the `meal-planner-ui` directory from your GitHub repo.
2. **Build Settings**:
   - Framework Preset: Next.js
   - Root Directory: `meal-planner-ui`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`
3. **Environment Variables**:
   ```bash
   # Backend API URL
   NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app

   # NextAuth Configuration
   NEXTAUTH_URL=https://claude-code-projects.vercel.app
   NEXTAUTH_SECRET=<generate-random-key>
   ```
4. **Deploy**: Click "Deploy".

### Verification
- Visit the deployed URL.
- Test Login/Signup (connects to Backend).
- Test Recipe Import (connects to Backend).

## 3. Post-Deployment Checks

Run the verification script locally to check both services:
```bash
./scripts/verify_deployment.sh
```

## Troubleshooting

### CORS Issues
If you see CORS errors in the browser console:
1. Check `CORS_ORIGINS` in Railway.
2. Ensure it exactly matches the Vercel URL (no trailing slash).
3. Redeploy Backend if changed.

### Database Connection
If the backend fails to start:
1. Check `DATABASE_URL` in Railway.
2. Ensure migrations ran (`alembic upgrade head`).
3. Check Railway logs for connection errors.

### NextAuth Errors
If login fails:
1. Check `NEXTAUTH_URL` matches the Vercel domain.
2. Check `NEXTAUTH_SECRET` is set.
3. Verify Backend logs for auth request failures.
