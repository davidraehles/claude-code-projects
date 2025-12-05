# View Components for Grocery Cart Display

This document describes the view components for displaying grocery cart items in different organizational modes.

## Components Overview

### 1. ViewToggle Component

**File**: `/frontend/src/components/knuspr/ViewToggle.tsx`

**Purpose**: Toggle button group for switching between Recipe and Category view modes.

**Props**:
```typescript
interface ViewToggleProps {
  currentView: 'recipe' | 'category';
  onViewChange: (view: 'recipe' | 'category') => void;
  className?: string;
}
```

**Features**:
- Clean toggle button group UI
- Active view highlighted with blue background
- Inactive view with gray background
- Icons for visual identification (ChefHat for recipe, Grid for category)
- Fully accessible with ARIA labels and keyboard navigation
- Focus states with ring for keyboard users
- Responsive design with Tailwind CSS

**Usage**:
```tsx
import ViewToggle from '@/components/knuspr/ViewToggle';

<ViewToggle
  currentView={viewMode}
  onViewChange={(mode) => setViewMode(mode)}
/>
```

---

### 2. RecipeView Component

**File**: `/frontend/src/components/knuspr/RecipeView.tsx`

**Purpose**: Display cart items grouped by their source recipes.

**Props**:
```typescript
interface RecipeViewProps {
  cart_items: CartItem[];
  onItemToggle?: (itemId: number, purchased: boolean) => void;
  className?: string;
}

interface CartItem {
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

interface RecipeSource {
  recipe_id: number;
  recipe_name: string;
}
```

**Features**:
- Groups items by recipe using `recipe_sources` field
- Collapsible/expandable recipe sections (accordion pattern)
- Items with multiple recipes appear in each relevant section
- Items without recipes go in "Other Items" section
- Checkboxes for marking items as purchased
- Shows quantity, unit, price per item
- Indicates when all items in a recipe are purchased (green checkmark)
- Cross-references when item belongs to multiple recipes
- Empty state with icon and message
- Fully accessible with ARIA labels
- Responsive design with hover states

**Usage**:
```tsx
import RecipeView from '@/components/knuspr/RecipeView';

<RecipeView
  cart_items={items}
  onItemToggle={(id, purchased) => handleToggle(id, purchased)}
/>
```

---

### 3. CategoryView Component

**File**: `/frontend/src/components/knuspr/CategoryView.tsx`

**Purpose**: Display cart items grouped by shopping categories in logical order.

**Props**:
```typescript
interface CategoryViewProps {
  cart_items: CartItem[];
  onItemToggle?: (itemId: number, purchased: boolean) => void;
  className?: string;
}
```

**Features**:
- Groups items by category (produce, dairy, meat, etc.)
- Smart sorting in logical shopping order:
  - Produce (first - typically at store entrance)
  - Dairy, Meat, Fish, Bakery
  - Grains, Pantry, Canned Goods
  - Oils & Vinegar, Spices
  - Beverages, Snacks
  - Frozen (last - to prevent thawing)
- Default "Uncategorized" for items without category
- Category icons for visual identification
- Collapsible/expandable category sections
- Checkboxes for marking items as purchased
- Shows quantity, unit, price per item and per unit
- Displays recipe sources as tags
- Category-level price totals
- Indicates when all items in category are purchased
- Empty state with icon and message
- Fully accessible with ARIA labels
- Responsive design with hover states

**Category Order**:
```typescript
[
  'produce', 'dairy', 'meat', 'fish', 'bakery',
  'grains', 'pantry', 'canned_goods', 'oils_vinegar',
  'spices', 'beverages', 'snacks', 'frozen', 'uncategorized'
]
```

**Usage**:
```tsx
import CategoryView from '@/components/knuspr/CategoryView';

<CategoryView
  cart_items={items}
  onItemToggle={(id, purchased) => handleToggle(id, purchased)}
/>
```

---

## Complete Example

See `GroceryListView.example.tsx` for a complete integration example.

```tsx
'use client';

import React, { useState } from 'react';
import ViewToggle, { ViewMode } from './ViewToggle';
import RecipeView from './RecipeView';
import CategoryView from './CategoryView';

export const GroceryListView = ({ cartItems, onItemToggle }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('recipe');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Grocery List</h2>
        <ViewToggle currentView={viewMode} onViewChange={setViewMode} />
      </div>

      {viewMode === 'recipe' ? (
        <RecipeView cart_items={cartItems} onItemToggle={onItemToggle} />
      ) : (
        <CategoryView cart_items={cartItems} onItemToggle={onItemToggle} />
      )}
    </div>
  );
};
```

---

## Accessibility Features

All components follow WCAG 2.1 AA standards:

1. **Keyboard Navigation**
   - All interactive elements are keyboard accessible
   - Focus indicators with ring styling
   - Logical tab order

2. **ARIA Labels**
   - Buttons have `aria-label` for screen readers
   - Toggle buttons use `aria-pressed` state
   - Expandable sections use `aria-expanded` and `aria-controls`
   - Checkboxes have descriptive labels

3. **Visual Indicators**
   - Clear active/inactive states
   - Color is not the only indicator (icons used)
   - High contrast ratios for text

4. **Screen Reader Support**
   - Semantic HTML elements
   - Hidden decorative icons with `aria-hidden`
   - Status announcements for purchased items

---

## Styling Approach

All components use Tailwind CSS with consistent patterns:

- **Colors**: Blue for primary actions, Gray for neutral, Green for success
- **Spacing**: Consistent padding and gaps (p-4, gap-3, space-y-3)
- **Borders**: Rounded corners (rounded-lg) with subtle borders
- **Shadows**: Soft shadows that increase on hover
- **Transitions**: Smooth color and shadow transitions (duration-200)
- **Hover States**: Subtle background color changes
- **Focus States**: Blue ring for keyboard focus

---

## Type Safety

All components are fully typed with TypeScript:

- Explicit prop interfaces
- Exported types for reuse
- Optional props with defaults
- Proper event handler typing

---

## Performance Considerations

1. **useMemo** for expensive computations (grouping items)
2. **useState** for local UI state (expanded sections)
3. Keys use stable identifiers (item.id) or fallback indices
4. Conditional rendering to avoid unnecessary DOM

---

## Testing Recommendations

1. **Unit Tests**
   - Component rendering with different props
   - Toggle functionality
   - Item grouping logic
   - Checkbox state management

2. **Integration Tests**
   - View switching behavior
   - Item purchase toggling
   - Empty state display

3. **Accessibility Tests**
   - Keyboard navigation
   - Screen reader announcements
   - Focus management

4. **Visual Tests**
   - Responsive design at different breakpoints
   - Hover and focus states
   - Loading and empty states

---

## Future Enhancements

Potential improvements for future iterations:

1. **Sorting Options**: Allow users to sort items within sections
2. **Search/Filter**: Add search bar to filter items
3. **Bulk Actions**: Select multiple items for bulk operations
4. **Drag & Drop**: Reorder items or move between categories
5. **Animations**: Smooth transitions when switching views
6. **Offline Support**: Cache state for offline use
7. **Print View**: Optimized layout for printing shopping list
8. **Share**: Export or share list with others
