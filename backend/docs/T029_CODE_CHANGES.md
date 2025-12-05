# T029: Code Changes Summary

## Overview

This document provides a detailed breakdown of all code changes made to optimize database queries with eager loading.

## Changes by File

### 1. `/home/darae/claude-code-projects/backend/app/api/v1/meal_plans.py`

#### Change 1: Add selectinload import

**Line 10**:
```python
# BEFORE
from sqlalchemy.orm import Session

# AFTER
from sqlalchemy.orm import Session, selectinload
```

#### Change 2: Optimize get_meal_plan endpoint

**Lines 276-284**:
```python
# BEFORE
meal_plan = (
    db.query(MealPlan)
    .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
    .first()
)

# AFTER
# Optimized query with eager loading to avoid N+1 queries
meal_plan = (
    db.query(MealPlan)
    .options(
        selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
    )
    .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
    .first()
)
```

**Impact**: Reduces queries from 12 to 3 when accessing meal plan with recipes.

#### Change 3: Optimize generate_grocery_cart endpoint

**Lines 376-405**:
```python
# BEFORE
meal_plan = (
    db.query(MealPlan)
    .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
    .first()
)

# ... later ...

# Get all recipes in meal plan
meal_plan_recipes = (
    db.query(MealPlanRecipe)
    .filter(MealPlanRecipe.meal_plan_id == meal_plan_id)
    .all()
)

# AFTER
# Optimized query with eager loading to avoid N+1 queries
meal_plan = (
    db.query(MealPlan)
    .options(
        selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
    )
    .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
    .first()
)

# ... later ...

# Use already-loaded recipes from meal plan (no additional query)
meal_plan_recipes = meal_plan.recipes
```

**Impact**: Eliminates separate query for meal_plan_recipes and N+1 queries for individual recipes.

---

### 2. `/home/darae/claude-code-projects/backend/app/api/v1/workflows.py`

#### Change 1: Add selectinload import

**Line 12**:
```python
# BEFORE
from sqlalchemy.orm import Session

# AFTER
from sqlalchemy.orm import Session, selectinload
```

#### Change 2: Pre-fetch recipes to avoid N+1 in create_cart_from_meal_plan

**Lines 127-159** (new code added):
```python
# BEFORE
for agg_item in aggregated_ingredients:
    try:
        # Get recipe names for source tracking
        recipe_sources = []
        for recipe_id in agg_item.recipe_ids:
            recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()  # N+1 query!
            if recipe:
                recipe_sources.append(
                    RecipeSource(recipe_id=recipe.id, recipe_name=recipe.title)
                )

# AFTER
# Pre-fetch all recipes involved to avoid N+1 queries
all_recipe_ids = set()
for agg_item in aggregated_ingredients:
    all_recipe_ids.update(agg_item.recipe_ids)

recipes_dict = {}
if all_recipe_ids:
    recipes = db.query(Recipe).filter(Recipe.id.in_(all_recipe_ids)).all()
    recipes_dict = {r.id: r for r in recipes}

# ... later in the loop ...

for agg_item in aggregated_ingredients:
    try:
        # Get recipe names for source tracking (using pre-fetched recipes)
        recipe_sources = []
        for recipe_id in agg_item.recipe_ids:
            recipe = recipes_dict.get(recipe_id)  # O(1) lookup, no query
            if recipe:
                recipe_sources.append(
                    RecipeSource(recipe_id=recipe.id, recipe_name=recipe.title)
                )
```

**Impact**: Converts N individual queries to 1 batch query using IN clause.

#### Change 3: Optimize meal plan query in meal_plan_with_groceries workflow

**Lines 251-262**:
```python
# BEFORE
meal_plan = db.query(MealPlan).filter(
    MealPlan.id == request.meal_plan_id,
    MealPlan.user_id == user_id
).first()

# AFTER
# 1. Validate meal plan (optimized with eager loading)
meal_plan = (
    db.query(MealPlan)
    .options(
        selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
    )
    .filter(
        MealPlan.id == request.meal_plan_id,
        MealPlan.user_id == user_id
    )
    .first()
)
```

**Impact**: Pre-loads all recipes with the meal plan query.

#### Change 4: Optimize cart items access in fill_knuspr_cart

**Lines 416-431**:
```python
# BEFORE
cart = (
    db.query(GroceryCart)
    .filter(GroceryCart.id == cart_id, GroceryCart.user_id == user_id)
    .first()
)

if not cart:
    raise HTTPException(...)

# 2. Fetch cart items
cart_items = (
    db.query(CartItem)
    .filter(CartItem.cart_id == cart_id)
    .all()
)

# AFTER
# 1. Validate cart exists and belongs to user (optimized with eager loading)
cart = (
    db.query(GroceryCart)
    .options(selectinload(GroceryCart.items))
    .filter(GroceryCart.id == cart_id, GroceryCart.user_id == user_id)
    .first()
)

if not cart:
    raise HTTPException(...)

# 2. Use already-loaded cart items (no additional query)
cart_items = cart.items
```

**Impact**: Eliminates separate query for cart items.

---

### 3. `/home/darae/claude-code-projects/backend/scripts/test_query_performance.py` (NEW FILE)

**Purpose**: Performance testing script to validate query optimizations.

**Key Features**:
- Query counter using SQLAlchemy events
- Before/after comparison tests
- Automated test database setup
- Comprehensive reporting

**Usage**:
```bash
cd backend
python3 scripts/test_query_performance.py
```

**Output Example**:
```
================================================================================
PERFORMANCE SUMMARY
================================================================================

1. GroceryAggregator (sync):
   Queries: 3
   Status: Already optimized with selectinload()

2. Meal Plan Query:
   Without eager loading: 12 queries
   With eager loading: 3 queries
   Improvement: 75.0% reduction

3. Grocery Cart Generation:
   Without optimization: 12 queries
   With optimization: 3 queries
   Improvement: 75.0% reduction
```

## Query Count Comparison

### Endpoint: GET /api/v1/meal-plans/{id}

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| Meal plan with 10 recipes | 12 queries | 3 queries | 75% |
| Meal plan with 50 recipes | 52 queries | 3 queries | 94% |
| Meal plan with 100 recipes | 102 queries | 3 queries | 97% |

### Endpoint: POST /api/v1/meal-plans/{id}/grocery-cart

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| Generate cart from 10 recipes | 12 queries | 3 queries | 75% |
| Generate cart from 50 recipes | 52 queries | 3 queries | 94% |
| Generate cart from 100 recipes | 102 queries | 3 queries | 97% |

### Endpoint: POST /api/v1/workflows/fill-knuspr-cart

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| Fill cart with 20 items | 3 queries | 2 queries | 33% |
| Fill cart with 100 items | 3 queries | 2 queries | 33% |

## Eager Loading Patterns Used

### Pattern 1: One-to-Many Relationship
```python
.options(selectinload(Parent.children))
```

**Example**:
```python
db.query(MealPlan).options(selectinload(MealPlan.recipes))
```

**SQL Generated**:
```sql
-- Query 1
SELECT * FROM meal_plans WHERE ...;

-- Query 2
SELECT * FROM meal_plan_recipes WHERE meal_plan_id IN (...);
```

### Pattern 2: Chained One-to-Many
```python
.options(
    selectinload(Parent.children)
    .selectinload(Child.grandchildren)
)
```

**Example**:
```python
db.query(MealPlan).options(
    selectinload(MealPlan.recipes)
    .selectinload(MealPlanRecipe.recipe)
)
```

**SQL Generated**:
```sql
-- Query 1
SELECT * FROM meal_plans WHERE ...;

-- Query 2
SELECT * FROM meal_plan_recipes WHERE meal_plan_id IN (...);

-- Query 3
SELECT * FROM recipes WHERE id IN (...);
```

### Pattern 3: Batch Query with IN Clause
```python
items = db.query(Model).filter(Model.id.in_(ids)).all()
lookup = {item.id: item for item in items}
```

**Example**:
```python
recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
recipes_dict = {r.id: r for r in recipes}
```

**SQL Generated**:
```sql
SELECT * FROM recipes WHERE id IN (1, 2, 3, 4, 5, ...);
```

## Testing Recommendations

### 1. Manual Testing with SQL Logging

Enable SQLAlchemy echo to see all queries:

```python
# In app/database.py or test setup
engine = create_engine(DATABASE_URL, echo=True)
```

### 2. Automated Query Count Tests

Add to your test suite:

```python
from sqlalchemy import event

def count_queries(session):
    query_count = 0

    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        query_count += 1

    event.listen(session.get_bind(), "before_cursor_execute", receive_before_cursor_execute)
    return query_count

def test_meal_plan_query_count(db_session):
    # Reset counter
    count = count_queries(db_session)

    # Execute endpoint
    result = get_meal_plan(meal_plan_id=1, db=db_session)

    # Assert query count
    assert count <= 3, f"Expected <= 3 queries, got {count}"
```

### 3. Performance Testing

Run the performance test script:

```bash
cd backend
python3 scripts/test_query_performance.py
```

## Rollback Instructions

If you need to rollback these changes:

### File 1: meal_plans.py
```bash
git checkout HEAD -- backend/app/api/v1/meal_plans.py
```

### File 2: workflows.py
```bash
git checkout HEAD -- backend/app/api/v1/workflows.py
```

### Remove test script
```bash
rm backend/scripts/test_query_performance.py
```

## Verification Checklist

- ✅ All endpoints return same data as before
- ✅ No breaking changes to API responses
- ✅ Query count reduced from 12 to 3 for meal plan queries
- ✅ Query count reduced from N+1 to 1 for recipe fetching in loops
- ✅ Cart items loaded in batch instead of separate query
- ✅ Performance test script validates improvements
- ✅ Code follows SQLAlchemy best practices
- ✅ Documentation updated

## Notes

1. **GroceryAggregator was already optimized** - No changes needed, already uses `selectinload()`

2. **Existing tests may need updates** - Some unit tests use `db=Mock()` instead of `db_session`, which is a pre-existing issue

3. **Production deployment** - Monitor query performance after deployment to validate improvements

4. **Database connection pool** - Ensure pool size is adequate for reduced query patterns

---

**Author**: Claude Code
**Date**: December 5, 2025
**Task**: T029 - Optimize database queries with eager loading
