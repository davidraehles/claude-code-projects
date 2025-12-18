---
goal: Implement Multi-Agent Recipe & Meal Planning System
version: 1.0.0
date_created: 2025-11-14
last_updated: 2025-12-15
owner: Meal Planner Team
status: 'In progress'
tags: [feature, architecture, ai, backend, frontend]
---

# Introduction

![Status: In progress](https://img.shields.io/badge/status-In%20progress-yellow)

This implementation plan outlines the architecture, phases, and technical approach for building a production-ready multi-agent recipe and meal planning SaaS. The system leverages a multi-agent architecture to automate the entire meal planning lifecycle: from harvesting recipes from the web, to generating personalized weekly meal plans, and finally optimizing grocery lists for seamless integration with the Knuspr delivery service.

## 1. Requirements & Constraints

- **REQ-001**: **Recipe Discovery and Import**: The system must allow users to import recipes via URL and automatically extract ingredients, instructions, prep time, cook time, and servings.
- **REQ-002**: **Ingredient Intelligence and Substitution**: The system must suggest ingredient substitutions based on dietary restrictions and identify seasonal ingredients.
- **REQ-003**: **Automated Weekly Meal Planning**: The system must generate a 7-day meal plan based on user preferences and minimize food waste.
- **REQ-004**: **Knuspr Grocery Cart Optimization**: The system must convert a meal plan into a Knuspr shopping cart, grouping items by store section.
- **REQ-005**: **Agent Hot-Swapping**: The system must allow individual agents to be updated or replaced without system downtime.
- **CON-001**: Backend must be built with **Python 3.11+** and **FastAPI**.
- **CON-002**: Frontend must be built with **Next.js 16** and **React 19**.
- **CON-003**: Database must be **PostgreSQL 16+**.
- **CON-004**: Application must be **WCAG 2.1 AAA** compliant.
- **CON-005**: All external API integrations (Knuspr) must handle rate limiting and authentication securely.
- **GUD-001**: Follow the "Library-First Architecture" for backend packages.
- **GUD-002**: Use Pydantic V2 for all data validation.
- **GUD-003**: Ensure all UI components are responsive and support 60fps animations.

## 2. Implementation Steps

### Implementation Phase 1: Foundation & Core Agents

- GOAL-001: Set up development environment, build core agents, event bus, recipe harvester, and monitoring.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Initialize FastAPI project structure following Library-First Architecture. Implemented in `backend/app/main.py` with modular routers in `backend/app/api/`. | | |
| TASK-002 | Set up PostgreSQL with Alembic migrations. Schema defined for `users`, `recipes`, `meal_plans`, `carts` in `backend/app/models/`. | | |
| TASK-003 | Set up Redis for caching and message queue (Pub/Sub). Configured in `backend/app/config/redis.py` and used by Event Bus. | | |
| TASK-004 | Configure Prometheus middleware and `/metrics` endpoint. Implemented in `backend/app/monitoring/prometheus.py`. | | |
| TASK-005 | Create GitHub Actions workflow for CI/CD. Includes `pytest` execution, `flake8`/`black` linting, and Docker image building. | | |
| TASK-006 | Implement User Authentication (Signup, Login, JWT, Preferences). Handled by `backend/app/api/auth.py` and `backend/app/services/auth_service.py`. | | |
| TASK-007 | Implement Agent Base Class, Capability Manifest, and Event Bus. Core logic in `backend/app/agents/base.py` and `backend/app/events/bus.py`. | | |
| TASK-008 | Implement Recipe Harvester. Includes `RecipeHarvester` agent (`backend/app/agents/recipe_harvester.py`) and scrapers (`html_scraper.py`, `rss_scraper.py`). | | |
| TASK-009 | Implement Ingredient Intelligence Agent. Logic for taxonomy and substitution rules in `backend/app/agents/ingredient_intelligence.py`. | | |
| TASK-010 | Set up Monitoring. Grafana Dashboards, AlertManager configuration, and Structured Logging via `backend/app/logging_config.py`. | | |
| TASK-011 | Implement Support Services. DLQ (Dead Letter Queue), Error Handler (`backend/app/agents/error_handler.py`), and Notification Service. | | |

### Implementation Phase 2: Orchestration & Meal Planning

- GOAL-002: Build Meal Architect agent, constraint solver, and orchestration workflow.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Integrate Z3 Constraint Solver and define meal planning DSL. Implemented within `backend/app/agents/meal_architect.py` for constraint satisfaction. | | |
| TASK-013 | Implement Meal Architect Agent. Handles generation and regeneration requests in `backend/app/agents/meal_architect.py`. | | |
| TASK-014 | Implement LangGraph Orchestration. Workflow defined in `backend/app/workflows/meal_planning_workflow.py` with nodes in `meal_planning_nodes.py`. | | |
| TASK-015 | Create Meal Planning API. Endpoints `POST /mealplans` and `GET /mealplans/{id}` exposed in `backend/app/api/meal_plans.py`. | | |

### Implementation Phase 3: Knuspr Integration & Cart Optimization

- GOAL-003: Integrate with Knuspr API and build Cart Optimizer agent.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-016 | Implement Knuspr MCP Client. Handles Product Search and Cart Creation via Model Context Protocol in `backend/app/services/knuspr_mcp.py`. | | |
| TASK-017 | Implement Cart Optimizer Agent. Logic for item grouping and delivery slot selection in `backend/app/agents/cart_optimizer.py`. | | |
| TASK-018 | Implement End-to-End Workflow. Orchestrates Meal Plan -> Cart -> Knuspr handoff, validated by integration tests. | | |

### Implementation Phase 4: Frontend & UI

- GOAL-004: Build mobile-first web UI for the entire workflow.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-019 | Setup Next.js 16 + React 19 Project. Configured with Tailwind CSS and TypeScript in `frontend/`. | | |
| TASK-020 | Implement Authentication UI. Login, Signup, and Profile components in `frontend/src/components/Auth/`. | | |
| TASK-021 | Implement Recipe Discovery UI. Search, Filter, and Details views in `frontend/src/components/recipe/`. | | |
| TASK-022 | Implement Meal Planner UI. Wizard, Calendar, and Review components in `frontend/src/components/MealPlan/`. | | |
| TASK-023 | Implement Shopping Cart UI. Preview, Delivery selection, and Knuspr Sync in `frontend/src/components/knuspr/` and `frontend/src/components/grocery/`. | | |

### Implementation Phase 5: Testing, Polish & Launch

- GOAL-005: Comprehensive testing, optimization, and production deployment.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-024 | Implement Unit, Integration, and E2E Tests. Backend tests in `backend/tests/`, Frontend E2E in `frontend/e2e/` using Playwright. | | |
| TASK-025 | Perform Performance Optimization. DB Indexes, Redis Caching, and Bundle Size optimization. | | |
| TASK-026 | Conduct Beta Testing. Feedback integration and bug fixes based on initial user cohort. | | |
| TASK-027 | Deploy to Production. Infrastructure setup on Railway (Backend) and Vercel (Frontend), including backups and monitoring. | | |

## 3. Alternatives

- **ALT-001**: **Greedy Algorithm for Meal Planning**: Considered for simplicity, but Z3 Constraint Solver chosen for better optimization of multiple constraints (waste, variety, time).
- **ALT-002**: **Direct Knuspr API**: Considered, but MCP (Model Context Protocol) chosen to standardize the interface for potential future grocery providers.
- **ALT-003**: **Client-Side Logic**: Considered for meal planning, but Server-Side Agents chosen for scalability, security, and access to heavy compute (Z3).

## 4. Dependencies

- **DEP-001**: **FastAPI 0.104+**: Backend framework.
- **DEP-002**: **SQLAlchemy 2.0**: ORM with async support.
- **DEP-003**: **Redis**: Message broker and cache.
- **DEP-004**: **Prometheus**: Metrics collection.
- **DEP-005**: **LangGraph**: Agent orchestration.
- **DEP-006**: **Z3 Solver**: Constraint satisfaction engine.
- **DEP-007**: **Next.js 16**: Frontend framework.
- **DEP-008**: **Knuspr API**: External grocery service.

## 5. Files

- **FILE-001**: `backend/app/agents/recipe_harvester.py`: Recipe harvesting logic.
- **FILE-002**: `backend/app/agents/meal_architect.py`: Meal planning agent.
- **FILE-003**: `backend/app/agents/cart_optimizer.py`: Cart optimization agent.
- **FILE-004**: `backend/app/services/knuspr_mcp.py`: Knuspr integration.
- **FILE-005**: `frontend/src/components/MealPlan/Planner.tsx`: Meal planner UI.

## 6. Testing

- **TEST-001**: **Unit Tests**: Verify agent logic, event handlers, and utility functions.
- **TEST-002**: **Integration Tests**: Verify agent-to-agent communication and database transactions.
- **TEST-003**: **E2E Tests**: Verify full user journey (Login -> Plan -> Cart) using Playwright.
- **TEST-004**: **Performance Tests**: Verify meal plan generation < 5s and API latency < 200ms.

## 7. Risks & Assumptions

- **RISK-001**: **Recipe Parsing Accuracy**: Parsing unstructured HTML is difficult. Mitigation: Start with structured sites (Ottolenghi) and use LLMs for edge cases.
- **RISK-002**: **Knuspr API Instability**: External dependency. Mitigation: Implement retries, caching, and manual fallback.
- **ASSUMPTION-001**: Users will provide sufficient dietary constraints to generate valid plans.
- **ASSUMPTION-002**: Knuspr product availability is relatively stable during the planning session.

## 8. Related Specifications / Further Reading

- [Feature Specification](./spec.md)
- [Data Model](./data-model.md)
- [Architecture Documentation](../../docs/architecture.md)
