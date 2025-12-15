/**
 * Meal Plan Form View - MVI Pattern
 */

'use client';

import { useMealPlan, mealPlanIntents } from '../index';
import {
  selectStartDate,
  selectNumDays,
  selectNumPeople,
  selectMealsPerDay,
  selectSelectedRestrictions,
  selectExcludedIngredients,
  selectIsSubmitting,
  selectError,
  selectTotalMeals,
  selectIsFormValid,
} from '../model/selectors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/Input';
import { Checkbox } from '@/components/ui/Checkbox';

const DIETARY_RESTRICTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-Free',
  'Dairy-Free',
  'Nut-Free',
  'Low-Carb',
];

export function MealPlanFormView() {
  const { state, dispatch, select } = useMealPlan();

  const startDate = select(selectStartDate);
  const numDays = select(selectNumDays);
  const numPeople = select(selectNumPeople);
  const mealsPerDay = select(selectMealsPerDay);
  const selectedRestrictions = select(selectSelectedRestrictions);
  const excludedIngredients = select(selectExcludedIngredients);
  const isSubmitting = select(selectIsSubmitting);
  const error = select(selectError);
  const totalMeals = select(selectTotalMeals);
  const isFormValid = select(selectIsFormValid);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(mealPlanIntents.submitMealPlan());
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-8">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Generate Meal Plan
        </h2>

        {/* Basic Settings */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) =>
                dispatch(mealPlanIntents.setStartDate({ date: e.target.value }))
              }
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Days
              </label>
              <Input
                type="number"
                min="1"
                max="14"
                value={numDays}
                onChange={(e) =>
                  dispatch(
                    mealPlanIntents.setNumDays({ numDays: parseInt(e.target.value) })
                  )
                }
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                People
              </label>
              <Input
                type="number"
                min="1"
                max="10"
                value={numPeople}
                onChange={(e) =>
                  dispatch(
                    mealPlanIntents.setNumPeople({
                      numPeople: parseInt(e.target.value),
                    })
                  )
                }
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Meals/Day
              </label>
              <Input
                type="number"
                min="1"
                max="5"
                value={mealsPerDay}
                onChange={(e) =>
                  dispatch(
                    mealPlanIntents.setMealsPerDay({
                      mealsPerDay: parseInt(e.target.value),
                    })
                  )
                }
                required
              />
            </div>
          </div>

          <p className="text-sm text-gray-600">
            Total meals: <span className="font-semibold">{totalMeals}</span>
          </p>
        </div>

        {/* Dietary Restrictions */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Dietary Restrictions
          </label>
          <div className="grid grid-cols-2 gap-3">
            {DIETARY_RESTRICTIONS.map((restriction) => (
              <label
                key={restriction}
                className="flex items-center gap-2 cursor-pointer"
              >
                <Checkbox
                  checked={selectedRestrictions.includes(restriction)}
                  onChange={() =>
                    dispatch(
                      mealPlanIntents.toggleDietaryRestriction({ restriction })
                    )
                  }
                />
                <span className="text-sm text-gray-700">{restriction}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Excluded Ingredients */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Exclude Ingredients
          </label>
          <Input
            type="text"
            placeholder="e.g., tomatoes, mushrooms, bell peppers"
            value={excludedIngredients}
            onChange={(e) =>
              dispatch(
                mealPlanIntents.setExcludedIngredients({
                  ingredients: e.target.value,
                })
              )
            }
          />
          <p className="text-xs text-gray-500 mt-1">
            Separate multiple ingredients with commas
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            type="submit"
            variant="primary"
            disabled={!isFormValid || isSubmitting}
            className="flex-1"
          >
            {isSubmitting ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Generating...
              </>
            ) : (
              'Generate Meal Plan'
            )}
          </Button>

          <Button
            type="button"
            variant="secondary"
            onClick={() => dispatch(mealPlanIntents.resetForm())}
            disabled={isSubmitting}
          >
            Reset
          </Button>
        </div>
      </div>
    </form>
  );
}
