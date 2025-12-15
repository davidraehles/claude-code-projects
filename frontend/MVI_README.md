# MVI Pattern Implementation

## Overview

This application has been refactored to implement the **Model-View-Intent (MVI)** architecture pattern. MVI is a unidirectional data flow pattern that provides:

- ✅ **Predictable State Transitions**: All state changes flow through intents
- ✅ **Time-Travel Debugging**: Built-in DevTools for state inspection
- ✅ **Type Safety**: Fully typed intents, state, and selectors
- ✅ **Testability**: Pure functions are easy to test
- ✅ **Middleware System**: Side effects handled cleanly
- ✅ **Performance**: Optimized re-renders with selectors

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  User Action → Intent → Middleware → Reducer        │
│                              ↓                       │
│                            Model                     │
│                              ↓                       │
│                          Selectors                   │
│                              ↓                       │
│                            View                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Directory Structure

```
frontend/src/
├── mvi/                       # Core MVI infrastructure
│   ├── core/
│   │   ├── types.ts          # Base types (Intent, Model, etc.)
│   │   ├── createMVI.ts      # MVI factory function
│   │   ├── middleware.ts     # Built-in middleware
│   │   └── devtools.ts       # DevTools & debugging
│   └── utils/
│       └── testing.ts        # Test utilities
│
└── features/                  # Feature modules (MVI)
    ├── groceryCart/
    │   ├── intents/          # Intent definitions
    │   │   ├── types.ts      # Intent types
    │   │   └── creators.ts   # Intent creators
    │   ├── model/            # Model layer
    │   │   ├── state.ts      # State interface
    │   │   ├── reducer.ts    # Pure reducer
    │   │   └── selectors.ts  # Selectors
    │   ├── views/            # View components
    │   │   └── *.tsx         # React components
    │   ├── middleware/       # Feature middleware
    │   ├── __tests__/        # Tests
    │   └── index.ts          # Module export
    │
    └── mealPlan/
        └── (same structure)
```

## Features Implemented

### 1. Grocery Cart (✅ Complete)

**Location**: `features/groceryCart/`

**Intents**:
- `USER_TOGGLED_ITEM` - Toggle item checkbox
- `USER_CHECKED_ALL_ITEMS` - Check all items
- `USER_UNCHECKED_ALL_ITEMS` - Uncheck all items
- `USER_SET_VIEW_MODE` - Switch between recipe/category view
- `USER_GENERATE_CART` - Generate cart from meal plan
- `CART_GENERATED` - Cart generation succeeded
- `CART_GENERATION_FAILED` - Cart generation failed
- `CART_RESET` - Reset cart state

**State**:
```typescript
interface GroceryCartState {
  checkedItems: Set<string>;
  viewMode: 'recipe' | 'category';
  isGenerating: boolean;
  error: string | null;
  generatedCart: { cartId: number; items: string[] } | null;
}
```

**Usage**:
```typescript
import { useGroceryCart, groceryCartIntents } from '@/features/groceryCart';

function MyComponent() {
  const { state, dispatch, select } = useGroceryCart();
  
  const checkedCount = select(selectCheckedCount);
  
  return (
    <button onClick={() => dispatch(groceryCartIntents.toggleItem({ ingredient: 'Milk' }))}>
      Toggle Milk ({checkedCount} checked)
    </button>
  );
}
```

### 2. Meal Plan (✅ Complete)

**Location**: `features/mealPlan/`

**Intents**:
- `USER_SET_START_DATE` - Set meal plan start date
- `USER_SET_NUM_DAYS` - Set number of days
- `USER_SET_NUM_PEOPLE` - Set number of people
- `USER_SET_MEALS_PER_DAY` - Set meals per day
- `USER_TOGGLED_DIETARY_RESTRICTION` - Toggle dietary restriction
- `USER_SET_EXCLUDED_INGREDIENTS` - Set excluded ingredients
- `USER_RESET_FORM` - Reset form
- `USER_SUBMIT_MEAL_PLAN` - Submit meal plan
- `GENERATING_MEAL_PLAN` - Generation started
- `MEAL_PLAN_GENERATED` - Generation succeeded
- `MEAL_PLAN_GENERATION_FAILED` - Generation failed

**State**:
```typescript
interface MealPlanState {
  startDate: string;
  numDays: number;
  numPeople: number;
  mealsPerDay: number;
  selectedRestrictions: string[];
  excludedIngredients: string;
  isSubmitting: boolean;
  error: string | null;
  generatedMealPlan: { id: number; data: any } | null;
}
```

## Using the MVI Pattern

### 1. Reading State

Use selectors to access state:

```typescript
const { select } = useMealPlan();

const numDays = select(selectNumDays);
const totalMeals = select(selectTotalMeals);
const isFormValid = select(selectIsFormValid);
```

### 2. Dispatching Intents

All user actions dispatch intents:

```typescript
const { dispatch } = useMealPlan();

// Simple intent
dispatch(mealPlanIntents.resetForm());

// Intent with payload
dispatch(mealPlanIntents.setNumDays({ numDays: 5 }));
```

### 3. Creating New Features

See `docs/MVI_PATTERN.md` for a complete guide on creating new MVI features.

## Middleware

The MVI pattern uses middleware for side effects:

### Built-in Middleware

1. **DevTools**: Time-travel debugging (enabled in development)
2. **Logger**: Logs all intents and state transitions
3. **Analytics**: Tracks user interactions
4. **Persistence**: Saves state to localStorage
5. **Debounce**: Debounces high-frequency intents
6. **Validation**: Validates intent payloads

### Feature-Specific Middleware

Each feature can define custom middleware:

```typescript
// Grocery Cart API middleware
export function createCartApiMiddleware(apiClient) {
  return (store) => (next) => async (intent) => {
    next(intent);
    
    if (intent.type === 'USER_GENERATE_CART') {
      try {
        const result = await apiClient.generateCart(intent.payload.mealPlanId);
        store.dispatch(groceryCartIntents.cartGenerated({
          cartId: result.id,
          items: result.items,
        }));
      } catch (error) {
        store.dispatch(groceryCartIntents.cartGenerationFailed({
          error: error.message,
        }));
      }
    }
  };
}
```

## Testing

### Testing Reducers

```typescript
import { mealPlanReducer } from './reducer';
import { mealPlanIntents } from '../intents/creators';

it('sets number of days', () => {
  const state = createInitialState();
  const nextState = mealPlanReducer(
    state,
    mealPlanIntents.setNumDays({ numDays: 5 })
  );
  
  expect(nextState.numDays).toBe(5);
});
```

### Testing Selectors

```typescript
import { selectTotalMeals } from './selectors';

it('calculates total meals', () => {
  const state = { numDays: 7, mealsPerDay: 3 };
  expect(selectTotalMeals(state)).toBe(21);
});
```

### Testing Components

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('increments counter on click', async () => {
  render(<MyComponent />);
  
  await userEvent.click(screen.getByText('Increment'));
  
  expect(screen.getByText(/Count: 1/)).toBeInTheDocument();
});
```

## Debugging

### DevTools Console

Access MVI DevTools in the browser console:

```javascript
// Get feature state history
window.__MVI_DEVTOOLS__.GroceryCart.getHistory();

// Get state at specific index
window.__MVI_DEVTOOLS__.GroceryCart.getState(5);

// Clear history
window.__MVI_DEVTOOLS__.GroceryCart.clearHistory();
```

### Performance Monitoring

The performance middleware tracks slow intents:

```
[GroceryCart] Slow intent detected: USER_TOGGLED_ITEM took 23.45ms
```

## Migration Guide

### From useState

**Before**:
```typescript
const [count, setCount] = useState(0);
const increment = () => setCount(count + 1);
```

**After**:
```typescript
const { state, dispatch } = useCounter();
const increment = () => dispatch(counterIntents.increment({ amount: 1 }));
```

### From useReducer

**Before**:
```typescript
const [state, dispatch] = useReducer(reducer, initialState);
```

**After**:
```typescript
const { state, dispatch } = useCounter();
// Same dispatch, but with middleware and DevTools!
```

## Best Practices

1. **Intent Naming**: Use `USER_*`, `SYSTEM_*`, `API_*` prefixes
2. **State Design**: Keep state flat, use Sets/Maps for lookups
3. **Selectors**: Always use selectors, never access state directly
4. **Middleware**: Keep focused on single responsibility
5. **Testing**: Test reducers and selectors independently

## Resources

- Full Documentation: `/frontend/docs/MVI_PATTERN.md`
- Example: `/frontend/src/features/groceryCart/`
- Tests: `/frontend/src/features/*/tests__/`

## Support

For questions or issues:
1. Check the documentation
2. Review example implementations
3. Open an issue with `mvi-pattern` label
