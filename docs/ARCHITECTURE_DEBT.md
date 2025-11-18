# Architecture Debt - MVI/Redux Pattern Violations

**Generated**: 2025-11-17
**Status**: All tasks tagged with `[ARCHITECTURE-DEBT]`

## Overview

This document tracks architectural debt identified during the MVI/Redux architecture audit of the meal-planner-ui frontend. All violations of clean architecture principles are catalogued with remediation tasks.

---

## Critical Priority Tasks

### ARCH-001: Eliminate API Client State Mutation
**Priority**: 🔴 Critical
**Tag**: `[ARCHITECTURE-DEBT]` `[IMMUTABILITY]`
**Estimated Effort**: 4 hours

**Problem**:
The API client (`src/lib/api.ts`) directly mutates its token state, violating the immutability principle:

```typescript
class ApiClient {
  private token: string | null = null

  setToken(token: string) {
    this.token = token  // ❌ DIRECT MUTATION
  }
}
```

This creates a global mutable singleton that's shared across the entire application, making state changes unpredictable and untraceable.

**Why It Violates MVI/Redux**:
- State mutations should be pure and traceable
- No action/event is dispatched when token changes
- Impossible to replay or debug auth state changes
- Violates Single Source of Truth (token in localStorage + API client)

**Acceptance Criteria**:
- [ ] Remove mutable token state from ApiClient
- [ ] Token passed as parameter to request methods
- [ ] Auth state managed by centralized store/context
- [ ] All API calls receive token from single source
- [ ] Token changes traceable through action/event log

**Implementation Guide**:
```typescript
// Before (anti-pattern)
api.setToken(token)
const recipes = await api.getRecipes()

// After (pure)
const recipes = await api.getRecipes(authState.token)
```

---

### ARCH-002: Implement Single Source of Truth for Auth State
**Priority**: 🔴 Critical
**Tag**: `[ARCHITECTURE-DEBT]` `[SINGLE-SOURCE]`
**Estimated Effort**: 8 hours

**Problem**:
Authentication state is duplicated across 5+ components:

```typescript
// Duplicated in: dashboard, generate, meal-plans, grocery-carts, meal-plans/[id]
const [authLoading, setAuthLoading] = useState(true)
const [userEmail, setUserEmail] = useState<string | null>(null)
const [error, setError] = useState<string | null>(null)

useEffect(() => {
  async function authenticate() {
    const restored = restoreAuth()
    if (!restored) await initTestAuth()
    setUserEmail(getCurrentUserEmail())
    setAuthLoading(false)
  }
  authenticate()
}, [])
```

**Why It Violates MVI/Redux**:
- Violates Single Source of Truth principle
- Each component has its own auth state copy
- State changes don't propagate to other components
- 5x redundant initialization logic
- Race conditions possible if auth state changes mid-session

**Acceptance Criteria**:
- [ ] Create React Context for auth state
- [ ] Single `AuthProvider` at app root
- [ ] All components consume from context
- [ ] Remove duplicate `useState` and `useEffect` auth logic
- [ ] Auth state changes propagate to all consumers
- [ ] Authentication initialized once at app startup

**Implementation Guide**:
```typescript
// Create src/contexts/AuthContext.tsx
interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
}

interface AuthActions {
  login: (credentials) => Promise<void>
  logout: () => void
  restoreSession: () => Promise<void>
}

const AuthContext = createContext<AuthState & AuthActions>()

// Usage in components
const { user, token, loading } = useAuth()
```

---

### ARCH-003: Centralize Side Effects with TanStack Query
**Priority**: 🔴 Critical
**Tag**: `[ARCHITECTURE-DEBT]` `[SIDE-EFFECTS]`
**Estimated Effort**: 2 days

**Problem**:
Side effects (API calls, data fetching) are scattered across components in `useEffect` hooks:

```typescript
// Pattern repeated in 5+ components
useEffect(() => {
  if (authLoading) return

  async function loadRecipes() {
    try {
      setLoading(true)
      const response = await api.getRecipes(1, 50)
      setRecipes(response.items)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  loadRecipes()
}, [authLoading])
```

**Why It Violates MVI/Redux**:
- Side effects should be isolated from component logic
- No separation between data fetching and UI rendering
- Duplicated loading/error state management (5+ components)
- No caching - data refetched on every navigation
- No request deduplication or cancellation
- Side effects can't be replayed or tested in isolation

**Acceptance Criteria**:
- [ ] Install and configure TanStack Query (React Query)
- [ ] Create query hooks for each API endpoint
- [ ] Remove direct API calls from components
- [ ] Remove loading/error state management from components
- [ ] Enable automatic caching and refetching
- [ ] Implement request cancellation on unmount
- [ ] Add query invalidation on mutations

**Implementation Guide**:
```typescript
// src/queries/recipes.ts
export const useRecipes = () => {
  return useQuery({
    queryKey: ['recipes'],
    queryFn: () => api.getRecipes(1, 50),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Component usage
const { data: recipes, isLoading, error } = useRecipes()
```

**Files to Refactor**:
- `src/app/dashboard/page.tsx` (lines 54-70)
- `src/app/meal-plans/page.tsx` (lines 42-60)
- `src/app/meal-plans/[id]/page.tsx`
- `src/app/grocery-carts/[id]/page.tsx`
- `src/app/generate/page.tsx` (lines 81-112)

---

## High Priority Tasks

### ARCH-004: Implement Action/Intent Layer for State Changes
**Priority**: 🟠 High
**Tag**: `[ARCHITECTURE-DEBT]` `[INTENT-SEMANTICS]`
**Estimated Effort**: 3 days

**Problem**:
No semantic action layer - state changes via direct `setState` calls:

```typescript
// Current: Direct imperative mutations
const toggleRestriction = (restriction: string) => {
  setSelectedRestrictions((prev) =>
    prev.includes(restriction)
      ? prev.filter((r) => r !== restriction)
      : [...prev, restriction]
  )
}

// No action describing user intent
// No trace of why state changed
// Can't replay state changes
```

**Why It Violates MVI/Redux**:
- No semantic actions expressing user intent
- State changes are anonymous function calls
- Can't log, replay, or debug state transitions
- No event sourcing or time-travel debugging
- Violates "actions as events" principle

**Acceptance Criteria**:
- [ ] Define action types for all user intents
- [ ] Implement action creators for common operations
- [ ] Use `useReducer` for complex state (form state, cart state)
- [ ] Actions should be descriptive events (USER_TOGGLED_RESTRICTION)
- [ ] Enable action logging in development
- [ ] State changes traceable to specific user actions

**Implementation Guide**:
```typescript
// Define action types
type MealPlanAction =
  | { type: 'USER_TOGGLED_DIETARY_RESTRICTION'; payload: string }
  | { type: 'USER_SET_START_DATE'; payload: string }
  | { type: 'USER_CHANGED_NUM_PEOPLE'; payload: number }
  | { type: 'MEAL_PLAN_GENERATION_STARTED' }
  | { type: 'MEAL_PLAN_GENERATION_SUCCEEDED'; payload: MealPlan }
  | { type: 'MEAL_PLAN_GENERATION_FAILED'; payload: string }

// Reducer for meal plan form
function mealPlanFormReducer(state: MealPlanFormState, action: MealPlanAction) {
  switch (action.type) {
    case 'USER_TOGGLED_DIETARY_RESTRICTION':
      return {
        ...state,
        restrictions: state.restrictions.includes(action.payload)
          ? state.restrictions.filter(r => r !== action.payload)
          : [...state.restrictions, action.payload]
      }
    // ... other cases
  }
}

// Component usage
const [state, dispatch] = useReducer(mealPlanFormReducer, initialState)

dispatch({
  type: 'USER_TOGGLED_DIETARY_RESTRICTION',
  payload: 'vegan'
})
```

**Files to Refactor**:
- `src/app/generate/page.tsx` (10+ useState calls → 1 useReducer)
- `src/app/grocery-carts/[id]/page.tsx` (checkbox toggles)
- Any complex form or multi-step flow

---

### ARCH-005: Extract Pure State Transition Logic
**Priority**: 🟠 High
**Tag**: `[ARCHITECTURE-DEBT]` `[PURE-FUNCTIONS]`
**Estimated Effort**: 2 days

**Problem**:
State transition logic mixed with side effects in component handlers:

```typescript
const handleGenerate = async (e: React.FormEvent) => {
  e.preventDefault()
  setError(null)  // State mutation
  setGenerating(true)  // State mutation

  try {
    // Side effect (API call) mixed with state logic
    const mealPlan = await api.createMealPlan({...})

    console.log('✅ Meal plan created:', mealPlan)  // Side effect
    router.push(`/meal-plans/${mealPlan.id}`)  // Side effect
  } catch (err: any) {
    console.error('Failed:', err)  // Side effect
    setError(err.message)  // State mutation
    setGenerating(false)  // State mutation
  }
}
```

**Why It Violates MVI/Redux**:
- State transitions not pure (mixed with async operations)
- Can't test state logic without mocking API
- Can't replay state transitions
- Violates "reducers must be pure" principle

**Acceptance Criteria**:
- [ ] Extract state transition logic to pure functions
- [ ] Separate state logic from side effects
- [ ] State transitions should be synchronous and deterministic
- [ ] Side effects handled in separate layer (middleware/effects)
- [ ] Pure functions testable without mocking

**Implementation Guide**:
```typescript
// Pure state transition
function handleGenerationResult(
  state: GeneratorState,
  result: { success: true; mealPlan: MealPlan } | { success: false; error: string }
): GeneratorState {
  if (!result.success) {
    return {
      ...state,
      generating: false,
      error: result.error
    }
  }

  return {
    ...state,
    generating: false,
    error: null,
    lastGenerated: result.mealPlan
  }
}

// Side effect handler (separate)
async function generateMealPlanEffect(params: MealPlanParams) {
  try {
    const mealPlan = await api.createMealPlan(params)
    return { success: true, mealPlan }
  } catch (err) {
    return { success: false, error: err.message }
  }
}

// Component orchestrates (but logic is pure and testable)
const result = await generateMealPlanEffect(formState)
setState(state => handleGenerationResult(state, result))
```

---

### ARCH-006: Eliminate Race Conditions with AbortController
**Priority**: 🟠 High
**Tag**: `[ARCHITECTURE-DEBT]` `[SIDE-EFFECTS]`
**Estimated Effort**: 1 day

**Problem**:
No request cancellation - setting state on unmounted components:

```typescript
useEffect(() => {
  if (authLoading) return

  async function loadRecipes() {
    setLoading(true)
    const response = await api.getRecipes(1, 50)
    setRecipes(response.items)  // ❌ May execute after unmount
    setFilteredRecipes(response.items)
  }

  loadRecipes()
  // ❌ No cleanup function - request continues after unmount
}, [authLoading])
```

**Why It Violates MVI/Redux**:
- Side effects not properly managed
- Memory leaks from unmounted component updates
- Violates "effects should be cancellable" principle

**Acceptance Criteria**:
- [ ] Add AbortController to all fetch operations
- [ ] Implement cleanup in useEffect hooks
- [ ] No state updates after component unmount
- [ ] Add `isMounted` checks or AbortSignal to API client
- [ ] Warning-free in React StrictMode

**Implementation Guide**:
```typescript
useEffect(() => {
  const abortController = new AbortController()

  async function loadRecipes() {
    try {
      setLoading(true)
      const response = await api.getRecipes(1, 50, {
        signal: abortController.signal
      })

      if (!abortController.signal.aborted) {
        setRecipes(response.items)
        setFilteredRecipes(response.items)
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message)
      }
    } finally {
      if (!abortController.signal.aborted) {
        setLoading(false)
      }
    }
  }

  loadRecipes()

  return () => {
    abortController.abort()  // Cleanup on unmount
  }
}, [])
```

**Alternative**: This is automatically handled by TanStack Query (ARCH-003)

---

## Medium Priority Tasks

### ARCH-007: Create Custom Hooks for Repeated Patterns
**Priority**: 🟡 Medium
**Tag**: `[ARCHITECTURE-DEBT]` `[DRY]`
**Estimated Effort**: 1.5 days

**Problem**:
Repeated useEffect patterns for authentication in 5+ components.

**Acceptance Criteria**:
- [ ] Create `useAuthenticatedData()` hook
- [ ] Create `useProtectedPage()` hook
- [ ] Remove duplicate useEffect auth logic
- [ ] Centralize loading/error patterns

**Implementation Guide**:
```typescript
// src/hooks/useAuthenticatedData.ts
export function useAuthenticatedData<T>(
  fetcher: () => Promise<T>
) {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading || !isAuthenticated) return

    const abortController = new AbortController()

    fetcher()
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))

    return () => abortController.abort()
  }, [authLoading, isAuthenticated])

  return { data, loading, error }
}

// Usage
const { data: recipes, loading } = useAuthenticatedData(() =>
  api.getRecipes(1, 50)
)
```

---

### ARCH-008: Implement Global Error Boundary
**Priority**: 🟡 Medium
**Tag**: `[ARCHITECTURE-DEBT]` `[ERROR-HANDLING]`
**Estimated Effort**: 4 hours

**Problem**:
Error handling scattered across components with try/catch blocks.

**Acceptance Criteria**:
- [ ] Create ErrorBoundary component
- [ ] Wrap app with error boundary
- [ ] Centralize error display logic
- [ ] Add error recovery mechanisms
- [ ] Log errors to error tracking service

**Implementation Guide**:
```typescript
// src/components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to error tracking (Sentry, etc.)
    console.error('Uncaught error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />
    }
    return this.props.children
  }
}
```

---

### ARCH-009: Add Request Deduplication
**Priority**: 🟡 Medium
**Tag**: `[ARCHITECTURE-DEBT]` `[PERFORMANCE]`
**Estimated Effort**: 1 day

**Problem**:
Multiple components can trigger same API call simultaneously.

**Acceptance Criteria**:
- [ ] Implement request deduplication in API client
- [ ] Cache in-flight requests
- [ ] Return same Promise for duplicate requests
- [ ] Add time-based cache invalidation

**Note**: This is automatically handled by TanStack Query (ARCH-003)

---

### ARCH-010: Implement State Persistence Layer
**Priority**: 🟡 Medium
**Tag**: `[ARCHITECTURE-DEBT]` `[PERSISTENCE]`
**Estimated Effort**: 1 day

**Problem**:
Form state lost on navigation/refresh (grocery cart checkboxes, form inputs).

**Acceptance Criteria**:
- [ ] Add state persistence middleware
- [ ] Persist form state to localStorage
- [ ] Restore state on mount
- [ ] Implement state hydration
- [ ] Add versioning to prevent corruption

**Implementation Guide**:
```typescript
// src/hooks/usePersistedState.ts
export function usePersistedState<T>(key: string, initialValue: T) {
  const [state, setState] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue

    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : initialValue
  })

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(state))
  }, [key, state])

  return [state, setState] as const
}
```

---

## Low Priority Tasks

### ARCH-011: Add Redux DevTools Integration
**Priority**: 🟢 Low
**Tag**: `[ARCHITECTURE-DEBT]` `[DEVTOOLS]`
**Estimated Effort**: 4 hours

**Problem**:
No time-travel debugging or state inspection tools.

**Acceptance Criteria**:
- [ ] Install Redux DevTools extension support
- [ ] Log all actions to DevTools
- [ ] Enable state snapshots
- [ ] Add action replay capability

**Note**: Only applicable after implementing action layer (ARCH-004)

---

### ARCH-012: Implement Optimistic Updates
**Priority**: 🟢 Low
**Tag**: `[ARCHITECTURE-DEBT]` `[UX]`
**Estimated Effort**: 2 days

**Problem**:
UI waits for server response before updating (poor UX).

**Acceptance Criteria**:
- [ ] Implement optimistic updates for mutations
- [ ] Rollback on error
- [ ] Show loading indicators for async operations
- [ ] Improve perceived performance

**Note**: TanStack Query provides this automatically (ARCH-003)

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
1. **ARCH-002**: Implement Auth Context (Single Source of Truth)
2. **ARCH-001**: Refactor API Client (Remove Mutation)
3. **ARCH-008**: Add Error Boundary

### Phase 2: Data Layer (Week 3-4)
4. **ARCH-003**: Integrate TanStack Query
5. **ARCH-006**: Add AbortController cleanup
6. **ARCH-009**: Request deduplication (via TanStack Query)

### Phase 3: State Management (Week 5-6)
7. **ARCH-004**: Implement Action/Intent layer
8. **ARCH-005**: Extract pure state transitions
9. **ARCH-007**: Create custom hooks

### Phase 4: Polish (Week 7-8)
10. **ARCH-010**: State persistence
11. **ARCH-011**: DevTools integration
12. **ARCH-012**: Optimistic updates

---

## Metrics for Success

**Before Refactoring**:
- 7 `useState` calls per component (avg)
- 3 `useEffect` hooks per component (avg)
- 0% code reuse for auth logic
- No caching (100% of navigations refetch data)
- ~1,150 lines of duplicated state management code

**After Refactoring**:
- 2-3 `useState` calls per component (avg) - 60% reduction
- 1 `useEffect` hook per component (avg) - 66% reduction
- 100% code reuse for auth logic (via Context)
- 95%+ cache hit rate (via TanStack Query)
- ~300 lines of state management code - 74% reduction
- Time-travel debugging enabled
- All state transitions traceable

---

## References

- [MVI Pattern](https://hannesdorfmann.com/android/mosby3-mvi-1/)
- [Redux Best Practices](https://redux.js.org/style-guide/style-guide)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [React Hooks Best Practices](https://react.dev/reference/react)

---

**Generated by**: Architecture Audit Tool
**Date**: 2025-11-17
**Audit Version**: 1.0
