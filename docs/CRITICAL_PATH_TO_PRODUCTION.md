// ... existing code ...
# Critical Path to Production

**Status**: Draft
**Date**: 2025-11-22
**Target**: Production Release v1.0

## Executive Summary

The application backend is mature, with 93% test coverage, active monitoring, and a successful deployment on Railway. However, the frontend lags significantly in stability due to identified architectural debt (state management, auth duplication) and incomplete user flows. The integration with Knuspr (grocery delivery) is functionally tested at the unit level but lacks the end-to-end orchestration required for the core value proposition.

**Current Readiness**:
*   **Backend**: ✅ Production Ready (Minor config tweaks needed)
*   **Frontend**: ⚠️ High Risk (Needs refactoring before feature completion)
*   **Integration**: ⚠️ Partial (MCP client ready, workflow missing)

---

## Phase 1: Core Stability & Reliability (Frontend Refactor)
**Goal**: Eliminate race conditions, data inconsistencies, and auth bugs to ensure a stable user foundation.

*   **[CRITICAL] Centralize Authentication State (ARCH-002)**
    *   *Problem*: Auth state is duplicated across 5+ components, leading to potential sync issues.
    *   *Action*: Implement a React Context `AuthProvider` to serve as the single source of truth.
    *   *Deliverable*: `src/contexts/AuthContext.tsx` replacing local `useState` in all pages.

*   **[CRITICAL] Implement TanStack Query (ARCH-003)**
    *   *Problem*: Data fetching is scattered in `useEffect` hooks with no caching or deduplication.
    *   *Action*: Replace direct API calls with `useQuery` hooks for Recipes, Meal Plans, and Carts.
    *   *Deliverable*: `src/hooks/useRecipes.ts`, `src/hooks/useMealPlans.ts`.

*   **[HIGH] Fix API Client State Mutation (ARCH-001)**
    *   *Problem*: The `ApiClient` class mutates its token, causing side effects.
    *   *Action*: Ensure the refactored immutable `api.ts` is correctly integrated into the new `AuthProvider`.
    *   *Deliverable*: Verified `api.ts` usage in `AuthContext`.

## Phase 2: Critical Integrations (Knuspr Workflow)
**Goal**: Enable the core "Meal Plan to Grocery Cart" value loop.

*   **[CRITICAL] Resolve MCP Deployment Strategy**
    *   *Problem*: Railway deployment likely lacks SSE support for the MCP server, causing 502s.
    *   *Action*: Verify if the local `rohlik-mcp` fork supports SSE. If so, deploy it to Railway. If not, implement a direct HTTP bridge or sidecar.
    *   *Deliverable*: Working `/health` and `/tools/call` endpoints on the deployed MCP service.

*   **[HIGH] Implement End-to-End Cart Workflow (US5)**
    *   *Problem*: The `POST /api/v1/workflows/meal-plan-with-groceries` endpoint is specified but not fully orchestrated.
    *   *Action*: Wire the `MealArchitect` output to the `CartOptimizer` input.
    *   *Deliverable*: Successful conversion of a Meal Plan ID to a Knuspr Cart ID in production.

## Phase 3: Feature Completeness (MVP UI)
**Goal**: Provide the minimum necessary UI for users to utilize the backend features.

*   **[HIGH] Meal Planner UI**
    *   *Action*: Build the multi-step generation form (Preferences -> Constraints -> Generation).
    *   *Deliverable*: `/generate` page connected to `POST /api/v1/meal_plans`.

*   **[HIGH] Cart Preview & Checkout UI**
    *   *Action*: Display the generated cart with "Missing Items" and "Delivery Slot" selection.
    *   *Deliverable*: `/grocery-carts/[id]` page.

## Phase 4: Production Infrastructure
**Goal**: Secure and monitor the application for public access.

*   **[HIGH] Secrets Management**
    *   *Action*: Rotate all development keys. Ensure `KNUSPR_ENCRYPTION_KEY` and `JWT_SECRET` are set in Railway/Vercel production environments.
    *   *Deliverable*: Verified environment variable audit.

*   **[MEDIUM] Monitoring Alerts**
    *   *Action*: Configure Grafana alerts for "High Error Rate" (>5%) and "MCP Connection Failure".
    *   *Deliverable*: Active AlertManager rules.

## Phase 5: Final Polish
**Goal**: UX improvements and documentation.

*   **[MEDIUM] User Documentation**
    *   *Action*: Update `README.md` and create a "Getting Started" guide for end-users.
*   **[LOW] UI Polish**
    *   *Action*: Add loading skeletons and error boundaries (ARCH-008).
// ... existing code ...
