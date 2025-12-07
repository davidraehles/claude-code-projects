'use client'

/**
 * Grocery Carts list page - View all generated grocery lists.
 * Shows a list of grocery carts the user has created from meal plans.
 */

import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/Button'

export default function GroceryCartsPage() {
  // Auth state from context
  const { user, isLoading: authLoading } = useAuth()

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
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Grocery Lists</h1>
          <p className="text-sm sm:text-base text-gray-600">
            Your generated grocery shopping lists from meal plans
          </p>
        </div>

        {/* Empty State */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">🛒</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">No grocery lists yet</h3>
          <p className="text-gray-600 mb-6">
            Create a meal plan and generate a grocery list to get started with your shopping.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/meal-plans">
              <Button variant="outline">View Meal Plans</Button>
            </Link>
            <Link href="/generate">
              <Button variant="primary">Generate New Plan</Button>
            </Link>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="mr-2">💡</span>
            How to Create a Grocery List
          </h3>
          <ol className="text-sm text-blue-800 space-y-2 list-decimal list-inside">
            <li>Go to <Link href="/meal-plans" className="font-semibold hover:underline">Meal Plans</Link> and select a meal plan</li>
            <li>Click &quot;Generate Grocery Cart&quot; on the meal plan detail page</li>
            <li>Review your shopping list with items organized by category or recipe</li>
            <li>Check off items as you shop and export or print your list</li>
          </ol>
        </div>
      </main>
    </div>
  )
}
