/**
 * MVI Pattern Core Types
 * 
 * Model-View-Intent is a unidirectional data flow pattern where:
 * - Intent: User actions that express intent to change state
 * - Model: Single immutable state tree representing UI state
 * - View: Pure function of the model that renders UI
 */

import { Dispatch } from 'react';

/**
 * Intent - Represents a user action or system event
 * All intents have a type and optional payload
 */
export interface Intent<TType extends string = string, TPayload = unknown> {
  type: TType;
  payload?: TPayload;
  meta?: {
    timestamp: number;
    source?: string;
  };
}

/**
 * Intent creator function type
 */
export type IntentCreator<TType extends string, TPayload = void> = 
  TPayload extends void
    ? () => Intent<TType, undefined>
    : (payload: TPayload) => Intent<TType, TPayload>;

/**
 * Model - Represents the complete UI state for a feature
 */
export interface Model<TState = unknown> {
  state: TState;
  isLoading?: boolean;
  error?: Error | null;
}

/**
 * Selector - Pure function that derives data from the model
 */
export type Selector<TState, TResult> = (state: TState) => TResult;

/**
 * Reducer - Pure function that produces new state from intent
 */
export type Reducer<TState, TIntent extends Intent> = (
  state: TState,
  intent: TIntent
) => TState;

/**
 * Middleware - Intercepts intents for side effects
 */
export type Middleware<TState, TIntent extends Intent> = (
  store: MiddlewareStore<TState, TIntent>
) => (next: Dispatch<TIntent>) => (intent: TIntent) => void | Promise<void>;

/**
 * Middleware store API
 */
export interface MiddlewareStore<TState, TIntent extends Intent> {
  getState: () => TState;
  dispatch: Dispatch<TIntent>;
}

/**
 * MVI Store - Combines state, dispatch, and selectors
 */
export interface MVIStore<TState, TIntent extends Intent> {
  state: TState;
  dispatch: Dispatch<TIntent>;
  select: <TResult>(selector: Selector<TState, TResult>) => TResult;
}

/**
 * MVI Configuration
 */
export interface MVIConfig<TState, TIntent extends Intent> {
  name: string;
  initialState: TState;
  reducer: Reducer<TState, TIntent>;
  middleware?: Middleware<TState, TIntent>[];
  persist?: {
    key: string;
    storage?: Storage;
  };
  devtools?: boolean;
}

/**
 * View Props - Props passed to view components
 */
export interface ViewProps<TState, TIntent extends Intent> {
  model: TState;
  dispatch: Dispatch<TIntent>;
}
