# Implementation Plan: Multi-Agent Recipe & Meal Planning System

**Feature**: Multi-Agent Recipe and Meal Planning System
**Version**: 1.0.0 (MVP)
**Timeline**: 8-12 weeks (estimated for team of 2-3)
**Status**: Planning Complete - Ready for Development

---

## Implementation Overview

This document outlines the architecture, phases, and technical approach for building a production-ready multi-agent recipe and meal planning SaaS.

### Success Definition
The MVP is successful when:
1. 10 concurrent users can complete workflow (recipe → meal plan → cart) in <10 minutes
2. 90%+ of Ottolenghi recipes harvested successfully
3. Meal plans generated in <5 seconds
4. Knuspr integration works end-to-end
5. Performance metrics exposed and dashboards created
6. Zero data leaks between users (security audit passed)

---

## Phase 1: Foundation & Core Agents (Weeks 1-4)

### Objectives
- Set up development environment
- Build core agents and event bus
- Implement recipe harvester
- Set up monitoring/observability

### 1A: Project Setup & Infrastructure (Week 1)

**Deliverables**:
- ✅ Docker Compose with PostgreSQL, Redis, FastAPI
- ✅ GitHub Actions CI/CD pipeline
- ✅ Prometheus setup with basic metrics
- ✅ Project structure and development guide
- ✅ Database migrations using Alembic
- ✅ pytest fixtures for agent testing

**Tasks**:
```
1. Initialize FastAPI project structure
   - packages/       (Library-First Architecture)
     - harvester/    (Recipe scraping & normalization)
     - intelligence/ (Ingredient taxonomy & substitution)
     - architect/    (Meal planning logic & solvers)
     - optimizer/    (Cart optimization & Knuspr integration)
     - core/         (Shared models, events, utils)
   - services/
     - api/          (FastAPI gateway importing packages)
   - tests/
   - docker/
   - k8s/            (Future: Kubernetes manifests)

2. Set up PostgreSQL with Alembic migrations
   - Initial schema (users, recipes, meal_plans, grocery_carts, etc.)
   - Row-level security policies
   - Indexes for common queries

3. Set up Redis for caching and message queue
   - Connection pooling
   - Pub/Sub topic setup
   - TTL management

4. Configure Prometheus
   - FastAPI middleware for request metrics
   - Custom metrics for agents
   - /metrics endpoint

5. Create GitHub Actions workflow
   - Run pytest on PR
   - Check coverage (>80% threshold)
   - Lint with flake8/black
   - Build Docker image
```

**Tech Stack Details**:
- FastAPI 0.104+ with Uvicorn
- SQLAlchemy 2.0 with async support
- Alembic for migrations
- Pydantic V2 for validation
- Prometheus Python client
- pytest with async support

---

### 1B: Authentication & User Management (Week 1.5)

**Deliverables**:
- ✅ User signup, login, logout flows
- ✅ JWT token authentication
- ✅ User preferences endpoint
- ✅ Knuspr credentials storage (encrypted)

**Endpoints**:
```
POST /api/v1/auth/signup
  - email, password, country
  - Returns: user_id, access_token

POST /api/v1/auth/login
  - email, password
  - Returns: access_token, expires_in

POST /api/v1/auth/logout
  - Invalidates token

GET /api/v1/users/me
  - Returns: current user profile

PUT /api/v1/users/preferences
  - Update dietary prefs, theme, etc.

POST /api/v1/users/knuspr-credentials
  - Store encrypted Knuspr login
  - Param: login, password, country

GET /api/v1/users/knuspr-credentials
  - Returns: is_valid, last_synced_at (no credentials exposed)
```

**Database**:
```sql
-- Alembic migration: 001_create_users_table
CREATE TABLE users (...)
CREATE INDEX idx_users_email ...
CREATE POLICY ...
```

**Security**:
- Passwords hashed with bcrypt (12 rounds)
- Knuspr credentials encrypted with PGCrypto
- JWT tokens with 1-hour expiry
- Rate limiting: 5 login attempts per IP per hour

---

### 1C: Recipe Harvester Agent - Architecture (Week 2)

**Deliverables**:
- ✅ Agent base class with health checks
- ✅ Capability manifest system
- ✅ Event bus pub/sub (Redis Pub/Sub)
- ✅ Idempotency framework for agents

**Architecture**:
```
RecipeHarvesterAgent (Base)
├── PuppeteerHarvester (dynamic sites)
├── HTTPHarvester (static HTML)
├── RSSHarvester (feed polling)
└── ClaudeEnrichment (AI analysis for edge cases)
```

**Agent Base Class**:
```python
class Agent:
    id: str
    agent_type: str
    version: str

    @property
    def capability_manifest(self) -> Dict:
        # Describes what this agent can do
        return {
            "agentId": self.id,
            "agentType": self.agent_type,
            "version": self.version,
            "capabilities": [...],
            "inputEvents": [...],
            "outputEvents": [...]
        }

    async def health_check(self) -> HealthStatus:
        # Check dependencies, return status
        pass

    async def handle_event(self, event: Event) -> None:
        # Process event, emit results
        pass
```

**Event Bus Implementation**:
```python
class EventBus:
    async def publish(self, event: Event) -> None:
        # Publish to Redis Pub/Sub
        # Include: eventType, payload, correlationId
        pass

    async def subscribe(self, topic: str, handler: Callable) -> None:
        # Subscribe to topic pattern
        # Call handler on matching events
        pass
```

**Idempotency Framework**:
```python
class IdempotencyKey:
    # Ensure agent handles same request only once
    # Key = (agent_id, source_url, harvest_timestamp)
    # Cache result for 24 hours
    pass
```

**Tasks**:
```
1. Create Agent base class with lifecycle
2. Implement capability manifest pattern
3. Set up Redis Pub/Sub event bus
4. Create health check endpoints (/health)
5. Implement event schema validation
6. Add correlation ID tracking
7. Create agent test fixtures
```

---

### 1D: Recipe Harvester - Ottolenghi Recipes (Week 2.5)

**Deliverables**:
- ✅ HTTP scraper for Ottolenghi website
- ✅ Recipe normalization pipeline
- ✅ Duplicate detection
- ✅ Harvesting metrics to Prometheus

**Implementation**:
```python
class OttolenghhiHarvester:
    async def harvest_recipes(self, page_url: str) -> List[Recipe]:
        # 1. Fetch page with retries
        # 2. Parse HTML (BeautifulSoup)
        # 3. Extract schema.org/Recipe if present
        # 4. Normalize fields
        # 5. Detect duplicates
        # 6. Store in PostgreSQL
        # 7. Emit recipe.harvested.success event
        pass

    async def detect_duplicate(self, recipe: Recipe) -> Optional[Recipe]:
        # Check title similarity
        # Check ingredient overlap (>80% match)
        # Merge if duplicate found
        pass
```

**Recipe Normalization**:
```
Input:  Various HTML formats, schema.org, microdata
Output: Canonical Recipe entity
        - Ingredients with standard units (cups → grams)
        - Instructions as ordered list
        - Metadata: source, harvest time, confidence
```

**Duplicate Detection**:
- Fuzzy title matching (levenshtein distance)
- Ingredient overlap calculation
- Merge strategy: keep newer, reference older

**Metrics**:
```
recipe_harvested_total{status, source}
recipe_harvest_duration_seconds{quantile}
recipe_duplicate_detected_total
recipe_normalization_errors_total
```

**Tasks**:
```
1. Create HTTP scraper with retries
2. Parse HTML and extract recipe data
3. Implement schema.org/Recipe detection
4. Create normalization pipeline (units, formats)
5. Implement duplicate detection algorithm
6. Add to PostgreSQL recipes table
7. Emit events to event bus
8. Add Prometheus metrics
9. Test with real Ottolenghi URLs (10+ recipes)
```

---

### 1E: Ingredient Intelligence Agent - Foundation (Week 3)

**Deliverables**:
- ✅ Ingredient taxonomy table (PostgreSQL)
- ✅ Basic substitution rules
- ✅ Ingredient classification agent
- ✅ Allergen checking

**Implementation**:
```python
class IngredientIntelligenceAgent:
    async def classify_ingredient(self, ingredient: str) -> IngredientInfo:
        # 1. Normalize ingredient name
        # 2. Look up in taxonomy
        # 3. Extract category, allergens, substitutes
        # 4. Emit ingredient.classification.complete event
        pass

    async def suggest_substitutions(self,
        ingredient: str,
        quantity: float,
        context: SubstitutionContext
    ) -> List[Substitute]:
        # 1. Look up ingredient in taxonomy
        # 2. Filter substitutes by dietary constraints
        # 3. Filter by seasonal availability
        # 4. Calculate ratios and adjustments
        # 5. Flag allergen warnings
        # 6. Emit ingredient.substitution.suggestions event
        pass
```

**Ingredient Taxonomy**:
- ~5000 common ingredients (to be built in week 3)
- Categories: dairy, protein, vegetables, grains, oils, etc.
- Substitutes with confidence scores and ratios
- Allergen information
- Seasonal availability by region

**Substitution Logic** (Phase 1: Rule-Based):
```
Input:  butter + vegan diet
Output: [
  {name: coconut oil, confidence: 0.95, ratio: 0.75},
  {name: olive oil, confidence: 0.85, ratio: 1.0}
]
```

**Phase 2 Upgrade**: Use Claude for intelligent substitutions.

**Tasks**:
```
1. Build ingredient taxonomy (DB seed file)
2. Create substitutes reference data
3. Implement ingredient classification service
4. Create substitution rule engine
5. Add allergen checking logic
6. Handle edge cases (ambiguous ingredients)
7. Create agent handlers for events
8. Add Prometheus metrics
```

---

### 1F: Monitoring & Observability Setup (Week 3.5)

**Deliverables**:
- ✅ Prometheus scraping working
- ✅ Grafana dashboards created
- ✅ Alert rules configured
- ✅ Structured logging setup

**Prometheus Metrics** (Already implemented via FastAPI middleware):
```
http_requests_total{endpoint, method, status}
http_request_duration_seconds{endpoint, quantile}

agent_requests_total{agent_type, status}
agent_request_duration_seconds{agent_type, quantile}
agent_errors_total{agent_type, error_type}

recipe_harvested_total{status, source}
recipes_in_database{user_id}

db_query_duration_seconds{operation, quantile}
db_connections_total
```

**Grafana Dashboards**:
1. System Health
   - FastAPI uptime, request rate, latency
   - Database connection pool
   - Redis memory usage

2. Agent Health
   - Recipe Harvester success rate, duration
   - Ingredient Intelligence requests, errors
   - Agent health checks

3. Business Metrics
   - Total recipes in system
   - Users created, active
   - Harvester success rate by source

**Alerting Rules** (AlertManager):
```yaml
- alert: HighErrorRate
  condition: error_rate > 5%

- alert: SlowQueryDetected
  condition: query_latency_p99 > 1s

- alert: AgentUnhealthy
  condition: agent_health_status != healthy
```

**Structured Logging**:
```python
logger.info("recipe_harvested", extra={
    "user_id": user_id,
    "recipe_id": recipe_id,
    "source": "ottolenghi",
    "duration_ms": 1250
})
```

**Tasks**:
```
1. Set up Prometheus scraping config
2. Create Grafana dashboards (3 total)
3. Configure alert rules (AlertManager)
4. Implement structured logging
5. Create log aggregation (ELK or Cloud Logging)
6. Add performance SLOs
7. Document metrics in README
```

---

### 1G: Support Services & Error Handling (Week 4)

**Deliverables**:
- ✅ Dead Letter Queue (DLQ) for failed events
- ✅ Error handler agent
- ✅ Notification service (Phase 1: in-app only)
- ✅ User preferences service

**Architecture**:
```
Event Processing Flow:
┌─────────────────────────────────────────┐
│ Event Published (any agent)             │
└──────────────┬──────────────────────────┘
               │
               ├─→ Route by Topic (recipe.*, ingredient.*, etc.)
               │
               ├─→ Handler processes successfully
               │   └─→ Next workflow step
               │
               └─→ Handler throws exception
                   └─→ Retry with exponential backoff (3 attempts)
                       ├─→ Success after retry: Continue
                       └─→ Failure after 3 retries
                           └─→ MOVE TO DEAD LETTER QUEUE (DLQ)
                               └─→ Error Handler Agent
                                   ├─→ Log detailed error
                                   ├─→ Notify user (in-app)
                                   ├─→ Create support ticket
                                   └─→ Emit error.unhandled event
```

**Error Handler Agent**:
```python
class ErrorHandlerAgent(Agent):
    async def handle_failed_event(self, event: Event) -> None:
        """Process events that failed after retries"""
        try:
            # 1. Extract error context
            error_details = {
                "eventType": event.eventType,
                "originalPayload": event.payload,
                "error": event.error,
                "retryCount": event.metadata.retryCount,
                "failureTimestamp": datetime.utcnow()
            }

            # 2. Store in database for investigation
            await self.db.failed_events.insert(error_details)

            # 3. Notify user if applicable
            if event.payload.get("user_id"):
                await self.notification_service.send_error_notification(
                    user_id=event.payload.user_id,
                    event_type=event.eventType,
                    error_message=event.error
                )

            # 4. Create monitoring alert
            self.metrics.error_unhandled_total.labels(
                event_type=event.eventType
            ).inc()

            # 5. Log for debugging
            logger.error(
                "unhandled_event_in_dlq",
                extra=error_details
            )
        except Exception as e:
            # Prevent error handler from failing
            logger.critical("error_handler_failed", extra={"error": str(e)})
```

**Notification Service**:
- **Phase 1 (MVP)**: In-app notifications only
  - "Meal plan generated successfully"
  - "Recipe harvesting failed, click to retry"
  - "Knuspr cart created, click to open"
  - Error notifications (with retry buttons)

- **Phase 2+**: Email + SMS notifications
  - Integration with SendGrid/AWS SNS
  - User notification preferences
  - Digest emails (daily/weekly)

**User Preferences Service**:
```python
class UserPreferencesService:
    async def get_preferences(self, user_id: int) -> UserPreferences:
        """Get user's app preferences"""
        # Notifications: in-app, email, sms
        # Dietary: vegetarian, vegan, gluten-free, etc.
        # Cuisine: preferred cuisines
        # Timing: max prep time, meal frequency
        # Language: for UI localization
        return user.preferences

    async def update_preferences(
        self,
        user_id: int,
        updates: UserPreferencesUpdate
    ) -> UserPreferences:
        """Update user preferences"""
        user.preferences.update(updates)
        await self.db.users.update(user)
        return user.preferences
```

**Database Table for Failed Events**:
```sql
CREATE TABLE failed_events (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  event_type VARCHAR(255) NOT NULL,
  original_payload JSONB NOT NULL,
  error_message TEXT,
  error_traceback TEXT,
  retry_count INT DEFAULT 0,
  failed_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,
  resolution_notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_failed_events_user_id ON failed_events(user_id);
CREATE INDEX idx_failed_events_resolved ON failed_events(resolved_at);
```

**Event Bus Dead Letter Queue Pattern**:
```
Phase 1 Implementation:
- Use separate Redis Pub/Sub topic: `*.failed`
- All failed events published to DLQ topic
- ErrorHandlerAgent subscribes to DLQ
- Maximum retry: 3 attempts with exponential backoff (1s, 2s, 4s)

Example Flow:
1. recipe.harvest.requested published
2. Harvester fails to extract recipe
3. After 3 retries, emits recipe.harvest.failed
4. ErrorHandlerAgent catches in DLQ topic
5. Stores in failed_events table
6. Notifies user via in-app notification
7. User can manually retry from UI
```

**Notification Event Schema**:
```json
{
  "eventType": "notification.created",
  "timestamp": "2025-11-14T10:30:00Z",
  "payload": {
    "userId": "user-456",
    "type": "info" | "warning" | "error" | "success",
    "title": "Meal Plan Generated",
    "message": "Your 7-day meal plan is ready",
    "actionUrl": "/meal-plans/plan-789",
    "actionLabel": "View Plan",
    "dismissable": true,
    "expiresAt": "2025-11-15T10:30:00Z"
  }
}
```

**Tasks**:
```
1. Create ErrorHandlerAgent class
2. Implement DLQ topic routing in event bus
3. Create failed_events table migration
4. Implement retry logic with exponential backoff
5. Create NotificationService class
6. Add in-app notification endpoints
7. Create UserPreferencesService
8. Add notification dismissal tracking
9. Create support ticket system (basic)
10. Test error scenarios (network failures, timeouts)
11. Document DLQ investigation procedures
12. Create dashboards for failed event monitoring
```

**Metrics to Expose**:
```
error_event_retry_total{event_type, attempt}
error_event_dlq_total{event_type}
error_event_resolved_total{event_type, resolution}
notification_created_total{type, user_id}
notification_read_total{type}
support_ticket_created_total{issue_type}
```

---

## Phase 2: Orchestration & Meal Planning (Weeks 5-7)

### Objectives
- Build Meal Architect agent with constraint solving
- Implement workflow orchestration (LangGraph)
- Create meal plan generation API

### 2A: Constraint Solver Integration (Week 5)

**Deliverables**:
- ✅ Z3 constraint solver setup
- ✅ Meal planning algorithm
- ✅ Constraint validation

**Constraints to Model**:
```
Variables:
  recipes[day] = selected recipe for each day
  adjustments[recipe] = serving size adjustments

Constraints:
  1. len(recipes) == number_of_meals
  2. all recipe.dietaryTags ⊆ user.allowedDiets
  3. all ingredient NOT IN user.excludedIngredients
  4. avg(recipe.prepTime) <= user.maxPrepTime
  5. variety: no recipe in last 14 days
  6. maximize: sum(ingredient_reuse)

Objective:
  maximize(ingredient_reuse) + variety_score
```

**Algorithm** (Simplified Z3 approach):
```python
def generate_meal_plan(constraints: MealPlanConstraints) -> MealPlan:
    # 1. Load recipes from DB filtered by constraints
    # 2. Create Z3 solver
    # 3. Define variables and constraints
    # 4. Solve
    # 5. Extract solution
    # 6. Calculate metrics (reuse %, variety)
    # 7. Return MealPlan
```

**Performance Target**: <5 seconds for 7-day plan.

**Tasks**:
```
1. Integrate Z3-solver Python bindings
2. Create meal planning DSL in Z3
3. Implement constraint builder from user input
4. Add recipe filtering (dietary, ingredients, timing)
5. Implement variety check (14-day lookback)
6. Optimize for ingredient reuse
7. Create test cases (various constraints)
8. Benchmark solve time
```

---

### 2B: Meal Architect Agent (Week 5.5)

**Deliverables**:
- ✅ Meal Architect agent implementation
- ✅ Meal plan generation event handler
- ✅ Regenerate-meal capability

**Agent Implementation**:
```python
class MealArchitectAgent(Agent):
    async def handle_mealplan_generation_requested(
        self, event: MealPlanGenerationRequested
    ) -> None:
        try:
            plan = await self.generate_meal_plan(
                event.payload.constraints,
                event.payload.user_id,
                event.payload.start_date
            )

            # Store in PostgreSQL
            await self.db.meal_plans.insert(plan)

            # Emit success event
            await self.event_bus.publish(
                MealPlanGenerated(plan=plan)
            )
        except Exception as e:
            await self.event_bus.publish(
                MealPlanGenerationFailed(error=str(e))
            )

    async def generate_meal_plan(self, ...) -> MealPlan:
        # Delegates to Z3 solver
        pass
```

**Event Handlers**:
- `mealplan.generation.requested` → generate plan, emit success/failure
- `mealplan.regenerate.requested` → swap one meal, keep others

**Capabilities**:
- `mealplan.generate` - Create new meal plan
- `mealplan.optimize` - Improve existing plan
- `mealplan.regenerate-meal` - Swap single meal

**Tasks**:
```
1. Implement MealArchitectAgent class
2. Add mealplan.generation.requested handler
3. Add mealplan.regenerate.requested handler
4. Implement meal plan storage to PostgreSQL
5. Add variety lookback query (14 days)
6. Create event emission pattern
7. Add error handling and dead letter queue
8. Test with various constraint combinations
```

---

### 2C: Orchestration with LangGraph (Week 6)

**Deliverables**:
- ✅ LangGraph workflow definition
- ✅ Multi-step orchestration patterns
- ✅ Workflow visualization

**Workflows to Implement**:

**1. Simple Meal Planning Flow**:
```
User Input (constraints)
  ↓
[Meal Architect] Generate Plan
  ↓
[Ingredient Intelligence] Check Availability
  ↓
[Is Available?]
  ├─ Yes → Store Plan → Success
  └─ No → Suggest Substitutions → Regenerate → Success
```

**2. Full Meal Planning + Grocery Flow**:
```
User Input (constraints)
  ↓
[Meal Architect] Generate Plan
  ↓
[Ingredient Intelligence] Verify & Suggest Substitutions
  ↓
[Cart Optimizer] Create Knuspr Cart (Week 7)
  ↓
[Notification Service] Notify User
  ↓
Success
```

**LangGraph Structure**:
```python
from langgraph.graph import StateGraph

def create_meal_planning_graph():
    graph = StateGraph(MealPlanningState)

    # Add nodes
    graph.add_node("generate_plan", generate_plan_node)
    graph.add_node("check_availability", check_availability_node)
    graph.add_node("suggest_substitutions", suggest_substitutions_node)
    graph.add_node("store_plan", store_plan_node)

    # Add edges
    graph.add_edge("START", "generate_plan")
    graph.add_edge("generate_plan", "check_availability")
    graph.add_conditional_edges(
        "check_availability",
        lambda state: "store_plan" if state.available else "suggest_substitutions"
    )
    graph.add_edge("suggest_substitutions", "store_plan")
    graph.add_edge("store_plan", "END")

    return graph.compile()
```

**Workflow Visualization**:
- LangSmith integration for execution tracing
- Mermaid diagrams in documentation

**Tasks**:
```
1. Install langgraph
2. Define workflow state schema
3. Create graph nodes for each step
4. Implement conditional routing
5. Add error handling and retries
6. Create workflow tests
7. Add LangSmith tracing
8. Document workflow diagrams
```

---

### 2D: Meal Planning API (Week 6.5)

**Deliverables**:
- ✅ POST /api/v1/mealplans endpoint
- ✅ GET /api/v1/mealplans/{id} endpoint
- ✅ PUT /api/v1/mealplans/{id} regenerate meal

**Endpoints**:
```
POST /api/v1/mealplans
  Input: {
    constraints: {
      numberOfMeals: 7,
      dietaryPreferences: ["vegetarian"],
      maxPrepTime: 45,
      ...
    },
    startDate: "2025-11-18"
  }
  Output: {
    mealPlanId: "plan-789",
    status: "generated",
    meals: [...],
    metrics: {...}
  }

GET /api/v1/mealplans/{id}
  Output: full MealPlan with meals, ingredients

PUT /api/v1/mealplans/{id}/regenerate-meal
  Input: { date: "2025-11-18" }
  Output: updated MealPlan with new recipe for that date

GET /api/v1/mealplans?startDate=&endDate=
  Output: list of user's meal plans (paginated)
```

**Error Handling**:
```
- 400: Invalid constraints (unsatisfiable, bad dates)
- 404: Meal plan not found
- 422: Constraint validation error
```

**Tasks**:
```
1. Create FastAPI route handlers
2. Add constraint validation
3. Trigger MealArchitectAgent
4. Implement async polling (wait for result)
5. Add error handling
6. Write integration tests
7. Add API documentation
```

---

## Phase 3: Knuspr Integration & Cart Optimization (Weeks 7-8)

### Objectives
- Integrate with Knuspr API (via MCP)
- Build Cart Optimizer agent
- Create end-to-end workflow

### 3A: Knuspr MCP Integration (Week 7)

**Deliverables**:
- ✅ Knuspr MCP server connection
- ✅ Recipe → Ingredient → Knuspr Product mapping
- ✅ Cart creation with Knuspr API

**MCP Server Setup** (Experimental):
```python
# From: https://github.com/tomaspavlin/rohlik-mcp
from knuspr_mcp import KnusprMCPClient

client = KnusprMCPClient(
    login_credentials=user.knuspr_login,
    country=user.country
)

# Available endpoints (per MCP spec)
products = await client.search_products(ingredient_name)
cart = await client.create_cart(items)
delivery_slots = await client.get_delivery_slots(date_range)
```

**Ingredient → Knuspr Product Mapping**:
```
Ingredient: "kidney beans, 2 cans"
  ↓
Search Knuspr: "kidney beans"
  ↓
Match: "Organic Kidney Beans 400g" (prod-123)
  ↓
Adjust: 2 cans × qty_per_can = final_quantity
  ↓
Add to Cart: {product_id, quantity, unit_price}
```

**Error Handling**:
- Product not found → Flag unavailable
- API timeout → Retry with backoff
- Rate limit → Queue for retry

**Tasks**:
```
1. Research Knuspr MCP server docs
2. Implement MCP client wrapper
3. Create ingredient → product search function
4. Handle fuzzy matching (canned beans variants)
5. Implement quantity conversion
6. Add error handling and fallbacks
7. Create integration tests with test credentials
```

---

### 3B: Cart Optimizer Agent (Week 7.5)

**Deliverables**:
- ✅ Cart Optimizer agent implementation
- ✅ Item grouping by store section
- ✅ Delivery slot selection

**Implementation**:
```python
class CartOptimizerAgent(Agent):
    async def handle_cart_creation_requested(
        self, event: CartCreationRequested
    ) -> None:
        try:
            # 1. Get ingredients from meal plan
            # 2. Search Knuspr for products
            # 3. Group by store section
            # 4. Select optimal delivery slot
            # 5. Create Knuspr cart
            # 6. Store in PostgreSQL
            # 7. Emit success event
        except Exception as e:
            # Emit failure event
            pass

    async def group_items_by_section(
        self, items: List[CartItem]
    ) -> Dict[str, List[CartItem]]:
        # Group by: produce, dairy, meat, canned_goods, frozen, etc.
        pass

    async def select_delivery_slot(
        self,
        available_slots: List[DeliverySlot],
        preferences: DeliveryPreferences
    ) -> DeliverySlot:
        # Prefer: earliest, cheapest, or user-specified
        pass
```

**Item Grouping**:
```json
{
  "produce": [carrot, onion, garlic],
  "dairy": [milk, butter],
  "canned_goods": [beans, tomatoes],
  "frozen": [peas],
  "meat": [chicken breast]
}
```

**Delivery Slot Selection**:
- Parse available slots from Knuspr
- Filter by user preferences (date range, time window)
- Select: earliest, cheapest, or user-preferred
- Calculate delivery cost

**Tasks**:
```
1. Implement CartOptimizerAgent class
2. Add cart.creation.requested handler
3. Create Knuspr product search service
4. Implement item grouping by section
5. Add delivery slot fetching and selection
6. Implement cart creation with Knuspr API
7. Handle unavailable items (suggest alternatives)
8. Store cart in PostgreSQL
9. Emit cart.created event
10. Add error handling and retries
```

---

### 3C: End-to-End Workflow (Week 8)

**Deliverables**:
- ✅ Full orchestration from meal plan → cart
- ✅ User-facing API
- ✅ Error recovery

**Complete Workflow**:
```
POST /api/v1/workflows/meal-plan-with-groceries
Input: {
  constraints: {...},
  startDate: "2025-11-18",
  deliveryPreferences: {
    preferredDates: ["2025-11-17"],
    preferredTimeSlot: "evening"
  }
}

Steps:
1. Generate meal plan (MealArchitectAgent)
2. Check availability & suggest substitutions (IngredientIntelligenceAgent)
3. Create Knuspr cart (CartOptimizerAgent)
4. Return cart URL to user

Output: {
  mealPlanId: "plan-789",
  cartId: "cart-321",
  knusprUrl: "https://knuspr.de/cart/...",
  metrics: {
    totalCost: 57.33,
    ingredientReuse: 0.35,
    estimatedTime: "75 minutes"
  }
}
```

**Error Recovery**:
- Meal plan generation fails → Return error with suggestions
- Ingredient unavailable → Trigger substitution → Regenerate cart
- Knuspr API error → Retry or provide manual list

**Tasks**:
```
1. Create workflow orchestration endpoint
2. Implement error recovery logic
3. Add user-friendly error messages
4. Create end-to-end tests
5. Document workflow for users
6. Add Prometheus metrics for workflow
```

---

## Phase 4: Frontend & UI (Weeks 8-10)

### Objectives
- Build mobile-first web UI
- Implement user workflows
- Test with real users

### 4A: Frontend Setup (Week 8.5)

**Technology**:
- Next.js 16 + React 19
- Mobile-first responsive design
- TypeScript for type safety
- Vite for fast builds

**Project Structure**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/      (login, signup)
│   │   ├── Recipes/   (search, details)
│   │   ├── MealPlan/  (planner, review)
│   │   ├── Cart/      (preview, summary)
│   │   └── Common/    (header, nav, footer)
│   ├── pages/
│   ├── hooks/
│   ├── api/           (API client)
│   ├── stores/        (state management)
│   ├── styles/        (Tailwind CSS)
│   └── App.tsx
├── public/
├── vite.config.ts
└── package.json
```

**Responsive Design**:
- Mobile: 375px (iPhone SE)
- Tablet: 768px
- Desktop: 1024px+

**Tasks**:
```
1. Create React/Vue project with Vite
2. Set up TypeScript configuration
3. Configure Tailwind CSS
4. Create project folder structure
5. Set up API client (axios/fetch)
6. Implement state management (Context/Pinia)
7. Create reusable components
8. Set up routing
9. Configure CI/CD for frontend
```

---

### 4B: Authentication UI (Week 9)

**Deliverables**:
- ✅ Login/signup pages
- ✅ User profile/preferences
- ✅ Knuspr credentials management

**Pages**:
```
/login
  - Email, password fields
  - Link to signup
  - Remember me option

/signup
  - Email, password, password confirm
  - Country dropdown (DE, AT, CH)
  - Terms of service checkbox
  - Auto-login after signup

/profile
  - User email (read-only)
  - Change password
  - Dietary preferences (checkboxes)
  - Knuspr credentials

/preferences
  - Language
  - Theme (light/dark)
  - Mobile notifications
  - Dietary restrictions
  - Favorite cuisines
```

**Tasks**:
```
1. Create login form with validation
2. Create signup form with validation
3. Implement authentication flow
4. Add password strength indicator
5. Create profile edit page
6. Implement Knuspr credentials form
7. Add error messages
8. Add success notifications
9. Test on mobile (375px)
```

---

### 4C: Recipe Discovery UI (Week 9)

**Deliverables**:
- ✅ Recipe search and filter
- ✅ Recipe detail page
- ✅ Favorites management

**Pages**:
```
/recipes
  - Search bar (by title, ingredient)
  - Filters:
    - Dietary tags (vegetarian, vegan, etc.)
    - Cuisine (Italian, Asian, etc.)
    - Difficulty (easy, medium, hard)
    - Time budget (prep + cook)
  - Recipe cards grid (mobile-responsive)
  - Pagination

/recipes/{id}
  - Recipe title, image
  - Prep/cook time, servings
  - Ingredients list
  - Instructions (step-by-step)
  - Dietary tags, cuisine
  - Add to favorites button
  - Source link (if applicable)
```

**Tasks**:
```
1. Create recipe search API integration
2. Build recipe list with filters
3. Create recipe card component
4. Implement pagination
5. Create recipe detail page
6. Add ingredient display
7. Implement favorites toggle
8. Add mobile-friendly layout
9. Test search performance
```

---

### 4D: Meal Planner UI (Week 9.5)

**Deliverables**:
- ✅ Meal plan creation wizard
- ✅ Plan preview and editing
- ✅ Shopping cart generation

**Pages**:
```
/meal-planner
  Step 1: Constraints
    - Number of meals (5-7)
    - Meal type (dinner, lunch, breakfast)
    - Dietary preferences
    - Allergies/exclusions
    - Time budget
    - Start date

  Step 2: Generated Plan
    - Weekly calendar view
    - Each day shows recipe
    - Can click to swap recipe
    - Shows ingredients aggregated
    - Estimated prep/cook time

  Step 3: Review & Confirm
    - Final meal plan summary
    - Total ingredients with quantities
    - Estimated time
    - Button: "Create Shopping Cart"

/meal-plan/{id}
  - Editable weekly view
  - Can swap individual meals
  - Shows ingredient reuse
  - Link to shopping cart
```

**Tasks**:
```
1. Create meal planner wizard component
2. Build constraints form
3. Add form validation
4. Create generated plan display
5. Implement recipe swapping UI
6. Add ingredient aggregation display
7. Create review/confirm page
8. Add loading states
9. Implement error handling
10. Test mobile experience
```

---

### 4E: Shopping Cart UI (Week 10)

**Deliverables**:
- ✅ Cart preview (read-only)
- ✅ Delivery preferences
- ✅ "Add to Knuspr" workflow

**Pages**:
```
/carts/{id}
  - Meal plan summary
  - Items grouped by Knuspr section
    - Produce
    - Dairy
    - Meat
    - Canned goods
    - Frozen
    - Pantry

  - Pricing breakdown
    - Subtotal
    - Delivery cost
    - Total

  - Delivery slot selection
    - Available dates/times
    - Price comparison

  - Button: "Go to Knuspr" (opens MCP cart)
  - Button: "Share cart" (copy link)
```

**Integration with Knuspr**:
- Generate Knuspr cart URL
- Pre-populate with items from meal plan
- User completes checkout in Knuspr app

**Tasks**:
```
1. Create cart display component
2. Implement item grouping by section
3. Add pricing breakdown
4. Create delivery slot selector
5. Implement Knuspr integration
6. Add "Go to Knuspr" button
7. Create cart summary/sharing
8. Add success/error messaging
9. Test full user flow
10. Optimize mobile UX
```

---

## Phase 5: Testing, Polish & Launch (Weeks 10-12)

### Objectives
- Complete comprehensive testing
- Performance optimization
- Beta testing with 5-10 users
- Production deployment

### 5A: Testing (Week 10)

**Deliverables**:
- ✅ Unit test suite (>80% coverage)
- ✅ Integration tests
- ✅ End-to-end tests
- ✅ Performance tests

**Test Coverage**:
```
Unit Tests:
- Agent logic (harvesting, substitution, planning)
- Event handlers
- Database models
- API endpoints
- Utility functions

Integration Tests:
- Agent-to-agent communication
- Database transactions
- Knuspr API integration
- Event bus reliability
- Workflow orchestration

E2E Tests:
- User signup → meal plan → cart creation
- Recipe search → add to plan
- Cart preview → Knuspr integration

Performance Tests:
- Meal plan generation <5s (100 recipes)
- Recipe search <200ms (1000 recipes)
- Cart creation <2s
- API response times (p99 <500ms)
```

**Tools**:
- pytest (unit/integration)
- Playwright (E2E)
- Locust (load testing)
- ApacheBench (HTTP performance)

**Tasks**:
```
1. Write unit tests for agents
2. Write integration tests for workflows
3. Create E2E test scenarios
4. Set up CI test reporting
5. Add performance benchmarks
6. Create load testing suite
7. Achieve 80%+ code coverage
8. Document test procedures
```

---

### 5B: Performance Optimization (Week 11)

**Deliverables**:
- ✅ Database query optimization
- ✅ Caching strategy
- ✅ API response time targets
- ✅ Frontend bundle optimization

**Optimizations**:
```
Backend:
- Add database indexes (query analysis)
- Implement query caching (24-hour TTL)
- Batch ingredient searches
- Optimize Z3 solver constraints
- Connection pooling tuning

Frontend:
- Code splitting (route-based)
- Image optimization
- Bundle size analysis
- CSS optimization
- Lazy loading components
```

**Metrics**:
```
- API p99 latency <500ms
- Meal plan generation <5s
- Frontend bundle <150KB (gzipped)
- First Contentful Paint <2s (mobile 3G)
```

**Tasks**:
```
1. Profile API response times
2. Analyze slow queries
3. Add strategic indexes
4. Implement caching layer
5. Optimize frontend bundle
6. Measure Core Web Vitals
7. Load test with 10 concurrent users
8. Document performance targets
```

---

### 5C: Beta Testing (Week 11)

**Deliverables**:
- ✅ Beta program setup
- ✅ User feedback integration
- ✅ Bug fixes and refinements

**Beta Plan**:
```
Recruitment: 5-10 users
- Mix of technical and non-technical
- From target markets (DE, AT, CH)
- 1-week beta period

Testing Scenarios:
1. Sign up and set preferences
2. Explore recipes
3. Create meal plan
4. Generate shopping cart
5. Access Knuspr integration

Feedback Collection:
- Usability feedback
- Bug reports
- Feature requests
- Performance issues
```

**Success Criteria**:
- Users complete workflow in <10 minutes (avg)
- NPS score >40
- Zero data loss incidents
- Zero security issues found

**Tasks**:
```
1. Recruit beta users
2. Create testing guide
3. Set up feedback system (TypeForm)
4. Monitor system during beta
5. Collect bug reports
6. Fix critical issues
7. Publish updates
8. Gather final feedback
```

---

### 5D: Production Deployment (Week 12)

**Deliverables**:
- ✅ Production environment setup
- ✅ Database backup/recovery
- ✅ Monitoring & alerting
- ✅ Documentation

**Deployment Checklist**:
```
Infrastructure:
  ☐ Production PostgreSQL (managed service)
  ☐ Production Redis (if needed)
  ☐ Production FastAPI servers (2+ replicas)
  ☐ Load balancer (Nginx or cloud LB)
  ☐ SSL/TLS certificates

Configuration:
  ☐ Environment variables
  ☐ Secrets management (AWS Secrets Manager)
  ☐ Database migrations applied
  ☐ API rate limiting configured
  ☐ CORS settings correct

Monitoring:
  ☐ Prometheus scraping working
  ☐ Grafana dashboards deployed
  ☐ Alert rules configured
  ☐ Log aggregation active
  ☐ Uptime monitoring

Security:
  ☐ SSL/TLS enforced
  ☐ CORS headers correct
  ☐ Rate limiting working
  ☐ Auth tokens validated
  ☐ Knuspr credentials encrypted

Backup & Recovery:
  ☐ Database backups automated (daily)
  ☐ Backup retention policy (30 days)
  ☐ Recovery test completed
  ☐ Disaster recovery plan documented

Documentation:
  ☐ API documentation (OpenAPI/Swagger)
  ☐ User guide
  ☐ Admin guide
  ☐ Runbook for incidents
  ☐ Release notes
```

**Post-Launch Monitoring**:
- Error rate tracking
- Performance monitoring
- User feedback monitoring
- Security audit logs

**Tasks**:
```
1. Set up production infrastructure
2. Configure auto-scaling
3. Set up database backups
4. Deploy all services
5. Run smoke tests
6. Monitor launch day closely
7. Be ready for rollback
8. Publish documentation
```

---

## Technical Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (Next.js 16 + React 19)            │
│   ┌────────────────────────────────────────────────┐   │
│   │ Auth | Recipes | MealPlan | Cart | Profile    │   │
│   └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓ (HTTPS)
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│   ┌────────────────────────────────────────────────┐   │
│   │ /api/v1/recipes  /auth  /mealplans  /carts   │   │
│   └────────────────────────────────────────────────┘   │
│                            ↓                             │
│   ┌──────────────────────────────────────────────┐    │
│   │           Agent Orchestration (LangGraph)     │    │
│   │  ┌─────────────┐  ┌────────────┐  ┌──────┐ │    │
│   │  │  Recipe     │  │ Ingredient │  │ Meal │ │    │
│   │  │ Harvester   │  │ Intelligence│  │Arch  │ │    │
│   │  └─────────────┘  └────────────┘  └──────┘ │    │
│   │  ┌──────────────────────────────────────┐  │    │
│   │  │   Cart Optimizer (Knuspr)           │  │    │
│   │  └──────────────────────────────────────┘  │    │
│   └──────────────────────────────────────────────┘    │
│                            ↓                             │
│   ┌──────────────────────────────────────────────┐    │
│   │         Event Bus (Redis Pub/Sub)             │    │
│   │    recipe.* | ingredient.* | mealplan.*     │    │
│   │    cart.* | *.failed (DLQ)                   │    │
│   └──────────────────────────────────────────────┘    │
│                            ↓                             │
│   ┌────────────────────────────────────────────────┐   │
│   │   PostgreSQL Database + Row-Level Security    │   │
│   │   users | recipes | meal_plans | carts        │   │
│   │   ingredient_taxonomy | knuspr_credentials    │   │
│   └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↓                                     ↓
    Prometheus (Metrics)              Knuspr API (MCP)
    Grafana (Dashboards)
    AlertManager (Alerts)
```

---

## Risk & Mitigation

### High-Risk Items

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Recipe parsing accuracy <90% | Medium | High | Start with Ottolenghi (simpler), add Claude for edge cases |
| Meal plan solver too slow (>5s) | Low | Medium | Benchmark early, optimize constraints, consider fallback greedy algorithm |
| Knuspr API instability | Low | High | Implement retries, cache products, provide manual list fallback |
| PostgreSQL data corruption | Very Low | Critical | Daily backups, WAL archiving, recovery testing |
| Multi-tenant data leak | Low | Critical | RLS policies, application checks, security audit before launch |

### Mitigation Strategies
1. **Early integration testing** - Test Knuspr MCP server in week 7
2. **Performance benchmarking** - Profile algorithms weekly
3. **Security audits** - External audit before launch
4. **Data validation** - Strict input validation, whitelist approaches

---

## Success Metrics (MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recipe harvest success | >90% | % of Ottolenghi URLs parsed successfully |
| Meal plan generation time | <5s | p99 latency for 7-day plan |
| API response time | <200ms | p99 latency across all endpoints |
| Code coverage | >80% | pytest coverage report |
| Error rate | <1% | Errors / total requests |
| Knuspr integration rate | 100% | Successful cart creations / attempts |
| User satisfaction | NPS >40 | Beta feedback score |
| Data security | 0 breaches | Security audit result |

---

## Next Steps

1. ✅ Complete specification and planning
2. ⏭️ Begin Phase 1A: Project setup (Week 1)
3. ⏭️ Daily standup on progress
4. ⏭️ Weekly demo of completed features

---

**Timeline**: 12 weeks (8-12 depending on team size and complexity)
**Team Size**: 2-3 developers recommended
**Budget Estimate**:
- Development: 8-12 person-weeks
- Infrastructure: ~$100-200/month (managed DB, compute)
- Anthropic API: ~$200-500/month (depends on usage)

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Next Review**: End of Phase 1 (Week 4)
