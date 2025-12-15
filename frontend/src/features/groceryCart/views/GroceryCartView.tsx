/**
 * Grocery Cart View - MVI Pattern
 * 
 * Pure view component that renders based on model state
 * and dispatches intents for user actions
 */

'use client';

import { useGroceryCart, groceryCartIntents } from '../index';
import {
  selectCheckedCount,
  selectAllItemsChecked,
  selectSomeItemsChecked,
  selectViewMode,
  selectIsGenerating,
  selectError,
  selectIsItemChecked,
  selectProgress,
} from '../model/selectors';
import { CategoryView } from './CategoryView';
import { RecipeView } from './RecipeView';
import { ViewToggle } from './ViewToggle';
import { Checkbox } from '@/components/ui/Checkbox';
import { Button } from '@/components/ui/button';
import { ProgressIndicator } from '@/components/ui/progress-indicator';

/**
 * Props for grocery cart data
 */
interface GroceryCartViewProps {
  mealPlanId: number;
  items: {
    ingredient: string;
    quantity: string;
    unit: string;
    category?: string;
    recipe?: string;
  }[];
}

/**
 * Grocery Cart View Component
 * 
 * This component is a pure function of the MVI model state.
 * All user interactions dispatch intents instead of directly mutating state.
 */
export function GroceryCartView({ mealPlanId, items }: GroceryCartViewProps) {
  // Connect to MVI store
  const { state, dispatch, select } = useGroceryCart();

  // Select derived state using selectors
  const viewMode = select(selectViewMode);
  const checkedCount = select(selectCheckedCount);
  const isGenerating = select(selectIsGenerating);
  const error = select(selectError);
  const totalItems = items.length;
  const allChecked = select((s) => selectAllItemsChecked(s, totalItems));
  const someChecked = select((s) => selectSomeItemsChecked(s, totalItems));
  const progress = select((s) => selectProgress(s, totalItems));

  // Intent handlers - All user actions dispatch intents
  const handleToggleItem = (ingredient: string) => {
    dispatch(groceryCartIntents.toggleItem({ ingredient }));
  };

  const handleCheckAll = () => {
    const allIngredients = items.map((item) => item.ingredient);
    dispatch(groceryCartIntents.checkAllItems({ ingredients: allIngredients }));
  };

  const handleUncheckAll = () => {
    dispatch(groceryCartIntents.uncheckAllItems());
  };

  const handleViewModeChange = (mode: 'recipe' | 'category') => {
    dispatch(groceryCartIntents.setViewMode({ viewMode: mode }));
  };

  const handleGenerateCart = () => {
    dispatch(groceryCartIntents.generateCart({ mealPlanId }));
  };

  return (
    <div className="grocery-cart-view">
      {/* Header with progress */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Grocery List</h2>
            <p className="text-sm text-gray-600 mt-1">
              {checkedCount} of {totalItems} items checked
            </p>
          </div>
          <div className="flex gap-3">
            <ViewToggle
              currentView={viewMode}
              onViewChange={handleViewModeChange}
            />
          </div>
        </div>

        {/* Progress bar */}
        <ProgressIndicator progress={progress} />

        {/* Bulk actions */}
        <div className="flex items-center gap-4 mt-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <Checkbox
              checked={allChecked}
              indeterminate={someChecked}
              onChange={(checked) => {
                if (checked) {
                  handleCheckAll();
                } else {
                  handleUncheckAll();
                }
              }}
            />
            <span className="text-sm font-medium text-gray-700">
              {allChecked ? 'Uncheck all' : 'Check all'}
            </span>
          </label>

          {checkedCount > 0 && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleUncheckAll}
            >
              Clear ({checkedCount})
            </Button>
          )}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <span className="text-2xl mr-3">⚠️</span>
            <div>
              <h3 className="text-red-900 font-semibold mb-1">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* View content */}
      {viewMode === 'category' ? (
        <CategoryView
          items={items}
          checkedItems={state.checkedItems}
          onToggleItem={handleToggleItem}
        />
      ) : (
        <RecipeView
          items={items}
          checkedItems={state.checkedItems}
          onToggleItem={handleToggleItem}
        />
      )}

      {/* Generate cart button */}
      <div className="mt-6 flex justify-end">
        <Button
          variant="primary"
          onClick={handleGenerateCart}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <span className="animate-spin mr-2">⏳</span>
              Generating...
            </>
          ) : (
            'Generate Cart'
          )}
        </Button>
      </div>
    </div>
  );
}
