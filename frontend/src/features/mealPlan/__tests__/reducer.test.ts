/**
 * Meal Plan Reducer Tests
 */

import { mealPlanReducer } from '../model/reducer';
import { createInitialState } from '../model/state';
import { mealPlanIntents } from '../intents/creators';

describe('MealPlan Reducer', () => {
  it('sets start date', () => {
    const state = createInitialState();
    const nextState = mealPlanReducer(
      state,
      mealPlanIntents.setStartDate({ date: '2025-01-01' })
    );

    expect(nextState.startDate).toBe('2025-01-01');
  });

  it('sets number of days with clamping', () => {
    const state = createInitialState();

    const nextState1 = mealPlanReducer(
      state,
      mealPlanIntents.setNumDays({ numDays: 5 })
    );
    expect(nextState1.numDays).toBe(5);

    const nextState2 = mealPlanReducer(
      state,
      mealPlanIntents.setNumDays({ numDays: 20 })
    );
    expect(nextState2.numDays).toBe(14); // Clamped to max

    const nextState3 = mealPlanReducer(
      state,
      mealPlanIntents.setNumDays({ numDays: -5 })
    );
    expect(nextState3.numDays).toBe(1); // Clamped to min
  });

  it('toggles dietary restriction', () => {
    const state = createInitialState();

    const nextState1 = mealPlanReducer(
      state,
      mealPlanIntents.toggleDietaryRestriction({ restriction: 'Vegetarian' })
    );
    expect(nextState1.selectedRestrictions).toContain('Vegetarian');

    const nextState2 = mealPlanReducer(
      nextState1,
      mealPlanIntents.toggleDietaryRestriction({ restriction: 'Vegetarian' })
    );
    expect(nextState2.selectedRestrictions).not.toContain('Vegetarian');
  });

  it('resets form while preserving meal plans', () => {
    const state = createInitialState();
    state.numDays = 5;
    state.selectedRestrictions = ['Vegan'];
    state.mealPlans = [{ id: 1 }, { id: 2 }];

    const nextState = mealPlanReducer(state, mealPlanIntents.resetForm());

    expect(nextState.numDays).toBe(7); // Back to default
    expect(nextState.selectedRestrictions).toEqual([]);
    expect(nextState.mealPlans).toEqual([{ id: 1 }, { id: 2 }]); // Preserved
  });

  it('handles meal plan generation flow', () => {
    const state = createInitialState();

    const submitting = mealPlanReducer(
      state,
      mealPlanIntents.submitMealPlan()
    );
    expect(submitting.isSubmitting).toBe(true);
    expect(submitting.error).toBeNull();

    const generated = mealPlanReducer(
      submitting,
      mealPlanIntents.mealPlanGenerated({
        mealPlanId: 123,
        mealPlan: { data: 'test' },
      })
    );
    expect(generated.isSubmitting).toBe(false);
    expect(generated.generatedMealPlan?.id).toBe(123);

    const failed = mealPlanReducer(
      submitting,
      mealPlanIntents.mealPlanGenerationFailed({ error: 'API error' })
    );
    expect(failed.isSubmitting).toBe(false);
    expect(failed.error).toBe('API error');
  });
});
