/**
 * ViewToggle component for switching between Recipe and Category views.
 *
 * Provides an accessible toggle button group for switching display modes
 * in the grocery cart interface.
 */

'use client';

import React from 'react';
import { ChefHat, Grid } from 'lucide-react';

export type ViewMode = 'recipe' | 'category';

interface ViewToggleProps {
  currentView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  className?: string;
}

export const ViewToggle: React.FC<ViewToggleProps> = ({
  currentView,
  onViewChange,
  className = '',
}) => {
  return (
    <div
      className={`inline-flex rounded-lg border border-gray-300 bg-white shadow-sm ${className}`}
      role="group"
      aria-label="View mode selection"
    >
      {/* Recipe View Button */}
      <button
        type="button"
        onClick={() => onViewChange('recipe')}
        className={`
          inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-l-lg
          transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:z-10
          ${
            currentView === 'recipe'
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }
        `}
        aria-pressed={currentView === 'recipe'}
        aria-label="View by recipe"
      >
        <ChefHat className="h-4 w-4" aria-hidden="true" />
        <span>Recipe View</span>
      </button>

      {/* Category View Button */}
      <button
        type="button"
        onClick={() => onViewChange('category')}
        className={`
          inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-r-lg
          border-l transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:z-10
          ${
            currentView === 'category'
              ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
          }
        `}
        aria-pressed={currentView === 'category'}
        aria-label="View by category"
      >
        <Grid className="h-4 w-4" aria-hidden="true" />
        <span>Category View</span>
      </button>
    </div>
  );
};

export default ViewToggle;
