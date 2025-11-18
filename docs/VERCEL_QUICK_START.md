# Vercel Quick Start Guide

Quick guide to deploy your Next.js frontend to Vercel.

## 🚀 Quick Deployment (3 Steps)

### Step 1: Setup Environment Variables
**Double-click** [setup-vercel-env.cmd](./setup-vercel-env.cmd)

This will automatically:
- ✅ Set `NEXT_PUBLIC_API_URL` to your Railway backend
- ✅ Generate and set secure `NEXTAUTH_SECRET`
- ✅ Configure for production, preview, and development

### Step 2: Deploy to Vercel
Open PowerShell in the project directory and run:
```powershell
cd meal-planner-ui
vercel --prod
```

Or deploy via Vercel dashboard:
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `davidraehles/claude-code-projects`
3. Set root directory to `meal-planner-ui`
4. Deploy!

### Step 3: Update NEXTAUTH_URL (After First Deployment)
After deployment, copy your Vercel URL and add it:
```powershell
cd meal-planner-ui
vercel env add NEXTAUTH_URL production
# Paste your URL when prompted (e.g., https://your-project.vercel.app)

# Redeploy to apply the change
vercel --prod --force
```

---

## 📋 What Was Fixed

### Problem
```
Deployment failed — Environment Variable "NEXT_PUBLIC_API_URL"
references Secret "api-url", which does not exist.
```

### Solution
1. **Removed secret references** from [vercel.json](./meal-planner-ui/vercel.json)
2. **Hardcoded Railway URL** in API rewrites
3. **Created setup script** to add environment variables via CLI

### Changes Made
- ✅ Updated `vercel.json` to remove `@secret` references
- ✅ Added Railway backend URL directly to rewrites
- ✅ Created `setup-vercel-env.ps1` for automated setup

---

## 🌐 Your Configuration

### Backend (Railway)
```
https://claude-code-projects-production.up.railway.app
```

### Environment Variables

#### NEXT_PUBLIC_API_URL
```bash
# Value: https://claude-code-projects-production.up.railway.app
# Purpose: Points frontend API calls to Railway backend
# Required: Yes
```

#### NEXTAUTH_SECRET
```bash
# Value: (Auto-generated secure random string)
# Purpose: Encrypts NextAuth.js session tokens
# Required: Yes
```

#### NEXTAUTH_URL
```bash
# Value: https://your-project.vercel.app (set after deployment)
# Purpose: Base URL for NextAuth.js callbacks
# Required: Yes (but can be added after first deployment)
```

---

## 🔧 Manual Setup (Alternative)

If you prefer to set variables manually via Vercel dashboard:

1. Go to your project on [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to **Settings** → **Environment Variables**
3. Add these variables:

```bash
Name: NEXT_PUBLIC_API_URL
Value: https://claude-code-projects-production.up.railway.app
Environments: Production, Preview, Development

Name: NEXTAUTH_SECRET
Value: (Generate with: openssl rand -base64 32)
Environments: Production, Preview, Development

Name: NEXTAUTH_URL
Value: https://your-project.vercel.app
Environments: Production
```

4. **Redeploy** from the Deployments tab

---

## 🐛 Troubleshooting

### Build Fails
```powershell
# Test build locally
cd meal-planner-ui
npm install
npm run build
```

### Environment Variables Not Working
```powershell
# List all variables
cd meal-planner-ui
vercel env ls

# Pull variables locally to test
vercel env pull .env.local
```

### API Calls Failing
```powershell
# Verify Railway backend is running
curl https://claude-code-projects-production.up.railway.app/health

# Check rewrites in vercel.json
# API calls to /api/* should be rewritten to Railway
```

### CORS Errors
Make sure your Railway backend has CORS configured to allow your Vercel domain.

---

## 📚 Next Steps

After successful deployment:

1. **Test the frontend**: Visit your Vercel URL
2. **Test API integration**: Check if frontend can call Railway backend
3. **Monitor logs**:
   ```powershell
   vercel logs <your-deployment-url>
   ```
4. **Set up automatic deployments**: Vercel will auto-deploy on push to `claude/main`

---

## 🎯 Quick Commands Reference

```powershell
# Deploy to production
cd meal-planner-ui
vercel --prod

# Deploy to preview
vercel

# View logs
vercel logs

# List deployments
vercel ls

# Open in browser
vercel open

# Force redeploy
vercel --prod --force
```

---

## ✅ Success Checklist

- [ ] Environment variables configured (run setup-vercel-env.cmd)
- [ ] Deployed to Vercel
- [ ] NEXTAUTH_URL updated with actual deployment URL
- [ ] Redeployed after adding NEXTAUTH_URL
- [ ] Frontend loads successfully
- [ ] API calls to Railway backend work
- [ ] No CORS errors in browser console

---

## 🆘 Need Help?

- **Railway logs**: `railway logs`
- **Vercel logs**: `vercel logs <url>`
- **Quick reference**: [CLI_QUICK_REFERENCE.md](./CLI_QUICK_REFERENCE.md)
- **Full deployment guide**: [DEPLOYMENT.md](./DEPLOYMENT.md)
