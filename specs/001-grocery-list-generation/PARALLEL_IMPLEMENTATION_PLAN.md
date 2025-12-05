# Parallel Implementation Plan: Grocery List Generation

**Feature Branch**: `001-grocery-list-generation`
**Execution Strategy**: Multi-instance parallel execution with phase-based synchronization

## Execution Phases

### Phase 1: Setup (Sequential - 2 parallel tasks)
**Prerequisite**: None
**Blocking**: Phase 2, 3, 4, 5

**Parallel Group 1A: API Contracts**
- **Instance 1**: T001 - Create OpenAPI contract for grocery list generation
- **Instance 2**: T002 - Create Knuspr integration workflow contract

**Sync Point**: Both contracts must be complete before Phase 2

---

### Phase 2: Foundational Backend (Parallel - 3 groups)
**Prerequisite**: Phase 1 complete
**Blocking**: Phase 3, 4

**Parallel Group 2A: Database Layer**
- **Instance 1**:
  - T003 - Create Alembic migration for `recipe_ids` column
  - T004 - Update `CartItem` SQLAlchemy model

**Parallel Group 2B: Service Implementation**
- **Instance 2**:
  - T005 - Create `GroceryAggregator` service skeleton
  - T006 - Implement ingredient string parsing logic
  - T007 - Implement unit conversion and normalization logic

**Parallel Group 2C: Testing**
- **Instance 3**:
  - T008 - Create unit tests for ingredient parsing and aggregation
  - (Wait for 2B to have service skeleton, then write tests)

**Sync Point**: All backend foundation tasks complete, tests passing

---

### Phase 3: User Story 1 - Aggregated Grocery List (Parallel - 2 groups)
**Prerequisite**: Phase 2 complete
**Blocking**: Phase 6

**Parallel Group 3A: Backend API**
- **Instance 1**:
  - T009 - Implement `aggregate_from_meal_plan` method
  - T010 - Update `CartItemSchema` with `recipe_sources`
  - T011 - Implement `create_cart_from_meal_plan` endpoint
  - T012 - Add integration tests for cart creation

**Parallel Group 3B: Frontend UI**
- **Instance 2**:
  - T013 - Update `useGroceryCarts` hook with generation mutation
  - T014 - Create `CartGenerationButton` component
  - T015 - Add generation button to Meal Plan details page

**Sync Point**: Backend API deployed + Frontend integrated, E2E smoke test

---

### Phase 4: User Story 3 - Knuspr Cart Integration (Parallel - 2 groups)
**Prerequisite**: Phase 2 complete
**Blocking**: Phase 6

**Parallel Group 4A: Backend Knuspr Client**
- **Instance 1**:
  - T016 - Update `KnusprMCPClient` with batched cart addition
  - T017 - Implement `fill_knuspr_cart` endpoint with progress tracking

**Parallel Group 4B: Frontend Knuspr UI**
- **Instance 2**:
  - T018 - Create `useKnusprCart` hook for cart population
  - T019 - Create `FillCartButton` component with progress
  - T020 - Integrate Knuspr authentication check and redirect
  - T021 - Add E2E test for Knuspr cart population

**Sync Point**: Knuspr integration working end-to-end, E2E test passing

---

### Phase 5: User Story 2 - View Switching (Parallel - 2 groups)
**Prerequisite**: Phase 3 complete (backend API available)
**Blocking**: Phase 6

**Parallel Group 5A: View Components**
- **Instance 1**:
  - T023 - Create `ViewToggle` component
  - T024 - Create `RecipeView` component
  - T025 - Refactor existing list into `CategoryView` component

**Parallel Group 5B: State Management & Integration**
- **Instance 2**:
  - T022 - Update `groceryCartReducer` for `viewMode` state
  - T026 - Integrate view switching into Grocery Cart page
  - T027 - Add E2E test for view toggling

**Sync Point**: View toggling working, E2E test passing

---

### Phase 6: Polish & Verification (Parallel - 3 groups)
**Prerequisite**: Phase 3, 4, 5 complete
**Blocking**: PR merge

**Parallel Group 6A: UI Polish**
- **Instance 1**:
  - T028 - Implement UI for unavailable/unmatched items

**Parallel Group 6B: Performance**
- **Instance 2**:
  - T029 - Optimize database queries with eager loading

**Parallel Group 6C: Quality Assurance**
- **Instance 3**:
  - T030 - Verify accessibility (ARIA labels)
  - T031 - Run full E2E regression suite

**Final Sync Point**: All polish complete, full test suite passing

---

## Dependency Graph

```
Phase 1 (Setup)
    ├─ T001 (Instance 1) ─┐
    └─ T002 (Instance 2) ─┴─> Phase 2 (Foundational)
                                ├─ T003, T004 (Instance 1) ─┐
                                ├─ T005, T006, T007 (Instance 2) ─┤
                                └─ T008 (Instance 3) ─────────────┴─> Phase 3 & 4 (Parallel)
                                                                        ├─ Phase 3 (US1)
                                                                        │   ├─ T009-T012 (Instance 1)
                                                                        │   └─ T013-T015 (Instance 2)
                                                                        │       │
                                                                        │       └─> Phase 5 (US2)
                                                                        │           ├─ T023-T025 (Instance 1)
                                                                        │           └─ T022, T026-T027 (Instance 2)
                                                                        │               │
                                                                        └─ Phase 4 (US3) │
                                                                            ├─ T016-T017 (Instance 1)
                                                                            └─ T018-T021 (Instance 2)
                                                                                │
                                                                                └─> Phase 6 (Polish)
                                                                                    ├─ T028 (Instance 1)
                                                                                    ├─ T029 (Instance 2)
                                                                                    └─ T030-T031 (Instance 3)
```

## Instance Allocation Strategy

### Instance 1: Backend Specialist
- Phases 1, 2, 3, 4 - Backend implementation
- Phase 6 - UI polish

### Instance 2: Full-Stack Developer
- Phases 1, 2, 3, 4, 5 - Frontend + Backend integration
- Phase 6 - Performance optimization

### Instance 3: QA/Testing Specialist
- Phase 2 - Unit tests
- Phase 6 - Accessibility & regression testing

## Execution Commands

### Phase 1: Setup
```bash
# Terminal 1
claude chat --prompt "Implement T001: Create OpenAPI contract for grocery list generation endpoints in specs/001-grocery-list-generation/contracts/grocery-list-api.yaml"

# Terminal 2
claude chat --prompt "Implement T002: Create contract for Knuspr integration workflow in specs/001-grocery-list-generation/contracts/knuspr-integration.yaml"
```

### Phase 2: Foundational Backend
```bash
# Terminal 1
claude chat --prompt "Implement T003-T004: Create Alembic migration for recipe_ids column and update CartItem model"

# Terminal 2
claude chat --prompt "Implement T005-T007: Create GroceryAggregator service with ingredient parsing and unit conversion logic"

# Terminal 3 (after T005 skeleton exists)
claude chat --prompt "Implement T008: Create unit tests for ingredient parsing and aggregation logic in backend/tests/unit/test_grocery_aggregator.py"
```

### Phase 3: User Story 1
```bash
# Terminal 1
claude chat --prompt "Implement T009-T012: Backend API for cart generation from meal plans with integration tests"

# Terminal 2
claude chat --prompt "Implement T013-T015: Frontend UI for cart generation button in meal plan details page"
```

### Phase 4: User Story 3
```bash
# Terminal 1
claude chat --prompt "Implement T016-T017: Backend Knuspr cart filling endpoint with batched operations and progress tracking"

# Terminal 2
claude chat --prompt "Implement T018-T021: Frontend Knuspr cart integration with authentication and E2E tests"
```

### Phase 5: User Story 2
```bash
# Terminal 1
claude chat --prompt "Implement T023-T025: Create ViewToggle, RecipeView, and CategoryView components"

# Terminal 2
claude chat --prompt "Implement T022, T026-T027: Update groceryCartReducer, integrate view switching, and add E2E tests"
```

### Phase 6: Polish
```bash
# Terminal 1
claude chat --prompt "Implement T028: Add UI for handling unavailable/unmatched items"

# Terminal 2
claude chat --prompt "Implement T029: Optimize database queries with eager loading"

# Terminal 3
claude chat --prompt "Implement T030-T031: Verify accessibility and run full E2E regression suite"
```

## Success Criteria per Phase

### Phase 1
- [ ] Both YAML contracts exist and are valid OpenAPI 3.0 specs
- [ ] Contracts reviewed and approved

### Phase 2
- [ ] Database migration applied successfully
- [ ] `CartItem` model includes `recipe_ids` field
- [ ] `GroceryAggregator` service has all methods implemented
- [ ] All unit tests passing (pytest)

### Phase 3
- [ ] Backend API endpoint `/api/v1/workflows/carts/from-meal-plan` works
- [ ] Frontend button triggers cart generation
- [ ] Integration tests passing
- [ ] Manual smoke test: Generate cart from meal plan

### Phase 4
- [ ] Backend endpoint `/api/v1/workflows/carts/{id}/fill-knuspr` works
- [ ] Frontend button shows progress indicator
- [ ] Knuspr authentication flow works
- [ ] E2E test `knuspr-integration.spec.ts` passing

### Phase 5
- [ ] View toggle switches between Recipe and Category views
- [ ] Both views render correctly
- [ ] E2E test `grocery-cart-views.spec.ts` passing

### Phase 6
- [ ] All 31 tasks completed
- [ ] Full E2E regression suite passing
- [ ] No accessibility violations
- [ ] Code review ready

## Risk Mitigation

1. **Phase 2 blocking**: If service implementation (2B) delays testing (2C), Instance 3 can start with skeleton tests
2. **Phase 3-4 parallel**: These are independent and can proceed simultaneously
3. **Phase 5 dependency**: Requires Phase 3 backend API, but can start component work early
4. **Integration issues**: Each phase has sync point with E2E smoke tests

## Communication Protocol

- Each instance commits to feature branch with task ID in commit message
- Sync points require all instances to report completion in shared document
- Blocking issues escalated immediately to master coordinator
