# Go, Cart! Documentation Hub

Central documentation for the **Go, Cart!** AI meal planning and grocery ordering platform.

**Last Updated**: December 14, 2025

## 🚀 Quick Start
[quickstart.md](quickstart.md) - Local development setup (15 minutes)

## 📋 Table of Contents

### Getting Started
| Guide | Description |
|-------|-------------|
| [Quickstart](quickstart.md) | Local development setup (15 min) |
| [Development Guide](DEVELOPMENT_GUIDE.md) | Complete workflow: testing, linting, common tasks |

### Integration & Features
| Guide | Description |
|-------|-------------|
| [Knuspr Integration](KNUSPR_INTEGRATION.md) | Complete grocery delivery integration guide |
| [Architecture](architecture.md) | System architecture & multi-agent workflows |

### Deployment
| Guide | Description |
|-------|-------------|
| [Railway Deployment](DEPLOYMENT_RAILWAY.md) | Multi-service production deployment |
| [Deployment Overview](deployment.md) | Quick deployment reference |

### Quick Reference
| Feature | Status | Documentation |
|---------|--------|---------------|
| Meal Planning | ✅ Complete | [Architecture](architecture.md#meal-planning-workflow) |
| Grocery Lists | ✅ Complete | [Architecture](architecture.md#grocery-cart-workflow) |
| Knuspr Integration | ✅ Complete | [Knuspr Integration](KNUSPR_INTEGRATION.md) |
| All 17 MCP Tools | ✅ Complete | [MCP Tools Reference](KNUSPR_INTEGRATION.md#mcp-tools-reference) |
| Railway Deployment | ✅ Complete | [Railway Guide](DEPLOYMENT_RAILWAY.md) |

### Development Tasks
| Topic | Guide |
|-------|-------|
| Testing | [Development Guide - Testing](DEVELOPMENT_GUIDE.md#testing) |
| Database Migrations | [Development Guide - Database](DEVELOPMENT_GUIDE.md#database-management) |
| Code Quality | [Development Guide - Code Quality](DEVELOPMENT_GUIDE.md#code-quality) |
| API Docs | [Swagger UI](http://localhost:8000/api/docs) |

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
