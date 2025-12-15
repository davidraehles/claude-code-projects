<!--
Sync Impact Report:
- Version change: 0.0.0 -> 1.0.0
- Modified principles: All (Initial creation)
- Added sections: Core Principles, Technology Standards, Development Workflow, Governance
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ Compatible)
  - .specify/templates/spec-template.md (✅ Compatible)
  - .specify/templates/tasks-template.md (✅ Compatible)
-->

# Go, Cart! Constitution

## Core Principles

### I. User-Centric Excellence
**Accessibility, Performance, and Reliability are non-negotiable.**
- **Accessibility**: All UI components MUST meet WCAG 2.1 AAA standards.
- **Performance**: UI MUST target 60fps; API responses SHOULD be <200ms (p95); Application MUST be Offline-first.
- **Reliability**: Critical user journeys MUST be covered by E2E tests.

### II. AI-First Architecture
**Intelligent, agentic, and integrated systems.**
- **Multi-Agent**: Complex business logic SHOULD be implemented using LangGraph agents.
- **Integration**: External services (e.g., Grocery APIs) MUST be integrated via MCP or robust adapters.
- **Intelligence**: Features SHOULD optimize for user intent, ingredient usage, and personalization.

### III. Robust Engineering
**Strict typing, layered architecture, and comprehensive testing.**
- **Type Safety**: Python code MUST pass `mypy` (strict); TypeScript code MUST use `strict: true`.
- **Architecture**: Backend MUST follow a 3-layer architecture (API -> Service -> Data).
- **Testing**: Business logic MUST have unit tests; API endpoints MUST have integration tests.

### IV. Security & Privacy
**Secure by design, protecting user data and AI interactions.**
- **OWASP**: All endpoints and inputs MUST be protected against OWASP Top 10 vulnerabilities.
- **Data Protection**: User data MUST be encrypted at rest and in transit.
- **AI Safety**: AI inputs and outputs MUST be sanitized to prevent injection or harmful content.

### V. Operational Maturity
**Containerized, automated, and observable.**
- **Containerization**: All services MUST be Dockerized for consistent development and deployment.
- **CI/CD**: All changes MUST pass automated testing pipelines before merging.
- **Observability**: Services MUST emit structured logs and metrics for monitoring.

## Technology Standards

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL 16+ (SQLAlchemy 2.0 Async, Alembic)
- **AI/Agents**: LangGraph, LangChain, PydanticAI

### Frontend
- **Framework**: Next.js 16 (App Router), React 19
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS, Framer Motion, GSAP
- **State**: React Query (TanStack Query)

### Infrastructure
- **Containerization**: Docker Compose
- **Deployment**: Railway (Backend), Vercel (Frontend)
- **Monitoring**: Prometheus, Sentry

## Development Workflow

1.  **Feature Branch**: Create a branch `feature/description` from `main`.
2.  **Specification**: Define user stories and acceptance criteria (use `/speckit.spec`).
3.  **Implementation**: Follow code style guidelines (Black, Prettier) and write tests.
4.  **Review**: Use AI agents for initial review, then peer review.
5.  **Merge**: Squash and merge after passing CI.

## Governance

This Constitution supersedes all other development practices. Amendments require a documented RFC and approval from the core team.

- **Compliance**: All PRs must verify compliance with these principles.
- **Exceptions**: Any deviation must be explicitly justified and documented in an ADR.
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH) applies to this document.

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
