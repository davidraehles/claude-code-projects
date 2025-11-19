# Implementation Plan: AI Meal Planner Chat Assistant

**Branch**: `003-ai-meal-planner-chat` | **Date**: 2025-11-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-ai-meal-planner-chat/spec.md`

---

## Summary

The AI Meal Planner Chat Assistant replaces form-based meal planning with a conversational AI interface. Users describe their dietary needs through natural language chat, receiving personalized meal plans in under 5 minutes. The feature includes voice input/output for hands-free planning and persistent preference storage for returning users. Built on top of the existing recipe management system, it integrates with LLM services and speech-to-text APIs while maintaining 100% compliance with dietary restrictions and GDPR requirements.

---

## Technical Context

**Language/Version**: Python 3.11 (backend) + Next.js 14 with TypeScript (frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, Pydantic, async libraries
- Frontend: React 18, Next.js 14, TypeScript, React Query
- LLM Integration: OpenAI API (or compatible LLM provider)
- Speech Services: Web Speech API (browser-native) + optional cloud STT/TTS service

**Storage**: PostgreSQL (existing database) for chat history, meal plans, user profiles, preferences

**Testing**:
- Frontend: Playwright (E2E + integration)
- Backend: pytest with SQLAlchemy test fixtures
- API Contract: OpenAPI schema validation

**Target Platform**: Web (Vercel-deployed frontend + Railway-deployed backend)

**Project Type**: Full-stack web application (frontend + backend)

**Performance Goals**:
- Meal plan generation: <10 seconds (constraint from spec)
- Chat message processing: <2 seconds round-trip
- Voice transcription: <5 seconds (constraint from spec)
- 95% uptime (constraint from spec)

**Constraints**:
- Unlimited concurrent user scalability (from clarifications)
- 100% allergen compliance (zero allergen-containing meals in plans)
- WCAG 2.1 Level AA desktop / AAA mobile accessibility
- GDPR-compliant with indefinite retention + user deletion rights
- Internet-required for chat/AI; offline caching for meal plans & preferences

**Scale/Scope**:
- MVPUser base: 1000-10,000 users (startup phase)
- Concurrent users: Unlimited with auto-scaling
- Data: ~50-100 lines of chat per session, ~7-30 days of meal plans retained

---

## Constitution Check

**Gate Status**: ✅ **PASS** - Feature aligns with all core principles

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Test-First Development** | ✅ PASS | E2E tests already created (`e2e/deployed-app.spec.ts`); backend unit tests planned in Phase 1; TDD cycle enforced |
| **II. Frequent Test-Commit-Push** | ✅ PASS | Specification committed (commit 207837d); plan and research will be committed atomically; feature branch workflow enforced |
| **III. MCP Tool Extensibility** | ✅ PASS | Playwright tests primary validation method; future PydanticAI integration for model validation; no blocking tech conflicts |
| **IV. Spec-Driven Development** | ✅ PASS | Complete spec.md with 4 user stories, 18 FR, 14 SC; clarified (4/4 Q&A resolved); ready for implementation |
| **V. Integration & Contract Testing** | ✅ PASS | API contracts designed in Phase 1; chat integration tested via E2E; voice integration via Playwright |

**Post-Design Re-check**: Will be performed after Phase 1 data-model.md and contracts/ completion.

---

## Project Structure

### Documentation (this feature)

```
specs/003-ai-meal-planner-chat/
├── spec.md                       # Feature specification (224 lines, fully clarified)
├── plan.md                       # This file (implementation plan)
├── research.md                   # Phase 0 output (TBD)
├── data-model.md                # Phase 1 output (TBD)
├── quickstart.md                # Phase 1 output (TBD)
├── contracts/                    # Phase 1 output (TBD)
│   ├── chat-api.openapi.yaml
│   ├── preferences-api.openapi.yaml
│   ├── voice-api.openapi.yaml
│   └── meal-plan-api.openapi.yaml
└── checklists/
    └── requirements.md           # Quality validation checklist
```

### Source Code (repository root)

```
# Option 2: Web application (frontend + backend)

backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── chat.py               # Chat endpoints (new)
│   │   │   ├── preferences.py        # User preferences (new)
│   │   │   ├── voice.py              # Voice processing (new)
│   │   │   ├── meal_plans.py         # Meal plan management (new)
│   │   │   └── [existing endpoints]
│   │   └── dependencies.py
│   ├── models/
│   │   ├── chat_session.py           # Chat session model (new)
│   │   ├── chat_message.py           # Chat message model (new)
│   │   ├── user_preference.py        # User preferences model (new)
│   │   ├── meal_plan.py              # Meal plan model (new)
│   │   └── [existing models]
│   ├── services/
│   │   ├── chat_service.py           # LLM chat orchestration (new)
│   │   ├── preference_service.py     # Preference management (new)
│   │   ├── voice_service.py          # Voice processing (new)
│   │   ├── meal_plan_service.py      # Meal plan generation (new)
│   │   └── [existing services]
│   └── main.py
└── tests/
    ├── contract/
    │   ├── test_chat_api.py          # Chat API contract tests (new)
    │   ├── test_preferences_api.py   # Preferences API contract tests (new)
    │   └── [existing contracts]
    ├── integration/
    │   ├── test_chat_flow.py         # Chat integration tests (new)
    │   ├── test_preference_flow.py   # Preference integration tests (new)
    │   └── [existing integrations]
    └── unit/
        ├── test_chat_service.py      # Chat service unit tests (new)
        ├── test_preference_service.py # Preference service unit tests (new)
        └── [existing unit tests]

frontend/ (meal-planner-ui/)
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx     # Main chat UI (new)
│   │   │   ├── ChatMessage.tsx       # Message display (new)
│   │   │   ├── VoiceInput.tsx        # Voice input button (new)
│   │   │   └── VoiceOutput.tsx       # Voice output player (new)
│   │   ├── preferences/
│   │   │   ├── PreferenceManager.tsx # Preferences UI (new)
│   │   │   └── PreferenceForm.tsx    # Preference editor (new)
│   │   ├── meal-plan/
│   │   │   ├── MealPlanDisplay.tsx   # Meal plan viewer (new)
│   │   │   └── MealExplanation.tsx   # Meal reasoning (new)
│   │   └── [existing components]
│   ├── pages/
│   │   ├── chat.tsx                  # Chat page (new)
│   │   └── [existing pages]
│   ├── services/
│   │   ├── chatApi.ts                # Chat API client (new)
│   │   ├── preferenceApi.ts          # Preference API client (new)
│   │   ├── voiceApi.ts               # Voice API client (new)
│   │   └── [existing services]
│   └── hooks/
│       ├── useChat.ts                # Chat hook (new)
│       ├── usePreferences.ts         # Preferences hook (new)
│       ├── useVoice.ts               # Voice hook (new)
│       └── [existing hooks]
└── tests/
    ├── e2e/
    │   ├── chat-flow.spec.ts         # Chat E2E tests (new)
    │   ├── voice-flow.spec.ts        # Voice E2E tests (new)
    │   ├── preference-flow.spec.ts   # Preference E2E tests (new)
    │   └── [existing specs]
    └── unit/
        ├── ChatInterface.test.tsx    # Chat component tests (new)
        └── [existing tests]
```

**Structure Decision**: Full-stack web application with existing monorepo structure. New chat, preferences, voice, and meal plan features implemented across backend services and frontend components. Leverages existing authentication, database, and API infrastructure. All new code follows project conventions (FastAPI endpoints, React hooks, TypeScript types).

---

## Implementation Phases

### Phase 0: Research & Unknowns Resolution

**Status**: Pending execution

**Tasks**:
1. Research LLM integration patterns for meal planning (Claude API, OpenAI, local models)
2. Research speech-to-text options (Web Speech API, Google Cloud Speech, Azure Cognitive)
3. Research text-to-speech options (Web Speech API, Elevenlabs, AWS Polly)
4. Research chat state management best practices (context windows, message history limits)
5. Research allergen validation patterns (fuzzy matching, ingredient databases)
6. Research accessibility patterns for voice features (ARIA labels, keyboard navigation)

**Output**: `research.md` with decisions, rationales, and alternatives considered

**Estimated Effort**: 2-3 days research + 1 day documentation

---

### Phase 1: Design & API Contracts

**Status**: Pending Phase 0 completion

**Tasks**:
1. Create `data-model.md` with entity relationships, validation rules, state transitions
2. Generate OpenAPI schemas in `contracts/` directory
3. Create `quickstart.md` with local setup instructions
4. Run agent context update script
5. Re-evaluate Constitution Check post-design

**Deliverables**:
- `data-model.md`: Database schema, entity relationships, validation rules
- `contracts/chat-api.openapi.yaml`: Chat endpoints (send message, get history, create session)
- `contracts/preferences-api.openapi.yaml`: Preference endpoints (save, get, update, delete)
- `contracts/voice-api.openapi.yaml`: Voice endpoints (transcribe, synthesize)
- `contracts/meal-plan-api.openapi.yaml`: Meal plan endpoints (generate, get, save, delete)
- `quickstart.md`: Local development guide with example requests

**Estimated Effort**: 3-4 days design + 2 days documentation

---

### Phase 2: Implementation Tasks

**Status**: Pending Phase 1 completion (generated via `/speckit.tasks`)

**High-Level Breakdown** (detailed in tasks.md):

**Backend** (8-10 weeks):
- Week 1-2: Chat session & message models, basic chat API endpoints
- Week 2-3: LLM integration, prompt engineering, conversation context management
- Week 3-4: Preference models & endpoints, permission validation
- Week 4-5: Voice integration (transcription, synthesis)
- Week 5-6: Meal plan service, allergen validation, caching
- Week 6-7: Integration testing, error handling, edge cases
- Week 7-8: Performance optimization, load testing
- Week 8+: Security review, GDPR compliance validation, deployment prep

**Frontend** (6-8 weeks):
- Week 1-2: Chat UI component, message display, input handling
- Week 2-3: Voice input/output buttons, permissions handling
- Week 3-4: Preferences UI, form validation, API integration
- Week 4-5: Meal plan display, explanation UI, offline caching
- Week 5-6: Accessibility (WCAG AA/AAA), keyboard navigation, screen reader tests
- Week 6-7: E2E test coverage, cross-browser testing
- Week 7-8: Performance optimization, bundle size reduction

**Testing** (Parallel - 4-6 weeks):
- Playwright E2E tests for all user flows
- Contract tests for all API endpoints
- Unit tests for services and components
- Accessibility testing (axe, screen readers)
- Load testing for unlimited concurrent users
- Voice recognition accuracy testing

**Estimated Total Effort**: 12-16 weeks (overlapping backend/frontend/testing)

---

## Success Metrics (from Specification)

### Launch Criteria (all MUST be met)

**Functional**:
- ✅ Users complete meal plan generation in <5 minutes (SC-001)
- ✅ 100% compliance with dietary restrictions and allergies (SC-008)
- ✅ Chat interface has 95% uptime (SC-010)
- ✅ System scales to unlimited concurrent users (from clarifications)

**Quality**:
- ✅ 80% of users provide sufficient info on first chat (SC-002)
- ✅ Voice transcription ≥90% accuracy (SC-006)
- ✅ 85% user preference alignment (SC-004)
- ✅ WCAG 2.1 AA (desktop) / AAA (mobile) accessibility (SC-012)
- ✅ GDPR compliance with user deletion rights (SC-014)

**Testing**:
- ✅ 100% E2E test coverage for all user stories
- ✅ 95%+ unit test coverage for services
- ✅ Contract tests pass for all API endpoints
- ✅ Accessibility tests pass (axe, keyboard nav, screen reader)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| LLM hallucinations in meal plans | Medium | High | Strict prompt engineering, allergen validation layer, user feedback loop |
| Voice recognition accuracy <90% | Medium | Medium | Multi-provider fallback, user correction flow, text-only mode |
| Scalability bottleneck at 10k users | Low | High | Early load testing, Redis caching, CDN optimization, horizontal scaling |
| Accessibility compliance gaps | Low | Medium | WCAG audit, axe testing in CI, screen reader testing, keyboard nav validation |
| GDPR data retention complexity | Low | High | Legal review, audit trail logging, automated deletion workflows |

---

## Next Steps

1. ✅ Specification complete and clarified
2. ✅ Constitution check passed
3. ⏭️ **Phase 0**: Execute research tasks → generate `research.md`
4. ⏭️ **Phase 1**: Design data model → generate API contracts → update agent context
5. ⏭️ **Phase 2**: Execute `/speckit.tasks` → implement features in test-first workflow

---

## References

- **Specification**: [spec.md](./spec.md) (224 lines, 18 FR, 14 SC, 4 user stories)
- **Constitution**: [constitution.md](../../.specify/memory/constitution.md) (Test-First, TDD, MCP-extensible)
- **Deployed App**: https://claude-code-projects.vercel.app
- **Repository**: https://github.com/davidraehles/claude-code-projects/tree/003-ai-meal-planner-chat

