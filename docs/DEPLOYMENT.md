# Deployment Guide

This guide covers deploying the Meal Planner application to Railway (backend) and Vercel (frontend).

## 🚂 Backend Deployment (Railway)

**Status**: ✅ Deployed
- **URL**: https://claude-code-projects-production.up.railway.app
- **Port**: 8080

### Railway Configuration
- Uses [Dockerfile](./Dockerfile) for containerized deployment
- Configuration in [railway.toml](./railway.toml)
- Excludes unnecessary files via [.railwayignore](./.railwayignore)

### Environment Variables (Railway)
Set these in your Railway dashboard:
- `DATABASE_URL` - PostgreSQL connection string (provision in Railway)
- `REDIS_URL` - Redis connection string (provision in Railway)
- `PORT` - Set to 8080 (Railway default)

---

## ▲ Frontend Deployment (Vercel)

### Quick Deploy
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. **Import** your repository: `davidraehles/claude-code-projects`
4. Configure project:
   - **Root Directory**: `meal-planner-ui`
   - **Framework**: Next.js (auto-detected)

### Environment Variables (Vercel)
Set these in the Vercel dashboard under **Settings → Environment Variables**:

```bash
# Backend API URL (Railway)
NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app

# NextAuth Secret (generate with: openssl rand -base64 32)
NEXTAUTH_SECRET=<your-generated-secret>

# Your Vercel URL (update after first deployment)
NEXTAUTH_URL=https://your-app.vercel.app
```

### Generate NextAuth Secret
```bash
openssl rand -base64 32
```

### Deploy
Click **Deploy** and Vercel will:
1. Install dependencies from [package.json](./meal-planner-ui/package.json)
2. Build the Next.js app
3. Deploy to production

---

## 📋 Post-Deployment Checklist

### After Railway Deployment
- [ ] Verify health endpoint: `https://claude-code-projects-production.up.railway.app/health`
- [ ] Check logs for any errors
- [ ] Test API endpoints

### After Vercel Deployment
- [ ] Update `NEXTAUTH_URL` with actual Vercel URL
- [ ] Verify frontend loads correctly
- [ ] Test API integration with Railway backend
- [ ] Check browser console for errors

---

## 🔧 Troubleshooting

### Railway Issues
- **Port binding**: Ensure PORT env var is set to 8080
- **Health check failing**: Check `/health` endpoint implementation
- **Build fails**: Review Dockerfile and build logs

### Vercel Issues
- **Build fails**: Check Node.js version compatibility
- **API calls fail**: Verify `NEXT_PUBLIC_API_URL` is correct
- **Auth issues**: Ensure `NEXTAUTH_SECRET` and `NEXTAUTH_URL` are set

---

## 🔄 Continuous Deployment

Both platforms are configured for automatic deployments:
- **Railway**: Auto-deploys on push to `claude/main` branch
- **Vercel**: Auto-deploys on push to `claude/main` branch

---

## 📚 Configuration Files

- Backend: [Dockerfile](./Dockerfile), [railway.toml](./railway.toml)
- Frontend: [vercel.json](./meal-planner-ui/vercel.json)
- Dependencies: [requirements.txt](./requirements.txt), [package.json](./meal-planner-ui/package.json)
