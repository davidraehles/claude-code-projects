/**
 * API Endpoint Constants
 *
 * Centralized definition of all API endpoints to prevent typos and ensure consistency.
 * Use these constants throughout the application instead of hardcoded strings.
 */

/**
 * API version prefix
 */
const API_V1 = '/api/v1' as const;

/**
 * Authentication endpoints
 */
export const AUTH_ENDPOINTS = {
  LOGIN: `${API_V1}/auth/login`,
  REGISTER: `${API_V1}/auth/register`,
  REFRESH: `${API_V1}/auth/refresh`,
  ME: `${API_V1}/users/me`,
} as const;

/**
 * Recipe endpoints
 */
export const RECIPE_ENDPOINTS = {
  BASE: `${API_V1}/recipes`,
  LIST: (skip: number, limit: number) => `${API_V1}/recipes?skip=${skip}&limit=${limit}`,
  DETAIL: (id: number) => `${API_V1}/recipes/${id}`,
  CREATE: `${API_V1}/recipes`,
  UPDATE: (id: number) => `${API_V1}/recipes/${id}`,
  DELETE: (id: number) => `${API_V1}/recipes/${id}`,
  HARVEST: `${API_V1}/recipes/harvest`,
  UPLOAD: `${API_V1}/recipes/upload`,
} as const;

/**
 * Meal plan endpoints
 * Note: Uses hyphens (meal-plans), not underscores (meal_plans)
 */
export const MEAL_PLAN_ENDPOINTS = {
  BASE: `${API_V1}/meal-plans`,
  LIST: (skip: number, limit: number) => `${API_V1}/meal-plans?skip=${skip}&limit=${limit}`,
  DETAIL: (id: number) => `${API_V1}/meal-plans/${id}`,
  CREATE: `${API_V1}/meal-plans`,
  DELETE: (id: number) => `${API_V1}/meal-plans/${id}`,
  GROCERY_CART: (mealPlanId: number) => `${API_V1}/meal-plans/${mealPlanId}/grocery-cart`,
} as const;

/**
 * Grocery cart endpoints
 */
export const GROCERY_CART_ENDPOINTS = {
  BASE: `${API_V1}/grocery-carts`,
  DETAIL: (id: number) => `${API_V1}/grocery-carts/${id}`,
} as const;

/**
 * Workflow endpoints
 */
export const WORKFLOW_ENDPOINTS = {
  MEAL_PLAN_WITH_GROCERIES: `${API_V1}/workflows/meal-plan-with-groceries`,
} as const;

/**
 * System endpoints
 */
export const SYSTEM_ENDPOINTS = {
  HEALTH: '/health',
} as const;

/**
 * All endpoints grouped for easy reference
 */
export const API_ENDPOINTS = {
  AUTH: AUTH_ENDPOINTS,
  RECIPES: RECIPE_ENDPOINTS,
  MEAL_PLANS: MEAL_PLAN_ENDPOINTS,
  GROCERY_CARTS: GROCERY_CART_ENDPOINTS,
  WORKFLOWS: WORKFLOW_ENDPOINTS,
  SYSTEM: SYSTEM_ENDPOINTS,
} as const;
