/**
 * API client for the Meal Planner backend.
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

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    this.token = token
  }

  clearToken() {
    this.token = null
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    }

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
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

  // ===== Auth Endpoints =====

  async login(data: LoginRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async signup(data: SignupRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getCurrentUser(): Promise<any> {
    return this.request("/api/v1/users/me")
  }

  // ===== Recipe Endpoints =====

  async getRecipes(
    page: number = 1,
    size: number = 50
  ): Promise<PaginatedResponse<Recipe>> {
    return this.request<PaginatedResponse<Recipe>>(
      `/api/v1/recipes?page=${page}&size=${size}`
    )
  }

  async getRecipe(id: number): Promise<Recipe> {
    return this.request<Recipe>(`/api/v1/recipes/${id}`)
  }

  async createRecipe(data: RecipeCreateRequest): Promise<Recipe> {
    return this.request<Recipe>("/api/v1/recipes", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async updateRecipe(id: number, data: Partial<RecipeCreateRequest>): Promise<Recipe> {
    return this.request<Recipe>(`/api/v1/recipes/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  async deleteRecipe(id: number): Promise<void> {
    return this.request<void>(`/api/v1/recipes/${id}`, {
      method: "DELETE",
    })
  }

  async importRecipe(data: RecipeImportRequest): Promise<Recipe> {
    return this.request<Recipe>("/api/v1/recipes/import", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  // ===== Meal Plan Endpoints =====

  async getMealPlans(
    page: number = 1,
    size: number = 20
  ): Promise<PaginatedResponse<MealPlan>> {
    return this.request<PaginatedResponse<MealPlan>>(
      `/api/v1/meal-plans?page=${page}&size=${size}`
    )
  }

  async getMealPlan(id: number): Promise<MealPlanDetail> {
    return this.request<MealPlanDetail>(`/api/v1/meal-plans/${id}`)
  }

  async createMealPlan(data: MealPlanCreateRequest): Promise<MealPlan> {
    return this.request<MealPlan>("/api/v1/meal-plans", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async deleteMealPlan(id: number): Promise<void> {
    return this.request<void>(`/api/v1/meal-plans/${id}`, {
      method: "DELETE",
    })
  }

  // ===== Grocery Cart Endpoints =====

  async generateGroceryCart(mealPlanId: number): Promise<GroceryCart> {
    return this.request<GroceryCart>(
      `/api/v1/meal-plans/${mealPlanId}/grocery-cart`,
      {
        method: "POST",
      }
    )
  }

  async getGroceryCart(id: number): Promise<GroceryCart> {
    return this.request<GroceryCart>(`/api/v1/grocery-carts/${id}`)
  }

  // ===== Health Check =====

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health")
  }
}

// Export singleton instance
export const api = new ApiClient()

// Export class for custom instances
export default ApiClient
