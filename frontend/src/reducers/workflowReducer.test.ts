/**
 * Tests for workflowReducer
 */

import type { CartPreviewData } from '@/components/knuspr/CartPreview'
import type { DeliverySlot } from '@/components/knuspr/DeliverySlotPicker'
import {
  workflowReducer,
  getInitialWorkflowState,
  selectIsStepComplete,
  selectIsLoading,
  selectHasError,
  selectCartItemCount,
  selectHasDeliverySlot,
  selectIsReadyForCheckout,
  type WorkflowState,
  type WorkflowAction,
} from './workflowReducer'

// Mock data factories for type-safe test data
function createMockCartData(overrides?: Partial<CartPreviewData>): CartPreviewData {
  return {
    cart_id: 'test-cart-123',
    knuspr_url: 'https://knuspr.de/cart',
    total_price: 50.0,
    item_count: 10,
    delivery_slot: null,
    items_by_section: {},
    unavailable_items: [],
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

function createMockDeliverySlot(overrides?: Partial<DeliverySlot>): DeliverySlot {
  return {
    slot_id: 'slot-123',
    date: '2024-12-20',
    time_range: '10:00-12:00',
    price: 5.99,
    available: true,
    ...overrides,
  }
}

describe('workflowReducer', () => {
  describe('getInitialWorkflowState', () => {
    it('should return initial state with loading step', () => {
      const state = getInitialWorkflowState()
      expect(state.step).toBe('loading')
      expect(state.isLoading).toBe(true)
      expect(state.cartData).toBeNull()
      expect(state.selectedDeliverySlot).toBeNull()
      expect(state.error).toBeNull()
    })
  })

  describe('WORKFLOW_STARTED action', () => {
    it('should reset state and set to loading', () => {
      const initialState: WorkflowState = {
        step: 'error',
        cartData: null,
        selectedDeliverySlot: null,
        error: { code: 'TEST_ERROR', message: 'Test', details: '', severity: 'error' },
        isLoading: false,
      }

      const action: WorkflowAction = {
        type: 'WORKFLOW_STARTED',
        payload: { mealPlanId: 123 },
      }

      const newState = workflowReducer(initialState, action)

      expect(newState.step).toBe('loading')
      expect(newState.isLoading).toBe(true)
      expect(newState.error).toBeNull()
      expect(newState.cartData).toBeNull()
    })
  })

  describe('CART_GENERATION_SUCCEEDED action', () => {
    it('should set cart data and move to cart-preview step', () => {
      const initialState = getInitialWorkflowState()
      const mockCartData = createMockCartData()

      const action: WorkflowAction = {
        type: 'CART_GENERATION_SUCCEEDED',
        payload: { cartData: mockCartData },
      }

      const newState = workflowReducer(initialState, action)

      expect(newState.step).toBe('cart-preview')
      expect(newState.cartData).toEqual(mockCartData)
      expect(newState.isLoading).toBe(false)
      expect(newState.error).toBeNull()
    })
  })

  describe('CART_GENERATION_FAILED action', () => {
    it('should set error and move to error step', () => {
      const initialState = getInitialWorkflowState()
      const mockError = {
        code: 'NETWORK_ERROR',
        message: 'Failed to connect',
        details: 'Network timeout',
        severity: 'error' as const,
      }

      const action: WorkflowAction = {
        type: 'CART_GENERATION_FAILED',
        payload: { error: mockError },
      }

      const newState = workflowReducer(initialState, action)

      expect(newState.step).toBe('error')
      expect(newState.error).toEqual(mockError)
      expect(newState.isLoading).toBe(false)
    })
  })

  describe('USER_SELECTED_DELIVERY_SLOT action', () => {
    it('should save delivery slot and move to review step', () => {
      const initialState: WorkflowState = {
        step: 'delivery-selection',
        cartData: createMockCartData({ item_count: 5 }),
        selectedDeliverySlot: null,
        error: null,
        isLoading: false,
      }

      const mockSlot = createMockDeliverySlot()

      const action: WorkflowAction = {
        type: 'USER_SELECTED_DELIVERY_SLOT',
        payload: { slot: mockSlot },
      }

      const newState = workflowReducer(initialState, action)

      expect(newState.step).toBe('review')
      expect(newState.selectedDeliverySlot).toEqual(mockSlot)
    })
  })

  describe('USER_CLICKED_CHECKOUT action', () => {
    it('should move to completed step', () => {
      const initialState: WorkflowState = {
        step: 'review',
        cartData: createMockCartData({ item_count: 5 }),
        selectedDeliverySlot: createMockDeliverySlot(),
        error: null,
        isLoading: false,
      }

      const action: WorkflowAction = {
        type: 'USER_CLICKED_CHECKOUT',
      }

      const newState = workflowReducer(initialState, action)

      expect(newState.step).toBe('completed')
    })
  })

  describe('USER_CLICKED_RETRY action', () => {
    it('should reset to loading state', () => {
      const initialState: WorkflowState = {
        step: 'error',
        cartData: null,
        selectedDeliverySlot: null,
        error: { code: 'ERROR', message: 'Test', details: '', severity: 'error' },
        isLoading: false,
      }

      const action: WorkflowAction = {
        type: 'USER_CLICKED_RETRY',
      }

      const newState = workflowReducer(initialState, action)

      expect(newState.step).toBe('loading')
      expect(newState.isLoading).toBe(true)
      expect(newState.error).toBeNull()
      expect(newState.cartData).toBeNull()
    })
  })

  describe('WORKFLOW_RESET action', () => {
    it('should reset to initial state', () => {
      const initialState: WorkflowState = {
        step: 'review',
        cartData: createMockCartData({ item_count: 5 }),
        selectedDeliverySlot: createMockDeliverySlot(),
        error: null,
        isLoading: false,
      }

      const action: WorkflowAction = {
        type: 'WORKFLOW_RESET',
      }

      const newState = workflowReducer(initialState, action)

      expect(newState).toEqual(getInitialWorkflowState())
    })
  })

  describe('Selectors', () => {
    describe('selectIsStepComplete', () => {
      it('should return true for completed steps', () => {
        const state: WorkflowState = {
          step: 'review',
          cartData: null,
          selectedDeliverySlot: null,
          error: null,
          isLoading: false,
        }

        expect(selectIsStepComplete(state, 'cart-preview')).toBe(true)
        expect(selectIsStepComplete(state, 'delivery-selection')).toBe(true)
        expect(selectIsStepComplete(state, 'review')).toBe(false)
      })
    })

    describe('selectIsLoading', () => {
      it('should return true when isLoading is true', () => {
        const state = getInitialWorkflowState()
        expect(selectIsLoading(state)).toBe(true)
      })

      it('should return false when isLoading is false', () => {
        const state: WorkflowState = {
          ...getInitialWorkflowState(),
          isLoading: false,
        }
        expect(selectIsLoading(state)).toBe(false)
      })
    })

    describe('selectHasError', () => {
      it('should return true when error exists', () => {
        const state: WorkflowState = {
          step: 'error',
          cartData: null,
          selectedDeliverySlot: null,
          error: { code: 'ERROR', message: 'Test', details: '', severity: 'error' },
          isLoading: false,
        }
        expect(selectHasError(state)).toBe(true)
      })

      it('should return false when no error', () => {
        const state = getInitialWorkflowState()
        expect(selectHasError(state)).toBe(false)
      })
    })

    describe('selectCartItemCount', () => {
      it('should return cart item count', () => {
        const state: WorkflowState = {
          step: 'cart-preview',
          cartData: createMockCartData({ item_count: 15 }),
          selectedDeliverySlot: null,
          error: null,
          isLoading: false,
        }
        expect(selectCartItemCount(state)).toBe(15)
      })

      it('should return 0 when no cart data', () => {
        const state = getInitialWorkflowState()
        expect(selectCartItemCount(state)).toBe(0)
      })
    })

    describe('selectHasDeliverySlot', () => {
      it('should return true when delivery slot selected', () => {
        const state: WorkflowState = {
          step: 'review',
          cartData: null,
          selectedDeliverySlot: createMockDeliverySlot(),
          error: null,
          isLoading: false,
        }
        expect(selectHasDeliverySlot(state)).toBe(true)
      })

      it('should return false when no delivery slot', () => {
        const state = getInitialWorkflowState()
        expect(selectHasDeliverySlot(state)).toBe(false)
      })
    })

    describe('selectIsReadyForCheckout', () => {
      it('should return true when all conditions met', () => {
        const state: WorkflowState = {
          step: 'review',
          cartData: createMockCartData({ item_count: 5 }),
          selectedDeliverySlot: createMockDeliverySlot(),
          error: null,
          isLoading: false,
        }
        expect(selectIsReadyForCheckout(state)).toBe(true)
      })

      it('should return false when step is not review', () => {
        const state: WorkflowState = {
          step: 'cart-preview',
          cartData: createMockCartData({ item_count: 5 }),
          selectedDeliverySlot: createMockDeliverySlot(),
          error: null,
          isLoading: false,
        }
        expect(selectIsReadyForCheckout(state)).toBe(false)
      })

      it('should return false when loading', () => {
        const state: WorkflowState = {
          step: 'review',
          cartData: createMockCartData({ item_count: 5 }),
          selectedDeliverySlot: createMockDeliverySlot(),
          error: null,
          isLoading: true,
        }
        expect(selectIsReadyForCheckout(state)).toBe(false)
      })

      it('should return false when has error', () => {
        const state: WorkflowState = {
          step: 'review',
          cartData: createMockCartData({ item_count: 5 }),
          selectedDeliverySlot: createMockDeliverySlot(),
          error: { code: 'ERROR', message: 'Test', details: '', severity: 'error' },
          isLoading: false,
        }
        expect(selectIsReadyForCheckout(state)).toBe(false)
      })

      it('should return false when no delivery slot selected', () => {
        const state: WorkflowState = {
          step: 'review',
          cartData: createMockCartData({ item_count: 5 }),
          selectedDeliverySlot: null,
          error: null,
          isLoading: false,
        }
        expect(selectIsReadyForCheckout(state)).toBe(false)
      })
    })
  })
})
