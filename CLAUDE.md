# AI Meal Planner - Development Guidelines

## Project Overview
Multi-agent recipe management and meal planning application with:
- **Backend**: FastAPI (Python 3.11+) with LangGraph workflows
- **Frontend**: Next.js 16 with React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Grocery Integration**: Knuspr MCP client for cart management

## Project Structure
```
backend/               # Python FastAPI backend
  app/                 # Application code
  tests/               # Backend tests (unit & integration)
  scripts/             # Python scripts (seeding, etc.)
  requirements.txt     # Python dependencies
frontend/              # Next.js frontend
  src/                 # React components & pages
  e2e/                 # Playwright E2E tests
  __tests__/           # Jest unit tests
infrastructure/        # Docker, deployment configs, monitoring scripts
docs/                  # Documentation
specs/                 # Feature specifications
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
- **Python**: Black formatter, isort for imports, mypy for type checking
- **TypeScript**: ESLint + Prettier, strict mode enabled
- **Commits**: Conventional commits (feat:, fix:, chore:, etc.)

## Active Features
- 002-multi-agent-recipe-app: Recipe management with AI agents
- 003-ai-meal-planner-chat: Chat-based meal planning interface

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
