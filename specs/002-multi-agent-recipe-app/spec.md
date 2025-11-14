# Feature Specification: Multi-Agent Recipe and Meal Planning System

**Feature Branch**: `002-multi-agent-recipe-app`
**Created**: 2025-11-14
**Status**: Draft
**Input**: Multi-agent architecture for recipe harvesting, meal planning, and grocery optimization with Knuspr integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recipe Discovery and Import (Priority: P1)

A user wants to build a personal recipe collection from various online sources (blogs, recipe sites, RSS feeds) without manual data entry. The system automatically harvests, normalizes, and stores recipes in a consistent format.

**Why this priority**: This is the foundation of the entire system - without recipes, there's nothing to plan meals from or optimize grocery orders with. It delivers immediate value by eliminating tedious manual recipe entry.

**Independent Test**: Can be fully tested by providing URLs to recipe sources and verifying that recipes are correctly extracted, normalized, and stored with all key attributes (ingredients, steps, timing, servings).

**Acceptance Scenarios**:

1. **Given** a URL to a recipe blog post, **When** the user submits it to the harvester, **Then** the system extracts the recipe with ingredients, instructions, cooking time, and servings
2. **Given** an RSS feed of a cooking website, **When** the system polls the feed, **Then** new recipes are automatically discovered and added to the collection
3. **Given** a website with an API, **When** the API connector is configured, **Then** recipes are fetched via API calls with proper rate limiting
4. **Given** multiple recipe sources for the same recipe, **When** recipes are harvested, **Then** duplicates are detected and merged intelligently

---

### User Story 2 - Ingredient Intelligence and Substitution (Priority: P2)

A user wants to adapt recipes based on dietary preferences, seasonal availability, or pantry inventory. The system understands ingredient taxonomy and suggests appropriate substitutions.

**Why this priority**: This enables recipe flexibility and personalization, making the system useful beyond basic recipe storage. It addresses real cooking scenarios where exact ingredients may not be available.

**Independent Test**: Can be tested by selecting a recipe and requesting substitutions for specific ingredients, then verifying suggestions are semantically appropriate (e.g., suggesting olive oil for canola oil, not sugar for salt).

**Acceptance Scenarios**:

1. **Given** a recipe with dairy ingredients, **When** the user specifies a vegan diet, **Then** the system suggests plant-based alternatives with ratios
2. **Given** a recipe requiring out-of-season produce, **When** the user requests seasonal alternatives, **Then** the system suggests currently available ingredients
3. **Given** a recipe with a missing pantry ingredient, **When** the user marks it unavailable, **Then** the system suggests substitutions from their inventory
4. **Given** an ingredient substitution, **When** applied to a recipe, **Then** the system adjusts quantities and instructions where necessary

---

### User Story 3 - Automated Weekly Meal Planning (Priority: P2)

A user wants to generate a balanced weekly meal plan that considers dietary constraints, variety, preparation time, and ingredient reuse to minimize waste.

**Why this priority**: This is the core value proposition - turning a recipe collection into actionable meal plans. It requires Recipe Discovery (P1) but delivers significant time-saving value.

**Independent Test**: Can be tested by specifying weekly constraints (servings, dietary preferences, time budget) and verifying the generated plan meets all constraints while providing variety.

**Acceptance Scenarios**:

1. **Given** user constraints (4 dinners, 30-min max prep, vegetarian), **When** requesting a meal plan, **Then** the system generates a valid plan meeting all constraints
2. **Given** a generated meal plan, **When** reviewing ingredients, **Then** the system maximizes ingredient reuse across recipes to minimize waste
3. **Given** previous meal plans, **When** generating a new plan, **Then** the system ensures variety by avoiding recently used recipes
4. **Given** a meal plan, **When** the user dislikes a suggested recipe, **Then** the system regenerates with an alternative that maintains constraints

---

### User Story 4 - Knuspr Grocery Cart Optimization (Priority: P3)

A user wants to automatically generate an optimized Knuspr grocery order from their meal plan, with items grouped by store section and optimized for delivery slots.

**Why this priority**: This is the final convenience layer that connects meal planning to actual grocery procurement. It requires a working meal plan (P2) and adds delivery optimization value.

**Independent Test**: Can be tested by providing a meal plan and verifying the generated Knuspr cart contains all required ingredients, properly categorized, with delivery slot selection.

**Acceptance Scenarios**:

1. **Given** a weekly meal plan, **When** generating a grocery order, **Then** the system creates a Knuspr cart with all required ingredients
2. **Given** a Knuspr cart, **When** items are added, **Then** they are grouped by store section (produce, dairy, meat, etc.) for efficient shopping
3. **Given** multiple delivery slot options, **When** ordering, **Then** the system suggests the most cost-effective or earliest available slot
4. **Given** items out of stock at Knuspr, **When** building the cart, **Then** the system suggests alternatives or flags items for manual purchase

---

### User Story 5 - Agent Hot-Swapping and Scalability (Priority: P3)

A developer wants to upgrade individual agents (e.g., swap a basic ingredient parser for an ML-powered one) without system downtime or affecting other agents.

**Why this priority**: This is an architectural quality attribute that enables long-term maintainability and evolution. It's lower priority than user-facing features but critical for system sustainability.

**Independent Test**: Can be tested by deploying an agent update and verifying other agents continue functioning normally, with seamless capability handoff.

**Acceptance Scenarios**:

1. **Given** a running system with multiple agents, **When** deploying a new version of one agent, **Then** the system continues operating without downtime
2. **Given** a new agent with enhanced capabilities, **When** it registers its capability manifest, **Then** the orchestrator routes appropriate requests to it
3. **Given** multiple instances of the same agent type, **When** load increases, **Then** the system scales that agent independently without affecting others
4. **Given** an agent failure, **When** it stops responding, **Then** the system detects failure and routes requests to healthy instances

---

### Edge Cases

- What happens when recipe harvesting fails due to site changes or anti-scraping measures?
- How does the system handle recipes with ambiguous ingredient measurements (e.g., "a pinch of salt")?
- What happens when meal plan constraints are unsatisfiable (e.g., requesting 10 meals from a 5-recipe database)?
- How does the system handle Knuspr API rate limits or temporary unavailability?
- What happens when ingredient substitutions result in allergen exposure?
- How does the system handle multi-language recipes or regional ingredient variations?
- What happens when an agent fails during a multi-agent workflow?
- How does the system handle event bus message loss or ordering issues?

## Requirements *(mandatory)*

### Functional Requirements

#### Recipe Harvesting
- **FR-001**: System MUST harvest recipes from web pages using Puppeteer-based scraping with schema.org/Recipe detection
- **FR-002**: System MUST harvest recipes from API endpoints with configurable connectors and rate limiting
- **FR-003**: System MUST harvest recipes from RSS feeds with periodic polling
- **FR-004**: System MUST normalize harvested recipes into a canonical data model (title, ingredients with quantities/units, instructions, metadata)
- **FR-005**: System MUST detect duplicate recipes using title similarity and ingredient overlap
- **FR-006**: System MUST handle harvesting failures gracefully and retry with exponential backoff

#### Ingredient Intelligence
- **FR-007**: System MUST maintain a food taxonomy mapping ingredients to categories (dairy, protein, vegetables, etc.)
- **FR-008**: System MUST suggest ingredient substitutions based on dietary preferences (vegan, vegetarian, gluten-free, etc.)
- **FR-009**: System MUST suggest ingredient substitutions based on seasonal availability
- **FR-010**: System MUST suggest ingredient substitutions based on user pantry inventory
- **FR-011**: System MUST calculate substitution ratios and adjust recipe quantities accordingly
- **FR-012**: System MUST flag potential allergen issues when suggesting substitutions

#### Meal Planning
- **FR-013**: System MUST generate weekly meal plans based on user constraints (number of meals, dietary preferences, time budget)
- **FR-014**: System MUST use constraint satisfaction algorithms to ensure plan validity
- **FR-015**: System MUST maximize ingredient reuse across recipes to minimize waste
- **FR-016**: System MUST ensure variety by avoiding recently used recipes (configurable lookback period)
- **FR-017**: System MUST allow users to regenerate individual meals while maintaining overall plan constraints
- **FR-018**: System MUST persist meal plans for future reference and shopping

#### Grocery Cart Optimization
- **FR-019**: System MUST integrate with Knuspr API to create grocery carts
- **FR-020**: System MUST aggregate ingredients from multiple recipes and eliminate duplicates
- **FR-021**: System MUST group cart items by store section for efficient shopping
- **FR-022**: System MUST suggest optimal delivery slots based on availability and user preferences
- **FR-023**: System MUST handle out-of-stock items by suggesting alternatives or flagging for manual purchase
- **FR-024**: System MUST track cart pricing and provide cost estimates

#### Agent Architecture
- **FR-025**: System MUST implement agents as independent, single-purpose entities with clear responsibilities
- **FR-026**: System MUST use an event bus for inter-agent communication (Phase 1: Redis Pub/Sub or FastAPI background tasks; Phase 2+: NATS or RabbitMQ for higher throughput)
- **FR-027**: System MUST require each agent to expose a capability manifest describing its functions
- **FR-028**: System MUST use LangGraph or CrewAI for orchestrating multi-agent workflows
- **FR-029**: System MUST deploy agents as separate containers for independent scaling
- **FR-030**: System MUST support hot-swapping agents without system downtime
- **FR-031**: System MUST implement health checks and automatic failover for agent failures

### Key Entities *(include if feature involves data)*

- **Recipe**: Represents a cooking recipe with title, source URL, ingredients (with quantities and units), instructions, cooking/prep time, servings, dietary tags, and harvesting metadata
- **Ingredient**: Represents a food item with name, category, taxonomy classification, common substitutes, allergen information, and seasonal availability
- **MealPlan**: Represents a weekly plan with selected recipes, target dates, serving adjustments, and constraint parameters
- **GroceryCart**: Represents a Knuspr order with ingredients, quantities, store sections, pricing, delivery slot, and order status
- **Agent**: Represents a system agent with ID, type (harvester/intelligence/architect/optimizer), capability manifest, health status, and container instance
- **UserProfile**: Represents user preferences with dietary restrictions, pantry inventory, favorite recipes, meal history, and delivery preferences

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Recipe Harvester agents successfully extract and normalize 90%+ of recipes from top 50 cooking websites
- **SC-002**: Ingredient Intelligence agents provide valid substitutions with 95%+ user acceptance rate
- **SC-003**: Meal Architect generates valid plans satisfying all constraints in <5 seconds for a 7-day plan
- **SC-004**: Cart Optimizer successfully creates Knuspr orders with 100% ingredient coverage for available items
- **SC-005**: System handles hot-swapping of individual agents with <1 second disruption to other agents
- **SC-006**: Individual agent types can scale independently to handle 10x load increase in their domain
- **SC-007**: Users can complete the full workflow (recipe discovery → meal planning → grocery order) in <10 minutes
- **SC-008**: System reduces meal planning time by 80% compared to manual planning (target: 5 min vs 25 min)
- **SC-009**: System reduces food waste by 30% through intelligent ingredient reuse across recipes
- **SC-010**: Event bus handles 1000+ messages/second with <100ms latency between agent communications

## Technical Approach Summary

### Architecture Overview

The system follows a **multi-agent swarm architecture** where specialized agents communicate via an event bus:

1. **Recipe Harvester Agents**: Multiple strategies (Puppeteer scraper, API connectors, RSS parsers) compete to harvest recipes
2. **Ingredient Intelligence Agents**: Understand food taxonomy and provide substitution logic
3. **Meal Architect Agent**: Orchestrates meal planning using constraint satisfaction
4. **Cart Optimizer Agents**: Interface with Knuspr API and optimize delivery

### Key Design Principles

- **Lego Modularity**: Each agent is independently deployable and replaceable
- **Event-Driven**: Agents communicate through pub/sub on event bus (Phase 1: Redis Pub/Sub, Phase 2+: NATS/RabbitMQ for production scale)
- **Capability Manifests**: Agents expose their capabilities for dynamic routing
- **Orchestration**: LangGraph or CrewAI manages complex multi-agent workflows
- **Containerization**: Each agent runs in its own container for independent scaling

### Technology Stack

**Core Agent & AI Stack**:
- **Agent Orchestration**: LangChain/LangGraph
- **Agent Framework**: PydanticAI + AtomicAgents
- **AI Models**: Anthropic Claude (ingredient intelligence, recipe analysis)
- **Production Deployment**: Docker Compose (Phase 1), Kubernetes with Agno + Google ADK evaluation (Phase 2+)

**Backend Infrastructure**:
- **API Framework**: FastAPI (Python)
- **Data Storage**: PostgreSQL (primary)
- **Message Queue/Cache**: Redis (prepared for future stages)
- **Containerization**: Docker
- **Monitoring**: Prometheus (for performance measurement)

**Supporting Services**:
- **Event Bus**: Redis Pub/Sub or FastAPI background tasks (Phase 1), Redis Streams/RabbitMQ (Phase 2+)
- **Recipe Harvesting**: Puppeteer (browser automation), Axios (HTTP), feedparser (RSS)
- **Constraint Solver**: Z3 (Phase 1), OR-Tools evaluation for Phase 2 optimization
- **API Integration**: Knuspr MCP Server (experimental), Knuspr REST client

**Frontend**:
- **UI Framework**: TBD in planning phase (mobile-first)
- **CLI**: TBD in planning phase (optional for power users)

## Open Questions - RESOLVED ✅

1. **Authentication**: Users authenticate with Knuspr using login credentials as documented in the projects README. System supports per-user credentials and country selection.
2. **Data Storage**: PostgreSQL for primary data store. Redis preparation for future stages (caching, message queuing).
3. **ML Integration**: Using Anthropic Claude models for ingredient intelligence and AI-powered features.
4. **Recipe Sources**: Starting with publicly available Ottolenghi recipes as primary source.
5. **Deployment**: Multi-tenant SaaS tool with monthly subscription model.
6. **UI**: Web-based with mobile-first approach. Optional CLI for power users.
7. **Cost Model**: Users pay Knuspr delivery fees directly through the Knuspr app. System only adds items to user's cart.
8. **Scaling Requirements**: Initial target: 10 concurrent users. Performance monitoring setup required (Prometheus) for future scaling analysis.
