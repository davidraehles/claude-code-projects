# Data Model & Database Schema

**Feature**: Multi-Agent Recipe and Meal Planning System
**Date**: 2025-11-14
**Database**: PostgreSQL 16+

---

## Overview

This document defines the core entities, relationships, and validation rules for the multi-agent recipe and meal planning system. All data is stored in PostgreSQL with row-level security for multi-tenant isolation.

---

## Core Entities

### 1. User

Represents a SaaS user with subscription and preferences.

**SQL Schema**:
```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  country VARCHAR(2) NOT NULL, -- ISO 3166-1 alpha-2 (DE, AT, CH, etc.)
  subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free', -- free, basic, premium
  subscription_expires_at TIMESTAMP,
  preferences JSONB, -- Mobile/desktop preferences, theme, etc.
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP -- Soft delete for GDPR
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_expires ON users(subscription_expires_at);
```

**TypeScript/Pydantic Schema**:
```typescript
class User {
  id: int
  email: str
  passwordHash: str (never exposed in API)
  country: str // ISO 3166-1 alpha-2
  subscriptionTier: 'free' | 'basic' | 'premium'
  subscriptionExpiresAt?: datetime
  preferences: {
    language?: str
    theme?: 'light' | 'dark'
    mobileNotifications?: bool
    dietaryPreferences?: str[] // Tags: vegetarian, vegan, gluten-free, etc.
  }
  createdAt: datetime
  updatedAt: datetime
}
```

**Row-Level Security**:
```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY select_own_user ON users FOR SELECT
  USING (id = current_user_id());
```

---

### 2. Recipe

Represents a harvested recipe with ingredients and instructions.

**SQL Schema**:
```sql
CREATE TABLE recipes (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  source_url VARCHAR(2048),
  source_type VARCHAR(50), -- 'web', 'api', 'rss', 'user_input'
  description TEXT,
  ingredients JSONB NOT NULL, -- Array of ingredient objects
  instructions JSONB NOT NULL, -- Array of instruction steps
  prep_time_minutes INT,
  cook_time_minutes INT,
  servings INT DEFAULT 4,
  dietary_tags TEXT[], -- vegetarian, vegan, gluten-free, etc.
  cuisine_tags TEXT[], -- italian, asian, mexican, etc.
  difficulty_level VARCHAR(50), -- easy, medium, hard
  nutrition_info JSONB, -- Calories, protein, fat, carbs per serving
  harvest_metadata JSONB, -- Method, timestamp, schema.org found, etc.
  is_favorite BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP -- Soft delete
);

CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_recipes_dietary_tags ON recipes USING GIN (dietary_tags);
CREATE INDEX idx_recipes_is_favorite ON recipes(user_id, is_favorite);
```

**Ingredients JSONB Structure**:
```json
[
  {
    "item": "all-purpose flour",
    "quantity": 2,
    "unit": "cups",
    "notes": "sifted",
    "normalized_item": "flour", // For matching/substitution
    "category": "grains"
  },
  {
    "item": "butter",
    "quantity": 1,
    "unit": "cup",
    "notes": "softened",
    "normalized_item": "butter",
    "category": "dairy"
  }
]
```

**Instructions JSONB Structure**:
```json
[
  {
    "step": 1,
    "text": "Preheat oven to 350°F.",
    "duration_minutes": 10
  },
  {
    "step": 2,
    "text": "Mix dry ingredients in a large bowl.",
    "duration_minutes": 5
  }
]
```

**TypeScript/Pydantic**:
```typescript
class Recipe {
  id: int
  userId: int
  title: str
  sourceUrl?: str
  sourceType: 'web' | 'api' | 'rss' | 'user_input'
  description?: str
  ingredients: Ingredient[]
  instructions: Instruction[]
  prepTimeMinutes?: int
  cookTimeMinutes?: int
  servings: int = 4
  dietaryTags: str[]
  cuisineTags: str[]
  difficultyLevel?: 'easy' | 'medium' | 'hard'
  nutritionInfo?: NutritionInfo
  harvestMetadata: {
    method: str
    harvestTimestamp: datetime
    schemaOrgFound: bool
    successRate: float
  }
  isFavorite: bool = False
  createdAt: datetime
  updatedAt: datetime
}

class Ingredient {
  item: str
  quantity: float
  unit: str // cups, grams, tbsp, etc.
  notes?: str
  normalizedItem: str
  category: str
}

class NutritionInfo {
  caloriesPerServing?: int
  proteinGrams?: float
  fatGrams?: float
  carbsGrams?: float
}
```

**Row-Level Security**:
```sql
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
CREATE POLICY select_own_recipes ON recipes FOR SELECT
  USING (user_id = current_user_id());
CREATE POLICY update_own_recipes ON recipes FOR UPDATE
  USING (user_id = current_user_id());
```

---

### 3. IngredientTaxonomy

Centralized ingredient reference for substitutions and analysis.

**SQL Schema**:
```sql
CREATE TABLE ingredient_taxonomy (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE, -- "butter"
  canonical_name VARCHAR(255), -- For alias resolution
  category VARCHAR(50) NOT NULL, -- dairy, protein, vegetables, grains, etc.
  substitutes JSONB, -- Array of substitute objects
  allergens TEXT[], -- peanuts, tree_nuts, milk, gluten, etc.
  seasonal_availability JSONB, -- { months: [1,2,3], regions: ['DE', 'AT'] }
  weight_grams_per_unit JSONB, -- { "cup": 240, "tbsp": 15, "gram": 1 }
  nutrition_info JSONB,
  aliases TEXT[], -- ["butter", "buerre", "ghee"]
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ingredient_taxonomy_category ON ingredient_taxonomy(category);
CREATE INDEX idx_ingredient_taxonomy_aliases ON ingredient_taxonomy USING GIN(aliases);
```

**Substitutes JSONB Structure**:
```json
[
  {
    "name": "coconut oil",
    "confidence": 0.95,
    "ratio": 0.75, // Use 75% of original amount
    "notes": "Higher fat content, works for baking",
    "allergens_added": [],
    "dietary_fit": ["vegan", "dairy-free"]
  },
  {
    "name": "olive oil",
    "confidence": 0.85,
    "ratio": 1.0,
    "notes": "Good for savory dishes",
    "allergens_added": [],
    "dietary_fit": ["vegan", "dairy-free"]
  }
]
```

**TypeScript/Pydantic**:
```typescript
class IngredientTaxonomy {
  id: int
  name: str
  canonicalName?: str
  category: str
  substitutes: Substitute[]
  allergens: str[]
  seasonalAvailability: {
    months: int[] // [1,2,3] for Jan-Mar
    regions: str[] // ISO country codes
  }
  weightGramsPerUnit: Record<str, float>
  nutritionInfo: NutritionInfo
  aliases: str[]
  createdAt: datetime
  updatedAt: datetime
}

class Substitute {
  name: str
  confidence: float // 0.0-1.0
  ratio: float // Adjustment factor
  notes?: str
  allergensAdded: str[]
  dietaryFit: str[]
}
```

---

### 4. MealPlan

Represents a weekly meal plan for a user.

**SQL Schema**:
```sql
CREATE TABLE meal_plans (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  meal_type VARCHAR(50) NOT NULL DEFAULT 'dinner', -- dinner, lunch, breakfast
  meals JSONB NOT NULL, -- Array of meal selections
  aggregated_ingredients JSONB, -- Deduplicated ingredient list
  constraints JSONB NOT NULL, -- User's meal planning constraints
  metrics JSONB, -- Planning metrics: reuse %, variety score, etc.
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP
);

CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_meal_plans_dates ON meal_plans(user_id, start_date, end_date);
```

**Meals JSONB Structure**:
```json
[
  {
    "date": "2025-11-18",
    "mealType": "dinner",
    "recipeId": 12345,
    "recipeName": "Vegetarian Chili",
    "servings": 4,
    "prepTimeMinutes": 15,
    "cookTimeMinutes": 30,
    "selectedIngredients": [
      { "item": "kidney beans", "quantity": 2, "unit": "cans" }
    ]
  }
]
```

**Constraints JSONB Structure**:
```json
{
  "numberOfMeals": 7,
  "mealTypes": ["dinner"],
  "servingsPerMeal": 4,
  "maxPrepTimeMinutes": 45,
  "maxCookTimeMinutes": 60,
  "dietaryPreferences": ["vegetarian"],
  "excludeIngredients": ["mushrooms", "olives"],
  "varietyLookbackDays": 14,
  "budgetPerMeal": 8.50
}
```

**Aggregated Ingredients Structure**:
```json
[
  {
    "ingredient": "kidney beans",
    "totalQuantity": 4,
    "unit": "cans",
    "usedInRecipes": [12345, 12346],
    "knusprProductId": "prod-456"
  }
]
```

**Metrics JSONB Structure**:
```json
{
  "totalPrepTimeMinutes": 180,
  "totalCookTimeMinutes": 310,
  "ingredientReusePercentage": 0.35,
  "varietyScore": 0.92,
  "estimatedWaste": 0.08,
  "estimatedCost": 58.50
}
```

**TypeScript/Pydantic**:
```typescript
class MealPlan {
  id: int
  userId: int
  startDate: date
  endDate: date
  mealType: 'dinner' | 'lunch' | 'breakfast'
  meals: PlannedMeal[]
  aggregatedIngredients: AggregatedIngredient[]
  constraints: MealPlanConstraints
  metrics: MealPlanMetrics
  createdAt: datetime
  updatedAt: datetime
}

class PlannedMeal {
  date: date
  mealType: str
  recipeId: int
  recipeName: str
  servings: int
  prepTimeMinutes: int
  cookTimeMinutes: int
}

class MealPlanConstraints {
  numberOfMeals: int
  mealTypes: str[]
  servingsPerMeal: int
  maxPrepTimeMinutes: int
  maxCookTimeMinutes: int
  dietaryPreferences: str[]
  excludeIngredients: str[]
  varietyLookbackDays: int
  budgetPerMeal?: float
}
```

---

### 5. GroceryCart

Represents a Knuspr grocery order.

**SQL Schema**:
```sql
CREATE TABLE grocery_carts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  meal_plan_id BIGINT REFERENCES meal_plans(id) ON DELETE SET NULL,
  knuspr_order_id VARCHAR(255), -- External Knuspr order ID
  items JSONB NOT NULL, -- Array of cart items
  items_grouped_by_section JSONB, -- Knuspr categories
  delivery_slot JSONB, -- Date, time window, cost
  pricing JSONB, -- Subtotal, delivery, total
  unavailable_items TEXT[], -- Items out of stock
  status VARCHAR(50) DEFAULT 'draft', -- draft, synced, ordered, cancelled
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_grocery_carts_user_id ON grocery_carts(user_id);
CREATE INDEX idx_grocery_carts_meal_plan_id ON grocery_carts(meal_plan_id);
CREATE INDEX idx_grocery_carts_knuspr_order_id ON grocery_carts(knuspr_order_id);
```

**Items JSONB Structure**:
```json
[
  {
    "ingredient": "kidney beans",
    "knusprProductId": "prod-123",
    "productName": "Organic Kidney Beans 400g",
    "quantity": 4,
    "unit": "cans",
    "unitPrice": 1.99,
    "totalPrice": 7.96,
    "storeSection": "canned-goods",
    "availability": "in-stock"
  }
]
```

**Delivery Slot Structure**:
```json
{
  "date": "2025-11-17",
  "timeWindow": "18:00-20:00",
  "cost": 4.99,
  "knusprSlotId": "slot-789"
}
```

**Pricing Structure**:
```json
{
  "subtotal": 52.34,
  "delivery": 4.99,
  "discount": 0.00,
  "total": 57.33
}
```

---

### 6. KnusprCredentials

Encrypted user credentials for Knuspr integration.

**SQL Schema**:
```sql
CREATE TABLE knuspr_credentials (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  login_encrypted BYTEA NOT NULL, -- Encrypted email/phone
  password_encrypted BYTEA NOT NULL, -- Encrypted password
  country VARCHAR(2) NOT NULL, -- User's Knuspr country
  last_synced_at TIMESTAMP,
  api_token_encrypted BYTEA, -- If using OAuth
  is_valid BOOLEAN DEFAULT TRUE,
  last_error TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_knuspr_credentials_user_id ON knuspr_credentials(user_id);
```

**Encryption Strategy**:
- Use PGCrypto or separate encryption service (AWS KMS, GCP Secrets)
- Keys rotated annually
- Credentials never logged or cached

**TypeScript/Pydantic** (only encrypted fields in API):
```typescript
class KnusprCredentials {
  userId: int
  country: str // ISO 3166-1 alpha-2
  isValid: bool
  lastSyncedAt?: datetime
  lastError?: str
  // login_encrypted and password_encrypted never exposed
}
```

---

### 7. AuditLog

Track all sensitive operations for compliance and debugging.

**SQL Schema**:
```sql
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(255) NOT NULL, -- 'recipe_harvested', 'cart_synced', etc.
  entity_type VARCHAR(50),
  entity_id BIGINT,
  details JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

---

## Relationships & Constraints

```
users
├── 1:N → recipes (user_id, soft delete)
├── 1:N → meal_plans
├── 1:N → grocery_carts
└── 1:1 → knuspr_credentials

meal_plans
├── N:1 → users
├── M:N → recipes (via meals JSONB)
└── 1:N → grocery_carts

grocery_carts
├── N:1 → users
└── N:1 → meal_plans (optional)

ingredient_taxonomy
└── Referenced by recipes (ingredients JSONB)
```

---

## Multi-Tenant Isolation Strategies

### Row-Level Security (RLS)
```sql
-- Enable RLS on all user-specific tables
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE grocery_carts ENABLE ROW LEVEL SECURITY;

-- Create policies for current_user_id() context variable
CREATE POLICY isolation_policy ON recipes
  USING (user_id = current_setting('app.user_id')::BIGINT);
```

### Application-Level Checks
- Every query includes `WHERE user_id = current_user.id`
- API layer validates tenant ownership before operations
- Audit logging for suspicious cross-user queries

---

## Indexing Strategy

### Primary Indexes (Mandatory)
```sql
-- User lookup
CREATE INDEX idx_users_email ON users(email);

-- Recipe discovery
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_recipes_dietary_tags ON recipes USING GIN(dietary_tags);

-- Meal plan queries
CREATE INDEX idx_meal_plans_user_id_dates ON meal_plans(user_id, start_date, end_date);

-- Cart lookups
CREATE INDEX idx_grocery_carts_user_id ON grocery_carts(user_id);
CREATE INDEX idx_grocery_carts_knuspr_order_id ON grocery_carts(knuspr_order_id);
```

### Performance Indexes (As-Needed)
- `meal_plans(user_id, created_at DESC)` for recent meals query
- `recipes(user_id, is_favorite)` for favorites list

---

## Validation Rules

### User
- Email must be valid format
- Country must be ISO 3166-1 alpha-2
- Password minimum 12 characters, must include uppercase, lowercase, number, special char
- Subscription tier must match billing records

### Recipe
- Title required, max 255 chars
- At least 1 ingredient and 1 instruction required
- Prep/cook time: 0-1440 minutes (24 hours max)
- Servings: 1-20 (reasonable range)
- Dietary tags must match predefined list
- Source URL must be valid HTTP(S) URL

### MealPlan
- Start date must be today or future
- End date must be >= start date
- Number of meals must match date range and meal types
- All recipes must belong to user
- Constraints must be satisfiable (validated by planner)

### GroceryCart
- Items must not be empty
- Delivery slot must be valid Knuspr slot
- Total pricing must be > 0

---

## Migration & Evolution Strategy

### Phase 1 (MVP)
- Minimal schema, focus on core entities
- No historical tracking (deleted_at only)
- Simple JSONB for flexible fields

### Phase 2 (Scaling)
- Add read replicas (requires logical decoding)
- Add partitioning for large tables (meal_plans by user_id)
- Extract JSONB fields to dedicated tables if needed
- Add soft-delete archival strategy

### Migration Approach
- Use Alembic for schema versioning
- Every migration tested against current data volume
- Rollback procedure documented
- Zero-downtime deployments using feature flags

---

**Version**: 1.0.0 (Phase 1 - MVP)
**Last Updated**: 2025-11-14
**Next Review**: Before Phase 2 scaling
