# Development Guide

Complete guide for developing and maintaining the meal planner application.

## Table of Contents
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Common Tasks](#common-tasks)
- [Performance Optimization](#performance-optimization)

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Quick Start

1. **Clone Repository**
```bash
git clone https://github.com/davidraehles/meal-planner.git
cd meal-planner
```

2. **Backend Setup**
```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
cp .env.local.example .env.local
```

4. **Start Services**
```bash
# Start all services with Docker
docker-compose up -d

# Or use VS Code tasks (Ctrl+Shift+B):
# - "Docker: Start All Services"
```

5. **Run Migrations**
```bash
docker exec -it recipe-api alembic upgrade head
```

6. **Verify**
```bash
# Backend: http://localhost:8000/health
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
```

---

## Project Structure

```
meal-planner/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # AI agents (CartOptimizer, etc.)
│   │   ├── api/            # REST API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── events/         # Event bus
│   │   └── monitoring/     # Metrics & observability
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # Test suite
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Pages (App Router)
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── public/
├── docs/                   # Documentation
├── infrastructure/         # Docker, monitoring
└── rohlik-mcp-temp/       # Knuspr MCP server
```

### Key Files

- `backend/app/main.py` - FastAPI app entry
- `backend/app/api/v1/router.py` - API router
- `frontend/src/app/layout.tsx` - Root layout
- `docker-compose.yml` - Service orchestration
- `.railway/services.json` - Railway deployment

---

## Development Workflow

### VS Code Tasks

Press `Ctrl+Shift+B` or `Cmd+Shift+B` to access:

**Docker:**
- Start All Services
- Stop All Services
- Rebuild and Start
- View API Logs
- View All Logs

**Testing:**
- Run All Tests
- Run Tests with Coverage
- Run Specific Test File

**Database:**
- Run Migrations
- Create New Migration
- Rollback Migration
- Reset Database

**Linting:**
- Run Black (Format)
- Run Flake8
- Run MyPy
- Run All Checks

**Shell Access:**
- Enter API Container
- PostgreSQL CLI
- Redis CLI

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# ... edit files ...

# Run tests
docker exec -it recipe-api pytest tests/ -v

# Lint code
docker exec -it recipe-api black app/ tests/
docker exec -it recipe-api flake8 app/ tests/ --max-line-length=120

# Commit
git add .
git commit -m "feat: your feature description"

# Push and create PR
git push origin feature/your-feature
```

### Environment Configuration

**Backend (`backend/.env`):**
```bash
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=recipe_app

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
```

**Frontend (`frontend/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Testing

### Backend Tests

**Run all tests:**
```bash
docker exec -it recipe-api pytest tests/ -v
```

**With coverage:**
```bash
docker exec -it recipe-api pytest tests/ --cov=app --cov-report=html
```

**Specific test file:**
```bash
docker exec -it recipe-api pytest tests/integration/test_cart_optimizer.py -v
```

**Test types:**
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/e2e/` - End-to-end tests
- `tests/scripts/` - Shell test scripts

**Shell test scripts:**
```bash
# Test Knuspr integration
backend/tests/scripts/test-knuspr-cheese.sh

# Test Railway deployment
backend/tests/scripts/test-railway-integration.sh

# Validate phase completion
backend/tests/scripts/validate-phase1.sh
```

### Frontend Tests

**Run tests:**
```bash
cd frontend
npm test
```

**E2E tests (Playwright):**
```bash
npm run test:e2e
```

**Visual regression:**
```bash
npm run test:visual
```

### Manual Testing

**Python test scripts:**
```bash
# Test Knuspr integration (all 17 MCP tools)
python3 backend/test_all_mcp_tools.py

# Test cart creation
python3 backend/test_add_cheese_simple.py

# Test Knuspr cheese workflow
python3 backend/test_knuspr_cheese.py
```

**Shell test scripts:**
```bash
# Validate phase completion
backend/tests/scripts/validate-phase1.sh

# Test Knuspr integration
backend/tests/scripts/test-knuspr-cheese.sh

# Test Railway deployment
backend/tests/scripts/test-railway-integration.sh
```

---

## Code Quality

### Linting & Formatting

**Python (Backend):**
```bash
# Format with Black
docker exec -it recipe-api black app/ tests/

# Lint with Flake8
docker exec -it recipe-api flake8 app/ tests/ --max-line-length=120

# Type check with MyPy
docker exec -it recipe-api mypy app/

# Run all checks
docker exec -it recipe-api sh -c 'black app/ tests/ && flake8 app/ tests/ && mypy app/'
```

**TypeScript (Frontend):**
```bash
cd frontend

# Lint
npm run lint

# Type check
npm run type-check

# Format
npm run format
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on commit:
- Black formatting
- Flake8 linting
- MyPy type checking
- ESLint (frontend)

---

## Common Tasks

### Database Management

**Create migration:**
```bash
docker exec -it recipe-api alembic revision --autogenerate -m "description"
```

**Apply migrations:**
```bash
docker exec -it recipe-api alembic upgrade head
```

**Rollback:**
```bash
docker exec -it recipe-api alembic downgrade -1
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d db
sleep 5
docker exec -it recipe-api alembic upgrade head
```

**Access PostgreSQL:**
```bash
docker exec -it recipe-postgres psql -U postgres recipe_app
```

### Add New API Endpoint

1. **Create endpoint file:**
```python
# backend/app/api/v1/endpoints/your_endpoint.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_items():
    return {"items": []}
```

2. **Add to router:**
```python
# backend/app/api/v1/router.py
from app.api.v1.endpoints import your_endpoint

api_router.include_router(
    your_endpoint.router,
    prefix="/your-endpoint",
    tags=["your-endpoint"]
)
```

3. **Add tests:**
```python
# backend/tests/api/test_your_endpoint.py
def test_get_items(client):
    response = client.get("/api/v1/your-endpoint/")
    assert response.status_code == 200
```

### Add Frontend Component

1. **Create component:**
```tsx
// frontend/src/components/YourComponent.tsx
export default function YourComponent() {
  return <div>Component</div>
}
```

2. **Add tests:**
```tsx
// frontend/__tests__/components/YourComponent.test.tsx
import { render } from '@testing-library/react'
import YourComponent from '@/components/YourComponent'

test('renders component', () => {
  const { getByText } = render(<YourComponent />)
  expect(getByText('Component')).toBeInTheDocument()
})
```

---

## Performance Optimization

### Backend Optimization

**Database:**
- Use indexes on frequently queried columns
- Implement query result caching with Redis
- Use connection pooling
- Batch database operations

**Caching:**
```python
from app.core.cache import cache_result

@cache_result(ttl=300)  # Cache for 5 minutes
async def get_expensive_data():
    # ... expensive operation
    return result
```

**Async operations:**
```python
# Use asyncio.gather for parallel operations
results = await asyncio.gather(
    operation1(),
    operation2(),
    operation3()
)
```

### Frontend Optimization

**Next.js:**
- Use Server Components by default
- Implement dynamic imports for code splitting
- Optimize images with next/image
- Enable static generation where possible

**React:**
- Memoize expensive computations with useMemo
- Use React.memo for component memoization
- Implement virtualization for long lists
- Lazy load components

---

## Monitoring

### Metrics

**Prometheus metrics:**
```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total requests')
request_duration = Histogram('http_request_duration_seconds', 'Request duration')
```

**Access metrics:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

### Logging

**Backend logging:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Info message")
logger.error("Error message", exc_info=True)
```

**View logs:**
```bash
docker logs -f recipe-api
docker-compose logs -f
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker exec recipe-postgres pg_isready

# Redis health
docker exec recipe-redis redis-cli ping
```

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Database connection failed:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres
# Restart if needed
docker-compose restart db
```

**Module not found:**
```bash
# Rebuild backend container
docker-compose build backend
docker-compose up -d
```

**Frontend build errors:**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

---

## Utility Scripts

### Deployment Monitoring
```bash
# Monitor Railway deployment
scripts/deployment/monitor-railway-deployment.sh

# Check Railway status
scripts/deployment/railway-status.sh
```

### Setup
```bash
# Setup Qdrant vector database
scripts/setup/setup-qdrant.sh
```

### Quick Reference
```bash
# Show common commands
scripts/quick-reference.sh
```

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Railway Docs](https://docs.railway.app/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Playwright Docs](https://playwright.dev/)

---

## Project Organization

### Configuration Files
- `backend/.env` - Backend environment
- `frontend/.env.local` - Frontend environment
- `docker-compose.yml` - Services
- `.vscode/tasks.json` - VS Code tasks

### Documentation
- `docs/KNUSPR_INTEGRATION.md` - Knuspr integration guide
- `docs/DEPLOYMENT_RAILWAY.md` - Railway deployment guide
- `docs/DEVELOPMENT_GUIDE.md` - This guide
- `docs/architecture.md` - Architecture overview

### Scripts
- `scripts/deployment/` - Deployment monitoring scripts
- `scripts/setup/` - Setup and installation scripts
- `scripts/quick-reference.sh` - Common commands reference
- `backend/tests/scripts/` - Test validation scripts

### Tests
- `backend/tests/unit/` - Unit tests
- `backend/tests/integration/` - Integration tests
- `backend/tests/scripts/` - Shell test scripts
- `backend/test_*.py` - Manual test scripts
- `frontend/__tests__/` - Frontend tests
- `frontend/e2e/` - E2E Playwright tests
