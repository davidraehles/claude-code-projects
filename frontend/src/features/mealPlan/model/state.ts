/**
 * Meal Plan - State Definition
 */

export interface MealPlanState {
  // Form fields
  startDate: string;
  numDays: number;
  numPeople: number;
  mealsPerDay: number;
  selectedRestrictions: string[];
  excludedIngredients: string;

  // Async state
  isSubmitting: boolean;
  isLoading: boolean;
  error: string | null;

  // Generated meal plan
  generatedMealPlan: {
    id: number;
    data: any;
  } | null;

  // List of meal plans
  mealPlans: any[];
}

export function createInitialState(): MealPlanState {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  return {
    startDate: tomorrow.toISOString().split('T')[0],
    numDays: 7,
    numPeople: 2,
    mealsPerDay: 3,
    selectedRestrictions: [],
    excludedIngredients: '',
    isSubmitting: false,
    isLoading: false,
    error: null,
    generatedMealPlan: null,
    mealPlans: [],
  };
}
