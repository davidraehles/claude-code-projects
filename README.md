# AI Meal Planner - Claude Code Projects

Multi-agent recipe management and meal planning application with AI-powered features and Knuspr grocery integration.

## About This Project

This is an AI-powered meal planning application that helps users:

- Discover and manage recipes from various online sources
- Generate personalized weekly meal plans
- Create optimized grocery lists
- Integrate with Knuspr for seamless grocery ordering
- Chat with an AI meal planner assistant

Built using a multi-agent architecture with specialized AI agents for recipe harvesting, meal planning, ingredient intelligence, and grocery cart optimization.

## Development Workflow

This project uses [Spec-Kit](https://github.com/github/spec-kit), a spec-driven development toolkit that provides structured workflows for building features with AI coding assistants.

### Available Spec-Kit Commands

- `/speckit.constitution` - Establish or update project principles and guidelines
- `/speckit.specify` - Create detailed feature specifications
- `/speckit.plan` - Generate technical implementation plans
- `/speckit.tasks` - Create actionable, dependency-ordered task lists
- `/speckit.implement` - Execute implementation following the plan
- `/speckit.analyze` - Analyze existing code and features
- `/speckit.checklist` - Generate quality checklists
- `/speckit.clarify` - Clarify requirements and resolve ambiguities

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: LangChain/LangGraph for agent orchestration
- **Agent Frameworks**: PydanticAI, AtomicAgents
- **AI Models**: Anthropic Claude for intelligent features
- **Grocery Integration**: Knuspr MCP client

### Frontend
- **Framework**: Next.js 16 with React 19
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: NextAuth.js
- **State Management**: React Query

### Infrastructure
- **Deployment**: Railway (backend), Vercel (frontend)
- **Monitoring**: Prometheus + custom scripts
- **Containerization**: Docker

## Project Structure

```
.
├── backend/                # FastAPI Python backend
│   ├── app/
│   │   ├── agents/        # AI agents (recipe harvester, meal architect, cart optimizer, etc.)
│   │   ├── api/           # FastAPI routes and endpoints
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── services/      # Business logic services
│   │   ├── workflows/     # LangGraph workflow orchestration
│   │   ├── schemas/       # Pydantic schemas for validation
│   │   └── utils/         # Utility functions
│   ├── migrations/        # Alembic database migrations
│   ├── tests/             # Backend tests (pytest)
│   └── scripts/           # Python scripts (seeding, verification)
├── frontend/              # Next.js React frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and API client
│   │   └── types/        # TypeScript type definitions
│   ├── e2e/              # Playwright E2E tests
│   └── __tests__/        # Jest unit tests
├── infrastructure/        # DevOps & deployment
│   ├── docker/           # Docker configuration
│   └── scripts/          # Deployment & monitoring scripts
├── docs/                  # Project documentation
├── specs/                 # Feature specifications (Spec-Kit)
│   ├── 001-grocery-list-generation/
│   ├── 002-multi-agent-recipe-app/
│   └── 003-ai-meal-planner-chat/
├── .claude/               # Claude Code configuration
│   ├── agents/           # ReAct agent system (8 agents)
│   └── commands/         # Custom slash commands
├── .kilocode/            # Kilocode workflow definitions
└── .specify/             # Spec-Kit templates and memory
```

## Features

### Currently Implemented

1. **Recipe Management** (Feature 002)
   - Recipe discovery and harvesting from web sources
   - File import for recipes
   - Recipe library with search and filtering
   - AI-powered ingredient intelligence

2. **Meal Planning** (Features 002, 003)
   - Automated weekly meal plan generation
   - Constraint satisfaction (dietary preferences, time budget)
   - AI chat assistant for meal planning
   - Voice input support

3. **Grocery Lists** (Feature 001)
   - Automated grocery list generation from meal plans
   - Ingredient aggregation and quantity scaling
   - Recipe and category view modes
   - Knuspr integration for cart population

4. **User Management**
   - Authentication with NextAuth.js
   - User profiles with dietary preferences
   - Saved meal plans and preferences

### In Development

- Enhanced ingredient substitution engine
- Advanced meal plan optimization
- Multi-language support
- Mobile app

## Quick Start

### For Developers

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd claude-code-projects
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Database Setup**
   - Install PostgreSQL
   - Create database: `createdb meal_planner`
   - Run migrations: `cd backend && alembic upgrade head`

For detailed setup instructions, see:
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [Quickstart Guide](./docs/QUICKSTART.md)

### For Feature Development

Create a new feature using Spec-Kit:

```bash
/speckit.specify "Your feature description here"
/speckit.plan
/speckit.tasks
/speckit.implement
```

## Multi-Agent System

This project uses a 8-agent ReAct (Reason + Act) system for parallelized development:

1. **Router Agent** - Orchestrates tasks and manages parallelization
2. **Spec Analyzer Agent** - Deep requirement analysis
3. **Frontend Dev Agent** - React/Next.js implementation
4. **Backend Dev Agent** - Python/FastAPI implementation
5. **Testing & Quality Agent** - Test generation and quality assurance
6. **Documentation Agent** - Keeps specs synchronized with code
7. **Integration Agent** - Final validation and merge readiness
8. **Agent Registry Manager** - Agent lifecycle management

See [.claude/agents/AGENT-REGISTRY.md](./.claude/agents/AGENT-REGISTRY.md) for details.

## Documentation

### Getting Started
- [Quickstart Guide](./docs/QUICKSTART.md) - Local development setup (15 min)
- [Deployment Guide](./docs/DEPLOYMENT.md) - Deploy to Railway and Vercel (30 min)
- [Testing Guide](./docs/TESTING_GUIDE.md) - Running tests (unit, integration, E2E)
- [Documentation Index](./docs/README.md) - Complete documentation catalog

### Project Status
- [Project Status](./docs/PROJECT_STATUS.md) - Current phase, features, and metrics
- [Phase 1 Complete](./docs/PHASE_1_COMPLETE.md) - Foundation phase milestones
- [Phase 2 Status](./docs/PHASE_2_STATUS.md) - Multi-agent system progress

### Architecture
- [Multi-Agent System](./.claude/agents/README.md) - 8-agent ReAct architecture
- [Agent Registry](./.claude/agents/AGENT-REGISTRY.md) - All available agents
- [Architecture Debt](./docs/ARCHITECTURE_DEBT.md) - Technical debt tracking

### Features
- [Feature 001 - Grocery Lists](./specs/001-grocery-list-generation/spec.md) - In progress
- [Feature 002 - Multi-Agent Recipe App](./specs/002-multi-agent-recipe-app/spec.md) - Phase 2
- [Feature 003 - AI Meal Planner Chat](./specs/003-ai-meal-planner-chat/spec.md) - Planned

### Developer Tools
- [CLI Tools](./docs/CLI_TOOLS.md) - Railway and Vercel CLI reference
- [VSCode Setup](./docs/VSCODE_DEVELOPMENT_READY.md) - VSCode configuration
- [Spec-Kit Guide](./.specify/README.md) - Spec-driven development toolkit

### Reference
- [Troubleshooting Archive](./docs/archive/) - Historical debugging notes
- [Agent System Archive](./.claude/agents/archive/) - Historical agent docs

## Live Deployments

- **Frontend**: https://claude-code-projects.vercel.app
- **Backend API**: https://claude-code-projects-production.up.railway.app
- **API Docs**: https://claude-code-projects-production.up.railway.app/api/docs

## Contributing

This project uses conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Maintenance tasks
- `docs:` - Documentation updates
- `test:` - Test changes

See [CLAUDE.md](./CLAUDE.md) for development guidelines.

## License

Proprietary - AI Meal Planner Application
