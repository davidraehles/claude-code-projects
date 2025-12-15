/**
 * Grocery Cart - State Definition
 * 
 * Immutable state tree for the grocery cart feature
 */

/**
 * View mode for grocery list
 */
export type ViewMode = 'recipe' | 'category';

/**
 * Grocery cart state interface
 */
export interface GroceryCartState {
  /**
   * Set of checked ingredient identifiers
   */
  checkedItems: Set<string>;

  /**
   * Current view mode
   */
  viewMode: ViewMode;

  /**
   * Loading state for async operations
   */
  isGenerating: boolean;

  /**
   * Error state
   */
  error: string | null;

  /**
   * Generated cart metadata
   */
  generatedCart: {
    cartId: number | null;
    items: string[];
  } | null;
}

/**
 * Initial state factory
 */
export function createInitialState(): GroceryCartState {
  return {
    checkedItems: new Set<string>(),
    viewMode: 'category',
    isGenerating: false,
    error: null,
    generatedCart: null,
  };
}

/**
 * State serialization for persistence
 */
export function serializeState(state: GroceryCartState): string {
  return JSON.stringify({
    checkedItems: Array.from(state.checkedItems),
    viewMode: state.viewMode,
    isGenerating: state.isGenerating,
    error: state.error,
    generatedCart: state.generatedCart,
  });
}

/**
 * State deserialization from persistence
 */
export function deserializeState(serialized: string): GroceryCartState {
  try {
    const parsed = JSON.parse(serialized);
    return {
      checkedItems: new Set(parsed.checkedItems || []),
      viewMode: parsed.viewMode || 'category',
      isGenerating: parsed.isGenerating || false,
      error: parsed.error || null,
      generatedCart: parsed.generatedCart || null,
    };
  } catch {
    return createInitialState();
  }
}
