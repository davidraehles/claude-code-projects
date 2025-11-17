/**
 * Grocery Cart Reducer - Implements Action/Intent Layer (ARCH-004)
 *
 * Manages checkbox state for grocery items.
 * Actions express user intent and create traceable state transitions.
 */

/**
 * State interface
 */
export interface GroceryCartState {
  checkedItems: Set<string>
}

/**
 * Action types - Describe user intents
 */
export type GroceryCartAction =
  | { type: 'USER_TOGGLED_ITEM'; payload: string }
  | { type: 'USER_CHECKED_ALL_ITEMS'; payload: string[] }
  | { type: 'USER_UNCHECKED_ALL_ITEMS' }
  | { type: 'CART_RESET' }

/**
 * Initial state factory
 */
export function getInitialCartState(): GroceryCartState {
  return {
    checkedItems: new Set<string>(),
  }
}

/**
 * Pure reducer function - All state transitions are traceable
 */
export function groceryCartReducer(
  state: GroceryCartState,
  action: GroceryCartAction
): GroceryCartState {
  // Log actions in development for debugging
  if (process.env.NODE_ENV === 'development') {
    console.log('[GroceryCartReducer]', action.type, action)
  }

  switch (action.type) {
    case 'USER_TOGGLED_ITEM':
      const ingredient = action.payload
      const newCheckedItems = new Set(state.checkedItems)

      if (newCheckedItems.has(ingredient)) {
        newCheckedItems.delete(ingredient)
      } else {
        newCheckedItems.add(ingredient)
      }

      return {
        ...state,
        checkedItems: newCheckedItems,
      }

    case 'USER_CHECKED_ALL_ITEMS':
      return {
        ...state,
        checkedItems: new Set(action.payload),
      }

    case 'USER_UNCHECKED_ALL_ITEMS':
      return {
        ...state,
        checkedItems: new Set(),
      }

    case 'CART_RESET':
      return getInitialCartState()

    default:
      return state
  }
}

/**
 * Selector: Get checked count
 */
export function selectCheckedCount(state: GroceryCartState): number {
  return state.checkedItems.size
}

/**
 * Selector: Check if item is checked
 */
export function selectIsItemChecked(state: GroceryCartState, ingredient: string): boolean {
  return state.checkedItems.has(ingredient)
}

/**
 * Selector: Check if all items are checked
 */
export function selectAllItemsChecked(state: GroceryCartState, totalItems: number): boolean {
  return state.checkedItems.size === totalItems
}
