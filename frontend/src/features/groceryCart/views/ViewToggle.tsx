/**
 * View Toggle - Pure component for switching between views
 */

'use client';

import { Button } from '@/components/ui/button';

interface ViewToggleProps {
  currentView: 'recipe' | 'category';
  onViewChange: (view: 'recipe' | 'category') => void;
}

export function ViewToggle({ currentView, onViewChange }: ViewToggleProps) {
  return (
    <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
      <button
        onClick={() => onViewChange('category')}
        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
          currentView === 'category'
            ? 'bg-blue-600 text-white'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
      >
        By Category
      </button>
      <button
        onClick={() => onViewChange('recipe')}
        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
          currentView === 'recipe'
            ? 'bg-blue-600 text-white'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
      >
        By Recipe
      </button>
    </div>
  );
}
