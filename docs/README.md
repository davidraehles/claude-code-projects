# Documentation

Welcome to the Multi-Agent Recipe App documentation!

---

## 🚀 Getting Started

New to this project? Start here:

1. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to Railway + Vercel (30 min)
2. **[CLI_TOOLS.md](CLI_TOOLS.md)** - Railway & Vercel CLI reference
3. **[QUICKSTART.md](QUICKSTART.md)** - Local development setup

---

## 📚 Main Guides

### Deployment & Operations
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[CLI_TOOLS.md](CLI_TOOLS.md)** - CLI commands & troubleshooting

### Development
- **[QUICKSTART.md](QUICKSTART.md)** - Local setup with Docker
- **[VSCODE_DEVELOPMENT_READY.md](VSCODE_DEVELOPMENT_READY.md)** - VSCode setup
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Manual testing procedures

### Architecture & Planning
- **[ARCHITECTURE_DEBT.md](ARCHITECTURE_DEBT.md)** - Technical debt & refactoring
- **[WEB_APP_MVP_PLAN.md](WEB_APP_MVP_PLAN.md)** - MVP implementation plan

### Project Status
- **[PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md)** - Phase 1 milestones
- **[PHASE_2_STATUS.md](PHASE_2_STATUS.md)** - Phase 2 progress

---

## 🔑 Key Learnings

### 1. Bcrypt Password Hashing
**Problem:** passlib's `bcrypt.hash()` requires explicit configuration

**Solution:**
```python
return bcrypt.using(ident="2b", rounds=12).hash(password)
```

### 2. Vercel NextAuth Proxy
**Problem:** Proxying `/api/*` breaks NextAuth routes

**Solution:** Only proxy backend routes:
```json
"source": "/api/v1/:path*"
```

### 3. Railway Environment Variables
**Problem:** Typing `${{Service.VAR}}` as text doesn't work

**Solution:** Use Railway's **Reference** feature

---

## 🌐 Live Deployments

- **Frontend:** https://claude-code-projects.vercel.app
- **Backend:** https://claude-code-projects-production.up.railway.app
- **API Docs:** https://claude-code-projects-production.up.railway.app/api/docs

---

## 📦 Archive

Historical troubleshooting notes: [`archive/`](archive/)

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.
