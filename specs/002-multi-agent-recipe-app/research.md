# Technical Research & Decision Log

**Feature**: Multi-Agent Recipe and Meal Planning System
**Date**: 2025-11-14
**Status**: Research Complete - Ready for Implementation Planning

---

## Executive Summary

This document outlines the technology selection for the multi-agent recipe and meal planning SaaS. Decisions prioritize:
1. **Proven frameworks** for multi-agent orchestration (LangChain/LangGraph)
2. **Fast time-to-market** (FastAPI, PostgreSQL, no custom frameworks)
3. **Cost efficiency** (Anthropic Claude for AI, no ML training)
4. **Team productivity** (Python ecosystem, familiar tools)
5. **Future scalability** (containerized agents, infrastructure-agnostic)

---

## Core Decision: Multi-Agent Architecture

### Why LangChain/LangGraph?
| Criterion | LangChain/LangGraph | CrewAI | Custom |
|-----------|-------------------|--------|--------|
| Maturity | Production-ready | Early/Experimental | High risk |
| Multi-agent orchestration | Excellent | Good | N/A |
| Community & docs | Large, mature | Growing | N/A |
| Workflow visualization | LangSmith integration | Basic | N/A |
| Cost | Free/open-source | Free/open-source | Engineer time |
| Learning curve | Moderate | Low | High |

**Decision**: Use LangChain/LangGraph for orchestration.

**Rationale**:
- Production maturity for multi-agent workflows (LangGraph specifically designed for this)
- Excellent integration with Anthropic Claude
- Built-in workflow visualization via LangSmith (helps debugging)
- Large community for troubleshooting

**Risk & Mitigation**:
- Risk: Dependency on third-party library updates
- Mitigation: Pin versions carefully, run contract tests, budget for migration if needed

---

## Core Decision: Agent Frameworks

### PydanticAI vs Traditional Approaches

| Aspect | PydanticAI | Traditional Agents |
|--------|-----------|-------------------|
| Type hints | Built-in | Manual with Pydantic |
| Async support | Native | Requires planning |
| Claude integration | First-class | Via LangChain |
| Learning curve | Smooth | Steeper |
| Documentation | Growing | Mature |

**Decision**: Use PydanticAI + AtomicAgents for individual agent implementations.

**Rationale**:
- Type safety built-in (matches Python 3.10+ ecosystem)
- Native async support (FastAPI requirement)
- Direct Anthropic Claude integration
- Simpler agent definitions than traditional frameworks

**Risk & Mitigation**:
- Risk: Smaller community than LangChain
- Mitigation: Wrap PydanticAI agents in LangGraph for orchestration, provide internal documentation

---

## Core Decision: AI/ML Stack

### Why Anthropic Claude Only?

**Considered Options**:
1. Claude + GPT-4 (multi-model)
2. Claude + Open-source LLM (cost optimization)
3. Fine-tuned Claude (specialized ingredients model)
4. Traditional ML (keyword matching, taxonomy)

**Decision**: Anthropic Claude exclusively, no fine-tuning in phase 1.

**Rationale**:
- Claude's food/recipe understanding is strong (trained on diverse web data)
- API costs predictable and reasonable for 10-user MVP
- No infrastructure cost for model hosting
- Ingredient substitution use case fits Claude's strengths
- Can add fine-tuning in phase 2 if ROI justifies it

**Cost Model**:
- Input token cost: ~$0.003/1K tokens
- Output token cost: ~$0.015/1K tokens
- Estimated usage: ~1000 tokens per ingredient substitution = ~$0.02/request
- At 100 users making 10 meal plans/month: ~$2000/month API cost
- Acceptable for MVP; reassess at scale

**Fallback Strategy** (if API costs spike):
- Cache common substitutions in PostgreSQL
- Use rule-based fallback for common ingredients
- Implement request batching

---

## Core Decision: Backend Framework

### FastAPI Selection

| Criterion | FastAPI | Django | Flask | Quart |
|-----------|---------|--------|-------|-------|
| Async-first | ✅ | ⚠️ (async possible) | ❌ | ✅ |
| Validation | Built-in (Pydantic) | Django ORM | Manual | Manual |
| Performance | Excellent | Good | Excellent | Excellent |
| Learning curve | Moderate | Steep | Very low | Moderate |
| Event bus integration | Simple | Possible | Simple | Simple |
| Docs auto-generation | OpenAPI 3.0 | Manual | Manual | Manual |

**Decision**: FastAPI for all backend services.

**Rationale**:
- Async-first architecture matches event-driven agents
- Pydantic validation aligns with PydanticAI
- Automatic OpenAPI documentation (helps API clients, testing)
- Modern Python (3.8+ required, which is standard)
- Uvicorn ASGI server is battle-tested

**Architecture**:
```
FastAPI App
├── /api/v1/recipes - Recipe endpoints
├── /api/v1/ingredients - Ingredient intelligence
├── /api/v1/mealplans - Meal planning
├── /api/v1/carts - Knuspr integration
├── /api/v1/users - User management
├── /health - Health check
└── /metrics - Prometheus metrics
```

---

## Core Decision: Data Storage

### PostgreSQL + Redis Strategy

**PostgreSQL Decision**:
- Relational schema for recipes, users, meal plans, carts
- JSON columns for flexible recipe metadata
- Row-level security for multi-tenant isolation
- ACID transactions for data integrity

**Schema Overview** (to be detailed in data-model.md):
```
users (id, email, password_hash, country, subscription_tier, created_at)
recipes (id, user_id, title, source_url, ingredients[], instructions[], metadata)
meal_plans (id, user_id, start_date, end_date, meals[], constraints, created_at)
grocery_carts (id, user_id, meal_plan_id, items[], knuspr_order_id, status)
ingredients (name, category, substitutes[], allergens[], seasonal_availability)
knuspr_credentials (user_id, login, password_encrypted, country, created_at)
```

**Redis Decision** (Phase 1: optional, Phase 2: required):
- Currently: Optional for cache/session store
- Phase 2: Required for message queue (replacing simple event bus)
- Strategy: Redis cluster with persistence (RDB + AOF)
- TTL strategy: Cache 24-hour meal plans, 1-hour session tokens

**Rationale**:
- PostgreSQL guarantees data integrity (critical for user data)
- JSON support allows flexible recipe metadata
- Row-level security provides multi-tenant isolation
- Redis prepares for scaling (caching + queuing)
- Combined approach avoids distributed consensus problems

---

## Core Decision: Event Bus / Message Queue

### Phase 1: Simple Pub/Sub (FastAPI Background Tasks + In-Memory)

For MVP with 10 users, we can use:
- Redis Pub/Sub (if Redis available)
- RabbitMQ (if external message broker preferred)
- Python background tasks + database polling (no external dependencies)

**Decision for Phase 1**: Use FastAPI background tasks + Redis Pub/Sub (if Redis available).

**Decision for Phase 2+**: Upgrade to RabbitMQ or Redis Streams for higher throughput.

**Event Envelope** (matches contracts/README.md):
```json
{
  "eventType": "domain.entity.action",
  "eventId": "uuid-v4",
  "timestamp": "2025-11-14T10:30:00Z",
  "correlationId": "uuid-for-request-tracing",
  "source": {
    "agentId": "agent-id",
    "agentType": "agent-type",
    "version": "1.0.0"
  },
  "payload": { /* ... */ },
  "metadata": {
    "retryCount": 0,
    "priority": "normal",
    "ttl": 3600
  }
}
```

**Topic Structure**:
```
recipe.*          → Recipe Harvester agents
ingredient.*      → Ingredient Intelligence agents
mealplan.*        → Meal Architect agent
cart.*            → Cart Optimizer agents
*.failed          → Error handler / dead letter queue
```

---

## Core Decision: Recipe Harvesting

### Web Scraping Technology

**Considered Options**:
1. **Puppeteer (browser automation)** - JavaScript engine, schema.org detection
2. **Scrapy (Python framework)** - Mature, but synchronous
3. **BeautifulSoup + Selenium** - Fine-grained control, but slow
4. **Knuspr/Rohlik API** - Not suitable for external recipe sources
5. **AI-powered extraction (Claude)** - Flexible, but expensive

**Decision**: Puppeteer for dynamic sites, simple HTTP for static content, Claude for edge cases.

**Rationale**:
- Puppeteer handles JavaScript-heavy recipe sites (common for modern blogs)
- Falls back to BeautifulSoup for static HTML
- Claude handles ambiguous/malformed recipes (expensive but rare)
- Ottolenghi recipes mostly static, so simple HTTP should work

**Implementation**:
```python
async def harvest_recipe(url: str) -> Recipe:
    # Try simple HTTP first
    content = await http_get(url)
    recipe = parse_recipe_html(content)

    if recipe is None:
        # Fall back to Puppeteer for JavaScript sites
        content = await puppeteer_fetch(url)
        recipe = parse_recipe_html(content)

    if recipe is None:
        # Last resort: Claude analysis
        recipe = await claude_extract_recipe(url, content)

    return recipe
```

**Rate Limiting**:
- Max 5 concurrent scrapes (Puppeteer resource limit)
- 1-second delay between requests (respect server load)
- Retry with exponential backoff on failure
- Cache results for 24 hours

---

## Core Decision: Constraint Solver for Meal Planning

### Z3 vs OR-Tools

| Criterion | Z3 | OR-Tools | Greedy |
|-----------|----|---------|----|
| Constraint power | Excellent | Excellent | Limited |
| Solve time | Milliseconds to seconds | Milliseconds to seconds | Milliseconds |
| Meal plan complexity | High (5+ constraints) | High (5+ constraints) | Low (1-2 constraints) |
| Learning curve | Moderate | Moderate | Easy |
| Python integration | Good | Excellent | Built-in |

**Decision**: Z3 for MVP, evaluate OR-Tools for phase 2.

**Rationale**:
- Z3 has Python bindings via `z3-solver` package
- Sufficient for typical meal plan constraints (7-14 meals, 50+ recipes)
- Proven in similar systems
- Can upgrade to OR-Tools if solve time becomes bottleneck

**Constraints to Implement**:
```
1. X meals per week (dinner only for MVP)
2. Max prep/cook time budget
3. Dietary preferences (vegetarian, vegan, gluten-free)
4. Exclude ingredients (allergies, preferences)
5. Maximize ingredient reuse (minimize waste)
6. Variety (no recipe repeat in 14 days)
```

**Performance Target**: <5 seconds for typical 7-day plan.

---

## Core Decision: Monitoring & Observability

### Prometheus + Grafana Stack

**Why Prometheus?**
- Industry standard for cloud-native monitoring
- Time-series database optimized for metrics
- Strong Python client library
- Integrates with Grafana for dashboards
- Alerting via AlertManager
- Free and open-source

**Metrics to Collect** (Phase 1):
```
# Agent Metrics
agent_requests_total{agent_type, status}
agent_request_duration_seconds{agent_type, quantile}
agent_errors_total{agent_type, error_type}

# API Metrics
api_requests_total{endpoint, method, status}
api_request_duration_seconds{endpoint, quantile}

# Database Metrics
db_query_duration_seconds{operation}
db_connections_total

# Knuspr Integration Metrics
knuspr_api_calls_total{operation, status}
knuspr_api_cost_usd{operation}

# Business Metrics
recipes_harvested_total
meal_plans_generated_total
users_active_total
```

**Dashboards** (to be created):
1. Agent Health (success rate, latency, errors)
2. API Performance (throughput, latency by endpoint)
3. Database (connections, query time, table sizes)
4. Knuspr Integration (call volume, cost, errors)
5. Business (users, recipes, meal plans)

---

## Core Decision: Deployment & Containerization

### Docker Composition Strategy

**Phase 1: Docker Compose (Single Server or Local)**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: recipes
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  fastapi:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://...
      REDIS_URL: redis://redis:6379
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

**Phase 2: Kubernetes Deployment** (using Agno or Google ADK):
- One pod per agent type (scalable independently)
- Stateless FastAPI servers (multiple replicas)
- PostgreSQL as managed service (Cloud SQL, RDS, etc.)
- Redis cluster for HA
- Prometheus as sidecar or external service

**Container Strategy**:
- Single base image for all agents (Python 3.11 slim)
- Multi-stage builds to minimize image size
- Environment variables for configuration
- Health check endpoints in all services

---

## Core Decision: Frontend Technology Stack

### Mobile-First Web App

**Framework Options**:
1. **React** - Largest ecosystem, most jobs
2. **Vue** - Easier learning curve, great for small teams
3. **Svelte** - Best performance, smallest bundle

**Decision**: TBD in planning phase, recommend React or Vue.

**MVP Requirements**:
- Authentication (login, signup, logout)
- Recipe search and details
- Meal plan creation and review
- Cart preview (read-only, editing in Knuspr)
- User preferences (dietary, country)

**Tech Stack** (tentative):
- Framework: React 18 or Vue 3
- Routing: React Router or Vue Router
- State: TanStack Query or Pinia
- Styling: Tailwind CSS (mobile-first utility classes)
- Forms: React Hook Form or VeeValidate
- Build: Vite or Create React App

**Mobile-First Strategy**:
- Start with 375px viewport (iPhone SE)
- Breakpoints: 375px (mobile), 768px (tablet), 1024px (desktop)
- Touch-friendly buttons (min 44x44px)
- Responsive images (srcset for different DPIs)
- Progressive enhancement (works without JavaScript)

---

## Risk Assessment & Mitigation

### High-Risk Decisions

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Anthropic API quota limits | Low | Medium | Cache substitutions, rule-based fallback |
| LangGraph breaking changes | Very Low | High | Pin versions, maintain fork if needed |
| Puppeteer performance | Medium | Medium | Async workers, queue management |
| PostgreSQL scaling limits | Low | High | Plan migration to cloud DB early |
| Knuspr API instability | Low | High | Fallback to manual cart, detailed logging |

### Low-Risk Decisions
- FastAPI (mature, battle-tested)
- PostgreSQL (industry standard)
- Docker (standard practice)
- Prometheus (industry standard)

---

## Technology Debt & Upgrade Path

### Phase 1 → Phase 2 Upgrades
| Component | Phase 1 | Phase 2 |
|-----------|---------|---------|
| Message Queue | FastAPI tasks | Redis Streams / RabbitMQ |
| Agent Scaling | Single instance | Multiple replicas + load balancing |
| Caching | Optional Redis | Required Redis cluster |
| Deployment | Docker Compose | Kubernetes + Agno |
| Monitoring | Prometheus basic | Prometheus + Grafana + AlertManager |
| ML | Claude API only | Cache + fine-tuning pipeline |

### Technical Debt to Avoid
- ❌ Don't skip contract testing (multi-agent complexity requires it)
- ❌ Don't defer monitoring setup (hard to add later)
- ❌ Don't optimize prematurely (10 users don't need Redis yet)
- ❌ Don't hardcode configuration (use environment variables)
- ❌ Don't skip security review (credentials in this system)

---

## Next Steps

1. ✅ Complete this research document
2. ⏭️ Generate detailed implementation plan (plan.md)
3. ⏭️ Design data model (data-model.md)
4. ⏭️ Create task breakdown (tasks.md)
5. ⏭️ Begin development with task #1

---

**Decision Authority**: Technical Lead
**Last Reviewed**: 2025-11-14
**Next Review**: Before Phase 2 planning (estimated Q1 2026)
