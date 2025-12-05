/**
 * React Query hooks for GroceryCart endpoints.
 * Provides automatic caching, refetching, and loading/error states.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { api } from '@/lib/api'

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

/**
 * Request/Response types for cart generation from meal plan
 */
export interface GenerateCartFromMealPlanRequest {
  meal_plan_id: number
  aggregate_duplicates?: boolean
}

export interface CartItem {
  id: number
  ingredient: string
  quantity: string
  category?: string
  recipe_ids?: number[]
  checked?: boolean
}

export interface GenerateCartFromMealPlanResponse {
  cart_id: number
  items: CartItem[]
  unmatched_ingredients: string[]
}

/**
 * Hook to generate a grocery cart from a meal plan using the workflow endpoint.
 * This is a simplified version that creates a cart without Knuspr integration.
 * Automatically invalidates grocery cart cache on success and shows toast notifications.
 */
export function useGenerateCartFromMealPlan() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation<
    GenerateCartFromMealPlanResponse,
    Error,
    GenerateCartFromMealPlanRequest
  >({
    mutationFn: async ({ meal_plan_id }) => {
      if (!token) {
        throw new Error('Not authenticated')
      }

      // Use the existing workflow endpoint
      const response = await api.createCartFromMealPlanWorkflow(
        meal_plan_id,
        undefined, // No delivery preferences for simple cart generation
        token
      )

      // Transform workflow response to expected format
      return {
        cart_id: response.result?.cart_id || 0,
        items: [], // Items will be fetched separately when viewing the cart
        unmatched_ingredients: response.result?.unavailable_items || []
      }
    },
    onSuccess: (response) => {
      // Invalidate specific grocery cart detail
      if (response.cart_id) {
        queryClient.invalidateQueries({ queryKey: groceryCartKeys.detail(response.cart_id) })
      }
      // Invalidate all grocery carts
      queryClient.invalidateQueries({ queryKey: groceryCartKeys.all })
    },
  })
}
