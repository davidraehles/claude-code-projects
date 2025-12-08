# Go, Cart! Architecture Overview

## System Overview
Go, Cart! is a full-stack AI-powered meal planning and grocery ordering application with multi-agent architecture.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│  (Next.js 16)   │◄──►│   (FastAPI)      │◄──►│   Services      │
└─────────────────┘    └──────────────────�┘    └─────────────────┘
     │                       │                       │
     │                       │                       │
  ┌──▼──┐              ┌────▼────┐            ┌─────▼─────┐
  │ PWA │              │ Agents  │            │  Knuspr   │
  │ SW  │              │Workflows│            │  MCP API  │
  └─────┘              └─────────┘            └───────────┘
```

## Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | [`FastAPI`](https://fastapi.tiangolo.com/) | REST API server |
| Database | PostgreSQL + SQLAlchemy + Alembic | Data persistence |
| Agents | LangGraph + PydanticAI | Multi-agent orchestration |
| Auth | JWT + bcrypt | User authentication |
| Monitoring | Prometheus + Sentry | Observability |
| Email | SMTP + Jinja2 | Transactional emails |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | [`Next.js 16`](https://nextjs.org/) + React 19 | App framework |
| Styling | Tailwind CSS | Component styling |
| Animations | Lenis + GSAP + Framer Motion | 60fps interactions |
| State | React Query | Data fetching |
| Auth | NextAuth.js | Authentication |
| PWA | Service Worker + IndexedDB | Offline support |

## Core Components

### 1. Multi-Agent System
```
Router Agent → [Meal Architect, Cart Optimizer, 
               Recipe Harvester, Ingredient Intelligence]
```

**Agents:**
- **Meal Architect**: Generates weekly meal plans with constraints
- **Cart Optimizer**: Creates optimized grocery lists
- **Recipe Harvester**: Scrapes and parses recipes from web
- **Ingredient Intelligence**: Normalizes and maps ingredients

### 2. Key Workflows
1. **Meal Planning Workflow** (`meal_planning_workflow.py`)
   - Input: Dietary preferences, budget, servings
   - Output: Weekly meal plan with recipes
   - States: Planning → Validation → Optimization

2. **Grocery Cart Workflow**
   - Input: Meal plan + recipes
   - Output: Aggregated shopping list
   - Integration: Knuspr MCP cart population

3. **Waitlist Workflow**
   - Offline-first signup with background sync
   - Email verification with queue position

### 3. Database Schema
```
Users → MealPlans → Recipes → Ingredients
     ↳ WaitlistEntries
     ↳ KnusprCredentials
     ↳ RateLimits
```

### 4. API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/meal-plans` | POST | Generate meal plan |
| `/api/v1/grocery-carts` | POST | Generate grocery list |
| `/api/v1/recipes` | GET/POST | Recipe CRUD |
| `/api/v1/waitlist` | POST | Join waitlist |
| `/api/v1/knuspr-credentials` | POST | Store Knuspr auth |

## Deployment Architecture
```
Vercel (Frontend) ←→ Railway (Backend) ←→ PostgreSQL (Neon/Supabase)
                         ↓
                   Knuspr MCP API
```

## Performance & Quality
- **60fps animations** (GPU accelerated)
- **WCAG 2.1 AAA** compliant
- **Core Web Vitals**: 95+ Lighthouse scores
- **14 integration tests** for waitlist
- **TypeScript strict mode**: 100% coverage
- **Offline-first**: Service Worker + IndexedDB

## Monitoring & Observability
```
Prometheus Metrics:
├── waitlist_signups_total
├── waitlist_queue_size  
├── workflow_duration_seconds
└── api_request_duration