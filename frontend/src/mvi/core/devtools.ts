/**
 * MVI DevTools - Development tools for debugging MVI state
 */

import type { Intent, Middleware } from './types';

interface DevToolsState<TState, TIntent extends Intent> {
  history: Array<{
    intent: TIntent;
    state: TState;
    timestamp: number;
  }>;
  currentIndex: number;
}

/**
 * DevTools middleware with time-travel debugging
 */
export function createDevToolsMiddleware<TState, TIntent extends Intent>(
  name: string,
  maxHistory: number = 50
): Middleware<TState, TIntent> {
  const devToolsState: DevToolsState<TState, TIntent> = {
    history: [],
    currentIndex: -1,
  };

  // Expose to window for debugging
  if (typeof window !== 'undefined') {
    (window as any).__MVI_DEVTOOLS__ = (window as any).__MVI_DEVTOOLS__ || {};
    (window as any).__MVI_DEVTOOLS__[name] = {
      getHistory: () => devToolsState.history,
      getCurrentIndex: () => devToolsState.currentIndex,
      getState: (index?: number) => {
        const idx = index ?? devToolsState.currentIndex;
        return devToolsState.history[idx]?.state;
      },
      clearHistory: () => {
        devToolsState.history = [];
        devToolsState.currentIndex = -1;
      },
    };
  }

  return (store) => (next) => async (intent) => {
    const prevState = store.getState();
    
    next(intent);
    
    const nextState = store.getState();

    // Add to history
    devToolsState.history.push({
      intent,
      state: nextState,
      timestamp: Date.now(),
    });

    devToolsState.currentIndex = devToolsState.history.length - 1;

    // Trim history if exceeds max
    if (devToolsState.history.length > maxHistory) {
      devToolsState.history.shift();
      devToolsState.currentIndex = Math.max(0, devToolsState.currentIndex - 1);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.groupCollapsed(
        `%c[${name}] ${intent.type}`,
        'color: #4CAF50; font-weight: bold;'
      );
      console.log('%cPrevious State:', 'color: #9E9E9E; font-weight: bold;', prevState);
      console.log('%cIntent:', 'color: #2196F3; font-weight: bold;', intent);
      console.log('%cNext State:', 'color: #4CAF50; font-weight: bold;', nextState);
      console.log(
        '%cState Diff:',
        'color: #FF9800; font-weight: bold;',
        computeDiff(prevState, nextState)
      );
      console.groupEnd();
    }
  };
}

/**
 * Compute diff between two states
 */
function computeDiff<T>(prev: T, next: T): Record<string, { from: unknown; to: unknown }> {
  const diff: Record<string, { from: unknown; to: unknown }> = {};

  if (typeof prev !== 'object' || typeof next !== 'object' || prev === null || next === null) {
    return { root: { from: prev, to: next } };
  }

  const allKeys = new Set([...Object.keys(prev), ...Object.keys(next)]);

  allKeys.forEach((key) => {
    const prevValue = (prev as any)[key];
    const nextValue = (next as any)[key];

    if (prevValue !== nextValue) {
      diff[key] = { from: prevValue, to: nextValue };
    }
  });

  return diff;
}

/**
 * Performance monitoring middleware
 */
export function createPerformanceMiddleware<TState, TIntent extends Intent>(
  name: string,
  threshold: number = 16 // 16ms = 60fps
): Middleware<TState, TIntent> {
  return () => (next) => async (intent) => {
    const startTime = performance.now();

    next(intent);

    const endTime = performance.now();
    const duration = endTime - startTime;

    if (duration > threshold) {
      console.warn(
        `[${name}] Slow intent detected: ${intent.type} took ${duration.toFixed(2)}ms`
      );
    }

    if (process.env.NODE_ENV === 'development') {
      performance.measure(`${name}:${intent.type}`, {
        start: startTime,
        end: endTime,
      });
    }
  };
}
