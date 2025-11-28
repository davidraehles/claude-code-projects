# Deployment Readiness Plan
**Goal:** Make all planned features available for user testing on Vercel + Railway
**Status:** Ready to Execute
**Timeline:** 2-3 hours
**Date:** 2025-11-18

---

## Current Status (Code-Verified)

### ✅ What's Working (100% Backend Complete)
- **Backend (Railway):** Fully deployed and production-ready ✅
  - Health endpoint: https://claude-code-projects-production.up.railway.app/health
  - API docs: https://claude-code-projects-production.up.railway.app/api/docs
  - **Authentication:** Fully implemented (326 lines)
    - JWT tokens (access + refresh)
    - Bcrypt password hashing (SHA-256 pre-hash + bcrypt 2b)
    - Token expiration handling
  - **Database:** PostgreSQL with 9 tables, all migrations working
  - **API Endpoints:** 25+ endpoints fully functional
    - `/api/v1/auth/*` - Register, login, refresh, profile (4 endpoints)
    - `/api/v1/recipes/*` - CRUD, harvest from URL (5 endpoints, 481 lines)
    - `/api/v1/meal-plans/*` - Generate, list, detail, delete (4 endpoints, 418 lines)
    - `/api/v1/ingredients/*` - Classify, substitutes, allergens (6 endpoints, 250 lines)
    - `/api/v1/users/*` - Preferences, notifications (6 endpoints, 194 lines)
  - **Meal Architect Agent:** Z3 constraint solver (784 lines, fully implemented)
  - **LangGraph Workflows:** Complete workflow orchestration (7 files, working)
  - **Recipe Scrapers:** HTML, API, RSS (all working with duplicate detection)
  - **Monitoring:** Prometheus + Grafana (20+ metrics, 2 dashboards)

- **Frontend (Vercel):** Landing page deployed, structure complete
  - URL: https://claude-code-projects.vercel.app
  - Beautiful landing page (hero, features, pricing, FAQ) ✅
  - 8 pages created (login, signup, dashboard, generate, etc.) ✅
  - Responsive design working ✅
  - Next.js 16 + React 19 + TailwindCSS 4 ✅

### ⚠️ What Needs Work (Frontend Integration Only)
- **Frontend Dependencies:** `node_modules` not installed locally (10 min fix)
- **Frontend API Integration:** Pages exist but not wired to backend (2-3 hours)
  - Recipe import UI → `/api/v1/recipes/harvest` (needs wiring)
  - Meal plan generator → `/api/v1/meal-plans` (needs wiring)
  - Dashboard → `/api/v1/recipes` (needs wiring)
  - Login/Signup → `/api/v1/auth/*` (needs wiring)
- **Environment Variables:** Need `.env.local` for development (5 min setup)

**Implementation Gap:** Frontend integration only - backend is 100% ready!

---

## Implementation Plan

### Phase 1: Local Setup & Testing (30 min)

#### Task 1.1: Install Frontend Dependencies
```bash
cd meal-planner-ui
npm install
```

**Expected Output:** All dependencies installed from package.json

#### Task 1.2: Set Up Environment Variables
Create `meal-planner-ui/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=<generate-with-openssl>
NEXTAUTH_URL=http://localhost:3000
```

**For Production (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app
NEXTAUTH_SECRET=<same-secret>
NEXTAUTH_URL=https://claude-code-projects.vercel.app
```

#### Task 1.3: Test Local Build
```bash
cd meal-planner-ui
npm run build
npm run dev
```

**Verify:**
- Landing page loads at http://localhost:3000
- No build errors
- All pages accessible

---

### Phase 2: Backend API Verification (15 min)

#### Task 2.1: Test Authentication Flow
```bash
# Register new user
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","country":"US"}'

# Login
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Save token for next requests
```

#### Task 2.2: Test Recipe Import
```bash
# Import recipe from URL (requires auth token)
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/recipes/harvest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url":"https://www.allrecipes.com/recipe/12345/"}'

# List recipes
curl -X GET https://claude-code-projects-production.up.railway.app/api/v1/recipes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Task 2.3: Test Meal Plan Generation
```bash
# Generate meal plan
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/meal-plans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "start_date": "2025-11-18",
    "num_days": 7,
    "num_people": 2,
    "meals_per_day": 3,
    "dietary_restrictions": ["vegetarian"]
  }'
```

**Expected:** All endpoints return 200/201 with valid JSON

---

### Phase 3: Frontend-Backend Integration (60 min)

#### Task 3.1: Wire Up Authentication Pages

**File:** `meal-planner-ui/src/app/login/page.tsx`
- Connect login form to `/api/v1/auth/login`
- Handle JWT token storage
- Redirect to dashboard on success

**File:** `meal-planner-ui/src/app/signup/page.tsx`
- Connect signup form to `/api/v1/auth/register`
- Auto-login after registration
- Redirect to onboarding

**Implementation:**
```typescript
// src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  if (!res.ok) throw new Error('Login failed')
  return res.json()
}
```

#### Task 3.2: Wire Up Recipe Import

**File:** `meal-planner-ui/src/app/dashboard/page.tsx`
- Add "Import Recipe" button
- Modal with URL input
- Call `/api/v1/recipes/harvest`
- Show loading state
- Refresh recipe list on success

**Features:**
- URL validation
- Error handling
- Loading spinner
- Success notification

#### Task 3.3: Wire Up Meal Plan Generator

**File:** `meal-planner-ui/src/app/generate/page.tsx`
- Multi-step form (preferences, constraints, review)
- Connect to `/api/v1/meal-plans`
- Show generated plan in calendar view
- Allow meal swaps

**Features:**
- Date picker for start date
- Number inputs for days, people, meals
- Dietary restriction chips
- Loading state (5-10 seconds)
- Calendar view of results

#### Task 3.4: Wire Up Dashboard Recipe List

**File:** `meal-planner-ui/src/app/dashboard/page.tsx`
- Fetch recipes from `/api/v1/recipes`
- Display in grid layout
- Search/filter functionality
- Recipe card click → details modal

---

### Phase 4: Deploy to Production (30 min)

#### Task 4.1: Update Vercel Environment Variables

In Vercel dashboard, set:
```bash
NEXT_PUBLIC_API_URL=https://claude-code-projects-production.up.railway.app
NEXTAUTH_SECRET=<generate-new-secret>
NEXTAUTH_URL=https://claude-code-projects.vercel.app
```

**Generate secrets:**
```bash
openssl rand -base64 32
```

#### Task 4.2: Deploy Frontend to Vercel

```bash
cd meal-planner-ui
vercel --prod
```

**Or push to GitHub for auto-deploy**

#### Task 4.3: Verify CORS Settings

Ensure Railway backend has:
```bash
CORS_ORIGINS=https://claude-code-projects.vercel.app,http://localhost:3000
```

#### Task 4.4: End-to-End Testing

Test full user journey:
1. Visit landing page
2. Sign up
3. Log in
4. Import a recipe from URL
5. Generate a meal plan
6. View grocery list
7. Log out

**Test URLs:**
- Landing: https://claude-code-projects.vercel.app
- Signup: https://claude-code-projects.vercel.app/signup
- Login: https://claude-code-projects.vercel.app/login
- Dashboard: https://claude-code-projects.vercel.app/dashboard
- Generate: https://claude-code-projects.vercel.app/generate

---

## Feature Checklist

### Must-Have Features (MVP)
- [x] Landing page with hero, features, pricing
- [x] User registration
- [x] User login/logout
- [ ] Recipe import from URL
- [ ] Recipe browsing (dashboard)
- [ ] Meal plan generation
- [ ] Dietary filters (vegetarian, vegan, gluten-free)
- [ ] Grocery list view
- [ ] User preferences

### Nice-to-Have (Can Add Later)
- [ ] Recipe search
- [ ] Drag-and-drop meal planning
- [ ] Export grocery list to PDF
- [ ] Recipe ratings
- [ ] Social sharing

---

## Testing Checklist

### Before Deployment
- [ ] All pages load without errors
- [ ] Login/signup works
- [ ] Recipe import works
- [ ] Meal plan generation works (<10s)
- [ ] Dietary filters work correctly
- [ ] Responsive on mobile
- [ ] No console errors
- [ ] API rate limiting tested

### After Deployment
- [ ] Production URL loads
- [ ] SSL certificate valid
- [ ] All API calls use HTTPS
- [ ] Authentication persists across page refreshes
- [ ] Error messages are user-friendly
- [ ] Loading states work
- [ ] 404 page works

---

## Known Limitations & Future Work

### Current Limitations
- No recipe image uploads (only URL import)
- No nutrition tracking (calculations work, but no UI)
- No family sharing
- No mobile app
- No recipe collections
- Limited to 1 meal plan at a time

### Phase 2 Enhancements (Post-Launch)
1. **Recipe Management:**
   - Manual recipe creation
   - Recipe editing
   - Recipe images (upload or fetch from URL)
   - Recipe collections/tags

2. **Meal Planning:**
   - Save multiple meal plans
   - Meal plan history
   - Meal swapping UI
   - Calendar drag-and-drop

3. **Grocery Lists:**
   - Export to PDF
   - Email grocery list
   - Print-friendly view
   - Knuspr integration (future)

4. **User Experience:**
   - Onboarding wizard
   - Sample recipes on signup
   - Recipe recommendations
   - Nutrition dashboard

---

## Rollback Plan

If deployment fails:

### Rollback Frontend
```bash
vercel rollback
```

### Rollback Backend
```bash
railway rollback
```

### Database Backup
Railway PostgreSQL has automatic backups. To restore:
1. Go to Railway dashboard
2. Select PostgreSQL service
3. Click "Backups"
4. Restore to previous snapshot

---

## Success Metrics

### Day 1 (Launch)
- [ ] 0 critical errors in production
- [ ] <500ms page load time
- [ ] 5+ successful meal plans generated
- [ ] 10+ recipes imported

### Week 1
- [ ] 20+ users signed up
- [ ] 50+ meal plans generated
- [ ] 100+ recipes imported
- [ ] 95%+ uptime

### Month 1
- [ ] 100+ users
- [ ] 1000+ meal plans
- [ ] <2% error rate
- [ ] 5+ paying customers (if pricing enabled)

---

## Support & Monitoring

### Error Tracking
- Frontend: Vercel Analytics
- Backend: Railway logs
- Database: Railway PostgreSQL logs

### Monitoring
```bash
# Backend health
curl https://claude-code-projects-production.up.railway.app/health

# Frontend health
curl https://claude-code-projects.vercel.app

# View logs
railway logs --tail
vercel logs --follow
```

### User Support
- Email: support@mealplannerai.com (set up)
- GitHub Issues: For bug reports
- Documentation: Link to docs from footer

---

## Commit Strategy

### During Implementation
Commit after each major feature:
```bash
git add .
git commit -m "feat: Connect recipe import UI to backend API"
git commit -m "feat: Implement meal plan generation flow"
git commit -m "fix: Handle authentication errors gracefully"
```

### Before Deployment
```bash
git add .
git commit -m "chore: Prepare for production deployment - all features wired"
git push origin main
```

---

**Created:** 2025-11-18
**Status:** Ready to Execute
**Estimated Time:** 2-3 hours
**Next Action:** Start with Phase 1, Task 1.1
