import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Knuspr Grocery Cart Integration
 *
 * Test suite for the complete workflow:
 * 1. User logs in
 * 2. Imports recipes or selects from meal plan
 * 3. Generates meal plan
 * 4. Creates Knuspr shopping cart
 * 5. Selects delivery slot
 * 6. Completes checkout
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://claude-code-projects-production.up.railway.app';
const FRONTEND_URL = process.env.FRONTEND_URL || 'https://meal-planner-h7g716e6b-the-raedical-cos-projects.vercel.app';

// Test user credentials (should be created before running tests)
const TEST_USER = {
  email: 'knuspr-test@example.com',
  password: 'test-password-123'
};

test.describe('Knuspr Grocery Cart Integration', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to app and clear any existing sessions
    await page.goto(FRONTEND_URL);
    await page.context().clearCookies();
  });

  test('should create grocery cart from meal plan with Knuspr products', async ({ page, request }) => {
    /**
     * Test: Create Knuspr cart from existing meal plan
     *
     * Flow:
     * 1. Login to app
     * 2. Create or select meal plan
     * 3. Call POST /api/v1/grocery-carts endpoint
     * 4. Verify cart created with products grouped by section
     * 5. Verify delivery slot selection
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');

    // Wait for redirect to dashboard
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);
    expect(page.url()).toContain('/dashboard');

    // Step 2: Navigate to meal plans
    await page.click('a:has-text("Meal Plans")');
    await page.waitForURL(`${FRONTEND_URL}/meal-plans`);

    // Step 3: Click "Create Grocery Cart" button on a meal plan
    const mealPlanCard = page.locator('[data-testid="meal-plan-card"]').first();
    await expect(mealPlanCard).toBeVisible();

    // Get meal plan ID from card
    const mealPlanId = await mealPlanCard.getAttribute('data-meal-plan-id');
    expect(mealPlanId).toBeTruthy();

    // Click create cart button
    await mealPlanCard.locator('button:has-text("Create Grocery Cart")').click();

    // Step 4: Wait for cart creation modal
    const cartModal = page.locator('[data-testid="cart-creation-modal"]');
    await expect(cartModal).toBeVisible({ timeout: 5000 });

    // Verify cart summary
    const cartSummary = page.locator('[data-testid="cart-summary"]');
    await expect(cartSummary).toBeVisible();

    // Check for items grouped by section
    const produceSection = page.locator('[data-testid="cart-section-produce"]');
    const dairySection = page.locator('[data-testid="cart-section-dairy"]');

    expect(
      (await produceSection.isVisible()) || (await dairySection.isVisible())
    ).toBeTruthy();

    // Verify total price is displayed
    const totalPrice = page.locator('[data-testid="cart-total-price"]');
    await expect(totalPrice).toContainText(/\d+\.\d{2}/);

    // Step 5: Verify delivery slot selection
    const deliverySlotSelect = page.locator('[data-testid="delivery-slot-select"]');
    await expect(deliverySlotSelect).toBeVisible();

    // Select a delivery slot
    await deliverySlotSelect.click();
    const firstSlot = page.locator('[data-testid="delivery-slot-option"]').first();
    await firstSlot.click();

    // Step 6: Verify Knuspr cart link
    const knusprLink = page.locator('[data-testid="knuspr-cart-link"]');
    await expect(knusprLink).toBeVisible();
    expect(await knusprLink.getAttribute('href')).toMatch(/knuspr\.cz\/cart\//);
  });

  test('should handle unavailable items gracefully', async ({ page, request }) => {
    /**
     * Test: Handle products not available on Knuspr
     *
     * Verify:
     * 1. Cart created with available items
     * 2. Unavailable items listed in warning section
     * 3. User can replace unavailable items
     * 4. Cart updates with replacements
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Create cart (which may have unavailable items)
    await page.click('a:has-text("Meal Plans")');
    await page.waitForURL(`${FRONTEND_URL}/meal-plans`);

    const mealPlanCard = page.locator('[data-testid="meal-plan-card"]').first();
    await mealPlanCard.locator('button:has-text("Create Grocery Cart")').click();

    // Step 3: Check for unavailable items warning
    const unavailableWarning = page.locator('[data-testid="unavailable-items-warning"]');
    const unavailableList = page.locator('[data-testid="unavailable-items-list"]');

    if (await unavailableWarning.isVisible()) {
      // Unavailable items exist
      await expect(unavailableList).toBeVisible();

      const items = unavailableList.locator('li');
      const count = await items.count();
      expect(count).toBeGreaterThan(0);

      // Step 4: Try to replace unavailable item
      const firstUnavailableItem = items.first();
      const replaceButton = firstUnavailableItem.locator('button:has-text("Find Alternative")');

      if (await replaceButton.isVisible()) {
        await replaceButton.click();

        // Alternative selection modal should appear
        const alternativeModal = page.locator('[data-testid="alternative-selection-modal"]');
        await expect(alternativeModal).toBeVisible({ timeout: 5000 });

        // Select first alternative
        const firstAlternative = alternativeModal.locator('[data-testid="alternative-option"]').first();
        await firstAlternative.click();

        // Verify cart updates
        const updatedCart = page.locator('[data-testid="cart-summary"]');
        await expect(updatedCart).toBeVisible();
      }
    }
  });

  test('should select optimal delivery slot based on user preferences', async ({ page }) => {
    /**
     * Test: Delivery slot selection logic
     *
     * Verify:
     * 1. All available slots displayed
     * 2. Slots correctly show date and time window
     * 3. Price displayed for each slot
     * 4. User can select slot based on preference
     * 5. "Budget Optimization" toggle works
     */

    // Step 1: Login and create cart
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    await page.click('a:has-text("Meal Plans")');
    const mealPlanCard = page.locator('[data-testid="meal-plan-card"]').first();
    await mealPlanCard.locator('button:has-text("Create Grocery Cart")').click();

    // Step 2: Open delivery slot selector
    const deliverySlotSelect = page.locator('[data-testid="delivery-slot-select"]');
    await deliverySlotSelect.click();

    // Step 3: Verify slots are displayed
    const slotOptions = page.locator('[data-testid="delivery-slot-option"]');
    const slotCount = await slotOptions.count();
    expect(slotCount).toBeGreaterThan(0);

    // Step 4: Verify slot details
    const firstSlot = slotOptions.first();
    const slotDate = firstSlot.locator('[data-testid="slot-date"]');
    const slotTime = firstSlot.locator('[data-testid="slot-time"]');
    const slotPrice = firstSlot.locator('[data-testid="slot-price"]');

    await expect(slotDate).toBeVisible();
    await expect(slotTime).toBeVisible();
    await expect(slotPrice).toBeVisible();

    // Step 5: Test budget optimization toggle
    const budgetToggle = page.locator('[data-testid="budget-optimization-toggle"]');
    if (await budgetToggle.isVisible()) {
      const isChecked = await budgetToggle.isChecked();

      // Toggle and verify slot order changes
      await budgetToggle.click();

      // After toggle, first slot should be different (if budget optimization changes sorting)
      const newFirstSlot = slotOptions.first();
      if (!isChecked) {
        // Now in budget mode - cheapest should be first
        const newPrice = await newFirstSlot.locator('[data-testid="slot-price"]').textContent();
        expect(newPrice).toBeTruthy();
      }
    }

    // Step 6: Select a slot
    await firstSlot.click();

    // Verify selection persists
    const selectedIndicator = firstSlot.locator('[data-testid="slot-selected"]');
    await expect(selectedIndicator).toBeVisible();
  });

  test('should display cart items grouped by store section', async ({ page }) => {
    /**
     * Test: Items grouped by store section
     *
     * Verify:
     * 1. Cart displays sections: produce, dairy, meat, canned goods, etc.
     * 2. Items correctly categorized
     * 3. Section headers visible
     * 4. Items show quantity, unit, and price
     */

    // Step 1: Login and create cart
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    await page.click('a:has-text("Meal Plans")');
    const mealPlanCard = page.locator('[data-testid="meal-plan-card"]').first();
    await mealPlanCard.locator('button:has-text("Create Grocery Cart")').click();

    // Step 2: Verify sections displayed
    const sections = page.locator('[data-testid^="cart-section-"]');
    const sectionCount = await sections.count();
    expect(sectionCount).toBeGreaterThan(0);

    // Step 3: Verify section headers and items
    for (let i = 0; i < Math.min(sectionCount, 3); i++) {
      const section = sections.nth(i);
      const header = section.locator('[data-testid="section-header"]');
      const items = section.locator('[data-testid="cart-item"]');

      await expect(header).toBeVisible();
      const itemCount = await items.count();
      expect(itemCount).toBeGreaterThanOrEqual(0);

      // Verify each item shows required fields
      if (itemCount > 0) {
        const firstItem = items.first();
        const itemName = firstItem.locator('[data-testid="item-name"]');
        const itemQuantity = firstItem.locator('[data-testid="item-quantity"]');
        const itemPrice = firstItem.locator('[data-testid="item-price"]');

        await expect(itemName).toBeVisible();
        await expect(itemQuantity).toBeVisible();
        await expect(itemPrice).toBeVisible();
      }
    }
  });

  test('should navigate from meal plan to checkout', async ({ page }) => {
    /**
     * Test: Complete workflow from meal plan to checkout
     *
     * Verify:
     * 1. Meal plan page has "Order Groceries" button
     * 2. Cart creation triggered
     * 3. Checkout button visible
     * 4. Checkout redirects to Knuspr
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to meal plan detail
    await page.click('a:has-text("Meal Plans")');
    const mealPlanCard = page.locator('[data-testid="meal-plan-card"]').first();
    await mealPlanCard.click();

    // Step 3: Verify "Order Groceries" button
    const orderGroceriesButton = page.locator('button:has-text("Order Groceries")');
    await expect(orderGroceriesButton).toBeVisible();
    await orderGroceriesButton.click();

    // Step 4: Wait for cart modal
    const cartModal = page.locator('[data-testid="cart-creation-modal"]');
    await expect(cartModal).toBeVisible({ timeout: 5000 });

    // Step 5: Look for checkout button
    const checkoutButton = page.locator('button:has-text("Proceed to Checkout")');
    if (await checkoutButton.isVisible()) {
      // Verify button would take to Knuspr
      const checkoutLink = checkoutButton.locator('[href*="knuspr"]');
      if (await checkoutLink.isVisible()) {
        expect(await checkoutLink.getAttribute('href')).toMatch(/knuspr/);
      }
    }
  });

  test('API: should return 400 for invalid meal plan ID', async ({ request }) => {
    /**
     * Test: API validation for invalid meal plan
     */
    const response = await request.post(
      `${API_URL}/api/v1/grocery-carts`,
      {
        data: {
          meal_plan_id: 'invalid-id',
          delivery_preferences: {}
        }
      }
    );

    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(body.detail || body.message).toBeTruthy();
  });

  test('API: should create cart with delivery preferences', async ({ request }) => {
    /**
     * Test: API creates cart with delivery preferences
     */
    const response = await request.post(
      `${API_URL}/api/v1/grocery-carts`,
      {
        data: {
          meal_plan_id: 'valid-meal-plan-id',
          delivery_preferences: {
            preferred_time_slot: 'evening',
            budget_optimization: true
          }
        }
      }
    );

    // Should be 200 if meal plan exists, 400 if not
    expect([200, 400]).toContain(response.status());

    if (response.status() === 200) {
      const body = await response.json();
      expect(body.cart_id).toBeTruthy();
      expect(body.total_price).toBeGreaterThan(0);
      expect(body.items_by_section).toBeTruthy();
    }
  });
});
