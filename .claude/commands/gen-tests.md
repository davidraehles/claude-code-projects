# Gen Tests Skill

Generate comprehensive test suite for existing code components or endpoints with high coverage.

## Usage

```
/gen-tests [file-path] [test-type]
```

## Parameters

- `file-path`: Path to component or endpoint (e.g., src/components/Hero.tsx, app/endpoints/recipes.py)
- `test-type`: unit | integration | e2e | all (default: unit)

## Examples

```
/gen-tests src/components/Hero.tsx unit
/gen-tests app/endpoints/recipes.py all
/gen-tests src/components/ContactForm.tsx integration
```

## What It Does

1. Analyzes the target file structure and dependencies
2. Identifies all functions, components, and edge cases
3. Generates unit tests covering:
   - Happy path execution
   - Error conditions
   - Edge cases
   - Type validation
   - Accessibility (for components)
4. Generates integration tests covering:
   - Component interactions
   - API endpoint workflows
   - Database operations
5. Adds E2E tests for critical user paths
6. Calculates and targets 90%+ code coverage

## Output

Creates test files:
```
Frontend:
  src/__tests__/ComponentName.test.tsx

Backend:
  tests/test_module.py
  tests/integration/test_workflow.py
```

## Test Generation Examples

### Frontend Component Tests

```typescript
// src/__tests__/ContactForm.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ContactForm } from "../components/ContactForm";
import { axe, toHaveNoViolations } from "jest-axe";

describe("ContactForm Component", () => {
  // ============ Rendering Tests ============
  describe("rendering", () => {
    test("renders form with all required fields", () => {
      render(<ContactForm onSubmit={vi.fn()} />);

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /submit/i })).toBeInTheDocument();
    });

    test("displays form title and description", () => {
      render(<ContactForm onSubmit={vi.fn()} />);

      expect(screen.getByText(/get in touch/i)).toBeInTheDocument();
      expect(screen.getByText(/we respond within/i)).toBeInTheDocument();
    });
  });

  // ============ User Interaction Tests ============
  describe("user interactions", () => {
    test("submits form with valid data", async () => {
      const handleSubmit = vi.fn().mockResolvedValue(undefined);
      render(<ContactForm onSubmit={handleSubmit} />);

      await userEvent.type(screen.getByLabelText(/email/i), "test@example.com");
      await userEvent.type(screen.getByLabelText(/message/i), "Test message");
      await userEvent.click(screen.getByRole("button", { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalledWith({
          email: "test@example.com",
          message: "Test message",
        });
      });
    });

    test("disables submit button during submission", async () => {
      const handleSubmit = vi.fn(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );
      render(<ContactForm onSubmit={handleSubmit} />);

      await userEvent.type(screen.getByLabelText(/email/i), "test@example.com");
      await userEvent.type(screen.getByLabelText(/message/i), "Test message");

      const submitButton = screen.getByRole("button", { name: /submit/i });
      await userEvent.click(submitButton);

      expect(submitButton).toBeDisabled();

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });
  });

  // ============ Validation Tests ============
  describe("validation", () => {
    test("shows error for invalid email", async () => {
      render(<ContactForm onSubmit={vi.fn()} />);

      await userEvent.type(screen.getByLabelText(/email/i), "invalid-email");
      await userEvent.click(screen.getByRole("button", { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
      });
    });

    test("shows error for empty message", async () => {
      render(<ContactForm onSubmit={vi.fn()} />);

      await userEvent.type(screen.getByLabelText(/email/i), "test@example.com");
      await userEvent.click(screen.getByRole("button", { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/message is required/i)).toBeInTheDocument();
      });
    });
  });

  // ============ Accessibility Tests ============
  describe("accessibility", () => {
    test("has no accessibility violations (axe-core)", async () => {
      const { container } = render(<ContactForm onSubmit={vi.fn()} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    test("form labels are properly associated with inputs", () => {
      render(<ContactForm onSubmit={vi.fn()} />);

      const emailInput = screen.getByLabelText(/email/i);
      const messageInput = screen.getByLabelText(/message/i);

      expect(emailInput).toHaveAttribute("type", "email");
      expect(messageInput).toHaveAttribute("required");
    });

    test("keyboard navigation works", async () => {
      render(<ContactForm onSubmit={vi.fn()} />);

      const emailInput = screen.getByLabelText(/email/i);
      emailInput.focus();
      expect(emailInput).toHaveFocus();

      await userEvent.tab();
      expect(screen.getByLabelText(/message/i)).toHaveFocus();

      await userEvent.tab();
      expect(screen.getByRole("button", { name: /submit/i })).toHaveFocus();
    });
  });

  // ============ Error Handling Tests ============
  describe("error handling", () => {
    test("displays error message on submission failure", async () => {
      const handleSubmit = vi.fn().mockRejectedValue(new Error("Server error"));
      render(<ContactForm onSubmit={handleSubmit} />);

      await userEvent.type(screen.getByLabelText(/email/i), "test@example.com");
      await userEvent.type(screen.getByLabelText(/message/i), "Test message");
      await userEvent.click(screen.getByRole("button", { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/error submitting form/i)).toBeInTheDocument();
      });
    });

    test("shows success message on successful submission", async () => {
      const handleSubmit = vi.fn().mockResolvedValue(undefined);
      render(<ContactForm onSubmit={handleSubmit} />);

      await userEvent.type(screen.getByLabelText(/email/i), "test@example.com");
      await userEvent.type(screen.getByLabelText(/message/i), "Test message");
      await userEvent.click(screen.getByRole("button", { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/thank you/i)).toBeInTheDocument();
      });
    });
  });

  // ============ Responsive Design Tests ============
  describe("responsive design", () => {
    test("renders correctly on mobile viewport", () => {
      window.matchMedia = vi.fn().mockImplementation((query) => ({
        matches: query === "(max-width: 640px)",
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }));

      render(<ContactForm onSubmit={vi.fn()} />);

      const form = screen.getByRole("form");
      expect(form).toHaveClass("flex-col");
    });
  });
});
```

### Backend API Tests

```python
# tests/test_recipes.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

class TestRecipeEndpoints:
    """Tests for recipe CRUD endpoints"""

    @pytest.mark.asyncio
    async def test_create_recipe_success(
        self, client: AsyncClient, db: AsyncSession, user_token: str
    ):
        """Test creating a recipe with valid data"""
        response = await client.post(
            "/recipes/",
            json={
                "title": "Pasta Carbonara",
                "ingredients": ["pasta", "eggs", "bacon"],
                "instructions": "Cook and mix...",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Pasta Carbonara"
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_create_recipe_validation_error(
        self, client: AsyncClient, user_token: str
    ):
        """Test creating recipe with invalid data"""
        response = await client.post(
            "/recipes/",
            json={"title": ""},  # Invalid: empty title
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 422
        assert "title" in str(response.json())

    @pytest.mark.asyncio
    async def test_get_recipe_success(
        self, client: AsyncClient, user_token: str, recipe_id: int
    ):
        """Test getting a recipe"""
        response = await client.get(
            f"/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        assert response.json()["id"] == recipe_id

    @pytest.mark.asyncio
    async def test_row_level_security(
        self, client: AsyncClient, other_user_token: str, recipe_id: int
    ):
        """Test that users cannot access other users' recipes"""
        response = await client.get(
            f"/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_recipes(self, client: AsyncClient, user_token: str):
        """Test listing user's recipes"""
        response = await client.get(
            "/recipes/",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

## Coverage Report

Generated tests should achieve:
- ✓ 90%+ line coverage
- ✓ 85%+ branch coverage
- ✓ 90%+ function coverage
- All error paths tested
- All user interactions tested
- Edge cases covered

## When to Use

- Have existing code that needs test coverage
- Want consistent test patterns across project
- Need to increase code coverage
- Refactoring and want test safety net
- Adding tests to legacy code
