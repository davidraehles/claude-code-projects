/**
 * MVI Testing Utilities
 */

import { renderHook } from '@testing-library/react';
import type { Intent, Reducer, MVIConfig } from '../core/types';
import { createMVI } from '../core/createMVI';

/**
 * Test helper to create a test MVI instance
 */
export function createTestMVI<TState, TIntent extends Intent>(
  config: Omit<MVIConfig<TState, TIntent>, 'name'> & { name?: string }
) {
  return createMVI({
    name: config.name || 'TestMVI',
    ...config,
    devtools: false, // Disable devtools in tests
  });
}

/**
 * Test reducer with a sequence of intents
 */
export function testReducerSequence<TState, TIntent extends Intent>(
  reducer: Reducer<TState, TIntent>,
  initialState: TState,
  intents: TIntent[]
): TState {
  return intents.reduce((state, intent) => reducer(state, intent), initialState);
}

/**
 * Create a mock dispatch function for testing
 */
export function createMockDispatch<TIntent extends Intent>(): {
  dispatch: jest.Mock<void, [TIntent]>;
  getDispatched: () => TIntent[];
  clear: () => void;
} {
  const dispatched: TIntent[] = [];

  const dispatch = jest.fn((intent: TIntent) => {
    dispatched.push(intent);
  });

  return {
    dispatch,
    getDispatched: () => [...dispatched],
    clear: () => {
      dispatched.length = 0;
      dispatch.mockClear();
    },
  };
}

/**
 * Test MVI hook with React Testing Library
 */
export function testMVIHook<TState, TIntent extends Intent>(
  config: MVIConfig<TState, TIntent>
) {
  const useMVI = createMVI(config);
  const { result } = renderHook(() => useMVI());

  return {
    getState: () => result.current.state,
    dispatch: (intent: TIntent) => result.current.dispatch(intent),
    select: result.current.select,
    rerender: () => renderHook(() => useMVI()),
  };
}

/**
 * Assert state equals expected
 */
export function assertState<TState>(
  actual: TState,
  expected: Partial<TState>,
  message?: string
) {
  Object.keys(expected).forEach((key) => {
    const actualValue = (actual as any)[key];
    const expectedValue = (expected as any)[key];

    if (actualValue !== expectedValue) {
      throw new Error(
        message ||
          `State mismatch for ${key}: expected ${JSON.stringify(
            expectedValue
          )}, got ${JSON.stringify(actualValue)}`
      );
    }
  });
}

/**
 * Create a test intent
 */
export function createTestIntent<TType extends string, TPayload = void>(
  type: TType,
  payload?: TPayload
): Intent<TType, TPayload> {
  return {
    type,
    payload: payload as TPayload,
    meta: {
      timestamp: Date.now(),
      source: 'test',
    },
  };
}
