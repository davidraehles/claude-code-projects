/**
 * Create Recipe Form Reducer - Implements Action/Intent Layer (ARCH-004)
 *
 * Manages the recipe creation form state with dynamic ingredients array.
 * Actions express user intent and create traceable state transitions.
 */

/**
 * State interface
 */
export interface CreateRecipeFormState {
  title: string
  ingredients: string[]
  instructions: string
  prepTime?: number
  cookTime?: number
  servings?: number
  dietaryTags: string[]
  success: boolean
}

/**
 * Action types - Describe user intents
 */
export type CreateRecipeFormAction =
  | { type: 'USER_CHANGED_TITLE'; payload: string }
  | { type: 'USER_CHANGED_INSTRUCTIONS'; payload: string }
  | { type: 'USER_CHANGED_PREP_TIME'; payload: number | undefined }
  | { type: 'USER_CHANGED_COOK_TIME'; payload: number | undefined }
  | { type: 'USER_CHANGED_SERVINGS'; payload: number | undefined }
  | { type: 'USER_CHANGED_INGREDIENT'; payload: { index: number; value: string } }
  | { type: 'USER_ADDED_INGREDIENT' }
  | { type: 'USER_REMOVED_INGREDIENT'; payload: { index: number } }
  | { type: 'USER_TOGGLED_DIETARY_TAG'; payload: string }
  | { type: 'RECIPE_CREATED_SUCCESSFULLY' }
  | { type: 'FORM_RESET' }

/**
 * Initial state factory
 */
export function getInitialCreateRecipeFormState(): CreateRecipeFormState {
  return {
    title: '',
    ingredients: [''],
    instructions: '',
    prepTime: undefined,
    cookTime: undefined,
    servings: 2,
    dietaryTags: [],
    success: false,
  }
}

/**
 * Pure reducer function - All state transitions are traceable
 */
export function createRecipeFormReducer(
  state: CreateRecipeFormState,
  action: CreateRecipeFormAction
): CreateRecipeFormState {
  // Log actions in development for debugging
  if (process.env.NODE_ENV === 'development') {
    console.log('[CreateRecipeFormReducer]', action.type, action)
  }

  switch (action.type) {
    case 'USER_CHANGED_TITLE':
      return {
        ...state,
        title: action.payload,
      }

    case 'USER_CHANGED_INSTRUCTIONS':
      return {
        ...state,
        instructions: action.payload,
      }

    case 'USER_CHANGED_PREP_TIME':
      return {
        ...state,
        prepTime: action.payload,
      }

    case 'USER_CHANGED_COOK_TIME':
      return {
        ...state,
        cookTime: action.payload,
      }

    case 'USER_CHANGED_SERVINGS':
      return {
        ...state,
        servings: action.payload,
      }

    case 'USER_CHANGED_INGREDIENT':
      const newIngredients = [...state.ingredients]
      newIngredients[action.payload.index] = action.payload.value
      return {
        ...state,
        ingredients: newIngredients,
      }

    case 'USER_ADDED_INGREDIENT':
      return {
        ...state,
        ingredients: [...state.ingredients, ''],
      }

    case 'USER_REMOVED_INGREDIENT':
      // Keep at least one ingredient
      if (state.ingredients.length <= 1) {
        return state
      }
      return {
        ...state,
        ingredients: state.ingredients.filter((_, i) => i !== action.payload.index),
      }

    case 'USER_TOGGLED_DIETARY_TAG':
      const hasTag = state.dietaryTags.includes(action.payload)
      return {
        ...state,
        dietaryTags: hasTag
          ? state.dietaryTags.filter((t) => t !== action.payload)
          : [...state.dietaryTags, action.payload],
      }

    case 'RECIPE_CREATED_SUCCESSFULLY':
      return {
        ...state,
        success: true,
      }

    case 'FORM_RESET':
      return getInitialCreateRecipeFormState()

    default:
      return state
  }
}

/**
 * Title validation constraints
 */
const MIN_TITLE_LENGTH = 3
const MAX_TITLE_LENGTH = 120

/**
 * Selector: Check if title is valid
 */
export function selectIsTitleValid(state: CreateRecipeFormState): boolean {
  const trimmedTitle = state.title.trim()
  const length = trimmedTitle.length
  return length >= MIN_TITLE_LENGTH && length <= MAX_TITLE_LENGTH
}

/**
 * Selector: Get valid (non-empty) ingredients
 */
export function selectValidIngredients(state: CreateRecipeFormState): string[] {
  return state.ingredients.filter((i) => i.trim().length > 0)
}

/**
 * Selector: Check if form has valid ingredients
 */
export function selectHasValidIngredients(state: CreateRecipeFormState): boolean {
  return selectValidIngredients(state).length > 0
}

/**
 * Selector: Check if form can be submitted
 */
export function selectCanSubmit(state: CreateRecipeFormState): boolean {
  return selectIsTitleValid(state) && selectHasValidIngredients(state)
}

/**
 * Selector: Get create recipe request data for API
 */
export function selectCreateRecipeRequest(state: CreateRecipeFormState): {
  title: string
  ingredients: string[]
  instructions: string
  prep_time?: number
  cook_time?: number
  servings?: number
  dietary_tags?: string[]
} {
  return {
    title: state.title,
    ingredients: selectValidIngredients(state),
    instructions: state.instructions,
    prep_time: state.prepTime,
    cook_time: state.cookTime,
    servings: state.servings,
    dietary_tags: state.dietaryTags.length > 0 ? state.dietaryTags : undefined,
  }
}

/**
 * Selector: Get total time (prep + cook)
 */
export function selectTotalTime(state: CreateRecipeFormState): number | undefined {
  if (state.prepTime === undefined && state.cookTime === undefined) {
    return undefined
  }
  return (state.prepTime || 0) + (state.cookTime || 0)
}

/**
 * Selector: Check if dietary tag is selected
 */
export function selectHasDietaryTag(state: CreateRecipeFormState, tag: string): boolean {
  return state.dietaryTags.includes(tag)
}

/**
 * Selector: Get ingredient count
 */
export function selectIngredientCount(state: CreateRecipeFormState): number {
  return state.ingredients.length
}

/**
 * Selector: Get valid ingredient count
 */
export function selectValidIngredientCount(state: CreateRecipeFormState): number {
  return selectValidIngredients(state).length
}
