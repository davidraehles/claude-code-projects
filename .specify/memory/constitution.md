<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0 (MINOR bump - new feature scope additions)
Rationale: Updated to include all 4 active features currently in scope:
  - 001-grocery-list-generation (implementation in progress)
  - 002-multi-agent-recipe-app (Phase 1D complete, Phase 2 in progress)
  - 003-ai-meal-planner-chat (specification complete, implementation pending)
  - 004-go-cart-rebranding (specification complete, clarified, ready for planning)
  - Added feature-specific compliance checkpoints to Governance section
  - Expanded Scope to explicitly list all 4 features and their status
  - Added rebranding-specific design system compliance principle

Templates Requiring Updates:
  - ✅ spec-template.md (no changes needed - principles already enforced)
  - ✅ plan-template.md (no changes needed - governance process compatible)
  - ✅ tasks-template.md (no changes needed - testing/observability applicable to all features)
  - ⚠ CLAUDE.md (update Active Features section to reflect 004 addition)
  - ⚠ README.md (add Go, Cart! to feature list)

Follow-up TODOs:
  - Update CI/CD pipeline to validate design system compliance for 004-go-cart-rebranding (Material Design 3)
  - Establish rebranding metrics dashboard for brand consistency tracking
  - Configure waitlist email verification monitoring and SLAs
-->

# Multi-Agent Recipe and Meal Planning System - Constitution

## Project Overview

**Project Name**: Multi-Agent Recipe and Meal Planning System

**Purpose**: Enable users to discover recipes, plan weekly meals based on constraints, and automatically generate optimized grocery orders integrated with Knuspr. Rebrand the platform as "Go, Cart!" with modern Material Design principles and waitlist functionality.

**Scope**: Full-stack application (FastAPI backend, Next.js frontend) with multi-agent orchestration using LangGraph

**Active Features in Scope**:
1. **001-grocery-list-generation** - Automated grocery list generation from meal plans with Knuspr integration (Implementation in progress)
2. **002-multi-agent-recipe-app** - Multi-agent recipe harvesting and meal plan generation (Phase 1D complete, Phase 2 in progress)
3. **003-ai-meal-planner-chat** - Conversational AI meal planning interface with voice support (Specification complete, implementation pending)
4. **004-go-cart-rebranding** - Platform rebranding as "Go, Cart!" with Material Design 3, dual-theme support, and waitlist functionality (Specification complete with clarifications, ready for planning)

---

## Core Principles

### I. Code Quality and Maintainability

**Non-negotiable Rules:**
- All code MUST pass type checking (mypy for Python, TypeScript strict mode for frontend)
- All code MUST conform to linting standards (Black/isort for Python, ESLint for TypeScript)
- Complex functions MUST have docstrings explaining inputs, outputs, and side effects
- No unused imports, variables, or commented-out code allowed
- Database queries MUST use parameterized statements (SQLAlchemy ORM, not raw SQL)

**Rationale:** Type safety and consistent style reduce bugs, improve readability, and enable confident refactoring. This is especially critical in a multi-agent system where component interdependencies are high.

---

### II. Testing Discipline (Test-First Development)

**Non-negotiable Rules:**
- New features MUST have tests written BEFORE implementation (Red-Green-Refactor cycle)
- All functions returning values MUST have unit tests (target ≥80% code coverage)
- All API endpoints MUST have integration tests verifying request/response contracts
- All inter-agent workflows MUST have end-to-end tests with mocked external services
- Database migrations MUST be tested in isolation before merge
- Tests MUST be deterministic and not depend on external services (use fixtures, mocks, in-memory databases)
- Test naming MUST follow pattern: `test_<function/endpoint>_<scenario>_<expected_result>`
- All tests MUST pass locally before CI/CD approval

**Rationale:** Test-first development catches bugs early, forces clear API design, and documents expected behavior. In a distributed system with agents, this is the primary defense against integration failures.

---

### III. User Experience Consistency

**Non-negotiable Rules:**
- All UI components MUST follow established design patterns (TailwindCSS utility classes, component hierarchy)
- All form inputs MUST have real-time validation feedback and clear error messages
- All async operations MUST show loading states (spinners, skeleton screens, progress indicators)
- All errors MUST be user-friendly (no stack traces) and actionable (suggest next steps)
- All workflows MUST maintain consistent navigation patterns and confirmation dialogs for destructive actions
- Accessibility MUST be verified: semantic HTML, ARIA labels, keyboard navigation support
- All UI MUST be responsive across desktop (1024+px), tablet (768-1023px), and mobile (<768px)

**Additional Requirements for 004-go-cart-rebranding:**
- All UI components MUST follow Material Design 3 principles (color system, typography, spacing, shadows)
- The application MUST support both light and dark themes with automatic system preference detection
- Brand identity "Go, Cart!" and tagline "Favorites on repeat. New loves on deck. Groceries on autopilot." MUST be consistently applied across all pages
- Waitlist signup form MUST provide user-friendly status feedback for email queuing, verification, and confirmation

**Rationale:** Consistent, polished UX builds user confidence and reduces support burden. Clear error handling and loading states are essential when coordinating multi-agent workflows with unpredictable latencies. Material Design 3 compliance ensures the rebranding is modern, accessible, and professional.

---

### IV. Performance and Scalability

**Non-negotiable Rules:**
- API response times MUST be <200ms for standard queries (indexed lookups, simple aggregations)
- Meal plan generation MUST complete within 5 seconds for typical constraints (7-day plan, <100 recipes)
- Frontend bundle size MUST remain <150KB (gzipped), <500KB uncompressed
- Database queries MUST use indexes on frequently filtered columns (user_id, created_at, source_url)
- Long-running operations (recipe scraping, cart creation) MUST be async with progress tracking
- Caching MUST be implemented for static/semi-static data (ingredient taxonomy, user preferences)
- N+1 queries MUST be eliminated through proper ORM eager loading or database denormalization
- All URLs/endpoints MUST support pagination (default 20, max 100 items)

**Additional Requirements for 004-go-cart-rebranding:**
- Waitlist signup form MUST respond within 2 seconds for UI interactions
- Email verification MUST be sent within 5 seconds of form submission
- Verification link clicks MUST result in confirmation within 2 seconds
- Material Design assets (fonts, icons, images) MUST be optimized and lazy-loaded

**Rationale:** Performance directly impacts user satisfaction and operational costs. Scalability constraints ensure the system can grow from pilot users to production scale without architectural changes. Rebranding performance targets ensure users perceive the platform as fast and modern.

---

### V. Observability and Operational Hygiene

**Non-negotiable Rules:**
- All agents MUST emit structured logs in JSON format with correlation IDs for tracing requests
- All async operations MUST emit start/complete/error events to the event bus
- All database operations MUST emit Prometheus metrics (operation count, latency percentiles)
- All API endpoints MUST have request/response metrics and error tracking
- Failed operations MUST be routed to Dead Letter Queue (DLQ) for review and manual recovery
- Health checks MUST be exposed at GET /health (overall system) and /health/agents (agent status)
- Production deployments MUST have alerting for: error rate >5%, p99 latency >1s, agent health failures
- All configuration MUST come from environment variables (12-factor app compliance)

**Additional Requirements for 004-go-cart-rebranding:**
- Waitlist signup events MUST emit metrics for: submissions, verifications, confirmation rates
- Email delivery MUST be tracked with success/failure metrics (target: 99% delivery)
- Database connection failures MUST emit alerts for asynchronous queue buildup
- Brand consistency MUST be measurable (track Material Design compliance metrics)

**Rationale:** Distributed systems fail in unexpected ways. Comprehensive observability enables rapid diagnosis, incident response, and post-mortems. This principle supports the multi-agent architecture's operational complexity. For the rebranding, observability ensures we can monitor waitlist growth and user engagement.

---

## Decision-Making Framework

### How Principles Guide Technical Choices

When evaluating technology, design, or architectural decisions, apply these filters in order:

1. **Testing**: Does it support automated testing? Can we write tests before code?
2. **Quality**: Does it enforce type safety, linting, and code organization?
3. **UX Consistency**: Does it align with established patterns (TailwindCSS, Next.js conventions, Material Design 3)?
4. **Performance**: Does it meet latency/throughput SLAs? Is scalability clear?
5. **Observability**: Can we instrument it? Does it emit required metrics/logs?

**Example Decision**: Choosing a UI component library for 004-go-cart-rebranding
- ❌ Reject: Library without Material Design 3 support (violates UX Consistency)
- ❌ Reject: Library without TypeScript support (violates Code Quality)
- ❌ Reject: Library that requires deeply nested mocking in tests (violates Testing Discipline)
- ✅ Accept: Built custom components with Tailwind + CSS variables aligned to Material Design 3 color system
- ✅ Accept: Use Shadcn/ui or similar Material Design-compatible component library if team consensus

---

## Governance

### Amendment Procedure

1. **Proposal**: File a GitHub issue titled "Constitution Amendment: <brief description>" with rationale
2. **Discussion**: Team reviews (minimum 24h), discusses trade-offs, gathers consensus
3. **Ratification**: Merge pull request in constitution.md with updated version and LAST_AMENDED_DATE
4. **Enforcement**: Update dependent templates and CI/CD gates within 1 week of ratification
5. **Documentation**: Announce amendment in team channels with affected workflows

### Versioning Policy

Constitution follows Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR** (e.g., 2.0.0): Principle removed, redefined, or backward-incompatible change (requires all in-flight work to be reviewed)
- **MINOR** (e.g., 1.1.0): Principle added or materially expanded (affects future PRs; grace period for existing work)
- **PATCH** (e.g., 1.0.1): Clarifications, wording updates, non-semantic refinements (no review impact)

### Compliance Review & Enforcement

- **Code Review**: Every PR MUST verify compliance with applicable principles (checklist in PR template)
- **Automated Gates**: CI/CD MUST enforce: linting (Black, ESLint), coverage (≥80%), type checking (mypy, tsc), test passing
- **Design System Gates** (for 004-go-cart-rebranding): PR MUST verify Material Design 3 compliance using Lighthouse and design system review checklist
- **Manual Gates**: Code reviewers verify: test quality, API design, UX consistency, observability (logs/metrics present), design system alignment
- **Monthly Audit**: Engineering lead reviews failed PRs/deployments to identify principle drift

### Feature-Specific Compliance Checkpoints

**001-grocery-list-generation:**
- Ingredient aggregation logic MUST be unit tested (edge cases: duplicate detection, quantity merging)
- Knuspr integration MUST have integration tests with mocked API
- Performance: grocery list generation <2 seconds for typical meal plans

**002-multi-agent-recipe-app:**
- Recipe harvester agents MUST emit structured logs with source tracking
- Meal architect constraint satisfaction MUST complete within 5-second SLA
- Cart optimizer MUST track Knuspr API success rates and fallback behavior

**003-ai-meal-planner-chat:**
- Voice input/output MUST have graceful fallback to text-based interaction
- Conversation state MUST persist in database with user preference tracking
- Natural language processing errors MUST show helpful alternatives to user

**004-go-cart-rebranding:**
- Material Design 3 compliance MUST pass automated Lighthouse and accessibility audits
- Waitlist email verification MUST have 99% delivery SLA and <5-second send latency
- Theme switching (light/dark) MUST respect system preferences and be persistence-capable
- Database connection failures during signup MUST trigger async queue with local persistence

### Principle Mapping to Implementation

| Principle | Key Tools/Standards | Enforcement |
|-----------|-------------------|------------|
| Code Quality | Black, isort, mypy, ESLint, TypeScript | Pre-commit hooks, CI/CD gate |
| Testing | pytest, Jest, Playwright, pytest-cov | Coverage reports, CI/CD gate (≥80%) |
| UX Consistency | TailwindCSS, Next.js patterns, Material Design 3, Storybook | Design system reviews, Lighthouse audits, browser testing |
| Performance | Apache Bench, Lighthouse, Prometheus | SLA monitoring, Grafana dashboards |
| Observability | Prometheus metrics, structured JSON logs, event bus | Health check endpoints, alert rules, email delivery tracking |

---

## Metadata

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Status** | Ratified |
| **Ratified Date** | 2025-11-22 |
| **Last Amended** | 2025-12-07 |
| **Author** | Claude Code (AI Assistant) |
| **Scope** | All 4 active features: 001-grocery-list-generation, 002-multi-agent-recipe-app, 003-ai-meal-planner-chat, 004-go-cart-rebranding |
| **Review Frequency** | Monthly (first Monday of each month) |

---

## Quick Reference for Developers

### Before Writing Code
- [ ] Read the relevant Principle section above
- [ ] For feature 004: Verify Material Design 3 requirements and theme support expectations
- [ ] Ensure your feature plan includes test strategy (Red-Green-Refactor)
- [ ] Verify you understand the UX pattern (desktop, tablet, mobile)
- [ ] Confirm API latency targets align with Performance principle
- [ ] Check what metrics/logs are required (Observability principle)

### Before Opening a PR
- [ ] All tests pass locally: `pytest` (backend), `npm test` (frontend)
- [ ] Type checking passes: `mypy src`, `tsc --noEmit` (frontend)
- [ ] Linting passes: `black src`, `eslint src`
- [ ] Coverage report shows ≥80%: `pytest --cov=src`
- [ ] For feature 004: Lighthouse audit score ≥90 (Performance, Accessibility)
- [ ] PR template includes Constitution compliance checklist

### Code Review Checklist
Reviewers MUST verify:
- [ ] Tests written first (see test file changes before implementation)
- [ ] Tests are comprehensive (happy path, edge cases, error scenarios)
- [ ] All API endpoints documented (OpenAPI/Swagger)
- [ ] No unused imports, variables, or commented code
- [ ] Type hints present on all functions
- [ ] Database queries use ORM (no raw SQL except migrations)
- [ ] Error messages are user-friendly
- [ ] Loading states shown for async operations
- [ ] Metrics/logging emitted (search for `logger`, `metrics`, event bus calls)
- [ ] Mobile responsive (verified in browser dev tools)
- [ ] For feature 004: Material Design 3 compliance verified (colors, typography, spacing, themes)
- [ ] For feature 004: Light/dark theme switching tested with system preference changes

---

## FAQ

**Q: What if a deadline pressure is creating test debt?**
A: Test-first is non-negotiable. Time pressures are managed by reducing scope, not test quality. Failing to test now creates larger delays during integration and production incidents.

**Q: Can we skip tests for "simple" changes?**
A: No. Simplicity is often an illusion. A one-line change can have cascading effects in a multi-agent system. All changes require tests. If a change is truly trivial, the test is trivial too (1-2 lines).

**Q: What if performance optimization requires breaking the API contract?**
A: Address via gradual migration: (1) new endpoint alongside old, (2) client-side feature flag to switch, (3) deprecation period, (4) old endpoint removal. Constitution's Performance principle does not override Testing or UX Consistency.

**Q: How do we handle technical debt in observability?**
A: Technical debt in observability (missing metrics, unclear logs) is treated as a bug. If you can't diagnose an issue in production, that's a bug. Add observability as part of the fix.

**Q: Who enforces this constitution?**
A: Shared responsibility. Code reviewers (primary), CI/CD gates (automated), team leads (audits), and all engineers (self-enforcement through culture).

**Q: What about the Material Design 3 requirement for feature 004?**
A: Material Design 3 compliance is a non-negotiable part of the UX Consistency principle for the rebranding. Lighthouse audits for Accessibility (target 95+) and Performance (target 90+) are required before PR merge. Design system reviews verify color contrast, typography scale, and theme switching functionality.

**Q: How do we monitor waitlist signup health?**
A: Observability principle requires tracking: email submission count, verification email delivery (99% SLA), confirmation clicks, and database queue size. Alert if email delivery drops below 98% or queue grows beyond 100 items. Weekly reports in team channels.

---

**This constitution is living documentation. All team members are responsible for understanding, following, and improving it.**
