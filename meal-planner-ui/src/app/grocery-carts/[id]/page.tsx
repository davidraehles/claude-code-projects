'use client'

/**
 * Grocery Cart detail page - Shopping list from meal plan.
 */

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import { initTestAuth, restoreAuth, getCurrentUserEmail } from '@/lib/auth'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import type { GroceryCart, GroceryItem } from '@/lib/types'

export default function GroceryCartPage() {
  const params = useParams()
  const cartId = parseInt(params.id as string)

  const [cart, setCart] = useState<GroceryCart | null>(null)
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [authLoading, setAuthLoading] = useState(true)
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Initialize authentication
  useEffect(() => {
    async function authenticate() {
      try {
        const restored = restoreAuth()
        if (!restored) {
          await initTestAuth()
        }
        setUserEmail(getCurrentUserEmail())
        setAuthLoading(false)
      } catch (err) {
        console.error('Authentication failed:', err)
        setError('Failed to authenticate. Please refresh the page.')
        setAuthLoading(false)
      }
    }
    authenticate()
  }, [])

  // Load grocery cart
  useEffect(() => {
    if (authLoading) return

    async function loadCart() {
      try {
        setLoading(true)
        const groceryCart = await api.getGroceryCart(cartId)
        setCart(groceryCart)
        setError(null)
      } catch (err: any) {
        console.error('Failed to load grocery cart:', err)
        setError(err.message || 'Failed to load grocery cart')
      } finally {
        setLoading(false)
      }
    }

    loadCart()
  }, [authLoading, cartId])

  // Toggle item checked state
  const toggleItem = (ingredient: string) => {
    setCheckedItems((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(ingredient)) {
        newSet.delete(ingredient)
      } else {
        newSet.add(ingredient)
      }
      return newSet
    })
  }

  // Print grocery list
  const handlePrint = () => {
    window.print()
  }

  // Export to text
  const handleExport = () => {
    if (!cart) return

    const text = generateTextExport(cart, checkedItems)
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
              <Button variant="outline">Back to Meal Plans</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!cart) {
    return null
  }

  // Group items by category
  const itemsByCategory = groupItemsByCategory(cart.items)
  const categories = Object.keys(itemsByCategory).sort()
  const checkedCount = checkedItems.size
  const totalCount = cart.items.length

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 print:hidden">
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
              {userEmail && (
                <span className="text-sm text-gray-600">👤 {userEmail}</span>
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
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Page Header */}
        <div className="mb-8 print:mb-6">
          <Link
            href={`/meal-plans/${cart.meal_plan_id}`}
            className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block print:hidden"
          >
            ← Back to Meal Plan
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2 print:text-3xl">
            Grocery List
          </h1>
          <p className="text-gray-600 print:text-sm">
            Shopping list for Meal Plan #{cart.meal_plan_id}
          </p>
        </div>

        {/* Actions Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8 print:hidden">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div>
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
            <div className="flex gap-3">
              <Button variant="outline" onClick={handleExport}>
                <span className="mr-2">📄</span>
                Export TXT
              </Button>
              <Button variant="primary" onClick={handlePrint}>
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

        {/* Items by Category */}
        <div className="space-y-6">
          {categories.map((category) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="mr-2">{getCategoryIcon(category)}</span>
                  {category}
                  <span className="ml-2 text-sm font-normal text-gray-500">
                    ({itemsByCategory[category].length} items)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {itemsByCategory[category].map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-start space-x-3 print:py-1"
                    >
                      <div className="print:hidden">
                        <Checkbox
                          label=""
                          checked={checkedItems.has(item.ingredient)}
                          onChange={() => toggleItem(item.ingredient)}
                        />
                      </div>
                      <div className="flex-1 print:flex print:justify-between">
                        <div className="flex items-baseline space-x-2">
                          <span
                            className={`font-medium ${
                              checkedItems.has(item.ingredient)
                                ? 'line-through text-gray-400'
                                : 'text-gray-900'
                            } print:text-black print:no-underline`}
                          >
                            {item.ingredient}
                          </span>
                          <span className="text-sm text-gray-600 print:text-black">
                            {item.quantity}
                          </span>
                        </div>
                        {item.estimated_cost && (
                          <span className="text-sm text-gray-500 ml-auto print:text-black">
                            ${item.estimated_cost.toFixed(2)}
                          </span>
                        )}
                      </div>
                      <div className="hidden print:block w-6 h-6 border-2 border-gray-400" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

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

// Helper: Group items by category
function groupItemsByCategory(items: GroceryItem[]): { [key: string]: GroceryItem[] } {
  const grouped: { [key: string]: GroceryItem[] } = {}

  items.forEach((item) => {
    const category = item.category || 'Other'
    if (!grouped[category]) {
      grouped[category] = []
    }
    grouped[category].push(item)
  })

  return grouped
}

// Helper: Get category icon
function getCategoryIcon(category: string): string {
  const icons: { [key: string]: string } = {
    Produce: '🥬',
    Dairy: '🥛',
    Meat: '🥩',
    Seafood: '🐟',
    Bakery: '🍞',
    Pantry: '🥫',
    Frozen: '🧊',
    Beverages: '🥤',
    Snacks: '🍿',
    Other: '📦',
  }
  return icons[category] || '📦'
}

// Helper: Generate text export
function generateTextExport(cart: GroceryCart, checkedItems: Set<string>): string {
  const lines: string[] = []

  lines.push('=' + '='.repeat(50))
  lines.push('GROCERY SHOPPING LIST')
  lines.push(`Meal Plan #${cart.meal_plan_id}`)
  lines.push(`Generated: ${new Date(cart.created_at).toLocaleString()}`)
  lines.push('=' + '='.repeat(50))
  lines.push('')

  const itemsByCategory = groupItemsByCategory(cart.items)
  const categories = Object.keys(itemsByCategory).sort()

  categories.forEach((category) => {
    lines.push(`\n${category.toUpperCase()} (${itemsByCategory[category].length} items)`)
    lines.push('-'.repeat(50))

    itemsByCategory[category].forEach((item) => {
      const checked = checkedItems.has(item.ingredient) ? '[✓]' : '[ ]'
      const cost = item.estimated_cost ? ` - $${item.estimated_cost.toFixed(2)}` : ''
      lines.push(`${checked} ${item.ingredient} - ${item.quantity}${cost}`)
    })
  })

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
