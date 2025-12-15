/**
 * MVI Middleware - Common middleware implementations
 */

import type { Middleware, Intent } from './types';

/**
 * Logger middleware - Logs all intents in development
 */
export function createLoggerMiddleware<TState, TIntent extends Intent>(
  name: string
): Middleware<TState, TIntent> {
  return (store) => (next) => async (intent) => {
    if (process.env.NODE_ENV === 'development') {
      const prevState = store.getState();
      console.log(`[${name}] Intent:`, intent.type, intent.payload);
      
      next(intent);
      
      const nextState = store.getState();
      console.log(`[${name}] State transition:`, {
        from: prevState,
        to: nextState,
      });
    } else {
      next(intent);
    }
  };
}

/**
 * Analytics middleware - Tracks intents for analytics
 */
export function createAnalyticsMiddleware<TState, TIntent extends Intent>(
  track: (event: string, properties?: Record<string, unknown>) => void
): Middleware<TState, TIntent> {
  return () => (next) => async (intent) => {
    // Track intent before processing
    track(intent.type, {
      payload: intent.payload,
      timestamp: intent.meta?.timestamp || Date.now(),
    });

    next(intent);
  };
}

/**
 * Validation middleware - Validates intent payloads
 */
export function createValidationMiddleware<TState, TIntent extends Intent>(
  validators: Partial<Record<TIntent['type'], (payload: unknown) => boolean>>
): Middleware<TState, TIntent> {
  return () => (next) => async (intent) => {
    const validator = validators[intent.type];
    
    if (validator && !validator(intent.payload)) {
      console.error(`[Validation] Invalid payload for ${intent.type}:`, intent.payload);
      return;
    }

    next(intent);
  };
}

/**
 * Async middleware - Handles async operations
 */
export function createAsyncMiddleware<TState, TIntent extends Intent>(): Middleware<
  TState,
  TIntent
> {
  return () => (next) => async (intent) => {
    // Support async intents
    if (intent.payload instanceof Promise) {
      try {
        const result = await intent.payload;
        next({
          ...intent,
          payload: result,
        } as TIntent);
      } catch (error) {
        console.error(`[Async] Error in ${intent.type}:`, error);
        // Dispatch error intent
        next({
          type: `${intent.type}_ERROR`,
          payload: error,
        } as TIntent);
      }
    } else {
      next(intent);
    }
  };
}

/**
 * Debounce middleware - Debounces specific intents
 */
export function createDebounceMiddleware<TState, TIntent extends Intent>(
  intentTypes: Set<TIntent['type']>,
  delay: number = 300
): Middleware<TState, TIntent> {
  const timeouts = new Map<TIntent['type'], NodeJS.Timeout>();

  return () => (next) => async (intent) => {
    if (intentTypes.has(intent.type)) {
      const existingTimeout = timeouts.get(intent.type);
      if (existingTimeout) {
        clearTimeout(existingTimeout);
      }

      const timeout = setTimeout(() => {
        next(intent);
        timeouts.delete(intent.type);
      }, delay);

      timeouts.set(intent.type, timeout);
    } else {
      next(intent);
    }
  };
}

/**
 * Persistence middleware - Saves state changes to storage
 */
export function createPersistenceMiddleware<TState, TIntent extends Intent>(
  key: string,
  storage: Storage = localStorage
): Middleware<TState, TIntent> {
  return (store) => (next) => async (intent) => {
    next(intent);

    // Save state after intent is processed
    try {
      const state = store.getState();
      storage.setItem(key, JSON.stringify(state));
    } catch (error) {
      console.error(`[Persistence] Failed to save state for ${key}:`, error);
    }
  };
}

/**
 * Compose multiple middleware into one
 */
export function composeMiddleware<TState, TIntent extends Intent>(
  ...middleware: Middleware<TState, TIntent>[]
): Middleware<TState, TIntent> {
  return (store) => {
    const chain = middleware.map(m => m(store));
    return (next) => {
      return chain.reduceRight(
        (composed, middlewareFn) => middlewareFn(composed),
        next
      );
    };
  };
}
