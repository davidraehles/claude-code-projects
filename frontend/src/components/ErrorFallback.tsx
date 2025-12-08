/**
 * Error Fallback UI component.
 * Displays user-friendly error messages with recovery options.
 */

'use client'

import { ErrorInfo } from 'react'
import { Button } from './ui/button'

interface ErrorFallbackProps {
  error: Error | null
  errorInfo?: ErrorInfo | null
  onReset?: () => void
}

export function ErrorFallback({ error, errorInfo, onReset }: ErrorFallbackProps) {
  const isDevelopment = process.env.NODE_ENV === 'development'

  const handleReload = () => {
    window.location.reload()
  }

  const handleGoHome = () => {
    window.location.href = '/'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Error Card */}
        <div className="bg-white rounded-xl shadow-lg border border-red-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-500 to-red-600 px-6 py-8 text-white">
            <div className="flex items-center space-x-4">
              <div className="text-5xl">⚠️</div>
              <div>
                <h1 className="text-2xl font-bold mb-1">Something went wrong</h1>
                <p className="text-red-100">
                  We encountered an unexpected error. Don&apos;t worry, your data is safe.
                </p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* User-friendly message */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">What can you do?</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Try refreshing the page</li>
                <li>• Go back to the home page and try again</li>
                <li>• Clear your browser cache if the problem persists</li>
                <li>• Contact support if you continue to see this error</li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              {onReset && (
                <Button
                  variant="primary"
                  onClick={onReset}
                  className="flex-1"
                >
                  Try Again
                </Button>
              )}
              <Button
                variant="outline"
                onClick={handleReload}
                className="flex-1"
              >
                Reload Page
              </Button>
              <Button
                variant="ghost"
                onClick={handleGoHome}
                className="flex-1"
              >
                Go Home
              </Button>
            </div>

            {/* Development-only error details */}
            {isDevelopment && error && (
              <details className="mt-6">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700 hover:text-gray-900">
                  Technical Details (Development Only)
                </summary>
                <div className="mt-4 space-y-4">
                  {/* Error Message */}
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h4 className="font-mono text-xs font-semibold text-red-900 mb-2">
                      Error Message:
                    </h4>
                    <pre className="text-xs text-red-800 overflow-x-auto">
                      {error.message}
                    </pre>
                  </div>

                  {/* Error Stack */}
                  {error.stack && (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-mono text-xs font-semibold text-gray-900 mb-2">
                        Stack Trace:
                      </h4>
                      <pre className="text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
                        {error.stack}
                      </pre>
                    </div>
                  )}

                  {/* Component Stack */}
                  {errorInfo?.componentStack && (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-mono text-xs font-semibold text-gray-900 mb-2">
                        Component Stack:
                      </h4>
                      <pre className="text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
                        {errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}

            {/* Support Info */}
            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Need help?{' '}
                <a
                  href="mailto:support@mealplanner.com"
                  className="text-blue-600 hover:text-blue-700 font-semibold"
                >
                  Contact Support
                </a>
              </p>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-4 text-center text-sm text-gray-500">
          Error occurred at {new Date().toLocaleString()}
        </div>
      </div>
    </div>
  )
}
