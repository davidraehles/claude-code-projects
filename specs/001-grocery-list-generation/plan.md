# Implementation Plan: Automated Grocery List Generation with Knuspr Integration

**Branch**: `001-grocery-list-generation` | **Date**: 2025-11-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-grocery-list-generation/spec.md`

**Note**: This plan leverages existing infrastructure: GroceryCart models, KnusprMCPClient, React Query patterns, and Redux-style reducers. Implementation focuses on completing mocked endpoints and adding recipe/category views.

## Summary

Implement end-to-end grocery list generation from meal plans by:
1. **Backend**: Complete mocked GroceryCart endpoints with real ingredient aggregation, quantity scaling, and Knuspr product matching
2. **Frontend**: Add recipe/category view toggle, maintain existing cart UI with checkbox persistence, integrate with existing hooks
3. **Integration**: Wire existing KnusprMCPClient to cart creation workflow, handle OAuth flow via existing credential management

**Alignment**: This feature completes the existing partial implementation rather than building from scratch. Database models, Knuspr client, and frontend cart page already exist.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+ (existing FastAPI app)
- Frontend: TypeScript 5.x with Next.js 16 + React 19

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, asyncio, KnusprMCPClient (existing), IngredientMapper (existing)
- Frontend: React Query, TailwindCSS, Next.js App Router

**Storage**: PostgreSQL (existing models: GroceryCart, CartItem, MealPlan, Recipe, Ingredient)

**Testing**:
- Backend: pytest with TestClient, in-memory SQLite, async fixtures
- Frontend: Jest (unit), Playwright (E2E), React Testing Library

**Target Platform**: Web application (Linux server backend, browser frontend)

**Project Type**: Web (backend/ + frontend/ directories)

**Performance Goals**:
- Grocery list generation: <2 seconds (per spec SC-001)
- View toggle: <1 second (per spec SC-003)
- Knuspr cart population: <5 seconds (per spec SC-005)

**Constraints**:
- Ingredient aggregation must be 100% accurate (spec SC-002)
- 95% product matching success rate (spec SC-006)
- 99% cart population success rate (spec SC-007)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality and Maintainability
- [x] TypeScript strict mode enabled in frontend (already active)
- [x] Python type hints with mypy validation (already active)
- [x] Black/isort for Python formatting (already active)
- [x] ESLint for TypeScript linting (already active)
- [x] No raw SQL - SQLAlchemy ORM only (existing pattern)
- [x] Docstrings on complex functions (will add for new aggregation logic)

### II. Testing Discipline
- [x] Tests written BEFORE implementation (Red-Green-Refactor)
- [x] Target ≥80% code coverage for new code
- [x] Unit tests for: ingredient aggregation, quantity scaling, product matching
- [x] Integration tests for: grocery cart creation endpoint, view toggling API
- [x] E2E tests for: full cart generation flow, Knuspr authentication, recipe/category views
- [x] All tests must pass before PR merge

### III. UX Consistency
- [x] TailwindCSS utility classes (existing pattern)
- [x] Loading states for async operations (spinner during cart generation, view toggle)
- [x] User-friendly error messages (Knuspr API failures, missing credentials)
- [x] Responsive design (desktop/tablet/mobile already in place for cart page)
- [x] Semantic HTML and ARIA labels (verify accessibility)

### IV. Performance and Scalability
- [x] API response times <200ms for cart retrieval (indexed queries)
- [x] Grocery list generation <2 seconds (spec requirement, in-memory aggregation)
- [x] View toggle <1 second (client-side reorganization, no API call)
- [x] Knuspr cart population <5 seconds (async with progress tracking)
- [x] Database indexes on `user_id`, `meal_plan_id`, `created_at`
- [x] Pagination for large ingredient lists (>100 items)

### V. Observability and Operational Hygiene
- [x] Structured JSON logging with correlation IDs
- [x] Metrics for cart creation (success rate, latency)
- [x] Prometheus metrics for Knuspr API calls (success, errors, retries)
- [x] Health check includes Knuspr connectivity status
- [x] Error tracking for product matching failures
- [x] Dead Letter Queue for failed Knuspr operations

### Constitution Compliance Summary
✅ **All gates passed** - Feature aligns with existing patterns, no new complexities introduced

## Project Structure

### Documentation (this feature)

```text
specs/001-grocery-list-generation/
├── spec.md              # Feature specification (COMPLETED)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (TO BE CREATED)
├── data-model.md        # Phase 1 output (TO BE CREATED)
├── quickstart.md        # Phase 1 output (TO BE CREATED)
├── contracts/           # Phase 1 output (TO BE CREATED)
│   ├── grocery-list-api.yaml    # OpenAPI spec
│   └── knuspr-integration.yaml  # Knuspr workflow contract
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root - EXISTING STRUCTURE)

```text
backend/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── models/
│   │   ├── grocery_cart.py      # [MODIFY] Add recipe_sources JSON to CartItem
│   │   ├── meal_plan.py         # [USE] Extract recipes and quantities
│   │   ├── recipe.py            # [USE] Parse ingredients field
│   │   └── ingredient.py        # [USE] For normalization and units
│   ├── api/
│   │   └── v1/
│   │       ├── grocery_carts.py # [MODIFY] Complete mocked endpoints
│   │       ├── knuspr_credentials.py  # [USE] Existing OAuth handling
│   │       └── workflows.py     # [NEW ENDPOINT] Cart from meal plan workflow
│   ├── services/
│   │   ├── knuspr_mcp_client.py    # [USE] Existing product search/cart creation
│   │   ├── ingredient_mapper.py    # [USE] Existing ingredient→product matching
│   │   ├── cart_optimizer.py       # [USE] Existing cart optimization
│   │   └── grocery_aggregator.py   # [NEW] Ingredient aggregation logic
│   └── schemas/
│       └── grocery_cart.py      # [MODIFY] Add view_mode, grouped_items schemas
└── tests/
    ├── unit/
    │   ├── test_grocery_aggregator.py  # [NEW] Aggregation unit tests
    │   └── test_knuspr_integration.py  # [EXTEND] Add cart creation tests
    ├── integration/
    │   └── test_grocery_cart_api.py    # [NEW] Endpoint integration tests
    └── e2e/
        └── test_meal_plan_to_cart.py   # [NEW] Full workflow E2E test

frontend/
├── src/
│   ├── app/
│   │   ├── grocery-carts/
│   │   │   └── [id]/
│   │   │       └── page.tsx     # [MODIFY] Add view toggle UI
│   │   └── meal-plans/
│   │       └── [id]/
│   │           └── page.tsx     # [MODIFY] Add "Generate Cart" button
│   ├── components/
│   │   └── knuspr/
│   │       ├── GroceryListView.tsx      # [NEW] Recipe/category view component
│   │       ├── ViewToggle.tsx           # [NEW] Toggle button component
│   │       └── CartGenerationButton.tsx # [NEW] "Start Filling Cart" button
│   ├── hooks/
│   │   └── queries/
│   │       ├── useGroceryCarts.ts     # [USE] Existing hook
│   │       └── useKnusprCredentials.ts # [USE] Existing hook
│   ├── reducers/
│   │   └── groceryCartReducer.ts # [MODIFY] Add view_mode state
│   └── lib/
│       └── api.ts                # [MODIFY] Add cart generation endpoint
└── e2e/
    ├── meal-plan-flow.spec.ts    # [EXTEND] Add cart generation to test
    └── grocery-cart-views.spec.ts # [NEW] Test recipe/category views
```

**Structure Decision**: Web application with existing backend/frontend separation. This feature extends existing grocery cart infrastructure rather than creating new directories. All new files integrate with established patterns (FastAPI routers, React Query hooks, reducer pattern).
