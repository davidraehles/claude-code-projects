# meal-planner Development Guidelines

**Last Updated**: December 2025
**Branch**: `002-multi-agent-recipe-app`
**Phase**: MVP - Meal Planning & Grocery Integration

## Quick Navigation

- **Backend**: Python 3.11+ FastAPI in `/backend/app/`
- **Frontend**: React 19 + Next.js 16 in `/frontend/`
- **Tests**: Unit tests in `/backend/tests/`, E2E in `/frontend/e2e/`
- **Specs**: Architecture & decisions in `/specs/002-multi-agent-recipe-app/`
- **Agents**: Local & awesome-copilot agents in `.github/agents/`

## 📚 Coding Standards & Instructions

**CRITICAL**: Before generating code, ALWAYS refer to the specific instruction file for the domain you are working in. These files contain the source of truth for coding standards.

| Domain | Instruction File | Key Focus |
|--------|------------------|-----------|
| **Next.js** | `.github/instructions/nextjs.instructions.md` | App Router, Server Components, Project Structure |
| **React** | `.github/instructions/reactjs.instructions.md` | Hooks, Functional Components, TypeScript |
| **Python** | `.github/instructions/python.instructions.md` | PEP 8, Pydantic V2, Type Hints |
| **Testing** | `.github/instructions/playwright-typescript.instructions.md` | Locators, Assertions, E2E Structure |
| **Security** | `.github/instructions/security-and-owasp.instructions.md` | OWASP Top 10, Auth, Input Validation |
| **Performance** | `.github/instructions/performance-optimization.instructions.md` | Optimization strategies for all layers |
| **Docker** | `.github/instructions/containerization-docker-best-practices.instructions.md` | Image optimization, Security |

## Active Technologies

### Backend Stack
- **Language**: Python 3.11+ with async/await
- **Framework**: FastAPI 0.104+ with Pydantic V2
- **Database**: PostgreSQL 16+ with SQLAlchemy 2.0 async, Alembic migrations
- **Agents**: LangGraph, LangChain, PydanticAI, AtomicAgents
- **Testing**: pytest with async fixtures, coverage reporting

### Frontend Stack
- **Language**: TypeScript 5.x (strict mode)
- **Framework**: Next.js 16 with React 19 (App Router)
- **Architecture**: Model-View-Intent (MVI) pattern
- **Styling**: Tailwind CSS 3.x, Framer Motion, GSAP (60fps target)
- **Forms**: React Hook Form 7.x + Zod validation
- **State**: React Query (TanStack Query)
- **Testing**: Jest, React Testing Library, Playwright E2E

### Infrastructure
- **Containerization**: Docker Compose (MVP), Kubernetes (Phase 2)
- **Deployment**: Railway (backend), Vercel (frontend), Neon PostgreSQL
- **CI/CD**: GitHub Actions (planned)
- **Monitoring**: Prometheus, Sentry (Phase 2)

### MCP Servers
- **awesome-copilot**: Custom agent team (10 specialized agents)
- **rohlik-mcp**: Grocery API integration
- **github-mcp**: Repository operations

## Available Agents

### 🚀 Beast Mode Agent
**Location**: [beast-mode-agent.md](beast-mode-agent.md)
**Specialty**: High-performance optimization, bottleneck elimination
**Activation**: @beast-mode or "Beast Mode, optimize this!"
**Domain**: Algorithm analysis, async optimization, DB queries, caching, infrastructure

### 🎨 Frontend Specialist
**Location**: [frontend-specialist-agent.md](frontend-specialist-agent.md)
**Specialty**: React 19, Next.js 16, UI/UX, accessibility, testing
**Activation**: @frontend-specialist or "Review my React component"
**Expertise**: Server/Client Components, TypeScript, Tailwind, WCAG 2.1 AA

### 🏗️ Backend Specialist
**Location**: [backend-specialist-agent.md](backend-specialist-agent.md)
**Specialty**: FastAPI, Python async patterns, database design, microservices
**Activation**: @backend-specialist or "Design an API endpoint"
**Expertise**: SQLAlchemy async, Pydantic validation, error handling, testing

## Awesome-Copilot Custom Agents

Located in [awesome-copilot/](awesome-copilot/) directory. These agents enhance team expertise:

### 1. Expert Next.js Developer [HIGH PRIORITY]
**File**: [awesome-copilot/expert-nextjs-developer.agent.md](awesome-copilot/expert-nextjs-developer.agent.md)
**Specialization**: App Router, Server Components, Cache Components, Turbopack, metadata, SEO
**When to Use**: Setting up pages, data fetching strategies, performance optimization, deployment
**Activation**: @expert-nextjs-developer

### 2. Expert React Frontend Engineer [HIGH PRIORITY]
**File**: [awesome-copilot/expert-react-frontend-engineer.agent.md](awesome-copilot/expert-react-frontend-engineer.agent.md)
**Specialization**: React 19.2 hooks, Server Components, Actions, concurrent rendering, TypeScript
**When to Use**: Component design, state management, performance optimization, testing
**Activation**: @expert-react-frontend-engineer

### 3. PostgreSQL Database Administrator [HIGH PRIORITY]
**File**: [awesome-copilot/postgresql-dba.agent.md](awesome-copilot/postgresql-dba.agent.md)
**Specialization**: Schema design, query optimization, indexing, performance monitoring, backups
**When to Use**: Database design, query optimization, performance issues, migrations
**Activation**: @postgresql-dba

### 4. Accessibility Expert [MEDIUM PRIORITY]
**File**: [awesome-copilot/accessibility-expert.agent.md](awesome-copilot/accessibility-expert.agent.md)
**Specialization**: WCAG 2.1/2.2 compliance, semantic HTML, ARIA, keyboard navigation, screen readers
**When to Use**: Accessibility reviews, form design, testing, compliance verification
**Activation**: @accessibility-expert

### 5. Playwright Tester Mode [MEDIUM PRIORITY]
**File**: [awesome-copilot/playwright-tester.agent.md](awesome-copilot/playwright-tester.agent.md)
**Specialization**: E2E testing with Playwright/TypeScript, test generation, reliability
**When to Use**: Writing E2E tests, test debugging, test structure design
**Activation**: @playwright-tester

### 6. API Architect [MEDIUM PRIORITY]
**File**: [awesome-copilot/api-architect.agent.md](awesome-copilot/api-architect.agent.md)
**Specialization**: REST API design, three-layer architecture, resilience patterns, design patterns
**When to Use**: API endpoint design, resilience implementation, API documentation
**Activation**: @api-architect

### 7. Security Expert [STRATEGIC]
**File**: [awesome-copilot/security-expert.agent.md](awesome-copilot/security-expert.agent.md)
**Specialization**: OWASP Top 10, authentication, encryption, LLM security, vulnerability assessment
**When to Use**: Security reviews, threat modeling, compliance, vulnerability analysis
**Activation**: @security-expert

### 8. DevOps / CI-CD Expert [STRATEGIC]
**File**: [awesome-copilot/devops-expert.agent.md](awesome-copilot/devops-expert.agent.md)
**Specialization**: GitHub Actions, Kubernetes, Docker, monitoring, deployment strategies, cloud platforms
**When to Use**: CI/CD pipeline setup, deployment strategy, infrastructure design, monitoring
**Activation**: @devops-expert

### 9. ADR Generator [STRATEGIC]
**File**: [awesome-copilot/adr-generator.agent.md](awesome-copilot/adr-generator.agent.md)
**Specialization**: Architectural Decision Records, decision documentation, alternatives analysis
**When to Use**: Documenting architectural decisions, ADR generation, design reviews
**Activation**: @adr-generator

### 10. Terraform / IaC Expert [STRATEGIC]
**File**: [awesome-copilot/terraform-expert.agent.md](awesome-copilot/terraform-expert.agent.md)
**Specialization**: Infrastructure as Code, Kubernetes provisioning, cloud platforms, GitOps
**When to Use**: Phase 2 Kubernetes setup, infrastructure automation, cloud migration
**Activation**: @terraform-expert

## Quick Commands

### Backend (from `/backend/`)
```bash
# Run containers
docker-compose up -d

# Run tests
docker exec -it recipe-api pytest tests/ -v

# Database migrations
docker exec -it recipe-api alembic upgrade head

# Lint & format
docker exec -it recipe-api black app/ tests/
docker exec -it recipe-api flake8 app/ tests/ --max-line-length=120
docker exec -it recipe-api mypy app/

# View logs
docker logs -f recipe-api
```

### Frontend (from `/frontend/`)
```bash
# Development
npm run dev

# Build
npm run build

# Tests
npm test
npm run test:e2e

# Lint & format
npm run lint
npm run format

# Performance analysis
npm run analyze
```

## Code Style Guidelines

### Python (Backend)
> **Ref**: `.github/instructions/python.instructions.md`
- **Async First**: Use `async/await` for all I/O operations (DB, API calls).
- **Validation**: Use **Pydantic V2** for all data schemas.
- **Typing**: Strict type hints required (mypy).
- **Style**: PEP 8 + Black (120 chars). Google-style docstrings.
- **Error Handling**: Use custom exceptions with context; never swallow errors.

### TypeScript (Frontend)
> **Ref**: `.github/instructions/nextjs.instructions.md` & `.github/instructions/reactjs.instructions.md`
- **Strict Mode**: `strict: true` is non-negotiable.
- **Architecture**: Model-View-Intent (MVI) pattern required for all new features.
- **React 19**: Use Server Components by default. Use `'use client'` only when necessary (interactivity/hooks).
- **No `next/dynamic` SSR hacks**: Follow the `nextjs.instructions.md` for Client/Server component composition.
- **Naming**: `PascalCase` for components, `camelCase` for hooks/utils.
- **Forms**: React Hook Form + Zod.

## Testing Guidelines

### Backend
- **Framework**: `pytest` with `pytest-asyncio`.
- **Coverage**: >80% for new logic.
- **Fixtures**: Use `conftest.py` for shared async fixtures.

### Frontend (E2E & Unit)
> **Ref**: `.github/instructions/playwright-typescript.instructions.md`
- **Locators**: Use **user-facing locators** (`getByRole`, `getByText`) ONLY. Avoid CSS selectors.
- **Assertions**: Use auto-retrying web-first assertions (`await expect(locator).toBeVisible()`).
- **Structure**: Group tests with `test.describe`. Use `test.step` for clarity.
- **Accessibility**: Integrate `axe-core` checks in E2E tests.

## Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/description`
2. **Make Changes**: Follow code style guidelines
3. **Test Locally**: Run tests, linting, formatters
4. **Use Agents**: Leverage awesome-copilot agents for reviews
5. **Create PR**: Reference issue, add test results
6. **Address Reviews**: Iterate based on feedback
7. **Merge**: Squash or rebase, delete branch

## Performance Targets

- **Frontend**: Lighthouse score >95 (performance, accessibility, best practices, SEO)
- **API Response**: <200ms p95 (measured at prod scale)
- **Database Queries**: <50ms p95 (indexed properly)
- **Bundle Size**: <100KB gzipped (main React app)
- **Core Web Vitals**: LCP <2.5s, FID <100ms, CLS <0.1

## Deployment & Environments

### Backend (Railway)
- **Staging**: Auto-deployed from `001-grocery-list-generation` branch
- **Production**: Manual deployment from release tags
- **Database**: Neon PostgreSQL (auto-backups)
- **Monitoring**: Sentry for error tracking

### Frontend (Vercel)
- **Staging**: Auto-deployed from `001-grocery-list-generation` branch
- **Production**: Auto-deployed from release tags
- **Analytics**: Built-in Next.js Analytics

## Key Features & Ownership

| Feature | Agent | Files | Status |
|---------|-------|-------|--------|
| Grocery List Generation | Meal Architect + API Architect | `/backend/app/agents/meal_architect.py` | MVP |
| Recipe Harvesting | Recipe Harvester | `/backend/app/agents/recipe_harvester.py` | MVP |
| Cart Optimization | Cart Optimizer | `/backend/app/agents/cart_optimizer.py` | MVP |
| Accessibility | Accessibility Expert | `/frontend/src/**/*.tsx` | In Progress |
| Performance | Beast Mode Agent | All layers | Continuous |

## Resources

- **Architecture**: [specs/002-multi-agent-recipe-app/](../../specs/002-multi-agent-recipe-app/)
- **Security**: [SECURITY_MIDDLEWARE_IMPLEMENTATION_REPORT.md](../../backend/SECURITY_MIDDLEWARE_IMPLEMENTATION_REPORT.md)
- **Deployment**: [docs/DEPLOYMENT_RAILWAY.md](../../docs/DEPLOYMENT_RAILWAY.md)
- **Specification**: [CLAUDE.md](../../CLAUDE.md)

## Phase Roadmap

### Phase 1 (Current): MVP
- ✅ Grocery list generation
- ✅ Recipe harvesting
- ✅ Cart optimization
- 🚧 Accessibility compliance
- 🚧 Performance optimization

### Phase 2: Scale & Intelligence
- Kubernetes deployment
- Advanced caching (Redis)
- ML-based recommendations
- Advanced analytics
- Mobile app (React Native)

---

**Need help?** Mention the relevant awesome-copilot agent:
- "@expert-nextjs-developer" for Next.js/React questions
- "@postgresql-dba" for database queries
- "@api-architect" for API design
- "@security-expert" for security reviews
- "@devops-expert" for deployment questions
- "@beast-mode" for performance optimization
