'use client'

/**
 * Meal Plan detail page - View specific meal plan with recipes.
 * Refactored to use Auth Context and React Query hooks.
 */

import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { useMealPlan } from '@/hooks/queries/useMealPlans'
import { useGenerateGroceryCart } from '@/hooks/queries/useGroceryCarts'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

export default function MealPlanDetailPage() {
  const params = useParams()
  const router = useRouter()
  const mealPlanId = parseInt(params.id as string)

  // Auth state from context
  const { user, isLoading: authLoading } = useAuth()

  // Data fetching with React Query
  const { data: mealPlan, isLoading: mealPlanLoading, error: mealPlanError } = useMealPlan(mealPlanId)

  // Generate grocery cart mutation
  const generateCart = useGenerateGroceryCart()

  // Derived state
  const loading = mealPlanLoading
  const error = mealPlanError?.message || generateCart.error?.message || null
  const generatingCart = generateCart.isPending

  // Generate grocery cart handler
  const handleGenerateCart = () => {
    generateCart.mutate(mealPlanId, {
      onSuccess: (cart) => {
        console.log('✅ Grocery cart generated:', cart)
        router.push(`/grocery-carts/${cart.id}`)
      },
      onError: (err) => {
        console.error('Failed to generate grocery cart:', err)
      },
    })
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
                Generate a consolidated grocery list for all recipes
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
                <span>🛒 Generate Grocery List</span>
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
      </main>
    </div>
  )
}
