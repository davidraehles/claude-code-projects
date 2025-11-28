'use client'

/**
 * Meal Plan detail page - View specific meal plan with recipes.
 * Refactored to use Auth Context and React Query hooks with MCP workflow integration.
 */

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { useMealPlan } from '@/hooks/queries/useMealPlans'
import { useCreateCartFromMealPlanWorkflow } from '@/hooks/queries/useWorkflows'
import { useKnusprCredentials } from '@/hooks/queries/useKnusprCredentials'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Checkbox } from '@/components/ui/Checkbox'

export default function MealPlanDetailPage() {
  const params = useParams()
  const router = useRouter()
  const mealPlanId = parseInt(params.id as string)

  // Local state for delivery preferences modal
  const [showDeliveryModal, setShowDeliveryModal] = useState(false)
  const [preferredTimeSlot, setPreferredTimeSlot] = useState<'morning' | 'afternoon' | 'evening'>('afternoon')
  const [budgetOptimization, setBudgetOptimization] = useState(false)

  // Auth state from context
  const { user, isLoading: authLoading } = useAuth()

  // Data fetching with React Query
  const { data: mealPlan, isLoading: mealPlanLoading, error: mealPlanError } = useMealPlan(mealPlanId)

  // Knuspr credentials status
  const { credentialStatus } = useKnusprCredentials()

  // Workflow mutation for generating cart with MCP integration
  const workflowMutation = useCreateCartFromMealPlanWorkflow()

  // Derived state
  const loading = mealPlanLoading
  const error = mealPlanError?.message || workflowMutation.error?.message || null
  const generatingCart = workflowMutation.isPending
  const hasKnusprCredentials = credentialStatus.data?.has_credentials || false

  // Generate grocery cart with delivery preferences
  const handleGenerateCart = () => {
    if (!hasKnusprCredentials) {
      // Show credentials setup prompt
      alert('Please configure Knuspr credentials first. Go to your account settings.')
      return
    }
    // Show delivery preferences modal
    setShowDeliveryModal(true)
  }

  // Submit workflow with delivery preferences
  const handleSubmitWorkflow = () => {
    workflowMutation.mutate(
      {
        mealPlanId,
        deliveryPreferences: {
          preferred_time_slot: preferredTimeSlot,
          budget_optimization: budgetOptimization,
        },
      },
      {
        onSuccess: (response) => {
          console.log('✅ Workflow completed:', response)
          setShowDeliveryModal(false)
          if (response.result?.cart_id) {
            router.push(`/grocery-carts/${response.result.cart_id}`)
          }
        },
        onError: (err) => {
          console.error('Failed to generate cart from meal plan:', err)
        },
      }
    )
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading meal plan...</p>
        </div>
      </div>
    )
  }

  if (error && !mealPlan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="text-center">
            <span className="text-4xl mb-3 block">⚠️</span>
            <h3 className="text-red-900 font-semibold mb-2">Error loading meal plan</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <Link href="/meal-plans">
              <Button variant="outline">Back to Meal Plans</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!mealPlan) {
    return null
  }

  // Days are already organized
  const days = mealPlan.days.sort((a, b) => a.day_number - b.day_number)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Link href="/" className="flex items-center space-x-2">
                <span className="text-3xl">🍽️</span>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  MealPlannerAI
                </span>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              {user?.email && (
                <span className="text-sm text-gray-600">👤 {user.email}</span>
              )}
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  Recipes
                </Button>
              </Link>
              <Link href="/meal-plans">
                <Button variant="ghost" size="sm">
                  Meal Plans
                </Button>
              </Link>
              <Link href="/generate">
                <Button variant="primary" size="sm">
                  Generate Plan
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Page Header */}
        <div className="mb-8">
          <Link href="/meal-plans" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
            ← Back to Meal Plans
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Meal Plan for {new Date(mealPlan.start_date).toLocaleDateString()}
          </h1>
          <p className="text-gray-600">
            {mealPlan.num_days} days • {mealPlan.num_people} people • {mealPlan.meals_per_day} meals/day
          </p>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Ready to shop?</h3>
              <p className="text-sm text-gray-600">
                {hasKnusprCredentials
                  ? 'Generate a Knuspr shopping cart with real products and delivery slots'
                  : 'Configure Knuspr integration to generate a real shopping cart'}
              </p>
            </div>
            <Button
              variant="primary"
              onClick={handleGenerateCart}
              disabled={generatingCart}
            >
              {generatingCart ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </span>
              ) : (
                <span>🛒 {hasKnusprCredentials ? 'Generate Knuspr Cart' : 'Setup Knuspr'}</span>
              )}
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Meals by Day */}
        <div className="space-y-8">
          {days.map((day) => (
              <div key={day.day_number}>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Day {day.day_number} - {new Date(day.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                </h2>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {day.meals.map((meal, idx) => (
                    <Card key={meal.id} hover>
                      <CardHeader>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-blue-600 uppercase">
                            {meal.meal_type || `Meal ${idx + 1}`}
                          </span>
                          <span className="text-xs text-gray-500">
                            {meal.servings} servings
                          </span>
                        </div>
                        <CardTitle className="text-lg">{meal.recipe.title}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {/* Ingredients */}
                        <div className="mb-3">
                          <p className="text-xs font-semibold text-gray-700 mb-1">Ingredients:</p>
                          <ul className="text-xs text-gray-600 space-y-0.5">
                            {meal.recipe.ingredients.slice(0, 3).map((ing, idx) => (
                              <li key={idx} className="line-clamp-1">• {ing}</li>
                            ))}
                            {meal.recipe.ingredients.length > 3 && (
                              <li className="text-gray-500 italic">
                                +{meal.recipe.ingredients.length - 3} more...
                              </li>
                            )}
                          </ul>
                        </div>

                        {/* Dietary tags */}
                        {meal.recipe.dietary_tags && meal.recipe.dietary_tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {meal.recipe.dietary_tags.map((tag) => (
                              <span
                                key={tag}
                                className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Nutrition */}
                        {meal.recipe.nutrition && (
                          <div className="grid grid-cols-3 gap-2 text-xs text-gray-600 border-t pt-2">
                            <div className="text-center">
                              <div className="font-semibold text-gray-900">
                                {Math.round(meal.recipe.nutrition.calories || 0)}
                              </div>
                              <div className="text-gray-500">cal</div>
                            </div>
                            <div className="text-center border-l border-r">
                              <div className="font-semibold text-gray-900">
                                {Math.round(meal.recipe.nutrition.protein || 0)}g
                              </div>
                              <div className="text-gray-500">protein</div>
                            </div>
                            <div className="text-center">
                              <div className="font-semibold text-gray-900">
                                {Math.round(meal.recipe.nutrition.carbs || 0)}g
                              </div>
                              <div className="text-gray-500">carbs</div>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
        </div>

        {/* Delivery Preferences Modal */}
        {showDeliveryModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Delivery Preferences</CardTitle>
                <CardDescription>
                  Choose your preferred delivery time and optimization strategy
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Time Slot Selection */}
                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-3">Preferred Time Slot</p>
                  <div className="space-y-2">
                    {(['morning', 'afternoon', 'evening'] as const).map((slot) => (
                      <label key={slot} className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          name="timeSlot"
                          value={slot}
                          checked={preferredTimeSlot === slot}
                          onChange={(e) => setPreferredTimeSlot(e.target.value as 'morning' | 'afternoon' | 'evening')}
                          className="w-4 h-4 text-blue-600"
                        />
                        <span className="ml-3 capitalize font-medium text-gray-700">
                          {slot === 'morning' && '🌅 Morning (6AM - 12PM)'}
                          {slot === 'afternoon' && '☀️ Afternoon (12PM - 6PM)'}
                          {slot === 'evening' && '🌙 Evening (6PM - 10PM)'}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Budget Optimization */}
                <div>
                  <Checkbox
                    label="Optimize for budget (find cheapest delivery option)"
                    checked={budgetOptimization}
                    onChange={(checked) => setBudgetOptimization(checked)}
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Without this, we'll prioritize the earliest available delivery slot
                  </p>
                </div>

                {/* Workflow Error */}
                {workflowMutation.error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-700">
                      {workflowMutation.error.message}
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeliveryModal(false)}
                    disabled={generatingCart}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleSubmitWorkflow}
                    disabled={generatingCart}
                    className="flex-1"
                  >
                    {generatingCart ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Creating Cart...
                      </span>
                    ) : (
                      'Create Cart'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  )
}
