# Tasks: Bulk Recipe Import from Parent Websites

**Input**: Design documents from `/specs/005-bulk-import/`  
**Prerequisites**: plan.md (✅), spec.md (from PR description)  
**Feature Branch**: `005-bulk-import`

**Tests**: Tests are included as they are critical for multi-step async operations.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create database migration for bulk import tables in `backend/migrations/versions/xxx_add_bulk_import_tables.py`
- [ ] T002 [P] Create BulkImportJob model in `backend/app/models/bulk_import_job.py`
- [ ] T003 [P] Create ImportedRecipe model in `backend/app/models/imported_recipe.py`
- [ ] T004 [P] Create RecipeDiscoveryResult model in `backend/app/models/recipe_discovery_result.py`
- [ ] T005 [P] Create bulk import schemas in `backend/app/schemas/bulk_import.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement RecipeDiscoveryService in `backend/app/services/recipe_discovery.py` (crawl parent URLs, extract recipe links)
- [ ] T007 [P] Implement DomainRateLimiter utility in `backend/app/utils/rate_limiter.py`
- [ ] T008 [P] Implement LLMClassifier for recipe page detection in `backend/app/utils/llm_classifier.py`
- [ ] T009 Implement ProgressTracker service for SSE in `backend/app/services/progress_tracker.py`
- [ ] T010 Implement BulkImportService orchestrator in `backend/app/services/bulk_import_service.py`
- [ ] T011 Create bulk import API router in `backend/app/api/v1/bulk_import.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Initiate Bulk Import from Parent Site (Priority: P1) 🎯 MVP

**Goal**: User can submit parent URL, system discovers recipe links and imports them

**Independent Test**: POST to `/bulk-import/start` with parent URL, system returns job_id and begins processing

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Unit test for RecipeDiscoveryService in `backend/tests/test_recipe_discovery.py` (test URL crawling, link extraction)
- [ ] T013 [P] [US1] Unit test for BulkImportService in `backend/tests/test_bulk_import_service.py` (test job creation, recipe processing)
- [ ] T014 [P] [US1] Integration test for bulk import flow in `backend/tests/integration/test_bulk_import_flow.py` (start → discover → import → complete)

### Implementation for User Story 1

- [ ] T015 [US1] Implement POST /bulk-import/start endpoint (validate URL, create job, start background task)
- [ ] T016 [US1] Implement GET /bulk-import/{job_id} endpoint (fetch job status and progress)
- [ ] T017 [US1] Implement job discovery phase (crawl parent URL, extract recipe links, store in RecipeDiscoveryResult)
- [ ] T018 [US1] Implement job import phase (iterate discovered links, call existing scrapers, handle errors)
- [ ] T019 [US1] Integrate with existing HTMLRecipeScraper/APIRecipeScraper in import loop
- [ ] T020 [US1] Implement basic error handling (network errors, scraping errors)
- [ ] T021 [US1] Add logging for bulk import operations

**Checkpoint**: At this point, User Story 1 should be fully functional - can start bulk import from API

---

## Phase 4: User Story 2 - Monitor Import Progress with Live Updates (Priority: P1) 🎯 MVP

**Goal**: User sees real-time progress bar with counters during bulk import

**Independent Test**: Start bulk import, connect to SSE endpoint, verify progress updates received in real-time

### Tests for User Story 2

- [ ] T022 [P] [US2] Unit test for ProgressTracker in `backend/tests/test_progress_tracker.py` (test event emission, SSE formatting)
- [ ] T023 [P] [US2] Integration test for SSE stream in `backend/tests/integration/test_sse_progress.py` (verify events received)
- [ ] T024 [P] [US2] E2E test for progress UI in `frontend/e2e/bulk-import-progress.spec.ts` (verify progress bar updates)

### Implementation for User Story 2

- [ ] T025 [US2] Implement GET /bulk-import/{job_id}/progress SSE endpoint
- [ ] T026 [US2] Update BulkImportService to emit progress events after each recipe
- [ ] T027 [US2] Implement ETA calculation in ProgressTracker (based on processing rate)
- [ ] T028 [P] [US2] Create ProgressTracker component in `frontend/src/components/ProgressTracker.tsx`
- [ ] T029 [P] [US2] Create useBulkImport hook in `frontend/src/hooks/useBulkImport.ts` (SSE connection management)
- [ ] T030 [US2] Extend import page in `frontend/src/app/import/page.tsx` to show progress tracker
- [ ] T031 [US2] Add error handling for SSE disconnections (auto-reconnect)

**Checkpoint**: At this point, User Stories 1 AND 2 work together - can see live progress

---

## Phase 5: User Story 3 - Handle Errors and Partial Failures Gracefully (Priority: P2)

**Goal**: Bulk import continues on failures, user sees clear error reporting and can retry

**Independent Test**: Start bulk import with mixed valid/invalid URLs, verify successful imports saved, failures logged with retry capability

### Tests for User Story 3

- [ ] T032 [P] [US3] Unit test for error categorization in `backend/tests/test_error_handler.py` (network vs scraping vs rate limit)
- [ ] T033 [P] [US3] Integration test for retry logic in `backend/tests/integration/test_retry_failed.py` (exponential backoff, max retries)

### Implementation for User Story 3

- [ ] T034 [US3] Implement error categorization in BulkImportService (NetworkError, ScrapingError, RateLimitError)
- [ ] T035 [US3] Implement retry logic with exponential backoff (max 3 attempts for network errors)
- [ ] T036 [US3] Handle rate limiting (429/403) with pause and retry
- [ ] T037 [US3] Implement GET /bulk-import/{job_id}/results endpoint (summary + failed list)
- [ ] T038 [US3] Implement POST /bulk-import/{job_id}/retry endpoint (re-process failed URLs only)
- [ ] T039 [P] [US3] Create ImportSummary component in `frontend/src/components/ImportSummary.tsx` (success/failure counts, error list)
- [ ] T040 [US3] Add retry button to ImportSummary component

**Checkpoint**: At this point, User Stories 1, 2, AND 3 work independently - resilient imports with retry

---

## Phase 6: User Story 4 - Deduplicate Recipes During Bulk Import (Priority: P2)

**Goal**: System automatically skips recipes already in user's library

**Independent Test**: Import single recipe, then bulk import parent URL containing that recipe, verify it's skipped as duplicate

### Tests for User Story 4

- [ ] T041 [P] [US4] Unit test for duplicate detection in `backend/tests/test_duplicate_detection.py` (URL match, title similarity)
- [ ] T042 [P] [US4] Integration test for bulk deduplication in `backend/tests/integration/test_bulk_deduplication.py`

### Implementation for User Story 4

- [ ] T043 [US4] Integrate existing find_duplicate_recipe() function into import loop
- [ ] T044 [US4] Check duplicates by source URL before scraping (fast path)
- [ ] T045 [US4] Check duplicates by title similarity after scraping (if URL not found)
- [ ] T046 [US4] Track duplicate count in BulkImportJob
- [ ] T047 [US4] Add "overwrite_duplicates" option to bulk import request
- [ ] T048 [US4] Implement overwrite logic (update existing recipe if option enabled)
- [ ] T049 [P] [US4] Show duplicate count in ProgressTracker component
- [ ] T050 [US4] Add checkbox for "overwrite duplicates" to BulkImportForm

**Checkpoint**: At this point, all P2 stories complete - deduplication prevents waste

---

## Phase 7: User Story 5 - Cancel or Pause Long-Running Imports (Priority: P3)

**Goal**: User can cancel bulk import, saving already-imported recipes

**Independent Test**: Start bulk import, cancel mid-process, verify status changes to cancelled and imported recipes are preserved

### Tests for User Story 5

- [ ] T051 [P] [US5] Unit test for cancellation in `backend/tests/test_cancellation.py` (graceful shutdown)
- [ ] T052 [P] [US5] Integration test for cancel flow in `backend/tests/integration/test_cancel_import.py`

### Implementation for User Story 5

- [ ] T053 [US5] Implement POST /bulk-import/{job_id}/cancel endpoint
- [ ] T054 [US5] Add cancellation flag to BulkImportJob model
- [ ] T055 [US5] Check cancellation flag in import loop, break gracefully
- [ ] T056 [US5] Complete current recipe before stopping (no partial imports)
- [ ] T057 [US5] Update job status to "cancelled" and set completed_at timestamp
- [ ] T058 [P] [US5] Add cancel button to ProgressTracker component
- [ ] T059 [US5] Handle cancellation in useBulkImport hook (close SSE, show confirmation)

**Checkpoint**: All user stories complete - full bulk import feature functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Optimize rate limiter for production (per-domain token buckets)
- [ ] T061 [P] Add comprehensive logging for debugging
- [ ] T062 [P] Create API documentation in `specs/005-bulk-import/contracts/bulk-import-api.md`
- [ ] T063 [P] Update project README with bulk import feature
- [ ] T064 Security: Add input validation for parent URL (whitelist schemes, sanitize)
- [ ] T065 Security: Add CORS headers for SSE endpoint
- [ ] T066 Performance: Add database indexes for bulk import queries
- [ ] T067 [P] E2E test for complete bulk import flow in `frontend/e2e/bulk-import-e2e.spec.ts`
- [ ] T068 [P] Load testing for 200-recipe bulk import
- [ ] T069 Documentation: Create quickstart guide in `specs/005-bulk-import/quickstart.md`
- [ ] T070 Monitoring: Add Prometheus metrics for bulk import operations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Extends US1 error handling
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Extends US1 import logic
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Adds cancel control to US1/US2

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Backend services before API endpoints
- API endpoints before frontend components
- Core implementation before UI integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Critical Path

The fastest path to MVP (User Stories 1 + 2 only):

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 8 (Polish)
```

**Estimated Time**: 2-3 weeks for MVP (US1 + US2)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T012: "Unit test for RecipeDiscoveryService"
Task T013: "Unit test for BulkImportService"
Task T014: "Integration test for bulk import flow"

# After tests written and failing, launch model creation:
Task T002: "Create BulkImportJob model"
Task T003: "Create ImportedRecipe model"
Task T004: "Create RecipeDiscoveryResult model"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (database, models, schemas)
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (bulk import initiation)
4. Complete Phase 4: User Story 2 (real-time progress)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready

**Result**: Users can bulk import recipes with live progress - core value delivered!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (basic bulk import)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP with progress!)
4. Add User Story 3 → Test independently → Deploy/Demo (error handling)
5. Add User Story 4 → Test independently → Deploy/Demo (deduplication)
6. Add User Story 5 → Test independently → Deploy/Demo (cancellation)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (1 week)
2. Once Foundational is done:
   - Developer A: User Story 1 + User Story 2 (core MVP)
   - Developer B: User Story 3 (error handling)
   - Developer C: User Story 4 (deduplication)
3. Stories complete and integrate independently
4. User Story 5 (cancel) can be added by any developer once US1/US2 are done

---

## Validation Checkpoints

### After Phase 2 (Foundational)
- [ ] Can create BulkImportJob in database
- [ ] RecipeDiscoveryService can crawl test URL and extract links
- [ ] BulkImportService can orchestrate a single recipe import
- [ ] ProgressTracker can emit SSE events

### After Phase 3 (US1)
- [ ] POST /bulk-import/start returns job_id
- [ ] Background task discovers recipe links from parent URL
- [ ] Background task imports each discovered recipe
- [ ] GET /bulk-import/{job_id} shows accurate status

### After Phase 4 (US2)
- [ ] SSE endpoint streams progress events
- [ ] Frontend receives real-time updates without polling
- [ ] Progress bar shows accurate percentage
- [ ] ETA calculation is reasonable

### After Phase 5 (US3)
- [ ] Network errors retry with exponential backoff
- [ ] Scraping errors skip and continue
- [ ] Rate limiting pauses and retries
- [ ] Failed imports listed with error messages
- [ ] Retry endpoint re-processes only failed URLs

### After Phase 6 (US4)
- [ ] Duplicate detection works by URL
- [ ] Duplicate detection works by title similarity (85%+)
- [ ] Duplicate count tracked and displayed
- [ ] Overwrite option updates existing recipes

### After Phase 7 (US5)
- [ ] Cancel button stops import gracefully
- [ ] Current recipe completes before full stop
- [ ] Imported recipes preserved after cancel
- [ ] Job status updated to "cancelled"

### After Phase 8 (Polish)
- [ ] All E2E tests pass
- [ ] Load testing passes (200 recipes)
- [ ] Documentation complete
- [ ] Monitoring metrics available

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = User Stories 1 + 2 (bulk import with progress) - delivers core value
- P2 stories (3 + 4) add resilience and intelligence
- P3 story (5) adds user control for edge cases
