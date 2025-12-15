/**
 * Grocery Cart Feature - MVI Module
 * 
 * Main export for the Grocery Cart MVI implementation
 */

import { createMVI } from '@/mvi';
import { createDevToolsMiddleware } from '@/mvi/core/devtools';
import { groceryCartReducer } from './model/reducer';
import { createInitialState } from './model/state';
import type { GroceryCartState } from './model/state';
import type { GroceryCartIntent } from './intents/types';
import {
  createCartApiMiddleware,
  createCartAnalyticsMiddleware,
  createCartPersistenceMiddleware,
  loadPersistedCartState,
} from './middleware/cartMiddleware';

// Re-export types and creators
export * from './intents/types';
export * from './intents/creators';
export * from './model/state';
export * from './model/selectors';

/**
 * Create the Grocery Cart MVI hook
 */
export function createGroceryCartMVI(config?: {
  apiClient?: {
    generateCart: (mealPlanId: number) => Promise<{ id: number; items: string[] }>;
  };
  analytics?: (event: string, properties?: Record<string, unknown>) => void;
  enablePersistence?: boolean;
}) {
  // Load persisted state if available
  const persistedState = config?.enablePersistence
    ? loadPersistedCartState()
    : null;

  const initialState: GroceryCartState = {
    ...createInitialState(),
    ...persistedState,
  };

  // Build middleware chain
  const middleware: any[] = [
    createDevToolsMiddleware<GroceryCartState, GroceryCartIntent>('GroceryCart'),
  ];

  if (config?.apiClient) {
    middleware.push(createCartApiMiddleware(config.apiClient));
  }

  if (config?.analytics) {
    middleware.push(createCartAnalyticsMiddleware(config.analytics));
  }

  if (config?.enablePersistence) {
    middleware.push(createCartPersistenceMiddleware());
  }

  return createMVI<GroceryCartState, GroceryCartIntent>({
    name: 'GroceryCart',
    initialState,
    reducer: groceryCartReducer,
    middleware,
    devtools: true,
  });
}

/**
 * Default Grocery Cart MVI hook with standard configuration
 */
export const useGroceryCart = createGroceryCartMVI({
  enablePersistence: true,
});
