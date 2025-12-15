/**
 * MVI Factory - Creates MVI store with middleware support
 */

import { useReducer, useMemo, useCallback, Dispatch, useEffect } from 'react';
import type { Intent, Reducer, Middleware, MVIConfig, MVIStore, Selector } from './types';

/**
 * Create a middleware-enhanced dispatch function
 */
function applyMiddleware<TState, TIntent extends Intent>(
  dispatch: Dispatch<TIntent>,
  middleware: Middleware<TState, TIntent>[],
  getState: () => TState
): Dispatch<TIntent> {
  if (middleware.length === 0) {
    return dispatch;
  }

  const store = { getState, dispatch };
  const chain = middleware.map(m => m(store));
  
  return chain.reduceRight(
    (next, middlewareFn) => middlewareFn(next),
    dispatch
  );
}

/**
 * Create MVI hook for a feature module
 */
export function createMVI<TState, TIntent extends Intent>(
  config: MVIConfig<TState, TIntent>
) {
  return function useMVI(): MVIStore<TState, TIntent> {
    // Core reducer with development logging
    const enhancedReducer: Reducer<TState, TIntent> = useCallback(
      (state: TState, intent: TIntent) => {
        if (process.env.NODE_ENV === 'development' && config.devtools !== false) {
          console.groupCollapsed(`[${config.name}] ${intent.type}`);
          console.log('Previous State:', state);
          console.log('Intent:', intent);
        }

        const nextState = config.reducer(state, intent);

        if (process.env.NODE_ENV === 'development' && config.devtools !== false) {
          console.log('Next State:', nextState);
          console.groupEnd();
        }

        return nextState;
      },
      [config.reducer, config.name, config.devtools]
    );

    // Initialize reducer
    const [state, baseDispatch] = useReducer(enhancedReducer, config.initialState);

    // Memoize getState function
    const getState = useCallback(() => state, [state]);

    // Apply middleware to dispatch
    const dispatch = useMemo(() => {
      if (!config.middleware || config.middleware.length === 0) {
        return baseDispatch;
      }
      return applyMiddleware(baseDispatch, config.middleware, getState);
    }, [baseDispatch, config.middleware, getState]);

    // State persistence
    useEffect(() => {
      if (config.persist) {
        const { key, storage = localStorage } = config.persist;
        try {
          storage.setItem(key, JSON.stringify(state));
        } catch (error) {
          console.error(`[${config.name}] Failed to persist state:`, error);
        }
      }
    }, [state, config.persist, config.name]);

    // Selector function with memoization
    const select = useCallback(
      <TResult,>(selector: Selector<TState, TResult>): TResult => {
        return selector(state);
      },
      [state]
    );

    return {
      state,
      dispatch,
      select,
    };
  };
}

/**
 * Load persisted state from storage
 */
export function loadPersistedState<TState>(
  key: string,
  initialState: TState,
  storage: Storage = localStorage
): TState {
  try {
    const serialized = storage.getItem(key);
    if (serialized === null) {
      return initialState;
    }
    return JSON.parse(serialized) as TState;
  } catch (error) {
    console.error(`Failed to load persisted state for ${key}:`, error);
    return initialState;
  }
}

/**
 * Create intent creator helper
 */
export function createIntent<TType extends string, TPayload = void>(
  type: TType
): TPayload extends void
  ? () => Intent<TType, undefined>
  : (payload: TPayload) => Intent<TType, TPayload> {
  return ((payload?: TPayload) => ({
    type,
    payload: payload as TPayload,
    meta: {
      timestamp: Date.now(),
    },
  })) as any;
}
