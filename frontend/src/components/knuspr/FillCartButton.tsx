'use client'

/**
 * FillCartButton component
 *
 * Provides a button to fill a Knuspr cart from a grocery cart with authentication.
 * Features:
 * - Credential input form with validation
 * - Progress indicator during cart filling
 * - Success message with Knuspr cart link
 * - Display of unmatched items
 * - Option to save credentials locally
 * - Full accessibility support
 */

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Checkbox } from '@/components/ui/Checkbox'
import { useFillKnusprCart } from '@/hooks/queries/useKnusprCart'
import { useKnusprCredentials } from '@/hooks/queries/useKnusprCredentials'
import type { CartItem } from '@/hooks/queries/useGroceryCarts'

export interface FillCartButtonProps {
  cart_id: number
  cart_items: CartItem[]
  className?: string
}

export function FillCartButton({
  cart_id,
  cart_items,
  className = '',
}: FillCartButtonProps) {
  const [showForm, setShowForm] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberCredentials, setRememberCredentials] = useState(false)
  const [formErrors, setFormErrors] = useState<{
    email?: string
    password?: string
  }>({})
  const [showPassword, setShowPassword] = useState(false)

  // Hooks
  const fillCartMutation = useFillKnusprCart(cart_id)
  const { credentialStatus, saveCredentials } = useKnusprCredentials()

  // Load saved credentials if available
  useEffect(() => {
    if (credentialStatus.data?.has_credentials && credentialStatus.data?.knuspr_email) {
      setEmail(credentialStatus.data.knuspr_email)
      setRememberCredentials(true)
    }
  }, [credentialStatus.data])

  // Validate form
  const validateForm = (): boolean => {
    const errors: { email?: string; password?: string } = {}

    if (!email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email address'
    }

    if (!password) {
      errors.password = 'Password is required'
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      // Save credentials if user opted in
      if (rememberCredentials) {
        await saveCredentials.mutateAsync({
          knuspr_email: email,
          knuspr_password: password,
          country: 'cz',
          test_connection: false,
        })
      }

      // Fill the Knuspr cart
      await fillCartMutation.mutateAsync({
        credentials: {
          email,
          password,
        },
        match_preferences: {
          allow_substitutions: true,
        },
      })
    } catch (error) {
      // Error is handled by mutation
      console.error('Failed to fill cart:', error)
    }
  }

  // Handle button click
  const handleButtonClick = () => {
    if (credentialStatus.data?.has_credentials) {
      // Use saved credentials automatically
      fillCartMutation.mutate({
        credentials: {
          email: credentialStatus.data.knuspr_email || email,
          password: '', // Backend will use saved credentials
        },
      })
    } else {
      // Show form
      setShowForm(true)
    }
  }

  // Reset state
  const handleReset = () => {
    setShowForm(false)
    setPassword('')
    setFormErrors({})
    fillCartMutation.reset()
  }

  // Idle state - initial button
  if (!showForm && !fillCartMutation.isPending && !fillCartMutation.isSuccess && !fillCartMutation.isError) {
    return (
      <div className={className}>
        <Button
          variant="primary"
          onClick={handleButtonClick}
          disabled={cart_items.length === 0}
          className="w-full"
          aria-label="Fill Knuspr cart with grocery items"
        >
          <span className="flex items-center justify-center gap-2">
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
            <span>Fill Knuspr Cart</span>
          </span>
        </Button>

        {cart_items.length === 0 && (
          <p className="text-sm text-gray-500 mt-2 text-center">
            No items in cart
          </p>
        )}
      </div>
    )
  }

  // Credential form state
  if (showForm && !fillCartMutation.isPending && !fillCartMutation.isSuccess) {
    return (
      <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Knuspr Login
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="email"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={formErrors.email}
            placeholder="your@email.com"
            autoComplete="email"
            aria-label="Knuspr email address"
            aria-invalid={!!formErrors.email}
            aria-describedby={formErrors.email ? 'email-error' : undefined}
          />

          <div>
            <Input
              type={showPassword ? 'text' : 'password'}
              label="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={formErrors.password}
              placeholder="Your Knuspr password"
              autoComplete="current-password"
              aria-label="Knuspr password"
              aria-invalid={!!formErrors.password}
              aria-describedby={formErrors.password ? 'password-error' : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-sm text-blue-600 hover:text-blue-700 mt-1"
            >
              {showPassword ? 'Hide' : 'Show'} password
            </button>
          </div>

          <div className="space-y-3">
            <Checkbox
              label="Remember my credentials (saved securely in your browser)"
              checked={rememberCredentials}
              onChange={setRememberCredentials}
            />

            {rememberCredentials && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <div className="flex items-start gap-2">
                  <svg
                    className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <p className="text-xs text-yellow-800">
                    Security notice: Credentials will be stored locally in your browser.
                    Never share your credentials with anyone.
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-xs text-blue-800">
              Don't have a Knuspr account?{' '}
              <a
                href="https://knuspr.cz/register"
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold underline hover:text-blue-900"
              >
                Create one here
              </a>
            </p>
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={fillCartMutation.isPending}
              aria-label="Submit and fill Knuspr cart"
            >
              Fill Cart
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              className="flex-1"
              aria-label="Cancel"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    )
  }

  // Loading state with progress
  if (fillCartMutation.isPending) {
    const progress = fillCartMutation.data?.progress || 0

    return (
      <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
        <div className="flex flex-col items-center">
          <svg
            className="animate-spin h-12 w-12 text-blue-600 mb-4"
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

          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Filling Knuspr Cart...
          </h3>

          <p className="text-sm text-gray-600 mb-4 text-center">
            Matching items with Knuspr products and adding to cart
          </p>

          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Cart filling progress"
            />
          </div>

          <p className="text-xs text-gray-500">
            {progress}% complete
          </p>
        </div>
      </div>
    )
  }

  // Success state
  if (fillCartMutation.isSuccess && fillCartMutation.data) {
    const { matched_items, unmatched_items, knuspr_cart_url } = fillCartMutation.data

    return (
      <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-3">
            <svg
              className="h-8 w-8 text-green-600 flex-shrink-0"
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
              <p className="font-semibold text-green-900 text-lg">
                Cart Filled Successfully!
              </p>
              <p className="text-sm text-green-700 mt-1">
                {matched_items} item{matched_items !== 1 ? 's' : ''} added to your Knuspr cart
              </p>
            </div>
          </div>
        </div>

        {/* Unmatched items warning */}
        {unmatched_items.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <svg
                className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div className="flex-1">
                <p className="font-semibold text-yellow-900">
                  {unmatched_items.length} item{unmatched_items.length !== 1 ? 's' : ''} could not be matched
                </p>
                <ul className="mt-2 space-y-1 text-sm text-yellow-800">
                  {unmatched_items.map((item, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-yellow-600">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
                <p className="text-xs text-yellow-700 mt-2">
                  You can manually add these items in your Knuspr cart or find alternatives.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-col gap-3">
          {knuspr_cart_url && (
            <a
              href={knuspr_cart_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block"
            >
              <Button
                variant="primary"
                className="w-full"
                aria-label="Open Knuspr cart in new tab"
              >
                <span className="flex items-center justify-center gap-2">
                  <span>View in Knuspr</span>
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
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </span>
              </Button>
            </a>
          )}

          <Button
            variant="outline"
            onClick={handleReset}
            className="w-full"
            aria-label="Close and return"
          >
            Done
          </Button>
        </div>
      </div>
    )
  }

  // Error state
  if (fillCartMutation.isError) {
    const errorMessage = fillCartMutation.error?.message || 'An unexpected error occurred'
    const isAuthError = errorMessage.toLowerCase().includes('auth') ||
                       errorMessage.toLowerCase().includes('credential') ||
                       errorMessage.toLowerCase().includes('login')

    return (
      <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
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
                {isAuthError ? 'Authentication Failed' : 'Failed to Fill Cart'}
              </p>
              <p className="text-sm text-red-700 mt-1">
                {errorMessage}
              </p>
              {isAuthError && (
                <p className="text-xs text-red-600 mt-2">
                  Please check your Knuspr email and password and try again.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            variant="primary"
            onClick={() => {
              setShowForm(true)
              fillCartMutation.reset()
            }}
            className="flex-1"
            aria-label="Try again with different credentials"
          >
            Try Again
          </Button>
          <Button
            variant="outline"
            onClick={handleReset}
            className="flex-1"
            aria-label="Cancel"
          >
            Cancel
          </Button>
        </div>
      </div>
    )
  }

  return null
}

export default FillCartButton
