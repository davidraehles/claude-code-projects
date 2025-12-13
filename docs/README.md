# Go, Cart! Documentation Hub

Central documentation for the **Go, Cart!** AI meal planning and grocery ordering platform.

**Last Updated**: December 8, 2025

## 🚀 Quick Start
[quickstart.md](quickstart.md) - Local development setup (15 minutes)

## 📋 Table of Contents

### Core Guides
| Guide | Description |
|-------|-------------|
| [`quickstart.md`](quickstart.md) | Local development setup |
| [`deployment.md`](deployment.md) | Production deployment (Railway + Vercel) |
| [`architecture.md`](architecture.md) | System architecture & multi-agent workflows |

### Feature Documentation
| Feature | Status | Guide |
|---------|--------|-------|
| Meal Planning | ✅ Complete | [`architecture.md`](architecture.md)#meal-planning-workflow |
| Grocery Lists | ✅ Complete | [`architecture.md`](architecture.md)#grocery-cart-workflow |
| Knuspr Integration | ✅ Complete | [`deployment.md`](deployment.md)#knuspr-configuration |
| Waitlist System | ✅ Complete | [`quickstart.md`](quickstart.md)#waitlist-testing |

### Development
| Topic | Guide |
|-------|-------|
| [Testing](quickstart.md#testing) | Backend + Frontend test suites |
| [Database](deployment.md#database-migrations) | Migrations + seeding |
| [API Docs](http://localhost:8000/api/docs) | Interactive Swagger UI |

## 🎯 Key Features

1. **AI-Powered Meal Planning**
   - Multi-agent workflows (LangGraph)
   - Dietary constraints + optimization
   - Weekly plans with recipe selection

2. **Smart Grocery Lists**
   - Ingredient aggregation & scaling
   - Category organization
   - Knuspr cart population

3. **Production Ready**
   - 60fps animations (Lenis + GSAP)
   - Offline-first PWA (Service Worker)
   - WCAG 2.1 AAA accessibility
   - Lighthouse 95+ scores

4. **Developer Experience**
   - TypeScript strict mode
   - 14+ integration tests
   - Prometheus monitoring
   - Sentry error tracking

## 🛠 Technology Stack

```
Frontend: Next.js 16 + React 19 + TypeScript
Backend: FastAPI + PostgreSQL + LangGraph
Infra: Railway + Vercel + Neon Postgres
Agents: PydanticAI + AtomicAgents
```

## 📊 Live Deployments
```
Frontend: https://gocart.app
Backend: https://api.gocart.app
API Docs: https://api.gocart.app/api/docs
```

## 🤝 Contributing
```
feat: new feature
fix: bug fixes  
docs: documentation
test: testing improvements
```

See [quickstart.md](quickstart.md) for development setup.

---

**Built with ❤️ using multi-agent AI development**