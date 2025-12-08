/**
 * Client-side layout wrapper with error boundary and auth context.
 * Separates client components from server layout.
 */

'use client'

import { ReactNode, useEffect } from 'react'
import { SessionProvider } from 'next-auth/react'
import { ErrorBoundary } from './ErrorBoundary'
import { AuthProvider } from '@/contexts/AuthContext'
import { QueryProvider } from '@/providers/QueryProvider'
import { SmoothScrollProvider } from '@/lib/animations/smooth-scroll'
import { ScrollProgressIndicator } from '@/components/ui/progress-indicator'

interface ClientLayoutProps {
  children: ReactNode
}

export function ClientLayout({ children }: ClientLayoutProps) {
  const handleError = (error: Error) => {
    // In production, log to error tracking service
    // Example: Sentry.captureException(error)
    console.error('[ErrorBoundary] Caught error:', error)
  }

  // Register Service Worker for offline functionality
  useEffect(() => {
    if ('serviceWorker' in navigator && typeof window !== 'undefined') {
      const registerServiceWorker = async () => {
        try {
          const registration = await navigator.serviceWorker.register('/sw.js', {
            scope: '/',
          })

          console.log('[Service Worker] Registered successfully:', registration.scope)

          // Check for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  console.log('[Service Worker] New version available')
                  // Could show a toast notification here to refresh
                }
              })
            }
          })

          // Handle messages from Service Worker
          navigator.serviceWorker.addEventListener('message', (event) => {
            console.log('[Service Worker] Message received:', event.data)

            if (event.data.type === 'WAITLIST_SYNC_COMPLETE') {
              console.log(
                `[Service Worker] Sync complete: ${event.data.successful} successful, ${event.data.failed} failed`
              )
              // Could dispatch a custom event or update state here
            }
          })
        } catch (error) {
          console.error('[Service Worker] Registration failed:', error)
        }
      }

      registerServiceWorker()
    }
  }, [])

  return (
    <ErrorBoundary onError={handleError}>
      <SessionProvider>
        <QueryProvider>
          <AuthProvider>
            <SmoothScrollProvider>
              <ScrollProgressIndicator />
              {children}
            </SmoothScrollProvider>
          </AuthProvider>
        </QueryProvider>
      </SessionProvider>
    </ErrorBoundary>
  )
}
