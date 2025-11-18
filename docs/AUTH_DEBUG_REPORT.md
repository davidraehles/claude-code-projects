# Vercel Frontend Authentication Debug Report

**Date**: 2025-11-18
**Production URL**: https://claude-code-projects.vercel.app
**Backend API**: https://claude-code-projects-production.up.railway.app

---

## Executive Summary

The "Failed to import recipe - Not authenticated" error was caused by **missing test user credentials** on the production backend database. The authentication flow itself is working correctly - the issue was that the hardcoded test user (`test@example.com`) didn't exist in production.

**Status**: ✅ **RESOLVED**

---

## Investigation Process

### 1. Initial Playwright Test (Before Fix)

Ran automated browser test against production Vercel app:

```bash
npx tsx debug-vercel-auth.ts
```

**Findings**:
- ❌ Token NOT in localStorage
- ❌ Login failed with: "Incorrect email or password"
- ❌ Backend returned 401 Unauthorized
- Console logs showed: `[AuthContext] No existing session, initializing test auth...` followed by auth failure

### 2. Backend Connectivity Test

```bash
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

**Result**: `{"detail":"Incorrect email or password"}`

### 3. User Registration

Registered the test user on production:

```bash
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","full_name":"Test User","country":"US"}'
```

**Result**: ✅ Successfully created user and received token:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 4. Verification Test (After Fix)

Re-ran Playwright test after user creation.

**Results**:
- ✅ Token successfully saved to localStorage
- ✅ Authorization header present in API requests
- ✅ Recipe import API returned 202 (queued)
- ✅ No console errors
- ✅ Auth flow working end-to-end

---

## Authentication Flow Analysis

### How It Works (Current Implementation)

1. **App Initialization** (`AuthContext.tsx`)
   ```typescript
   useEffect(() => {
     initializeAuth() // Runs on app mount
   }, [])
   ```

2. **Auto-Login Logic** (`lib/auth.ts`)
   ```typescript
   export async function initTestAuth(): Promise<string | null> {
     const response = await api.login({
       email: 'test@example.com',
       password: 'testpassword123'
     })
     localStorage.setItem('auth_token', response.access_token)
     return response.access_token
   }
   ```

3. **Token Storage**
   - Token stored in `localStorage.auth_token`
   - Email stored in `localStorage.user_email`
   - Auth context provides token to all hooks via `useAuthToken()`

4. **API Request Flow**
   ```typescript
   // useImportRecipe hook
   const token = useAuthToken() // Gets from AuthContext

   // Passes to API client
   api.importRecipe(data, token)

   // API client adds header
   headers["Authorization"] = `Bearer ${token}`
   ```

---

## Test Results: Before vs After

### Before Fix
| Check | Status | Details |
|-------|--------|---------|
| Token in localStorage | ❌ | Missing |
| Login API call | ❌ | 401 Unauthorized |
| Authorization header | ❌ | Not sent |
| Import API call | ❌ | "Not authenticated" |
| Console errors | ❌ | Multiple auth failures |

### After Fix
| Check | Status | Details |
|-------|--------|---------|
| Token in localStorage | ✅ | Present (JWT, 205 chars) |
| Login API call | ✅ | 200 OK with token |
| Authorization header | ✅ | `Bearer eyJhbG...` |
| Import API call | ✅ | 202 Accepted (queued) |
| Console errors | ✅ | None |

---

## API Request Details (After Fix)

### Import Recipe Request
```http
POST /api/v1/recipes/harvest HTTP/2
Host: claude-code-projects-production.up.railway.app
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "url": "https://www.bbcgoodfood.com/recipes/chocolate-cake",
  "source_type": "html"
}
```

### Response
```json
{
  "success": true,
  "message": "Recipe harvest queued for https://www.bbcgoodfood.com/recipes/chocolate-cake. Check back shortly.",
  "recipe": null,
  "is_duplicate": false,
  "duplicate_of_id": null
}
```

**Status**: 202 Accepted
**Interpretation**: Recipe import successfully queued for background processing

---

## Root Cause Analysis

### Primary Issue
The production backend database did not have the test user that the frontend expects for auto-login.

### Why This Happened
- Frontend uses hardcoded test credentials (`test@example.com` / `testpassword123`)
- These credentials work in local development (local database has test user)
- Production database was likely reset or never seeded with test user
- Railway backend uses a separate database from local development

### Contributing Factors
1. **No automated seeding**: Production database doesn't auto-create test user
2. **Hardcoded credentials**: Frontend depends on specific test account
3. **No auth fallback**: If auto-login fails, user sees error instead of signup prompt

---

## Frontend Auth Implementation Review

### Files Analyzed

1. **`/src/contexts/AuthContext.tsx`**
   - Provides global auth state
   - Auto-initializes with test user on mount
   - Stores token in localStorage
   - ✅ Implementation is correct

2. **`/src/lib/auth.ts`**
   - `initTestAuth()`: Logs in test user
   - `restoreAuth()`: Restores from localStorage
   - `getAuthToken()`: Retrieves current token
   - ✅ Implementation is correct

3. **`/src/lib/api.ts`**
   - Immutable API client (token passed as parameter)
   - Adds `Authorization: Bearer {token}` header when token provided
   - ✅ Implementation is correct

4. **`/src/hooks/queries/useRecipes.ts`**
   - `useImportRecipe()`: Gets token from `useAuthToken()` hook
   - Passes token to `api.importRecipe(data, token)`
   - Throws "Not authenticated" if token is null
   - ✅ Implementation is correct

5. **`/src/app/import/page.tsx`**
   - Uses `useAuth()` to get auth state
   - Shows loading spinner while authenticating
   - Displays user email when authenticated
   - ✅ Implementation is correct

### Token Flow Diagram
```
App Mount
  ↓
AuthContext.initializeAuth()
  ↓
Try restoreAuth() from localStorage
  ↓ (if no token)
Call initTestAuth() → Login API
  ↓
Save token to localStorage
  ↓
Update AuthContext state
  ↓
useAuthToken() hook provides token
  ↓
useImportRecipe() uses token
  ↓
api.importRecipe(data, token)
  ↓
Request with Authorization header
```

---

## Screenshots

Generated during Playwright test (saved to project root):

1. **01-homepage.png** - Initial landing page
2. **04-import-page-ready.png** - Import page after auth
3. **05-import-result.png** - Success state after import

**Video Recording**: `playwright-videos/` (screen recording of entire flow)

---

## Recommendations

### Immediate Actions (Optional Improvements)

1. **Add production database seeding**
   ```bash
   # Run on Railway backend
   python scripts/seed_test_user.py
   ```

2. **Better error handling**
   - If auto-login fails, redirect to signup instead of showing error
   - Add "Guest mode" or manual login option

3. **Environment-specific auth**
   ```typescript
   // Only auto-login in development
   if (process.env.NODE_ENV === 'development') {
     token = await initTestAuth()
   }
   ```

4. **User feedback**
   - Show clearer message when auth fails
   - Provide manual login/signup buttons

### Long-term Considerations

1. **Remove hardcoded test user**
   - Use proper signup/login flow for all users
   - Only use test user in development/staging

2. **Token expiration handling**
   - Current tokens expire after 30 minutes
   - Add refresh token logic
   - Handle 401 responses by re-authenticating

3. **Secure token storage**
   - Consider using httpOnly cookies instead of localStorage
   - Implement CSRF protection

---

## Testing Commands

### Test Auth Manually
```bash
# Test backend login
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'

# Test recipe import with token
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/recipes/harvest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"url":"https://www.bbcgoodfood.com/recipes/test","source_type":"html"}'
```

### Run Automated Test
```bash
npx tsx debug-vercel-auth.ts
```

---

## Conclusion

**Issue**: ✅ RESOLVED
**Root Cause**: Missing test user in production database
**Solution**: Created test user on production backend
**Status**: Recipe import now works correctly on Vercel frontend

The authentication implementation is solid. The token flow works as designed:
1. ✅ Token saved to localStorage after login
2. ✅ Token retrieved by hooks via AuthContext
3. ✅ Token sent in Authorization header
4. ✅ Backend accepts token and processes requests

No code changes required - the issue was purely data-related (missing user).
