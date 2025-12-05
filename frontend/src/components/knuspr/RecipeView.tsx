/**
 * RecipeView component for displaying cart items grouped by recipe.
 *
 * Groups ingredients by their source recipes, showing which recipes
 * each ingredient belongs to. Items can belong to multiple recipes.
 */

'use client';

import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, Package, CheckCircle2 } from 'lucide-react';

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

interface RecipeViewProps {
  cart_items: CartItem[];
  onItemToggle?: (itemId: number, purchased: boolean) => void;
  className?: string;
}

interface GroupedByRecipe {
  [recipeId: string]: {
    recipe_name: string;
    items: CartItem[];
  };
}

export const RecipeView: React.FC<RecipeViewProps> = ({
  cart_items,
  onItemToggle,
  className = '',
}) => {
  const [expandedRecipes, setExpandedRecipes] = useState<Set<string>>(new Set());

  // Group items by recipe
  const groupedItems = useMemo(() => {
    const grouped: GroupedByRecipe = {};
    const otherItems: CartItem[] = [];

    cart_items.forEach((item) => {
      if (item.recipe_sources && item.recipe_sources.length > 0) {
        // Add item to each recipe it belongs to
        item.recipe_sources.forEach((recipe) => {
          const key = `recipe-${recipe.recipe_id}`;
          if (!grouped[key]) {
            grouped[key] = {
              recipe_name: recipe.recipe_name,
              items: [],
            };
          }
          grouped[key].items.push(item);
        });
      } else {
        // Items without recipes go to "Other Items"
        otherItems.push(item);
      }
    });

    // Add "Other Items" section if there are any
    if (otherItems.length > 0) {
      grouped['other'] = {
        recipe_name: 'Other Items',
        items: otherItems,
      };
    }

    return grouped;
  }, [cart_items]);

  const toggleRecipe = (recipeKey: string) => {
    const newExpanded = new Set(expandedRecipes);
    if (newExpanded.has(recipeKey)) {
      newExpanded.delete(recipeKey);
    } else {
      newExpanded.add(recipeKey);
    }
    setExpandedRecipes(newExpanded);
  };

  const handleCheckboxChange = (item: CartItem, checked: boolean) => {
    if (onItemToggle && item.id) {
      onItemToggle(item.id, checked);
    }
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
      {Object.entries(groupedItems).map(([recipeKey, { recipe_name, items }]) => {
        const isExpanded = expandedRecipes.has(recipeKey);
        const purchasedCount = items.filter((item) => item.is_purchased).length;
        const totalItems = items.length;

        return (
          <div
            key={recipeKey}
            className="rounded-lg border border-gray-200 bg-white overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Recipe Header */}
            <button
              onClick={() => toggleRecipe(recipeKey)}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
              aria-expanded={isExpanded}
              aria-controls={`recipe-${recipeKey}-items`}
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div
                  className={`
                  flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
                  ${recipeKey === 'other' ? 'bg-gray-100' : 'bg-blue-100'}
                `}
                >
                  {recipeKey === 'other' ? (
                    <Package className="h-4 w-4 text-gray-600" aria-hidden="true" />
                  ) : (
                    <span className="text-lg" aria-hidden="true">
                      🍳
                    </span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{recipe_name}</h3>
                  <p className="text-sm text-gray-500">
                    {purchasedCount} of {totalItems} items purchased
                  </p>
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
                id={`recipe-${recipeKey}-items`}
                className="border-t border-gray-200 divide-y divide-gray-100"
              >
                {items.map((item, idx) => {
                  const itemKey = item.id || `${recipeKey}-item-${idx}`;

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
                            {item.category && (
                              <>
                                <span className="text-gray-300">•</span>
                                <span className="capitalize">{item.category}</span>
                              </>
                            )}
                            {item.total_price !== undefined && (
                              <>
                                <span className="text-gray-300">•</span>
                                <span className="font-medium text-gray-700">
                                  €{item.total_price.toFixed(2)}
                                </span>
                              </>
                            )}
                          </div>
                          {/* Show other recipes if item belongs to multiple recipes */}
                          {item.recipe_sources && item.recipe_sources.length > 1 && (
                            <div className="text-xs text-blue-600 mt-1">
                              Also in:{' '}
                              {item.recipe_sources
                                .filter((r) => r.recipe_name !== recipe_name)
                                .map((r) => r.recipe_name)
                                .join(', ')}
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

export default RecipeView;
