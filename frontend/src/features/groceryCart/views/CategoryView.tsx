/**
 * Category View - Pure component for category-organized grocery list
 */

'use client';

import { Checkbox } from '@/components/ui/Checkbox';

interface CategoryViewProps {
  items: Array<{
    ingredient: string;
    quantity: string;
    unit: string;
    category?: string;
  }>;
  checkedItems: Set<string>;
  onToggleItem: (ingredient: string) => void;
}

export function CategoryView({ items, checkedItems, onToggleItem }: CategoryViewProps) {
  // Group items by category
  const itemsByCategory = items.reduce((acc, item) => {
    const category = item.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as Record<string, typeof items>);

  const categories = Object.keys(itemsByCategory).sort();

  return (
    <div className="space-y-6">
      {categories.map((category) => (
        <div key={category} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {category}
            <span className="text-sm font-normal text-gray-500 ml-2">
              ({itemsByCategory[category].length} items)
            </span>
          </h3>
          <div className="space-y-3">
            {itemsByCategory[category].map((item) => {
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
