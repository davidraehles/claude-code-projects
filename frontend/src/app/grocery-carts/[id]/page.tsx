'use client'

/**
 * Grocery Cart detail page - Shopping list from meal plan.
 * Refactored to use Auth Context, React Query hooks, and Action/Intent Layer (ARCH-004).
 */

import React from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { useGroceryCart } from '@/hooks/queries/useGroceryCarts'
import { usePersistedReducer } from '@/hooks/usePersistedReducer'
import {
  groceryCartReducer,
  getInitialCartState,
  selectCheckedCount,
  type GroceryCartState,
} from '@/reducers/groceryCartReducer'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { ViewToggle } from '@/components/grocery/ViewToggle'
import { RecipeView } from '@/components/grocery/RecipeView'
import { CategoryView } from '@/components/grocery/CategoryView'
import { UnmatchedItemsAlert } from '@/components/grocery/UnmatchedItemsAlert'
import type { GroceryCart, GroceryItem } from '@/lib/types'

export default function GroceryCartPage() {
  const params = useParams()

  // Safely parse cart ID from params
  const rawId = params?.id
  const cartId = typeof rawId === 'string' ? parseInt(rawId, 10) : NaN
  const isValidId = !isNaN(cartId) && cartId > 0

  // Auth state from context
  const { user, isLoading: authLoading } = useAuth()

  // Data fetching with React Query - only fetch if ID is valid
  const { data: cart, isLoading: cartLoading, error: cartError } = useGroceryCart(cartId, isValidId)

  // Local UI state - Persisted reducer with DevTools (ARCH-004 + ARCH-010 + ARCH-011)
  const [cartState, dispatch] = usePersistedReducer(groceryCartReducer, {
    key: `grocery-cart-${cartId}`,
    initialState: getInitialCartState(),
    version: 1,
    devToolsName: `GroceryCart-${cartId}`, // Enable Redux DevTools
    // Custom serialization for Set
    serialize: (persisted) => {
      const serializable = {
        checkedItems: Array.from(persisted.checkedItems),
        viewMode: persisted.viewMode,
      }
      return JSON.stringify(serializable)
    },
    // Custom deserialization for Set
    deserialize: (json): GroceryCartState => {
      const parsed = JSON.parse(json)
      return {
        checkedItems: new Set<string>(parsed.checkedItems || []),
        viewMode: parsed.viewMode || 'category',
      }
    },
    validate: (state): state is GroceryCartState => {
      return (
        state !== null &&
        typeof state === 'object' &&
        'checkedItems' in state &&
        state.checkedItems instanceof Set &&
        'viewMode' in state &&
        (state.viewMode === 'recipe' || state.viewMode === 'category')
      )
    },
  })

  // Derived state
  const loading = cartLoading
  const error = cartError?.message || null
  const checkedCount = selectCheckedCount(cartState)

  // Handle view mode changes with sessionStorage persistence
  const handleViewChange = (newView: 'recipe' | 'category') => {
    dispatch({ type: 'SET_VIEW_MODE', payload: { viewMode: newView } })
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(`grocery-cart-view-${cartId}`, newView)
    }
  }

  // Initialize view mode from sessionStorage on mount
  React.useEffect(() => {
    if (typeof window !== 'undefined' && isValidId) {
      const savedView = sessionStorage.getItem(`grocery-cart-view-${cartId}`)
      if (savedView === 'recipe' || savedView === 'category') {
        dispatch({ type: 'SET_VIEW_MODE', payload: { viewMode: savedView } })
      }
    }
  }, [cartId, isValidId, dispatch])

  // Print grocery list
  const handlePrint = () => {
    window.print()
  }

  // Export to text
  const handleExport = () => {
    if (!cart) return

    const text = generateTextExport(cart, cartState.checkedItems, cartState.viewMode)
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `grocery-list-${cart.id}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Handle invalid cart ID
  if (!isValidId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="text-center">
            <span className="text-4xl mb-3 block">⚠️</span>
            <h3 className="text-red-900 font-semibold mb-2">Invalid grocery cart ID</h3>
            <p className="text-red-700 mb-4">The grocery cart ID provided is not valid.</p>
            <Link href="/meal-plans">
              <Button variant="secondary">Back to Meal Plans</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading grocery list...</p>
        </div>
      </div>
    )
  }

  if (error && !cart) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="text-center">
            <span className="text-4xl mb-3 block">⚠️</span>
            <h3 className="text-red-900 font-semibold mb-2">Error loading grocery cart</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <Link href="/meal-plans">
              <Button variant="secondary">Back to Meal Plans</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!cart) {
    return null
  }

  const totalCount = cart.items.length

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="print:hidden">
        <Header userEmail={user?.email || null} />
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Page Header */}
        <div className="mb-8 print:mb-6">
          <Link
            href={`/meal-plans/${cart.meal_plan_id}`}
            className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block print:hidden"
          >
            ← Back to Meal Plan
          </Link>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2 print:text-3xl">
            Grocery List
          </h1>
          <p className="text-sm sm:text-base text-gray-600 print:text-sm">
            Shopping list for Meal Plan #{cart.meal_plan_id}
          </p>
        </div>

        {/* Actions Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-6 mb-8 print:hidden">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="w-full sm:w-auto">
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-2xl">✓</span>
                <h3 className="font-semibold text-gray-900">
                  {checkedCount} of {totalCount} items checked
                </h3>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(checkedCount / totalCount) * 100}%` }}
                />
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
              <Button variant="secondary" onClick={handleExport} className="w-full sm:w-auto">
                <span className="mr-2">📄</span>
                Export TXT
              </Button>
              <Button variant="primary" onClick={handlePrint} className="w-full sm:w-auto">
                <span className="mr-2">🖨️</span>
                Print List
              </Button>
            </div>
          </div>
        </div>

        {/* Print Header (hidden on screen) */}
        <div className="hidden print:block mb-6 pb-4 border-b-2 border-gray-300">
          <h2 className="text-2xl font-bold">Grocery Shopping List</h2>
          <p className="text-sm text-gray-600">Meal Plan #{cart.meal_plan_id}</p>
          <p className="text-sm text-gray-600">
            Generated: {new Date(cart.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Unmatched Items Alert */}
        {(cart.unmatched_items?.length ?? 0) > 0 || (cart.unavailable_items?.length ?? 0) > 0 ? (
          <div className="mb-6 print:hidden">
            <UnmatchedItemsAlert
              items={[...(cart.unmatched_items || []), ...(cart.unavailable_items || [])]}
              cartId={cart.id}
            />
          </div>
        ) : null}

        {/* View Toggle */}
        <div className="mb-6 print:hidden">
          <ViewToggle
            currentView={cartState.viewMode}
            onViewChange={handleViewChange}
          />
        </div>

        {/* Items Display - Conditional based on view mode */}
        {cartState.viewMode === 'recipe' ? (
          <RecipeView
            items={cart.items}
            checkedItems={cartState.checkedItems}
            onItemToggle={(ingredient) =>
              dispatch({ type: 'USER_TOGGLED_ITEM', payload: ingredient })
            }
          />
        ) : (
          <CategoryView
            items={cart.items}
            checkedItems={cartState.checkedItems}
            onItemToggle={(ingredient) =>
              dispatch({ type: 'USER_TOGGLED_ITEM', payload: ingredient })
            }
          />
        )}

        {/* Summary */}
        {cart.items.some((item) => item.estimated_cost) && (
          <div className="mt-8 bg-gradient-to-br from-green-50 to-blue-50 border border-green-200 rounded-lg p-6 print:bg-white print:border-2 print:border-gray-300">
            <h3 className="font-semibold text-gray-900 mb-4 print:text-lg">
              Estimated Total
            </h3>
            <div className="text-3xl font-bold text-green-700 print:text-black">
              $
              {cart.items
                .reduce((sum, item) => sum + (item.estimated_cost || 0), 0)
                .toFixed(2)}
            </div>
            <p className="text-sm text-gray-600 mt-2 print:text-black">
              Prices are estimates and may vary by store
            </p>
          </div>
        )}

        {/* Tips */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6 print:hidden">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="mr-2">💡</span>
            Shopping Tips
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• Check off items as you shop to track your progress</li>
            <li>• Categories are organized by typical grocery store layout</li>
            <li>• Compare prices between brands to stay within budget</li>
            <li>• Consider buying non-perishables in bulk to save money</li>
          </ul>
        </div>
      </main>
    </div>
  )
}

// Helper: Generate text export
function generateTextExport(
  cart: GroceryCart,
  checkedItems: Set<string>,
  viewMode: 'recipe' | 'category'
): string {
  const lines: string[] = []

  lines.push('=' + '='.repeat(50))
  lines.push('GROCERY SHOPPING LIST')
  lines.push(`Meal Plan #${cart.meal_plan_id}`)
  lines.push(`View: ${viewMode === 'recipe' ? 'Recipe View' : 'Category View'}`)
  lines.push(`Generated: ${new Date(cart.created_at).toLocaleString()}`)
  lines.push('=' + '='.repeat(50))
  lines.push('')

  if (viewMode === 'recipe') {
    // Group by recipe
    const itemsByRecipe: { [key: string]: GroceryItem[] } = {}
    cart.items.forEach((item) => {
      if (item.recipe_sources && item.recipe_sources.length > 0) {
        item.recipe_sources.forEach((source) => {
          if (!itemsByRecipe[source.recipe_name]) {
            itemsByRecipe[source.recipe_name] = []
          }
          itemsByRecipe[source.recipe_name].push(item)
        })
      } else {
        const otherKey = 'Other Items'
        if (!itemsByRecipe[otherKey]) {
          itemsByRecipe[otherKey] = []
        }
        itemsByRecipe[otherKey].push(item)
      }
    })

    const recipes = Object.keys(itemsByRecipe).sort()
    recipes.forEach((recipe) => {
      lines.push(`\n${recipe.toUpperCase()} (${itemsByRecipe[recipe].length} ingredients)`)
      lines.push('-'.repeat(50))

      itemsByRecipe[recipe].forEach((item) => {
        const checked = checkedItems.has(item.ingredient) ? '[✓]' : '[ ]'
        const cost = item.estimated_cost ? ` - $${item.estimated_cost.toFixed(2)}` : ''
        const category = item.category ? ` (${item.category})` : ''
        lines.push(`${checked} ${item.ingredient} - ${item.quantity}${category}${cost}`)
      })
    })
  } else {
    // Group by category
    const itemsByCategory: { [key: string]: GroceryItem[] } = {}
    cart.items.forEach((item) => {
      const category = item.category || 'Uncategorized'
      if (!itemsByCategory[category]) {
        itemsByCategory[category] = []
      }
      itemsByCategory[category].push(item)
    })

    const categories = Object.keys(itemsByCategory).sort()
    categories.forEach((category) => {
      lines.push(`\n${category.toUpperCase()} (${itemsByCategory[category].length} items)`)
      lines.push('-'.repeat(50))

      itemsByCategory[category].forEach((item) => {
        const checked = checkedItems.has(item.ingredient) ? '[✓]' : '[ ]'
        const cost = item.estimated_cost ? ` - $${item.estimated_cost.toFixed(2)}` : ''
        const recipes =
          item.recipe_sources && item.recipe_sources.length > 0
            ? ` [${item.recipe_sources.map((s) => s.recipe_name).join(', ')}]`
            : ''
        lines.push(`${checked} ${item.ingredient} - ${item.quantity}${recipes}${cost}`)
      })
    })
  }

  lines.push('')
  lines.push('=' + '='.repeat(50))
  lines.push(`Total Items: ${cart.items.length}`)
  lines.push(`Checked: ${checkedItems.size}`)

  const totalCost = cart.items.reduce((sum, item) => sum + (item.estimated_cost || 0), 0)
  if (totalCost > 0) {
    lines.push(`Estimated Total: $${totalCost.toFixed(2)}`)
  }

  lines.push('=' + '='.repeat(50))

  return lines.join('\n')
}
