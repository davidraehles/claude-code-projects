'use client';

/**
 * Workflow page - Cart generation workflow with MVI pattern (ARCH-004).
 * Refactored to use reducer for state machine management.
 */

import React, { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import CartPreview from '@/components/knuspr/CartPreview';
import DeliverySlotPicker, { DeliverySlot } from '@/components/knuspr/DeliverySlotPicker';
import MissingItemsSuggestions from '@/components/knuspr/MissingItemsSuggestions';
import CartErrorHandler from '@/components/knuspr/CartErrorHandler';
import { api } from '@/lib/api';
import { useReducerWithDevTools } from '@/hooks/useReducerWithDevTools';
import {
  workflowReducer,
  getInitialWorkflowState,
  selectIsStepComplete,
  selectIsStepAccessible,
  selectIsLoading,
  selectHasError,
  selectCartItemCount,
  selectHasDeliverySlot,
  selectIsReadyForCheckout,
  type WorkflowStep,
} from '@/reducers/workflowReducer';

function WorkflowPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mealPlanId = searchParams.get('meal_plan_id');

  // Workflow state with reducer and DevTools (ARCH-004 + ARCH-011)
  const [state, dispatch] = useReducerWithDevTools(
    workflowReducer,
    getInitialWorkflowState(),
    'WorkflowStateMachine'
  );

  // Validate and parse meal plan ID
  const validateMealPlanId = (id: string | null): number | null => {
    if (!id) return null;
    const parsed = parseInt(id, 10);
    if (isNaN(parsed) || parsed <= 0) return null;
    return parsed;
  };

  // Cart generation mutation
  const generateCartMutation = useMutation({
    mutationFn: async (id: number) => {
      const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
      if (!token) throw new Error('Not authenticated');

      return api.createCartFromMealPlanWorkflow(
        id,
        {
          preferred_dates: [],
          preferred_time_slot: 'afternoon',
          budget_optimization: false,
        },
        token
      );
    },
    onSuccess: (data) => {
      if (data.result) {
        dispatch({
          type: 'CART_GENERATION_SUCCEEDED',
          payload: { cartData: data.result as any },
        });
      } else {
        throw new Error('Invalid response format');
      }
    },
    onError: (err) => {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      let errorCode = 'GENERIC_ERROR';
      if (errorMessage.includes('Not authenticated')) {
        errorCode = 'MISSING_CREDENTIALS';
      } else if (errorMessage.includes('timeout')) {
        errorCode = 'KNUSPR_CONNECTION_TIMEOUT';
      } else if (errorMessage.includes('not found')) {
        errorCode = 'PRODUCT_NOT_FOUND';
      }

      dispatch({
        type: 'CART_GENERATION_FAILED',
        payload: {
          error: {
            code: errorCode,
            message: 'Failed to generate cart',
            details: errorMessage,
            severity: 'error',
          },
        },
      });
    },
  });

  // Fetch cart data on component mount
  useEffect(() => {
    const validatedMealPlanId = validateMealPlanId(mealPlanId);

    if (!validatedMealPlanId) {
      dispatch({
        type: 'CART_GENERATION_FAILED',
        payload: {
          error: {
            code: 'MISSING_MEAL_PLAN',
            message: 'No meal plan specified',
            details: 'Please select a valid meal plan to create a cart.',
            severity: 'error',
            suggestions: ['Go back and select a meal plan', 'Create a new meal plan first'],
          },
        },
      });
      return;
    }

    dispatch({ type: 'WORKFLOW_STARTED', payload: { mealPlanId: validatedMealPlanId } });
    generateCartMutation.mutate(validatedMealPlanId);
  }, [mealPlanId]);

  // Event handlers
  const handleRetry = () => {
    dispatch({ type: 'USER_CLICKED_RETRY' });
    const validatedMealPlanId = validateMealPlanId(mealPlanId);
    if (validatedMealPlanId) {
      generateCartMutation.mutate(validatedMealPlanId);
    }
  };

  const handleDeliverySlotSelect = (slot: DeliverySlot) => {
    dispatch({ type: 'USER_SELECTED_DELIVERY_SLOT', payload: { slot } });
  };

  const handleCheckout = () => {
    if (state.cartData) {
      dispatch({ type: 'USER_CLICKED_CHECKOUT' });
      window.open(state.cartData.knuspr_url, '_blank');
    }
  };

  const handleNavigateToStep = (step: WorkflowStep) => {
    if (selectIsStepAccessible(state, step)) {
      dispatch({ type: 'USER_NAVIGATED_TO_STEP', payload: { step } });
    }
  };

  // Render based on workflow step
  if (selectIsLoading(state) && state.step === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Generating Your Cart</h2>
              <p className="text-gray-600">
                We&apos;re converting your meal plan into a Knuspr shopping cart...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (state.step === 'error') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-2xl">
          <Link
            href="/meal-plans"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Meal Plans
          </Link>

          <CartErrorHandler
            error={state.error}
            onRetry={handleRetry}
            onContactSupport={() => window.open('/support', '_blank')}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/meal-plans"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Meal Plans
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Complete Your Order</h1>
              <p className="text-gray-600 mt-2">
                Review your cart and select a delivery slot
              </p>
            </div>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8 flex items-center justify-between">
          {[
            { name: 'Cart Review', step: 'cart-preview' as const },
            { name: 'Delivery', step: 'delivery-selection' as const },
            { name: 'Complete', step: 'review' as const },
          ].map((item, idx, arr) => {
            const isCurrentStep = state.step === item.step;
            const isComplete = selectIsStepComplete(state, item.step);
            const isAccessible = selectIsStepAccessible(state, item.step);

            return (
              <React.Fragment key={item.step}>
                <button
                  onClick={() => handleNavigateToStep(item.step)}
                  disabled={!isAccessible}
                  className={`flex flex-col items-center gap-2 flex-1 pb-6 relative text-sm font-medium ${
                    isCurrentStep ? 'text-blue-600' : isComplete ? 'text-green-600' : 'text-gray-400'
                  } ${isAccessible ? 'cursor-pointer' : 'cursor-not-allowed'}`}
                >
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full border-2 font-bold ${
                      isCurrentStep
                        ? 'border-blue-600 bg-blue-50'
                        : isComplete
                          ? 'border-green-600 bg-green-50 text-green-600'
                          : 'border-gray-300 bg-gray-100'
                    }`}
                  >
                    {isComplete ? '✓' : idx + 1}
                  </div>
                  {item.name}
                </button>
                {idx < arr.length - 1 && (
                  <div
                    className={`h-0.5 w-8 mb-8 ${
                      selectIsStepComplete(state, item.step) ? 'bg-green-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {/* Cart Preview */}
          {(state.step === 'cart-preview' || state.step === 'delivery-selection' || state.step === 'review') &&
            state.cartData && (
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <CartPreview
                  data={state.cartData}
                  onCheckout={() => handleNavigateToStep('delivery-selection')}
                  isLoading={false}
                />
              </div>
            )}

          {/* Missing Items */}
          {(state.step === 'delivery-selection' || state.step === 'review') &&
            (state.cartData?.unavailable_items?.length ?? 0) > 0 && (
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <MissingItemsSuggestions
                  unavailableItems={state.cartData?.unavailable_items || []}
                  cartSubtotal={state.cartData?.total_price || 0}
                />
              </div>
            )}

          {/* Delivery Slot Selection */}
          {(state.step === 'delivery-selection' || state.step === 'review') && (
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <DeliverySlotPicker
                slots={state.cartData?.delivery_slot ? [state.cartData.delivery_slot] : []}
                selected={state.selectedDeliverySlot?.slot_id}
                onSelect={handleDeliverySlotSelect}
                timePreference="afternoon"
              />
            </div>
          )}

          {/* Review & Checkout */}
          {state.step === 'review' && (
            <div className="rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 p-6 space-y-4">
              <h3 className="text-lg font-semibold text-green-900">Ready to Checkout?</h3>
              <p className="text-green-800">
                Your cart is ready with{' '}
                <strong className="font-semibold">{selectCartItemCount(state)}</strong> items.
                {selectHasDeliverySlot(state) && state.selectedDeliverySlot && (
                  <>
                    {' '}
                    Delivery scheduled for{' '}
                    <strong className="font-semibold">
                      {new Date(state.selectedDeliverySlot.date).toLocaleDateString()}
                    </strong>
                    .
                  </>
                )}
              </p>
              <button
                onClick={handleCheckout}
                disabled={!selectIsReadyForCheckout(state)}
                className="w-full rounded-lg bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 transition-colors"
              >
                Complete Order on Knuspr →
              </button>
              <p className="text-xs text-green-700 text-center">
                You&apos;ll be redirected to Knuspr to finalize your order
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            Questions?{' '}
            <a href="/help" className="text-blue-600 hover:text-blue-700 font-medium">
              View Help
            </a>{' '}
            or{' '}
            <a href="/support" className="text-blue-600 hover:text-blue-700 font-medium">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function WorkflowPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Loading Workflow...</h2>
            </div>
          </div>
        </div>
      </div>
    }>
      <WorkflowPageContent />
    </Suspense>
  );
}
