# Multi-Agent Recipe System - Setup & Quickstart Guide

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Status**: Ready for Phase 1 Development

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Setup (5 minutes)](#quick-setup-5-minutes)
4. [Development Environment](#development-environment)
5. [Project Structure](#project-structure)
6. [Running Services](#running-services)
7. [Testing](#testing)
8. [Documentation Navigation](#documentation-navigation)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Multi-Agent Recipe and Meal Planning System** is a production-ready SaaS platform that:

- 🔍 **Harvests recipes** from multiple sources (Ottolenghi, APIs, RSS feeds)
- 🍽️ **Plans weekly meals** based on dietary constraints, time budget, and ingredient preferences
- 🛒 **Generates optimized grocery carts** via Knuspr integration
- 🤖 **Uses multi-agent architecture** with independent, scalable agents
- 📊 **Measures everything** with Prometheus monitoring from day one
- 👥 **Supports multiple users** with complete data isolation

**Tech Stack**:
- Backend: FastAPI (Python 3.10+) + PostgreSQL + Redis
- Agents: LangChain/LangGraph + PydanticAI + AtomicAgents
- AI: Anthropic Claude
- Monitoring: Prometheus + Grafana
- Container: Docker + Docker Compose
- Frontend: Next.js 16 + React 19 (mobile-first)

---

## Prerequisites

### Required
- **Python**: 3.10 or higher
  ```bash
  python --version  # Should show 3.10+
  ```

- **Docker & Docker Compose**
  ```bash
  docker --version   # 20.10+
  docker-compose --version  # 2.0+
  ```

- **Git**
  ```bash
  git --version
  ```

- **Anthropic API Key**
  - Get from https://console.anthropic.com/
  - Store in `.env` file (see setup below)

### Optional
- **PostgreSQL client** (for local DB testing)
  ```bash
  psql --version  # For manual queries
  ```

- **Redis CLI** (for cache testing)
  ```bash
  redis-cli --version
  ```

---

## Quick Setup (5 minutes)

### Step 1: Clone & Navigate to Project

```bash
cd /home/user/claude-code-projects
git status  # Verify you're on claude/multi-agent-recipe-planning-01SKWk1RPqGpxZUgCcjZ4umH
```

### Step 2: Create Environment File

```bash
cat > .env << 'EOF'
# Core Configuration
ENVIRONMENT=development
DEBUG=True

# Anthropic API (get from https://console.anthropic.com/)
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# PostgreSQL
DATABASE_URL=postgresql://recipes_user:recipes_password@localhost:5432/recipes_db
DATABASE_ECHO=True  # Log SQL queries in dev

# Redis
REDIS_URL=redis://localhost:6379/0

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_WORKERS=4

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-secret-key-here-replace-with-random-32-char-hex
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=1

# Prometheus
PROMETHEUS_PORT=9090

# Logging
LOG_LEVEL=INFO
EOF

cat .env  # Verify content
```

### Step 3: Start Services with Docker Compose

```bash
# Build and start all services in background
docker-compose up -d

# Check services are running
docker-compose ps

# Expected output:
# NAME                 STATUS
# postgres            Up (healthy)
# redis               Up
# fastapi             Up
# prometheus          Up
```

### Step 4: Initialize Database

```bash
# Run migrations
docker-compose exec fastapi alembic upgrade head

# Seed initial data (ingredient taxonomy, etc.)
docker-compose exec fastapi python scripts/seed_data.py
```

### Step 5: Verify Setup

```bash
# API health check
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-11-14T..."}

# Prometheus metrics
curl http://localhost:9090/api/v1/targets

# PostgreSQL connection
docker-compose exec postgres psql -U recipes_user -d recipes_db -c "SELECT COUNT(*) FROM users;"
```

**You're done! 🎉 Services are running.**

---

## Development Environment

### IDE Setup

#### VS Code (Recommended)
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```

#### PyCharm
1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Docker Compose"
4. Service: "fastapi"

### Virtual Environment (for local Python work)

```bash
# Create venv
python -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt
```

### Install Git Hooks (Pre-commit checks)

```bash
# Install pre-commit
pip install pre-commit

# Configure hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## Project Structure

```
/home/user/claude-code-projects/
├── specs/                          # Specification documents
│   ├── 001-landing-page-redesign/  # (Other project)
│   └── 002-multi-agent-recipe-app/
│       ├── spec.md                 # Requirements & user stories
│       ├── constitution.md         # Architectural principles
│       ├── research.md             # Technology decisions
│       ├── data-model.md           # Database schema
│       ├── plan.md                 # 12-week implementation plan
│       └── contracts/
│           └── README.md           # Agent interfaces & event contracts
│
├── src/                            # Application source code (Phase 1)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── auth.py             # Login, signup, logout
│   │   │   ├── recipes.py          # Recipe CRUD, search
│   │   │   ├── mealplans.py        # Meal plan generation, update
│   │   │   ├── carts.py            # Shopping cart operations
│   │   │   └── health.py           # Health check, metrics
│   │   ├── dependencies.py         # FastAPI dependencies
│   │   └── main.py                 # FastAPI app initialization
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                 # Agent base class
│   │   ├── recipe_harvester.py     # Recipe harvesting agents
│   │   ├── ingredient_intelligence.py  # Substitution & classification
│   │   ├── meal_architect.py       # Meal planning agent
│   │   └── cart_optimizer.py       # Knuspr integration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User Pydantic models
│   │   ├── recipe.py               # Recipe models
│   │   ├── mealplan.py             # Meal plan models
│   │   └── cart.py                 # Cart models
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── session.py              # Database session management
│   │   └── alembic/
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   │           └── 001_create_users_table.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py                 # User authentication
│   │   ├── recipe.py               # Recipe business logic
│   │   ├── mealplan.py             # Meal planning logic
│   │   └── knuspr.py               # Knuspr API integration
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── schemas.py              # Event type definitions
│   │   ├── bus.py                  # Event bus implementation
│   │   └── handlers.py             # Event handlers
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py              # Structured logging
│   │   ├── metrics.py              # Prometheus metrics
│   │   └── validation.py           # Input validation
│   │
│   └── config.py                   # Configuration from .env
│
├── tests/
│   ├── unit/                       # Unit tests
│   │   ├── test_agents.py
│   │   ├── test_services.py
│   │   └── test_models.py
│   ├── integration/                # Integration tests
│   │   ├── test_agent_workflows.py
│   │   ├── test_db.py
│   │   └── test_api.py
│   ├── e2e/                        # End-to-end tests
│   │   └── test_user_workflows.py
│   └── conftest.py                 # Pytest fixtures
│
├── scripts/
│   ├── seed_data.py                # Initialize ingredient taxonomy
│   ├── create_user.py              # Create test user
│   └── reset_db.py                 # Reset database
│
├── docker/
│   ├── Dockerfile                  # FastAPI service
│   └── Dockerfile.agent            # Agent service (future)
│
├── k8s/                            # Kubernetes manifests (Phase 2)
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
│
├── docker-compose.yml              # Local development stack
├── docker-compose.prod.yml         # Production stack (Phase 2)
├── .env.example                    # Environment template
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── .gitignore
├── README.md                       # Main project README
├── Makefile                        # Development shortcuts
└── pytest.ini                      # Pytest configuration
```

---

## Running Services

### Start All Services

```bash
# Background (detached) mode
docker-compose up -d

# Foreground mode (see logs)
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f fastapi        # API logs
docker-compose logs -f postgres       # Database logs
docker-compose logs -f redis          # Cache logs
docker-compose logs -f prometheus     # Metrics logs
```

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **FastAPI** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **Prometheus** | http://localhost:9090 | Metrics & dashboards |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache & message queue |

### Database Migrations

```bash
# Create new migration
docker-compose exec fastapi alembic revision --autogenerate -m "Add user table"

# Apply migrations
docker-compose exec fastapi alembic upgrade head

# Rollback one migration
docker-compose exec fastapi alembic downgrade -1

# Check migration status
docker-compose exec fastapi alembic current
```

### Running Tests

```bash
# Run all tests
docker-compose exec fastapi pytest

# Run with coverage
docker-compose exec fastapi pytest --cov=src --cov-report=html

# Run specific test file
docker-compose exec fastapi pytest tests/unit/test_agents.py

# Run with verbose output
docker-compose exec fastapi pytest -v

# Run only integration tests
docker-compose exec fastapi pytest tests/integration/
```

---

## Testing

### Test Structure

```
tests/
├── unit/
│   └── test_agents.py
│       ├── TestRecipeHarvester
│       │   ├── test_harvest_valid_url
│       │   ├── test_harvest_invalid_url
│       │   └── test_normalize_recipe
│       └── TestIngredientIntelligence
│           ├── test_classify_ingredient
│           └── test_suggest_substitutions
├── integration/
│   └── test_agent_workflows.py
│       ├── TestMealPlanGeneration
│       │   ├── test_full_workflow
│       │   └── test_event_bus_communication
│       └── TestDatabaseOperations
└── conftest.py  # Shared fixtures
```

### Writing Tests

```python
# tests/unit/test_agents.py
import pytest
from src.agents.recipe_harvester import RecipeHarvester

@pytest.fixture
def harvester():
    return RecipeHarvester()

def test_harvest_valid_url(harvester):
    """Test harvesting from valid recipe URL"""
    recipe = harvester.harvest("https://ottolenghi.com/...")
    assert recipe.title is not None
    assert len(recipe.ingredients) > 0
    assert len(recipe.instructions) > 0
```

### Coverage Target

- **Minimum**: 80% code coverage
- **Critical paths**: 100% (agent logic, auth, data isolation)
- **UI components**: 60% (acceptable for frontend)

```bash
# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Documentation Navigation

### For Understanding the Project

1. **Start here**: [spec.md](specs/002-multi-agent-recipe-app/spec.md)
   - What are we building?
   - Who are the users?
   - What's the success criteria?

2. **Architecture**: [constitution.md](specs/002-multi-agent-recipe-app/constitution.md)
   - Why this architecture?
   - Core principles
   - Governance rules

3. **Tech decisions**: [research.md](specs/002-multi-agent-recipe-app/research.md)
   - Why FastAPI, not Django?
   - Why LangChain/LangGraph?
   - Risk assessment

### For Building Features

4. **Database design**: [data-model.md](specs/002-multi-agent-recipe-app/data-model.md)
   - Entity definitions
   - SQL schemas
   - Validation rules

5. **Agent contracts**: [contracts/README.md](specs/002-multi-agent-recipe-app/contracts/README.md)
   - Agent event schemas
   - Event bus patterns
   - Orchestration workflows

### For Implementation

6. **Week-by-week plan**: [plan.md](specs/002-multi-agent-recipe-app/plan.md)
   - Phase 1A-1F (Foundation)
   - Phase 2A-2D (Orchestration)
   - Phase 3-5 (Full system)

---

## Common Tasks

### Create a New API Endpoint

```python
# src/api/routes/recipes.py
from fastapi import APIRouter, Depends
from src.models.recipe import RecipeResponse
from src.services.recipe import get_recipes

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/", response_model=list[RecipeResponse])
async def list_recipes(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    """List user's recipes"""
    return await get_recipes(current_user.id, skip, limit)
```

### Add a Database Migration

```bash
# Create migration
docker-compose exec fastapi alembic revision --autogenerate -m "Add recipe_source_url"

# Edit the generated file in src/db/alembic/versions/

# Apply it
docker-compose exec fastapi alembic upgrade head
```

### Test an Agent in Isolation

```python
# tests/unit/test_recipe_harvester.py
@pytest.mark.asyncio
async def test_harvest_ottolenghi_recipe():
    harvester = RecipeHarvester()
    recipe = await harvester.harvest("https://ottolenghi.com/recipes/...")

    assert recipe.title == "Expected Title"
    assert len(recipe.ingredients) >= 1
```

### Monitor Agent Performance

```bash
# View Prometheus metrics
curl http://localhost:9090/api/v1/query?query=agent_requests_total

# View in Grafana (once dashboards created)
# http://localhost:3000 (username: admin, password: admin)
```

### Debug Event Bus

```python
# Subscribe to all events (debug script)
import asyncio
from src.events.bus import event_bus

async def debug_events():
    async def handler(event):
        print(f"EVENT: {event.eventType} - {event.payload}")

    await event_bus.subscribe("*", handler)
    await asyncio.sleep(3600)  # 1 hour

asyncio.run(debug_events())
```

---

## Troubleshooting

### PostgreSQL Connection Fails

```bash
# Check if database is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Try manual connection
docker-compose exec postgres psql -U recipes_user -d recipes_db -c "SELECT 1"

# Reset database (WARNING: deletes all data)
docker-compose down -v  # Remove volumes
docker-compose up -d postgres
```

### Redis Connection Fails

```bash
# Check Redis status
docker-compose exec redis redis-cli ping
# Should return: PONG

# Clear Redis cache (for debugging)
docker-compose exec redis redis-cli FLUSHDB
```

### API Returns 500 Error

```bash
# Check API logs
docker-compose logs fastapi --tail=50

# Check database logs
docker-compose logs postgres --tail=20

# Restart API service
docker-compose restart fastapi
```

### Tests Fail with "ModuleNotFoundError"

```bash
# Rebuild Docker image
docker-compose build fastapi

# Restart
docker-compose restart fastapi

# Retry tests
docker-compose exec fastapi pytest
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process or change port in .env
# FASTAPI_PORT=8001
```

### Need to Debug a Specific Function

```python
# Add this to any Python file
import pdb; pdb.set_trace()

# In Docker container
docker-compose exec fastapi python -m pdb src/agents/recipe_harvester.py
```

---

## Development Workflow

### Daily Development Cycle

1. **Start day**: `docker-compose up -d`
2. **Make changes** to code in `src/`
3. **Run tests**: `docker-compose exec fastapi pytest`
4. **Check coverage**: `pytest --cov=src`
5. **Review logs**: `docker-compose logs fastapi`
6. **Commit**: `git add . && git commit -m "message"`
7. **End day**: `docker-compose down` (or keep running)

### Before Pushing to Branch

```bash
# Run all checks
docker-compose exec fastapi pytest --cov=src
docker-compose exec fastapi black src tests
docker-compose exec fastapi flake8 src tests
docker-compose exec fastapi mypy src

# Check git status
git status

# Push
git push origin branch-name
```

---

## Next Steps

1. ✅ Run this setup guide (you're here!)
2. ⏭️ Start [Phase 1A: Project Setup](specs/002-multi-agent-recipe-app/plan.md#phase-1-foundation--core-agents-weeks-1-4)
3. ⏭️ Review [Constitution](specs/002-multi-agent-recipe-app/constitution.md) before making architectural decisions
4. ⏭️ Refer to [Data Model](specs/002-multi-agent-recipe-app/data-model.md) when writing database code

---

## Quick Reference

### Essential Commands

```bash
# Docker
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f fastapi    # View logs
docker-compose exec fastapi bash  # Shell into container

# Testing
pytest                            # Run all tests
pytest --cov=src                  # With coverage
pytest tests/unit/                # Only unit tests

# Database
alembic revision --autogenerate -m "message"  # Create migration
alembic upgrade head              # Apply migrations
alembic downgrade -1              # Rollback

# Git
git status                        # Check status
git add .                         # Stage changes
git commit -m "message"           # Commit
git push origin branch-name       # Push to remote

# Code Quality
black src tests                   # Format code
flake8 src tests                  # Lint
mypy src                          # Type checking
```

---

## Support & Documentation

- **Questions about architecture?** → See [constitution.md](specs/002-multi-agent-recipe-app/constitution.md)
- **Questions about tech stack?** → See [research.md](specs/002-multi-agent-recipe-app/research.md)
- **Questions about database?** → See [data-model.md](specs/002-multi-agent-recipe-app/data-model.md)
- **Questions about implementation?** → See [plan.md](specs/002-multi-agent-recipe-app/plan.md)
- **Questions about agents?** → See [contracts/README.md](specs/002-multi-agent-recipe-app/contracts/README.md)

---

**Happy developing! 🚀**

For issues or questions, refer to the relevant spec document or create an GitHub issue with clear description.

---

**Last Updated**: 2025-11-14
**Status**: Ready for Phase 1 Development
