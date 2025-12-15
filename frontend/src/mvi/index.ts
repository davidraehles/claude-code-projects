/**
 * MVI Pattern - Model-View-Intent
 * 
 * A unidirectional data flow architecture for React applications
 * 
 * @see https://cycle.js.org/model-view-intent.html
 */

// Core exports
export * from './core/types';
export * from './core/createMVI';
export * from './core/middleware';
export * from './core/devtools';

// Utility exports
export * from './utils/testing';

// Re-export for convenience
export { createMVI, createIntent, loadPersistedState } from './core/createMVI';
export type { MVIStore, Intent, Selector, Middleware } from './core/types';
