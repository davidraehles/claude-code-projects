/**
 * Workflow Reducer - Implements Action/Intent Layer (ARCH-004)
 *
 * Manages the cart generation workflow state machine.
 * Actions express user intent and create traceable state transitions.
 */

import type { CartPreviewData } from '@/components/knuspr/CartPreview'
import type { DeliverySlot } from '@/components/knuspr/DeliverySlotPicker'
import type { CartError } from '@/components/knuspr/CartErrorHandler'

/**
 * Workflow step type
 */
export type WorkflowStep = 
  | 'loading' 
  | 'cart-preview' 
  | 'delivery-selection' 
  | 'review' 
  | 'completed' 
  | 'error'

/**
 * State interface
 */
export interface WorkflowState {
  step: WorkflowStep
  cartData: CartPreviewData | null
  selectedDeliverySlot: DeliverySlot | null
  error: CartError | null
  isLoading: boolean
}

/**
 * Action types - Describe user intents
 */
export type WorkflowAction =
  | { type: 'WORKFLOW_STARTED'; payload: { mealPlanId: number } }
  | { type: 'CART_GENERATION_SUCCEEDED'; payload: { cartData: CartPreviewData } }
  | { type: 'CART_GENERATION_FAILED'; payload: { error: CartError } }
  | { type: 'USER_NAVIGATED_TO_STEP'; payload: { step: WorkflowStep } }
  | { type: 'USER_SELECTED_DELIVERY_SLOT'; payload: { slot: DeliverySlot } }
  | { type: 'USER_CLICKED_CHECKOUT' }
  | { type: 'USER_CLICKED_RETRY' }
  | { type: 'WORKFLOW_RESET' }

/**
 * Initial state factory
 */
export function getInitialWorkflowState(): WorkflowState {
  return {
    step: 'loading',
    cartData: null,
    selectedDeliverySlot: null,
    error: null,
    isLoading: true,
  }
}

/**
 * Pure reducer function - All state transitions are traceable
 */
export function workflowReducer(
  state: WorkflowState,
  action: WorkflowAction
): WorkflowState {
  // Log actions in development for debugging
  if (process.env.NODE_ENV === 'development') {
    console.log('[WorkflowReducer]', action.type, action)
  }

  switch (action.type) {
    case 'WORKFLOW_STARTED':
      return {
        ...state,
        step: 'loading',
        isLoading: true,
        error: null,
        cartData: null,
        selectedDeliverySlot: null,
      }

    case 'CART_GENERATION_SUCCEEDED':
      return {
        ...state,
        step: 'cart-preview',
        cartData: action.payload.cartData,
        isLoading: false,
        error: null,
      }

    case 'CART_GENERATION_FAILED':
      return {
        ...state,
        step: 'error',
        error: action.payload.error,
        isLoading: false,
      }

    case 'USER_NAVIGATED_TO_STEP':
      // Only allow navigation to accessible steps
      if (!isStepAccessible(action.payload.step, state.step)) {
        return state
      }
      return {
        ...state,
        step: action.payload.step,
      }

    case 'USER_SELECTED_DELIVERY_SLOT':
      return {
        ...state,
        selectedDeliverySlot: action.payload.slot,
        step: 'review',
      }

    case 'USER_CLICKED_CHECKOUT':
      return {
        ...state,
        step: 'completed',
      }

    case 'USER_CLICKED_RETRY':
      return {
        ...state,
        step: 'loading',
        isLoading: true,
        error: null,
        cartData: null,
        selectedDeliverySlot: null,
      }

    case 'WORKFLOW_RESET':
      return getInitialWorkflowState()

    default:
      return state
  }
}

/**
 * Workflow step navigation helpers
 */
const WORKFLOW_STEPS = ['cart-preview', 'delivery-selection', 'review'] as const

function getStepIndex(step: WorkflowStep): number {
  return WORKFLOW_STEPS.indexOf(step as typeof WORKFLOW_STEPS[number])
}

/**
 * Selector: Check if a step is complete
 */
export function selectIsStepComplete(state: WorkflowState, step: WorkflowStep): boolean {
  return getStepIndex(step) < getStepIndex(state.step)
}

/**
 * Selector: Check if a step is accessible (can be navigated to)
 */
export function selectIsStepAccessible(state: WorkflowState, step: WorkflowStep): boolean {
  return getStepIndex(step) <= getStepIndex(state.step) && 
         WORKFLOW_STEPS.includes(state.step as typeof WORKFLOW_STEPS[number])
}

/**
 * Helper for reducer logic
 */
function isStepAccessible(step: WorkflowStep, currentStep: WorkflowStep): boolean {
  return getStepIndex(step) <= getStepIndex(currentStep) && 
         WORKFLOW_STEPS.includes(currentStep as typeof WORKFLOW_STEPS[number])
}

/**
 * Selector: Check if workflow is in loading state
 */
export function selectIsLoading(state: WorkflowState): boolean {
  return state.isLoading
}

/**
 * Selector: Check if workflow has error
 */
export function selectHasError(state: WorkflowState): boolean {
  return state.error !== null
}

/**
 * Selector: Get cart item count
 */
export function selectCartItemCount(state: WorkflowState): number {
  return state.cartData?.item_count || 0
}

/**
 * Selector: Check if delivery slot is selected
 */
export function selectHasDeliverySlot(state: WorkflowState): boolean {
  return state.selectedDeliverySlot !== null
}

/**
 * Selector: Check if ready for checkout
 */
export function selectIsReadyForCheckout(state: WorkflowState): boolean {
  return state.step === 'review' && 
         state.cartData !== null && 
         !state.isLoading && 
         state.error === null
}
