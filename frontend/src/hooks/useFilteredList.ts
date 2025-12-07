/**
 * useFilteredList - Custom hook for client-side list filtering
 *
 * Implements ARCH-007: Extract common filtering pattern
 */

import { useEffect, useState, useMemo } from 'react'

export interface FilterOptions<T> {
  /** List of items to filter */
  items: T[]
  /** Search query string */
  query: string
  /** Function to extract searchable text from an item */
  getSearchableText: (item: T) => string[]
  /** Optional: debounce delay in milliseconds */
  debounceMs?: number
}

/**
 * Hook for filtering a list based on a search query.
 *
 * @example
 * const { filtered, setQuery, query } = useFilteredList({
 *   items: recipes,
 *   query: '',
 *   getSearchableText: (recipe) => [
 *     recipe.title,
 *     ...recipe.ingredients,
 *     ...(recipe.dietary_tags || [])
 *   ]
 * })
 */
export function useFilteredList<T>(options: FilterOptions<T>) {
  const { items, query, getSearchableText } = options
  const [filtered, setFiltered] = useState<T[]>(items)

  useEffect(() => {
    if (!query.trim()) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFiltered(items)
      return
    }

    const lowercaseQuery = query.toLowerCase()
    const results = items.filter((item) => {
      const searchableTexts = getSearchableText(item)
      return searchableTexts.some((text) =>
        text.toLowerCase().includes(lowercaseQuery)
      )
    })

    setFiltered(results)
  }, [query, items, getSearchableText])

  return filtered
}

/**
 * Hook for debouncing a value.
 * Useful for search inputs to reduce unnecessary filtering.
 *
 * @example
 * const debouncedQuery = useDebounce(searchQuery, 300)
 */
export function useDebounce<T>(value: T, delayMs: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delayMs)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delayMs])

  return debouncedValue
}
