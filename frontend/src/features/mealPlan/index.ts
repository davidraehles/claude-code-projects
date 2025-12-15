/**
 * Meal Plan Feature - MVI Module
 */

import { createMVI } from '@/mvi';
import { createDevToolsMiddleware } from '@/mvi/core/devtools';
import { mealPlanReducer } from './model/reducer';
import { createInitialState } from './model/state';
import type { MealPlanState } from './model/state';
import type { MealPlanIntent } from './intents/types';
import {
  createMealPlanApiMiddleware,
  createMealPlanAnalyticsMiddleware,
  createMealPlanPersistenceMiddleware,
} from './middleware/mealPlanMiddleware';

export * from './intents/types';
export * from './intents/creators';
export * from './model/state';
export * from './model/selectors';

export function createMealPlanMVI(config?: {
  apiClient?: {
    createMealPlan: (data: any) => Promise<{ id: number; data: any }>;
    getMealPlans: () => Promise<any[]>;
  };
  analytics?: (event: string, properties?: Record<string, unknown>) => void;
  enablePersistence?: boolean;
}) {
  const middleware: any[] = [
    createDevToolsMiddleware<MealPlanState, MealPlanIntent>('MealPlan'),
  ];

  if (config?.apiClient) {
    middleware.push(createMealPlanApiMiddleware(config.apiClient));
  }

  if (config?.analytics) {
    middleware.push(createMealPlanAnalyticsMiddleware(config.analytics));
  }

  if (config?.enablePersistence) {
    middleware.push(createMealPlanPersistenceMiddleware());
  }

  return createMVI<MealPlanState, MealPlanIntent>({
    name: 'MealPlan',
    initialState: createInitialState(),
    reducer: mealPlanReducer,
    middleware,
    devtools: true,
  });
}

export const useMealPlan = createMealPlanMVI({
  enablePersistence: true,
});
