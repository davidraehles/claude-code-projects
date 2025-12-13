/**
 * React Query hooks for Recipe endpoints.
 * Provides automatic caching, refetching, and loading/error states.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import type { RecipeCreateRequest, RecipeImportRequest } from '@/lib/types'

/**
 * Query keys for recipes.
 * Organized by entity and parameters for automatic cache invalidation.
 */
export const recipeKeys = {
  all: ['recipes'] as const,
  lists: () => [...recipeKeys.all, 'list'] as const,
  list: (skip: number, limit: number) => [...recipeKeys.lists(), { skip, limit }] as const,
  details: () => [...recipeKeys.all, 'detail'] as const,
  detail: (id: number) => [...recipeKeys.details(), id] as const,
}

/**
 * Hook to fetch paginated recipes.
 * Automatically handles auth token and provides loading/error states.
 */
export function useRecipes(skip: number = 0, limit: number = 50) {
  const token = useAuthToken()

  return useQuery({
    queryKey: recipeKeys.list(skip, limit),
    queryFn: async () => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.getRecipes(skip, limit, token)
    },
    enabled: !!token, // Only run query if authenticated
  })
}

/**
 * Hook to fetch a single recipe by ID.
 */
export function useRecipe(id: number, enabled: boolean = true) {
  const token = useAuthToken()

  return useQuery({
    queryKey: recipeKeys.detail(id),
    queryFn: async () => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.getRecipe(id, token)
    },
    enabled: !!token && enabled,
  })
}

/**
 * Hook to create a new recipe.
 * Automatically invalidates recipe list cache on success.
 */
export function useCreateRecipe() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: RecipeCreateRequest) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.createRecipe(data, token)
    },
    onSuccess: () => {
      // Invalidate and refetch recipe lists
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() })
    },
  })
}

/**
 * Hook to update an existing recipe.
 * Automatically invalidates affected caches on success.
 */
export function useUpdateRecipe() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<RecipeCreateRequest> }) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.updateRecipe(id, data, token)
    },
    onSuccess: (updatedRecipe) => {
      // Invalidate specific recipe detail
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(updatedRecipe.id) })
      // Invalidate recipe lists
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() })
    },
  })
}

/**
 * Hook to delete a recipe.
 * Automatically invalidates recipe list cache on success.
 */
export function useDeleteRecipe() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.deleteRecipe(id, token)
    },
    onSuccess: () => {
      // Invalidate and refetch recipe lists
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() })
    },
  })
}

/**
 * Hook to import a recipe from URL.
 * Automatically invalidates recipe list cache on success.
 */
export function useImportRecipe() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: RecipeImportRequest) => {
      if (!token) {
        throw new Error('Not authenticated')
      }
      return api.importRecipe(data, token)
    },
    onSuccess: () => {
      // Invalidate and refetch recipe lists
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() })
    },
  })
}
