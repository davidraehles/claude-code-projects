/**
 * CategoryView - Display grocery items grouped by category
 */

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Checkbox } from '@/components/ui/Checkbox'
import type { GroceryItem } from '@/lib/types'

interface CategoryViewProps {
  items: GroceryItem[]
  checkedItems: Set<string>
  onItemToggle: (ingredient: string) => void
}

export function CategoryView({ items, checkedItems, onItemToggle }: CategoryViewProps) {
  // Group items by category
  const itemsByCategory = groupItemsByCategory(items)
  const categories = Object.keys(itemsByCategory).sort()

  return (
    <div id="category-view" role="tabpanel" className="space-y-6">
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
                      onChange={() => onItemToggle(item.ingredient)}
                    />
                  </div>
                  <div className="flex-1 print:flex print:justify-between">
                    <div className="flex flex-col">
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
                      {item.recipe_sources && item.recipe_sources.length > 0 && (
                        <div className="text-xs text-gray-500 mt-1">
                          Used in: {item.recipe_sources.map((s) => s.recipe_name).join(', ')}
                        </div>
                      )}
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
  )
}

// Helper: Group items by category
function groupItemsByCategory(items: GroceryItem[]): { [key: string]: GroceryItem[] } {
  const grouped: { [key: string]: GroceryItem[] } = {}

  items.forEach((item) => {
    const category = item.category || 'Uncategorized'
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
    Uncategorized: '📦',
    Other: '📦',
  }
  return icons[category] || '📦'
}
