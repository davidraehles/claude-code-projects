/**
 * React Query provider for data fetching and caching.
 * Centralizes side effects and provides automatic caching/refetching.
 */

'use client'

import { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a client outside the component to ensure singleton behavior
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Don't refetch on window focus in development to reduce noise
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',
      // Retry failed requests once
      retry: 1,
      // Consider data stale after 5 minutes
      staleTime: 5 * 60 * 1000,
      // Keep unused data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
    },
  },
})

interface QueryProviderProps {
  children: ReactNode
}

/**
 * Provider component that wraps the app with React Query.
 * Must be used within a client component.
 */
export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
