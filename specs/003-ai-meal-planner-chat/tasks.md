# Implementation Tasks: AI Meal Planner Chat Assistant

**Feature**: 003 - AI Meal Planner Chat
**Branch**: `003-ai-meal-planner-chat`
**Created**: 2025-11-19
**Based on**: spec.md (P1-P3 user stories), plan.md (tech stack), data-model.md (entities), contracts/ (API endpoints)

---

## Overview

This document contains all implementation tasks organized by user story priority (P1, P2, P3) and execution phase. Tasks are structured for independent completion with clear file paths and acceptance criteria.

**Total Tasks**: 87 tasks across 5 implementation phases
**Estimated Effort**: 12-16 weeks (overlapping backend/frontend/testing)
**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1 - Core Chat)

---

## Phase Structure

| Phase | Focus | Duration | User Stories |
|-------|-------|----------|--------------|
| **Phase 1** | Project Setup & Infrastructure | 1 week | N/A |
| **Phase 2** | Foundational Components (Database, LLM, Auth) | 2 weeks | N/A |
| **Phase 3** | User Story 1 - Core Chat (P1) | 3 weeks | US1 |
| **Phase 4** | User Story 2 - Voice Features (P2) | 2 weeks | US2 |
| **Phase 5** | User Story 3 - Preferences (P2) | 2 weeks | US3 |
| **Phase 6** | User Story 4 - Meal Reasoning (P3) | 1 week | US4 |
| **Phase 7** | Polish, Optimization, Deployment | 2 weeks | N/A |

---

## Dependencies & Execution Strategy

### Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1 - Core Chat) ← MUST COMPLETE BEFORE US2/US3
    ├─→ Phase 4 (US2 - Voice) [depends on US1]
    ├─→ Phase 5 (US3 - Preferences) [depends on US1]
    └─→ Phase 6 (US4 - Meal Reasoning) [depends on US1]
        ↓
Phase 7 (Polish & Deployment)
```

### Parallel Execution

**Within Phase 2** (after Phase 1):
- Backend database setup (T016-T020) can run in parallel with frontend scaffolding (T021-T025)

**Within Phase 3** (after Phase 2):
- Backend chat service development (T026-T032) can run in parallel with frontend chat UI (T033-T038)

**Within Phase 4** (after Phase 3):
- Voice service backend (T039-T043) can run in parallel with voice UI components (T044-T047)

**Within Phase 5** (after Phase 3):
- Preferences backend (T048-T052) can run in parallel with preferences UI (T053-T056)

---

## User Stories (from spec.md)

### User Story 1 (P1) - Create Meal Plan via Chat
**Goal**: Users create personalized meal plans through conversational AI without forms
**Independent Test**: Start chat → provide preferences → receive meal plan matching preferences
**Acceptance**: User completes meal plan in <5 minutes via chat conversation

### User Story 2 (P2) - Voice Input for Hands-Free Planning
**Goal**: Users engage with meal planner via voice input/output
**Independent Test**: Enable voice → speak preferences → receive audio feedback with meal plan
**Acceptance**: Voice transcription ≥90% accuracy, audio output plays correctly

### User Story 3 (P2) - Save & Manage Preferences
**Goal**: Users save dietary preferences and have them auto-referenced in future sessions
**Independent Test**: Save preferences → create new session → verify preferences auto-loaded
**Acceptance**: Saved preferences appear in next chat, can be modified anytime

### User Story 4 (P3) - View Meal Reasoning
**Goal**: Users understand why specific meals were chosen
**Independent Test**: Generate meal plan → request explanation → receive AI reasoning
**Acceptance**: Each meal has explanation available, alternatives provided on request

---

## PHASE 1: Project Setup & Infrastructure (Week 1)

**Goal**: Initialize project structure, set up databases, configure deployment pipelines
**Duration**: 1 week
**Completion Criteria**: Database running, backend/frontend scaffolding complete, deployment ready

---

### Database & Migration Setup

- [ ] T001 Create migration scripts for chat_sessions, chat_messages tables in backend/migrations
- [ ] T002 Create migration scripts for user_preferences table in backend/migrations
- [ ] T003 Create migration scripts for meal_plans, meal_plan_items tables in backend/migrations
- [ ] T004 Create migration scripts for voice_recordings, audio_cache tables in backend/migrations
- [ ] T005 [P] Create migration for extending users table with GDPR fields in backend/migrations
- [ ] T006 [P] Create migration for extending recipes table with dietary metadata in backend/migrations
- [ ] T007 Create database indexes for all tables (performance optimization) in backend/migrations
- [ ] T008 Run migrations locally and verify all tables created successfully

### Backend Project Scaffolding

- [ ] T009 Create base project structure: backend/app/{api,models,services,schemas} directories
- [ ] T010 [P] Initialize FastAPI main.py with middleware, error handlers, CORS in backend/app/main.py
- [ ] T011 Create database connection pool and SQLAlchemy session management in backend/app/database.py
- [ ] T012 [P] Set up Redis client for caching and session management in backend/app/redis_client.py
- [ ] T013 Create environment configuration module (secrets, API keys) in backend/app/config.py
- [ ] T014 Initialize logging configuration for all services in backend/app/logging.py

### Frontend Project Scaffolding

- [ ] T015 [P] Create Next.js 14 project structure with TypeScript in frontend/
- [ ] T016 [P] Set up Tailwind CSS and component library structure in frontend/src/styles
- [ ] T017 Create API client base class for REST endpoints in frontend/src/services/api-client.ts
- [ ] T018 Set up React Query configuration for data fetching in frontend/src/hooks/useQuery.ts
- [ ] T019 [P] Create authentication context and hooks in frontend/src/context/auth.ts
- [ ] T020 [P] Set up error boundary and error handling utilities in frontend/src/utils/error-handler.ts

### Deployment & CI/CD

- [ ] T021 Configure Railway deployment for backend with environment variables
- [ ] T022 [P] Configure Vercel deployment for frontend with build scripts
- [ ] T023 Set up GitHub Actions for running tests on PR (test.yml workflow)
- [ ] T024 [P] Set up GitHub Actions for deploying to production (deploy.yml workflow)
- [ ] T025 Create .env.example files with required variables (backend/.env.example, frontend/.env.example)

**Phase 1 Complete**: Database, backend/frontend scaffolding, CI/CD pipelines ready

---

## PHASE 2: Foundational Components (Weeks 2-3)

**Goal**: Implement shared infrastructure that all user stories depend on
**Duration**: 2 weeks
**Completion Criteria**: LLM integration working, authentication enforced, models defined, caching operational

**Dependencies**: MUST complete Phase 1 first

---

### Database Models (SQLAlchemy)

- [ ] T026 Create User model extending existing auth in backend/app/models/user.py
- [ ] T027 Create UserPreference model with dietary restrictions, allergies in backend/app/models/user_preference.py
- [ ] T028 Create ChatSession model with status transitions in backend/app/models/chat_session.py
- [ ] T029 Create ChatMessage model with intent detection fields in backend/app/models/chat_message.py
- [ ] T030 Create MealPlan model with allergen validation in backend/app/models/meal_plan.py
- [ ] T031 [P] Create MealPlanItem model with recipe relationships in backend/app/models/meal_plan_item.py
- [ ] T032 [P] Create VoiceRecording model with TTL fields in backend/app/models/voice_recording.py
- [ ] T033 [P] Create AudioCache model for TTS caching in backend/app/models/audio_cache.py
- [ ] T034 Write unit tests for all models in backend/tests/unit/test_models.py

### LLM Integration (Claude API)

- [ ] T035 Create LLM client wrapper for Claude API in backend/app/services/llm_client.py
- [ ] T036 Implement prompt templates for meal planning in backend/app/prompts/meal_planner_prompts.py
- [ ] T037 Implement intent detection prompt in backend/app/prompts/intent_detection_prompts.py
- [ ] T038 Implement preference extraction prompt in backend/app/prompts/preference_extraction_prompts.py
- [ ] T039 Create cost tracking module for token usage in backend/app/services/cost_tracker.py
- [ ] T040 Create rate limiting decorator for LLM calls in backend/app/middleware/rate_limiter.py
- [ ] T041 Write unit tests for LLM integration in backend/tests/unit/test_llm_client.py

### Authentication & Authorization

- [ ] T042 Create JWT token validation middleware in backend/app/middleware/auth.py
- [ ] T043 [P] Create user_id extraction from JWT in request dependencies in backend/app/dependencies.py
- [ ] T044 [P] Apply auth middleware to all protected endpoints (will be enforced in route handlers)
- [ ] T045 Create GDPR compliance middleware for data deletion requests in backend/app/middleware/gdpr.py
- [ ] T046 Write tests for authentication flows in backend/tests/unit/test_auth.py

### Caching & Session Management

- [ ] T047 Implement Redis-backed session caching in backend/app/services/session_cache.py
- [ ] T048 Create cache invalidation strategies (TTL, explicit invalidation) in backend/app/services/cache_invalidator.py
- [ ] T049 Implement preference cache with 24-hour TTL in backend/app/services/preference_cache.py
- [ ] T050 Create audio cache management service in backend/app/services/audio_cache_service.py
- [ ] T051 Write tests for caching layer in backend/tests/unit/test_cache.py

### Validation & Error Handling

- [ ] T052 Create Pydantic schemas for request/response validation in backend/app/schemas/
- [ ] T053 Create global exception handlers for API errors in backend/app/exceptions.py
- [ ] T054 Create allergen validation utility functions in backend/app/utils/allergen_validator.py
- [ ] T055 [P] Create dietary restriction validation in backend/app/utils/dietary_validator.py
- [ ] T056 Create preference conflict detection logic in backend/app/utils/preference_conflict_detector.py
- [ ] T057 Write unit tests for validation utilities in backend/tests/unit/test_validation.py

### API Contract Enforcement

- [ ] T058 Generate FastAPI server stubs from chat-api.openapi.yaml using openapi-generator
- [ ] T059 [P] Generate FastAPI server stubs from preferences-api.openapi.yaml
- [ ] T060 [P] Generate FastAPI server stubs from voice-api.openapi.yaml
- [ ] T061 [P] Generate FastAPI server stubs from meal-plan-api.openapi.yaml
- [ ] T062 Configure Swagger UI documentation from OpenAPI specs in backend/app/main.py

### Frontend Base Components

- [ ] T063 Create layout components (Header, Sidebar, Footer) in frontend/src/components/layout/
- [ ] T064 [P] Create form components (Input, Select, Checkbox, Button) in frontend/src/components/forms/
- [ ] T065 [P] Create utility components (Modal, Loading, Error) in frontend/src/components/common/
- [ ] T066 Create pages scaffolding (chat page, preferences page, history page) in frontend/src/pages/
- [ ] T067 Write unit tests for layout and utility components in frontend/tests/unit/

**Phase 2 Complete**: Models defined, LLM integrated, auth working, caching operational, API stubs generated

---

## PHASE 3: User Story 1 - Create Meal Plan via Chat (P1) (Weeks 4-6)

**Goal**: Implement core chat interface where users describe preferences and receive personalized meal plans
**Duration**: 3 weeks
**Independent Test**: User can start chat → provide preferences → receive meal plan < 5 minutes
**Acceptance Criteria**:
- User completes meal plan generation through chat in <5 minutes
- 80% of users provide sufficient information on first chat
- Generated meal plans match stated preferences

**Dependencies**: MUST complete Phase 2 first

---

### Backend: Chat Session & Message Management

- [ ] T068 [US1] Implement createChatSession endpoint in backend/app/api/v1/chat.py
- [ ] T069 [US1] Implement listChatSessions endpoint in backend/app/api/v1/chat.py
- [ ] T070 [US1] Implement getChatSession endpoint in backend/app/api/v1/chat.py
- [ ] T071 [US1] [P] Implement updateChatSession endpoint in backend/app/api/v1/chat.py
- [ ] T072 [US1] Implement sendChatMessage endpoint in backend/app/api/v1/chat.py
- [ ] T073 [US1] Implement getChatHistory endpoint in backend/app/api/v1/chat.py
- [ ] T074 [US1] [P] Implement getChatMessage endpoint in backend/app/api/v1/chat.py
- [ ] T075 [US1] [P] Implement summarizeChatSession endpoint in backend/app/api/v1/chat.py

### Backend: Chat Business Logic

- [ ] T076 [US1] Implement ChatService.create_session() in backend/app/services/chat_service.py
- [ ] T077 [US1] Implement ChatService.send_message() with LLM processing in backend/app/services/chat_service.py
- [ ] T078 [US1] Implement intent detection in ChatService in backend/app/services/chat_service.py
- [ ] T079 [US1] [P] Implement preference extraction from chat in backend/app/services/chat_service.py
- [ ] T080 [US1] Implement conversation context management in backend/app/services/chat_service.py
- [ ] T081 [US1] [P] Implement message summarization for long conversations in backend/app/services/chat_service.py
- [ ] T082 [US1] Write integration tests for chat flow in backend/tests/integration/test_chat_flow.py
- [ ] T083 [US1] Write contract tests for chat API endpoints in backend/tests/contract/test_chat_api.py

### Backend: Meal Plan Generation

- [ ] T084 [US1] Implement MealPlanService.generate_meal_plan() in backend/app/services/meal_plan_service.py
- [ ] T085 [US1] Implement allergen validation before saving in backend/app/services/meal_plan_service.py
- [ ] T086 [US1] [P] Implement dietary restriction validation in MealPlanService in backend/app/services/meal_plan_service.py
- [ ] T087 [US1] Implement meal diversity checking in backend/app/services/meal_plan_service.py
- [ ] T088 [US1] [P] Implement meal plan caching strategy in backend/app/services/meal_plan_service.py
- [ ] T089 [US1] Write unit tests for MealPlanService in backend/tests/unit/test_meal_plan_service.py

### Frontend: Chat Interface UI

- [ ] T090 [US1] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
- [ ] T091 [US1] [P] Create ChatMessage component for displaying messages in frontend/src/components/chat/ChatMessage.tsx
- [ ] T092 [US1] [P] Create ChatInput component for message composition in frontend/src/components/chat/ChatInput.tsx
- [ ] T093 [US1] [P] Create MealPlanDisplay component for showing meal plans in frontend/src/components/chat/MealPlanDisplay.tsx
- [ ] T094 [US1] Create chat page layout in frontend/src/pages/chat.tsx
- [ ] T095 [US1] [P] Implement message loading and error states in ChatInterface

### Frontend: Chat Business Logic

- [ ] T096 [US1] Create useChat hook for chat operations in frontend/src/hooks/useChat.ts
- [ ] T097 [US1] Implement chatApi.createSession() in frontend/src/services/chatApi.ts
- [ ] T098 [US1] Implement chatApi.sendMessage() in frontend/src/services/chatApi.ts
- [ ] T099 [US1] Implement chatApi.getChatHistory() in frontend/src/services/chatApi.ts
- [ ] T100 [US1] [P] Implement real-time WebSocket connection for chat in frontend/src/services/websocket.ts
- [ ] T101 [US1] Create WebSocket message handling logic in frontend/src/services/websocket-handler.ts

### Frontend: Meal Plan UI

- [ ] T102 [US1] Create MealPlanItem component for individual meals in frontend/src/components/meal-plan/MealPlanItem.tsx
- [ ] T103 [US1] [P] Implement meal plan save functionality in frontend/src/components/meal-plan/SavePlanButton.tsx
- [ ] T104 [US1] Create meal approval/rejection UI in frontend/src/components/meal-plan/ApprovalButtons.tsx
- [ ] T105 [US1] [P] Implement allergen compliance display in frontend/src/components/meal-plan/AllergenWarnings.tsx

### E2E Tests for US1

- [ ] T106 [US1] Write E2E test: Create chat session in tests/e2e/chat-flow.spec.ts
- [ ] T107 [US1] [P] Write E2E test: Send message and receive AI response in tests/e2e/chat-flow.spec.ts
- [ ] T108 [US1] [P] Write E2E test: Generate meal plan from chat in tests/e2e/chat-flow.spec.ts
- [ ] T109 [US1] Write E2E test: Verify meal plan matches preferences in tests/e2e/chat-flow.spec.ts
- [ ] T110 [US1] [P] Write E2E test: Time meal plan generation (should be <5 min) in tests/e2e/chat-flow.spec.ts

**Phase 3 Complete**: Core chat working, meal plan generation functional, E2E tests passing for US1

---

## PHASE 4: User Story 2 - Voice Input for Hands-Free Planning (P2) (Weeks 7-8)

**Goal**: Enable users to speak preferences and receive audio feedback
**Duration**: 2 weeks
**Independent Test**: Enable voice → speak preferences → receive transcription and audio response
**Acceptance Criteria**:
- Voice transcription ≥90% accuracy
- Voice output plays correctly for meal plans
- 40% of users use voice feature within first month

**Dependencies**: MUST complete Phase 3 (US1) first

---

### Backend: Speech-to-Text Service

- [ ] T111 [US2] Create VoiceService for speech-to-text in backend/app/services/voice_service.py
- [ ] T112 [US2] Implement Deepgram integration for STT in backend/app/services/voice_service.py
- [ ] T113 [US2] [P] Implement Web Speech API fallback in backend/app/services/voice_service.py
- [ ] T114 [US2] Implement confidence score extraction and validation in backend/app/services/voice_service.py
- [ ] T115 [US2] [P] Implement voice recording storage (24-hour TTL) in backend/app/services/voice_service.py
- [ ] T116 [US2] Implement cost tracking for voice API calls in backend/app/services/voice_service.py
- [ ] T117 [US2] Implement transcribeAudio endpoint in backend/app/api/v1/voice.py
- [ ] T118 [US2] Write unit tests for voice service in backend/tests/unit/test_voice_service.py

### Backend: Text-to-Speech Service

- [ ] T119 [US2] Create TextToSpeechService in backend/app/services/tts_service.py
- [ ] T120 [US2] Implement Azure Neural TTS integration in backend/app/services/tts_service.py
- [ ] T121 [US2] [P] Implement ElevenLabs fallback option in backend/app/services/tts_service.py
- [ ] T122 [US2] Implement audio caching with SHA256 hashing in backend/app/services/tts_service.py
- [ ] T123 [US2] [P] Implement LRU eviction policy for audio cache in backend/app/services/tts_service.py
- [ ] T124 [US2] Implement cost optimization for frequently synthesized text in backend/app/services/tts_service.py
- [ ] T125 [US2] Implement synthesizeAudio endpoint in backend/app/api/v1/voice.py
- [ ] T126 [US2] Write unit tests for TTS service in backend/tests/unit/test_tts_service.py

### Backend: Voice API Endpoints

- [ ] T127 [US2] Implement getVoiceRecording endpoint in backend/app/api/v1/voice.py
- [ ] T128 [US2] [P] Implement deleteVoiceRecording endpoint (GDPR) in backend/app/api/v1/voice.py
- [ ] T129 [US2] Implement voiceHealth endpoint in backend/app/api/v1/voice.py
- [ ] T130 [US2] [P] Write contract tests for voice API in backend/tests/contract/test_voice_api.py

### Frontend: Voice Input Component

- [ ] T131 [US2] Create VoiceInput component with microphone access in frontend/src/components/chat/VoiceInput.tsx
- [ ] T132 [US2] [P] Implement Web Audio API for recording in frontend/src/services/audio-recorder.ts
- [ ] T133 [US2] [P] Implement listening indicator (visual feedback) in frontend/src/components/chat/ListeningIndicator.tsx
- [ ] T134 [US2] Implement audio file upload to backend in frontend/src/services/voiceApi.ts
- [ ] T135 [US2] [P] Create fallback to text input if microphone unavailable in frontend/src/components/chat/VoiceInputFallback.tsx
- [ ] T136 [US2] Implement error handling for failed transcription in frontend/src/components/chat/VoiceErrorHandler.tsx

### Frontend: Voice Output Component

- [ ] T137 [US2] Create VoiceOutput component for playing audio in frontend/src/components/chat/VoiceOutput.tsx
- [ ] T138 [US2] [P] Implement audio player UI (play/pause/progress) in frontend/src/components/meal-plan/AudioPlayer.tsx
- [ ] T139 [US2] Implement meal plan audio generation request in frontend/src/services/voiceApi.ts
- [ ] T140 [US2] [P] Create useVoice hook for voice operations in frontend/src/hooks/useVoice.ts

### Frontend: Voice Integration

- [ ] T141 [US2] Integrate VoiceInput into ChatInput component in frontend/src/components/chat/ChatInput.tsx
- [ ] T142 [US2] [P] Integrate VoiceOutput into MealPlanDisplay in frontend/src/components/meal-plan/MealPlanDisplay.tsx
- [ ] T143 [US2] Implement voice permission request and error handling in frontend/src/hooks/useVoicePermissions.ts
- [ ] T144 [US2] [P] Add voice toggle setting in user preferences UI in frontend/src/components/settings/VoiceSettings.tsx

### E2E Tests for US2

- [ ] T145 [US2] Write E2E test: Record voice input and transcribe in tests/e2e/voice-flow.spec.ts
- [ ] T146 [US2] [P] Write E2E test: Verify transcription accuracy in tests/e2e/voice-flow.spec.ts
- [ ] T147 [US2] Write E2E test: Generate and play audio response in tests/e2e/voice-flow.spec.ts
- [ ] T148 [US2] [P] Write E2E test: Fall back to text if voice unavailable in tests/e2e/voice-flow.spec.ts

**Phase 4 Complete**: Voice input/output working, transcription ≥90%, audio caching operational, E2E tests passing for US2

---

## PHASE 5: User Story 3 - Save & Manage Preferences (P2) (Weeks 9-10)

**Goal**: Allow users to save dietary preferences and have them auto-referenced in future sessions
**Duration**: 2 weeks
**Independent Test**: Save preferences → create new session → verify preferences auto-loaded and referenced
**Acceptance Criteria**:
- 60% of users save preferences after first successful plan
- Saved preferences appear in next chat session
- Preferences can be modified anytime

**Dependencies**: MUST complete Phase 3 (US1) first

---

### Backend: User Preferences Management

- [ ] T149 [US3] Implement getUserPreferences endpoint in backend/app/api/v1/preferences.py
- [ ] T150 [US3] Implement saveUserPreferences endpoint in backend/app/api/v1/preferences.py
- [ ] T151 [US3] [P] Implement updateUserPreferences (PATCH) endpoint in backend/app/api/v1/preferences.py
- [ ] T152 [US3] Implement deleteUserPreferences endpoint (GDPR) in backend/app/api/v1/preferences.py
- [ ] T153 [US3] [P] Implement validatePreferences endpoint in backend/app/api/v1/preferences.py
- [ ] T154 [US3] Implement getAllergenList endpoint in backend/app/api/v1/preferences.py
- [ ] T155 [US3] [P] Implement getDietaryRestrictionsList endpoint in backend/app/api/v1/preferences.py
- [ ] T156 [US3] [P] Implement getCuisineList endpoint in backend/app/api/v1/preferences.py

### Backend: Preference Business Logic

- [ ] T157 [US3] Create PreferenceService in backend/app/services/preference_service.py
- [ ] T158 [US3] Implement PreferenceService.get_user_preferences() in backend/app/services/preference_service.py
- [ ] T159 [US3] [P] Implement PreferenceService.save_preferences() in backend/app/services/preference_service.py
- [ ] T160 [US3] [P] Implement PreferenceService.update_preferences() in backend/app/services/preference_service.py
- [ ] T161 [US3] Implement conflict detection for conflicting preferences in backend/app/services/preference_service.py
- [ ] T162 [US3] Implement allergen severity validation in backend/app/services/preference_service.py
- [ ] T163 [US3] [P] Implement cache invalidation on preference update in backend/app/services/preference_service.py
- [ ] T164 [US3] Implement auto-loading preferences in ChatService.create_session() in backend/app/services/chat_service.py
- [ ] T165 [US3] Write unit tests for PreferenceService in backend/tests/unit/test_preference_service.py
- [ ] T166 [US3] [P] Write contract tests for preferences API in backend/tests/contract/test_preferences_api.py

### Backend: GDPR Compliance

- [ ] T167 [US3] Implement deleteUserPreferences with cascade to chat/plans in backend/app/services/preference_service.py
- [ ] T168 [US3] [P] Implement deletion audit trail logging in backend/app/services/preference_service.py
- [ ] T169 [US3] Create GDPR compliance report generator in backend/app/services/gdpr_service.py
- [ ] T170 [US3] [P] Write tests for GDPR deletion workflows in backend/tests/unit/test_gdpr_service.py

### Frontend: Preference Management UI

- [ ] T171 [US3] Create PreferenceManager component in frontend/src/components/preferences/PreferenceManager.tsx
- [ ] T172 [US3] [P] Create PreferenceForm component with all dietary/ethnological fields in frontend/src/components/preferences/PreferenceForm.tsx
- [ ] T173 [US3] [P] Create AllergySelector component with severity levels in frontend/src/components/preferences/AllergySelector.tsx
- [ ] T174 [US3] Create CuisinePreferenceSelector component in frontend/src/components/preferences/CuisinePreferenceSelector.tsx
- [ ] T175 [US3] [P] Create DietaryRestrictionSelector component in frontend/src/components/preferences/DietaryRestrictionSelector.tsx
- [ ] T176 [US3] Create PreferenceHistory component showing modification history in frontend/src/components/preferences/PreferenceHistory.tsx

### Frontend: Preference Business Logic

- [ ] T177 [US3] Create usePreferences hook in frontend/src/hooks/usePreferences.ts
- [ ] T178 [US3] Implement preferenceApi.getPreferences() in frontend/src/services/preferenceApi.ts
- [ ] T179 [US3] [P] Implement preferenceApi.savePreferences() in frontend/src/services/preferenceApi.ts
- [ ] T180 [US3] [P] Implement preferenceApi.updatePreferences() in frontend/src/services/preferenceApi.ts
- [ ] T181 [US3] Implement preferenceApi.deletePreferences() in frontend/src/services/preferenceApi.ts
- [ ] T182 [US3] [P] Implement preferenceApi.validatePreferences() in frontend/src/services/preferenceApi.ts
- [ ] T183 [US3] Create preferences page layout in frontend/src/pages/preferences.tsx

### Frontend: Preference Integration with Chat

- [ ] T184 [US3] Display saved preferences in chat context in frontend/src/components/chat/ChatInterface.tsx
- [ ] T185 [US3] [P] Show preference-matching meals with highlights in frontend/src/components/meal-plan/MealPlanDisplay.tsx
- [ ] T186 [US3] Implement preference conflict warnings in frontend/src/components/preferences/ConflictWarning.tsx
- [ ] T187 [US3] [P] Add "Save These Preferences" button after successful meal plan in frontend/src/components/meal-plan/SavePreferencesButton.tsx

### E2E Tests for US3

- [ ] T188 [US3] Write E2E test: Save preferences in tests/e2e/preference-flow.spec.ts
- [ ] T189 [US3] [P] Write E2E test: Preferences auto-loaded in new session in tests/e2e/preference-flow.spec.ts
- [ ] T190 [US3] Write E2E test: Modify preferences in tests/e2e/preference-flow.spec.ts
- [ ] T191 [US3] [P] Write E2E test: Conflict detection on preference update in tests/e2e/preference-flow.spec.ts
- [ ] T192 [US3] Write E2E test: Delete preferences (GDPR) in tests/e2e/preference-flow.spec.ts

**Phase 5 Complete**: Preferences saved/managed, auto-loaded in sessions, GDPR compliance, E2E tests passing for US3

---

## PHASE 6: User Story 4 - View Meal Reasoning (P3) (Week 11)

**Goal**: Users understand why specific meals were chosen and can request alternatives
**Duration**: 1 week
**Independent Test**: Generate meal plan → click meal → see AI reasoning → request alternative
**Acceptance Criteria**:
- Each meal has explanation available on hover/click
- AI provides reasoning for meal selection
- Alternative meals provided with similar nutritional value

**Dependencies**: MUST complete Phase 3 (US1) first

---

### Backend: Meal Reasoning Service

- [ ] T193 [US4] Implement MealExplanationService in backend/app/services/meal_explanation_service.py
- [ ] T194 [US4] Implement reasoning extraction from LLM in backend/app/services/meal_explanation_service.py
- [ ] T195 [US4] [P] Implement alternative meal suggestion logic in backend/app/services/meal_explanation_service.py
- [ ] T196 [US4] Implement nutritional equivalence calculation in backend/app/services/meal_explanation_service.py
- [ ] T197 [US4] [P] Store reasoning with each meal in meal_plan_items.ai_reasoning_why_chosen in backend/app/models/meal_plan_item.py
- [ ] T198 [US4] Implement getAlternativeMeal endpoint in backend/app/api/v1/meal_plans.py
- [ ] T199 [US4] Write unit tests for meal explanation service in backend/tests/unit/test_meal_explanation_service.py

### Frontend: Meal Explanation UI

- [ ] T200 [US4] Create MealExplanation component in frontend/src/components/meal-plan/MealExplanation.tsx
- [ ] T201 [US4] [P] Implement explanation modal/tooltip on meal hover/click in frontend/src/components/meal-plan/MealExplanationModal.tsx
- [ ] T202 [US4] Create ReasoningDisplay component for showing AI reasoning in frontend/src/components/meal-plan/ReasoningDisplay.tsx
- [ ] T203 [US4] [P] Create AlternativeMealButton component in frontend/src/components/meal-plan/AlternativeMealButton.tsx
- [ ] T204 [US4] Implement meal swap UI (remove meal, add alternative) in frontend/src/components/meal-plan/MealSwapUI.tsx

### Frontend: Meal Reasoning Integration

- [ ] T205 [US4] Create useMealExplanation hook in frontend/src/hooks/useMealExplanation.ts
- [ ] T206 [US4] [P] Implement mealPlanApi.getAlternativeMeal() in frontend/src/services/mealPlanApi.ts
- [ ] T207 [US4] Integrate MealExplanation into MealPlanDisplay in frontend/src/components/meal-plan/MealPlanDisplay.tsx
- [ ] T208 [US4] [P] Implement meal swap/update functionality in frontend/src/services/mealPlanApi.ts

### E2E Tests for US4

- [ ] T209 [US4] Write E2E test: View meal explanation in tests/e2e/meal-reasoning.spec.ts
- [ ] T210 [US4] [P] Write E2E test: Request alternative meal in tests/e2e/meal-reasoning.spec.ts
- [ ] T211 [US4] Write E2E test: Swap meal in plan in tests/e2e/meal-reasoning.spec.ts
- [ ] T212 [US4] [P] Write E2E test: Verify alternative has similar nutritional value in tests/e2e/meal-reasoning.spec.ts

**Phase 6 Complete**: Meal reasoning implemented, alternatives available, E2E tests passing for US4

---

## Summary

### Task Statistics

| Phase | Duration | Task Count | Focus |
|-------|----------|-----------|-------|
| Phase 1 | Week 1 | T001-T025 (25 tasks) | Setup & Infrastructure |
| Phase 2 | Weeks 2-3 | T026-T067 (42 tasks) | Foundational Components |
| Phase 3 | Weeks 4-6 | T068-T110 (43 tasks) | User Story 1 (P1) - Chat |
| Phase 4 | Weeks 7-8 | T111-T148 (38 tasks) | User Story 2 (P2) - Voice |
| Phase 5 | Weeks 9-10 | T149-T192 (44 tasks) | User Story 3 (P2) - Preferences |
| Phase 6 | Week 11 | T193-T212 (20 tasks) | User Story 4 (P3) - Reasoning |
| **TOTAL** | **11 weeks** | **212 tasks** | **All Features** |

### MVP Scope (Weeks 1-6)

**Minimum Viable Product includes**:
- Phase 1: All setup tasks (T001-T025)
- Phase 2: All foundational tasks (T026-T067)
- Phase 3: All US1 tasks (T068-T110)

This delivers the core value: **Users can create personalized meal plans via conversational AI in <5 minutes without forms**.

Phases 4-6 are post-MVP enhancements:
- Phase 4: Voice input/output
- Phase 5: Preference persistence
- Phase 6: Meal reasoning transparency

### Getting Started

1. **Start Phase 1**: Clone repo, run `T001-T025` (setup)
2. **After Phase 1**: Run `T026-T067` in parallel with Phase 2 tasks
3. **After Phase 2**: Start Phase 3 with your team (can parallelize T068-T110 with frontend/backend split)
4. **Track Progress**: Mark tasks complete as you go, use todo list or project board

Each task is specific enough for an LLM or developer to execute independently without additional context.

---

**Status**: ✅ Generated - Ready for Execution

**Generated**: 2025-11-19
**Next Step**: Begin Phase 1 implementation
