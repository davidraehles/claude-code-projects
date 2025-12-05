/**
 * RecipeView - Display grocery items grouped by recipe
 */

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Checkbox } from '@/components/ui/Checkbox'
import type { GroceryItem } from '@/lib/types'

interface RecipeViewProps {
  items: GroceryItem[]
  checkedItems: Set<string>
  onItemToggle: (ingredient: string) => void
}

export function RecipeView({ items, checkedItems, onItemToggle }: RecipeViewProps) {
  // Group items by recipe
  const itemsByRecipe = groupItemsByRecipe(items)
  const recipeNames = Object.keys(itemsByRecipe).sort()

  if (recipeNames.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <p className="text-yellow-800">
          No recipe information available for these items. Switch to Category View to see items grouped by category.
        </p>
      </div>
    )
  }

  return (
    <div id="recipe-view" role="tabpanel" className="space-y-6">
      {recipeNames.map((recipeName) => (
        <Card key={recipeName}>
          <CardHeader>
            <CardTitle className="flex items-center">
              <span className="mr-2">🍽️</span>
              {recipeName}
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({itemsByRecipe[recipeName].length} ingredients)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {itemsByRecipe[recipeName].map((item, idx) => (
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
                    {item.category && (
                      <span className="text-xs text-gray-500 ml-2">
                        ({item.category})
                      </span>
                    )}
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

// Helper: Group items by recipe
function groupItemsByRecipe(items: GroceryItem[]): { [key: string]: GroceryItem[] } {
  const grouped: { [key: string]: GroceryItem[] } = {}

  items.forEach((item) => {
    // If item has recipe sources, add to each recipe group
    if (item.recipe_sources && item.recipe_sources.length > 0) {
      item.recipe_sources.forEach((source) => {
        if (!grouped[source.recipe_name]) {
          grouped[source.recipe_name] = []
        }
        grouped[source.recipe_name].push(item)
      })
    } else {
      // Items without recipe sources go to "Other Items"
      const otherKey = 'Other Items'
      if (!grouped[otherKey]) {
        grouped[otherKey] = []
      }
      grouped[otherKey].push(item)
    }
  })

  return grouped
}
