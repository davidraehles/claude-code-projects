---
title: Feature Specification - Multi-Agent Recipe and Meal Planning System
version: 1.0.0
date_created: 2025-11-14
last_updated: 2025-12-15
owner: Meal Planner Team
tags: [app, design, process, ai, automation]
---

# Introduction

This specification defines the requirements and architecture for the Multi-Agent Recipe and Meal Planning System. This system leverages a multi-agent architecture to automate the entire meal planning lifecycle: from harvesting recipes from the web, to generating personalized weekly meal plans, and finally optimizing grocery lists for seamless integration with the Knuspr delivery service.

## 1. Purpose & Scope

The purpose of this specification is to outline the functional and non-functional requirements for the "Go, Cart!" application's core AI features.

**Scope:**
- **Recipe Harvesting**: Automated extraction and normalization of recipes from various web sources.
- **Ingredient Intelligence**: Understanding ingredient taxonomy, substitutions, and dietary attributes.
- **Meal Planning**: AI-driven generation of weekly meal plans based on user preferences and constraints.
- **Cart Optimization**: Intelligent mapping of meal plan ingredients to Knuspr store items, optimizing for cost and availability.
- **Agent Architecture**: A scalable, modular multi-agent system using LangGraph.

**Out of Scope:**
- Payment processing (handled by Knuspr).
- Physical delivery logistics.
- Social sharing features (Phase 2).

## 2. Definitions

- **Knuspr**: A grocery delivery service (known as Rohlik in other markets) that serves as the primary integration target for grocery fulfillment.
- **Agent**: An autonomous software unit responsible for a specific domain of tasks (e.g., Recipe Harvester, Meal Architect).
- **MCP (Model Context Protocol)**: A standard for connecting AI models to external tools and data sources.
- **LangGraph**: A library for building stateful, multi-actor applications with LLMs, used to orchestrate the agents.
- **Harvester**: The agent responsible for scraping and parsing recipes.
- **Architect**: The agent responsible for generating meal plans.
- **Optimizer**: The agent responsible for converting ingredients into a shopping cart.

## 3. Requirements, Constraints & Guidelines

### Functional Requirements

- **REQ-001**: **Recipe Discovery and Import**
  - The system must allow users to import recipes via URL.
  - The system must automatically extract ingredients, instructions, prep time, cook time, and servings.
  - The system must support RSS feed polling for automated discovery.
- **REQ-002**: **Ingredient Intelligence and Substitution**
  - The system must suggest ingredient substitutions based on dietary restrictions (e.g., vegan, gluten-free).
  - The system must identify seasonal ingredients and suggest alternatives.
- **REQ-003**: **Automated Weekly Meal Planning**
  - The system must generate a 7-day meal plan based on user preferences (e.g., "4 dinners, vegetarian, under 30 mins").
  - The system must minimize food waste by reusing ingredients across recipes in a plan.
- **REQ-004**: **Knuspr Grocery Cart Optimization**
  - The system must convert a meal plan into a Knuspr shopping cart.
  - The system must group items by store section.
  - The system must handle out-of-stock items by suggesting alternatives.
- **REQ-005**: **Agent Hot-Swapping**
  - The system must allow individual agents to be updated or replaced without system downtime.

### Constraints

- **CON-001**: Backend must be built with **Python 3.11+** and **FastAPI**.
- **CON-002**: Frontend must be built with **Next.js 16** and **React 19**.
- **CON-003**: Database must be **PostgreSQL 16+**.
- **CON-004**: Application must be **WCAG 2.1 AAA** compliant.
- **CON-005**: All external API integrations (Knuspr) must handle rate limiting and authentication securely.

### Guidelines

- **GUD-001**: Follow the "Library-First Architecture" for backend packages.
- **GUD-002**: Use Pydantic V2 for all data validation.
- **GUD-003**: Ensure all UI components are responsive and support 60fps animations.

## 4. Interfaces & Data Contracts

### Core Entities (Simplified)

**User**
```typescript
interface User {
  id: number;
  email: string;
  preferences: UserPreferences;
  subscriptionTier: 'free' | 'basic' | 'premium';
}
```

**Recipe**
```typescript
interface Recipe {
  id: number;
  title: string;
  sourceUrl: string;
  ingredients: Ingredient[];
  instructions: Step[];
  dietaryTags: string[];
}
```

**MealPlan**
```typescript
interface MealPlan {
  id: number;
  userId: number;
  startDate: string;
  days: MealPlanDay[];
  status: 'draft' | 'active' | 'completed';
}
```

### API Endpoints

- `POST /api/v1/recipes/harvest`: Submit a URL for harvesting.
- `POST /api/v1/plans/generate`: Generate a new meal plan.
- `POST /api/v1/cart/knuspr/sync`: Sync a meal plan to a Knuspr cart.

## 5. Acceptance Criteria

- **AC-001**: Given a valid recipe URL, When submitted to the harvester, Then the recipe is saved with >90% accuracy for ingredients and instructions.
- **AC-002**: Given a user with "Vegan" preference, When generating a meal plan, Then no recipes with animal products are included.
- **AC-003**: Given a generated meal plan, When "Create Cart" is clicked, Then a Knuspr cart is created with all necessary ingredients matched to available products.
- **AC-004**: Given an out-of-stock item at Knuspr, When syncing the cart, Then the system prompts the user with a valid alternative product.
- **AC-005**: The system shall support concurrent usage by at least 10 users without performance degradation.

## 6. Test Automation Strategy

- **Test Levels**:
  - **Unit Tests**: Python `pytest` for backend logic, Jest for frontend components.
  - **Integration Tests**: API endpoint testing with `pytest-asyncio` and test database.
  - **End-to-End Tests**: Playwright tests for critical user journeys (Login -> Plan -> Cart).
- **Coverage Requirements**: Minimum 80% code coverage for backend and frontend.
- **Performance Testing**: Lighthouse CI for frontend performance and accessibility; `locust` for API load testing.
- **CI/CD Integration**: Tests run on every Pull Request via GitHub Actions.

## 7. Rationale & Context

The decision to use a multi-agent architecture is driven by the need for specialized intelligence in distinct domains (harvesting vs. planning vs. shopping). This allows for independent scaling and evolution of each capability.

The integration with Knuspr is a key differentiator, providing a seamless "plan to plate" experience that competitors lack.

## 8. Dependencies & External Integrations

### External Systems
- **EXT-001**: **Knuspr (Rohlik) API** - Required for product search, cart management, and checkout.
- **EXT-002**: **OpenAI API** - Required for LLM capabilities (GPT-4o) used by agents.

### Infrastructure Dependencies
- **INF-001**: **PostgreSQL** - Primary relational database.
- **INF-002**: **Redis** - Caching and message broker for agents.
- **INF-003**: **Docker** - Containerization for consistent deployment.

## 9. Examples & Edge Cases

**Edge Case: Recipe with no clear ingredients list**
If the harvester encounters a page where ingredients are unstructured text, it should attempt to use the LLM to parse it. If confidence is low, it should flag the recipe for manual review.

**Edge Case: Knuspr API downtime**
If the Knuspr API is unavailable, the system should allow the user to export the shopping list as a text file or email, and retry the sync later.

## 10. Validation Criteria

- All **P1** and **P2** user stories must be implemented and verified.
- **Lighthouse Performance Score** must be > 95 on key pages.
- **Accessibility Audit** must show 0 critical violations (WCAG 2.1 AA).
- **Security Audit** must pass with no high-severity vulnerabilities.

## 11. Related Specifications / Further Reading

- [Architecture Documentation](../../docs/architecture.md)
- [Data Model Specification](./data-model.md)
- [Implementation Plan](./plan.md)


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
- **UI Framework**: Next.js 16 + React 19 (mobile-first)
- **CLI**: Mandatory for all core agents (Harvester, Architect, Optimizer) to ensure library-first testability and independent operation.

## Open Questions - RESOLVED ✅

1. **Authentication**: Users authenticate with Knuspr using login credentials as documented in the projects README. System supports per-user credentials and country selection.
2. **Data Storage**: PostgreSQL for primary data store. Redis preparation for future stages (caching, message queuing).
3. **ML Integration**: Using Anthropic Claude models for ingredient intelligence and AI-powered features.
4. **Recipe Sources**: Starting with publicly available Ottolenghi recipes as primary source.
5. **Deployment**: Multi-tenant SaaS tool with monthly subscription model.
6. **UI**: Web-based with mobile-first approach. Optional CLI for power users.
7. **Cost Model**: Users pay Knuspr delivery fees directly through the Knuspr app. System only adds items to user's cart.
8. **Scaling Requirements**: Initial target: 10 concurrent users. Performance monitoring setup required (Prometheus) for future scaling analysis.
