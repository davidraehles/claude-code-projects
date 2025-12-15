/**
 * Grocery Cart - Reducer
 * 
 * Pure function that produces new state from intents
 */

import type { GroceryCartState } from './state';
import { createInitialState } from './state';
import type { GroceryCartIntent } from '../intents/types';

/**
 * Grocery cart reducer - Handles all state transitions
 */
export function groceryCartReducer(
  state: GroceryCartState,
  intent: GroceryCartIntent
): GroceryCartState {
  switch (intent.type) {
    case 'USER_TOGGLED_ITEM': {
      const { ingredient } = intent.payload!;
      const newCheckedItems = new Set(state.checkedItems);

      if (newCheckedItems.has(ingredient)) {
        newCheckedItems.delete(ingredient);
      } else {
        newCheckedItems.add(ingredient);
      }

      return {
        ...state,
        checkedItems: newCheckedItems,
      };
    }

    case 'USER_CHECKED_ALL_ITEMS': {
      const { ingredients } = intent.payload!;
      return {
        ...state,
        checkedItems: new Set(ingredients),
      };
    }

    case 'USER_UNCHECKED_ALL_ITEMS': {
      return {
        ...state,
        checkedItems: new Set(),
      };
    }

    case 'USER_SET_VIEW_MODE': {
      const { viewMode } = intent.payload!;
      return {
        ...state,
        viewMode,
      };
    }

    case 'USER_GENERATE_CART': {
      return {
        ...state,
        isGenerating: true,
        error: null,
      };
    }

    case 'CART_GENERATED': {
      const { cartId, items } = intent.payload!;
      return {
        ...state,
        isGenerating: false,
        error: null,
        generatedCart: { cartId, items },
      };
    }

    case 'CART_GENERATION_FAILED': {
      const { error } = intent.payload!;
      return {
        ...state,
        isGenerating: false,
        error,
        generatedCart: null,
      };
    }

    case 'CART_RESET': {
      return createInitialState();
    }

    default:
      return state;
  }
}
