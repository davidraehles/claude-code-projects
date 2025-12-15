/**
 * Meal Plan - Reducer
 */

import type { MealPlanState } from './state';
import { createInitialState } from './state';
import type { MealPlanIntent } from '../intents/types';

export function mealPlanReducer(
  state: MealPlanState,
  intent: MealPlanIntent
): MealPlanState {
  switch (intent.type) {
    case 'USER_SET_START_DATE':
      return {
        ...state,
        startDate: intent.payload!.date,
      };

    case 'USER_SET_NUM_DAYS':
      return {
        ...state,
        numDays: Math.max(1, Math.min(14, intent.payload!.numDays)),
      };

    case 'USER_SET_NUM_PEOPLE':
      return {
        ...state,
        numPeople: Math.max(1, Math.min(10, intent.payload!.numPeople)),
      };

    case 'USER_SET_MEALS_PER_DAY':
      return {
        ...state,
        mealsPerDay: Math.max(1, Math.min(5, intent.payload!.mealsPerDay)),
      };

    case 'USER_TOGGLED_DIETARY_RESTRICTION': {
      const { restriction } = intent.payload!;
      const restrictions = state.selectedRestrictions;

      return {
        ...state,
        selectedRestrictions: restrictions.includes(restriction)
          ? restrictions.filter((r) => r !== restriction)
          : [...restrictions, restriction],
      };
    }

    case 'USER_SET_EXCLUDED_INGREDIENTS':
      return {
        ...state,
        excludedIngredients: intent.payload!.ingredients,
      };

    case 'USER_RESET_FORM':
      return {
        ...createInitialState(),
        mealPlans: state.mealPlans, // Preserve loaded meal plans
      };

    case 'USER_SUBMIT_MEAL_PLAN':
    case 'GENERATING_MEAL_PLAN':
      return {
        ...state,
        isSubmitting: true,
        error: null,
      };

    case 'MEAL_PLAN_GENERATED': {
      const { mealPlanId, mealPlan } = intent.payload!;
      return {
        ...state,
        isSubmitting: false,
        error: null,
        generatedMealPlan: {
          id: mealPlanId,
          data: mealPlan,
        },
      };
    }

    case 'MEAL_PLAN_GENERATION_FAILED':
      return {
        ...state,
        isSubmitting: false,
        error: intent.payload!.error,
      };

    case 'USER_LOAD_MEAL_PLANS':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'MEAL_PLANS_LOADED':
      return {
        ...state,
        isLoading: false,
        error: null,
        mealPlans: intent.payload!.mealPlans,
      };

    default:
      return state;
  }
}
