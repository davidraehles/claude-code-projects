/**
 * Example usage of ViewToggle, RecipeView, and CategoryView components.
 *
 * This demonstrates how to integrate the view components into a grocery
 * cart or list interface with view mode switching.
 */

'use client';

import React, { useState } from 'react';
import ViewToggle, { ViewMode } from './ViewToggle';
import RecipeView, { CartItem } from './RecipeView';
import CategoryView from './CategoryView';

interface GroceryListViewExampleProps {
  cartItems: CartItem[];
  onItemToggle?: (itemId: number, purchased: boolean) => void;
}

export const GroceryListViewExample: React.FC<GroceryListViewExampleProps> = ({
  cartItems,
  onItemToggle,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('recipe');

  return (
    <div className="space-y-6">
      {/* Header with View Toggle */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Grocery List</h2>
          <p className="text-sm text-gray-600 mt-1">
            {cartItems.length} items • Switch views to organize your shopping
          </p>
        </div>
        <ViewToggle currentView={viewMode} onViewChange={setViewMode} />
      </div>

      {/* Dynamic View Content */}
      <div className="mt-6">
        {viewMode === 'recipe' ? (
          <RecipeView
            cart_items={cartItems}
            onItemToggle={onItemToggle}
            className="animate-fadeIn"
          />
        ) : (
          <CategoryView
            cart_items={cartItems}
            onItemToggle={onItemToggle}
            className="animate-fadeIn"
          />
        )}
      </div>

      {/* Summary Stats */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-gray-900">{cartItems.length}</p>
            <p className="text-sm text-gray-600">Total Items</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">
              {cartItems.filter((item) => item.is_purchased).length}
            </p>
            <p className="text-sm text-gray-600">Purchased</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-blue-600">
              {cartItems.filter((item) => !item.is_purchased).length}
            </p>
            <p className="text-sm text-gray-600">Remaining</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GroceryListViewExample;
