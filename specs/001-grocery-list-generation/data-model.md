# Data Model: Grocery List Generation

**Feature**: 001-grocery-list-generation
**Date**: 2025-11-29
**Status**: Phase 1 - Design

## Overview

This document defines the data structures needed for grocery list generation. Most entities already exist in the database - this feature primarily adds relationships and computed properties rather than new tables.

---

## Existing Entities (Reused)

### User
**Source**: `backend/app/models/user.py`

```python
class User(Base):
    id: int
    email: str
    password_hash: str
    country: str  # For Knuspr domain mapping
    created_at: datetime
```

**Relationships**:
- `user.meal_plans` → `MealPlan[]`
- `user.grocery_carts` → `GroceryCart[]`
- `user.knuspr_credentials` → `KnusprCredential[]`

---

### Recipe
**Source**: `backend/app/models/recipe.py`

```python
class Recipe(Base):
    id: int
    user_id: int
    title: str
    ingredients: JSON  # ["1 cup flour", "2 tbsp sugar"]
    instructions: str
    prep_time: int | None
    cook_time: int | None
    servings: int | None
    dietary_tags: List[str] | None
    nutrition: JSON | None  # {calories, protein, carbs, fat}
    source_url: str | None
    created_at: datetime
```

**Usage in Feature**:
- Parse `ingredients` JSON array to extract quantities
- Sum quantities across recipes in meal plan
- Track which recipes contribute each ingredient

---

### MealPlan
**Source**: `backend/app/models/meal_plan.py`

```python
class MealPlan(Base):
    id: int
    user_id: int
    name: str
    start_date: date
    end_date: date
    num_days: int
    num_people: int
    meals_per_day: int
    dietary_restrictions: List[str] | None
    excluded_ingredients: List[str] | None
    status: str  # "generating" | "ready" | "failed"
    created_at: datetime
```

**Relationships**:
- `meal_plan.recipes` → `MealPlanRecipe[]` → `Recipe[]`
- `meal_plan.grocery_carts` → `GroceryCart[]`

**Usage in Feature**:
- Source of recipes for aggregation
- `num_people` used for quantity scaling
- Basis for cart creation

---

### MealPlanRecipe (Join Table)
**Source**: `backend/app/models/meal_plan.py`

```python
class MealPlanRecipe(Base):
    id: int
    meal_plan_id: int
    recipe_id: int
    day_number: int
    meal_type: str  # "breakfast" | "lunch" | "dinner"
    scheduled_date: date
    servings: int  # Scaled for num_people
```

**Usage in Feature**:
- Determines which recipes are in a meal plan
- `servings` field used for quantity scaling

---

### Ingredient (Reference Table)
**Source**: `backend/app/models/ingredient.py`

```python
class Ingredient(Base):
    id: int
    name: str  # Normalized name (lowercase, singular)
    aliases: JSON  # ["tomato", "tomatoes", "roma tomato"]
    category: str  # "Produce" | "Dairy" | etc.
    unit_conversions: JSON  # {"cup": 240, "tbsp": 15} (ml)
    nutrition_per_100g: JSON | None
```

**Usage in Feature**:
- Normalize ingredient names via `aliases`
- Assign category for categorization view
- Convert units via `unit_conversions`

---

## Modified Entities

### GroceryCart
**Source**: `backend/app/models/grocery_cart.py`
**Changes**: None to schema, but endpoints now create real carts instead of mocks

```python
class GroceryCart(Base):
    id: int
    user_id: int
    meal_plan_id: int | None  # Links to source meal plan
    status: str  # "active" | "ordered" | "completed"
    knuspr_cart_id: str | None  # External Knuspr cart reference
    knuspr_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- `cart.items` → `CartItem[]`
- `cart.meal_plan` → `MealPlan`

---

### CartItem (MODIFIED)
**Source**: `backend/app/models/grocery_cart.py`
**Changes**: Add `recipe_ids` field to track ingredient sources

```python
class CartItem(Base):
    id: int
    cart_id: int
    ingredient_id: int | None  # Reference to Ingredient table
    ingredient_name: str  # Display name (e.g., "Flour")
    quantity: float
    unit: str  # "ml", "g", "pcs", "cup", etc.
    category: str  # "Produce", "Dairy", etc.
    estimated_cost: float | None
    knuspr_product_id: str | None
    recipe_ids: JSON  # NEW: [1, 3, 7] - recipe IDs that need this ingredient
```

**New Field**:
```python
# Migration
def upgrade():
    op.add_column('cart_items',
        sa.Column('recipe_ids', sa.JSON(), nullable=True, server_default='[]'))
```

**Purpose of `recipe_ids`**:
- Track which recipes contribute to this ingredient
- Display in UI: "Flour (from Pancakes, Bread, Cookies)"
- Support recipe view mode (group by recipe instead of category)

---

## New Entities

### AggregatedIngredient (Computed, Not Stored)
**Usage**: Intermediate data structure during aggregation, not persisted

```python
@dataclass
class AggregatedIngredient:
    """
    Represents a single ingredient aggregated from multiple recipes.
    Created during cart generation, converted to CartItem for storage.
    """
    name: str  # Normalized ingredient name
    total_quantity: float  # Sum of all quantities
    unit: str  # Standard unit (ml, g, pcs)
    category: str
    sources: List[RecipeSource]  # Which recipes contribute this ingredient

@dataclass
class RecipeSource:
    """Details about one recipe's contribution to an ingredient."""
    recipe_id: int
    recipe_title: str
    quantity: float
    unit: str  # Original unit from recipe
```

**Example**:
```python
AggregatedIngredient(
    name="flour",
    total_quantity=720,  # ml (converted from cups)
    unit="ml",
    category="Bakery",
    sources=[
        RecipeSource(recipe_id=1, recipe_title="Pancakes", quantity=1, unit="cup"),
        RecipeSource(recipe_id=3, recipe_title="Bread", quantity=2, unit="cup")
    ]
)
```

**Conversion to CartItem**:
```python
def to_cart_item(self, cart_id: int) -> CartItem:
    return CartItem(
        cart_id=cart_id,
        ingredient_name=self.name.title(),
        quantity=self.total_quantity,
        unit=self.unit,
        category=self.category,
        recipe_ids=[src.recipe_id for src in self.sources]
    )
```

---

## Frontend Data Structures

### GroceryCartState (React Reducer)
**Source**: `frontend/src/reducers/groceryCartReducer.ts`
**Changes**: Add `viewMode` field

```typescript
type GroceryCartState = {
  checkedItems: Set<string>;  // Existing: tracks checked ingredients
  viewMode: 'recipe' | 'category';  // NEW: toggle between views
}

type GroceryCartAction =
  | { type: 'USER_TOGGLED_ITEM'; payload: string }
  | { type: 'USER_CHECKED_ALL_ITEMS' }
  | { type: 'USER_UNCHECKED_ALL_ITEMS' }
  | { type: 'CART_RESET' }
  | { type: 'USER_TOGGLED_VIEW_MODE' };  // NEW
```

---

### GroceryListViewData (Frontend Display)
**Usage**: Computed from `GroceryCart` for rendering

```typescript
// Recipe View
type RecipeGroup = {
  recipeId: number;
  recipeTitle: string;
  items: GroceryItem[];
  totalCost: number;
};

type RecipeViewData = {
  groups: RecipeGroup[];
  grandTotal: number;
};

// Category View (existing structure, no changes)
type CategoryGroup = {
  category: string;
  icon: string;
  items: GroceryItem[];
};

type CategoryViewData = {
  groups: CategoryGroup[];
  grandTotal: number;
};
```

---

## API Response Schemas

### CartCreateResponse
**Endpoint**: POST `/api/v1/grocery-carts`

```typescript
interface CartCreateResponse {
  id: number;
  meal_plan_id: number;
  items: CartItem[];
  total_items: number;
  status: "active";
  created_at: string;
  unavailable_items?: string[];  // Ingredients not matched to Knuspr
}
```

### CartItemSchema (Extended)
**Changes**: Add `recipe_sources` to API response for frontend display

```typescript
interface CartItem {
  id: number;
  ingredient_name: string;
  quantity: number;
  unit: string;
  category: string;
  estimated_cost?: number;
  checked?: boolean;  // Frontend-only, from reducer
  recipe_sources?: RecipeSource[];  // NEW: computed from recipe_ids
}

interface RecipeSource {
  recipe_id: number;
  recipe_title: string;
  quantity: number;
  unit: string;
}
```

**Backend Serialization**:
```python
# In schemas/grocery_cart.py
class CartItemSchema(BaseModel):
    # ... existing fields ...
    recipe_sources: List[RecipeSourceSchema] | None = None

    @classmethod
    def from_orm_with_sources(cls, cart_item: CartItem, db: Session):
        # Load recipes by IDs in cart_item.recipe_ids
        sources = []
        if cart_item.recipe_ids:
            recipes = db.query(Recipe).filter(Recipe.id.in_(cart_item.recipe_ids)).all()
            for recipe in recipes:
                # Find this ingredient in recipe.ingredients
                sources.append(RecipeSourceSchema(
                    recipe_id=recipe.id,
                    recipe_title=recipe.title,
                    quantity=...,  # Parse from recipe.ingredients
                    unit=...
                ))
        return cls(..., recipe_sources=sources)
```

---

## Data Flow Diagram

```
User creates Meal Plan
         ↓
[MealPlan with recipes] ──→ Extract recipes ──→ [MealPlanRecipe joins]
         ↓
Parse ingredients from Recipe.ingredients JSON
         ↓
Normalize names via Ingredient.aliases
         ↓
Aggregate quantities (group by normalized name, sum quantities)
         ↓
Assign categories from Ingredient.category
         ↓
[AggregatedIngredient] ──→ Convert to CartItem ──→ Store in DB
         ↓
Match to Knuspr products via KnusprMCPClient
         ↓
[GroceryCart with CartItem[]]
         ↓
Frontend: Group by recipe_ids OR category
         ↓
Display in RecipeView or CategoryView
```

---

## Validation Rules

### CartItem
- `quantity` must be > 0
- `unit` must be in allowed list: ["ml", "g", "pcs", "cup", "tbsp", "tsp", "oz", "lb"]
- `category` must be valid category enum
- `recipe_ids` must reference existing Recipe IDs

### GroceryCart
- `meal_plan_id` must reference existing MealPlan (if provided)
- Cannot create cart for meal plan with status "generating" or "failed"
- User must own the meal plan

---

## Database Indexes

**Existing (no changes needed)**:
- `cart_items.cart_id` (foreign key index)
- `grocery_carts.user_id` (foreign key index)
- `grocery_carts.meal_plan_id` (foreign key index)

**New (recommended)**:
```sql
CREATE INDEX idx_cart_items_recipe_ids ON cart_items USING GIN (recipe_ids);
-- Speeds up queries filtering by recipe membership
```

---

## Summary

**Entities Modified**: 1 (CartItem - add `recipe_ids`)
**Entities Created**: 0 (all new structures are computed/temporary)
**Entities Reused**: 6 (User, Recipe, MealPlan, MealPlanRecipe, Ingredient, GroceryCart)

**Complexity**: Low - feature extends existing data model rather than creating new tables

**Ready for**: API contract definition (Phase 1 contracts/)
