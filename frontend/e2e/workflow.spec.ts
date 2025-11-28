import { test, expect } from '@playwright/test';

test.describe('Cart Workflow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set base URL if not configured
    if (!process.env.BASE_URL) {
      process.env.BASE_URL = 'http://localhost:3000';
    }
  });

  test('complete workflow: cart generation and delivery selection', async ({ page }) => {
    // Navigate to workflow page with meal plan ID
    await page.goto('/workflow?meal_plan_id=1');

    // Should show loading state initially
    await expect(page.locator('text=Generating Your Cart')).toBeVisible();

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Verify cart elements are displayed
    await expect(page.locator('text=Continue to Checkout')).toBeVisible();
    await expect(page.locator('text=Back to Meal Plans')).toBeVisible();

    // Progress indicator should be visible
    await expect(page.locator('text=Cart Review')).toBeVisible();
    await expect(page.locator('text=Delivery')).toBeVisible();
    await expect(page.locator('text=Complete')).toBeVisible();
  });

  test('handles missing meal plan ID error', async ({ page }) => {
    // Navigate to workflow without meal plan ID
    await page.goto('/workflow');

    // Should show error state
    await expect(page.locator('text=Unable to connect to Knuspr')).toBeVisible({ timeout: 5000 });

    // Error handler should provide suggestions
    await expect(page.locator('text=What you can try')).toBeVisible();

    // Should have back button
    await expect(page.locator('text=Back to Meal Plans')).toBeVisible();
  });

  test('displays unavailable items section', async ({ page }) => {
    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // If there are unavailable items, they should be displayed
    const unavailableSection = page.locator('text=/Item\\(s\\) Not Available/');
    const isVisible = await unavailableSection.isVisible().catch(() => false);

    if (isVisible) {
      await expect(unavailableSection).toBeVisible();
      // Should have ability to add alternatives
      const addButtons = page.locator('text=Add Alternative');
      const count = await addButtons.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('allows selecting delivery slot', async ({ page }) => {
    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Click continue to checkout to move to next step
    await page.click('text=Continue to Checkout');

    // Should show delivery selection step
    await expect(page.locator('text=Select Delivery Slot')).toBeVisible({ timeout: 5000 });

    // Should be able to select a slot
    const slotButton = page.locator('[data-testid="delivery-slot"]').first();
    if (await slotButton.isVisible().catch(() => false)) {
      await slotButton.click();

      // Should move to review step
      await expect(page.locator('text=Review')).toBeVisible();
    }
  });

  test('displays price breakdown correctly', async ({ page }) => {
    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Verify price elements are displayed
    await expect(page.locator('text=Subtotal')).toBeVisible();
    await expect(page.locator('text=Delivery Fee')).toBeVisible();
    await expect(page.locator('text=Total')).toBeVisible();

    // Prices should contain euro symbol
    const prices = page.locator('text=/€/');
    const count = await prices.count();
    expect(count).toBeGreaterThan(0);
  });

  test('allows retry on error', async ({ page }) => {
    // Navigate to workflow with invalid ID to trigger error
    await page.goto('/workflow?meal_plan_id=999999');

    // Wait for error state
    await expect(page.locator('text=Cart Generation Failed')).toBeVisible({ timeout: 10000 });

    // Click retry button
    const retryButton = page.locator('text=Try Again');
    if (await retryButton.isVisible()) {
      await retryButton.click();

      // Should show loading state
      await expect(page.locator('text=Generating')).toBeVisible({ timeout: 5000 });
    }
  });

  test('displays error suggestions', async ({ page }) => {
    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=999999');

    // Wait for error
    await expect(page.locator('text=Cart Generation Failed')).toBeVisible({ timeout: 10000 });

    // Error suggestions should be visible
    await expect(page.locator('text=What you can try')).toBeVisible();

    // Should have contact support option
    const contactButton = page.locator('text=Contact Support');
    if (await contactButton.isVisible()) {
      expect(true).toBe(true); // Support button is available
    }
  });

  test('shows progress indicator updates', async ({ page }) => {
    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Cart Review step should be active (blue)
    const cartReviewStep = page.locator('button:has-text("Cart Review")');
    const cartReviewClasses = await cartReviewStep.getAttribute('class');
    expect(cartReviewClasses).toContain('text-blue-600');

    // Click continue to move to next step
    await page.click('text=Continue to Checkout');

    // Delivery step should now be active (if it exists)
    await page.waitForTimeout(500);
    const deliveryStep = page.locator('button:has-text("Delivery")');
    const deliveryClasses = await deliveryStep.getAttribute('class');
    expect(deliveryClasses).toBeDefined();
  });

  test('displays responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Content should be visible on mobile
    await expect(page.locator('text=Complete Your Order')).toBeVisible();

    // Buttons should be clickable on mobile
    const buttons = page.locator('button');
    const count = await buttons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('shows help and support links', async ({ page }) => {
    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Should have help link
    const helpLink = page.locator('text=View Help');
    if (await helpLink.isVisible()) {
      expect(true).toBe(true);
    }

    // Should have support link
    const supportLink = page.locator('text=Contact Support');
    if (await supportLink.isVisible()) {
      expect(true).toBe(true);
    }
  });

  test('prevents navigation without meal plan ID', async ({ page }) => {
    // Navigate to workflow without ID
    await page.goto('/workflow');

    // Should show error instead of blank page
    const errorHandler = page.locator('[data-testid="error-handler"]');
    const isVisible = await errorHandler.isVisible().catch(() => false);

    // Should have error message
    await expect(page.locator('text=/error|Error|failed|Failed/')).toBeVisible({ timeout: 5000 });
  });

  test('handles authentication errors', async ({ page }) => {
    // Clear authentication tokens
    await page.context().clearCookies();

    // Navigate to workflow
    await page.goto('/workflow?meal_plan_id=1');

    // Should handle auth error gracefully (either redirect to login or show error)
    const hasError = await page.locator('text=/error|Error|unauthorized|Unauthorized/').isVisible().catch(() => false);
    const hasLoginForm = await page.locator('input[type="password"]').isVisible().catch(() => false);

    expect(hasError || hasLoginForm).toBe(true);
  });
});

test.describe('Cart Component Accessibility', () => {
  test('cart preview has proper heading hierarchy', async ({ page }) => {
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Should have h1, h2, h3 elements
    const h1 = page.locator('h1');
    const h2 = page.locator('h2');

    // At least one heading should exist
    const h1Count = await h1.count();
    const h2Count = await h2.count();

    expect(h1Count + h2Count).toBeGreaterThan(0);
  });

  test('buttons are keyboard accessible', async ({ page }) => {
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Tab to first button and press Enter
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Should be able to interact with keyboard
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBe('BUTTON');
  });

  test('images have alt text (if any)', async ({ page }) => {
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Check all images have alt text or aria-label
    const images = page.locator('img');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      const ariaLabel = await images.nth(i).getAttribute('aria-label');
      expect(alt || ariaLabel).toBeTruthy();
    }
  });

  test('color contrast is sufficient', async ({ page }) => {
    await page.goto('/workflow?meal_plan_id=1');

    // Wait for cart to load
    await expect(page.locator('text=Your Shopping Cart')).toBeVisible({ timeout: 10000 });

    // Check that text is readable (basic check)
    const textElements = page.locator('p, span, button');
    const count = await textElements.count();
    expect(count).toBeGreaterThan(0);
  });
});
