# Tasks: Multi-Agent Recipe & Meal Planning System

**Feature**: 002-multi-agent-recipe-app
**Status**: In Progress
**Total Tasks**: 32

## Phase 1: Setup
*Goal: Initialize project structure and development environment.*

- [x] T001 Initialize FastAPI project structure following Library-First Architecture in [backend/app/main.py](backend/app/main.py)
- [x] T002 Set up PostgreSQL with Alembic migrations and schema definitions in [backend/app/models/](backend/app/models/)
- [x] T003 Set up Redis for caching and message queue in [backend/app/config/redis.py](backend/app/config/redis.py)
- [x] T004 Configure Prometheus middleware and metrics endpoint in [backend/app/monitoring/prometheus.py](backend/app/monitoring/prometheus.py)
- [x] T005 Create GitHub Actions workflow for CI/CD in [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [x] T006 Setup Next.js 16 + React 19 Project with Tailwind CSS in [frontend/package.json](frontend/package.json)

## Phase 2: Foundational
*Goal: Build core authentication, agent infrastructure, and monitoring.*

- [x] T007 Implement User Authentication (Signup, Login, JWT) in [backend/app/api/auth.py](backend/app/api/auth.py)
- [x] T008 Implement Authentication UI (Login, Signup, Profile) in [frontend/src/components/Auth/](frontend/src/components/Auth/)
- [x] T009 Implement Agent Base Class, Capability Manifest, and Event Bus in [backend/app/agents/base.py](backend/app/agents/base.py)
- [x] T010 Set up Monitoring (Grafana, AlertManager, Structured Logging) in [backend/app/logging_config.py](backend/app/logging_config.py)
- [x] T011 Implement Support Services (DLQ, Error Handler) in [backend/app/agents/error_handler.py](backend/app/agents/error_handler.py)

## Phase 3: User Story 1 - Recipe Discovery & Intelligence
*Goal: Enable recipe harvesting and ingredient intelligence.*

- [x] T012 [US1] Implement Recipe Harvester agent and scrapers in [backend/app/agents/recipe_harvester.py](backend/app/agents/recipe_harvester.py)
- [x] T013 [US1] Implement Ingredient Intelligence Agent for taxonomy and substitutions in [backend/app/agents/ingredient_intelligence.py](backend/app/agents/ingredient_intelligence.py)
- [x] T014 [US1] Implement Recipe Discovery UI (Search, Filter, Details) in [frontend/src/components/recipe/](frontend/src/components/recipe/)

## Phase 4: User Story 2 - Meal Planning
*Goal: Automate weekly meal planning with constraint satisfaction.*

- [x] T015 [US2] Integrate Z3 Constraint Solver and define meal planning DSL in [backend/app/agents/meal_architect.py](backend/app/agents/meal_architect.py)
- [x] T016 [US2] Implement Meal Architect Agent for plan generation in [backend/app/agents/meal_architect.py](backend/app/agents/meal_architect.py)
- [x] T017 [US2] Implement LangGraph Orchestration workflow in [backend/app/workflows/meal_planning_workflow.py](backend/app/workflows/meal_planning_workflow.py)
- [x] T018 [US2] Create Meal Planning API endpoints in [backend/app/api/meal_plans.py](backend/app/api/meal_plans.py)
- [x] T019 [US2] Implement Meal Planner UI (Wizard, Calendar, Review) in [frontend/src/components/MealPlan/](frontend/src/components/MealPlan/)

## Phase 5: User Story 3 - Knuspr Integration
*Goal: Convert meal plans to optimized Knuspr shopping carts.*

- [x] T020 [US3] Implement Knuspr MCP Client for product search and cart creation in [backend/app/services/knuspr_mcp.py](backend/app/services/knuspr_mcp.py)
- [x] T021 [US3] Implement Cart Optimizer Agent for item grouping in [backend/app/agents/cart_optimizer.py](backend/app/agents/cart_optimizer.py)
- [x] T022 [US3] Implement End-to-End Workflow (Meal Plan -> Cart -> Knuspr) in [backend/app/workflows/](backend/app/workflows/)
- [x] T023 [US3] Implement Shopping Cart UI (Preview, Delivery, Sync) in [frontend/src/components/grocery/](frontend/src/components/grocery/)

## Phase 6: Polish & Launch
*Goal: Ensure quality, performance, and production readiness.*

- [x] T024 Implement Unit, Integration, and E2E Tests in [backend/tests/](backend/tests/)
- [x] T025 Perform Performance Optimization (Indexes, Caching, Bundle Size) in [backend/app/config/database.py](backend/app/config/database.py)
- [x] T026 Conduct Beta Testing and feedback integration in [docs/BETA_FEEDBACK.md](docs/BETA_FEEDBACK.md)
- [x] T027 Deploy to Production (Railway/Vercel) in [railway.toml](railway.toml)

## Phase 7: Frontend AI Integration
*Goal: Make AI reasoning and interaction visible to the user.*

- [x] T028 Implement Server-Sent Events (SSE) endpoint for real-time agent thought streaming in [backend/app/api/v1/stream.py](backend/app/api/v1/stream.py)
- [x] T029 Create "Agent Thought" UI component to visualize the reasoning process in [frontend/src/components/ai/AgentThoughtLog.tsx](frontend/src/components/ai/AgentThoughtLog.tsx)
- [x] T030 Implement "Chat with Chef" interface for refining meal plans in [frontend/src/components/ai/ChefChat.tsx](frontend/src/components/ai/ChefChat.tsx)
- [x] T031 Update Meal Architect to support iterative refinement via chat in [backend/app/agents/meal_architect.py](backend/app/agents/meal_architect.py)
- [x] T032 Add "Explain this" feature to Recipe and Meal Plan details in [frontend/src/components/recipe/RecipeExplanation.tsx](frontend/src/components/recipe/RecipeExplanation.tsx)

## Dependencies

1. **US1** (Recipe Discovery) is independent.
2. **US2** (Meal Planning) depends on **US1** (needs recipes to plan).
3. **US3** (Knuspr Integration) depends on **US2** (needs meal plan to create cart).

## Parallel Execution Examples

- **US1**: Backend Harvester (T012) and Frontend Recipe UI (T014) can be developed in parallel.
- **US2**: Z3 Solver integration (T015) and Meal Planner UI (T019) can be developed in parallel.
- **US3**: Knuspr MCP Client (T020) and Cart UI (T023) can be developed in parallel.

## Implementation Strategy

- **MVP Scope**: Complete Phase 1, 2, and 3 (US1). This provides a working recipe database.
- **Incremental Delivery**:
    - Deliver US1 to allow users to build their recipe library.
    - Deliver US2 to enable planning with those recipes.
    - Deliver US3 to close the loop with grocery delivery.
