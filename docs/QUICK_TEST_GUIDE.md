# Quick Test Guide - Generate Meal Plan Feature

## 🚀 Quick Start (5 minutes)

### Step 1: Seed Test Data (1 minute)

```bash
cd /home/darae/claude-code-projects
python scripts/seed_test_data.py
```

Expected output:
```
✅ Created test user: test@example.com (ID: 1)
✅ Created 19 new recipes
Total recipes: 40
```

---

### Step 2: Test on Vercel (3 minutes)

1. **Visit:** https://claude-code-projects.vercel.app/generate
2. **Login** with your test account
3. **Fill the form:**
   - Start Date: Pick today or tomorrow
   - Days: `7`
   - People: `2`
   - Meals/Day: `3`
   - Dietary: Check "Vegetarian" ✓
   - Exclude: `mushrooms` (optional)
4. **Click:** "Generate Meal Plan" button
5. **Wait:** 10-30 seconds for processing
6. **Check:** Did it redirect to the meal plan page?

---

### Step 3: Check Results (1 minute)

After generation, verify:
- ✅ Meal plan created (status = "ready")
- ✅ 21 meals generated (7 days × 3 meals)
- ✅ All recipes are vegetarian
- ✅ No "mushrooms" in meals
- ✅ Can view the full meal plan

---

## 📊 What Was Added

| Item | Count | Details |
|------|-------|---------|
| **Total Recipes** | 40 | +19 new recipes |
| **Vegan Recipes** | 13 | Diverse options |
| **Vegetarian Recipes** | 10 | With & without dairy |
| **Gluten-Free Recipes** | 15 | Main courses & sides |
| **Test Scripts** | 3 | Playwright + debug |

---

## 🔧 Testing Tools Created

### 1. **Playwright Tests**
```bash
npx playwright test meal-plan-generation.spec.ts --headed
```
Tests:
- Page loading
- Form rendering
- Form submission
- API responses

### 2. **Debug Script**
```bash
bash scripts/debug_meal_plan.sh
```
Checks:
- API accessibility
- Frontend connectivity
- Asset loading

### 3. **Seed Data Script**
```bash
python scripts/seed_test_data.py
```
Creates:
- Test user
- 40 recipes with nutrition data

---

## ⚠️ Common Issues & Fixes

### Issue: "No recipes found"
**Fix:** Run seed script
```bash
python scripts/seed_test_data.py
```

### Issue: Form won't submit
**Fix:** Check:
- Start date is today or future
- All number fields have values
- Backend is running (Railway)

### Issue: Waiting too long (>30s)
**Fix:**
- Check Railway logs
- Try with fewer days (3-5)
- Try without dietary restrictions

### Issue: 403 on API
**Fix:**
- Must be logged in
- Session might have expired
- Try logging out and back in

---

## 📋 Form Fields Reference

| Field | Min | Max | Example | Required |
|-------|-----|-----|---------|----------|
| Start Date | - | - | 2025-11-20 | ✅ |
| Days | 1 | 14 | 7 | ✅ |
| People | 1 | 10 | 2 | ✅ |
| Meals/Day | 1 | 5 | 3 | ✅ |
| Dietary Restrictions | - | - | vegetarian | ❌ |
| Excluded Ingredients | - | - | mushrooms | ❌ |

---

## 🎯 Success Criteria

The feature is working if:

1. ✅ Form loads without errors
2. ✅ All form fields are editable
3. ✅ Submit button becomes active when form is valid
4. ✅ Form submits and returns 202 ACCEPTED
5. ✅ Redirects to meal plan page within 30 seconds
6. ✅ Meal plan shows 21 meals (for 7 days × 3 meals)
7. ✅ All dietary restrictions are respected
8. ✅ No excluded ingredients appear in the meals

---

## 📱 Testing Checklist

- [ ] Form renders on desktop
- [ ] Form renders on mobile
- [ ] Form validation works
- [ ] Dietary restrictions display correctly
- [ ] Submit button shows loading state
- [ ] API returns 202 ACCEPTED
- [ ] Meal plan generates without errors
- [ ] Dietary filters are applied
- [ ] No excluded ingredients in results
- [ ] Can view and edit generated plan

---

## 🐛 If Something Breaks

1. **Check browser console** (F12)
2. **Check Network tab** for failed requests
3. **Check Railway logs** for backend errors
4. **Run debug script:** `bash scripts/debug_meal_plan.sh`
5. **Check seed data:** `python scripts/seed_test_data.py`
6. **Try another browser** to rule out local cache

---

## 📚 Full Documentation

For detailed information, see: `MEAL_PLAN_DEBUG_GUIDE.md`

---

**Status:** ✅ Ready for testing
**Last Updated:** 2025-11-18
**Recipe Database:** 40 recipes seeded
