# Phase 1: Data Model & Database Schema

**Feature**: 003-ai-meal-planner-chat
**Date**: 2025-11-18
**Status**: Design Phase 1 Complete
**Based on**: spec.md, research.md, plan.md

---

## Overview

This document defines the complete data model for the AI Meal Planner Chat Assistant, including database schema, entity relationships, validation rules, and state transitions. The model is designed to support:

- Unlimited concurrent users with horizontal scaling
- Persistent chat history and meal plan storage
- User preference management with dietary compliance
- Real-time WebSocket communication with stateless architecture
- Multi-tier caching strategy (Redis hot, PostgreSQL warm, S3 cold)

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────┐
│ Core Entities                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐                                       │
│  │ User             │                                       │
│  ├──────────────────┤                                       │
│  │ id (PK)          │                                       │
│  │ email            │                                       │
│  │ created_at       │                                       │
│  │ preferences_id   │──┐                                    │
│  └──────────────────┘  │                                    │
│         ▲              │                                    │
│         │              │                                    │
│    ┌────┴──────────────┴────────────────────┐              │
│    │                                         │              │
│  ┌─┴──────────────────┐    ┌────────────────┴─────────┐   │
│  │ ChatSession        │    │ UserPreference           │   │
│  ├────────────────────┤    ├──────────────────────────┤   │
│  │ id (PK)            │    │ id (PK)                  │   │
│  │ user_id (FK)       │    │ user_id (FK, unique)     │   │
│  │ created_at         │    │ allergies[]              │   │
│  │ updated_at         │    │ dietary_restrictions[]   │   │
│  │ is_active          │    │ cuisine_preferences[]    │   │
│  │ context_summary    │    │ cooking_skill           │   │
│  │ total_messages     │    │ household_size          │   │
│  └────────────┬───────┘    │ max_prep_time_minutes   │   │
│               │            │ equipment[]             │   │
│               │ 1:N        │ updated_at              │   │
│               │            │ version                 │   │
│               │            └──────────────────────────┘   │
│               │                                            │
│  ┌────────────┴──────────────┐                            │
│  │ ChatMessage                │                            │
│  ├────────────────────────────┤                            │
│  │ id (PK)                    │                            │
│  │ session_id (FK)            │                            │
│  │ sender (enum)              │                            │
│  │ role (user/assistant)      │                            │
│  │ content (text)             │                            │
│  │ tokens_used                │                            │
│  │ timestamp                  │                            │
│  │ intent_detected (optional) │                            │
│  │ metadata (JSON)            │                            │
│  └────────────────────────────┘                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ MealPlan                                             │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ id (PK)                                              │ │
│  │ user_id (FK)                                         │ │
│  │ session_id (FK)                                      │ │
│  │ created_at                                           │ │
│  │ total_prep_time_minutes                              │ │
│  │ cuisine_distribution (JSON)                          │ │
│  │ preferences_applied (JSON)                           │ │
│  │ generation_cost_tokens                               │ │
│  │ is_saved                                             │ │
│  └──────────────────────────┬───────────────────────────┘ │
│                             │ 1:N                         │
│  ┌──────────────────────────┴───────────────────────┐     │
│  │ MealPlanItem                                      │     │
│  ├───────────────────────────────────────────────────┤     │
│  │ id (PK)                                           │     │
│  │ meal_plan_id (FK)                                 │     │
│  │ recipe_id (FK)                                    │     │
│  │ meal_type (breakfast/lunch/dinner/snack)          │     │
│  │ date (serving date)                               │     │
│  │ portion_size                                      │     │
│  │ dietary_notes (why chosen)                        │     │
│  │ order_in_day                                      │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Recipe (Existing - Extended)                         │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ id (PK)                                              │ │
│  │ name                                                 │ │
│  │ cuisine_type                                         │ │
│  │ prep_time_minutes                                    │ │
│  │ cooking_time_minutes                                 │ │
│  │ servings                                             │ │
│  │ ingredients[] (with allergen tags)                   │ │
│  │ allergen_flags (bitset for 200+ allergens)           │ │
│  │ dietary_tags[] (vegan, keto, low-carb, etc)          │ │
│  │ equipment_required[] (oven, blender, etc)            │ │
│  │ difficulty_level (1-5)                               │ │
│  │ nutrition (JSON: calories, protein, carbs, fat)      │ │
│  │ vector_embedding (for semantic search)               │ │
│  │ updated_at                                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Voice & Cache Entities                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────┐                 │
│  │ VoiceRecording                       │                 │
│  ├──────────────────────────────────────┤                 │
│  │ id (PK)                              │                 │
│  │ session_id (FK)                      │                 │
│  │ audio_data_url (S3 or CDN path)      │                 │
│  │ duration_seconds                     │                 │
│  │ transcription (text)                 │                 │
│  │ confidence_score (0-1)               │                 │
│  │ provider (web_speech/deepgram/azure) │                 │
│  │ created_at                           │                 │
│  │ ttl_days (auto-delete after N days)  │                 │
│  └──────────────────────────────────────┘                 │
│                                                             │
│  ┌──────────────────────────────────────┐                 │
│  │ AudioCache                           │                 │
│  ├──────────────────────────────────────┤                 │
│  │ id (PK)                              │                 │
│  │ recipe_id (FK)                       │                 │
│  │ text_hash (SHA256)                   │                 │
│  │ audio_url (S3/CDN)                   │                 │
│  │ duration_seconds                     │                 │
│  │ provider (azure_tts)                 │                 │
│  │ hit_count                            │                 │
│  │ created_at                           │                 │
│  │ expires_at                           │                 │
│  └──────────────────────────────────────┘                 │
│                                                             │
│  ┌──────────────────────────────────────┐                 │
│  │ SessionCache (Redis-backed)          │                 │
│  ├──────────────────────────────────────┤                 │
│  │ id (PK)                              │                 │
│  │ session_id (FK)                      │                 │
│  │ recent_messages (JSON)               │                 │
│  │ context_summary (text)               │                 │
│  │ user_profile_hash                    │                 │
│  │ embedding_cache (JSON)               │                 │
│  │ ttl_seconds                          │                 │
│  │ created_at                           │                 │
│  │ last_accessed_at                     │                 │
│  └──────────────────────────────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### 1. User

**Purpose**: Core user identity linked to existing authentication system

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  auth_provider VARCHAR(50) NOT NULL DEFAULT 'internal', -- oauth/internal
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  last_login_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,

  -- Foreign key to preferences
  preferences_id UUID,

  -- GDPR tracking
  gdpr_consent_given_at TIMESTAMP,
  deletion_requested_at TIMESTAMP,

  CONSTRAINT check_email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**Validation Rules**:
- Email must be valid RFC 5322 format
- Cannot be updated after creation
- Deletion cascades to all related data (chats, preferences, meal plans)

---

### 2. UserPreference

**Purpose**: Store persistent user dietary and ethnological preferences

```sql
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

  -- Dietary restrictions (array of enum values)
  dietary_restrictions TEXT[] DEFAULT '{}',
    -- Examples: 'vegan', 'vegetarian', 'keto', 'low-carb', 'gluten-free', 'kosher', 'halal'

  -- Allergies (stored as JSON for extensibility)
  allergies JSONB DEFAULT '[]',
    -- Example: [{"allergen": "peanut", "severity": "severe"}, {"allergen": "shellfish", "severity": "mild"}]

  -- Cuisine preferences (array of enum values)
  cuisine_preferences TEXT[] DEFAULT '{}',
    -- Examples: 'mediterranean', 'asian', 'latin_american', 'indian', 'middle_eastern', 'european'

  -- Cooking skill level
  cooking_skill VARCHAR(20) DEFAULT 'intermediate',
    -- Enum: 'beginner', 'intermediate', 'advanced'

  -- Household composition
  household_size INT DEFAULT 1 CHECK (household_size > 0 AND household_size <= 20),
  household_types TEXT[] DEFAULT '{}',
    -- Examples: 'infant', 'child', 'teen', 'adult', 'senior'

  -- Time availability
  max_prep_time_minutes INT DEFAULT 60 CHECK (max_prep_time_minutes > 0),
  max_cooking_time_minutes INT DEFAULT 90 CHECK (max_cooking_time_minutes > 0),

  -- Equipment available
  equipment_available TEXT[] DEFAULT '{}',
    -- Examples: 'oven', 'stovetop', 'microwave', 'blender', 'food_processor'

  -- Budget constraints
  budget_tier VARCHAR(20) DEFAULT 'moderate',
    -- Enum: 'budget-friendly', 'moderate', 'premium'

  -- Dietary goals
  dietary_goals TEXT[] DEFAULT '{}',
    -- Examples: 'weight_loss', 'muscle_gain', 'maintenance', 'performance'

  -- Version for optimistic locking
  version INT DEFAULT 1,

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT valid_cooking_skill CHECK (cooking_skill IN ('beginner', 'intermediate', 'advanced')),
  CONSTRAINT valid_budget_tier CHECK (budget_tier IN ('budget-friendly', 'moderate', 'premium'))
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_dietary_restrictions ON user_preferences USING GIN(dietary_restrictions);
CREATE INDEX idx_user_preferences_cuisine_preferences ON user_preferences USING GIN(cuisine_preferences);
CREATE INDEX idx_user_preferences_updated_at ON user_preferences(updated_at);
```

**Validation Rules**:
- One preference record per user (enforced by UNIQUE constraint)
- Allergies must include severity level (mild/moderate/severe)
- Dietary restrictions and cuisine preferences are pre-defined enums
- Must be validated against Recipe allergen_flags before meal plan generation
- Version field supports optimistic locking for concurrent updates

**State Transitions**:
- Created on first user signup or preference save
- Updated when user modifies any preference
- Cached in Redis with 24-hour TTL
- Invalidates all meal plan caches when updated

---

### 3. ChatSession

**Purpose**: Represent a single conversation thread with the AI meal planner

```sql
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Session state
  is_active BOOLEAN DEFAULT TRUE,
  status VARCHAR(20) DEFAULT 'active',
    -- Enum: 'active', 'paused', 'archived', 'deleted'

  -- Context tracking
  context_summary TEXT, -- LLM-generated summary for long conversations
  total_messages INT DEFAULT 0,
  total_tokens_used INT DEFAULT 0,

  -- Performance tracking
  first_message_at TIMESTAMP,
  last_message_at TIMESTAMP,
  average_response_time_ms INT,

  -- Topic detection (from intent analysis)
  primary_topic VARCHAR(100), -- 'breakfast', 'lunch', 'dinner', 'weekly_plan', 'preferences', etc
  subtopics TEXT[] DEFAULT '{}',

  -- Session metadata
  metadata JSONB DEFAULT '{}',
    -- Custom data: voice_enabled, browser_type, etc

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT valid_status CHECK (status IN ('active', 'paused', 'archived', 'deleted'))
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_is_active ON chat_sessions(is_active);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX idx_chat_sessions_last_message_at ON chat_sessions(last_message_at);
CREATE INDEX idx_chat_sessions_user_created ON chat_sessions(user_id, created_at DESC);
```

**Validation Rules**:
- `user_id` must exist in users table
- `created_at` is immutable
- `status` controls whether session appears in active list
- `total_tokens_used` is read-only (calculated from ChatMessage records)

**State Transitions**:
1. `active` (initial state when created)
2. `paused` (user closes chat without archiving)
3. `archived` (user clicks "save session")
4. `deleted` (user manually deletes session)
5. Auto-archive after 7 days of inactivity

**Caching Strategy**:
- Active sessions: Hot in Redis (5-min TTL)
- Recent messages: Redis (1-hour TTL)
- Full history: PostgreSQL (permanent)

---

### 4. ChatMessage

**Purpose**: Store individual messages in a chat session

```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,

  -- Message content
  sender VARCHAR(20) NOT NULL,
    -- Enum: 'user' or 'assistant'
  role VARCHAR(20) DEFAULT NULL, -- For future multi-assistant scenarios
  content TEXT NOT NULL,

  -- Token tracking for cost monitoring
  tokens_used INT DEFAULT 0,

  -- Intent analysis (optional)
  intent_detected VARCHAR(100),
    -- Examples: 'request_meal_plan', 'modify_preference', 'ask_clarification', 'approve_plan'
  sentiment VARCHAR(20),
    -- Enum: 'positive', 'neutral', 'negative'

  -- Metadata
  metadata JSONB DEFAULT '{}',
    -- voice_duration_ms, audio_confidence, etc

  -- For summarization tracking
  is_summarized BOOLEAN DEFAULT FALSE,
  summary_id UUID REFERENCES chat_messages(id), -- Pointer to summary message if this was summarized

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT valid_sender CHECK (sender IN ('user', 'assistant')),
  CONSTRAINT valid_intent CHECK (intent_detected IN (
    'request_meal_plan', 'modify_preference', 'ask_clarification', 'approve_plan',
    'reject_plan', 'request_explanation', 'save_preference', 'voice_input', NULL
  ))
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_sender ON chat_messages(sender);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);
CREATE INDEX idx_chat_messages_intent ON chat_messages(intent_detected) WHERE intent_detected IS NOT NULL;
```

**Validation Rules**:
- `session_id` must exist and be owned by authenticated user
- `sender` is immutable after creation
- `content` cannot be empty
- `tokens_used` is calculated at insertion time
- `created_at` is immutable

**Message History Limits**:
- Keep last 10 messages verbatim in context window
- Summarize messages 11-30 using LLM (1 summary call per 10 messages)
- Archive messages >30 days old to S3
- Retrieve full history on demand (cold storage)

---

### 5. MealPlan

**Purpose**: Store generated meal plans from chat sessions

```sql
CREATE TABLE meal_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,

  -- Meal plan metadata
  name VARCHAR(255) DEFAULT 'Weekly Meal Plan',
  description TEXT,

  -- Timing
  plan_start_date DATE NOT NULL,
  plan_duration_days INT DEFAULT 7 CHECK (plan_duration_days > 0 AND plan_duration_days <= 365),

  -- Aggregated metrics
  total_prep_time_minutes INT,
  total_cooking_time_minutes INT,
  total_servings INT,

  -- Preferences applied (for reference/audit)
  preferences_applied JSONB NOT NULL,
    -- Snapshot of UserPreference at generation time

  -- Cuisine distribution (for diversity tracking)
  cuisine_distribution JSONB DEFAULT '{}',
    -- Example: {"mediterranean": 3, "asian": 2, "latin": 2}

  -- Generation cost (for analytics)
  generation_cost_tokens INT,

  -- Dietary compliance validation
  passed_allergen_check BOOLEAN NOT NULL DEFAULT FALSE,
  allergen_violations TEXT[] DEFAULT '{}',
  dietary_compliance_score NUMERIC(3,2) DEFAULT 1.0 CHECK (dietary_compliance_score >= 0 AND dietary_compliance_score <= 1.0),

  -- User interaction
  is_saved BOOLEAN DEFAULT FALSE,
  saved_at TIMESTAMP,
  is_favorited BOOLEAN DEFAULT FALSE,
  user_satisfaction_score INT CHECK (user_satisfaction_score IS NULL OR (user_satisfaction_score >= 1 AND user_satisfaction_score <= 5)),
  feedback TEXT,

  -- Version tracking for modifications
  is_original BOOLEAN DEFAULT TRUE,
  parent_meal_plan_id UUID REFERENCES meal_plans(id),

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT valid_start_date CHECK (plan_start_date >= CURRENT_DATE),
  CONSTRAINT check_pass_before_save CHECK (
    (NOT is_saved) OR (passed_allergen_check = TRUE)
  )
);

CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_meal_plans_session_id ON meal_plans(session_id);
CREATE INDEX idx_meal_plans_is_saved ON meal_plans(is_saved);
CREATE INDEX idx_meal_plans_created_at ON meal_plans(created_at);
CREATE INDEX idx_meal_plans_user_created ON meal_plans(user_id, created_at DESC);
CREATE INDEX idx_meal_plans_parent ON meal_plans(parent_meal_plan_id);
```

**Validation Rules**:
- `user_id` and `session_id` must both be owned by authenticated user
- `plan_start_date` cannot be in the past
- `passed_allergen_check` MUST be TRUE before `is_saved` can be TRUE
- `preferences_applied` is a JSON snapshot (immutable after creation)
- `parent_meal_plan_id` is only set when user modifies an existing plan

**State Transitions**:
1. Created with `is_saved = FALSE`
2. User reviews and approves → `passed_allergen_check = TRUE`
3. User saves → `is_saved = TRUE`, `saved_at = NOW()`
4. User modifies (removes meal X, adds meal Y) → New MealPlan with `parent_meal_plan_id`

---

### 6. MealPlanItem

**Purpose**: Individual meal within a meal plan

```sql
CREATE TABLE meal_plan_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meal_plan_id UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
  recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE RESTRICT,

  -- Meal context
  meal_type VARCHAR(20) NOT NULL,
    -- Enum: 'breakfast', 'lunch', 'dinner', 'snack'
  serving_date DATE NOT NULL,
  order_in_day INT NOT NULL CHECK (order_in_day > 0 AND order_in_day <= 10),

  -- Portion information
  portion_size NUMERIC(5,2) NOT NULL DEFAULT 1.0 CHECK (portion_size > 0),
  portion_unit VARCHAR(50) DEFAULT 'serving',
    -- Examples: 'serving', 'cup', 'gram', 'ounce'
  servings INT NOT NULL DEFAULT 1 CHECK (servings > 0),

  -- Dietary notes (why this meal was chosen for this person)
  dietary_notes TEXT,
    -- Example: "High protein, low-carb option that fits your keto preference"

  -- AI reasoning (for explanations)
  ai_reasoning_why_chosen TEXT,
  ai_reasoning_alternatives TEXT,

  -- Substitution tracking
  is_substitution BOOLEAN DEFAULT FALSE,
  original_recipe_id UUID REFERENCES recipes(id),
  substitution_reason VARCHAR(255),

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT valid_meal_type CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
  CONSTRAINT valid_serving_date CHECK (serving_date >= CURRENT_DATE),
  CONSTRAINT check_substitution CHECK (
    (NOT is_substitution) OR (original_recipe_id IS NOT NULL)
  )
);

CREATE INDEX idx_meal_plan_items_meal_plan_id ON meal_plan_items(meal_plan_id);
CREATE INDEX idx_meal_plan_items_recipe_id ON meal_plan_items(recipe_id);
CREATE INDEX idx_meal_plan_items_meal_type ON meal_plan_items(meal_type);
CREATE INDEX idx_meal_plan_items_serving_date ON meal_plan_items(serving_date);
CREATE INDEX idx_meal_plan_items_meal_plan_serving ON meal_plan_items(meal_plan_id, serving_date, order_in_day);
```

**Validation Rules**:
- `recipe_id` must exist and not be deleted
- `serving_date` must be >= current date
- `portion_size` must be > 0 (fractional portions allowed)
- `order_in_day` must be unique per (meal_plan_id, serving_date, meal_type)

---

### 7. Recipe (Extended)

**Purpose**: Store recipe data with dietary metadata (extends existing Recipe table)

```sql
-- Extend existing recipes table
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS (
  -- Dietary tagging
  dietary_tags TEXT[] DEFAULT '{}',
    -- Examples: 'vegan', 'keto', 'low-carb', 'gluten-free', 'high-protein', 'dairy-free'

  -- Allergen tracking (bitset for efficient filtering)
  allergen_flags BIGINT DEFAULT 0,
    -- Bit positions: peanut=0, treenut=1, milk=2, egg=3, fish=4, shellfish=5, soy=6, wheat=7...
    -- Supports up to 63 allergens (use two columns for more)

  -- Ingredient structure
  ingredients_detailed JSONB NOT NULL DEFAULT '[]',
    -- Example: [
    --   {"name": "chicken breast", "amount": 2, "unit": "pieces", "allergens": ["soy_sauce"], "calories": 165},
    --   {"name": "olive oil", "amount": 1, "unit": "tbsp", "allergens": [], "calories": 120}
    -- ]

  -- Time breakdown
  prep_time_minutes INT NOT NULL,
  cooking_time_minutes INT NOT NULL,

  -- Nutritional information
  nutrition JSONB NOT NULL DEFAULT '{}',
    -- Example: {"calories": 450, "protein_g": 45, "carbs_g": 30, "fat_g": 15, "fiber_g": 5}

  -- Equipment requirements
  equipment_required TEXT[] DEFAULT '{}',
    -- Examples: 'oven', 'stovetop', 'blender', 'microwave'

  -- Difficulty level (for skill-based recommendations)
  difficulty_level INT DEFAULT 2 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),

  -- Vector embedding for semantic search
  embedding VECTOR(1536) DEFAULT NULL, -- OpenAI text-embedding-3-small dimension

  -- Sourcing metadata
  cuisine_type VARCHAR(50) NOT NULL,
  source_url TEXT,

  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recipes_dietary_tags ON recipes USING GIN(dietary_tags);
CREATE INDEX idx_recipes_allergen_flags ON recipes(allergen_flags);
CREATE INDEX idx_recipes_difficulty_level ON recipes(difficulty_level);
CREATE INDEX idx_recipes_cuisine_type ON recipes(cuisine_type);
CREATE INDEX idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops);
```

**Validation Rules**:
- `allergen_flags` is a bitmask (immutable after creation, set during recipe import)
- `ingredients_detailed` must include all allergen information
- `prep_time_minutes` + `cooking_time_minutes` must equal or exceed `cook_time_minutes`
- `embedding` is generated once on recipe creation, never updated
- All ingredients must be present in ingredients_detailed

**Allergen Bitmask Reference**:
```
Bit 0-7:    Common allergens (peanut, treenut, milk, egg, fish, shellfish, soy, wheat)
Bit 8-15:   Secondary allergens (sesame, mustard, celery, lupin, mollusks, etc)
Bit 16-23:  Thresholds & processing (may contain, cross-contact, processed in facility)
Bit 24+:    Reserved for future allergen tracking
```

---

### 8. VoiceRecording

**Purpose**: Track voice input recordings (temporary, auto-deleted)

```sql
CREATE TABLE voice_recordings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,

  -- Audio metadata
  audio_data_url TEXT NOT NULL, -- S3 or Deepgram storage path
  duration_seconds INT NOT NULL CHECK (duration_seconds > 0 AND duration_seconds <= 600),

  -- Transcription
  transcription TEXT NOT NULL,
  confidence_score NUMERIC(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),

  -- Provider information (for debugging)
  provider VARCHAR(50) NOT NULL,
    -- Enum: 'web_speech_api', 'deepgram', 'azure'
  raw_response JSONB DEFAULT NULL, -- Debug: Store raw API response

  -- GDPR tracking
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL, -- Auto-delete after this date

  CONSTRAINT valid_provider CHECK (provider IN ('web_speech_api', 'deepgram', 'azure')),
  CONSTRAINT expires_in_future CHECK (expires_at > created_at)
);

CREATE INDEX idx_voice_recordings_session_id ON voice_recordings(session_id);
CREATE INDEX idx_voice_recordings_expires_at ON voice_recordings(expires_at);

-- Auto-delete expired recordings
CREATE OR REPLACE FUNCTION delete_expired_voice_recordings()
RETURNS void AS $$
BEGIN
  DELETE FROM voice_recordings WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;
```

**Validation Rules**:
- `duration_seconds` must be 1-600 seconds (max 10 minutes)
- `confidence_score` must be 0.0-1.0
- `expires_at` must be in the future (typically 24 hours from creation)
- Audio data is NOT stored in database (only URL/path)
- Raw API response is optional, for debugging only

**Caching Strategy**:
- Voice recordings are temporary (not cached long-term)
- Hot in Redis only during active session (5-min TTL)
- Automatically deleted from S3 after `expires_at`

---

### 9. AudioCache

**Purpose**: Cache text-to-speech output for cost optimization

```sql
CREATE TABLE audio_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Key for cache lookup
  text_hash CHAR(64) NOT NULL UNIQUE, -- SHA256 of text being synthesized
  recipe_id UUID REFERENCES recipes(id),

  -- Audio metadata
  audio_url TEXT NOT NULL, -- S3/CDN path to cached MP3
  duration_seconds INT NOT NULL,
  audio_format VARCHAR(10) DEFAULT 'mp3',

  -- TTS provider
  provider VARCHAR(50) NOT NULL,
    -- Enum: 'azure_neural_tts', 'elevenlabs', 'google_cloud'
  voice_id VARCHAR(100),

  -- Cache statistics
  hit_count INT DEFAULT 0,
  last_accessed_at TIMESTAMP,

  -- Lifecycle
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL, -- 30-day TTL

  CONSTRAINT valid_provider CHECK (provider IN ('azure_neural_tts', 'elevenlabs', 'google_cloud'))
);

CREATE INDEX idx_audio_cache_text_hash ON audio_cache(text_hash);
CREATE INDEX idx_audio_cache_recipe_id ON audio_cache(recipe_id);
CREATE INDEX idx_audio_cache_expires_at ON audio_cache(expires_at);

-- Update hit count and last_accessed_at on cache hit
CREATE OR REPLACE FUNCTION touch_audio_cache(cache_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE audio_cache
  SET hit_count = hit_count + 1,
      last_accessed_at = NOW()
  WHERE id = cache_id;
END;
$$ LANGUAGE plpgsql;
```

**Validation Rules**:
- `text_hash` is immutable (calculated once at insertion)
- `hit_count` auto-increments on cache access
- `expires_at` is typically 30 days from creation
- Pre-generate audio for top 100 popular recipes

---

### 10. SessionCache (Redis-backed)

**Purpose**: High-speed session context caching (stored in Redis, not PostgreSQL)

```
Key Structure: session:{session_id}:*

Example Redis entries:
─────────────────────────────────────────

session:abc123:messages
  ├─ TTL: 1 hour
  ├─ Type: JSON Array
  └─ Value: [
       {"id": "msg1", "sender": "user", "content": "...", "tokens": 150},
       {"id": "msg2", "sender": "assistant", "content": "...", "tokens": 200}
     ]

session:abc123:context
  ├─ TTL: 5 minutes
  ├─ Type: String (JSON)
  └─ Value: {"topic": "dinner", "preferences_active": [...], "pending_action": "awaiting_user"}

session:abc123:profile_cache
  ├─ TTL: 24 hours (expires with UserPreference version)
  ├─ Type: String (JSON)
  └─ Value: {"allergies": [...], "cooking_skill": "intermediate", ...}

session:abc123:embedding_cache
  ├─ TTL: 5 minutes
  ├─ Type: String (JSON)
  └─ Value: {"user_input": "...vector...", "cached_recipes": [...]}
```

**Caching Strategy**:
- Recent messages (last 10): 1-hour TTL
- Context summary: 5-minute TTL (refreshed on each message)
- User profile: 24-hour TTL (invalidated on preference update)
- Embeddings: 5-minute TTL (invalidated on profile change)

---

## Validation Rules by Entity

### UserPreference Validation

```python
# Allergen severity validation
allergy_severity in ['mild', 'moderate', 'severe']

# Cuisine preference whitelist
cuisine_preferences ⊆ [
  'mediterranean', 'asian', 'latin_american', 'indian',
  'middle_eastern', 'european', 'african', 'american'
]

# Dietary restrictions whitelist
dietary_restrictions ⊆ [
  'vegan', 'vegetarian', 'keto', 'low_carb', 'gluten_free',
  'kosher', 'halal', 'paleo', 'whole30', 'low_fat'
]

# Time constraints
max_prep_time_minutes > 0 AND max_prep_time_minutes <= 480 (8 hours)
max_cooking_time_minutes > 0 AND max_cooking_time_minutes <= 480

# Household size
household_size >= 1 AND household_size <= 20
```

### MealPlan Validation

```python
# Allergen compliance check (MUST PASS before saving)
for meal in meal_plan.meals:
  recipe = fetch_recipe(meal.recipe_id)
  for user_allergen in user.preferences.allergies:
    assert user_allergen NOT IN recipe.allergen_flags

# Dietary restriction compliance
for meal in meal_plan.meals:
  recipe = fetch_recipe(meal.recipe_id)
  for diet_restriction in user.preferences.dietary_restrictions:
    assert diet_restriction IN recipe.dietary_tags

# Diversity check (at least 2 different cuisines in 7-day plan)
unique_cuisines = set(meal.recipe.cuisine_type for meal in meal_plan.meals)
assert len(unique_cuisines) >= 2
```

### ChatMessage Intent Detection

```python
# Intent classification (LLM-powered)
intents = {
  'request_meal_plan': 'User explicitly asks for meal plan generation',
  'modify_preference': 'User changes dietary restriction or preference',
  'ask_clarification': 'AI asks follow-up question',
  'approve_plan': 'User approves generated meal plan',
  'reject_plan': 'User rejects meal plan and asks for alternative',
  'request_explanation': 'User asks "why was this meal chosen?"',
  'save_preference': 'User explicitly saves preferences',
  'voice_input': 'Message originated from voice input'
}
```

---

## State Transitions & Lifecycle

### Chat Session Lifecycle

```
┌─────────────┐
│   Created   │  create_session(user_id)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Active    │  add_message()
├─────────────┤  (main interaction loop)
│ is_active=T │
│status=active│
└──────┬──────┘
       │ (user inactive 7 days)
       ▼
┌─────────────┐
│   Paused    │  (can resume)
├─────────────┤
│ is_active=T │
│status=paused│
└──────┬──────┘
       │ (user clicks "save")
       ▼
┌──────────────┐
│  Archived    │  (read-only)
├──────────────┤
│ is_active=T  │
│status=archive│
└──────┬───────┘
       │ (user manually deletes)
       ▼
┌──────────────┐
│   Deleted    │  (soft delete, can restore)
├──────────────┤
│ is_active=F  │
│status=deleted│
└──────────────┘
```

### Meal Plan Lifecycle

```
┌──────────────┐
│   Generated  │  generate_meal_plan()
└──────┬───────┘
       │
       ▼
┌────────────────────────────┐
│   Review (not saved)       │  User reviews
├────────────────────────────┤
│ is_saved=F                 │  AI explains meals
│ passed_allergen_check=?    │  User can request changes
└──────┬──────────────────┬──┘
       │                  │
       │ (approve)        │ (reject)
       ▼                  ▼
┌────────────────┐    ┌────────────────────┐
│  Allergen OK   │    │ Request Changes    │
├────────────────┤    ├────────────────────┤
│ passed_..=TRUE │    │ Create new plan    │
│ is_saved=F     │    │ with parent_id ref │
└──────┬─────────┘    └────────────────────┘
       │
       │ (save)
       ▼
┌────────────────┐
│    Saved       │  save_meal_plan()
├────────────────┤
│ is_saved=TRUE  │
│ saved_at=NOW() │
└────────────────┘
       │
       │ (modify)
       ▼
┌──────────────────────┐
│ Saved + Modified     │  User removes/adds meals
├──────────────────────┤
│ New MealPlan record  │
│ parent_meal_plan_id  │
└──────────────────────┘
```

---

## Database Indexes

### Performance Indexes

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Chat session queries
CREATE INDEX idx_chat_sessions_user_created ON chat_sessions(user_id, created_at DESC);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(user_id) WHERE is_active = TRUE;

-- Message retrieval (most common query)
CREATE INDEX idx_messages_session_created ON chat_messages(session_id, created_at DESC);

-- Meal plan queries
CREATE INDEX idx_meal_plans_user_created ON meal_plans(user_id, created_at DESC);
CREATE INDEX idx_meal_plans_saved ON meal_plans(user_id, is_saved) WHERE is_saved = TRUE;

-- Recipe filtering (most expensive queries)
CREATE INDEX idx_recipes_dietary_tags ON recipes USING GIN(dietary_tags);
CREATE INDEX idx_recipes_allergen_flags ON recipes(allergen_flags);
CREATE INDEX idx_recipes_cuisine_type ON recipes(cuisine_type);
CREATE INDEX idx_recipes_difficulty ON recipes(difficulty_level);

-- Vector search for semantic recipe matching
CREATE INDEX idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops);

-- Cache expiration cleanup
CREATE INDEX idx_voice_recordings_expires ON voice_recordings(expires_at);
CREATE INDEX idx_audio_cache_expires ON audio_cache(expires_at);
```

---

## Data Retention & GDPR Compliance

### Retention Policy

| Data Type | Retention | Deletion Policy |
|-----------|-----------|-----------------|
| Chat History | Indefinite | User can request full deletion |
| Meal Plans | Indefinite | Deleted with user account |
| Preferences | Indefinite | Deleted with user account |
| Voice Recordings | 24 hours | Auto-delete after TTL |
| Audio Cache | 30 days | LRU eviction based on hit count |
| User Account | Indefinite | Soft delete (retain for analytics) |

### User Deletion Workflow

```sql
-- When user requests account deletion:

1. Set users.deletion_requested_at = NOW()
2. Anonymize email (hash + random string)
3. Archive to cold storage:
   - Chat histories → S3/Analytics
   - Meal plans → S3/Analytics
   - Preferences → Retained (anonymized)
4. Delete from hot storage:
   - Redis cache entries
   - Voice recordings (expires_at = NOW())
   - Recent chat messages
5. Keep PostgreSQL records for GDPR audit trail (30-year retention)
6. Flag as deleted after 30-day grace period (allow user to restore)
```

---

## Migration Strategy

### Phase 1 Deliverables

This data model is designed to coexist with the existing recipe database:

1. **Create new tables** (ChatSession, ChatMessage, MealPlan, MealPlanItem, etc)
2. **Extend existing tables** (add columns to Users and Recipe)
3. **Create indexes** (all performance-critical paths)
4. **No data migration** required (backward compatible)

### Future Optimization

- Partition chat_messages by session_id (sharding for 1M+ messages)
- Archive old messages to S3 with Athena query support
- Vector search for recipe similarity
- Time-series database for analytics (Timescale)

---

## Summary

This data model provides:

✅ **Scalability**: Supports unlimited concurrent users with proper indexing
✅ **Compliance**: GDPR-ready with deletion workflows
✅ **Performance**: Multi-tier caching (Redis → PostgreSQL → S3)
✅ **Auditability**: Complete chat history with timestamps
✅ **Flexibility**: JSON fields for extensibility
✅ **Safety**: Constraint-based allergen validation

**Status**: Ready for Phase 1 API contract generation (Phase 2)
