/**
 * React Query hook for file-based recipe import.
 * Handles uploading HTML and PDF files to extract recipes.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthToken } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import { recipeKeys } from './useRecipes'

/**
 * Hook to upload a recipe file (HTML or PDF).
 * Automatically invalidates recipe list cache on success.
 */
export function useFileUpload() {
  const token = useAuthToken()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      if (!token) {
        throw new Error('Not authenticated')
      }

      // Validate file type
      const ext = file.name.split('.').pop()?.toLowerCase()
      if (!ext || !['html', 'htm', 'pdf'].includes(ext)) {
        throw new Error('Unsupported file type. Please upload an HTML or PDF file.')
      }

      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        throw new Error('File is too large. Maximum size is 10MB.')
      }

      return api.uploadRecipeFile(file, token)
    },
    onSuccess: () => {
      // Invalidate and refetch recipe lists
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() })
    },
  })
}
