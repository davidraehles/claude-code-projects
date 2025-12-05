/**
 * React Query hooks for Knuspr cart integration.
 * Provides functionality for filling Knuspr carts from grocery carts.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { groceryCartKeys } from './useGroceryCarts'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Request types for filling Knuspr cart
 */
export interface FillKnusprCartRequest {
  credentials: {
    email: string
    password: string
  }
  match_preferences?: {
    prefer_organic?: boolean
    max_price_difference?: number
    allow_substitutions?: boolean
  }
}

/**
 * Response types for filling Knuspr cart
 */
export interface FillKnusprCartResponse {
  success: boolean
  matched_items: number
  unmatched_items: string[]
  progress: number
  knuspr_cart_url?: string
  total_price?: number
  delivery_slots?: Array<{
    date: string
    time_slot: string
    price: number
  }>
}

/**
 * Hook to fill a Knuspr cart from a grocery cart.
 *
 * Usage:
 * ```tsx
 * const fillCartMutation = useFillKnusprCart(cart_id)
 *
 * await fillCartMutation.mutateAsync({
 *   credentials: { email: 'user@example.com', password: 'password' },
 *   match_preferences: { prefer_organic: true }
 * })
 * ```
 */
export function useFillKnusprCart(cartId: number) {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation<FillKnusprCartResponse, Error, FillKnusprCartRequest>({
    mutationFn: async (request: FillKnusprCartRequest) => {
      if (!token) {
        throw new Error('Not authenticated')
      }

      const response = await fetch(
        `${API_URL}/api/v1/workflows/carts/${cartId}/fill-knuspr`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        }
      )

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
        }))
        throw new Error(error.detail || 'Failed to fill Knuspr cart')
      }

      return response.json()
    },
    onSuccess: (data) => {
      // Invalidate grocery cart cache to reflect updated state
      queryClient.invalidateQueries({ queryKey: groceryCartKeys.detail(cartId) })
      queryClient.invalidateQueries({ queryKey: groceryCartKeys.all })

      // Log success for debugging
      console.log('Knuspr cart filled successfully:', {
        matched: data.matched_items,
        unmatched: data.unmatched_items.length,
        url: data.knuspr_cart_url,
      })
    },
    onError: (error) => {
      // Log error for debugging
      console.error('Failed to fill Knuspr cart:', error.message)
    },
  })
}

/**
 * Export query keys for manual cache management if needed
 */
export const knusprCartKeys = {
  all: ['knusprCarts'] as const,
  fill: (cartId: number) => [...knusprCartKeys.all, 'fill', cartId] as const,
}
