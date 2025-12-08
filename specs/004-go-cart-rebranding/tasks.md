---
description: "Task list for Go, Cart! Rebranding feature implementation"
---

# Tasks: Go, Cart! Rebranding

**Input**: Design documents from `/specs/004-go-cart-rebranding/`
**Prerequisites**: plan.md, design-spec.md, data-model.md, contracts/waitlist-api.yaml

**Tests**: Tests are included as requested in the plan (TDD for API).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: [US1] Waitlist Backend, [US2] Frontend Foundation, [US3] Animations, [US4] Integration

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize the new frontend project and prepare the backend environment.

- [x] T001 Create frontend directory structure at `frontend/`
- [x] T002 Initialize Next.js 14 project in `frontend/` with TypeScript
- [x] T003 [P] Configure Tailwind CSS with design tokens in `frontend/tailwind.config.ts`
- [x] T004 [P] Configure ESLint and Prettier in `frontend/.eslintrc.json` and `frontend/.prettierrc`
- [x] T005 Install frontend dependencies (framer-motion, gsap, lenis) in `frontend/package.json`
- [x] T006 [P] Setup font loading (Cabinet Grotesk, Inter) in `frontend/src/app/layout.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for backend and frontend base.

- [x] T012 [P] [US1] Create WaitlistEntry model in `backend/app/models/waitlist.py`
- [x] T013 [P] [US1] Create Waitlist schemas in `backend/app/schemas/waitlist.py`
- [x] T007 Create Waitlist database migration in `backend/migrations/versions/`
- [x] T008 [P] Define shared types/interfaces in `frontend/src/types/index.ts`
- [x] T009 [P] Create base UI components (Button, Container) in `frontend/src/components/ui/`
- [x] T010 Setup global CSS variables for colors/themes in `frontend/src/app/globals.css`

**Checkpoint**: Frontend project ready for components, Backend DB ready for models.

---

## Phase 3: User Story 1 - Waitlist Backend Service (Priority: P1) 🎯 MVP

**Goal**: Enable backend support for waitlist signups and email verification.

**Independent Test**: Verify API endpoints using `backend/tests/integration/test_waitlist.py`.

### Tests for User Story 1
- [ ] T011 [P] [US1] Create integration test for waitlist flow in `backend/tests/integration/test_waitlist.py`

### Implementation for User Story 1
- [ ] T014 [US1] Update EmailService to support verification emails in `backend/app/services/email.py`
- [ ] T037 [US1] Create HTML email template for verification in `backend/app/templates/email/verification.html`
- [x] T015 [US1] Implement Waitlist API endpoints (including resend logic) in `backend/app/api/v1/waitlist.py`
- [x] T016 [US1] Register waitlist router in `backend/app/api/v1/__init__.py`
- [ ] T038 [US1] Instrument Waitlist API with Prometheus metrics in `backend/app/api/v1/waitlist.py`

**Checkpoint**: Backend API is fully functional and passes tests.

---

## Phase 4: User Story 2 - Landing Page Structure & Static Layout (Priority: P2)

**Goal**: Implement the visual structure of the landing page with responsive design.

**Independent Test**: Visually verify the landing page renders all sections correctly on mobile and desktop.

### Implementation for User Story 2
- [x] T017 [P] [US2] Create Hero section component in `frontend/src/components/sections/hero.tsx`
- [x] T018 [P] [US2] Create Curation section component in `frontend/src/components/sections/curation.tsx`
- [x] T019 [P] [US2] Create Planning section component in `frontend/src/components/sections/planning.tsx`
- [x] T020 [P] [US2] Create Aggregation section component in `frontend/src/components/sections/aggregation.tsx`
- [x] T021 [P] [US2] Create Checkout section component in `frontend/src/components/sections/checkout.tsx`
- [x] T022 [P] [US2] Create Footer component in `frontend/src/components/sections/footer.tsx`
- [x] T023 [US2] Assemble landing page in `frontend/src/app/page.tsx`

**Checkpoint**: Static landing page is viewable and responsive.

---

## Phase 5: User Story 3 - Advanced Animations & Interactivity (Priority: P3)

**Goal**: Add the "Wow" factor with scroll-linked animations and micro-interactions.

**Independent Test**: Verify animations trigger correctly on scroll and interactions feel smooth.

### Implementation for User Story 3
- [ ] T024 [P] [US3] Configure Lenis smooth scrolling in `frontend/src/lib/animations/smooth-scroll.tsx`
- [ ] T025 [P] [US3] Implement GSAP ScrollTrigger logic for Aggregation section in `frontend/src/components/sections/aggregation.tsx`
- [ ] T026 [P] [US3] Add Framer Motion entrance animations to Hero in `frontend/src/components/sections/hero.tsx`
- [ ] T027 [P] [US3] Add drag-and-drop animation to Planning section in `frontend/src/components/sections/planning.tsx`
- [ ] T028 [US3] Implement scroll progress indicator in `frontend/src/components/ui/progress-indicator.tsx`

**Checkpoint**: Landing page is fully animated and interactive.

---

## Phase 6: User Story 4 - Waitlist Frontend Integration (Priority: P4)

**Goal**: Connect the frontend landing page to the backend Waitlist API.

**Independent Test**: Verify full user flow: Signup on frontend -> Backend DB entry -> Email received.

### Implementation for User Story 4
- [ ] T029 [P] [US4] Create WaitlistForm component in `frontend/src/components/sections/waitlist-form.tsx`
- [ ] T030 [US4] Implement API client for waitlist endpoints in `frontend/src/lib/api.ts`
- [ ] T039 [US4] Implement IndexedDB wrapper for offline storage in `frontend/src/lib/offline-storage.ts`
- [ ] T040 [US4] Create Service Worker for background sync in `frontend/public/sw.js` and registration in `frontend/src/app/providers.tsx`
- [ ] T031 [US4] Integrate form with API, offline queueing, and handle loading/error states in `frontend/src/components/sections/waitlist-form.tsx`
- [ ] T032 [US4] Create Email Verification page and logic in `frontend/src/app/verify/page.tsx`

**Checkpoint**: Full feature is functional end-to-end.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final optimizations and checks.

- [ ] T033 [P] Add SEO meta tags and Open Graph images in `frontend/src/app/layout.tsx`
- [ ] T034 [P] Optimize images and assets in `frontend/public/`
- [ ] T035 Verify accessibility (ARIA labels, keyboard nav) across all components
- [ ] T036 Run Lighthouse performance audit and optimize bundle size

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup.
- **US1 (Backend)**: Depends on Foundational (DB migration).
- **US2 (Frontend Static)**: Depends on Foundational (UI components).
- **US3 (Animations)**: Depends on US2 (Sections must exist).
- **US4 (Integration)**: Depends on US1 (API) and US2 (UI).

### Parallel Opportunities
- US1 (Backend) and US2 (Frontend Static) can be developed in parallel after Phase 2.
- Within US2, all sections (Hero, Curation, etc.) can be built in parallel.
- Within US3, animations for different sections can be implemented in parallel.

## Implementation Strategy

### MVP First (US1 + US2 + US4 Basic)
1. Complete Setup & Foundational.
2. Build Backend API (US1).
3. Build Static Frontend (US2).
4. Integrate Basic Signup Form (US4).
5. **Release MVP** (Functional waitlist, static page).

### Enhanced Experience (US3)
1. Add Animations and Polish (US3).
2. **Release Full Experience**.
