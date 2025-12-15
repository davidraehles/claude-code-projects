/**
 * Grocery Cart Selectors Tests
 */

import { createInitialState } from '../model/state';
import {
  selectCheckedCount,
  selectIsItemChecked,
  selectAllItemsChecked,
  selectSomeItemsChecked,
  selectViewMode,
  selectIsGenerating,
  selectError,
  selectProgress,
  selectCartSummary,
} from '../model/selectors';

describe('GroceryCart Selectors', () => {
  describe('selectCheckedCount', () => {
    it('returns 0 for empty checked items', () => {
      const state = createInitialState();
      expect(selectCheckedCount(state)).toBe(0);
    });

    it('returns correct count of checked items', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.checkedItems.add('Lettuce');

      expect(selectCheckedCount(state)).toBe(2);
    });
  });

  describe('selectIsItemChecked', () => {
    it('returns true for checked item', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');

      expect(selectIsItemChecked(state, 'Tomatoes')).toBe(true);
    });

    it('returns false for unchecked item', () => {
      const state = createInitialState();

      expect(selectIsItemChecked(state, 'Tomatoes')).toBe(false);
    });
  });

  describe('selectAllItemsChecked', () => {
    it('returns true when all items are checked', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.checkedItems.add('Lettuce');

      expect(selectAllItemsChecked(state, 2)).toBe(true);
    });

    it('returns false when not all items are checked', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');

      expect(selectAllItemsChecked(state, 2)).toBe(false);
    });

    it('returns false when no items are checked', () => {
      const state = createInitialState();

      expect(selectAllItemsChecked(state, 2)).toBe(false);
    });
  });

  describe('selectSomeItemsChecked', () => {
    it('returns true when some but not all items are checked', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');

      expect(selectSomeItemsChecked(state, 3)).toBe(true);
    });

    it('returns false when all items are checked', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.checkedItems.add('Lettuce');

      expect(selectSomeItemsChecked(state, 2)).toBe(false);
    });

    it('returns false when no items are checked', () => {
      const state = createInitialState();

      expect(selectSomeItemsChecked(state, 2)).toBe(false);
    });
  });

  describe('selectViewMode', () => {
    it('returns current view mode', () => {
      const state = createInitialState();
      expect(selectViewMode(state)).toBe('category');

      state.viewMode = 'recipe';
      expect(selectViewMode(state)).toBe('recipe');
    });
  });

  describe('selectIsGenerating', () => {
    it('returns generating state', () => {
      const state = createInitialState();
      expect(selectIsGenerating(state)).toBe(false);

      state.isGenerating = true;
      expect(selectIsGenerating(state)).toBe(true);
    });
  });

  describe('selectError', () => {
    it('returns error state', () => {
      const state = createInitialState();
      expect(selectError(state)).toBeNull();

      state.error = 'Network error';
      expect(selectError(state)).toBe('Network error');
    });
  });

  describe('selectProgress', () => {
    it('calculates correct progress percentage', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');

      expect(selectProgress(state, 4)).toBe(25);
    });

    it('returns 0 for no items', () => {
      const state = createInitialState();

      expect(selectProgress(state, 0)).toBe(0);
    });

    it('returns 100 for all items checked', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.checkedItems.add('Lettuce');

      expect(selectProgress(state, 2)).toBe(100);
    });
  });

  describe('selectCartSummary', () => {
    it('returns comprehensive cart summary', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.checkedItems.add('Lettuce');
      state.viewMode = 'recipe';

      const summary = selectCartSummary(state, 5);

      expect(summary).toEqual({
        checkedCount: 2,
        totalItems: 5,
        progress: 40,
        allChecked: false,
        someChecked: true,
        viewMode: 'recipe',
      });
    });
  });
});
