# CLI Quick Reference

Quick reference for Railway and Vercel CLI commands.

## 🎯 Setup (One-Time)

### Install CLIs
```cmd
# Double-click this file:
run-install.cmd
```

### Login & Link
```cmd
# Double-click this file:
login-cli-tools.cmd

# Or run manually:
railway login
railway link

vercel login
cd meal-planner-ui
vercel link
```

---

## 🚂 Railway Commands

### Viewing Logs & Status
```bash
# View real-time logs
railway logs

# Follow logs (continuous)
railway logs --follow

# View logs from specific service
railway logs --service meal-planner-api

# Check deployment status
railway status

# View recent deployments
railway up --detach
```

### Environment Variables
```bash
# List all variables
railway variables

# Add a variable
railway variables set KEY=value

# Remove a variable
railway variables delete KEY

# View database URL
railway variables | findstr DATABASE
```

### Development & Testing
```bash
# Run command in Railway environment
railway run python manage.py migrate

# Open Railway dashboard
railway open

# SSH into service (if available)
railway shell

# Check service info
railway service
```

### Deployment
```bash
# Deploy current directory
railway up

# Deploy specific service
railway up --service meal-planner-api

# Rollback to previous deployment
railway rollback
```

---

## ▲ Vercel Commands

**Note**: Run these from `meal-planner-ui` directory

### Deployment
```bash
cd meal-planner-ui

# Deploy to preview (automatic URL)
vercel

# Deploy to production
vercel --prod

# Deploy with specific environment
vercel --env production
```

### Viewing Logs & Status
```bash
# List all deployments
vercel ls

# View logs from latest deployment
vercel logs

# View logs from specific deployment
vercel logs <deployment-url>

# Inspect deployment
vercel inspect <deployment-url>
```

### Environment Variables
```bash
# List environment variables
vercel env ls

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Remove environment variable
vercel env rm NEXT_PUBLIC_API_URL production

# Pull environment variables to .env.local
vercel env pull
```

### Project Management
```bash
# Open Vercel dashboard
vercel open

# View project info
vercel project ls

# Remove a deployment
vercel rm <deployment-url>

# Link to different project
vercel link
```

### Development
```bash
# Run local dev server with Vercel env
vercel dev

# Build locally
vercel build

# Run production build locally
npm run build && npm start
```

---

## 🐛 Common Debugging Workflows

### Railway Backend Issues

**Check if service is running:**
```bash
railway status
railway logs --follow
```

**Verify environment variables:**
```bash
railway variables | findstr PORT
railway variables | findstr DATABASE_URL
```

**Test database connection:**
```bash
railway run python -c "from app.database import engine; print('DB Connected')"
```

**View build logs:**
```bash
railway logs --service meal-planner-api | findstr "ERROR"
```

### Vercel Frontend Issues

**Check build status:**
```bash
cd meal-planner-ui
vercel ls
```

**View build logs:**
```bash
vercel logs <deployment-url>
```

**Test environment variables:**
```bash
vercel env ls
```

**Test local build:**
```bash
npm run build
# Check for errors
```

### Integration Issues (Frontend ↔ Backend)

**Verify API URL in Vercel:**
```bash
cd meal-planner-ui
vercel env ls | findstr API_URL
# Should be: https://claude-code-projects-production.up.railway.app
```

**Test API endpoint from Railway:**
```bash
curl https://claude-code-projects-production.up.railway.app/health
```

**Check CORS settings in Railway:**
```bash
railway logs | findstr CORS
```

---

## 📋 Your Project URLs

### Backend (Railway)
- **Production**: https://claude-code-projects-production.up.railway.app
- **Health Check**: https://claude-code-projects-production.up.railway.app/health
- **API Docs**: https://claude-code-projects-production.up.railway.app/docs

### Frontend (Vercel)
- **Production**: (Set after first deployment)
- **Preview**: (Generated for each deployment)

### Dashboards
- **Railway**: https://railway.app/dashboard
- **Vercel**: https://vercel.com/dashboard
- **GitHub**: https://github.com/davidraehles/claude-code-projects

---

## 🔥 Emergency Commands

### Restart Railway Service
```bash
railway service restart
```

### Rollback Railway Deployment
```bash
railway rollback
```

### Delete Failed Vercel Deployment
```bash
vercel rm <failed-deployment-url>
```

### Force Redeploy
```bash
# Railway
railway up --detach

# Vercel
vercel --prod --force
```

---

## 💡 Pro Tips

1. **Keep logs open during deployment:**
   ```bash
   # Terminal 1: Railway logs
   railway logs --follow

   # Terminal 2: Vercel logs
   vercel logs --follow <url>
   ```

2. **Test locally before deploying:**
   ```bash
   # Backend
   docker build -t test-api .
   docker run -p 8080:8080 -e PORT=8080 test-api

   # Frontend
   cd meal-planner-ui
   vercel dev
   ```

3. **Use environment files for local development:**
   ```bash
   # Pull production env vars
   cd meal-planner-ui
   vercel env pull .env.local
   ```

4. **Quick health checks:**
   ```bash
   # Railway API
   curl https://claude-code-projects-production.up.railway.app/health

   # Vercel frontend
   curl <your-vercel-url>
   ```

---

## 📚 More Resources

- [INSTALL_CLI_TOOLS.md](./INSTALL_CLI_TOOLS.md) - Installation guide
- [CLI_INSTALLATION.md](./CLI_INSTALLATION.md) - Detailed CLI reference
- [DEPLOYMENT.md](./DEPLOYMENT.md) - General deployment guide
- [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) - Railway-specific guide
