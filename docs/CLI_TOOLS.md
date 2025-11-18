# CLI Tools Reference

Quick reference for Railway and Vercel CLI tools.

---

## Installation

### Railway CLI

**Linux/Mac:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

**Windows:**
```bash
iwr https://railway.app/install.ps1 | iex
```

### Vercel CLI

```bash
npm install -g vercel
```

---

## Railway CLI

### Authentication

```bash
# Login
railway login

# Link to project
railway link
railway link -p <project-id>
```

### Deployment

```bash
# Deploy current directory
railway up

# Deploy in detached mode
railway up -d

# Deploy to specific environment
railway up --environment production
```

### Environment Variables

```bash
# List variables
railway variables

# Set variable
railway variables set KEY=value

# Delete variable
railway variables delete KEY
```

### Logs & Status

```bash
# View logs
railway logs

# Follow logs (live)
railway logs --follow

# Check status
railway status
```

### Services

```bash
# Run command in Railway environment
railway run <command>

# Examples
railway run python manage.py migrate
railway run alembic upgrade head
```

---

## Vercel CLI

### Authentication

```bash
# Login
vercel login

# Link to project
vercel link
```

### Deployment

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Deploy with custom domain
vercel --prod --scope <team-name>
```

### Environment Variables

```bash
# List variables
vercel env ls

# Add variable
vercel env add

# Pull variables to local
vercel env pull
```

### Projects

```bash
# List projects
vercel list

# Project info
vercel inspect

# View deployments
vercel ls
```

---

## Common Workflows

### Deploy Full Stack

```bash
# 1. Deploy backend
railway up -d

# 2. Wait for deployment
sleep 30

# 3. Deploy frontend
cd meal-planner-ui
vercel --prod
```

### Debug Deployment Issues

```bash
# Railway
railway logs --follow

# Vercel
vercel logs <deployment-url>
```

### Update Environment Variables

```bash
# Railway
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set JWT_SECRET_KEY=$(openssl rand -hex 32)

# Vercel
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXTAUTH_SECRET production
```

### Force Redeploy

```bash
# Railway (trigger redeploy)
git commit --allow-empty -m "chore: trigger redeploy"
git push

# Vercel (redeploy last)
vercel --force
```

---

## Troubleshooting

### Railway Not Deploying

```bash
# Check if linked
railway status

# Check recent deployments
railway logs | head -50

# Force relink
railway unlink
railway link
```

### Vercel Build Fails

```bash
# Check build logs
vercel logs <deployment-url>

# Test build locally
npm run build

# Check environment variables
vercel env ls
```

### Database Connection Issues

```bash
# Railway - Check DATABASE_URL
railway variables | grep DATABASE_URL

# Test connection
railway run psql $DATABASE_URL -c "SELECT 1"
```

---

## Quick Commands

```bash
# Railway
railway login && railway link && railway up -d

# Vercel
vercel login && vercel link && vercel --prod

# Generate secrets
openssl rand -hex 32   # JWT_SECRET_KEY
openssl rand -base64 32  # NEXTAUTH_SECRET
```

---

**More Info:**
- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
