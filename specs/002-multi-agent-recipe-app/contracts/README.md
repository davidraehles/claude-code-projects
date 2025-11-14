# Agent Contracts & Interfaces

**Feature**: Multi-Agent Recipe and Meal Planning System
**Date**: 2025-11-14

## Overview

This directory contains interface contracts and capability manifests for the multi-agent system. Each agent type exposes a well-defined contract that describes its capabilities, input/output formats, and event patterns.

## Agent Types

### 1. Recipe Harvester Agents

**Purpose**: Scrape, normalize, and store recipes from various sources (FR-001 to FR-006)

**Agent Variants**:
- `harvester-puppeteer`: Browser automation for dynamic recipe sites
- `harvester-api`: Direct API connectors for supported platforms
- `harvester-rss`: RSS/Atom feed polling for recipe blogs

**Capability Manifest**:
```json
{
  "agentId": "harvester-puppeteer-01",
  "agentType": "recipe-harvester",
  "version": "1.0.0",
  "capabilities": [
    "harvest.web.puppeteer",
    "harvest.schema-org",
    "harvest.microdata"
  ],
  "inputEvents": [
    "recipe.harvest.requested"
  ],
  "outputEvents": [
    "recipe.harvested.success",
    "recipe.harvested.failed"
  ],
  "configuration": {
    "maxConcurrentScrapes": 5,
    "timeout": 30000,
    "retryAttempts": 3
  }
}
```

**Event Contracts**:

**Input**: `recipe.harvest.requested`
```json
{
  "eventType": "recipe.harvest.requested",
  "timestamp": "2025-11-14T10:30:00Z",
  "payload": {
    "sourceUrl": "https://example.com/recipe/chocolate-cake",
    "sourceType": "web",
    "priority": "normal",
    "requestId": "uuid-here"
  }
}
```

**Output**: `recipe.harvested.success`
```json
{
  "eventType": "recipe.harvested.success",
  "timestamp": "2025-11-14T10:30:15Z",
  "payload": {
    "requestId": "uuid-here",
    "recipe": {
      "title": "Classic Chocolate Cake",
      "sourceUrl": "https://example.com/recipe/chocolate-cake",
      "ingredients": [
        {
          "item": "all-purpose flour",
          "quantity": 2,
          "unit": "cups",
          "notes": "sifted"
        }
      ],
      "instructions": [
        "Preheat oven to 350°F...",
        "Mix dry ingredients..."
      ],
      "prepTime": 20,
      "cookTime": 35,
      "servings": 8,
      "metadata": {
        "harvestMethod": "puppeteer",
        "harvestTimestamp": "2025-11-14T10:30:15Z",
        "schemaOrgFound": true
      }
    }
  }
}
```

**Output**: `recipe.harvested.failed`
```json
{
  "eventType": "recipe.harvested.failed",
  "timestamp": "2025-11-14T10:30:10Z",
  "payload": {
    "requestId": "uuid-here",
    "sourceUrl": "https://example.com/recipe/chocolate-cake",
    "error": "Timeout after 30s",
    "retryable": true,
    "attemptNumber": 1
  }
}
```

---

### 2. Ingredient Intelligence Agents

**Purpose**: Understand food taxonomy and suggest ingredient substitutions (FR-007 to FR-012)

**Agent Variants**:
- `intelligence-taxonomy`: Basic rule-based ingredient classification
- `intelligence-ml`: ML-powered ingredient understanding
- `intelligence-seasonal`: Seasonal availability tracking

**Capability Manifest**:
```json
{
  "agentId": "intelligence-taxonomy-01",
  "agentType": "ingredient-intelligence",
  "version": "1.0.0",
  "capabilities": [
    "ingredient.classify",
    "ingredient.substitute",
    "ingredient.allergen-check"
  ],
  "inputEvents": [
    "ingredient.substitution.requested",
    "ingredient.classification.requested"
  ],
  "outputEvents": [
    "ingredient.substitution.suggestions",
    "ingredient.classification.complete"
  ]
}
```

**Event Contracts**:

**Input**: `ingredient.substitution.requested`
```json
{
  "eventType": "ingredient.substitution.requested",
  "timestamp": "2025-11-14T10:35:00Z",
  "payload": {
    "ingredient": "butter",
    "quantity": 1,
    "unit": "cup",
    "context": {
      "recipeId": "recipe-123",
      "recipeType": "baking",
      "dietaryConstraints": ["vegan"],
      "pantryInventory": ["olive oil", "coconut oil", "margarine"],
      "seasonalPreference": true
    },
    "requestId": "uuid-here"
  }
}
```

**Output**: `ingredient.substitution.suggestions`
```json
{
  "eventType": "ingredient.substitution.suggestions",
  "timestamp": "2025-11-14T10:35:01Z",
  "payload": {
    "requestId": "uuid-here",
    "originalIngredient": "butter",
    "suggestions": [
      {
        "ingredient": "coconut oil",
        "quantity": 0.75,
        "unit": "cup",
        "confidence": 0.95,
        "reason": "Available in pantry, vegan, suitable for baking",
        "adjustments": "Reduce quantity by 25% due to higher fat content",
        "allergenWarnings": ["tree nut"]
      },
      {
        "ingredient": "margarine",
        "quantity": 1,
        "unit": "cup",
        "confidence": 0.85,
        "reason": "Available in pantry, vegan, 1:1 substitution",
        "adjustments": null,
        "allergenWarnings": []
      }
    ]
  }
}
```

---

### 3. Meal Architect Agent

**Purpose**: Generate weekly meal plans using constraint satisfaction (FR-013 to FR-018)

**Capability Manifest**:
```json
{
  "agentId": "architect-planner-01",
  "agentType": "meal-architect",
  "version": "1.0.0",
  "capabilities": [
    "mealplan.generate",
    "mealplan.optimize",
    "mealplan.regenerate-meal"
  ],
  "inputEvents": [
    "mealplan.generation.requested",
    "mealplan.regenerate.requested"
  ],
  "outputEvents": [
    "mealplan.generated",
    "mealplan.generation.failed"
  ],
  "configuration": {
    "constraintSolver": "z3",
    "maxSolveTime": 10000,
    "varietyLookback": 14
  }
}
```

**Event Contracts**:

**Input**: `mealplan.generation.requested`
```json
{
  "eventType": "mealplan.generation.requested",
  "timestamp": "2025-11-14T10:40:00Z",
  "payload": {
    "userId": "user-456",
    "constraints": {
      "numberOfMeals": 7,
      "mealTypes": ["dinner"],
      "servingsPerMeal": 4,
      "maxPrepTimeMinutes": 45,
      "maxCookTimeMinutes": 60,
      "dietaryPreferences": ["vegetarian"],
      "excludeIngredients": ["mushrooms"],
      "varietyLookbackDays": 14
    },
    "startDate": "2025-11-18",
    "requestId": "uuid-here"
  }
}
```

**Output**: `mealplan.generated`
```json
{
  "eventType": "mealplan.generated",
  "timestamp": "2025-11-14T10:40:04Z",
  "payload": {
    "requestId": "uuid-here",
    "mealPlanId": "plan-789",
    "userId": "user-456",
    "plan": {
      "startDate": "2025-11-18",
      "endDate": "2025-11-24",
      "meals": [
        {
          "date": "2025-11-18",
          "mealType": "dinner",
          "recipeId": "recipe-123",
          "recipeName": "Vegetarian Chili",
          "servings": 4,
          "prepTime": 15,
          "cookTime": 30
        }
      ],
      "aggregatedIngredients": [
        {
          "ingredient": "kidney beans",
          "totalQuantity": 4,
          "unit": "cans",
          "usedInRecipes": ["recipe-123", "recipe-456"]
        }
      ],
      "metrics": {
        "totalPrepTime": 180,
        "totalCookTime": 310,
        "ingredientReusePct": 0.35,
        "varietyScore": 0.92
      }
    }
  }
}
```

---

### 4. Cart Optimizer Agents

**Purpose**: Interface with Knuspr API and optimize grocery carts (FR-019 to FR-024)

**Capability Manifest**:
```json
{
  "agentId": "optimizer-knuspr-01",
  "agentType": "cart-optimizer",
  "version": "1.0.0",
  "capabilities": [
    "cart.create",
    "cart.optimize-sections",
    "cart.delivery-slot-selection"
  ],
  "inputEvents": [
    "cart.creation.requested"
  ],
  "outputEvents": [
    "cart.created",
    "cart.creation.failed"
  ],
  "configuration": {
    "apiEndpoint": "https://api.knuspr.de/v1",
    "rateLimit": 10,
    "deliveryPreference": "earliest"
  }
}
```

**Event Contracts**:

**Input**: `cart.creation.requested`
```json
{
  "eventType": "cart.creation.requested",
  "timestamp": "2025-11-14T10:45:00Z",
  "payload": {
    "userId": "user-456",
    "mealPlanId": "plan-789",
    "ingredients": [
      {
        "ingredient": "kidney beans",
        "quantity": 4,
        "unit": "cans"
      }
    ],
    "deliveryPreferences": {
      "preferredDates": ["2025-11-17", "2025-11-18"],
      "preferredTimeSlot": "evening",
      "minDeliveryDate": "2025-11-17"
    },
    "requestId": "uuid-here"
  }
}
```

**Output**: `cart.created`
```json
{
  "eventType": "cart.created",
  "timestamp": "2025-11-14T10:45:05Z",
  "payload": {
    "requestId": "uuid-here",
    "cartId": "cart-321",
    "knusprOrderId": "order-654",
    "items": [
      {
        "ingredient": "kidney beans",
        "knusprProductId": "prod-123",
        "productName": "Organic Kidney Beans 400g",
        "quantity": 4,
        "unitPrice": 1.99,
        "totalPrice": 7.96,
        "storeSection": "canned-goods",
        "availability": "in-stock"
      }
    ],
    "itemsGroupedBySection": {
      "produce": [],
      "dairy": [],
      "canned-goods": ["prod-123"],
      "meat": []
    },
    "deliverySlot": {
      "date": "2025-11-17",
      "timeWindow": "18:00-20:00",
      "cost": 4.99
    },
    "pricing": {
      "subtotal": 52.34,
      "delivery": 4.99,
      "total": 57.33
    },
    "unavailableItems": []
  }
}
```

---

## Event Bus Schema

All agents communicate through an event bus (NATS or RabbitMQ) using the following patterns:

### Event Envelope Format

Every event follows this structure:
```json
{
  "eventType": "domain.entity.action",
  "eventId": "uuid-v4",
  "timestamp": "ISO-8601",
  "correlationId": "uuid-for-request-tracing",
  "source": {
    "agentId": "agent-identifier",
    "agentType": "agent-type",
    "version": "semver"
  },
  "payload": {
    // Event-specific data
  },
  "metadata": {
    "retryCount": 0,
    "priority": "normal",
    "ttl": 3600
  }
}
```

### Event Naming Convention

Events follow the pattern: `{domain}.{entity}.{action}`

Examples:
- `recipe.harvest.requested`
- `recipe.harvested.success`
- `ingredient.substitution.requested`
- `mealplan.generation.requested`
- `cart.created`

### Topics and Subscriptions

```
recipe.*                 → Recipe Harvester Agents subscribe
ingredient.*             → Ingredient Intelligence Agents subscribe
mealplan.*               → Meal Architect Agent subscribes
cart.*                   → Cart Optimizer Agents subscribe
*.*.failed               → Error Handler subscribes (dead letter queue)
```

---

## Orchestration Workflows

Complex multi-agent workflows are coordinated using LangGraph or CrewAI.

### Example: Full Meal Planning Flow

```yaml
workflow: weekly-meal-plan-with-groceries
steps:
  - name: generate-meal-plan
    agent: meal-architect
    input: user-constraints
    output: meal-plan

  - name: check-ingredient-availability
    agent: ingredient-intelligence
    input: meal-plan.ingredients
    output: availability-report

  - name: substitute-unavailable
    agent: ingredient-intelligence
    input: availability-report.unavailable
    output: substitutions
    conditional: if unavailable items exist

  - name: create-grocery-cart
    agent: cart-optimizer
    input: meal-plan.ingredients + substitutions
    output: knuspr-cart

  - name: notify-user
    agent: notification-service
    input: meal-plan + knuspr-cart
    output: success
```

---

## Health Check Contract

All agents must implement a health check endpoint:

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "agentId": "harvester-puppeteer-01",
  "agentType": "recipe-harvester",
  "version": "1.0.0",
  "uptime": 3600,
  "metrics": {
    "requestsProcessed": 142,
    "requestsFailed": 3,
    "averageProcessingTime": 1250
  },
  "dependencies": [
    {
      "name": "event-bus",
      "status": "healthy"
    },
    {
      "name": "database",
      "status": "healthy"
    }
  ],
  "timestamp": "2025-11-14T10:50:00Z"
}
```

---

## API Gateway (Optional)

If exposing agents via HTTP API:

### Recipe Harvesting
```
POST /api/v1/recipes/harvest
Content-Type: application/json

{
  "sourceUrl": "https://example.com/recipe/chocolate-cake",
  "priority": "high"
}
```

### Meal Planning
```
POST /api/v1/mealplans
Content-Type: application/json

{
  "constraints": {...},
  "startDate": "2025-11-18"
}
```

### Cart Creation
```
POST /api/v1/carts
Content-Type: application/json

{
  "mealPlanId": "plan-789",
  "deliveryPreferences": {...}
}
```

---

## Testing Contracts

### Contract Testing

Use tools like Pact or Postman to verify agent contracts:

```bash
# Validate agent capability manifests
npm run test:contracts

# Test event schema compliance
npm run test:events

# Integration test workflows
npm run test:workflows
```

### Example Test

```typescript
import { describe, it, expect } from 'vitest';
import { validateEvent } from './lib/event-validator';
import { recipeHarvestSuccessSchema } from './contracts/schemas';

describe('Recipe Harvester Events', () => {
  it('validates recipe.harvested.success event schema', () => {
    const event = {
      eventType: 'recipe.harvested.success',
      timestamp: '2025-11-14T10:30:15Z',
      payload: {
        requestId: 'uuid-123',
        recipe: { /* ... */ }
      }
    };

    const result = validateEvent(event, recipeHarvestSuccessSchema);
    expect(result.valid).toBe(true);
  });
});
```

---

## Security Considerations

1. **Agent Authentication**: Each agent authenticates with the event bus using mTLS certificates
2. **Event Validation**: All events validated against JSON schemas before processing
3. **Rate Limiting**: Per-agent rate limits to prevent runaway agents
4. **Dead Letter Queue**: Failed events routed to DLQ for investigation
5. **Audit Trail**: All agent actions logged with correlation IDs

---

## Next Steps

1. Implement capability manifest for each agent type
2. Define JSON schemas for all event types
3. Set up event bus (NATS/RabbitMQ) with topic routing
4. Implement health check endpoints
5. Create contract testing suite
6. Document orchestration workflows in LangGraph/CrewAI

---

**References**:
- [Specification](../spec.md)
- [Data Model](../data-model.md) (to be created)
- [Implementation Plan](../plan.md) (to be created)
