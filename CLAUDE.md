# AI Meal Planner - Development Guidelines

## Project Overview

AI-powered meal planning and recipe management application with multi-agent architecture:

- **Backend**: FastAPI (Python 3.11+) with LangGraph workflows and specialized AI agents
- **Frontend**: Next.js 16 with React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL with SQLAlchemy ORM (async)
- **AI Integration**: Anthropic Claude for intelligent features
- **Grocery Integration**: Knuspr MCP client for cart management
- **Agent System**: 8 specialized ReAct agents for parallelized development

## Project Structure

```
backend/                    # Python FastAPI backend
  app/
    agents/                # AI agents (recipe_harvester, meal_architect, cart_optimizer, etc.)
    api/                   # FastAPI routes and endpoints
    models/                # SQLAlchemy database models
    schemas/               # Pydantic validation schemas
    services/              # Business logic services
    workflows/             # LangGraph workflow orchestration
    utils/                 # Utility functions
  tests/                   # Backend tests (pytest, unit & integration)
  scripts/                 # Python scripts (seeding, verification)
  migrations/              # Alembic database migrations
  requirements.txt         # Python dependencies

frontend/                  # Next.js frontend
  src/
    app/                   # Next.js App Router pages (dashboard, generate, grocery-carts, etc.)
    components/            # React components (layout, recipe, ui)
    lib/                   # Utilities and API client
  e2e/                     # Playwright E2E tests
  __tests__/               # Jest unit tests

infrastructure/            # Docker, deployment configs, monitoring scripts
  docker/                  # Docker Compose configurations
  scripts/                 # Deployment and monitoring scripts

docs/                      # Project documentation
specs/                     # Feature specifications (Spec-Kit)
  001-grocery-list-generation/
  002-multi-agent-recipe-app/
  003-ai-meal-planner-chat/

.claude/                   # Claude Code configuration
  agents/                  # ReAct agent system (8 agents)
  commands/                # Custom slash commands
```

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest tests/
```

### Frontend
```bash
cd frontend
npm install
npm run dev
npm test
npx playwright test
```

### Infrastructure
```bash
cd infrastructure
docker-compose up -d
```

## Code Style

### Python (Backend)
- **Formatter**: Black (line length: 100)
- **Import Sorting**: isort
- **Type Checking**: pyright --strict
- **Linting**: pylint, flake8
- **Testing**: pytest with async support
- **Type Hints**: 100% coverage required
- **Async/Await**: All I/O operations must be async

### TypeScript (Frontend)
- **Formatter**: Prettier
- **Linting**: ESLint with strict rules
- **Type Mode**: TypeScript strict mode enabled
- **Testing**: Jest (unit), React Testing Library, Playwright (E2E)
- **Accessibility**: WCAG 2.1 AA compliance (Level AAA on mobile)

### Git Conventions
- **Commits**: Conventional commits (feat:, fix:, chore:, docs:, test:)
- **Branches**: Feature branches from `claude/main`
- **PRs**: Require all tests passing, type checking, and linting

## Features

### Active Features

1. **001-grocery-list-generation** (Branch: `001-grocery-list-generation`)
   - Status: Implementation in progress
   - Automated grocery list generation from meal plans
   - Ingredient aggregation and quantity scaling
   - Recipe and category view modes
   - Knuspr cart integration

2. **002-multi-agent-recipe-app** (Branch: `002-multi-agent-recipe-app`)
   - Status: Phase 1D complete, Phase 2 in progress
   - Multi-agent recipe harvesting (web, API, RSS, file import)
   - Ingredient intelligence and substitution
   - Meal plan generation with constraint satisfaction
   - Cart optimizer with Knuspr integration

3. **003-ai-meal-planner-chat** (Branch: `003-ai-meal-planner-chat`)
   - Status: Specification complete, implementation pending
   - Conversational AI meal planning interface
   - Voice input and output support
   - User preference persistence
   - Natural language meal plan generation

### Implemented Features

- User authentication (NextAuth.js)
- Recipe library with search and filtering
- Meal plan generation
- Grocery cart management
- Knuspr integration (MCP client)
- Multi-agent workflow orchestration

## Technology Stack

### Backend Core
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 16+ with SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic V2
- **Testing**: pytest, pytest-asyncio, pytest-cov

### AI/Agent Infrastructure
- **Agent Orchestration**: LangChain, LangGraph
- **Agent Frameworks**: PydanticAI, AtomicAgents
- **AI Models**: Anthropic Claude (via API)
- **Event Bus**: Redis Pub/Sub (prepared for future NATS/RabbitMQ)

### Specialized Agents (Backend)
- Recipe Harvester (web scraping, API, RSS, file import)
- Ingredient Intelligence (taxonomy, substitutions)
- Meal Architect (constraint satisfaction, planning)
- Cart Optimizer (Knuspr integration, optimization)

### Frontend Core
- **Language**: TypeScript 5.x
- **Framework**: Next.js 16 with React 19 (App Router)
- **Styling**: Tailwind CSS 3.x
- **Authentication**: NextAuth.js
- **State Management**: React Query (TanStack Query)
- **Forms**: React Hook Form + Zod validation
- **Testing**: Jest, React Testing Library, Playwright

### Infrastructure
- **Deployment**: Railway (backend), Vercel (frontend)
- **Monitoring**: Prometheus (metrics), custom scripts
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions (planned)

### Database Models
- User, Recipe, Ingredient, MealPlan, GroceryCart, CartItem
- Agent (capability tracking)
- UserProfile (preferences, dietary restrictions)

## Multi-Agent Development System

This project uses 8 specialized ReAct agents for parallelized development:

1. **Router Agent** - Task orchestration and parallelization
2. **Spec Analyzer Agent** - Requirement analysis
3. **Frontend Dev Agent** - React/Next.js implementation
4. **Backend Dev Agent** - Python/FastAPI implementation
5. **Testing & Quality Agent** - Test generation and QA
6. **Documentation Agent** - Spec synchronization
7. **Integration Agent** - Validation and merge readiness
8. **Agent Registry Manager** - Agent lifecycle management

See [.claude/agents/AGENT-REGISTRY.md](./.claude/agents/AGENT-REGISTRY.md) for detailed documentation.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Recent Changes
- 001-grocery-list-generation: Added PostgreSQL (existing models: GroceryCart, CartItem, MealPlan, Recipe, Ingredient)

- 2025-11-29: Multi-agent system registered (8 agents)
- 2025-11-29: Feature 001 (Grocery Lists) - Implementation plan complete

## Active Technologies
- PostgreSQL (existing models: GroceryCart, CartItem, MealPlan, Recipe, Ingredient) (001-grocery-list-generation)
