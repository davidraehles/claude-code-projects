/**
 * Meal Plan - Middleware
 */

import type { Middleware } from '@/mvi';
import type { MealPlanState } from '../model/state';
import type { MealPlanIntent } from '../intents/types';
import { mealPlanIntents } from '../intents/creators';
import { selectFormData } from '../model/selectors';

export function createMealPlanApiMiddleware(
  apiClient: {
    createMealPlan: (data: any) => Promise<{ id: number; data: any }>;
    getMealPlans: () => Promise<any[]>;
  }
): Middleware<MealPlanState, MealPlanIntent> {
  return (store) => (next) => async (intent) => {
    next(intent);

    if (intent.type === 'USER_SUBMIT_MEAL_PLAN') {
      const state = store.getState();
      const formData = selectFormData(state);

      store.dispatch(mealPlanIntents.generatingMealPlan());

      try {
        const result = await apiClient.createMealPlan(formData);

        store.dispatch(
          mealPlanIntents.mealPlanGenerated({
            mealPlanId: result.id,
            mealPlan: result.data,
          })
        );
      } catch (error) {
        store.dispatch(
          mealPlanIntents.mealPlanGenerationFailed({
            error: error instanceof Error ? error.message : 'Failed to generate meal plan',
          })
        );
      }
    }

    if (intent.type === 'USER_LOAD_MEAL_PLANS') {
      try {
        const mealPlans = await apiClient.getMealPlans();

        store.dispatch(mealPlanIntents.mealPlansLoaded({ mealPlans }));
      } catch (error) {
        console.error('Failed to load meal plans:', error);
      }
    }
  };
}

export function createMealPlanAnalyticsMiddleware(
  track: (event: string, properties?: Record<string, unknown>) => void
): Middleware<MealPlanState, MealPlanIntent> {
  return () => (next) => async (intent) => {
    switch (intent.type) {
      case 'USER_SUBMIT_MEAL_PLAN':
        track('meal_plan_submitted');
        break;

      case 'MEAL_PLAN_GENERATED':
        track('meal_plan_generated_success', {
          mealPlanId: intent.payload?.mealPlanId,
        });
        break;

      case 'MEAL_PLAN_GENERATION_FAILED':
        track('meal_plan_generation_failed', {
          error: intent.payload?.error,
        });
        break;

      case 'USER_TOGGLED_DIETARY_RESTRICTION':
        track('dietary_restriction_toggled', {
          restriction: intent.payload?.restriction,
        });
        break;
    }

    next(intent);
  };
}

export function createMealPlanPersistenceMiddleware(): Middleware<
  MealPlanState,
  MealPlanIntent
> {
  const STORAGE_KEY = 'mealplanner:mealPlanForm';

  return (store) => (next) => async (intent) => {
    next(intent);

    const shouldPersist = [
      'USER_SET_START_DATE',
      'USER_SET_NUM_DAYS',
      'USER_SET_NUM_PEOPLE',
      'USER_SET_MEALS_PER_DAY',
      'USER_TOGGLED_DIETARY_RESTRICTION',
      'USER_SET_EXCLUDED_INGREDIENTS',
    ].includes(intent.type);

    if (shouldPersist) {
      try {
        const state = store.getState();
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            startDate: state.startDate,
            numDays: state.numDays,
            numPeople: state.numPeople,
            mealsPerDay: state.mealsPerDay,
            selectedRestrictions: state.selectedRestrictions,
            excludedIngredients: state.excludedIngredients,
          })
        );
      } catch (error) {
        console.error('Failed to persist meal plan form:', error);
      }
    }
  };
}
