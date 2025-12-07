/**
 * Custom hook for fetching data with authentication.
 * Automatically handles auth state and provides loading/error states.
 */

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'

interface UseAuthenticatedDataOptions<T> {
  /**
   * Data fetcher function that receives the auth token
   */
  fetcher: (token: string) => Promise<T>

  /**
   * Skip fetching if true
   */
  skip?: boolean

  /**
   * Dependencies to trigger refetch
   */
  deps?: (string | number | boolean | null | undefined)[]
}

interface UseAuthenticatedDataResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

/**
 * Hook for fetching authenticated data.
 * Eliminates duplicate useEffect patterns across components.
 *
 * @example
 * const { data: recipes, loading, error } = useAuthenticatedData({
 *   fetcher: (token) => api.getRecipes(1, 50, token)
 * })
 */
export function useAuthenticatedData<T>({
  fetcher,
  skip = false,
  deps = [],
}: UseAuthenticatedDataOptions<T>): UseAuthenticatedDataResult<T> {
  const { token, isAuthenticated, isLoading: authLoading } = useAuth()
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    // Wait for auth to finish loading
    if (authLoading) return

    // Skip if not authenticated or skip flag is set
    if (!isAuthenticated || !token || skip) {
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const result = await fetcher(token)
      setData(result)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
      console.error('[useAuthenticatedData] Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, isAuthenticated, token, skip, ...deps])

  return {
    data,
    loading: authLoading || loading,
    error,
    refetch: fetchData,
  }
}
