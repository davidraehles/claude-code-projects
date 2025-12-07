/**
 * usePersistedReducer - Hook for reducers with localStorage persistence
 *
 * Implements ARCH-010: State persistence layer
 */

import { useReducer, useEffect, useCallback, Reducer, useRef } from 'react'

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
  /** Optional: name for Redux DevTools (enables DevTools integration) */
  devToolsName?: string
}

interface PersistedState<S> {
  version: number
  state: S
}

// Redux DevTools Extension API types
interface ReduxDevToolsExtension {
  connect(options?: Record<string, unknown>): DevToolsConnection
}

interface DevToolsConnection {
  subscribe(listener: (message: Record<string, unknown>) => void): () => void
  unsubscribe(): void
  send(action: Record<string, unknown>, state: unknown): void
  init(state: unknown): void
}

declare global {
  interface Window {
    __REDUX_DEVTOOLS_EXTENSION__?: ReduxDevToolsExtension
  }
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
    devToolsName,
  } = options

  const devToolsRef = useRef<DevToolsConnection | null>(null)
  const isTimeTravel = useRef(false)

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

  // Connect to Redux DevTools (ARCH-011)
  useEffect(() => {
    if (
      !devToolsName ||
      process.env.NODE_ENV !== 'development' ||
      typeof window === 'undefined' ||
      !window.__REDUX_DEVTOOLS_EXTENSION__
    ) {
      return
    }

    try {
      const devTools = window.__REDUX_DEVTOOLS_EXTENSION__.connect({
        name: devToolsName,
        features: {
          pause: true,
          lock: true,
          persist: true,
          export: true,
          import: 'custom',
          jump: true,
          skip: true,
          reorder: true,
          dispatch: true,
        },
      })

      devToolsRef.current = devTools
      devTools.init(state)

      const unsubscribe = devTools.subscribe((message) => {
        if (message.type === 'DISPATCH') {
          isTimeTravel.current = true
        }
      })

      return () => {
        unsubscribe()
        devTools.unsubscribe()
      }
    } catch (error) {
      console.warn(`[usePersistedReducer] Error connecting to DevTools:`, error)
    }
  }, [devToolsName])

  // Send updates to DevTools
  useEffect(() => {
    if (devToolsRef.current && !isTimeTravel.current) {
      devToolsRef.current.send({ type: '@@STATE_UPDATE' }, state)
    }
    isTimeTravel.current = false
  }, [state])

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

  // Wrap dispatch to send actions to DevTools
  const enhancedDispatch = useCallback(
    (action: A) => {
      if (devToolsRef.current) {
        devToolsRef.current.send(action, state)
      }
      dispatch(action)
    },
    [state]
  )

  return [state, devToolsName ? enhancedDispatch : dispatch]
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
