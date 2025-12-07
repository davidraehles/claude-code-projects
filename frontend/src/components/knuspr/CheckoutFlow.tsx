'use client';

import React, { useState, useCallback } from 'react';
import { ArrowRight, ArrowLeft, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import CartPreview, { CartPreviewData } from './CartPreview';
import DeliverySlotPicker, { DeliverySlot } from './DeliverySlotPicker';
import { formatEUR } from '@/lib/formatCurrency';

export type CheckoutStep = 'cart' | 'delivery' | 'confirm' | 'complete';

export interface CheckoutFlowProps {
  cartData: CartPreviewData;
  availableSlots: DeliverySlot[];
  onCheckoutComplete?: (orderId: string) => void;
  onCancel?: () => void;
  isProcessing?: boolean;
}

interface CheckoutState {
  currentStep: CheckoutStep;
  selectedSlot: DeliverySlot | null;
  error: string | null;
  orderConfirmed: boolean;
  orderId?: string;
}

/**
 * CheckoutFlow Component
 *
 * Orchestrates the complete checkout workflow:
 * 1. Cart Review - Display cart items with summary
 * 2. Delivery Selection - Pick delivery slot and confirm
 * 3. Confirmation - Final review before checkout
 * 4. Complete - Success state with order confirmation
 *
 * Implements stepping through checkout stages with back/forward navigation
 * and error recovery at each stage.
 */
const CheckoutFlow: React.FC<CheckoutFlowProps> = ({
  cartData,
  availableSlots,
  onCheckoutComplete,
  onCancel,
  isProcessing = false,
}) => {
  const [state, setState] = useState<CheckoutState>({
    currentStep: 'cart',
    selectedSlot: cartData.delivery_slot || null,
    error: null,
    orderConfirmed: false,
  });

  /**
   * Navigate to next step
   * Validates that required fields are set before allowing progression
   */
  const goToNextStep = useCallback(() => {
    setState((prev) => {
      switch (prev.currentStep) {
        case 'cart':
          return { ...prev, currentStep: 'delivery', error: null };
        case 'delivery':
          if (!state.selectedSlot) {
            return { ...prev, error: 'Please select a delivery slot' };
          }
          return { ...prev, currentStep: 'confirm', error: null };
        case 'confirm':
          return { ...prev, currentStep: 'complete', error: null, orderConfirmed: true };
        default:
          return prev;
      }
    });
  }, [state.selectedSlot]);

  /**
   * Navigate to previous step
   */
  const goToPreviousStep = useCallback(() => {
    setState((prev) => {
      const stepOrder: CheckoutStep[] = ['cart', 'delivery', 'confirm', 'complete'];
      const currentIndex = stepOrder.indexOf(prev.currentStep);

      if (currentIndex > 0) {
        return {
          ...prev,
          currentStep: stepOrder[currentIndex - 1],
          error: null,
        };
      }
      return prev;
    });
  }, []);

  /**
   * Handle slot selection
   */
  const handleSlotSelected = useCallback((slot: DeliverySlot) => {
    setState((prev) => ({
      ...prev,
      selectedSlot: slot,
      error: null,
    }));
  }, []);

  /**
   * Handle final checkout submission
   */
  const handleCheckout = useCallback(() => {
    if (!state.selectedSlot) {
      setState((prev) => ({
        ...prev,
        error: 'No delivery slot selected. Please go back and select a slot.',
      }));
      return;
    }

    // Generate order ID when completing checkout
    // In production, this would submit to the backend
    const orderId = `ORD-${Date.now()}`;
    setState((prev) => ({
      ...prev,
      orderId,
    }));

    if (onCheckoutComplete) {
      onCheckoutComplete(orderId);
    }
  }, [state.selectedSlot, onCheckoutComplete]);

  /**
   * Render cart review step
   */
  const renderCartStep = () => (
    <div className="space-y-6">
      <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
        <h2 className="text-lg font-semibold text-blue-900">Step 1 of 3: Review Cart</h2>
        <p className="text-sm text-blue-700 mt-1">
          Please review your shopping items before proceeding to delivery selection.
        </p>
      </div>
      <CartPreview data={cartData} isLoading={false} />
    </div>
  );

  /**
   * Render delivery selection step
   */
  const renderDeliveryStep = () => (
    <div className="space-y-6">
      <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
        <h2 className="text-lg font-semibold text-blue-900">Step 2 of 3: Select Delivery Slot</h2>
        <p className="text-sm text-blue-700 mt-1">
          Choose your preferred delivery date and time window.
        </p>
      </div>

      {state.error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 flex gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Selection Required</p>
            <p className="text-sm text-red-800">{state.error}</p>
          </div>
        </div>
      )}

      <DeliverySlotPicker
        slots={availableSlots}
        selected={state.selectedSlot?.slot_id}
        onSelect={handleSlotSelected}
      />

      {state.selectedSlot && (
        <div className="rounded-lg bg-green-50 border border-green-200 p-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-green-900">Delivery Confirmed</p>
              <p className="text-sm text-green-700">
                {new Date(state.selectedSlot.date).toLocaleDateString()} •{' '}
                {state.selectedSlot.time_window} ({formatEUR(state.selectedSlot.price)})
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  /**
   * Render confirmation step
   */
  const renderConfirmStep = () => (
    <div className="space-y-6">
      <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
        <h2 className="text-lg font-semibold text-blue-900">Step 3 of 3: Confirm Order</h2>
        <p className="text-sm text-blue-700 mt-1">
          Please review all details before completing your order.
        </p>
      </div>

      {/* Cart Summary */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Order Summary</h3>

        <div className="space-y-3 py-4 border-y border-gray-200">
          <div className="flex justify-between">
            <span className="text-gray-600">Items ({cartData.item_count})</span>
            <span className="font-medium text-gray-900">
              {formatEUR(Object.values(cartData.items_by_section)
                .flat()
                .reduce((sum, item) => sum + item.price * item.quantity, 0))}
            </span>
          </div>

          {state.selectedSlot && (
            <div className="flex justify-between">
              <span className="text-gray-600">Delivery ({state.selectedSlot.time_window})</span>
              <span className="font-medium text-gray-900">{formatEUR(state.selectedSlot.price)}</span>
            </div>
          )}

          <div className="flex justify-between pt-2">
            <span className="text-lg font-semibold text-gray-900">Total</span>
            <span className="text-2xl font-bold text-blue-600">
              {formatEUR(Object.values(cartData.items_by_section)
                .flat()
                .reduce((sum, item) => sum + item.price * item.quantity, 0) +
                (state.selectedSlot?.price || 0))}
            </span>
          </div>
        </div>

        {/* Delivery Details */}
        {state.selectedSlot && (
          <div className="rounded-lg bg-gray-50 p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Delivery Details</h4>
            <p className="text-sm text-gray-700">
              <strong>Date:</strong> {new Date(state.selectedSlot.date).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Time:</strong> {state.selectedSlot.time_window}
            </p>
          </div>
        )}

        {/* Terms Acceptance */}
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4">
          <label className="flex gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={state.orderConfirmed}
              onChange={(e) =>
                setState((prev) => ({
                  ...prev,
                  orderConfirmed: e.target.checked,
                }))
              }
              className="mt-1 w-4 h-4 accent-blue-600"
            />
            <span className="text-sm text-gray-700">
              I confirm that the cart contents and delivery details are correct, and I authorize
              this purchase.
            </span>
          </label>
        </div>
      </div>
    </div>
  );

  /**
   * Render completion step
   */
  const renderCompleteStep = () => (
    <div className="rounded-lg border border-green-200 bg-green-50 p-8 text-center space-y-4">
      <CheckCircle className="h-16 w-16 text-green-600 mx-auto" />
      <h2 className="text-2xl font-bold text-green-900">Order Confirmed!</h2>
      <p className="text-green-800">
        Your shopping cart has been successfully submitted to Knuspr.
      </p>

      <div className="bg-white rounded-lg p-4 my-4">
        <p className="text-sm text-gray-600">Order ID</p>
        <p className="text-lg font-mono font-bold text-gray-900 break-all">
          {state.orderId || 'Generating...'}
        </p>
      </div>

      <p className="text-sm text-green-700">
        You will receive an email confirmation shortly with your delivery details.
      </p>
    </div>
  );

  // Render based on current step
  const renderContent = () => {
    switch (state.currentStep) {
      case 'cart':
        return renderCartStep();
      case 'delivery':
        return renderDeliveryStep();
      case 'confirm':
        return renderConfirmStep();
      case 'complete':
        return renderCompleteStep();
      default:
        return null;
    }
  };

  // Render navigation buttons
  const renderNavigation = () => {
    if (state.currentStep === 'complete') {
      return (
        <button
          onClick={onCancel}
          className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-gray-600 px-6 py-3 font-semibold text-white hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Return to Dashboard
        </button>
      );
    }

    return (
      <div className="flex gap-3">
        <button
          onClick={goToPreviousStep}
          disabled={state.currentStep === 'cart' || isProcessing}
          className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowLeft className="h-5 w-5" />
          Back
        </button>

        <button
          onClick={
            state.currentStep === 'confirm' ? handleCheckout : goToNextStep
          }
          disabled={
            isProcessing ||
            (state.currentStep === 'confirm' && !state.orderConfirmed) ||
            (state.currentStep === 'delivery' && !state.selectedSlot)
          }
          className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing && <Loader className="h-5 w-5 animate-spin" />}
          {state.currentStep === 'confirm'
            ? 'Complete Order'
            : 'Next'}
          {!isProcessing && <ArrowRight className="h-5 w-5" />}
        </button>
      </div>
    );
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Progress Indicator */}
      {state.currentStep !== 'complete' && (
        <div className="flex items-center justify-between">
          {(['cart', 'delivery', 'confirm'] as const).map((step, index) => {
            const stepOrder = ['cart', 'delivery', 'confirm'] as const;
            const currentIndex = state.currentStep === 'complete'
              ? stepOrder.length
              : stepOrder.indexOf(state.currentStep as typeof stepOrder[number]);
            const isComplete = currentIndex > index;
            const isCurrent = currentIndex === index;

            return (
              <React.Fragment key={step}>
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold transition-all ${isComplete
                      ? 'bg-green-600 text-white'
                      : isCurrent
                        ? 'bg-blue-600 text-white ring-4 ring-blue-100'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                >
                  {isComplete ? '✓' : index + 1}
                </div>
                {index < 2 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${isComplete ? 'bg-green-600' : 'bg-gray-200'
                      }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      )}

      {/* Step Content */}
      {renderContent()}

      {/* Navigation */}
      <div className="pt-4">{renderNavigation()}</div>
    </div>
  );
};

export default CheckoutFlow;
