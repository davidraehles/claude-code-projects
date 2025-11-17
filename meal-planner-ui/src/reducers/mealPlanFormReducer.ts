/**
 * Meal Plan Form Reducer - Implements Action/Intent Layer (ARCH-004)
 *
 * Replaces 10+ useState calls with a single useReducer.
 * Actions express user intent and create traceable state transitions.
 */

import type { MealPlanCreateRequest } from '@/lib/types'

/**
 * Form state interface
 */
export interface MealPlanFormState {
  startDate: string
  numDays: number
  numPeople: number
  mealsPerDay: number
  selectedRestrictions: string[]
  excludedIngredients: string
}

/**
 * Action types - Describe user intents
 */
export type MealPlanFormAction =
  | { type: 'USER_SET_START_DATE'; payload: string }
  | { type: 'USER_CHANGED_NUM_DAYS'; payload: number }
  | { type: 'USER_CHANGED_NUM_PEOPLE'; payload: number }
  | { type: 'USER_CHANGED_MEALS_PER_DAY'; payload: number }
  | { type: 'USER_TOGGLED_DIETARY_RESTRICTION'; payload: string }
  | { type: 'USER_CHANGED_EXCLUDED_INGREDIENTS'; payload: string }
  | { type: 'USER_RESET_FORM' }
  | { type: 'FORM_INITIALIZED_WITH_DEFAULT_DATE'; payload: string }

/**
 * Initial state factory
 */
export function getInitialState(): MealPlanFormState {
  // Calculate tomorrow's date
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)

  return {
    startDate: tomorrow.toISOString().split('T')[0],
    numDays: 7,
    numPeople: 2,
    mealsPerDay: 3,
    selectedRestrictions: [],
    excludedIngredients: '',
  }
}

/**
 * Pure reducer function - All state transitions are traceable
 */
export function mealPlanFormReducer(
  state: MealPlanFormState,
  action: MealPlanFormAction
): MealPlanFormState {
  // Log actions in development for debugging
  if (process.env.NODE_ENV === 'development') {
    console.log('[MealPlanFormReducer]', action.type, action)
  }

  switch (action.type) {
    case 'USER_SET_START_DATE':
      return {
        ...state,
        startDate: action.payload,
      }

    case 'USER_CHANGED_NUM_DAYS':
      return {
        ...state,
        numDays: Math.max(1, Math.min(14, action.payload)), // Clamp 1-14
      }

    case 'USER_CHANGED_NUM_PEOPLE':
      return {
        ...state,
        numPeople: Math.max(1, Math.min(10, action.payload)), // Clamp 1-10
      }

    case 'USER_CHANGED_MEALS_PER_DAY':
      return {
        ...state,
        mealsPerDay: Math.max(1, Math.min(5, action.payload)), // Clamp 1-5
      }

    case 'USER_TOGGLED_DIETARY_RESTRICTION':
      const restriction = action.payload
      const currentRestrictions = state.selectedRestrictions

      return {
        ...state,
        selectedRestrictions: currentRestrictions.includes(restriction)
          ? currentRestrictions.filter((r) => r !== restriction)
          : [...currentRestrictions, restriction],
      }

    case 'USER_CHANGED_EXCLUDED_INGREDIENTS':
      return {
        ...state,
        excludedIngredients: action.payload,
      }

    case 'FORM_INITIALIZED_WITH_DEFAULT_DATE':
      return {
        ...state,
        startDate: action.payload,
      }

    case 'USER_RESET_FORM':
      return getInitialState()

    default:
      return state
  }
}

/**
 * Selector: Convert form state to API request format
 */
export function selectMealPlanRequest(
  state: MealPlanFormState
): MealPlanCreateRequest {
  // Parse excluded ingredients
  const excludedList = state.excludedIngredients
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item.length > 0)

  return {
    start_date: state.startDate,
    num_days: state.numDays,
    num_people: state.numPeople,
    meals_per_day: state.mealsPerDay,
    dietary_restrictions: state.selectedRestrictions.length > 0
      ? state.selectedRestrictions
      : undefined,
    excluded_ingredients: excludedList.length > 0
      ? excludedList
      : undefined,
  }
}

/**
 * Selector: Calculate total meals
 */
export function selectTotalMeals(state: MealPlanFormState): number {
  return state.numDays * state.mealsPerDay
}
