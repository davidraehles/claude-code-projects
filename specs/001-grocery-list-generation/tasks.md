# Tasks: Automated Grocery List Generation with Knuspr Integration

**Feature Branch**: `001-grocery-list-generation`
**Status**: Pending
**Tech Stack**: Python 3.11+ (FastAPI), TypeScript 5.x (Next.js 16 + React 19), PostgreSQL

## Phase 1: Setup
*Initialize project structure and define API contracts.*

- [ ] [T001] Create OpenAPI contract for grocery list generation endpoints in `specs/001-grocery-list-generation/contracts/grocery-list-api.yaml`
- [ ] [T002] [P] Create contract for Knuspr integration workflow in `specs/001-grocery-list-generation/contracts/knuspr-integration.yaml`

## Phase 2: Foundational
*Core backend infrastructure and data model changes.*

- [ ] [T003] Create Alembic migration to add `recipe_ids` JSON column to `cart_items` table in `backend/migrations/versions/006_add_recipe_ids_to_cart_items.py`
- [ ] [T004] Update `CartItem` SQLAlchemy model to include `recipe_ids` field in `backend/app/models/grocery_cart.py`
- [ ] [T005] Create `GroceryAggregator` service class skeleton in `backend/app/services/grocery_aggregator.py`
- [ ] [T006] Implement ingredient string parsing logic (regex-based) in `backend/app/services/grocery_aggregator.py`
- [ ] [T007] Implement unit conversion and normalization logic in `backend/app/services/grocery_aggregator.py`
- [ ] [T008] Create unit tests for ingredient parsing and aggregation logic in `backend/tests/unit/test_grocery_aggregator.py`

## Phase 3: User Story 1 - View Aggregated Grocery List (P1)
*Generate and view grocery lists from meal plans.*

- [ ] [T009] [US1] Implement `aggregate_from_meal_plan` method with eager loading in `backend/app/services/grocery_aggregator.py`
- [ ] [T010] [US1] Update `CartItemSchema` to include `recipe_sources` field in `backend/app/schemas/grocery_cart.py`
- [ ] [T011] [US1] Implement `create_cart_from_meal_plan` endpoint in `backend/app/api/v1/workflows.py`
- [ ] [T012] [US1] Add integration tests for cart creation endpoint in `backend/tests/integration/test_grocery_cart_api.py`
- [ ] [T013] [US1] Update `useGroceryCarts` hook to support cart generation mutation in `frontend/src/hooks/queries/useGroceryCarts.ts`
- [ ] [T014] [US1] Create `CartGenerationButton` component in `frontend/src/components/knuspr/CartGenerationButton.tsx`
- [ ] [T015] [US1] Add generation button to Meal Plan details page in `frontend/src/app/meal-plans/[id]/page.tsx`

## Phase 4: User Story 3 - Fill Knuspr Cart (P1)
*Send ingredients to Knuspr cart with authentication handling.*

- [ ] [T016] [US3] Update `KnusprMCPClient` to support batched cart addition in `backend/app/services/knuspr_mcp_client.py`
- [ ] [T017] [US3] Implement `fill_knuspr_cart` endpoint with progress tracking in `backend/app/api/v1/workflows.py`
- [ ] [T018] [US3] Create `useKnusprCart` hook for cart population in `frontend/src/hooks/queries/useKnusprCart.ts`
- [ ] [T019] [US3] Create `FillCartButton` component with progress indicator in `frontend/src/components/knuspr/FillCartButton.tsx`
- [ ] [T020] [US3] Integrate Knuspr authentication check and redirect in `frontend/src/components/knuspr/FillCartButton.tsx`
- [ ] [T021] [US3] Add E2E test for Knuspr cart population workflow in `frontend/e2e/knuspr-integration.spec.ts`

## Phase 5: User Story 2 - Switch Views (P2)
*Toggle between Recipe and Category views.*

- [ ] [T022] [US2] Update `groceryCartReducer` to handle `viewMode` state in `frontend/src/reducers/groceryCartReducer.ts`
- [ ] [T023] [US2] Create `ViewToggle` component in `frontend/src/components/knuspr/ViewToggle.tsx`
- [ ] [T024] [US2] Create `RecipeView` component for grouped display in `frontend/src/components/knuspr/RecipeView.tsx`
- [ ] [T025] [US2] Refactor existing list into `CategoryView` component in `frontend/src/components/knuspr/CategoryView.tsx`
- [ ] [T026] [US2] Integrate view switching logic into Grocery Cart page in `frontend/src/app/grocery-carts/[id]/page.tsx`
- [ ] [T027] [US2] Add E2E test for view toggling in `frontend/e2e/grocery-cart-views.spec.ts`

## Phase 6: Polish
*Cross-cutting concerns and final verification.*

- [ ] [T028] Implement UI for handling unavailable/unmatched items in `frontend/src/app/grocery-carts/[id]/page.tsx`
- [ ] [T029] Optimize database queries with eager loading in `backend/app/services/grocery_aggregator.py`
- [ ] [T030] Verify accessibility (ARIA labels) of new components in `frontend/src/components/knuspr/`
- [ ] [T031] Run full E2E regression suite including `frontend/e2e/meal-plan-flow.spec.ts`

## Dependencies
- KnusprMCPClient (Existing)
- IngredientMapper (Existing)
- MealPlan models (Existing)

## Implementation Strategy
1. **Backend First**: Build the aggregation logic and API endpoints to ensure data is available.
2. **Frontend Integration**: Connect the UI to the new endpoints, starting with the basic list view.
3. **Knuspr Connection**: Add the "Fill Cart" functionality once the local cart is stable.
4. **View Refinement**: Add the view toggling and polish the UI.
