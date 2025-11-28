/**
 * Tests for API endpoint constants
 *
 * These tests verify that:
 * 1. All endpoints use the correct format (hyphens vs underscores)
 * 2. Dynamic endpoints generate correct URLs
 * 3. Endpoints match the backend route definitions
 */

import {
  AUTH_ENDPOINTS,
  RECIPE_ENDPOINTS,
  MEAL_PLAN_ENDPOINTS,
  GROCERY_CART_ENDPOINTS,
  WORKFLOW_ENDPOINTS,
  SYSTEM_ENDPOINTS,
} from '@/lib/apiEndpoints';

describe('API Endpoint Constants', () => {
  describe('Auth Endpoints', () => {
    it('should have correct auth endpoint paths', () => {
      expect(AUTH_ENDPOINTS.LOGIN).toBe('/api/v1/auth/login');
      expect(AUTH_ENDPOINTS.REGISTER).toBe('/api/v1/auth/register');
      expect(AUTH_ENDPOINTS.REFRESH).toBe('/api/v1/auth/refresh');
      expect(AUTH_ENDPOINTS.ME).toBe('/api/v1/users/me');
    });
  });

  describe('Recipe Endpoints', () => {
    it('should have correct recipe endpoint paths', () => {
      expect(RECIPE_ENDPOINTS.BASE).toBe('/api/v1/recipes');
      expect(RECIPE_ENDPOINTS.CREATE).toBe('/api/v1/recipes');
      expect(RECIPE_ENDPOINTS.HARVEST).toBe('/api/v1/recipes/harvest');
      expect(RECIPE_ENDPOINTS.UPLOAD).toBe('/api/v1/recipes/upload');
    });

    it('should generate correct list endpoint with pagination', () => {
      expect(RECIPE_ENDPOINTS.LIST(0, 50)).toBe('/api/v1/recipes?skip=0&limit=50');
      expect(RECIPE_ENDPOINTS.LIST(10, 20)).toBe('/api/v1/recipes?skip=10&limit=20');
    });

    it('should generate correct detail endpoint with ID', () => {
      expect(RECIPE_ENDPOINTS.DETAIL(1)).toBe('/api/v1/recipes/1');
      expect(RECIPE_ENDPOINTS.DETAIL(123)).toBe('/api/v1/recipes/123');
    });

    it('should generate correct update endpoint with ID', () => {
      expect(RECIPE_ENDPOINTS.UPDATE(1)).toBe('/api/v1/recipes/1');
    });

    it('should generate correct delete endpoint with ID', () => {
      expect(RECIPE_ENDPOINTS.DELETE(1)).toBe('/api/v1/recipes/1');
    });
  });

  describe('Meal Plan Endpoints', () => {
    it('should use hyphens (meal-plans) not underscores (meal_plans)', () => {
      expect(MEAL_PLAN_ENDPOINTS.BASE).toBe('/api/v1/meal-plans');
      expect(MEAL_PLAN_ENDPOINTS.BASE).not.toContain('meal_plans');
    });

    it('should have correct meal plan endpoint paths', () => {
      expect(MEAL_PLAN_ENDPOINTS.CREATE).toBe('/api/v1/meal-plans');
    });

    it('should generate correct list endpoint with pagination', () => {
      expect(MEAL_PLAN_ENDPOINTS.LIST(0, 20)).toBe('/api/v1/meal-plans?skip=0&limit=20');
      expect(MEAL_PLAN_ENDPOINTS.LIST(5, 10)).toBe('/api/v1/meal-plans?skip=5&limit=10');
    });

    it('should generate correct detail endpoint with ID', () => {
      expect(MEAL_PLAN_ENDPOINTS.DETAIL(1)).toBe('/api/v1/meal-plans/1');
      expect(MEAL_PLAN_ENDPOINTS.DETAIL(456)).toBe('/api/v1/meal-plans/456');
    });

    it('should generate correct delete endpoint with ID', () => {
      expect(MEAL_PLAN_ENDPOINTS.DELETE(1)).toBe('/api/v1/meal-plans/1');
    });

    it('should generate correct grocery cart endpoint with meal plan ID', () => {
      expect(MEAL_PLAN_ENDPOINTS.GROCERY_CART(1)).toBe('/api/v1/meal-plans/1/grocery-cart');
      expect(MEAL_PLAN_ENDPOINTS.GROCERY_CART(789)).toBe('/api/v1/meal-plans/789/grocery-cart');
    });
  });

  describe('Grocery Cart Endpoints', () => {
    it('should have correct grocery cart endpoint paths', () => {
      expect(GROCERY_CART_ENDPOINTS.BASE).toBe('/api/v1/grocery-carts');
    });

    it('should generate correct detail endpoint with ID', () => {
      expect(GROCERY_CART_ENDPOINTS.DETAIL(1)).toBe('/api/v1/grocery-carts/1');
      expect(GROCERY_CART_ENDPOINTS.DETAIL(999)).toBe('/api/v1/grocery-carts/999');
    });
  });

  describe('Workflow Endpoints', () => {
    it('should have correct workflow endpoint paths', () => {
      expect(WORKFLOW_ENDPOINTS.MEAL_PLAN_WITH_GROCERIES).toBe('/api/v1/workflows/meal-plan-with-groceries');
    });
  });

  describe('System Endpoints', () => {
    it('should have correct system endpoint paths', () => {
      expect(SYSTEM_ENDPOINTS.HEALTH).toBe('/health');
    });
  });

  describe('Endpoint Consistency', () => {
    it('should not contain underscores in meal plan URLs', () => {
      const mealPlanEndpoints = Object.values(MEAL_PLAN_ENDPOINTS);

      mealPlanEndpoints.forEach((endpoint) => {
        if (typeof endpoint === 'string') {
          expect(endpoint).not.toContain('meal_plans');
        }
      });
    });

    it('should use consistent versioning (v1)', () => {
      const allEndpoints = [
        ...Object.values(AUTH_ENDPOINTS),
        ...Object.values(RECIPE_ENDPOINTS).filter(e => typeof e === 'string'),
        ...Object.values(MEAL_PLAN_ENDPOINTS).filter(e => typeof e === 'string'),
        ...Object.values(GROCERY_CART_ENDPOINTS).filter(e => typeof e === 'string'),
        ...Object.values(WORKFLOW_ENDPOINTS),
      ];

      allEndpoints.forEach((endpoint) => {
        if (typeof endpoint === 'string' && endpoint.startsWith('/api')) {
          expect(endpoint).toMatch(/^\/api\/v1\//);
        }
      });
    });
  });
});
