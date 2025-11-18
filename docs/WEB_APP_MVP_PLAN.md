# Web App MVP Implementation Plan

**Date**: 2025-11-17
**Timeline**: 1-2 weeks
**Goal**: Launch a production-ready meal planning web app

---

## 🎯 Overview

Transform the backend meal planning API into a full-featured web application with:
- Beautiful, responsive UI
- User authentication
- Recipe management
- AI-powered meal planning
- Grocery list generation
- Mobile-first design

---

## 📋 Phase 1: Simple Frontend (3-4 days)

### Tech Stack

```
Frontend:  Next.js 14 (App Router) + TypeScript + Tailwind CSS
Auth:      NextAuth.js (Google OAuth + Email)
State:     React Context + SWR for data fetching
UI:        Headless UI + Heroicons
Deployment: Vercel (free tier)
Backend:   Existing FastAPI on Railway/Render
```

### Project Structure

```
meal-planner-ui/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx          # Recipe library
│   │   │   ├── plan/
│   │   │   │   └── page.tsx          # Meal plan generator
│   │   │   └── cart/
│   │   │       └── page.tsx          # Grocery list
│   │   ├── page.tsx                  # Landing page
│   │   ├── layout.tsx
│   │   └── api/
│   │       └── auth/
│   │           └── [...nextauth]/
│   │               └── route.ts
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── recipe/
│   │   │   ├── RecipeCard.tsx
│   │   │   ├── RecipeList.tsx
│   │   │   └── RecipeImport.tsx
│   │   ├── meal-plan/
│   │   │   ├── MealPlanForm.tsx
│   │   │   ├── MealPlanCalendar.tsx
│   │   │   └── MealPlanCard.tsx
│   │   ├── cart/
│   │   │   ├── GroceryList.tsx
│   │   │   └── GroceryItem.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       └── Modal.tsx
│   ├── lib/
│   │   ├── api.ts                    # API client
│   │   ├── auth.ts                   # NextAuth config
│   │   └── types.ts                  # TypeScript types
│   └── styles/
│       └── globals.css
├── public/
│   └── images/
├── .env.local
├── next.config.js
└── package.json
```

---

## 🏗️ Implementation Tasks

### Task 1: Project Setup (Day 1 - Morning)

**Time**: 2 hours

```bash
# Create Next.js app
npx create-next-app@latest meal-planner-ui --typescript --tailwind --app

# Install dependencies
cd meal-planner-ui
npm install next-auth swr @headlessui/react @heroicons/react
npm install -D @types/node @types/react
```

**Files to Create**:
- ✅ `.env.local` - Environment variables
- ✅ `src/lib/api.ts` - API client
- ✅ `src/lib/types.ts` - TypeScript interfaces

**Deliverable**: Basic Next.js app running locally

---

### Task 2: Landing Page (Day 1 - Afternoon)

**Time**: 3 hours

**File**: `src/app/page.tsx`

**Sections**:
1. **Hero**: "AI-Powered Meal Planning in Minutes"
   - Headline
   - Subheadline
   - CTA: "Start Planning Free"
   - Hero image/illustration

2. **Features**:
   - 🎯 Smart meal planning with dietary filters
   - 🔄 Automatic variety (no repetition)
   - 💰 Budget tracking
   - 🛒 One-click grocery lists

3. **How It Works**:
   - Step 1: Add your recipes
   - Step 2: Set your preferences
   - Step 3: Get your plan
   - Step 4: Shop with ease

4. **Pricing**:
   - Free: 5 plans/month, 20 recipes
   - Pro ($9/mo): Unlimited
   - Premium ($19/mo): Family + nutrition tracking

5. **CTA**: Sign up form

**Deliverable**: Beautiful landing page

---

### Task 3: Authentication (Day 2 - Morning)

**Time**: 3 hours

**Files**:
- `src/app/api/auth/[...nextauth]/route.ts`
- `src/app/(auth)/login/page.tsx`
- `src/app/(auth)/signup/page.tsx`
- `src/lib/auth.ts`

**Features**:
- Email/password authentication
- Google OAuth (optional)
- Protected routes
- User session management

**NextAuth Config**:
```typescript
import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

export const authOptions = {
  providers: [
    CredentialsProvider({
      async authorize(credentials) {
        // Call FastAPI /auth/login endpoint
        const res = await fetch(`${process.env.API_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: credentials?.email,
            password: credentials?.password,
          }),
        })

        const user = await res.json()
        if (res.ok && user) {
          return user
        }
        return null
      }
    })
  ],
  pages: {
    signIn: '/login',
  },
}
```

**Deliverable**: Working authentication flow

---

### Task 4: Dashboard - Recipe Library (Day 2 - Afternoon)

**Time**: 4 hours

**File**: `src/app/(dashboard)/dashboard/page.tsx`

**Components**:
- `RecipeCard.tsx` - Individual recipe display
- `RecipeList.tsx` - Grid of recipes
- `RecipeImport.tsx` - Import from URL

**Features**:
- View all recipes
- Search and filter
- Import recipe from URL
- View recipe details
- Edit/delete recipes

**Layout**:
```
┌─────────────────────────────────────┐
│ Header (Logo, Search, Profile)     │
├─────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│ │ 🍕  │ │ 🥗  │ │ 🍝  │ │ 🍲  │   │
│ │Pizza│ │Salad│ │Pasta│ │Soup │   │
│ └─────┘ └─────┘ └─────┘ └─────┘   │
│                                     │
│ [+ Import Recipe]                  │
└─────────────────────────────────────┘
```

**Deliverable**: Functional recipe library

---

### Task 5: Meal Plan Generator (Day 3 - Full Day)

**Time**: 6 hours

**File**: `src/app/(dashboard)/plan/page.tsx`

**Components**:
- `MealPlanForm.tsx` - Configuration form
- `MealPlanCalendar.tsx` - Calendar view
- `MealPlanCard.tsx` - Individual plan display

**Form Fields**:
```typescript
interface MealPlanFormData {
  startDate: Date
  numDays: number         // 1-30
  numPeople: number       // 1-20
  mealsPerDay: number     // 1-6
  dietaryRestrictions: string[]  // vegan, vegetarian, gluten_free
  excludedIngredients: string[]
  targetCaloriesPerDay?: number
  targetBudget?: number
}
```

**Features**:
- Multi-step form
- Dietary restrictions selector (chips)
- Calendar date picker
- Real-time preview
- Loading states during generation
- Error handling

**Flow**:
```
Step 1: Preferences → Step 2: Constraints → Step 3: Review → Generate!
```

**Calendar View**:
```
┌─── Monday ───┬─── Tuesday ──┬─── Wednesday ─┐
│ Breakfast:   │ Breakfast:   │ Breakfast:    │
│ 🥐 Croissant │ 🥞 Pancakes  │ 🍳 Eggs       │
│              │              │               │
│ Lunch:       │ Lunch:       │ Lunch:        │
│ 🥗 Salad     │ 🍕 Pizza     │ 🌮 Tacos      │
│              │              │               │
│ Dinner:      │ Dinner:      │ Dinner:       │
│ 🍝 Pasta     │ 🍲 Curry     │ 🍗 Chicken    │
└──────────────┴──────────────┴───────────────┘
```

**Deliverable**: Working meal plan generator

---

### Task 6: Grocery List (Day 4 - Morning)

**Time**: 3 hours

**File**: `src/app/(dashboard)/cart/page.tsx`

**Components**:
- `GroceryList.tsx` - Aggregated ingredient list
- `GroceryItem.tsx` - Checkable item
- Export buttons (PDF, Email, Print)

**Features**:
- Aggregated ingredients across all meals
- Checkboxes for marking purchased
- Grouped by category (produce, dairy, meat, etc.)
- Export to PDF
- Print-friendly view

**Layout**:
```
┌─────────────────────────────────────┐
│ Grocery List for Week of Nov 20    │
├─────────────────────────────────────┤
│ Produce                             │
│ ☐ Tomatoes (4)                      │
│ ☐ Lettuce (2 heads)                 │
│ ☐ Onions (3)                        │
│                                     │
│ Dairy                               │
│ ☐ Milk (2 liters)                   │
│ ☐ Cheese (500g)                     │
│                                     │
│ [📧 Email] [📄 PDF] [🖨️ Print]     │
└─────────────────────────────────────┘
```

**Deliverable**: Functional grocery list

---

### Task 7: Mobile Responsiveness (Day 4 - Afternoon)

**Time**: 3 hours

**Requirements**:
- Mobile-first design
- Responsive breakpoints (sm, md, lg, xl)
- Touch-friendly UI elements
- Hamburger menu for mobile
- Optimized images

**Breakpoints**:
```css
/* Tailwind defaults */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

**Deliverable**: Mobile-responsive app

---

## 📋 Phase 2: Polish User Experience (1-2 days)

### Task 8: Onboarding Flow (Day 5 - Morning)

**Time**: 3 hours

**Steps**:
1. **Welcome**: "Welcome to MealPlannerAI!"
2. **Add First Recipe**: Guide to import recipe
3. **Create First Plan**: Walk through meal plan form
4. **Done**: "You're all set!"

**Implementation**: Modal overlay with steps

**Deliverable**: Smooth onboarding

---

### Task 9: Sample Data (Day 5 - Afternoon)

**Time**: 2 hours

**Feature**: Pre-load 20 sample recipes for new users

**Categories**:
- 5 breakfast recipes
- 5 lunch recipes
- 10 dinner recipes
- Mix of dietary types (vegan, vegetarian, regular)

**Deliverable**: Sample recipes on signup

---

### Task 10: Visual Polish (Day 6 - Morning)

**Time**: 3 hours

**Improvements**:
- Recipe card images (use Unsplash API)
- Loading skeletons
- Empty states with illustrations
- Success/error toasts
- Smooth transitions and animations
- Consistent color palette

**Deliverable**: Polished UI

---

### Task 11: Drag-and-Drop Calendar (Day 6 - Afternoon)

**Time**: 3 hours

**Feature**: Drag recipes to calendar slots

**Library**: `@dnd-kit/core`

**Usage**:
```typescript
// Drag recipe from sidebar to calendar
<DndContext onDragEnd={handleDragEnd}>
  <Droppable id="monday-breakfast">
    <RecipeCard recipe={recipe} />
  </Droppable>
</DndContext>
```

**Deliverable**: Interactive meal planning

---

## 📋 Phase 3: Deploy Full Stack (1 day)

### Task 12: Environment Setup (Day 7 - Morning)

**Time**: 2 hours

**Backend Deployment (Railway/Render)**:
```bash
# Railway CLI
railway login
railway init
railway add --plugin postgresql
railway up
```

**Environment Variables**:
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=...
CORS_ORIGINS=https://meal-planner.vercel.app
```

**Deliverable**: Backend deployed

---

### Task 13: Frontend Deployment (Day 7 - Afternoon)

**Time**: 2 hours

**Vercel Deployment**:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd meal-planner-ui
vercel

# Set environment variables
vercel env add API_URL
vercel env add NEXTAUTH_SECRET
vercel env add NEXTAUTH_URL
```

**Environment Variables**:
```
API_URL=https://meal-planner-api.railway.app
NEXTAUTH_SECRET=...
NEXTAUTH_URL=https://meal-planner.vercel.app
```

**Deliverable**: Frontend deployed

---

### Task 14: Connect Frontend to Backend (Day 7 - Evening)

**Time**: 2 hours

**Tasks**:
- Update CORS settings in FastAPI
- Test all API endpoints
- Verify authentication flow
- Test meal plan generation
- Test grocery list export

**Deliverable**: Full-stack app working

---

## 📋 Phase 4: Landing Page (1 day)

### Task 15: Marketing Landing Page (Day 8)

**Time**: 6 hours

**Sections**:

1. **Hero**:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        🍽️ AI-Powered Meal Planning in Minutes

        Stop stressing about what to cook.
        Get personalized meal plans that fit your diet,
        budget, and schedule.

        [Start Planning Free →]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

2. **Features Grid**:
   - Smart dietary filters
   - Automatic variety
   - Budget optimization
   - Grocery list generation
   - Mobile-friendly
   - Export to PDF

3. **How It Works**:
   - Add recipes (or use our library)
   - Set preferences
   - Generate plan
   - Shop with ease

4. **Screenshots**:
   - Recipe library view
   - Meal plan generator
   - Calendar view
   - Grocery list

5. **Testimonials**: (Mock for MVP)
   > "Saved me 3 hours every week!" - Sarah M.

6. **Pricing Table**:
   ```
   ┌─────────────┬─────────────┬─────────────┐
   │    Free     │     Pro     │  Premium    │
   ├─────────────┼─────────────┼─────────────┤
   │ 5 plans/mo  │  Unlimited  │  Unlimited  │
   │ 20 recipes  │  Unlimited  │  Unlimited  │
   │ PDF export  │ PDF + Email │ PDF + Email │
   │             │ Priority    │ Priority    │
   │             │   support   │   support   │
   │             │             │  Nutrition  │
   │             │             │   tracking  │
   │             │             │   Family    │
   │             │             │   sharing   │
   ├─────────────┼─────────────┼─────────────┤
   │    $0       │    $9/mo    │   $19/mo    │
   │  [Start]    │  [Try Pro]  │ [Contact]   │
   └─────────────┴─────────────┴─────────────┘
   ```

7. **FAQ**:
   - How does it work?
   - Is it really AI-powered?
   - Can I add my own recipes?
   - What dietary restrictions are supported?
   - How much does it cost?

8. **Final CTA**:
   - Email signup
   - Social proof (# of users, plans generated)

**Deliverable**: Beautiful landing page

---

## 🚀 Distribution Channels

### Launch Week Activities

**Day 1**: Product Hunt Launch
- Prepare assets (screenshots, logo, demo video)
- Write compelling description
- Schedule launch for 12:01 AM PT
- Ask team/friends to upvote

**Day 2**: BetaList Submission
- Submit to BetaList.com
- Target early adopters
- Collect email signups

**Day 3**: Social Media
- Twitter/X: Thread about the product
- LinkedIn: Professional meal planning solution
- Instagram: Visual recipe cards
- TikTok: 30-second demo videos

**Day 4**: Facebook Groups
- Post in meal prep groups
- Healthy eating communities
- Budget cooking groups
- Provide value, not just promotion

**Day 5**: Reddit
- r/mealprep
- r/EatCheapAndHealthy
- r/fitness
- Follow subreddit rules, provide value

**Day 6-7**: Paid Ads Test
- Google Ads: "meal planning app"
- Facebook Ads: Target food bloggers, busy parents
- Budget: $100 test
- Track conversion rate

---

## 💰 Monetization Strategy

### Pricing Tiers

**Free Tier**:
- 5 meal plans per month
- 20 recipes
- Basic dietary filters
- PDF export
- **Target**: Acquire users, prove value

**Pro Tier ($9/month)**:
- Unlimited meal plans
- Unlimited recipes
- All dietary filters
- PDF + Email export
- Priority support
- **Target**: Power users, meal prep enthusiasts

**Premium Tier ($19/month)**:
- Everything in Pro
- Nutrition tracking
- Family sharing (up to 4 people)
- Knuspr integration (future)
- Custom meal templates
- **Target**: Families, fitness enthusiasts

### Revenue Projections

**Month 1-3** (Launch):
- 100 free users
- 5 Pro users ($45/mo)
- 0 Premium users
- **Total**: $45/mo

**Month 4-6** (Growth):
- 500 free users
- 25 Pro users ($225/mo)
- 5 Premium users ($95/mo)
- **Total**: $320/mo

**Month 7-12** (Scale):
- 2,000 free users
- 100 Pro users ($900/mo)
- 20 Premium users ($380/mo)
- **Total**: $1,280/mo

**Year 2 Target**: $5,000/mo MRR

---

## 📊 Success Metrics

### KPIs to Track

**Acquisition**:
- Website visitors
- Signup conversion rate
- Traffic sources

**Activation**:
- Users who add first recipe
- Users who generate first plan
- Time to first plan

**Engagement**:
- Meal plans generated per week
- Recipes added per user
- Return visit rate

**Retention**:
- Day 1, 7, 30 retention
- Churn rate
- Net Promoter Score (NPS)

**Revenue**:
- Free to Pro conversion rate
- Pro to Premium upgrade rate
- Monthly Recurring Revenue (MRR)
- Customer Lifetime Value (LTV)

### Analytics Setup

**Tools**:
- Google Analytics 4
- Mixpanel (user behavior)
- Stripe (payments)
- Vercel Analytics (performance)

---

## 🎯 Launch Checklist

### Pre-Launch (Week Before)

- [ ] All pages complete and tested
- [ ] Authentication working
- [ ] API integration tested
- [ ] Mobile responsive
- [ ] Performance optimized
- [ ] SEO metadata added
- [ ] Privacy policy page
- [ ] Terms of service page
- [ ] Contact/support email
- [ ] Analytics installed
- [ ] Error tracking (Sentry)

### Launch Day

- [ ] Deploy to production
- [ ] Test all features live
- [ ] Product Hunt launch
- [ ] Social media posts
- [ ] Email to waitlist
- [ ] Monitor errors
- [ ] Respond to feedback

### Post-Launch (Week After)

- [ ] Collect user feedback
- [ ] Fix critical bugs
- [ ] Improve onboarding
- [ ] Add requested features
- [ ] Iterate on pricing
- [ ] Plan next features

---

## 🔮 Future Enhancements

### Phase 2 (Month 2-3)

- Knuspr integration
- Nutrition tracking
- Recipe recommendations
- Social sharing
- Recipe ratings/reviews

### Phase 3 (Month 4-6)

- Mobile app (React Native)
- Family sharing
- Meal prep mode
- Custom dietary profiles
- Recipe collections

### Phase 4 (Month 7-12)

- AI recipe generation
- Voice commands
- Smart grocery delivery
- Subscription boxes
- B2B offering (nutritionists, gyms)

---

**Created**: 2025-11-17
**Timeline**: 1-2 weeks
**Goal**: Launch MVP and get first 100 users
**Success**: 5+ paying customers by end of month 1
