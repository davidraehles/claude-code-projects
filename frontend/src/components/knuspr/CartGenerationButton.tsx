'use client'

/**
 * CartGenerationButton component
 *
 * Allows users to generate a grocery cart from a meal plan.
 * Provides visual feedback for loading, success, and error states.
 * Includes proper accessibility features and responsive design.
 */

import React, { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useGenerateCartFromMealPlan } from '@/hooks/queries/useGroceryCarts'

export interface CartGenerationButtonProps {
  meal_plan_id: number
  className?: string
}

export function CartGenerationButton({
  meal_plan_id,
  className = ''
}: CartGenerationButtonProps) {
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)
  const [generatedCartId, setGeneratedCartId] = useState<number | null>(null)

  // Use the mutation hook
  const mutation = useGenerateCartFromMealPlan()

  const handleGenerateCart = () => {
    setShowSuccessMessage(false)

    mutation.mutate(
      { meal_plan_id },
      {
        onSuccess: (response) => {
          setGeneratedCartId(response.cart_id)
          setShowSuccessMessage(true)

          // Auto-hide success message after 5 seconds
          setTimeout(() => {
            setShowSuccessMessage(false)
          }, 5000)
        },
        onError: (error) => {
          console.error('Failed to generate cart:', error)
        }
      }
    )
  }

  // Loading state
  if (mutation.isPending) {
    return (
      <div className={`flex flex-col items-center ${className}`}>
        <Button
          variant="primary"
          disabled
          className="flex items-center gap-2"
          aria-busy="true"
          aria-label="Generating grocery cart"
        >
          <svg
            className="animate-spin h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Generating Cart...</span>
        </Button>
        <p className="text-sm text-gray-600 mt-2">
          This may take a few seconds
        </p>
      </div>
    )
  }

  // Success state with link to cart
  if (showSuccessMessage && generatedCartId) {
    return (
      <div className={`flex flex-col items-center ${className}`}>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-3 w-full">
          <div className="flex items-center gap-3">
            <svg
              className="h-6 w-6 text-green-600 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <p className="font-semibold text-green-900">
                Cart Generated Successfully!
              </p>
              <p className="text-sm text-green-700 mt-1">
                Your grocery cart is ready to view
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-3 w-full">
          <Link
            href={`/grocery-carts/${generatedCartId}`}
            className="flex-1"
          >
            <Button
              variant="primary"
              className="w-full"
              aria-label="View generated grocery cart"
            >
              View Cart
            </Button>
          </Link>

          <Button
            variant="secondary"
            onClick={handleGenerateCart}
            className="flex-1"
            aria-label="Generate another grocery cart"
          >
            Generate Again
          </Button>
        </div>
      </div>
    )
  }

  // Error state
  if (mutation.isError) {
    return (
      <div className={`flex flex-col ${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-3">
          <div className="flex items-start gap-3">
            <svg
              className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <p className="font-semibold text-red-900">
                Failed to Generate Cart
              </p>
              <p className="text-sm text-red-700 mt-1">
                {mutation.error?.message || 'An unexpected error occurred'}
              </p>
            </div>
          </div>
        </div>

        <Button
          variant="primary"
          onClick={handleGenerateCart}
          className="w-full"
          aria-label="Retry generating grocery cart"
        >
          Try Again
        </Button>
      </div>
    )
  }

  // Idle state - initial button
  return (
    <Button
      variant="primary"
      onClick={handleGenerateCart}
      className={className}
      aria-label="Generate grocery cart from meal plan"
    >
      <span className="flex items-center gap-2">
        <svg
          className="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
        <span>Generate Grocery Cart</span>
      </span>
    </Button>
  )
}

export default CartGenerationButton
