/**
 * Grocery Cart - Intent Creators
 * 
 * Factory functions to create intent objects with proper typing
 */

import { createIntent } from '@/mvi';
import type {
  ToggleItemIntent,
  CheckAllItemsIntent,
  UncheckAllItemsIntent,
  SetViewModeIntent,
  ResetCartIntent,
  GenerateCartIntent,
  CartGeneratedIntent,
  CartGenerationFailedIntent,
} from './types';

/**
 * Intent creators for grocery cart feature
 */
export const groceryCartIntents = {
  /**
   * Create intent to toggle a single item
   */
  toggleItem: createIntent<'USER_TOGGLED_ITEM', { ingredient: string }>(
    'USER_TOGGLED_ITEM'
  ),

  /**
   * Create intent to check all items
   */
  checkAllItems: createIntent<'USER_CHECKED_ALL_ITEMS', { ingredients: string[] }>(
    'USER_CHECKED_ALL_ITEMS'
  ),

  /**
   * Create intent to uncheck all items
   */
  uncheckAllItems: createIntent<'USER_UNCHECKED_ALL_ITEMS', undefined>(
    'USER_UNCHECKED_ALL_ITEMS'
  ),

  /**
   * Create intent to set view mode
   */
  setViewMode: createIntent<
    'USER_SET_VIEW_MODE',
    { viewMode: 'recipe' | 'category' }
  >('USER_SET_VIEW_MODE'),

  /**
   * Create intent to reset cart
   */
  resetCart: createIntent<'CART_RESET', undefined>('CART_RESET'),

  /**
   * Create intent to generate cart
   */
  generateCart: createIntent<'USER_GENERATE_CART', { mealPlanId: number }>(
    'USER_GENERATE_CART'
  ),

  /**
   * Create intent for successful cart generation
   */
  cartGenerated: createIntent<
    'CART_GENERATED',
    { cartId: number; items: string[] }
  >('CART_GENERATED'),

  /**
   * Create intent for failed cart generation
   */
  cartGenerationFailed: createIntent<'CART_GENERATION_FAILED', { error: string }>(
    'CART_GENERATION_FAILED'
  ),
} as const;

// Type helpers for consumers
export type GroceryCartIntentCreators = typeof groceryCartIntents;
