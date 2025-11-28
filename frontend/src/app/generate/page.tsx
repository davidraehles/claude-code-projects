'use client'

/**
 * Meal Plan Generator page - Create personalized meal plans.
 * Refactored to use Auth Context, React Query hooks, and Action/Intent Layer (ARCH-004).
 */

import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateMealPlan } from '@/hooks/queries/useMealPlans'
import { useReducerWithDevTools } from '@/hooks/useReducerWithDevTools'
import {
  mealPlanFormReducer,
  getInitialState,
  selectMealPlanRequest,
  selectTotalMeals,
} from '@/reducers/mealPlanFormReducer'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Checkbox } from '@/components/ui/Checkbox'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

const COMMON_DIETARY_RESTRICTIONS = [
  'vegetarian',
  'vegan',
  'gluten-free',
  'dairy-free',
  'keto',
  'paleo',
  'low-carb',
  'low-fat',
  'nut-free',
  'pescatarian',
]

export default function GeneratePage() {
  const router = useRouter()

  // Auth state from context
  const { user, isLoading: authLoading } = useAuth()

  // Create meal plan mutation
  const createMealPlan = useCreateMealPlan()

  // Form state - useReducer with DevTools integration (ARCH-004 + ARCH-011)
  const [formState, dispatch] = useReducerWithDevTools(
    mealPlanFormReducer,
    getInitialState(),
    'MealPlanForm'
  )

  // Derived state
  const generating = createMealPlan.isPending
  const error = createMealPlan.error?.message || null
  const totalMeals = selectTotalMeals(formState)

  // Handle form submission - Pure selector extracts request data (ARCH-004)
  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()

    // Use selector to convert form state to API request
    const requestData = selectMealPlanRequest(formState)

    // Create meal plan using mutation
    createMealPlan.mutate(requestData, {
      onSuccess: (mealPlan) => {
        console.log('✅ Meal plan created:', mealPlan)
        router.push(`/meal-plans/${mealPlan.id}`)
      },
      onError: (err) => {
        console.error('Failed to generate meal plan:', err)
      },
    })
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Authenticating...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header userEmail={user?.email || null} />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Page Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            Generate Meal Plan
          </h1>
          <p className="text-sm sm:text-base text-gray-600">
            Create a personalized weekly meal plan based on your preferences
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="text-red-900 font-semibold mb-1">
                  Failed to generate meal plan
                </h3>
                <p className="text-red-700">{error}</p>
                <p className="text-sm text-red-600 mt-2">
                  Make sure the backend API is running and you have recipes in your library.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Generation Form */}
        <form onSubmit={handleGenerate}>
          <div className="space-y-6">
            {/* Basic Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Settings</CardTitle>
                <CardDescription>
                  Configure your meal plan duration and household size
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <Input
                    label="Start Date"
                    type="date"
                    value={formState.startDate}
                    onChange={(e) => dispatch({ type: 'USER_SET_START_DATE', payload: e.target.value })}
                    required
                    min={new Date().toISOString().split('T')[0]}
                  />
                  <Input
                    label="Number of Days"
                    type="number"
                    value={formState.numDays}
                    onChange={(e) => dispatch({ type: 'USER_CHANGED_NUM_DAYS', payload: parseInt(e.target.value) })}
                    required
                    min={1}
                    max={14}
                  />
                  <Input
                    label="Number of People"
                    type="number"
                    value={formState.numPeople}
                    onChange={(e) => dispatch({ type: 'USER_CHANGED_NUM_PEOPLE', payload: parseInt(e.target.value) })}
                    required
                    min={1}
                    max={10}
                  />
                  <Input
                    label="Meals per Day"
                    type="number"
                    value={formState.mealsPerDay}
                    onChange={(e) => dispatch({ type: 'USER_CHANGED_MEALS_PER_DAY', payload: parseInt(e.target.value) })}
                    required
                    min={1}
                    max={5}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Dietary Restrictions */}
            <Card>
              <CardHeader>
                <CardTitle>Dietary Restrictions</CardTitle>
                <CardDescription>
                  Select any dietary requirements or preferences (optional)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {COMMON_DIETARY_RESTRICTIONS.map((restriction) => (
                    <Checkbox
                      key={restriction}
                      label={restriction.charAt(0).toUpperCase() + restriction.slice(1)}
                      checked={formState.selectedRestrictions.includes(restriction)}
                      onChange={() => dispatch({ type: 'USER_TOGGLED_DIETARY_RESTRICTION', payload: restriction })}
                      disabled={generating}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Excluded Ingredients */}
            <Card>
              <CardHeader>
                <CardTitle>Excluded Ingredients</CardTitle>
                <CardDescription>
                  List any ingredients you want to avoid (comma-separated, optional)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Input
                  placeholder="e.g., mushrooms, cilantro, bell peppers"
                  value={formState.excludedIngredients}
                  onChange={(e) => dispatch({ type: 'USER_CHANGED_EXCLUDED_INGREDIENTS', payload: e.target.value })}
                  disabled={generating}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Separate multiple ingredients with commas
                </p>
              </CardContent>
            </Card>

            {/* Summary & Generate */}
            <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm mb-6">
                  <p>
                    <span className="font-semibold">📅 Duration:</span>{' '}
                    {formState.numDays} day{formState.numDays !== 1 ? 's' : ''} starting {new Date(formState.startDate).toLocaleDateString()}
                  </p>
                  <p>
                    <span className="font-semibold">👥 Household:</span>{' '}
                    {formState.numPeople} person{formState.numPeople !== 1 ? 's' : ''},{' '}
                    {formState.mealsPerDay} meal{formState.mealsPerDay !== 1 ? 's' : ''} per day
                  </p>
                  <p>
                    <span className="font-semibold">🎯 Total Meals:</span>{' '}
                    {totalMeals} meals
                  </p>
                  {formState.selectedRestrictions.length > 0 && (
                    <p>
                      <span className="font-semibold">🥗 Dietary:</span>{' '}
                      {formState.selectedRestrictions.join(', ')}
                    </p>
                  )}
                  {formState.excludedIngredients && (
                    <p>
                      <span className="font-semibold">🚫 Excluding:</span>{' '}
                      {formState.excludedIngredients}
                    </p>
                  )}
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full"
                  disabled={generating}
                >
                  {generating ? (
                    <span className="flex items-center justify-center">
                      <svg
                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      Generating Your Meal Plan...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <span className="mr-2">✨</span>
                      Generate Meal Plan
                    </span>
                  )}
                </Button>

                {generating && (
                  <p className="text-xs text-gray-600 text-center mt-3">
                    This may take 10-30 seconds depending on your preferences...
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="mr-2">💡</span>
            How it works
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>
              • Our AI analyzes your recipe library and preferences
            </li>
            <li>
              • Recipes are selected to maximize variety and nutrition balance
            </li>
            <li>
              • All dietary restrictions and excluded ingredients are respected
            </li>
            <li>
              • You can adjust or regenerate your plan at any time
            </li>
          </ul>
        </div>
      </main>
    </div>
  )
}
