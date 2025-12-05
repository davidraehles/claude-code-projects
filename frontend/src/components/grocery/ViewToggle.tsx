/**
 * ViewToggle - Toggle between Recipe and Category views
 */

interface ViewToggleProps {
  currentView: 'recipe' | 'category'
  onViewChange: (view: 'recipe' | 'category') => void
}

export function ViewToggle({ currentView, onViewChange }: ViewToggleProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-1 inline-flex" role="tablist">
      <button
        role="tab"
        aria-selected={currentView === 'category'}
        aria-controls="category-view"
        onClick={() => onViewChange('category')}
        className={`
          px-4 py-2 rounded-md font-medium text-sm transition-all duration-200
          ${
            currentView === 'category'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }
        `}
      >
        Category View
      </button>
      <button
        role="tab"
        aria-selected={currentView === 'recipe'}
        aria-controls="recipe-view"
        onClick={() => onViewChange('recipe')}
        className={`
          px-4 py-2 rounded-md font-medium text-sm transition-all duration-200
          ${
            currentView === 'recipe'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }
        `}
      >
        Recipe View
      </button>
    </div>
  )
}
