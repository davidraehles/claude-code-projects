'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { CartPreviewData } from '@/components/knuspr/CartPreview';
import { DeliverySlot } from '@/components/knuspr/DeliverySlotPicker';
import { CartError } from '@/components/knuspr/CartErrorHandler';

// Lazy load components for better initial page load
const CartPreview = dynamic(
  () => import('@/components/knuspr/CartPreview').then((mod) => mod.default),
  {
    loading: () => (
      <div className="rounded-lg bg-white p-6 shadow-sm animate-pulse">
        <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    ),
    ssr: true,
  }
);

const DeliverySlotPicker = dynamic(
  () => import('@/components/knuspr/DeliverySlotPicker').then((mod) => mod.default),
  {
    loading: () => (
      <div className="rounded-lg bg-white p-6 shadow-sm animate-pulse">
        <div className="h-6 bg-gray-200 rounded mb-4 w-1/2"></div>
        <div className="space-y-2">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    ),
    ssr: true,
  }
);

const MissingItemsSuggestions = dynamic(
  () => import('@/components/knuspr/MissingItemsSuggestions').then((mod) => mod.default),
  {
    loading: () => (
      <div className="rounded-lg bg-white p-6 shadow-sm animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3"></div>
      </div>
    ),
    ssr: false, // Not critical for initial load
  }
);

const CartErrorHandler = dynamic(
  () => import('@/components/knuspr/CartErrorHandler').then((mod) => mod.default),
  {
    loading: () => null,
    ssr: true,
  }
);

type WorkflowStep = 'loading' | 'cart-preview' | 'delivery-selection' | 'review' | 'completed' | 'error';

interface WorkflowState {
  step: WorkflowStep;
  cartData: CartPreviewData | null;
  selectedDeliverySlot: DeliverySlot | null;
  error: CartError | null;
  isLoading: boolean;
}

export default function OptimizedWorkflowPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mealPlanId = searchParams.get('meal_plan_id');

  const [state, setState] = useState<WorkflowState>({
    step: 'loading',
    cartData: null,
    selectedDeliverySlot: null,
    error: null,
    isLoading: true,
  });

  // Memoize workflow steps to prevent re-renders
  const workflowSteps = useMemo(
    () => [
      { name: 'Cart Review', step: 'cart-preview' as const },
      { name: 'Delivery', step: 'delivery-selection' as const },
      { name: 'Complete', step: 'review' as const },
    ],
    []
  );

  // Memoize callbacks to prevent unnecessary re-renders
  const handleRetry = useCallback(() => {
    setState((prev) => ({ ...prev, step: 'loading', isLoading: true, error: null }));
    window.location.reload();
  }, []);

  const handleDeliverySlotSelect = useCallback((slot: DeliverySlot) => {
    setState((prev) => ({
      ...prev,
      selectedDeliverySlot: slot,
      step: 'review',
    }));
  }, []);

  const handleCheckout = useCallback(() => {
    setState((prev) => {
      if (prev.cartData) {
        window.open(prev.cartData.knuspr_url, '_blank');
      }
      return prev;
    });
  }, []);

  // Fetch cart data on component mount
  useEffect(() => {
    if (!mealPlanId) {
      setState((prev) => ({
        ...prev,
        step: 'error',
        error: {
          code: 'MISSING_MEAL_PLAN',
          message: 'No meal plan specified',
          details: 'Please select a meal plan to create a cart.',
          severity: 'error',
          suggestions: ['Go back and select a meal plan', 'Create a new meal plan first'],
        },
        isLoading: false,
      }));
      return;
    }

    const generateCart = async () => {
      try {
        const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');

        if (!token) {
          throw new Error('Not authenticated');
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/workflows/meal-plan-with-groceries`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              meal_plan_id: parseInt(mealPlanId, 10),
              delivery_preferences: {
                preferred_dates: [],
                preferred_time_slot: 'afternoon',
                budget_optimization: false,
              },
            }),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to generate cart');
        }

        setState((prev) => ({
          ...prev,
          step: 'cart-preview',
          cartData: data.result,
          isLoading: false,
        }));
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';

        let errorCode = 'GENERIC_ERROR';
        if (errorMessage.includes('Not authenticated')) {
          errorCode = 'MISSING_CREDENTIALS';
        } else if (errorMessage.includes('timeout')) {
          errorCode = 'KNUSPR_CONNECTION_TIMEOUT';
        } else if (errorMessage.includes('not found')) {
          errorCode = 'PRODUCT_NOT_FOUND';
        }

        setState((prev) => ({
          ...prev,
          step: 'error',
          error: {
            code: errorCode,
            message: 'Failed to generate cart',
            details: errorMessage,
            severity: 'error',
          },
          isLoading: false,
        }));
      }
    };

    generateCart();
  }, [mealPlanId]);

  // Render based on workflow step
  if (state.isLoading && state.step === 'loading') {
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
            href="/meals"
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

  const stepIndex = workflowSteps.findIndex((s) => s.step === state.step);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/meals"
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
          {workflowSteps.map((item, idx, arr) => (
            <React.Fragment key={item.step}>
              <button
                onClick={() =>
                  stepIndex >= idx &&
                  setState((prev) => ({ ...prev, step: item.step }))
                }
                className={`flex flex-col items-center gap-2 flex-1 pb-6 relative text-sm font-medium ${
                  state.step === item.step
                    ? 'text-blue-600'
                    : idx < stepIndex
                    ? 'text-green-600'
                    : 'text-gray-400'
                }`}
              >
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 font-bold ${
                    state.step === item.step
                      ? 'border-blue-600 bg-blue-50'
                      : idx < stepIndex
                      ? 'border-green-600 bg-green-50 text-green-600'
                      : 'border-gray-300 bg-gray-100'
                  }`}
                >
                  {idx < stepIndex ? '✓' : idx + 1}
                </div>
                {item.name}
              </button>
              {idx < arr.length - 1 && (
                <div
                  className={`h-0.5 w-8 mb-8 ${
                    stepIndex > idx ? 'bg-green-600' : 'bg-gray-300'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {/* Cart Preview */}
          {(state.step === 'cart-preview' || state.step === 'delivery-selection' || state.step === 'review') &&
            state.cartData && (
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <CartPreview
                data={state.cartData}
                onCheckout={() => setState((prev) => ({ ...prev, step: 'delivery-selection' }))}
                isLoading={false}
              />
            </div>
          )}

          {/* Missing Items */}
          {(state.step === 'delivery-selection' || state.step === 'review') &&
            state.cartData?.unavailable_items.length! > 0 && (
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
                <strong className="font-semibold">{state.cartData?.item_count}</strong> items.
                {state.selectedDeliverySlot && (
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
                className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 transition-colors"
              >
                Complete Order on Knuspr →
              </button>
              <p className="text-xs text-green-700 text-center">
                You'll be redirected to Knuspr to finalize your order
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
