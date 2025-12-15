# MVI Migration Guide

## Overview

This guide helps developers migrate existing components from traditional React patterns (useState, useReducer) to the MVI (Model-View-Intent) pattern.

## When to Use MVI

✅ **Use MVI for:**
- Features with complex state logic
- Forms with multiple fields
- Features requiring undo/redo
- Components with heavy side effects
- Features needing time-travel debugging
- State that needs persistence

❌ **Don't use MVI for:**
- Simple toggle states
- Ephemeral UI state (hover, focus)
- Very simple components
- One-off utilities

## Migration Patterns

### Pattern 1: Single useState → MVI

**Before:**
```typescript
function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(count - 1)}>-</button>
    </div>
  );
}
```

**After:**
```typescript
// 1. Create intents/types.ts
export type IncrementIntent = Intent<'USER_INCREMENTED', undefined>;
export type DecrementIntent = Intent<'USER_DECREMENTED', undefined>;
export type CounterIntent = IncrementIntent | DecrementIntent;

// 2. Create intents/creators.ts
export const counterIntents = {
  increment: createIntent<'USER_INCREMENTED', undefined>('USER_INCREMENTED'),
  decrement: createIntent<'USER_DECREMENTED', undefined>('USER_DECREMENTED'),
};

// 3. Create model/state.ts
export interface CounterState {
  count: number;
}
export const createInitialState = (): CounterState => ({ count: 0 });

// 4. Create model/reducer.ts
export function counterReducer(state: CounterState, intent: CounterIntent) {
  switch (intent.type) {
    case 'USER_INCREMENTED':
      return { ...state, count: state.count + 1 };
    case 'USER_DECREMENTED':
      return { ...state, count: state.count - 1 };
    default:
      return state;
  }
}

// 5. Create model/selectors.ts
export const selectCount = (state: CounterState) => state.count;

// 6. Create index.ts
export const useCounter = createMVI({
  name: 'Counter',
  initialState: createInitialState(),
  reducer: counterReducer,
});

// 7. Update component
function Counter() {
  const { state, dispatch, select } = useCounter();
  const count = select(selectCount);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => dispatch(counterIntents.increment())}>+</button>
      <button onClick={() => dispatch(counterIntents.decrement())}>-</button>
    </div>
  );
}
```

### Pattern 2: Multiple useState → MVI

**Before:**
```typescript
function UserForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [age, setAge] = useState(0);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await api.createUser({ name, email, age });
    } catch (error) {
      setErrors(error.errors);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={e => setName(e.target.value)} />
      <input value={email} onChange={e => setEmail(e.target.value)} />
      <input value={age} onChange={e => setAge(e.target.value)} />
      <button disabled={isSubmitting}>Submit</button>
    </form>
  );
}
```

**After:**
```typescript
// 1. Define all intents
export type SetNameIntent = Intent<'USER_SET_NAME', { name: string }>;
export type SetEmailIntent = Intent<'USER_SET_EMAIL', { email: string }>;
export type SetAgeIntent = Intent<'USER_SET_AGE', { age: number }>;
export type SubmitIntent = Intent<'USER_SUBMIT', undefined>;
export type SubmittedIntent = Intent<'USER_SUBMITTED', undefined>;
export type SubmitFailedIntent = Intent<'SUBMIT_FAILED', { errors: any }>;

// 2. State interface
export interface UserFormState {
  name: string;
  email: string;
  age: number;
  errors: Record<string, string>;
  isSubmitting: boolean;
}

// 3. Reducer
export function userFormReducer(state: UserFormState, intent: UserFormIntent) {
  switch (intent.type) {
    case 'USER_SET_NAME':
      return { ...state, name: intent.payload!.name };
    case 'USER_SET_EMAIL':
      return { ...state, email: intent.payload!.email };
    case 'USER_SET_AGE':
      return { ...state, age: intent.payload!.age };
    case 'USER_SUBMIT':
      return { ...state, isSubmitting: true, errors: {} };
    case 'USER_SUBMITTED':
      return { ...state, isSubmitting: false };
    case 'SUBMIT_FAILED':
      return { ...state, isSubmitting: false, errors: intent.payload!.errors };
    default:
      return state;
  }
}

// 4. API Middleware
export function createUserFormApiMiddleware(api) {
  return (store) => (next) => async (intent) => {
    next(intent);
    
    if (intent.type === 'USER_SUBMIT') {
      const state = store.getState();
      try {
        await api.createUser({
          name: state.name,
          email: state.email,
          age: state.age,
        });
        store.dispatch(userFormIntents.submitted());
      } catch (error) {
        store.dispatch(userFormIntents.submitFailed({ errors: error.errors }));
      }
    }
  };
}

// 5. Component
function UserForm() {
  const { state, dispatch } = useUserForm();
  
  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      dispatch(userFormIntents.submit());
    }}>
      <input
        value={state.name}
        onChange={e => dispatch(userFormIntents.setName({ name: e.target.value }))}
      />
      <input
        value={state.email}
        onChange={e => dispatch(userFormIntents.setEmail({ email: e.target.value }))}
      />
      <input
        value={state.age}
        onChange={e => dispatch(userFormIntents.setAge({ age: parseInt(e.target.value) }))}
      />
      <button disabled={state.isSubmitting}>Submit</button>
    </form>
  );
}
```

### Pattern 3: useReducer → MVI

**Before:**
```typescript
const initialState = { items: [], loading: false };

function reducer(state, action) {
  switch (action.type) {
    case 'ADD_ITEM':
      return { ...state, items: [...state.items, action.payload] };
    case 'REMOVE_ITEM':
      return { ...state, items: state.items.filter(i => i.id !== action.payload) };
    default:
      return state;
  }
}

function TodoList() {
  const [state, dispatch] = useReducer(reducer, initialState);
  // ...
}
```

**After:**
```typescript
// Already 80% there! Just need to:
// 1. Create intent types and creators
// 2. Add selectors
// 3. Wrap in createMVI
// 4. Add middleware if needed

// intents/creators.ts
export const todoIntents = {
  addItem: createIntent<'ADD_ITEM', { item: Todo }>('ADD_ITEM'),
  removeItem: createIntent<'REMOVE_ITEM', { id: string }>('REMOVE_ITEM'),
};

// model/selectors.ts
export const selectItems = (state: TodoState) => state.items;
export const selectItemCount = (state: TodoState) => state.items.length;

// index.ts
export const useTodoList = createMVI({
  name: 'TodoList',
  initialState,
  reducer, // Your existing reducer!
  middleware: [
    createDevToolsMiddleware('TodoList'),
  ],
});

// Component
function TodoList() {
  const { state, dispatch, select } = useTodoList();
  const items = select(selectItems);
  // ...
}
```

## Common Challenges & Solutions

### Challenge 1: Async Operations

**Problem:** Where do API calls go?

**Solution:** Use middleware

```typescript
export function createApiMiddleware(apiClient) {
  return (store) => (next) => async (intent) => {
    next(intent);
    
    if (intent.type === 'USER_FETCH_DATA') {
      try {
        const data = await apiClient.fetchData();
        store.dispatch(dataFetchedIntent({ data }));
      } catch (error) {
        store.dispatch(dataFetchFailedIntent({ error: error.message }));
      }
    }
  };
}
```

### Challenge 2: Form Validation

**Problem:** Where does validation logic go?

**Solution:** Use selectors or validation middleware

```typescript
// Option 1: Selectors
export function selectIsFormValid(state: FormState): boolean {
  return (
    state.email.includes('@') &&
    state.name.length > 0 &&
    state.age >= 18
  );
}

// Option 2: Validation Middleware
export function createValidationMiddleware() {
  return (store) => (next) => (intent) => {
    if (intent.type === 'USER_SUBMIT') {
      const state = store.getState();
      if (!validateForm(state)) {
        store.dispatch(validationFailedIntent({ errors: getErrors(state) }));
        return;
      }
    }
    next(intent);
  };
}
```

### Challenge 3: Dependent State

**Problem:** State that depends on other state

**Solution:** Use selectors

```typescript
export function selectTotalPrice(state: CartState): number {
  return state.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function selectDiscountedPrice(state: CartState): number {
  const total = selectTotalPrice(state);
  return state.discountCode ? total * 0.9 : total;
}
```

### Challenge 4: State Persistence

**Problem:** Need to save/restore state

**Solution:** Use persistence middleware

```typescript
// Already built-in!
export const useMyFeature = createMVI({
  name: 'MyFeature',
  initialState: loadPersistedState('myFeature', createInitialState()),
  reducer,
  middleware: [
    createPersistenceMiddleware('myFeature'),
  ],
});
```

## Step-by-Step Migration Checklist

### For Each Feature:

- [ ] **Step 1**: Identify all state variables
- [ ] **Step 2**: List all user actions that change state
- [ ] **Step 3**: Create intent types for each action
- [ ] **Step 4**: Create intent creators
- [ ] **Step 5**: Define state interface
- [ ] **Step 6**: Implement reducer with all intents
- [ ] **Step 7**: Create selectors for derived state
- [ ] **Step 8**: Implement middleware for side effects
- [ ] **Step 9**: Create MVI module with createMVI
- [ ] **Step 10**: Update component to use MVI hook
- [ ] **Step 11**: Write tests for reducer
- [ ] **Step 12**: Write tests for selectors
- [ ] **Step 13**: Update integration tests

## Testing Migration

### Before (Component Test):
```typescript
it('increments counter', async () => {
  render(<Counter />);
  const button = screen.getByText('+');
  await userEvent.click(button);
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

### After (Pure Function Test + Component Test):
```typescript
// Pure function test (faster, more reliable)
it('increments counter', () => {
  const state = { count: 0 };
  const nextState = counterReducer(state, counterIntents.increment());
  expect(nextState.count).toBe(1);
});

// Component test (integration)
it('increments counter in UI', async () => {
  render(<Counter />);
  await userEvent.click(screen.getByText('+'));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

## Tips & Best Practices

1. **Start Small**: Migrate one feature at a time
2. **Keep Tests**: Port existing tests, don't rewrite from scratch
3. **Use DevTools**: Leverage time-travel debugging during migration
4. **Document Intents**: Good intent names make code self-documenting
5. **Incremental**: Can mix MVI with existing patterns during transition
6. **Pair Program**: Migrate first feature with team member
7. **Code Review**: Get feedback on first MVI implementation

## Getting Help

- Review example implementations:
  - `/frontend/src/features/groceryCart/`
  - `/frontend/src/features/mealPlan/`
- Read the full documentation: `/frontend/docs/MVI_PATTERN.md`
- Check the quick start: `/frontend/MVI_README.md`
- Ask in team chat or code reviews

## Common Mistakes to Avoid

❌ **Don't:**
- Mutate state in reducer
- Dispatch intents from reducer
- Use side effects in selectors
- Mix MVI and non-MVI patterns in same feature
- Skip testing pure functions

✅ **Do:**
- Keep reducers pure
- Use middleware for side effects
- Test reducers and selectors independently
- Use selectors consistently
- Document intent meanings
