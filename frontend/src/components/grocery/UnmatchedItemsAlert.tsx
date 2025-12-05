'use client'

/**
 * UnmatchedItemsAlert component
 *
 * Displays items that couldn't be matched with Knuspr products.
 * Features:
 * - Warning banner with amber/yellow color scheme
 * - Collapsible/expandable list of unmatched items
 * - Suggestions for handling unmatched items
 * - Option to dismiss individual items or the entire alert
 * - Link to Knuspr for manual search
 * - Full accessibility support (ARIA roles, keyboard navigation)
 * - Persists dismissal state in localStorage
 */

import React, { useState } from 'react'
import { AlertTriangle, ChevronDown, ChevronUp, X, ExternalLink, Search } from 'lucide-react'

export interface UnmatchedItemsAlertProps {
  items: string[]
  cartId: number
  className?: string
}

// Helper function to load dismissed items from localStorage
function loadDismissedItems(storageKey: string): Set<string> {
  if (typeof window === 'undefined') {
    return new Set()
  }

  try {
    const stored = localStorage.getItem(storageKey)
    if (stored) {
      return new Set(JSON.parse(stored))
    }
  } catch (error) {
    console.error('Failed to load dismissed items from localStorage:', error)
  }

  return new Set()
}

// Helper function to load alert dismissed state from localStorage
function loadAlertDismissed(alertStorageKey: string): boolean {
  if (typeof window === 'undefined') {
    return false
  }

  try {
    const alertDismissed = localStorage.getItem(alertStorageKey)
    return alertDismissed === 'true'
  } catch (error) {
    console.error('Failed to load alert dismissed state from localStorage:', error)
  }

  return false
}

export function UnmatchedItemsAlert({ items, cartId, className = '' }: UnmatchedItemsAlertProps) {
  // Storage keys for persisting dismissal state
  const storageKey = `unmatched-items-dismissed-${cartId}`
  const alertStorageKey = `unmatched-alert-dismissed-${cartId}`

  // State with lazy initialization from localStorage
  const [isExpanded, setIsExpanded] = useState(true)
  const [dismissedItems, setDismissedItems] = useState<Set<string>>(() =>
    loadDismissedItems(storageKey)
  )
  const [isAlertDismissed, setIsAlertDismissed] = useState(() =>
    loadAlertDismissed(alertStorageKey)
  )

  // Save dismissed items to localStorage
  const saveDismissedItems = (newDismissedItems: Set<string>) => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(storageKey, JSON.stringify(Array.from(newDismissedItems)))
      } catch (error) {
        console.error('Failed to save dismissed items to localStorage:', error)
      }
    }
  }

  // Handle dismissing individual items
  const handleDismissItem = (item: string) => {
    const newDismissed = new Set(dismissedItems)
    newDismissed.add(item)
    setDismissedItems(newDismissed)
    saveDismissedItems(newDismissed)
  }

  // Handle dismissing entire alert
  const handleDismissAlert = () => {
    setIsAlertDismissed(true)
    if (typeof window !== 'undefined') {
      localStorage.setItem(alertStorageKey, 'true')
    }
  }

  // Filter out dismissed items
  const visibleItems = items.filter((item) => !dismissedItems.has(item))

  // Don't render if no items or alert is dismissed
  if (visibleItems.length === 0 || isAlertDismissed) {
    return null
  }

  return (
    <div
      className={`bg-amber-50 border border-amber-300 rounded-lg ${className}`}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      {/* Header */}
      <div className="p-4 sm:p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle
            className="h-6 w-6 text-amber-600 flex-shrink-0 mt-0.5"
            aria-hidden="true"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h3 className="text-base sm:text-lg font-semibold text-amber-900">
                  {visibleItems.length} Item{visibleItems.length !== 1 ? 's' : ''} Could Not Be Matched
                </h3>
                <p className="text-sm text-amber-800 mt-1">
                  These ingredients are not available in Knuspr or could not be automatically matched.
                  You can search for them manually or find alternative products.
                </p>
              </div>
              <button
                onClick={handleDismissAlert}
                className="text-amber-700 hover:text-amber-900 hover:bg-amber-100 rounded-lg p-1.5 transition-colors flex-shrink-0"
                aria-label="Dismiss this alert"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Expand/Collapse Button */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-amber-900 hover:text-amber-950 transition-colors"
              aria-expanded={isExpanded}
              aria-controls="unmatched-items-list"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="h-4 w-4" aria-hidden="true" />
                  <span>Hide Items</span>
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" aria-hidden="true" />
                  <span>Show Items ({visibleItems.length})</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Expandable Items List */}
        {isExpanded && (
          <div
            id="unmatched-items-list"
            className="mt-4 space-y-2"
          >
            {visibleItems.map((item, index) => (
              <div
                key={`${item}-${index}`}
                className="bg-white border border-amber-200 rounded-lg p-3 sm:p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <span className="text-lg flex-shrink-0" aria-hidden="true">
                      🔍
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 break-words">{item}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        Not found in Knuspr catalog
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <a
                      href={`https://www.knuspr.cz/search?q=${encodeURIComponent(item)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors"
                      aria-label={`Search for ${item} in Knuspr`}
                    >
                      <Search className="h-3 w-3" />
                      <span className="hidden sm:inline">Search</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                    <button
                      onClick={() => handleDismissItem(item)}
                      className="p-1.5 text-amber-700 hover:text-amber-900 hover:bg-amber-100 rounded-lg transition-colors"
                      aria-label={`Mark ${item} as handled`}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Suggestions Footer */}
      <div className="bg-amber-100 border-t border-amber-300 px-4 sm:px-6 py-3 rounded-b-lg">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-start gap-2">
            <span className="text-base flex-shrink-0" aria-hidden="true">
              💡
            </span>
            <p className="text-xs sm:text-sm text-amber-900">
              <span className="font-semibold">Tip:</span> Click the search button to find alternatives in Knuspr,
              or manually add these items during checkout.
            </p>
          </div>
          <a
            href="https://www.knuspr.cz"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-xs sm:text-sm font-medium text-amber-900 hover:text-amber-950 transition-colors flex-shrink-0"
          >
            <span>Browse Knuspr</span>
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </div>
    </div>
  )
}

export default UnmatchedItemsAlert
