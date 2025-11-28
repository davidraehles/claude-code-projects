/**
 * React Query hooks for Workflow endpoints.
 * Provides integration with end-to-end meal plan to grocery cart workflows.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import { groceryCartKeys } from './useGroceryCarts'

interface DeliveryPreferences {
  preferred_dates?: string[]
  preferred_time_slot?: 'morning' | 'afternoon' | 'evening'
  budget_optimization?: boolean
}

interface WorkflowResult {
  cart_id: number
  knuspr_url: string
  total_price: number
  item_count: number
  delivery_slot?: unknown
  items_by_section?: Record<string, unknown>
  unavailable_items?: string[]
}

interface WorkflowResponse {
  workflow_id: string
  status: string
  message: string
  result?: WorkflowResult
}

/**
 * Hook to create a grocery cart from a meal plan using the end-to-end workflow.
 * This workflow integrates with Knuspr MCP to map ingredients to actual products
 * and create a real shopping cart with delivery slot selection.
 */
export function useCreateCartFromMealPlanWorkflow() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation<
    WorkflowResponse,
    Error,
    { mealPlanId: number; deliveryPreferences?: DeliveryPreferences }
  >({
    mutationFn: async ({ mealPlanId, deliveryPreferences }) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.createCartFromMealPlanWorkflow(
        mealPlanId,
        deliveryPreferences,
        token
      )
    },
    onSuccess: (response) => {
      // Invalidate grocery cart caches
      if (response.result?.cart_id) {
        queryClient.invalidateQueries({
          queryKey: groceryCartKeys.detail(response.result.cart_id),
        })
      }
      queryClient.invalidateQueries({ queryKey: groceryCartKeys.all })
    },
  })
}
