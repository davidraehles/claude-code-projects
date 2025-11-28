# Claude Code Projects

This project is initialized with [Spec-Kit](https://github.com/github/spec-kit), a spec-driven development toolkit from GitHub.

## About Spec-Kit

Spec-Kit provides a structured workflow for building software features using AI coding assistants. It helps teams:

- Define clear project principles and requirements
- Create detailed specifications
- Generate actionable implementation plans
- Track progress with organized task lists

## Available Commands

This project includes the following slash commands for Claude Code:

- `/speckit.constitution` - Establish or update project principles and guidelines
- `/speckit.specify` - Create detailed feature specifications
- `/speckit.plan` - Generate technical implementation plans
- `/speckit.tasks` - Create actionable, dependency-ordered task lists
- `/speckit.implement` - Execute implementation following the plan
- `/speckit.analyze` - Analyze existing code and features
- `/speckit.checklist` - Generate quality checklists
- `/speckit.clarify` - Clarify requirements and resolve ambiguities

## Project Structure

```
.
├── backend/              # FastAPI Python backend
│   ├── app/             # Application code
│   │   ├── agents/      # AI agents (cart optimizer, meal architect, etc.)
│   │   ├── api/         # API routes
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── services/    # Business logic services
│   │   └── workflows/   # LangGraph workflow orchestration
│   ├── migrations/      # Alembic database migrations
│   ├── tests/           # Backend tests (unit & integration)
│   └── scripts/         # Python scripts (seeding, verification)
├── frontend/            # Next.js React frontend
│   ├── src/             # Application source code
│   ├── e2e/             # Playwright E2E tests
│   └── __tests__/       # Jest unit tests
├── infrastructure/      # DevOps & deployment configuration
│   ├── docker/          # Docker configuration (Prometheus, Grafana)
│   └── scripts/         # Deployment & monitoring scripts
├── docs/                # Project documentation
├── specs/               # Feature specifications (Spec-Kit)
├── .claude/             # Claude Code configuration
├── .kilocode/           # Kilocode workflow definitions
└── .specify/            # Spec-Kit templates and memory
```

## Getting Started

To create a new feature specification:

```bash
/speckit.specify "Your feature description here"
```

For more information about Spec-Kit, visit: https://github.com/github/spec-kit

## Documentation

### Project Documentation

- **[Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)** - Complete guide for deploying to Railway and Vercel
- **[Architecture](./docs/ARCHITECTURE.md)** - System architecture overview
- **[Troubleshooting Archive](./docs/archive/)** - Historical debugging notes

### Spec-Kit Documentation

- [Spec-Kit README](./.specify/README.md)
- [Spec-Kit Agent Guide](https://github.com/github/spec-kit/blob/main/AGENTS.md)

## Live Deployments

- **Frontend**: https://claude-code-projects.vercel.app
- **Backend API**: https://claude-code-projects-production.up.railway.app
- **API Docs**: https://claude-code-projects-production.up.railway.app/api/docs
