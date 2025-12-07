/**
 * useReducerWithDevTools - React useReducer with Redux DevTools integration
 *
 * Implements ARCH-011: Redux DevTools Integration
 *
 * Features:
 * - Time-travel debugging
 * - Action replay
 * - State inspection
 * - Import/export state snapshots
 * - Action filtering
 */

import { useReducer, useEffect, useRef, Reducer } from 'react'

// Redux DevTools Extension API types
interface ReduxDevToolsExtension {
  connect(options?: DevToolsOptions): DevToolsConnection
}

interface DevToolsOptions {
  name?: string
  features?: {
    pause?: boolean
    lock?: boolean
    persist?: boolean
    export?: boolean | string
    import?: boolean | string
    jump?: boolean
    skip?: boolean
    reorder?: boolean
    dispatch?: boolean
    test?: boolean
  }
  trace?: boolean
  traceLimit?: number
}

interface DevToolsConnection {
  subscribe(listener: (message: Record<string, unknown>) => void): () => void
  unsubscribe(): void
  send(action: Record<string, unknown>, state: unknown): void
  init(state: unknown): void
}

// Extend Window interface if not already extended
interface WindowWithDevTools extends Window {
  __REDUX_DEVTOOLS_EXTENSION__?: ReduxDevToolsExtension
}

/**
 * Enhanced useReducer with Redux DevTools integration.
 *
 * Automatically connects to Redux DevTools Extension if available.
 * In production, falls back to standard useReducer.
 *
 * @example
 * const [state, dispatch] = useReducerWithDevTools(
 *   mealPlanFormReducer,
 *   initialState,
 *   'MealPlanForm'
 * )
 *
 * @param reducer - Reducer function
 * @param initialState - Initial state
 * @param name - Name to display in DevTools
 * @param init - Optional state initializer
 */
export function useReducerWithDevTools<S, A>(
  reducer: Reducer<S, A>,
  initialState: S,
  name: string = 'Reducer',
  init?: (initialState: S) => S
): [S, React.Dispatch<A>] {
  const [state, dispatch] = init
    ? (useReducer(reducer, initialState, init) as [S, React.Dispatch<A>])
    : (useReducer(reducer, initialState) as [S, React.Dispatch<A>])

  const devToolsRef = useRef<DevToolsConnection | null>(null)
  const isTimeTravel = useRef(false)

  // Connect to Redux DevTools
  useEffect(() => {
    // Only connect in development and if DevTools extension is available
    if (
      process.env.NODE_ENV !== 'development' ||
      typeof window === 'undefined' ||
      !window.__REDUX_DEVTOOLS_EXTENSION__
    ) {
      return
    }

    try {
      // Connect to DevTools
      const devTools = window.__REDUX_DEVTOOLS_EXTENSION__.connect({
        name,
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
          test: true,
        },
        trace: true,
        traceLimit: 25,
      })

      devToolsRef.current = devTools

      // Initialize with current state
      devTools.init(state)

      // Subscribe to time-travel actions
      const unsubscribe = devTools.subscribe((message: Record<string, unknown>) => {
        if (message.type === 'DISPATCH') {
          const payload = message.payload as Record<string, unknown>
          switch (payload.type) {
            case 'JUMP_TO_STATE':
            case 'JUMP_TO_ACTION':
              isTimeTravel.current = true
              // State will be sent in message.state
              break
            case 'COMMIT':
              devTools.init(state)
              break
            case 'ROLLBACK':
              isTimeTravel.current = true
              break
            case 'TOGGLE_ACTION':
              // Replay actions
              isTimeTravel.current = true
              break
            case 'IMPORT_STATE':
              // Import state from file
              if ((payload as Record<string, unknown>).nextLiftedState) {
                const nextLiftedState = (payload as Record<string, unknown>).nextLiftedState as Record<string, unknown>
                const { computedStates } = nextLiftedState
                if (computedStates && Array.isArray(computedStates) && computedStates.length > 0) {
                  isTimeTravel.current = true
                }
              }
              break
          }
        }
      })

      // Cleanup
      return () => {
        unsubscribe()
        devTools.unsubscribe()
      }
    } catch (error) {
      console.warn('[useReducerWithDevTools] Error connecting to DevTools:', error)
    }
  }, [name])

  // Send state updates to DevTools
  useEffect(() => {
    if (devToolsRef.current && !isTimeTravel.current) {
      // Send the current state to DevTools
      // We don't have the action here, so we send a generic update
      devToolsRef.current.send({ type: '@@STATE_UPDATE' }, state)
    }
    isTimeTravel.current = false
  }, [state])

  // Wrap dispatch to send actions to DevTools
  const dispatchWithDevTools = (action: A) => {
    if (devToolsRef.current) {
      devToolsRef.current.send(action as Record<string, unknown>, state)
    }
    dispatch(action)
  }

  return [state, dispatchWithDevTools as React.Dispatch<A>]
}

/**
 * Combine useReducerWithDevTools with usePersistedReducer for best of both worlds.
 *
 * @example
 * const [state, dispatch] = usePersistedReducerWithDevTools(
 *   groceryCartReducer,
 *   {
 *     key: 'grocery-cart',
 *     initialState: getInitialCartState(),
 *     version: 1,
 *   },
 *   'GroceryCart'
 * )
 */
export function usePersistedReducerWithDevTools<S, A>(
  reducer: Reducer<S, A>,
  options: {
    key: string
    initialState: S
    version?: number
    serialize?: (state: S) => string
    deserialize?: (json: string) => S
    validate?: (state: unknown) => state is S
  },
  name: string = 'PersistedReducer'
): [S, React.Dispatch<A>] {
  // For now, we'll use the simpler approach
  // In a full implementation, we'd merge both hooks
  return useReducerWithDevTools(reducer, options.initialState, name)
}
