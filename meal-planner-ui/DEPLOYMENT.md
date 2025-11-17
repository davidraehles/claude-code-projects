# Vercel Deployment Guide

Complete step-by-step guide to deploy MealPlannerAI frontend to Vercel.

## Prerequisites

- [ ] Code pushed to GitHub
- [ ] Backend API deployed and accessible
- [ ] Vercel account created

## Step 1: Prepare Environment Variables

Before deploying, prepare these values:

### NEXTAUTH_SECRET
Generate a secure random string:
```bash
openssl rand -base64 32
```
Copy the output - you'll need it for Vercel.

### NEXT_PUBLIC_API_URL
Your backend API URL. Examples:
- Development: `http://localhost:8000`
- Production: `https://api.mealplanner.com`
- Heroku: `https://your-app.herokuapp.com`
- Railway: `https://your-app.up.railway.app`

### NEXTAUTH_URL
Leave this blank for first deployment - you'll update it after getting your Vercel URL.

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel**:
   - Visit [https://vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Create New Project**:
   - Click "Add New..." → "Project"
   - Select your GitHub repository
   - Vercel will auto-detect it's a Next.js project

3. **Configure Project**:
   - **Root Directory**: `meal-planner-ui` (if frontend is in subdirectory)
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

4. **Add Environment Variables**:
   Click "Environment Variables" and add:

   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://your-backend-api.com

   Name: NEXTAUTH_SECRET
   Value: <your-generated-secret-from-step-1>

   Name: NEXTAUTH_URL
   Value: (leave blank for now)
   ```

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd meal-planner-ui
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: mealplanner-ui
# - Directory: ./
# - Override settings? No

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL
# Enter your backend URL

vercel env add NEXTAUTH_SECRET
# Paste your generated secret

# Deploy to production
vercel --prod
```

## Step 3: Post-Deployment Configuration

### Update NEXTAUTH_URL

1. After first deployment, copy your Vercel URL (e.g., `https://mealplanner-ui-abc123.vercel.app`)

2. In Vercel dashboard:
   - Go to Settings → Environment Variables
   - Add or update `NEXTAUTH_URL` with your Vercel URL
   - Click "Save"

3. **Redeploy** for changes to take effect:
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment

### Test Your Deployment

1. **Visit your Vercel URL**:
   - Landing page should load
   - Navigation should work

2. **Test Authentication**:
   - Go to `/signup`
   - Create an account
   - Verify you're redirected to `/dashboard`

3. **Test API Integration**:
   - Check browser console for errors
   - Verify recipes load on dashboard
   - Try generating a meal plan

### Common Post-Deployment Issues

#### Issue: "Authentication failed"
**Solution**: Check that `NEXTAUTH_URL` matches your Vercel URL exactly (including https://)

#### Issue: "Failed to fetch recipes"
**Solution**:
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check that backend API allows CORS from your Vercel domain
- Test backend API endpoint directly

#### Issue: "Invalid session"
**Solution**: Clear cookies and try logging in again. Verify `NEXTAUTH_SECRET` is set.

## Step 4: Custom Domain (Optional)

### Add Custom Domain

1. **In Vercel Dashboard**:
   - Go to Settings → Domains
   - Click "Add Domain"
   - Enter your domain (e.g., `app.mealplanner.com`)

2. **Configure DNS**:
   Vercel will provide DNS records. Add to your DNS provider:
   ```
   Type: CNAME
   Name: app (or @)
   Value: cname.vercel-dns.com
   ```

3. **Update Environment Variables**:
   - Go to Settings → Environment Variables
   - Update `NEXTAUTH_URL` to your custom domain
   - Example: `https://app.mealplanner.com`
   - Click "Save"

4. **Redeploy**:
   - Go to Deployments
   - Redeploy latest deployment

## Step 5: Monitoring and Maintenance

### Enable Analytics

In Vercel dashboard:
- Go to Analytics tab
- Enable Web Analytics (free)
- Monitor page views, performance, and errors

### Set Up Automatic Deployments

Vercel automatically deploys when you push to GitHub:
- **Production**: Deploys from `main` branch
- **Preview**: Deploys from feature branches

### Monitor Logs

View real-time logs:
- Go to Deployments
- Click on a deployment
- View "Functions" or "Build Logs" tabs

## Environment Variables Quick Reference

| Variable | Required | Example | When to Update |
|----------|----------|---------|----------------|
| `NEXT_PUBLIC_API_URL` | Yes | `https://api.example.com` | When backend URL changes |
| `NEXTAUTH_SECRET` | Yes | `abc123...` | Once during setup |
| `NEXTAUTH_URL` | Yes | `https://app.example.com` | After first deploy, when domain changes |

## Deployment Checklist

Before going live:

- [ ] Environment variables configured
- [ ] First deployment successful
- [ ] `NEXTAUTH_URL` updated and redeployed
- [ ] Authentication tested (signup, login, logout)
- [ ] API integration tested (recipes, meal plans)
- [ ] Mobile responsiveness verified
- [ ] Custom domain configured (if applicable)
- [ ] CORS configured on backend for your Vercel domain
- [ ] Analytics enabled
- [ ] Error monitoring set up

## Rollback Instructions

If you need to rollback to a previous deployment:

1. Go to Deployments tab in Vercel
2. Find the working deployment
3. Click "..." menu → "Promote to Production"
4. Confirm

## Getting Help

- **Vercel Documentation**: https://vercel.com/docs
- **NextAuth.js Docs**: https://next-auth.js.org/getting-started/introduction
- **Next.js Deployment**: https://nextjs.org/docs/deployment

## Security Checklist

Before production:
- [ ] `NEXTAUTH_SECRET` is cryptographically secure (min 32 chars)
- [ ] No sensitive data in `.env.example`
- [ ] Backend API uses HTTPS
- [ ] CORS properly configured on backend
- [ ] Rate limiting enabled on API
- [ ] Security headers configured (Vercel does this by default)

---

**You're ready to deploy!** 🚀

Just import your repository in Vercel and follow the steps above.
