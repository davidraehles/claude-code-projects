# CLI Installation Guide for Windows

This guide will help you install Railway and Vercel CLI tools on your Windows system for debugging deployment failures.

## Prerequisites

You need Node.js and npm installed. If you don't have them:

### Install Node.js (Required)

1. **Download Node.js LTS** from [nodejs.org](https://nodejs.org/)
2. Run the installer (includes npm)
3. Verify installation in a new terminal:
   ```cmd
   node --version
   npm --version
   ```

## Railway CLI Installation

### Method 1: Using npm (Recommended)
```cmd
npm install -g @railway/cli
```

### Method 2: Using Scoop (if you have Scoop)
```cmd
scoop install railway
```

### Method 3: Direct Download
1. Download from [Railway CLI Releases](https://github.com/railwayapp/cli/releases)
2. Extract to a folder in your PATH
3. Add to PATH if needed

### Verify Installation
```cmd
railway --version
```

## Vercel CLI Installation

### Using npm (Recommended)
```cmd
npm install -g vercel
```

### Verify Installation
```cmd
vercel --version
```

## Authentication

### Railway
```cmd
# Login to Railway
railway login

# Link to your project
cd c:\Users\david\workspaces\claude-code-projects
railway link
```

### Vercel
```cmd
# Login to Vercel
vercel login

# Link to your project
cd c:\Users\david\workspaces\claude-code-projects\meal-planner-ui
vercel link
```

## Debugging Commands

### Railway Debugging

```cmd
# View logs from Railway deployment
railway logs

# Check environment variables
railway variables

# Run command in Railway environment
railway run <command>

# Deploy manually
railway up

# Check service status
railway status

# Open Railway dashboard
railway open
```

### Vercel Debugging

```cmd
# View deployment logs
vercel logs <deployment-url>

# List all deployments
vercel ls

# Inspect a deployment
vercel inspect <deployment-url>

# Check environment variables
vercel env ls

# Deploy manually (development)
vercel

# Deploy to production
vercel --prod

# Open Vercel dashboard
vercel open
```

## Common Issues & Solutions

### Railway

**Issue**: Port binding error
```cmd
# Check if PORT env var is set correctly
railway variables
# Should show PORT=8080 or similar
```

**Issue**: Build fails
```cmd
# View build logs
railway logs --build

# Test build locally with Docker
docker build -t test-app .
docker run -p 8000:8000 -e PORT=8000 test-app
```

### Vercel

**Issue**: Build fails
```cmd
# Run build locally
cd meal-planner-ui
npm install
npm run build
```

**Issue**: Environment variables missing
```cmd
# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Pull environment variables to local .env
vercel env pull
```

## Quick Test Deployment

### Test Railway Locally
```cmd
# Test with Docker (Railway uses Docker)
docker build -t meal-planner-api .
docker run -p 8080:8080 -e PORT=8080 meal-planner-api

# Test health endpoint
curl http://localhost:8080/health
```

### Test Vercel Locally
```cmd
cd meal-planner-ui
npm install
vercel dev
# Opens at http://localhost:3000
```

## Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Vercel Dashboard: https://vercel.com/dashboard
- Railway Docs: https://docs.railway.app/
- Vercel Docs: https://vercel.com/docs

## Your Project URLs

- **Railway Backend**: https://claude-code-projects-production.up.railway.app
- **Vercel Frontend**: (Set after deployment)
- **GitHub Repo**: https://github.com/davidraehles/claude-code-projects
