/**
 * React Query hooks for MealPlan endpoints.
 * Provides automatic caching, refetching, and loading/error states.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import type { MealPlan, MealPlanDetail, MealPlanCreateRequest } from '@/lib/types'

/**
 * Query keys for meal plans.
 * Organized by entity and parameters for automatic cache invalidation.
 */
export const mealPlanKeys = {
  all: ['mealPlans'] as const,
  lists: () => [...mealPlanKeys.all, 'list'] as const,
  list: (skip: number, limit: number) => [...mealPlanKeys.lists(), { skip, limit }] as const,
  details: () => [...mealPlanKeys.all, 'detail'] as const,
  detail: (id: number) => [...mealPlanKeys.details(), id] as const,
}

/**
 * Hook to fetch paginated meal plans.
 * Automatically handles auth token and provides loading/error states.
 */
export function useMealPlans(skip: number = 0, limit: number = 20) {
  const token = useAuthToken()

  return useQuery({
    queryKey: mealPlanKeys.list(skip, limit),
    queryFn: async () => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.getMealPlans(skip, limit, token)
    },
    enabled: !!token && token.trim().length > 0,
  })
}

/**
 * Hook to fetch a single meal plan by ID with full details.
 */
export function useMealPlan(id: number, enabled: boolean = true) {
  const token = useAuthToken()

  return useQuery({
    queryKey: mealPlanKeys.detail(id),
    queryFn: async () => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.getMealPlan(id, token)
    },
    enabled: !!token && token.trim().length > 0 && enabled,
  })
}

/**
 * Hook to create a new meal plan.
 * Automatically invalidates meal plan list cache on success.
 */
export function useCreateMealPlan() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: MealPlanCreateRequest) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.createMealPlan(data, token)
    },
    onSuccess: () => {
      // Invalidate and refetch meal plan lists
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() })
    },
  })
}

/**
 * Hook to delete a meal plan.
 * Automatically invalidates meal plan list cache on success.
 */
export function useDeleteMealPlan() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.deleteMealPlan(id, token)
    },
    onSuccess: () => {
      // Invalidate and refetch meal plan lists
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() })
    },
  })
}
