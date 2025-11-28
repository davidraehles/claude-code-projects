/**
 * React Query hooks for GroceryCart endpoints.
 * Provides automatic caching, refetching, and loading/error states.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import type { GroceryCart } from '@/lib/types'

/**
 * Query keys for grocery carts.
 * Organized by entity and parameters for automatic cache invalidation.
 */
export const groceryCartKeys = {
  all: ['groceryCarts'] as const,
  details: () => [...groceryCartKeys.all, 'detail'] as const,
  detail: (id: number) => [...groceryCartKeys.details(), id] as const,
}

/**
 * Hook to fetch a single grocery cart by ID.
 */
export function useGroceryCart(id: number, enabled: boolean = true) {
  const token = useAuthToken()

  return useQuery({
    queryKey: groceryCartKeys.detail(id),
    queryFn: async () => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.getGroceryCart(id, token)
    },
    enabled: !!token && enabled,
  })
}

/**
 * Hook to generate a grocery cart from a meal plan.
 * Automatically invalidates grocery cart cache on success.
 */
export function useGenerateGroceryCart() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (mealPlanId: number) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.generateGroceryCart(mealPlanId, token)
    },
    onSuccess: (groceryCart) => {
      // Invalidate specific grocery cart detail
      queryClient.invalidateQueries({ queryKey: groceryCartKeys.detail(groceryCart.id) })
      // Invalidate all grocery carts
      queryClient.invalidateQueries({ queryKey: groceryCartKeys.all })
    },
  })
}
