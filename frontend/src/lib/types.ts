/**
 * TypeScript type definitions for the Meal Planner API.
 */

// ===== User & Auth =====

export interface User {
  id: number
  email: string
  country: string
  created_at: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  country: string
}

// ===== Recipe =====

export interface Recipe {
  id: number
  user_id: number
  title: string
  ingredients: string[]
  instructions: string
  prep_time?: number
  cook_time?: number
  servings?: number
  dietary_tags?: string[]
  nutrition?: NutritionInfo
  source_url?: string
  source_type?: string
  created_at: string
  updated_at: string
}

export interface NutritionInfo {
  calories?: number
  protein?: number
  carbs?: number
  fat?: number
  fiber?: number
  sugar?: number
}

export interface RecipeCreateRequest {
  title: string
  ingredients: string[]
  instructions: string
  prep_time?: number
  cook_time?: number
  servings?: number
  dietary_tags?: string[]
  nutrition?: NutritionInfo
  source_url?: string
}

export interface RecipeImportRequest {
  url: string
  source_type: "html" | "api" | "rss"
}

// ===== Meal Plan =====

export interface MealPlan {
  id: number
  user_id: number
  name: string
  start_date: string
  end_date: string
  num_days: number
  num_people: number
  meals_per_day: number
  dietary_restrictions?: string[]
  excluded_ingredients?: string[]
  target_calories_per_day?: number
  target_budget?: number
  preferred_cuisines?: string[]
  status: "generating" | "ready" | "failed"
  total_recipes?: number
  total_calories?: number
  total_cost?: number
  created_at: string
  updated_at: string
}

export interface MealPlanCreateRequest {
  start_date: string
  num_days: number
  num_people: number
  meals_per_day: number
  dietary_restrictions?: string[]
  excluded_ingredients?: string[]
  target_calories_per_day?: number
  target_budget?: number
  preferred_cuisines?: string[]
}

export interface MealPlanDay {
  day_number: number
  date: string
  meals: Meal[]
}

export interface Meal {
  meal_type: string
  recipe_id: number
  recipe_name: string
  servings: number
  calories?: number
  cost?: number
}

export interface MealPlanDetail {
  meal_plan: MealPlan
  days: MealPlanDay[]
  statistics: MealPlanStatistics
}

/**
 * The API may return either a nested MealPlanDetail structure or a flat structure
 * combining MealPlan with its related days and statistics.
 */
export type MealPlanDetailResponse = MealPlanDetail | (MealPlan & { days: MealPlanDay[]; statistics: MealPlanStatistics })

export interface MealPlanStatistics {
  total_meals: number
  total_recipes: number
  unique_recipes: number
  avg_calories_per_day: number
  avg_cost_per_day: number
  dietary_compliance: {
    [key: string]: number
  }
}

// ===== Grocery Cart =====

export interface GroceryCart {
  id: number
  meal_plan_id: number
  items: GroceryItem[]
  total_items: number
  status: "active" | "purchased"
  created_at: string
  unmatched_items?: string[]
  unavailable_items?: string[]
}

export interface RecipeSource {
  recipe_id: number
  recipe_name: string
}

export interface GroceryItem {
  ingredient: string
  quantity: string
  category?: string
  estimated_cost?: number
  checked?: boolean
  recipe_sources?: RecipeSource[]
}

// ===== API Responses =====

export interface ApiError {
  detail: string
  status_code: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// ===== Form Data =====

export interface MealPlanFormData {
  startDate: Date
  numDays: number
  numPeople: number
  mealsPerDay: number
  dietaryRestrictions: string[]
  excludedIngredients: string[]
  targetCaloriesPerDay?: number
  targetBudget?: number
}

// ===== UI State =====

export interface LoadingState {
  isLoading: boolean
  error?: string
}

export interface ToastMessage {
  id: string
  type: "success" | "error" | "info" | "warning"
  message: string
  duration?: number
}
