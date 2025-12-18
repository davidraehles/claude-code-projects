# Go, Cart! Architecture Overview

## System Overview
Go, Cart! is a full-stack AI-powered meal planning and grocery ordering application with multi-agent architecture.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│  (Next.js 16)   │◄──►│   (FastAPI)      │◄──►│   Services      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
     │                       │                       │
     │                       │                       │
  ┌──▼──┐              ┌────▼────┐            ┌─────▼─────┐
  │ PWA │              │ Agents  │            │  Knuspr   │
  │ SW  │              │Workflows│            │  MCP API  │
  └─────┘              └─────────┘            └───────────┘
```

## Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | [`FastAPI`](https://fastapi.tiangolo.com/) | REST API server |
| Database | PostgreSQL + SQLAlchemy + Alembic | Data persistence |
| Agents | LangGraph + PydanticAI | Multi-agent orchestration |
| Auth | JWT + bcrypt | User authentication |
| Monitoring | Prometheus + Sentry | Observability |
| Email | SMTP + Jinja2 | Transactional emails |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | [`Next.js 16`](https://nextjs.org/) + React 19 | App framework |
| Styling | Tailwind CSS | Component styling |
| Animations | Lenis + GSAP + Framer Motion | 60fps interactions |
| State (Server) | React Query | Data fetching & caching |
| State (Local) | MVI Pattern with useReducer | Predictable state management |
| Auth | NextAuth.js | Authentication |
| PWA | Service Worker + IndexedDB | Offline support |

## Core Components

### 1. Multi-Agent System
```
Router Agent → [Meal Architect, Cart Optimizer, 
               Recipe Harvester, Ingredient Intelligence]
```

**Agents:**
- **Meal Architect**: Generates weekly meal plans with constraints
- **Cart Optimizer**: Creates optimized grocery lists
- **Recipe Harvester**: Scrapes and parses recipes from web
- **Ingredient Intelligence**: Normalizes and maps ingredients

### 2. Key Workflows
1. **Meal Planning Workflow** (`meal_planning_workflow.py`)
   - Input: Dietary preferences, budget, servings
   - Output: Weekly meal plan with recipes
   - States: Planning → Validation → Optimization

2. **Grocery Cart Workflow**
   - Input: Meal plan + recipes
   - Output: Aggregated shopping list
   - Integration: Knuspr MCP cart population

3. **Waitlist Workflow**
   - Offline-first signup with background sync
   - Email verification with queue position

### 3. Database Schema
```
Users → MealPlans → Recipes → Ingredients
     ↳ WaitlistEntries
     ↳ KnusprCredentials
     ↳ RateLimits
```

### 4. API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/meal-plans` | POST | Generate meal plan |
| `/api/v1/grocery-carts` | POST | Generate grocery list |
| `/api/v1/recipes` | GET/POST | Recipe CRUD |
| `/api/v1/waitlist` | POST | Join waitlist |
| `/api/v1/knuspr-credentials` | POST | Store Knuspr auth |

## Frontend Architecture: MVI Pattern (ARCH-004)

### Model-View-Intent (MVI) Pattern

The frontend implements the MVI architectural pattern for predictable, testable state management:

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│ Intent  │────▶│  Model  │────▶│  View   │
│ Actions │     │(Actions)│     │(Reducer)│     │(Render) │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                       │
                                       │ State Updates
                                       ▼
                                  ┌─────────┐
                                  │DevTools │
                                  │  Debug  │
                                  └─────────┘
```

**Key Principles:**
- **Unidirectional data flow**: User actions → Actions → Reducer → New State → View
- **Pure functions**: All reducers are pure (same input = same output)
- **Traceable state changes**: Every state transition is logged and debuggable
- **Time-travel debugging**: Redux DevTools integration for all reducers
- **Testability**: Pure reducers are easily testable in isolation

### Implemented Reducers

#### 1. Workflow Reducer (`workflowReducer.ts`)
**Purpose**: Cart generation workflow state machine

**State Machine**:
```
loading → cart-preview → delivery-selection → review → completed
   │                                             │
   └──────────────── error ──────────────────────┘
```

**Actions**: 8 action types
- `WORKFLOW_STARTED`: Initialize workflow
- `CART_GENERATION_SUCCEEDED`: Move to cart preview
- `CART_GENERATION_FAILED`: Handle errors
- `USER_NAVIGATED_TO_STEP`: Manual step navigation
- `USER_SELECTED_DELIVERY_SLOT`: Save delivery choice
- `USER_CLICKED_CHECKOUT`: Complete order
- `USER_CLICKED_RETRY`: Retry failed operation
- `WORKFLOW_RESET`: Reset workflow

**Selectors**: 8 selectors for derived state
- `selectIsStepComplete`: Check step completion
- `selectIsStepAccessible`: Check step accessibility
- `selectIsLoading`: Loading state
- `selectHasError`: Error state
- `selectCartItemCount`: Cart item count
- `selectHasDeliverySlot`: Delivery slot selection status
- `selectIsReadyForCheckout`: Checkout readiness

**Tests**: 100% coverage with comprehensive test suite

#### 2. Import Form Reducer (`importFormReducer.ts`)
**Purpose**: Recipe import form state (URL and file upload)

**State**:
```typescript
{
  url: string
  sourceType: 'html' | 'api' | 'rss'
  selectedFile: File | null
  urlImportSuccess: boolean
  fileUploadSuccess: boolean
}
```

**Actions**: 7 action types
- `USER_CHANGED_URL`: Update URL input
- `USER_SELECTED_SOURCE_TYPE`: Change source type
- `USER_SELECTED_FILE`: Select file for upload
- `USER_CLEARED_FILE`: Clear selected file
- `URL_IMPORT_SUCCEEDED`: Mark URL import success
- `FILE_UPLOAD_SUCCEEDED`: Mark file upload success
- `FORM_RESET`: Reset form

**Selectors**: 8 selectors for validation and derived state
- `selectIsUrlValid`: URL validation
- `selectHasFile`: File selection status
- `selectFileInfo`: File metadata
- `selectCanSubmitUrl`: URL form submission validation
- `selectCanSubmitFile`: File form submission validation
- `selectImportRequest`: API request data
- `selectHasSuccess`: Success status

**Tests**: 100% coverage with comprehensive test suite

#### 3. Create Recipe Form Reducer (`createRecipeFormReducer.ts`)
**Purpose**: Recipe creation form with dynamic ingredients array

**State**:
```typescript
{
  title: string
  ingredients: string[]
  instructions: string
  prepTime?: number
  cookTime?: number
  servings?: number
  dietaryTags: string[]
  success: boolean
}
```

**Actions**: 11 action types
- `USER_CHANGED_TITLE`: Update recipe title
- `USER_CHANGED_INSTRUCTIONS`: Update instructions
- `USER_CHANGED_PREP_TIME`: Set prep time
- `USER_CHANGED_COOK_TIME`: Set cook time
- `USER_CHANGED_SERVINGS`: Set servings
- `USER_CHANGED_INGREDIENT`: Update ingredient at index
- `USER_ADDED_INGREDIENT`: Add new ingredient
- `USER_REMOVED_INGREDIENT`: Remove ingredient
- `USER_TOGGLED_DIETARY_TAG`: Toggle dietary tag
- `RECIPE_CREATED_SUCCESSFULLY`: Mark creation success
- `FORM_RESET`: Reset form

**Selectors**: 10 selectors for validation and derived state
- `selectIsTitleValid`: Title validation
- `selectValidIngredients`: Filter valid ingredients
- `selectHasValidIngredients`: Ingredients validation
- `selectCanSubmit`: Form submission validation
- `selectCreateRecipeRequest`: API request data
- `selectTotalTime`: Calculated total time (prep + cook)
- `selectHasDietaryTag`: Check tag selection
- `selectIngredientCount`: Total ingredient count
- `selectValidIngredientCount`: Valid ingredient count

**Tests**: 100% coverage with comprehensive test suite

### Benefits Achieved

**1. Testability**
- Pure reducer functions are easily testable in isolation
- 100% test coverage for all reducers
- Actions and selectors are independently testable
- No mocking required for reducer tests

**2. Debugging**
- Redux DevTools integration for time-travel debugging
- All state changes are logged in development mode
- Clear action names describe user intent
- Step-by-step state transition visibility

**3. Traceability**
- Every state change has an explicit action
- Action names follow `WHO_DID_WHAT` pattern
- State transitions are predictable and documented
- Easy to trace bugs to specific actions

**4. Maintainability**
- Clear separation of concerns (View, Model, Intent)
- Selectors encapsulate derived state logic
- Reducers are pure and side-effect free
- Easy to add new actions and state transitions

**5. Consistency**
- Unified pattern across the entire frontend
- All complex state uses reducers
- DevTools integration is standard
- Action naming conventions are consistent

### Usage Example

```typescript
// In a React component
const [state, dispatch] = useReducerWithDevTools(
  workflowReducer,
  getInitialWorkflowState(),
  'WorkflowStateMachine' // DevTools name
)

// Dispatch user actions
dispatch({ type: 'WORKFLOW_STARTED', payload: { mealPlanId: 123 } })

// Use selectors for derived state
const isLoading = selectIsLoading(state)
const canCheckout = selectIsReadyForCheckout(state)

// Render based on state
if (isLoading) return <LoadingSpinner />
if (canCheckout) return <CheckoutButton onClick={handleCheckout} />
```

### Testing Example

```typescript
describe('workflowReducer', () => {
  it('should transition to cart-preview on success', () => {
    const initialState = getInitialWorkflowState()
    const action = {
      type: 'CART_GENERATION_SUCCEEDED',
      payload: { cartData: mockCart }
    }
    
    const newState = workflowReducer(initialState, action)
    
    expect(newState.step).toBe('cart-preview')
    expect(newState.cartData).toEqual(mockCart)
    expect(newState.isLoading).toBe(false)
  })
})
```

## Deployment Architecture
```
Vercel (Frontend) ←→ Railway (Backend) ←→ PostgreSQL (Neon/Supabase)
                         ↓
                   Knuspr MCP API
```

## Performance & Quality
- **60fps animations** (GPU accelerated)
- **WCAG 2.1 AAA** compliant
- **Core Web Vitals**: 95+ Lighthouse scores
- **14 integration tests** for waitlist
- **TypeScript strict mode**: 100% coverage
- **Offline-first**: Service Worker + IndexedDB
- **MVI Pattern**: Predictable state management with 100% test coverage

## Monitoring & Observability
```
Prometheus Metrics:
├── waitlist_signups_total
├── waitlist_queue_size  
├── workflow_duration_seconds
└── api_request_duration

Redux DevTools (Development):
├── Time-travel debugging
├── Action history
├── State snapshots
└── Diff viewer
```

## Development Guidelines

### State Management Decision Tree

**Should I use MVI pattern (reducer)?**
```
Is the state complex? ────────────────────▶ YES ─▶ Use MVI pattern
   │                                                  (useReducerWithDevTools)
   NO
   │
   ▼
Does it need to be testable? ─────────────▶ YES ─▶ Use MVI pattern
   │
   NO
   │
   ▼
Is it just server data? ──────────────────▶ YES ─▶ Use React Query
   │
   NO
   │
   ▼
Use useState ──────────────────────────────────────▶ Simple local state
```

**State Complexity Indicators**:
- Multiple related pieces of state
- State transitions follow rules
- Need to trace state changes
- Complex validation logic
- Dynamic arrays or nested objects

### Adding a New Reducer

1. **Create reducer file**: `/frontend/src/reducers/myFeatureReducer.ts`
2. **Define state interface**: Clear TypeScript types
3. **Define action types**: Use `WHO_DID_WHAT` naming
4. **Implement reducer**: Pure function, log in dev mode
5. **Create selectors**: Encapsulate derived state
6. **Write tests**: Aim for 100% coverage
7. **Integrate DevTools**: Use `useReducerWithDevTools`
8. **Update documentation**: Add to this file

### Best Practices

- **Actions**: Use descriptive names that express intent
- **Reducers**: Keep them pure, no side effects
- **Selectors**: Use for all derived state
- **Tests**: Test reducers and selectors independently
- **DevTools**: Always enable in development
- **Documentation**: Document state machines and transitions
