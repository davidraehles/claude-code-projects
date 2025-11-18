# Recipe Import & Create Features - Root Cause Analysis
**Date:** 2025-11-18
**Status:** Diagnosing feature gaps

---

## Problem Statement

Users cannot import recipes from URLs or create new recipes in the Vercel-deployed frontend. The dashboard has buttons linking to `/import` and `/create`, but these pages don't exist.

```
Error: 404 Not Found
Route: /import
Route: /create
```

---

## Three Possible Root Causes

### 🔴 ROOT CAUSE #1: Missing Page Components (MOST LIKELY - 95% Confidence)

**Description:**
The pages `/import` and `/create` were never implemented as Next.js route pages.

**Evidence:**
```bash
$ ls meal-planner-ui/src/app/
✅ dashboard/page.tsx
✅ generate/page.tsx
✅ login/page.tsx
❌ import/page.tsx (MISSING)
❌ create/page.tsx (MISSING)
```

**Why this happened:**
- Dashboard links to `/import` and `/create` (lines 98, 105)
- Planning document mentions these features as "In Progress"
- But actual page implementation was never completed

**Impact:**
- Clicking "Import from URL" → 404 error
- Clicking "Create Recipe" → 404 error
- Users cannot access these features at all

**Evidence in code:**
```typescript
// dashboard/page.tsx line 98
<Link href="/import" className="w-full sm:w-auto">
  <Button>Import from URL</Button>
</Link>

<Link href="/create" className="w-full sm:w-auto">
  <Button>Create Recipe</Button>
</Link>
```

---

### 🟡 ROOT CAUSE #2: API Endpoints Not Wired to Frontend (Secondary - 30% Confidence)

**Description:**
The page components exist but aren't calling the correct backend API endpoints.

**Likelihood:** LOW - This is secondary because:
1. We verified `useImportRecipe` hook exists and is configured
2. Backend `/api/v1/recipes/harvest` is working
3. Backend `/api/v1/recipes` (POST) endpoint exists for creation

**If this is the issue:**
- Pages might call wrong API endpoint URL
- Incorrect request payload format
- Missing error handling for API failures

**Evidence this is NOT the primary cause:**
```typescript
// hooks/queries/useRecipes.ts exists and has
export function useImportRecipe() {
  return useMutation({
    mutationFn: async (data: RecipeImportRequest) => {
      return api.importRecipe(data, token)  // ✅ Hook exists
    },
  })
}
```

---

### 🟡 ROOT CAUSE #3: Environment Variables or CORS Configuration (Secondary - 20% Confidence)

**Description:**
The pages exist and hooks work, but API calls fail due to:
- Missing `NEXT_PUBLIC_API_URL` in Vercel environment
- CORS errors blocking requests from Vercel to Railway backend
- API authentication token not being passed correctly

**Evidence this is NOT the primary cause:**
```bash
✅ Vercel deployment succeeded (build completed)
✅ Landing page loads (vercel.json has rewrites configured)
✅ Login/Signup pages work (auth endpoints called successfully)
✅ Other pages load (no 404 on /dashboard, /generate)
```

If CORS/env was broken, ALL API calls would fail, not just import/create.

---

## Diagnosis Verdict

### PRIMARY ROOT CAUSE: Missing Page Components (#1)

**Confidence: 95%**

The simple fact that:
1. Dashboard links to `/import` and `/create` (confirmed in code)
2. These directories don't exist (confirmed with `ls`)
3. Next.js returns 404 for missing routes (expected behavior)

**This is almost certainly the root cause.**

---

## Solution Map

### Immediate Fix (30 minutes)

Create the missing page components:

1. **`meal-planner-ui/src/app/import/page.tsx`**
   - Form to input recipe URL
   - Use `useImportRecipe()` hook
   - Call `api.importRecipe(data, token)`
   - Show loading state + success/error messages

2. **`meal-planner-ui/src/app/create/page.tsx`**
   - Form to manually create recipe
   - Use `useCreateRecipe()` hook
   - Call `api.createRecipe(data, token)`
   - Show loading state + success/error messages

### Implementation Steps

```typescript
// meal-planner-ui/src/app/import/page.tsx
'use client'

import { useState } from 'react'
import { useImportRecipe } from '@/hooks/queries/useRecipes'
import { useAuth } from '@/contexts/AuthContext'

export default function ImportPage() {
  const { user } = useAuth()
  const { mutate: importRecipe, isPending, error } = useImportRecipe()
  const [url, setUrl] = useState('')

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault()
    importRecipe({ url, source_type: 'html' })
  }

  return (
    <form onSubmit={handleImport}>
      <input value={url} onChange={(e) => setUrl(e.target.value)} />
      <button disabled={isPending}>
        {isPending ? 'Importing...' : 'Import Recipe'}
      </button>
      {error && <p>{error.message}</p>}
    </form>
  )
}
```

### Verification

After implementing:
```bash
# Deployment will automatically trigger
# Vercel should build successfully (assuming no new bugs)
# Test in production:
1. Visit https://claude-code-projects.vercel.app/dashboard
2. Click "Import from URL" button
3. Should navigate to /import page (no 404)
4. Should show recipe import form
```

---

## Secondary Issues (If Primary Fix Doesn't Solve It)

If pages are created but features still don't work:

### Check #1: API Call Failures
```bash
# In browser DevTools → Network tab
# Try importing a recipe
# Look for POST to /api/v1/recipes/harvest
# Check response: 200 or error code?
```

### Check #2: CORS Errors
```bash
# Console should show:
# ❌ CORS error: Access-Control-Allow-Origin missing
# (But this would affect all API calls, including login)
```

### Check #3: Environment Variables
```bash
# In Vercel dashboard:
# Settings → Environment Variables
# Verify: NEXT_PUBLIC_API_URL = correct Railway URL
# Verify: NEXTAUTH_SECRET = set
# Verify: NEXTAUTH_URL = https://claude-code-projects.vercel.app
```

---

## Recommendation

**IMMEDIATE ACTION:** Create `/import` and `/create` page components.

This will unblock the feature and allow users to:
1. Import recipes from any website
2. Create custom recipes manually
3. Both features fully functional with backend

**Estimated time:** 30 minutes
**Risk:** None (just missing UI)
**Benefit:** Features become usable

---

## Prevention

For future features:
1. ✅ Create page component FIRST (even if stub)
2. ✅ Wire to API hooks SECOND
3. ✅ Test locally BEFORE deployment
4. ✅ Verify production after deployment

This ensures no "missing route" surprises post-deployment.

---

**Analysis Date:** 2025-11-18
**Analyst:** Claude Code
**Status:** Ready for implementation
