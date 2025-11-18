# Testing Guide - Phase 2 Enhancements
## Comprehensive Validation for Production Readiness

**Date**: 2025-11-17
**Purpose**: Validate all three enhancements work correctly
**Estimated Time**: 30-45 minutes

---

## Prerequisites Checklist

Before starting tests, ensure:

```bash
# 1. Docker is running
docker ps

# 2. All services are up
docker-compose ps
# Expected: db, redis, api, prometheus, grafana (all healthy)

# 3. Database is accessible
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "SELECT 1;"
# Expected: (1 row)

# 4. API is responding
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

---

## PART 1: Database Migration (5 minutes)

### Step 1: Apply Migration 005

```bash
# Apply the migration
docker exec -it recipe-api alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade 004 -> 005, add dietary tags
# ✅ Added dietary_tags column to recipes table
```

### Step 2: Verify Migration

```bash
# Check if column exists
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "\d recipes;"

# Expected: Should see 'dietary_tags' column with type 'json'
```

### Step 3: Check Migration History

```bash
# View migration history
docker exec -it recipe-api alembic current

# Expected: 005_add_dietary_tags (head)
```

### Rollback Test (Optional)

```bash
# Test rollback
docker exec -it recipe-api alembic downgrade -1

# Expected: Column removed

# Re-apply
docker exec -it recipe-api alembic upgrade head

# Expected: Column re-added
```

---

## PART 2: Unit Tests (10-15 minutes)

### Step 1: Run Enhanced Test Suite

```bash
# Run all enhanced tests with verbose output
docker exec -it recipe-api pytest tests/test_meal_plans_enhanced.py -v

# Expected output:
# tests/test_meal_plans_enhanced.py::TestDietaryRestrictionFiltering::test_filter_vegan_recipes PASSED
# tests/test_meal_plans_enhanced.py::TestDietaryRestrictionFiltering::test_filter_vegetarian_recipes_includes_vegan PASSED
# tests/test_meal_plans_enhanced.py::TestDietaryRestrictionFiltering::test_filter_gluten_free_recipes PASSED
# ... (15 tests total)
# ======================== 15 passed in 5.23s ========================
```

### Step 2: Run with Coverage

```bash
# Run with coverage report
docker exec -it recipe-api pytest tests/test_meal_plans_enhanced.py \
  --cov=app.agents.meal_architect \
  --cov-report=term-missing \
  -v

# Expected coverage: ~90%
```

### Step 3: Run Specific Test Classes

```bash
# Test dietary restrictions only
docker exec -it recipe-api pytest tests/test_meal_plans_enhanced.py::TestDietaryRestrictionFiltering -v

# Test variety history only
docker exec -it recipe-api pytest tests/test_meal_plans_enhanced.py::TestRecipeVarietyHistory -v

# Test nutrition calculation only
docker exec -it recipe-api pytest tests/test_meal_plans_enhanced.py::TestImprovedNutritionCalculation -v

# Test excluded ingredients only
docker exec -it recipe-api pytest tests/test_meal_plans_enhanced.py::TestExcludedIngredients -v
```

### Step 4: Run Original Tests (Regression Check)

```bash
# Ensure we didn't break existing functionality
docker exec -it recipe-api pytest tests/test_meal_plans.py -v

# Expected: All original tests still pass (10 tests)
```

---

## PART 3: API Testing with cURL (15-20 minutes)

### Setup: Create Test User and Recipes

```bash
# Create test user (replace with your actual auth endpoint)
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "country": "DE"
  }'

# Save the access_token from response
export TOKEN="<your_access_token>"
```

### Test 1: Create Vegan Recipes

```bash
# Create a vegan recipe
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vegan Buddha Bowl",
    "ingredients": ["quinoa", "chickpeas", "kale", "tahini", "lemon"],
    "instructions": "Cook quinoa. Mix with chickpeas, kale, tahini, and lemon.",
    "prep_time": 15,
    "cook_time": 20,
    "servings": 2,
    "dietary_tags": ["vegan", "gluten_free"],
    "nutrition": {"calories": 450},
    "source_url": "https://example.com/vegan-bowl"
  }'

# Create a non-vegan recipe
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chicken Salad",
    "ingredients": ["chicken breast", "lettuce", "tomatoes", "ranch dressing"],
    "instructions": "Grill chicken. Toss with lettuce and tomatoes.",
    "prep_time": 10,
    "cook_time": 15,
    "servings": 2,
    "dietary_tags": ["gluten_free"],
    "nutrition": {"calories": 350},
    "source_url": "https://example.com/chicken-salad"
  }'
```

### Test 2: Create Meal Plan with Vegan Restriction

```bash
# Request vegan meal plan
curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-25",
    "num_days": 3,
    "num_people": 2,
    "dietary_restrictions": ["vegan"],
    "meals_per_day": 3
  }'

# Expected: Response should only include vegan recipes
# Check the response - all recipes should have "vegan" in dietary_tags
```

### Test 3: Create Meal Plan with Excluded Ingredients

```bash
# Exclude specific ingredient
curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-26",
    "num_days": 3,
    "num_people": 2,
    "excluded_ingredients": ["chicken"],
    "meals_per_day": 3
  }'

# Expected: No recipes with chicken in ingredients
```

### Test 4: Multiple Dietary Restrictions

```bash
# Vegan + gluten-free
curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-27",
    "num_days": 3,
    "num_people": 2,
    "dietary_restrictions": ["vegan", "gluten_free"],
    "meals_per_day": 3
  }'

# Expected: Only recipes tagged as BOTH vegan AND gluten_free
```

### Test 5: Verify Improved Nutrition Calculation

```bash
# Create meal plan and check totals
PLAN_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-28",
    "num_days": 3,
    "num_people": 2,
    "meals_per_day": 3
  }')

echo $PLAN_RESPONSE | jq '.total_calories, .total_cost'

# Expected:
# - total_calories: Should be reasonable (e.g., 2700-9000 for 9 meals)
# - total_cost: Should be reasonable (e.g., €20-80 for 9 meals)
# - More accurate than before (not just 600 cal * 9 meals)
```

---

## PART 4: Recipe Variety Testing (10 minutes)

### Test 1: Create Multiple Meal Plans

```bash
# Create first meal plan
PLAN1=$(curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-25",
    "num_days": 7,
    "num_people": 2,
    "meals_per_day": 3
  }')

PLAN1_ID=$(echo $PLAN1 | jq -r '.id')

# Get recipes from first plan
curl http://localhost:8000/api/v1/meal-plans/$PLAN1_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.days[].meals[].recipe_id' > plan1_recipes.txt

# Wait a moment, then create second plan
sleep 2

PLAN2=$(curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-12-02",
    "num_days": 7,
    "num_people": 2,
    "meals_per_day": 3
  }')

PLAN2_ID=$(echo $PLAN2 | jq -r '.id')

# Get recipes from second plan
curl http://localhost:8000/api/v1/meal-plans/$PLAN2_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.days[].meals[].recipe_id' > plan2_recipes.txt

# Compare recipes - should be different
diff plan1_recipes.txt plan2_recipes.txt

# Expected: Many differences (recipes should vary)
```

### Test 2: Verify 14-Day Lookback

```bash
# This Python script tests the variety feature
docker exec -it recipe-api python3 << 'EOF'
from app.database import SessionLocal
from app.agents.meal_architect import MealArchitectAgent
from datetime import date, timedelta

db = SessionLocal()
agent = MealArchitectAgent(db)

# Get recently used recipe IDs for test user
user_id = 1  # Replace with actual user ID
recently_used = agent._get_recently_used_recipe_ids(user_id, days=14)

print(f"Recently used recipes (last 14 days): {len(recently_used)}")
print(f"Recipe IDs: {recently_used}")

db.close()
EOF
```

---

## PART 5: Swagger UI Testing (5 minutes)

### Interactive Testing

1. **Open Swagger UI**: http://localhost:8000/api/docs

2. **Authenticate**:
   - Click "Authorize" button
   - Enter your bearer token
   - Click "Authorize"

3. **Test POST /api/v1/meal-plans**:
   - Click "Try it out"
   - Fill in request body:
   ```json
   {
     "start_date": "2025-11-25",
     "num_days": 7,
     "num_people": 2,
     "dietary_restrictions": ["vegetarian"],
     "excluded_ingredients": ["mushrooms"],
     "target_calories_per_day": 2000,
     "meals_per_day": 3
   }
   ```
   - Click "Execute"
   - Verify response includes dietary-compliant recipes

4. **Test GET /api/v1/meal-plans/{id}**:
   - Use ID from previous response
   - Verify detailed view includes days and statistics
   - Check that total_calories and total_cost are reasonable

---

## PART 6: Performance Testing (Optional)

### Test 1: Measure Generation Time

```bash
# Time a meal plan generation
time curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-25",
    "num_days": 7,
    "num_people": 2,
    "dietary_restrictions": ["vegan"],
    "meals_per_day": 3
  }'

# Expected: < 3 seconds total (including network)
```

### Test 2: Load Test (Optional)

```bash
# Install Apache Bench if needed
# sudo apt-get install apache2-utils

# Create test.json
cat > test.json << 'EOF'
{
  "start_date": "2025-11-25",
  "num_days": 3,
  "num_people": 2,
  "meals_per_day": 3
}
EOF

# Run load test (10 concurrent requests, 100 total)
ab -n 100 -c 10 -p test.json -T application/json \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/meal-plans

# Expected:
# - Requests per second: > 5
# - Mean response time: < 2000ms
# - No failed requests
```

---

## PART 7: Database Validation

### Verify Data Integrity

```bash
# Check that dietary_tags are being saved
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "
  SELECT id, title, dietary_tags
  FROM recipes
  WHERE dietary_tags IS NOT NULL
  LIMIT 5;
"

# Expected: Should see JSON arrays like ["vegan", "gluten_free"]
```

### Check Meal Plan Variety

```bash
# Query to see if recipes are being reused too soon
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "
  SELECT
    mp.id,
    mp.start_date,
    COUNT(DISTINCT mpr.recipe_id) as unique_recipes,
    COUNT(mpr.recipe_id) as total_meals
  FROM meal_plans mp
  JOIN meal_plan_recipes mpr ON mp.id = mpr.meal_plan_id
  WHERE mp.user_id = 1
  GROUP BY mp.id, mp.start_date
  ORDER BY mp.start_date DESC
  LIMIT 5;
"

# Expected: unique_recipes should equal total_meals (no duplicates within same plan)
```

---

## PART 8: Error Handling Tests

### Test 1: No Matching Recipes

```bash
# Try to create plan with impossible constraints
curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-25",
    "num_days": 30,
    "num_people": 2,
    "dietary_restrictions": ["vegan", "gluten_free"],
    "excluded_ingredients": ["rice", "quinoa", "beans", "lentils"],
    "meals_per_day": 3
  }'

# Expected: 500 error with message "No suitable recipes found for the given constraints"
```

### Test 2: Invalid Dietary Restriction

```bash
# Unknown dietary restriction (should still work, just won't filter)
curl -X POST http://localhost:8000/api/v1/meal-plans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-25",
    "num_days": 3,
    "num_people": 2,
    "dietary_restrictions": ["paleo"],
    "meals_per_day": 3
  }'

# Expected: 202 Accepted (ignores unknown restriction)
```

---

## EXPECTED RESULTS SUMMARY

### ✅ What Should Work

1. **Migration**:
   - ✅ dietary_tags column added
   - ✅ Backward compatible (existing recipes still work)

2. **Dietary Filtering**:
   - ✅ Vegan plans only include vegan recipes
   - ✅ Vegetarian includes vegan recipes too
   - ✅ Gluten-free filtering works
   - ✅ Multiple restrictions use AND logic
   - ✅ Excluded ingredients are respected

3. **Recipe Variety**:
   - ✅ Second meal plan uses different recipes
   - ✅ Recipes beyond 14 days can be reused
   - ✅ No duplicates within same meal plan

4. **Nutrition Calculation**:
   - ✅ Uses recipe nutrition data when available
   - ✅ Falls back to ingredient-based calculation
   - ✅ More accurate totals than before
   - ✅ Reasonable bounds (300-1000 cal/serving)

5. **All Tests Pass**:
   - ✅ 15/15 new tests pass
   - ✅ 10/10 original tests still pass
   - ✅ No regressions

### ⚠️ Known Limitations

1. **Ingredient Parsing**: Simple keyword matching
2. **Nutrition Accuracy**: Estimates when data missing
3. **Cost Accuracy**: Category-based estimates
4. **Variety**: Requires enough recipes in database

---

## TROUBLESHOOTING

### Issue: Tests Fail

**Symptom**: pytest shows failures

**Diagnosis**:
```bash
# Check if database has test data
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "SELECT COUNT(*) FROM recipes;"

# Check if Ingredient Intelligence tables exist
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "\dt"
```

**Solutions**:
1. Ensure all migrations are applied: `alembic upgrade head`
2. Seed ingredient data if needed
3. Check logs: `docker logs recipe-api`

### Issue: No Recipes in Meal Plan

**Symptom**: Error "No suitable recipes found"

**Diagnosis**:
```bash
# Check how many recipes exist for user
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "
  SELECT COUNT(*) FROM recipes WHERE user_id = 1;
"
```

**Solutions**:
1. Create more recipes (need at least 21 for 7-day plan with 3 meals/day)
2. Relax dietary restrictions
3. Reduce num_days or meals_per_day

### Issue: All Meal Plans Have Same Recipes

**Symptom**: Variety feature not working

**Diagnosis**:
```bash
# Check meal plan dates
docker exec -it recipe-postgres psql -U postgres -d recipe_app -c "
  SELECT id, start_date, status FROM meal_plans WHERE user_id = 1 ORDER BY start_date;
"
```

**Solutions**:
1. Ensure meal plans have status 'ready', 'active', or 'completed'
2. Check that plans are within 14-day window
3. Verify you have enough recipes (> 42 for two 21-recipe plans)

---

## TEST COMPLETION CHECKLIST

Mark items as you complete them:

- [ ] Migration applied successfully
- [ ] Migration verified in database
- [ ] All 15 enhanced tests pass
- [ ] All 10 original tests still pass
- [ ] Coverage > 85%
- [ ] Vegan filtering works
- [ ] Vegetarian filtering works
- [ ] Gluten-free filtering works
- [ ] Multiple restrictions work (AND logic)
- [ ] Excluded ingredients work
- [ ] Recipe variety works (different recipes in consecutive plans)
- [ ] Nutrition totals are reasonable
- [ ] Cost estimates are reasonable
- [ ] API responds in < 3 seconds
- [ ] No errors in logs

**Signature**: _________________ **Date**: _________________

---

## NEXT STEPS AFTER TESTING

### If All Tests Pass ✅
1. Mark Phase 2 as Production-Ready
2. Create deployment plan
3. Choose next phase (2C or 3)

### If Tests Fail ⚠️
1. Document failures
2. Create GitHub issues
3. Fix issues
4. Re-test

---

**Document Created**: 2025-11-17
**Last Updated**: 2025-11-17
**Status**: Ready for Validation
