'use client'

/**
 * Meal Plans list page - View all meal plans.
 * Refactored to use Auth Context and React Query hooks.
 */

import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { useMealPlans } from '@/hooks/queries/useMealPlans'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

export default function MealPlansPage() {
  // Auth state from context
  const { user, isLoading: authLoading } = useAuth()

  // Data fetching with React Query
  const { data: mealPlansData, isLoading: mealPlansLoading, error: mealPlansError } = useMealPlans(1, 20)

  // Derived state
  const mealPlans = mealPlansData?.items || []
  const loading = mealPlansLoading
  const error = mealPlansError?.message || null

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
      <main className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">My Meal Plans</h1>
          <p className="text-sm sm:text-base text-gray-600">
            View and manage your generated meal plans
          </p>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="text-red-900 font-semibold mb-1">Error loading meal plans</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-48 animate-pulse"
              >
                <div className="h-6 bg-gray-200 rounded mb-4 w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded mb-3 w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && mealPlans.length === 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">📅</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No meal plans yet</h3>
            <p className="text-gray-600 mb-6">
              Generate your first meal plan to get started with personalized meal planning.
            </p>
            <Link href="/generate">
              <Button variant="primary">Generate Meal Plan</Button>
            </Link>
          </div>
        )}

        {/* Meal Plans Grid */}
        {!loading && mealPlans.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mealPlans.map((plan) => (
              <Card key={plan.id} hover className="cursor-pointer">
                <Link href={`/meal-plans/${plan.id}`}>
                  <CardHeader>
                    <CardTitle>
                      {new Date(plan.start_date).toLocaleDateString()} - Week {plan.id}
                    </CardTitle>
                    <CardDescription>
                      {plan.num_days} days • {plan.num_people} people
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm text-gray-600">
                      <p>📅 Start: {new Date(plan.start_date).toLocaleDateString()}</p>
                      <p>🍽️ Meals per day: {plan.meals_per_day}</p>
                      <p>👥 Servings: {plan.num_people}</p>
                      <p className="text-xs text-gray-500 mt-3">
                        Created {new Date(plan.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </CardContent>
                </Link>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
