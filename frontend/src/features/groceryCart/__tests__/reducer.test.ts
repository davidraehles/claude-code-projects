/**
 * Grocery Cart Reducer Tests
 */

import { groceryCartReducer } from '../model/reducer';
import { createInitialState } from '../model/state';
import { groceryCartIntents } from '../intents/creators';

describe('GroceryCart Reducer', () => {
  describe('USER_TOGGLED_ITEM', () => {
    it('adds item to checked items', () => {
      const state = createInitialState();
      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.toggleItem({ ingredient: 'Tomatoes' })
      );

      expect(nextState.checkedItems.has('Tomatoes')).toBe(true);
    });

    it('removes item from checked items if already checked', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.toggleItem({ ingredient: 'Tomatoes' })
      );

      expect(nextState.checkedItems.has('Tomatoes')).toBe(false);
    });
  });

  describe('USER_CHECKED_ALL_ITEMS', () => {
    it('checks all provided items', () => {
      const state = createInitialState();
      const ingredients = ['Tomatoes', 'Lettuce', 'Onions'];

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.checkAllItems({ ingredients })
      );

      expect(nextState.checkedItems.size).toBe(3);
      ingredients.forEach((item) => {
        expect(nextState.checkedItems.has(item)).toBe(true);
      });
    });
  });

  describe('USER_UNCHECKED_ALL_ITEMS', () => {
    it('clears all checked items', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.checkedItems.add('Lettuce');

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.uncheckAllItems()
      );

      expect(nextState.checkedItems.size).toBe(0);
    });
  });

  describe('USER_SET_VIEW_MODE', () => {
    it('changes view mode to recipe', () => {
      const state = createInitialState();

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.setViewMode({ viewMode: 'recipe' })
      );

      expect(nextState.viewMode).toBe('recipe');
    });

    it('changes view mode to category', () => {
      const state = createInitialState();
      state.viewMode = 'recipe';

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.setViewMode({ viewMode: 'category' })
      );

      expect(nextState.viewMode).toBe('category');
    });
  });

  describe('USER_GENERATE_CART', () => {
    it('sets isGenerating to true', () => {
      const state = createInitialState();

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.generateCart({ mealPlanId: 1 })
      );

      expect(nextState.isGenerating).toBe(true);
      expect(nextState.error).toBeNull();
    });
  });

  describe('CART_GENERATED', () => {
    it('sets generated cart and clears loading state', () => {
      const state = createInitialState();
      state.isGenerating = true;

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.cartGenerated({
          cartId: 123,
          items: ['Tomatoes', 'Lettuce'],
        })
      );

      expect(nextState.isGenerating).toBe(false);
      expect(nextState.error).toBeNull();
      expect(nextState.generatedCart).toEqual({
        cartId: 123,
        items: ['Tomatoes', 'Lettuce'],
      });
    });
  });

  describe('CART_GENERATION_FAILED', () => {
    it('sets error and clears loading state', () => {
      const state = createInitialState();
      state.isGenerating = true;

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.cartGenerationFailed({
          error: 'Network error',
        })
      );

      expect(nextState.isGenerating).toBe(false);
      expect(nextState.error).toBe('Network error');
      expect(nextState.generatedCart).toBeNull();
    });
  });

  describe('CART_RESET', () => {
    it('resets to initial state', () => {
      const state = createInitialState();
      state.checkedItems.add('Tomatoes');
      state.viewMode = 'recipe';
      state.error = 'Some error';

      const nextState = groceryCartReducer(
        state,
        groceryCartIntents.resetCart()
      );

      expect(nextState).toEqual(createInitialState());
    });
  });
});
