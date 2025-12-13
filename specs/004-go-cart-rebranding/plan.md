# Implementation Plan: Go, Cart! Rebranding

**Branch**: `feature/004-go-cart-rebranding` | **Date**: 2025-12-07 | **Spec**: [Design Spec](./design-spec.md)
**Input**: Feature specification from `specs/004-go-cart-rebranding/design-spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Rebrand the "Multi-Agent Recipe and Meal Planning System" to "Go, Cart!" by implementing a high-performance landing page and design system based on Material Design 3. The scope includes a responsive landing page with complex scroll-linked animations, a waitlist signup flow with email verification, and a dual-theme (light/dark) UI foundation using Next.js 14, Tailwind CSS, and Framer Motion/GSAP.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11 (Backend)
**Primary Dependencies**: Next.js 14 (App Router), Tailwind CSS, Framer Motion, GSAP, FastAPI, SQLAlchemy, LangGraph
**Storage**: PostgreSQL (Waitlist data), Redis (Event Bus/Cache)
**Observability**: Sentry (Error Tracking), Prometheus (Metrics)
**Testing**: Playwright (E2E), Jest/Vitest (Unit), Pytest (Backend)
**Target Platform**: Web (Responsive: Mobile, Tablet, Desktop)
**Project Type**: Web application (Frontend + Backend)
**Performance Goals**: Lighthouse Performance > 90, FCP < 1.5s, LCP < 2.5s, CLS < 0.1
**Constraints**: Material Design 3 compliance, Dark/Light mode support, Waitlist email delivery < 5s
**Scale/Scope**: Landing page sections (Hero, Curation, Planning, Aggregation, Checkout), Waitlist API

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality and Maintainability
- [x] **TypeScript Strict Mode**: Frontend will use strict TypeScript configuration.
- [x] **Linting**: ESLint and Prettier will be configured for the new Next.js app.
- [x] **Docstrings/Comments**: Complex animation logic (GSAP/Framer) requires detailed comments.

### II. Testing Discipline
- [x] **Test-First**: API endpoints for waitlist will be TDD'd.
- [x] **Unit Tests**: Components and utility functions will be tested with Jest/Vitest.
- [x] **E2E Tests**: Critical flows (Waitlist signup, Theme switching) will be tested with Playwright.

### III. User Experience Consistency
- [x] **Material Design 3**: Design tokens and components will strictly follow MD3 (colors, typography, elevation).
- [x] **Responsiveness**: Mobile-first approach with breakpoints at 640px, 768px, 1024px, 1280px.
- [x] **Theme Support**: System-aware Light/Dark mode implementation.
- [x] **Loading States**: Async operations (signup) will have clear loading indicators.
- [x] **Brand Assets**: SVG logos and icons are defined in `specs/004-go-cart-rebranding/svg-logos.xml` and must be used for brand consistency.

### IV. Performance and Scalability
- [x] **Bundle Size**: **EXCEPTION GRANTED** (See `research.md`). Target < 200KB for Landing Page to support rich animations. Core app remains < 150KB.
- [x] **Waitlist SLA**: < 2s response for UI, < 5s for email delivery.
- [x] **Asset Optimization**: WebP images, lazy loading for below-fold content.

### V. Observability and Operational Hygiene
- [x] **Metrics**: Track waitlist submissions, verification rates, and email delivery success.
- [x] **Logging**: Structured logs for backend API.
- [x] **Health Checks**: Endpoint for waitlist service health.

## Project Structure

### Documentation (this feature)

```text
specs/004-go-cart-rebranding/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── app/
│   ├── api/v1/
│   │   └── waitlist.py      # New endpoint
│   ├── models/
│   │   └── waitlist.py      # New model
│   ├── schemas/
│   │   └── waitlist.py      # New schema
│   ├── services/
│   │   └── email.py         # Email service update
│   └── templates/
│       └── email/
│           └── verification.html # New email template
└── tests/
    └── integration/
        └── test_waitlist.py

frontend/ (New Directory)
├── public/
│   └── sw.js                # Service Worker for background sync
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/              # MD3 Primitives
│   │   └── sections/        # Landing Page Sections
│   ├── lib/
│   │   ├── animations/      # GSAP/Framer logic
│   │   ├── offline-storage.ts # IndexedDB wrapper
│   │   └── utils.ts
│   └── types/
└── tests/
```

**Structure Decision**: We are introducing a `frontend` directory for the Next.js application, keeping it separate from the existing FastAPI `backend`. This aligns with the "Web application" structure option.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Bundle Size Target (200KB vs 150KB) | Rich animations (GSAP) and potential 3D elements (Three.js) required for "Wow" factor in rebranding. | Pure CSS/Simple JS animations fail to meet the "Premium" and "Smart" brand personality requirements. |
