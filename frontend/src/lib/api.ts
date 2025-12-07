/**
 * API client for the Meal Planner backend.
 * Refactored to be immutable - token passed as parameter instead of mutation.
 * Uses centralized endpoint constants to prevent typos and ensure consistency.
 */

import type {
  AuthResponse,
  LoginRequest,
  SignupRequest,
  Recipe,
  RecipeCreateRequest,
  RecipeImportRequest,
  MealPlan,
  MealPlanCreateRequest,
  MealPlanDetail,
  GroceryCart,
  PaginatedResponse,
} from "./types"
import {
  AUTH_ENDPOINTS,
  RECIPE_ENDPOINTS,
  MEAL_PLAN_ENDPOINTS,
  GROCERY_CART_ENDPOINTS,
  WORKFLOW_ENDPOINTS,
  SYSTEM_ENDPOINTS,
} from "./apiEndpoints"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export interface ApiClientOptions {
  token?: string | null
}

class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL
  }

  /**
   * Make an authenticated request.
   * Token is passed as parameter (immutable pattern).
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    token?: string | null
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    }

    // Add Authorization header if token provided
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }))
      throw new Error(error.detail || "An error occurred")
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T
    }

    return response.json()
  }

  // ===== Auth Endpoints (no token required) =====

  async login(data: LoginRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>(AUTH_ENDPOINTS.LOGIN, {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async signup(data: SignupRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>(AUTH_ENDPOINTS.REGISTER, {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getCurrentUser(token: string): Promise<Record<string, unknown>> {
    return this.request(AUTH_ENDPOINTS.ME, {}, token)
  }

  // ===== Recipe Endpoints (token required) =====

  async getRecipes(
    skip: number = 0,
    limit: number = 50,
    token?: string | null
  ): Promise<PaginatedResponse<Recipe>> {
    return this.request<PaginatedResponse<Recipe>>(
      RECIPE_ENDPOINTS.LIST(skip, limit),
      {},
      token
    )
  }

  async getRecipe(id: number, token?: string | null): Promise<Recipe> {
    return this.request<Recipe>(RECIPE_ENDPOINTS.DETAIL(id), {}, token)
  }

  async createRecipe(data: RecipeCreateRequest, token?: string | null): Promise<Recipe> {
    return this.request<Recipe>(
      RECIPE_ENDPOINTS.CREATE,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async updateRecipe(
    id: number,
    data: Partial<RecipeCreateRequest>,
    token?: string | null
  ): Promise<Recipe> {
    return this.request<Recipe>(
      RECIPE_ENDPOINTS.UPDATE(id),
      {
        method: "PUT",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async deleteRecipe(id: number, token?: string | null): Promise<void> {
    return this.request<void>(
      RECIPE_ENDPOINTS.DELETE(id),
      {
        method: "DELETE",
      },
      token
    )
  }

  async importRecipe(data: RecipeImportRequest, token?: string | null): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>(
      RECIPE_ENDPOINTS.HARVEST,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async uploadRecipeFile(file: File, token?: string | null): Promise<Record<string, unknown>> {
    const formData = new FormData()
    formData.append("file", file)

    const url = `${this.baseURL}${RECIPE_ENDPOINTS.UPLOAD}`
    const headers: Record<string, string> = {}

    // Add Authorization header if token provided
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }

    const response = await fetch(url, {
      method: "POST",
      headers,
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }))
      throw new Error(error.detail || "Failed to upload file")
    }

    return response.json()
  }

  // ===== Meal Plan Endpoints (token required) =====

  async getMealPlans(
    skip: number = 0,
    limit: number = 20,
    token?: string | null
  ): Promise<MealPlan[]> {
    return this.request<MealPlan[]>(
      MEAL_PLAN_ENDPOINTS.LIST(skip, limit),
      {},
      token
    )
  }

  async getMealPlan(id: number, token?: string | null): Promise<MealPlanDetail> {
    return this.request<MealPlanDetail>(MEAL_PLAN_ENDPOINTS.DETAIL(id), {}, token)
  }

  async createMealPlan(data: MealPlanCreateRequest, token?: string | null): Promise<MealPlan> {
    return this.request<MealPlan>(
      MEAL_PLAN_ENDPOINTS.CREATE,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async deleteMealPlan(id: number, token?: string | null): Promise<void> {
    return this.request<void>(
      MEAL_PLAN_ENDPOINTS.DELETE(id),
      {
        method: "DELETE",
      },
      token
    )
  }

  // ===== Grocery Cart Endpoints (token required) =====

  async generateGroceryCart(mealPlanId: number, token?: string | null): Promise<GroceryCart> {
    return this.request<GroceryCart>(
      MEAL_PLAN_ENDPOINTS.GROCERY_CART(mealPlanId),
      {
        method: "POST",
      },
      token
    )
  }

  async getGroceryCart(id: number, token?: string | null): Promise<GroceryCart> {
    return this.request<GroceryCart>(GROCERY_CART_ENDPOINTS.DETAIL(id), {}, token)
  }

  // ===== Workflow Endpoints (token required) =====

  async createCartFromMealPlanWorkflow(
    mealPlanId: number,
    deliveryPreferences?: {
      preferred_dates?: string[]
      preferred_time_slot?: 'morning' | 'afternoon' | 'evening'
      budget_optimization?: boolean
    },
    token?: string | null
  ): Promise<{
    workflow_id: string
    status: string
    message: string
    result?: {
      cart_id: number
      knuspr_url: string
      total_price: number
      item_count: number
      delivery_slot?: unknown
      items_by_section?: Record<string, unknown>
      unavailable_items?: string[]
    }
  }> {
    return this.request(
      WORKFLOW_ENDPOINTS.MEAL_PLAN_WITH_GROCERIES,
      {
        method: "POST",
        body: JSON.stringify({
          meal_plan_id: mealPlanId,
          delivery_preferences: deliveryPreferences,
        }),
      },
      token
    )
  }

  // ===== Health Check =====

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>(SYSTEM_ENDPOINTS.HEALTH)
  }
}

// Export singleton instance (stateless now - no mutation)
export const api = new ApiClient()

// Export class for custom instances
export default ApiClient
