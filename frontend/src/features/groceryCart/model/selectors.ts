/**
 * Grocery Cart - Selectors
 * 
 * Pure functions that derive data from state
 * Selectors enable efficient re-renders and testable logic
 */

import type { GroceryCartState, ViewMode } from './state';

/**
 * Select checked items count
 */
export function selectCheckedCount(state: GroceryCartState): number {
  return state.checkedItems.size;
}

/**
 * Check if a specific item is checked
 */
export function selectIsItemChecked(
  state: GroceryCartState,
  ingredient: string
): boolean {
  return state.checkedItems.has(ingredient);
}

/**
 * Check if all items are checked
 */
export function selectAllItemsChecked(
  state: GroceryCartState,
  totalItems: number
): boolean {
  return state.checkedItems.size > 0 && state.checkedItems.size === totalItems;
}

/**
 * Check if some (but not all) items are checked
 */
export function selectSomeItemsChecked(
  state: GroceryCartState,
  totalItems: number
): boolean {
  const count = state.checkedItems.size;
  return count > 0 && count < totalItems;
}

/**
 * Select current view mode
 */
export function selectViewMode(state: GroceryCartState): ViewMode {
  return state.viewMode;
}

/**
 * Select loading state
 */
export function selectIsGenerating(state: GroceryCartState): boolean {
  return state.isGenerating;
}

/**
 * Select error state
 */
export function selectError(state: GroceryCartState): string | null {
  return state.error;
}

/**
 * Select generated cart
 */
export function selectGeneratedCart(state: GroceryCartState) {
  return state.generatedCart;
}

/**
 * Select checked items as array
 */
export function selectCheckedItemsArray(state: GroceryCartState): string[] {
  return Array.from(state.checkedItems);
}

/**
 * Select progress (checked / total)
 */
export function selectProgress(
  state: GroceryCartState,
  totalItems: number
): number {
  if (totalItems === 0) return 0;
  return (state.checkedItems.size / totalItems) * 100;
}

/**
 * Compound selector: cart summary
 */
export function selectCartSummary(state: GroceryCartState, totalItems: number) {
  return {
    checkedCount: selectCheckedCount(state),
    totalItems,
    progress: selectProgress(state, totalItems),
    allChecked: selectAllItemsChecked(state, totalItems),
    someChecked: selectSomeItemsChecked(state, totalItems),
    viewMode: selectViewMode(state),
  };
}
