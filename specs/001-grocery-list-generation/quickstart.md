# Quickstart: Grocery List Generation Feature

**Feature**: 001-grocery-list-generation
**Last Updated**: 2025-11-29

## For Developers

### Prerequisites
- Python 3.11+ (backend)
- Node.js 20+ (frontend)
- PostgreSQL running
- Knuspr MCP server configured

### Quick Start (Backend)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations (add recipe_ids field)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest tests/unit/test_grocery_aggregator.py -v
pytest tests/integration/test_grocery_cart_api.py -v
```

### Quick Start (Frontend)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run unit tests
npm test

# Run E2E tests
npx playwright test e2e/grocery-cart-views.spec.ts
```

---

## Key Files to Modify

### Backend
1. **New Service**: `backend/app/services/grocery_aggregator.py`
   - Implement `aggregate_from_meal_plan(meal_plan_id)` function
   - Parse ingredients, normalize names, sum quantities

2. **Modify Endpoint**: `backend/app/api/v1/grocery_carts.py`
   - Replace mock responses with real database operations
   - Use `GroceryAggregator` service

3. **Add Migration**: `backend/alembic/versions/XXX_add_recipe_ids.py`
   - Add `recipe_ids` JSON field to `cart_items` table

### Frontend
1. **New Component**: `frontend/src/components/knuspr/GroceryListView.tsx`
   - Accepts `items` and `viewMode` props
   - Renders recipe-grouped OR category-grouped views

2. **New Component**: `frontend/src/components/knuspr/ViewToggle.tsx`
   - Button to toggle between recipe/category views
   - Updates reducer state

3. **Modify Reducer**: `frontend/src/reducers/groceryCartReducer.ts`
   - Add `viewMode: 'recipe' | 'category'` to state
   - Add `USER_TOGGLED_VIEW_MODE` action

4. **Modify Page**: `frontend/src/app/grocery-carts/[id]/page.tsx`
   - Import and use `GroceryListView` component
   - Add view toggle button

---

## API Usage Examples

### 1. Create Grocery Cart from Meal Plan

**Request**:
```http
POST /api/v1/grocery-carts
Authorization: Bearer <token>
Content-Type: application/json

{
  "meal_plan_id": 42
}
```

**Response**:
```json
{
  "id": 123,
  "meal_plan_id": 42,
  "items": [
    {
      "id": 456,
      "ingredient_name": "Flour",
      "quantity": 720,
      "unit": "ml",
      "category": "Bakery",
      "recipe_sources": [
        {"recipe_id": 1, "recipe_title": "Pancakes", "quantity": 1.0, "unit": "cup"},
        {"recipe_id": 3, "recipe_title": "Bread", "quantity": 2.0, "unit": "cup"}
      ]
    }
  ],
  "total_items": 24,
  "status": "active",
  "created_at": "2025-11-29T10:00:00Z"
}
```

### 2. Start Knuspr Cart Workflow

**Request**:
```http
POST /api/v1/workflows/cart-from-meal-plan
Authorization: Bearer <token>
Content-Type: application/json

{
  "meal_plan_id": 42,
  "delivery_preferences": {
    "preferred_time_slot": "afternoon",
    "budget_optimization": false
  }
}
```

**Response (202 Accepted)**:
```json
{
  "workflow_id": "wf-123abc",
  "status": "in_progress",
  "message": "Generating grocery cart and syncing to Knuspr..."
}
```

**Later (poll or webhook)**:
```json
{
  "workflow_id": "wf-123abc",
  "status": "completed",
  "result": {
    "cart_id": 123,
    "knuspr_url": "https://knuspr.de/cart/abc123",
    "total_price": 48.50,
    "item_count": 24
  }
}
```

---

## Testing Strategy

### Unit Tests (TDD - Write First!)

**Backend** (`backend/tests/unit/test_grocery_aggregator.py`):
```python
def test_aggregate_single_recipe():
    """Single recipe with 3 ingredients."""
    result = aggregator.aggregate_from_recipes([recipe_1])
    assert len(result) == 3
    assert result[0].name == "flour"
    assert result[0].total_quantity == 240  # 1 cup

def test_aggregate_multiple_recipes_same_ingredient():
    """Two recipes both using flour - should sum."""
    result = aggregator.aggregate_from_recipes([recipe_1, recipe_2])
    flour = [i for i in result if i.name == "flour"][0]
    assert flour.total_quantity == 720  # 3 cups total
    assert len(flour.sources) == 2

def test_unit_conversion():
    """Convert cups to ml."""
    result = aggregator.convert_quantity(1.0, "cup", "ml")
    assert result == 240
```

**Frontend** (`frontend/__tests__/components/GroceryListView.test.tsx`):
```typescript
test('renders recipe view with grouped items', () => {
  render(<GroceryListView items={mockItems} viewMode="recipe" />);
  expect(screen.getByText('Pancakes')).toBeInTheDocument();
  expect(screen.getByText('Bread')).toBeInTheDocument();
});

test('renders category view with grouped items', () => {
  render(<GroceryListView items={mockItems} viewMode="category" />);
  expect(screen.getByText('Bakery')).toBeInTheDocument();
  expect(screen.getByText('Produce')).toBeInTheDocument();
});

test('view toggle updates reducer state', () => {
  const { result } = renderHook(() => useGroceryCartReducer());
  act(() => result.current.dispatch({ type: 'USER_TOGGLED_VIEW_MODE' }));
  expect(result.current.state.viewMode).toBe('category');
});
```

### Integration Tests

**Backend** (`backend/tests/integration/test_grocery_cart_api.py`):
```python
def test_create_cart_from_meal_plan(client, test_user, meal_plan_with_recipes):
    response = client.post(
        "/api/v1/grocery-carts",
        json={"meal_plan_id": meal_plan_with_recipes.id},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_items"] > 0
    assert all("recipe_sources" in item for item in data["items"])
```

### E2E Tests

**Frontend** (`frontend/e2e/grocery-cart-views.spec.ts`):
```typescript
test('full workflow: create cart, toggle views, verify aggregation', async ({ page }) => {
  // 1. Navigate to meal plan
  await page.goto('/meal-plans/42');

  // 2. Click "Generate Cart"
  await page.click('button:has-text("Generate Grocery Cart")');

  // 3. Wait for cart creation
  await expect(page.locator('text=Your Grocery Cart')).toBeVisible();

  // 4. Verify category view (default)
  await expect(page.locator('text=Bakery')).toBeVisible();

  // 5. Toggle to recipe view
  await page.click('button:has-text("View by Recipe")');

  // 6. Verify recipe grouping
  await expect(page.locator('text=Pancakes')).toBeVisible();
  await expect(page.locator('text=(from Pancakes, Bread)')).toBeVisible();
});
```

---

## Debugging Tips

### Backend Issues

**Cart items have duplicate ingredients**:
```python
# Check normalization
from app.services.grocery_aggregator import normalize_ingredient_name
print(normalize_ingredient_name("Tomatoes"))  # Should be "tomato"
print(normalize_ingredient_name("tomato"))    # Should be "tomato"
```

**Quantity calculations wrong**:
```python
# Check unit conversion
from app.models.ingredient import Ingredient
flour = db.query(Ingredient).filter_by(name="flour").first()
print(flour.unit_conversions)  # Should have {"cup": 120, "tbsp": 7.5}
```

**Knuspr authentication failing**:
```bash
# Verify credentials
curl -X GET http://localhost:8000/api/v1/knuspr-credentials \
  -H "Authorization: Bearer <token>"

# Test connection
curl -X POST http://localhost:8000/api/v1/knuspr-credentials/verify \
  -H "Authorization: Bearer <token>"
```

### Frontend Issues

**View toggle not working**:
```typescript
// Check reducer state in Redux DevTools
// Look for USER_TOGGLED_VIEW_MODE actions
// Verify viewMode state changes

// Or add console logs
useEffect(() => {
  console.log('Current view mode:', viewMode);
}, [viewMode]);
```

**Items not grouped correctly**:
```typescript
// Check recipe_sources in API response
fetch('/api/v1/grocery-carts/123')
  .then(r => r.json())
  .then(data => console.log(data.items[0].recipe_sources));
```

---

## Architecture Diagrams

### Data Flow

```
User triggers cart creation
         ↓
[POST /grocery-carts {meal_plan_id}]
         ↓
Load MealPlan with recipes (eager loading)
         ↓
Extract ingredients from Recipe.ingredients JSON
         ↓
GroceryAggregator.aggregate()
  - Parse ingredient strings
  - Normalize names via Ingredient.aliases
  - Convert units via Ingredient.unit_conversions
  - Group by normalized name
  - Sum quantities
         ↓
Create CartItem records with recipe_ids
         ↓
[Return GroceryCart with items]
         ↓
Frontend renders with GroceryListView
  - If viewMode='category': groupBy(items, 'category')
  - If viewMode='recipe': groupBy(items, item => item.recipe_sources[0].recipe_id)
```

### Component Hierarchy (Frontend)

```
GroceryCartPage (page.tsx)
├── ViewToggle (new)
│   └── dispatch USER_TOGGLED_VIEW_MODE
├── GroceryListView (new)
│   ├── RecipeView (if viewMode='recipe')
│   │   └── RecipeGroup[]
│   │       └── CartItem (with source labels)
│   └── CategoryView (if viewMode='category')
│       └── CategoryGroup[]
│           └── CartItem (existing)
└── CartActions (existing)
    ├── Print button
    └── Export TXT
```

---

## Performance Benchmarks

**Target Performance** (from spec):
- Cart generation: <2 seconds
- View toggle: <1 second
- Knuspr cart population: <5 seconds

**How to Measure**:
```python
# Backend
import time
start = time.time()
cart = create_grocery_cart(meal_plan_id=42)
print(f"Cart creation took {time.time() - start:.2f}s")

# Frontend
console.time('viewToggle');
dispatch({ type: 'USER_TOGGLED_VIEW_MODE' });
console.timeEnd('viewToggle');
```

**Optimization Checklist**:
- [ ] Use eager loading for recipes (avoid N+1 queries)
- [ ] Cache ingredient normalization (LRU cache, 1000 items)
- [ ] Batch Knuspr product searches (max 10 concurrent)
- [ ] Index `cart_items.recipe_ids` (GIN index for JSON queries)

---

## Configuration

**Environment Variables** (add to `.env`):
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost/mealplanner
KNUSPR_MCP_URL=http://localhost:3001/mcp  # Or local script path
KNUSPR_USERNAME=your-knuspr-email
KNUSPR_PASSWORD=your-knuspr-password
KNUSPR_BASE_URL=https://www.knuspr.cz  # or .de, .at

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

**"Meal plan has no recipes"**:
- Ensure meal plan has status "ready" (not "generating" or "failed")
- Check `meal_plan_recipes` join table has entries

**"Ingredient not found" errors**:
- Populate Ingredient table with common ingredients
- Add aliases for variations (e.g., "tomato", "tomatoes", "Roma tomato")

**Knuspr cart creation fails**:
- Verify Knuspr credentials are active
- Check MCP server is running
- Review Knuspr API logs for 401/403 errors

---

## Next Steps

After implementing this feature:
1. Run `/speckit.tasks` to generate implementation task breakdown
2. Follow TDD: write tests first, then implementation
3. Deploy to staging for integration testing
4. Monitor Prometheus metrics for cart creation latency
5. Gather user feedback on recipe vs. category views

**Questions?** Check `research.md` for technical decisions and `data-model.md` for schema details.
