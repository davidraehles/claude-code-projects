/**
 * Meal Plan - Selectors
 */

import type { MealPlanState } from './state';

export function selectStartDate(state: MealPlanState): string {
  return state.startDate;
}

export function selectNumDays(state: MealPlanState): number {
  return state.numDays;
}

export function selectNumPeople(state: MealPlanState): number {
  return state.numPeople;
}

export function selectMealsPerDay(state: MealPlanState): number {
  return state.mealsPerDay;
}

export function selectSelectedRestrictions(state: MealPlanState): string[] {
  return state.selectedRestrictions;
}

export function selectExcludedIngredients(state: MealPlanState): string {
  return state.excludedIngredients;
}

export function selectIsSubmitting(state: MealPlanState): boolean {
  return state.isSubmitting;
}

export function selectIsLoading(state: MealPlanState): boolean {
  return state.isLoading;
}

export function selectError(state: MealPlanState): string | null {
  return state.error;
}

export function selectGeneratedMealPlan(state: MealPlanState) {
  return state.generatedMealPlan;
}

export function selectMealPlans(state: MealPlanState): any[] {
  return state.mealPlans;
}

export function selectTotalMeals(state: MealPlanState): number {
  return state.numDays * state.mealsPerDay;
}

export function selectExcludedIngredientsList(state: MealPlanState): string[] {
  return state.excludedIngredients
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

export function selectIsFormValid(state: MealPlanState): boolean {
  return (
    state.startDate.length > 0 &&
    state.numDays > 0 &&
    state.numPeople > 0 &&
    state.mealsPerDay > 0
  );
}

export function selectFormData(state: MealPlanState) {
  return {
    start_date: state.startDate,
    num_days: state.numDays,
    num_people: state.numPeople,
    meals_per_day: state.mealsPerDay,
    dietary_restrictions: state.selectedRestrictions.length > 0
      ? state.selectedRestrictions
      : undefined,
    excluded_ingredients: selectExcludedIngredientsList(state).length > 0
      ? selectExcludedIngredientsList(state)
      : undefined,
  };
}
