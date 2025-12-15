/**
 * Grocery Cart - Intent Types
 * 
 * Defines all user actions and system events for the grocery cart feature
 */

import type { Intent } from '@/mvi';

/**
 * User toggles a single item checkbox
 */
export type ToggleItemIntent = Intent<
  'USER_TOGGLED_ITEM',
  { ingredient: string }
>;

/**
 * User checks all items
 */
export type CheckAllItemsIntent = Intent<
  'USER_CHECKED_ALL_ITEMS',
  { ingredients: string[] }
>;

/**
 * User unchecks all items
 */
export type UncheckAllItemsIntent = Intent<'USER_UNCHECKED_ALL_ITEMS', undefined>;

/**
 * User switches view mode (recipe/category)
 */
export type SetViewModeIntent = Intent<
  'USER_SET_VIEW_MODE',
  { viewMode: 'recipe' | 'category' }
>;

/**
 * System resets cart (on navigation or explicit reset)
 */
export type ResetCartIntent = Intent<'CART_RESET', undefined>;

/**
 * User initiates cart generation
 */
export type GenerateCartIntent = Intent<
  'USER_GENERATE_CART',
  { mealPlanId: number }
>;

/**
 * Cart generation succeeded
 */
export type CartGeneratedIntent = Intent<
  'CART_GENERATED',
  { cartId: number; items: string[] }
>;

/**
 * Cart generation failed
 */
export type CartGenerationFailedIntent = Intent<
  'CART_GENERATION_FAILED',
  { error: string }
>;

/**
 * Union of all grocery cart intents
 */
export type GroceryCartIntent =
  | ToggleItemIntent
  | CheckAllItemsIntent
  | UncheckAllItemsIntent
  | SetViewModeIntent
  | ResetCartIntent
  | GenerateCartIntent
  | CartGeneratedIntent
  | CartGenerationFailedIntent;
