/**
 * usePersistedReducer - Hook for reducers with localStorage persistence
 *
 * Implements ARCH-010: State persistence layer
 */

import { useReducer, useEffect, useCallback, Reducer } from 'react'

interface PersistedReducerOptions<S> {
  /** LocalStorage key for persisting state */
  key: string
  /** Initial state if no persisted state exists */
  initialState: S
  /** Optional: version number for state schema migrations */
  version?: number
  /** Optional: custom serializer (defaults to JSON.stringify) */
  serialize?: (state: S) => string
  /** Optional: custom deserializer (defaults to JSON.parse) */
  deserialize?: (json: string) => S
  /** Optional: validation function to check if persisted state is valid */
  validate?: (state: unknown) => state is S
}

interface PersistedState<S> {
  version: number
  state: S
}

/**
 * useReducer with automatic localStorage persistence.
 *
 * Features:
 * - Automatically saves state to localStorage on every change
 * - Restores state on mount
 * - Supports versioning for schema migrations
 * - Type-safe with validation
 * - Handles localStorage errors gracefully
 *
 * @example
 * const [state, dispatch] = usePersistedReducer({
 *   key: 'grocery-cart',
 *   reducer: groceryCartReducer,
 *   initialState: getInitialCartState(),
 *   version: 1,
 * })
 */
export function usePersistedReducer<S, A>(
  reducer: Reducer<S, A>,
  options: PersistedReducerOptions<S>
): [S, React.Dispatch<A>] {
  const {
    key,
    initialState,
    version = 1,
    serialize = JSON.stringify,
    deserialize = JSON.parse,
    validate,
  } = options

  // Load initial state from localStorage
  const loadPersistedState = useCallback((): S => {
    if (typeof window === 'undefined') {
      return initialState
    }

    try {
      const serialized = localStorage.getItem(key)
      if (!serialized) {
        return initialState
      }

      const persisted: PersistedState<string> = JSON.parse(serialized)

      // Check version - discard old versions
      if (persisted.version !== version) {
        console.log(`[usePersistedReducer] Version mismatch for "${key}". Discarding old state.`)
        localStorage.removeItem(key)
        return initialState
      }

      // Deserialize the state
      const deserializedState = deserialize
        ? deserialize(persisted.state)
        : JSON.parse(persisted.state)

      // Validate state structure if validator provided
      if (validate && !validate(deserializedState)) {
        console.warn(`[usePersistedReducer] Invalid state structure for "${key}". Using initial state.`)
        localStorage.removeItem(key)
        return initialState
      }

      return deserializedState
    } catch (error) {
      console.error(`[usePersistedReducer] Error loading state for "${key}":`, error)
      return initialState
    }
  }, [key, initialState, version, deserialize, validate])

  // Initialize reducer with persisted state
  const [state, dispatch] = useReducer(reducer, initialState, loadPersistedState)

  // Persist state to localStorage whenever it changes
  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    try {
      // Use custom serializer if provided, otherwise default to JSON
      const stateToSerialize = serialize ? serialize(state) : JSON.stringify(state)
      const persisted: PersistedState<string> = {
        version,
        state: stateToSerialize,
      }
      const serialized = JSON.stringify(persisted)
      localStorage.setItem(key, serialized)
    } catch (error) {
      console.error(`[usePersistedReducer] Error saving state for "${key}":`, error)
    }
  }, [key, state, version, serialize])

  return [state, dispatch]
}

/**
 * Clear persisted state from localStorage.
 *
 * @example
 * clearPersistedState('grocery-cart')
 */
export function clearPersistedState(key: string): void {
  if (typeof window === 'undefined') {
    return
  }

  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.error(`[clearPersistedState] Error clearing "${key}":`, error)
  }
}
