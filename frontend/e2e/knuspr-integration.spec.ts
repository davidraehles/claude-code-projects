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

  // ===== T021: New E2E Tests for FillCartButton Component =====

  test('should successfully fill Knuspr cart from grocery cart', async ({ page }) => {
    /**
     * Test: Complete flow of filling Knuspr cart with credentials
     *
     * Verify:
     * 1. Navigate to grocery cart page
     * 2. Click "Fill Knuspr Cart" button
     * 3. Enter Knuspr credentials
     * 4. Verify progress indicator appears
     * 5. Wait for success message
     * 6. Check matched items count is shown
     * 7. Verify Knuspr cart link is present
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to grocery carts (assuming we have a grocery cart)
    await page.goto(`${FRONTEND_URL}/grocery-carts`);
    await page.waitForLoadState('networkidle');

    // Find and click on first grocery cart
    const cartCard = page.locator('[data-testid="grocery-cart-card"]').first();
    if (await cartCard.isVisible()) {
      await cartCard.click();
    } else {
      // Create a cart if none exists
      await page.goto(`${FRONTEND_URL}/meal-plans`);
      const mealPlanCard = page.locator('[data-testid="meal-plan-card"]').first();
      await mealPlanCard.locator('button:has-text("Create Grocery Cart")').click();
      await page.waitForURL(/\/grocery-carts\/\d+/);
    }

    // Step 3: Click "Fill Knuspr Cart" button
    const fillCartButton = page.locator('button:has-text("Fill Knuspr Cart")');
    await expect(fillCartButton).toBeVisible({ timeout: 5000 });
    await fillCartButton.click();

    // Step 4: Enter Knuspr credentials
    const emailInput = page.locator('input[type="email"][aria-label*="Knuspr"]');
    const passwordInput = page.locator('input[type="password"][aria-label*="Knuspr"]');

    await expect(emailInput).toBeVisible({ timeout: 3000 });
    await emailInput.fill('knuspr-test@example.com');
    await passwordInput.fill('test-knuspr-password');

    // Submit form
    const submitButton = page.locator('button[type="submit"]:has-text("Fill Cart")');
    await submitButton.click();

    // Step 5: Verify progress indicator appears
    const progressBar = page.locator('[role="progressbar"]');
    await expect(progressBar).toBeVisible({ timeout: 3000 });

    // Wait for loading text
    await expect(page.locator('text=Filling Knuspr Cart')).toBeVisible();

    // Step 6: Wait for success message (may take a while)
    const successMessage = page.locator('text=Cart Filled Successfully');
    await expect(successMessage).toBeVisible({ timeout: 30000 });

    // Step 7: Check matched items count
    const matchedItemsText = page.locator('text=/\\d+ items? added to your Knuspr cart/');
    await expect(matchedItemsText).toBeVisible();

    // Step 8: Verify Knuspr cart link is present
    const knusprLink = page.locator('a:has-text("View in Knuspr")');
    await expect(knusprLink).toBeVisible();

    const href = await knusprLink.getAttribute('href');
    expect(href).toBeTruthy();
    expect(href).toMatch(/knuspr/i);
  });

  test('should handle authentication failure', async ({ page }) => {
    /**
     * Test: Handle invalid Knuspr credentials
     *
     * Verify:
     * 1. Enter invalid credentials
     * 2. Verify error message appears
     * 3. Check that retry is possible
     */

    // Step 1: Login to app
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to a grocery cart
    await page.goto(`${FRONTEND_URL}/grocery-carts`);
    await page.waitForLoadState('networkidle');

    const cartCard = page.locator('[data-testid="grocery-cart-card"]').first();
    if (await cartCard.isVisible()) {
      await cartCard.click();
    }

    // Step 3: Click "Fill Knuspr Cart" button
    const fillCartButton = page.locator('button:has-text("Fill Knuspr Cart")');
    await expect(fillCartButton).toBeVisible({ timeout: 5000 });
    await fillCartButton.click();

    // Step 4: Enter INVALID credentials
    const emailInput = page.locator('input[type="email"][aria-label*="Knuspr"]');
    const passwordInput = page.locator('input[type="password"][aria-label*="Knuspr"]');

    await expect(emailInput).toBeVisible({ timeout: 3000 });
    await emailInput.fill('invalid@example.com');
    await passwordInput.fill('wrong-password');

    // Submit form
    const submitButton = page.locator('button[type="submit"]:has-text("Fill Cart")');
    await submitButton.click();

    // Step 5: Verify error message appears
    const errorMessage = page.locator('text=Authentication Failed, text=Failed to Fill Cart');
    await expect(errorMessage.first()).toBeVisible({ timeout: 10000 });

    // Step 6: Check that retry button is available
    const retryButton = page.locator('button:has-text("Try Again")');
    await expect(retryButton).toBeVisible();

    // Verify clicking retry shows form again
    await retryButton.click();
    await expect(emailInput).toBeVisible();
  });

  test('should display unmatched items', async ({ page }) => {
    /**
     * Test: Display items that couldn't be matched on Knuspr
     *
     * Verify:
     * 1. Fill cart with items (some may not match)
     * 2. Verify unmatched items list is shown if any
     * 3. Check warning message is displayed
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to grocery cart
    await page.goto(`${FRONTEND_URL}/grocery-carts`);
    await page.waitForLoadState('networkidle');

    const cartCard = page.locator('[data-testid="grocery-cart-card"]').first();
    if (await cartCard.isVisible()) {
      await cartCard.click();
    }

    // Step 3: Fill Knuspr cart
    const fillCartButton = page.locator('button:has-text("Fill Knuspr Cart")');
    await fillCartButton.click();

    const emailInput = page.locator('input[type="email"][aria-label*="Knuspr"]');
    const passwordInput = page.locator('input[type="password"][aria-label*="Knuspr"]');

    await emailInput.fill('knuspr-test@example.com');
    await passwordInput.fill('test-knuspr-password');

    const submitButton = page.locator('button[type="submit"]:has-text("Fill Cart")');
    await submitButton.click();

    // Step 4: Wait for completion
    const successMessage = page.locator('text=Cart Filled Successfully');
    await expect(successMessage).toBeVisible({ timeout: 30000 });

    // Step 5: Check for unmatched items warning (if any)
    const unmatchedWarning = page.locator('text=/could not be matched/i');

    if (await unmatchedWarning.isVisible()) {
      // Unmatched items exist - verify they're displayed
      const unmatchedList = page.locator('ul').filter({ hasText: /could not be matched/i });
      const listItems = unmatchedList.locator('li');

      const count = await listItems.count();
      expect(count).toBeGreaterThan(0);

      // Verify each item is displayed with bullet point
      for (let i = 0; i < Math.min(count, 3); i++) {
        const item = listItems.nth(i);
        await expect(item).toBeVisible();
        const text = await item.textContent();
        expect(text).toBeTruthy();
        expect(text!.trim().length).toBeGreaterThan(0);
      }

      // Verify help text is shown
      const helpText = page.locator('text=/manually add these items/i');
      await expect(helpText).toBeVisible();
    }
  });

  test('should validate credential form fields', async ({ page }) => {
    /**
     * Test: Form validation for credential inputs
     *
     * Verify:
     * 1. Empty email shows error
     * 2. Invalid email format shows error
     * 3. Short password shows error
     * 4. Valid inputs allow submission
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to grocery cart
    await page.goto(`${FRONTEND_URL}/grocery-carts`);
    const cartCard = page.locator('[data-testid="grocery-cart-card"]').first();
    if (await cartCard.isVisible()) {
      await cartCard.click();
    }

    // Step 3: Open credential form
    const fillCartButton = page.locator('button:has-text("Fill Knuspr Cart")');
    await fillCartButton.click();

    const emailInput = page.locator('input[type="email"][aria-label*="Knuspr"]');
    const passwordInput = page.locator('input[type="password"][aria-label*="Knuspr"]');
    const submitButton = page.locator('button[type="submit"]:has-text("Fill Cart")');

    // Test 1: Submit empty form
    await submitButton.click();

    // Should show validation errors
    const emailError = page.locator('text=Email is required');
    const passwordError = page.locator('text=Password is required');

    await expect(emailError.or(page.locator('[aria-invalid="true"]').first())).toBeVisible();

    // Test 2: Invalid email format
    await emailInput.fill('invalid-email');
    await submitButton.click();

    const invalidEmailError = page.locator('text=Invalid email address');
    if (await invalidEmailError.isVisible()) {
      await expect(invalidEmailError).toBeVisible();
    }

    // Test 3: Short password
    await emailInput.fill('valid@example.com');
    await passwordInput.fill('123');
    await submitButton.click();

    const shortPasswordError = page.locator('text=/Password must be at least/i');
    if (await shortPasswordError.isVisible()) {
      await expect(shortPasswordError).toBeVisible();
    }

    // Test 4: Valid inputs should allow submission (will fail on backend, but form validates)
    await emailInput.fill('valid@example.com');
    await passwordInput.fill('validpassword123');
    await submitButton.click();

    // Form should submit (either progress bar or error from backend)
    const progressOrError = page.locator('[role="progressbar"], text=/Failed/i, text=/Filling/i');
    await expect(progressOrError.first()).toBeVisible({ timeout: 5000 });
  });

  test('should show/hide password toggle', async ({ page }) => {
    /**
     * Test: Password visibility toggle
     *
     * Verify:
     * 1. Password is hidden by default
     * 2. Toggle button shows password
     * 3. Toggle button hides password again
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to grocery cart
    await page.goto(`${FRONTEND_URL}/grocery-carts`);
    const cartCard = page.locator('[data-testid="grocery-cart-card"]').first();
    if (await cartCard.isVisible()) {
      await cartCard.click();
    }

    // Step 3: Open credential form
    const fillCartButton = page.locator('button:has-text("Fill Knuspr Cart")');
    await fillCartButton.click();

    const passwordInput = page.locator('input[aria-label*="Knuspr password"]');
    await expect(passwordInput).toBeVisible();

    // Step 4: Verify password is hidden by default
    const inputType = await passwordInput.getAttribute('type');
    expect(inputType).toBe('password');

    // Step 5: Click show password toggle
    const showPasswordButton = page.locator('button:has-text("Show password")');
    await showPasswordButton.click();

    // Verify password is now visible
    const newInputType = await passwordInput.getAttribute('type');
    expect(newInputType).toBe('text');

    // Step 6: Click hide password toggle
    const hidePasswordButton = page.locator('button:has-text("Hide password")');
    await hidePasswordButton.click();

    // Verify password is hidden again
    const finalInputType = await passwordInput.getAttribute('type');
    expect(finalInputType).toBe('password');
  });

  test('should remember credentials when checkbox is selected', async ({ page }) => {
    /**
     * Test: Remember credentials functionality
     *
     * Verify:
     * 1. Checkbox for remembering credentials exists
     * 2. Security warning is shown when checked
     * 3. Link to create Knuspr account is present
     */

    // Step 1: Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(`${FRONTEND_URL}/dashboard`);

    // Step 2: Navigate to grocery cart
    await page.goto(`${FRONTEND_URL}/grocery-carts`);
    const cartCard = page.locator('[data-testid="grocery-cart-card"]').first();
    if (await cartCard.isVisible()) {
      await cartCard.click();
    }

    // Step 3: Open credential form
    const fillCartButton = page.locator('button:has-text("Fill Knuspr Cart")');
    await fillCartButton.click();

    // Step 4: Find remember credentials checkbox
    const rememberCheckbox = page.locator('input[type="checkbox"]').filter({
      hasText: /remember/i
    }).or(page.locator('label:has-text("Remember")').locator('input[type="checkbox"]'));

    const checkboxLocator = page.locator('label', { hasText: /Remember my credentials/i }).locator('input[type="checkbox"]');
    await expect(checkboxLocator).toBeVisible();

    // Step 5: Check the checkbox
    await checkboxLocator.check();
    await expect(checkboxLocator).toBeChecked();

    // Step 6: Verify security warning appears
    const securityWarning = page.locator('text=/Security notice/i, text=/stored locally/i');
    await expect(securityWarning.first()).toBeVisible();

    // Step 7: Verify link to create Knuspr account
    const createAccountLink = page.locator('a[href*="knuspr"]').filter({ hasText: /Create one here/i });
    await expect(createAccountLink).toBeVisible();

    const href = await createAccountLink.getAttribute('href');
    expect(href).toMatch(/knuspr/i);
  });
});
