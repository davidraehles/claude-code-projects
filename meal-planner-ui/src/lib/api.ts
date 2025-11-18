/**
 * API client for the Meal Planner backend.
 * Refactored to be immutable - token passed as parameter instead of mutation.
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
    return this.request<AuthResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async signup(data: SignupRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getCurrentUser(token: string): Promise<any> {
    return this.request("/api/v1/users/me", {}, token)
  }

  // ===== Recipe Endpoints (token required) =====

  async getRecipes(
    skip: number = 0,
    limit: number = 50,
    token?: string | null
  ): Promise<PaginatedResponse<Recipe>> {
    return this.request<PaginatedResponse<Recipe>>(
      `/api/v1/recipes?skip=${skip}&limit=${limit}`,
      {},
      token
    )
  }

  async getRecipe(id: number, token?: string | null): Promise<Recipe> {
    return this.request<Recipe>(`/api/v1/recipes/${id}`, {}, token)
  }

  async createRecipe(data: RecipeCreateRequest, token?: string | null): Promise<Recipe> {
    return this.request<Recipe>(
      "/api/v1/recipes",
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
      `/api/v1/recipes/${id}`,
      {
        method: "PUT",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async deleteRecipe(id: number, token?: string | null): Promise<void> {
    return this.request<void>(
      `/api/v1/recipes/${id}`,
      {
        method: "DELETE",
      },
      token
    )
  }

  async importRecipe(data: RecipeImportRequest, token?: string | null): Promise<any> {
    return this.request<any>(
      "/api/v1/recipes/harvest",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async uploadRecipeFile(file: File, token?: string | null): Promise<any> {
    const formData = new FormData()
    formData.append("file", file)

    const url = `${this.baseURL}/api/v1/recipes/upload`
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
      `/api/v1/meal_plans?skip=${skip}&limit=${limit}`,
      {},
      token
    )
  }

  async getMealPlan(id: number, token?: string | null): Promise<MealPlanDetail> {
    return this.request<MealPlanDetail>(`/api/v1/meal_plans/${id}`, {}, token)
  }

  async createMealPlan(data: MealPlanCreateRequest, token?: string | null): Promise<MealPlan> {
    return this.request<MealPlan>(
      "/api/v1/meal_plans",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      token
    )
  }

  async deleteMealPlan(id: number, token?: string | null): Promise<void> {
    return this.request<void>(
      `/api/v1/meal_plans/${id}`,
      {
        method: "DELETE",
      },
      token
    )
  }

  // ===== Grocery Cart Endpoints (token required) =====

  async generateGroceryCart(mealPlanId: number, token?: string | null): Promise<GroceryCart> {
    return this.request<GroceryCart>(
      `/api/v1/meal_plans/${mealPlanId}/grocery-cart`,
      {
        method: "POST",
      },
      token
    )
  }

  async getGroceryCart(id: number, token?: string | null): Promise<GroceryCart> {
    return this.request<GroceryCart>(`/api/v1/grocery-carts/${id}`, {}, token)
  }

  // ===== Health Check =====

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health")
  }
}

// Export singleton instance (stateless now - no mutation)
export const api = new ApiClient()

// Export class for custom instances
export default ApiClient
