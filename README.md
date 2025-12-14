# Go, Cart! 🚀 AI Meal Planner & Grocery Cart

**AI-powered meal planning with seamless Knuspr grocery integration**

[![Frontend](https://gocart.app)](https://gocart.app) [![API](https://api.gocart.app/api/docs)](https://api.gocart.app/api/docs)

## ✨ What is Go, Cart!?

Go, Cart! transforms meal planning into a delightful experience:

- **AI Meal Architect** generates personalized weekly plans
- **Smart Grocery Lists** with ingredient optimization
- **One-click Knuspr** cart population
- **60fps Animations** with Lenis + GSAP + Framer Motion
- **Offline-first** PWA with Service Worker
- **WCAG 2.1 AAA** accessible

## 🎯 Key Features

| Feature | Status |
|---------|--------|
| Multi-agent meal planning | ✅ Live |
| Knuspr grocery integration | ✅ Live |
| Offline waitlist signup | ✅ Live |
| Recipe harvesting | ✅ Live |
| Ingredient intelligence | ✅ Live |

## 🚀 Quick Start (5 minutes)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install && npm run dev
```

**Open**: [http://localhost:3000](http://localhost:3000)

**Full guide**: [docs/quickstart.md](docs/quickstart.md)

## 🏗️ Architecture

```
Next.js 16 + React 19 → FastAPI → PostgreSQL + LangGraph Agents → Knuspr MCP
       ↓                       ↓
   PWA + 60fps            Prometheus + Sentry
```

**Details**: [docs/architecture.md](docs/architecture.md)

## 🚀 Deploy to Production

```bash
# Backend (Railway)
cd backend && railway up

# Frontend (Vercel)
cd frontend && vercel --prod
```

**Guide**: [docs/deployment.md](docs/deployment.md)

## 📚 Documentation

| Topic | Link |
|-------|------|
| **Getting Started** | |
| [Quickstart](docs/quickstart.md) | Local development setup |
| [Development Guide](docs/DEVELOPMENT_GUIDE.md) | Complete development workflow |
| **Integration** | |
| [Knuspr Integration](docs/KNUSPR_INTEGRATION.md) | Grocery delivery integration |
| [API Documentation](http://localhost:8000/api/docs) | Interactive Swagger UI |
| **Deployment** | |
| [Railway Deployment](docs/DEPLOYMENT_RAILWAY.md) | Production deployment guide |
| [Architecture](docs/architecture.md) | System architecture overview |

## 🧪 Testing

```bash
# Backend (14+ integration tests)
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test && npm run lighthouse
```

## 🔧 Environment Setup

Copy `.env.example` → `.env` and configure:

```
DATABASE_URL=postgresql://...
SECRET_KEY=sk-64-random-chars-here
KNUSPR_CLIENT_ID=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

```bash
git checkout -b feat/your-feature
# Follow conventional commits
git commit -m "feat: add meal plan optimization"
git push origin feat/your-feature
```

## 📈 Production Status

- **Lighthouse**: 95+ (Performance), 100 (Accessibility, SEO)
- **Tests**: 14 integration tests passing
- **Builds**: Clean production builds
- **Deployments**: Railway (backend), Vercel (frontend)

## 🌟 Acknowledgments

Built with multi-agent AI development using:
- **LangGraph** for agent orchestration
- **FastAPI** for production-ready APIs
- **Next.js 16** for modern frontend
- **Spec-Kit** for structured development

---

[![License](https://img.shields.io/badge/license-proprietary-blue)](LICENSE)
