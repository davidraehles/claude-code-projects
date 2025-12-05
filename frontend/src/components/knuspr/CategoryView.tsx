/**
 * CategoryView component for displaying cart items grouped by category.
 *
 * Groups ingredients by their categories (produce, dairy, meat, etc.)
 * in a logical shopping order for efficient grocery shopping.
 */

'use client';

import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, Package, CheckCircle2, Tag } from 'lucide-react';

export interface RecipeSource {
  recipe_id: number;
  recipe_name: string;
}

export interface CartItem {
  id?: number;
  name: string;
  quantity: number;
  unit: string;
  category?: string;
  unit_price?: number;
  total_price?: number;
  recipe_sources?: RecipeSource[];
  knuspr_product_id?: string;
  knuspr_url?: string;
  is_purchased: boolean;
}

interface CategoryViewProps {
  cart_items: CartItem[];
  onItemToggle?: (itemId: number, purchased: boolean) => void;
  className?: string;
}

interface GroupedByCategory {
  [category: string]: CartItem[];
}

// Define shopping order for categories (produce first, frozen last)
const CATEGORY_ORDER = [
  'produce',
  'dairy',
  'meat',
  'fish',
  'bakery',
  'grains',
  'pantry',
  'canned_goods',
  'oils_vinegar',
  'spices',
  'beverages',
  'snacks',
  'frozen',
  'uncategorized',
];

// Category icons for visual identification
const CATEGORY_ICONS: Record<string, string> = {
  produce: '🥕',
  dairy: '🥛',
  meat: '🍗',
  fish: '🐟',
  bakery: '🍞',
  grains: '🌾',
  pantry: '🥫',
  canned_goods: '🥫',
  oils_vinegar: '🫒',
  spices: '🌶️',
  beverages: '🥤',
  snacks: '🍿',
  frozen: '❄️',
  uncategorized: '📦',
};

export const CategoryView: React.FC<CategoryViewProps> = ({
  cart_items,
  onItemToggle,
  className = '',
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  // Group items by category and sort by shopping order
  const groupedItems = useMemo(() => {
    const grouped: GroupedByCategory = {};

    // Group items
    cart_items.forEach((item) => {
      const category = item.category?.toLowerCase() || 'uncategorized';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(item);
    });

    // Sort categories by shopping order
    const sortedGrouped: GroupedByCategory = {};
    const categories = Object.keys(grouped);

    // First add categories in defined order
    CATEGORY_ORDER.forEach((category) => {
      if (grouped[category]) {
        sortedGrouped[category] = grouped[category];
      }
    });

    // Then add any remaining categories not in the order
    categories.forEach((category) => {
      if (!CATEGORY_ORDER.includes(category)) {
        sortedGrouped[category] = grouped[category];
      }
    });

    return sortedGrouped;
  }, [cart_items]);

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const handleCheckboxChange = (item: CartItem, checked: boolean) => {
    if (onItemToggle && item.id) {
      onItemToggle(item.id, checked);
    }
  };

  const formatCategoryName = (category: string): string => {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' & ');
  };

  // Empty state
  if (cart_items.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <Package className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">No items in cart</p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {Object.entries(groupedItems).map(([category, items]) => {
        const isExpanded = expandedCategories.has(category);
        const purchasedCount = items.filter((item) => item.is_purchased).length;
        const totalItems = items.length;
        const totalPrice = items.reduce(
          (sum, item) => sum + (item.total_price || 0),
          0
        );

        return (
          <div
            key={category}
            className="rounded-lg border border-gray-200 bg-white overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Category Header */}
            <button
              onClick={() => toggleCategory(category)}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
              aria-expanded={isExpanded}
              aria-controls={`category-${category}-items`}
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-lg" aria-hidden="true">
                    {CATEGORY_ICONS[category] || CATEGORY_ICONS.uncategorized}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {formatCategoryName(category)}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>
                      {purchasedCount} of {totalItems} items
                    </span>
                    {totalPrice > 0 && (
                      <>
                        <span className="text-gray-300">•</span>
                        <span className="font-medium text-gray-700">
                          €{totalPrice.toFixed(2)}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                {purchasedCount === totalItems && totalItems > 0 && (
                  <CheckCircle2 className="h-5 w-5 text-green-600" aria-label="All items purchased" />
                )}
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" aria-hidden="true" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" aria-hidden="true" />
                )}
              </div>
            </button>

            {/* Items List */}
            {isExpanded && (
              <div
                id={`category-${category}-items`}
                className="border-t border-gray-200 divide-y divide-gray-100"
              >
                {items.map((item, idx) => {
                  const itemKey = item.id || `${category}-item-${idx}`;

                  return (
                    <div
                      key={itemKey}
                      className={`
                        px-4 py-3 hover:bg-gray-50 transition-colors
                        ${item.is_purchased ? 'bg-gray-50' : 'bg-white'}
                      `}
                    >
                      <label className="flex items-start gap-3 cursor-pointer group">
                        {/* Checkbox */}
                        <input
                          type="checkbox"
                          checked={item.is_purchased}
                          onChange={(e) => handleCheckboxChange(item, e.target.checked)}
                          className="mt-0.5 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
                          aria-label={`Mark ${item.name} as purchased`}
                        />

                        {/* Item Details */}
                        <div className="flex-1 min-w-0">
                          <p
                            className={`
                            font-medium truncate transition-all
                            ${item.is_purchased ? 'text-gray-500 line-through' : 'text-gray-900'}
                          `}
                          >
                            {item.name}
                          </p>
                          <div className="flex items-center gap-3 text-sm text-gray-500 mt-1">
                            <span>
                              {item.quantity} {item.unit}
                            </span>
                            {item.total_price !== undefined && (
                              <>
                                <span className="text-gray-300">•</span>
                                <span className="font-medium text-gray-700">
                                  €{item.total_price.toFixed(2)}
                                </span>
                              </>
                            )}
                            {item.unit_price !== undefined && (
                              <span className="text-xs text-gray-400">
                                (€{item.unit_price.toFixed(2)}/{item.unit})
                              </span>
                            )}
                          </div>
                          {/* Show recipe sources if available */}
                          {item.recipe_sources && item.recipe_sources.length > 0 && (
                            <div className="flex items-center gap-1 text-xs text-blue-600 mt-1">
                              <Tag className="h-3 w-3" aria-hidden="true" />
                              <span>
                                {item.recipe_sources.map((r) => r.recipe_name).join(', ')}
                              </span>
                            </div>
                          )}
                        </div>
                      </label>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default CategoryView;
