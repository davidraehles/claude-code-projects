/**
 * Meal Plan - Intent Types
 * 
 * Defines all user actions and system events for meal planning
 */

import type { Intent } from '@/mvi';

/**
 * User sets start date
 */
export type SetStartDateIntent = Intent<
  'USER_SET_START_DATE',
  { date: string }
>;

/**
 * User changes number of days
 */
export type SetNumDaysIntent = Intent<
  'USER_SET_NUM_DAYS',
  { numDays: number }
>;

/**
 * User changes number of people
 */
export type SetNumPeopleIntent = Intent<
  'USER_SET_NUM_PEOPLE',
  { numPeople: number }
>;

/**
 * User changes meals per day
 */
export type SetMealsPerDayIntent = Intent<
  'USER_SET_MEALS_PER_DAY',
  { mealsPerDay: number }
>;

/**
 * User toggles dietary restriction
 */
export type ToggleDietaryRestrictionIntent = Intent<
  'USER_TOGGLED_DIETARY_RESTRICTION',
  { restriction: string }
>;

/**
 * User changes excluded ingredients
 */
export type SetExcludedIngredientsIntent = Intent<
  'USER_SET_EXCLUDED_INGREDIENTS',
  { ingredients: string }
>;

/**
 * User resets form
 */
export type ResetFormIntent = Intent<'USER_RESET_FORM', undefined>;

/**
 * User submits meal plan form
 */
export type SubmitMealPlanIntent = Intent<'USER_SUBMIT_MEAL_PLAN', undefined>;

/**
 * Meal plan generation started
 */
export type GeneratingMealPlanIntent = Intent<'GENERATING_MEAL_PLAN', undefined>;

/**
 * Meal plan generated successfully
 */
export type MealPlanGeneratedIntent = Intent<
  'MEAL_PLAN_GENERATED',
  { mealPlanId: number; mealPlan: any }
>;

/**
 * Meal plan generation failed
 */
export type MealPlanGenerationFailedIntent = Intent<
  'MEAL_PLAN_GENERATION_FAILED',
  { error: string }
>;

/**
 * User loads existing meal plans
 */
export type LoadMealPlansIntent = Intent<'USER_LOAD_MEAL_PLANS', undefined>;

/**
 * Meal plans loaded successfully
 */
export type MealPlansLoadedIntent = Intent<
  'MEAL_PLANS_LOADED',
  { mealPlans: any[] }
>;

/**
 * Union of all meal plan intents
 */
export type MealPlanIntent =
  | SetStartDateIntent
  | SetNumDaysIntent
  | SetNumPeopleIntent
  | SetMealsPerDayIntent
  | ToggleDietaryRestrictionIntent
  | SetExcludedIngredientsIntent
  | ResetFormIntent
  | SubmitMealPlanIntent
  | GeneratingMealPlanIntent
  | MealPlanGeneratedIntent
  | MealPlanGenerationFailedIntent
  | LoadMealPlansIntent
  | MealPlansLoadedIntent;
