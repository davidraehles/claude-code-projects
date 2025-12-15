/**
 * Meal Plan - Intent Creators
 */

import { createIntent } from '@/mvi';

export const mealPlanIntents = {
  setStartDate: createIntent<'USER_SET_START_DATE', { date: string }>(
    'USER_SET_START_DATE'
  ),

  setNumDays: createIntent<'USER_SET_NUM_DAYS', { numDays: number }>(
    'USER_SET_NUM_DAYS'
  ),

  setNumPeople: createIntent<'USER_SET_NUM_PEOPLE', { numPeople: number }>(
    'USER_SET_NUM_PEOPLE'
  ),

  setMealsPerDay: createIntent<'USER_SET_MEALS_PER_DAY', { mealsPerDay: number }>(
    'USER_SET_MEALS_PER_DAY'
  ),

  toggleDietaryRestriction: createIntent<
    'USER_TOGGLED_DIETARY_RESTRICTION',
    { restriction: string }
  >('USER_TOGGLED_DIETARY_RESTRICTION'),

  setExcludedIngredients: createIntent<
    'USER_SET_EXCLUDED_INGREDIENTS',
    { ingredients: string }
  >('USER_SET_EXCLUDED_INGREDIENTS'),

  resetForm: createIntent<'USER_RESET_FORM', undefined>('USER_RESET_FORM'),

  submitMealPlan: createIntent<'USER_SUBMIT_MEAL_PLAN', undefined>(
    'USER_SUBMIT_MEAL_PLAN'
  ),

  generatingMealPlan: createIntent<'GENERATING_MEAL_PLAN', undefined>(
    'GENERATING_MEAL_PLAN'
  ),

  mealPlanGenerated: createIntent<
    'MEAL_PLAN_GENERATED',
    { mealPlanId: number; mealPlan: any }
  >('MEAL_PLAN_GENERATED'),

  mealPlanGenerationFailed: createIntent<
    'MEAL_PLAN_GENERATION_FAILED',
    { error: string }
  >('MEAL_PLAN_GENERATION_FAILED'),

  loadMealPlans: createIntent<'USER_LOAD_MEAL_PLANS', undefined>(
    'USER_LOAD_MEAL_PLANS'
  ),

  mealPlansLoaded: createIntent<'MEAL_PLANS_LOADED', { mealPlans: any[] }>(
    'MEAL_PLANS_LOADED'
  ),
} as const;
