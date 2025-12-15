/**
 * Grocery Cart - Middleware
 * 
 * Handles side effects like API calls, analytics, and persistence
 */

import type { Middleware } from '@/mvi';
import type { GroceryCartState } from '../model/state';
import type { GroceryCartIntent } from '../intents/types';
import { groceryCartIntents } from '../intents/creators';

/**
 * API middleware - Handles cart generation API calls
 */
export function createCartApiMiddleware(
  apiClient: {
    generateCart: (mealPlanId: number) => Promise<{ id: number; items: string[] }>;
  }
): Middleware<GroceryCartState, GroceryCartIntent> {
  return (store) => (next) => async (intent) => {
    // Process the intent first
    next(intent);

    // Handle side effects based on intent type
    if (intent.type === 'USER_GENERATE_CART') {
      const { mealPlanId } = intent.payload!;

      try {
        // Make API call
        const result = await apiClient.generateCart(mealPlanId);

        // Dispatch success intent
        store.dispatch(
          groceryCartIntents.cartGenerated({
            cartId: result.id,
            items: result.items,
          })
        );
      } catch (error) {
        // Dispatch error intent
        store.dispatch(
          groceryCartIntents.cartGenerationFailed({
            error: error instanceof Error ? error.message : 'Failed to generate cart',
          })
        );
      }
    }
  };
}

/**
 * Analytics middleware - Tracks user interactions
 */
export function createCartAnalyticsMiddleware(
  track: (event: string, properties?: Record<string, unknown>) => void
): Middleware<GroceryCartState, GroceryCartIntent> {
  return () => (next) => async (intent) => {
    // Track specific user intents
    switch (intent.type) {
      case 'USER_TOGGLED_ITEM':
        track('grocery_cart_item_toggled', {
          ingredient: intent.payload?.ingredient,
        });
        break;

      case 'USER_CHECKED_ALL_ITEMS':
        track('grocery_cart_checked_all', {
          itemCount: intent.payload?.ingredients.length,
        });
        break;

      case 'USER_UNCHECKED_ALL_ITEMS':
        track('grocery_cart_unchecked_all');
        break;

      case 'USER_SET_VIEW_MODE':
        track('grocery_cart_view_changed', {
          viewMode: intent.payload?.viewMode,
        });
        break;

      case 'USER_GENERATE_CART':
        track('grocery_cart_generation_started', {
          mealPlanId: intent.payload?.mealPlanId,
        });
        break;

      case 'CART_GENERATED':
        track('grocery_cart_generated_success', {
          cartId: intent.payload?.cartId,
          itemCount: intent.payload?.items.length,
        });
        break;

      case 'CART_GENERATION_FAILED':
        track('grocery_cart_generation_failed', {
          error: intent.payload?.error,
        });
        break;
    }

    next(intent);
  };
}

/**
 * Persistence middleware - Saves cart state to local storage
 */
export function createCartPersistenceMiddleware(): Middleware<
  GroceryCartState,
  GroceryCartIntent
> {
  const STORAGE_KEY = 'mealplanner:groceryCart';

  return (store) => (next) => async (intent) => {
    next(intent);

    // Persist state after certain intents
    const shouldPersist = [
      'USER_TOGGLED_ITEM',
      'USER_CHECKED_ALL_ITEMS',
      'USER_UNCHECKED_ALL_ITEMS',
      'USER_SET_VIEW_MODE',
      'CART_GENERATED',
    ].includes(intent.type);

    if (shouldPersist) {
      try {
        const state = store.getState();
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            checkedItems: Array.from(state.checkedItems),
            viewMode: state.viewMode,
          })
        );
      } catch (error) {
        console.error('Failed to persist grocery cart state:', error);
      }
    }
  };
}

/**
 * Load persisted cart state
 */
export function loadPersistedCartState(): Partial<GroceryCartState> | null {
  const STORAGE_KEY = 'mealplanner:groceryCart';

  try {
    const serialized = localStorage.getItem(STORAGE_KEY);
    if (!serialized) return null;

    const parsed = JSON.parse(serialized);
    return {
      checkedItems: new Set(parsed.checkedItems || []),
      viewMode: parsed.viewMode || 'category',
    };
  } catch (error) {
    console.error('Failed to load persisted grocery cart state:', error);
    return null;
  }
}
