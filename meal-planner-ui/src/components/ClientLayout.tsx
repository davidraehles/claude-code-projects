/**
 * Client-side layout wrapper with error boundary and auth context.
 * Separates client components from server layout.
 */

'use client'

import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { ErrorBoundary } from './ErrorBoundary'
import { AuthProvider } from '@/contexts/AuthContext'
import { QueryProvider } from '@/providers/QueryProvider'

interface ClientLayoutProps {
  children: ReactNode
}

export function ClientLayout({ children }: ClientLayoutProps) {
  const handleError = (error: Error) => {
    // In production, log to error tracking service
    // Example: Sentry.captureException(error)
    console.error('[ErrorBoundary] Caught error:', error)
  }

  return (
    <ErrorBoundary onError={handleError}>
      <SessionProvider>
        <QueryProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </QueryProvider>
      </SessionProvider>
    </ErrorBoundary>
  )
}
