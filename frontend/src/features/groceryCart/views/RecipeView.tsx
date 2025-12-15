/**
 * Recipe View - Pure component for recipe-organized grocery list
 */

'use client';

import { Checkbox } from '@/components/ui/Checkbox';

interface RecipeViewProps {
  items: Array<{
    ingredient: string;
    quantity: string;
    unit: string;
    recipe?: string;
  }>;
  checkedItems: Set<string>;
  onToggleItem: (ingredient: string) => void;
}

export function RecipeView({ items, checkedItems, onToggleItem }: RecipeViewProps) {
  // Group items by recipe
  const itemsByRecipe = items.reduce((acc, item) => {
    const recipe = item.recipe || 'General Items';
    if (!acc[recipe]) {
      acc[recipe] = [];
    }
    acc[recipe].push(item);
    return acc;
  }, {} as Record<string, typeof items>);

  const recipes = Object.keys(itemsByRecipe).sort();

  return (
    <div className="space-y-6">
      {recipes.map((recipe) => (
        <div key={recipe} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {recipe}
            <span className="text-sm font-normal text-gray-500 ml-2">
              ({itemsByRecipe[recipe].length} items)
            </span>
          </h3>
          <div className="space-y-3">
            {itemsByRecipe[recipe].map((item) => {
              const isChecked = checkedItems.has(item.ingredient);
              return (
                <label
                  key={item.ingredient}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    isChecked
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <Checkbox
                    checked={isChecked}
                    onChange={() => onToggleItem(item.ingredient)}
                  />
                  <span
                    className={`flex-1 ${
                      isChecked
                        ? 'line-through text-gray-500'
                        : 'text-gray-900'
                    }`}
                  >
                    {item.ingredient}
                  </span>
                  <span className="text-sm text-gray-600">
                    {item.quantity} {item.unit}
                  </span>
                </label>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
