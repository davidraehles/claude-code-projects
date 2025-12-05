import { test, expect } from '@playwright/test'

/**
 * E2E tests for Grocery Cart View Switching (T027)
 *
 * Tests the toggle functionality between Recipe View and Category View,
 * including session persistence and correct item grouping.
 */

test.describe('Grocery Cart View Switching', () => {
  // This would be a real grocery cart ID in production
  // For testing, we'll need to create or use a test cart
  const TEST_CART_URL = '/grocery-carts/1'

  test.beforeEach(async ({ page }) => {
    // Clear sessionStorage to start fresh
    await page.goto(TEST_CART_URL)
    await page.evaluate(() => sessionStorage.clear())
  })

  test('should toggle between Recipe and Category views', async ({ page }) => {
    await page.goto(TEST_CART_URL)

    // Wait for the page to load
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible
    const viewToggle = page.locator('[role="tablist"]')
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Verify Category View is default
    const categoryButton = page.locator('button[role="tab"][aria-controls="category-view"]')
    const recipeButton = page.locator('button[role="tab"][aria-controls="recipe-view"]')

    await expect(categoryButton).toHaveAttribute('aria-selected', 'true')
    await expect(recipeButton).toHaveAttribute('aria-selected', 'false')

    // Verify category view is displayed
    const categoryView = page.locator('#category-view')
    await expect(categoryView).toBeVisible()

    // Click "Recipe View" toggle button
    await recipeButton.click()
    await page.waitForTimeout(500) // Wait for transition

    // Verify Recipe View is now active
    await expect(recipeButton).toHaveAttribute('aria-selected', 'true')
    await expect(categoryButton).toHaveAttribute('aria-selected', 'false')

    // Verify recipe-grouped display appears
    const recipeView = page.locator('#recipe-view')
    await expect(recipeView).toBeVisible()

    // Check recipe names are visible as section headers (looking for recipe emoji)
    const recipeHeaders = page.locator('h3:has-text("🍽️")')
    const headerCount = await recipeHeaders.count()
    expect(headerCount).toBeGreaterThan(0)

    // Click "Category View" toggle button
    await categoryButton.click()
    await page.waitForTimeout(500)

    // Verify Category View is active again
    await expect(categoryButton).toHaveAttribute('aria-selected', 'true')
    await expect(recipeButton).toHaveAttribute('aria-selected', 'false')

    // Verify category-grouped display appears
    await expect(categoryView).toBeVisible()

    // Check category names are visible (looking for category icons)
    const categoryHeaders = page.locator('h3:has-text("🥬"), h3:has-text("🥛"), h3:has-text("🥩"), h3:has-text("🐟"), h3:has-text("🍞"), h3:has-text("🥫"), h3:has-text("🧊"), h3:has-text("🥤"), h3:has-text("📦")')
    const categoryCount = await categoryHeaders.count()
    expect(categoryCount).toBeGreaterThan(0)
  })

  test('should persist view mode during session', async ({ page }) => {
    await page.goto(TEST_CART_URL)

    // Wait for the page to load
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible
    const viewToggle = page.locator('[role="tablist"]')
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Switch to Recipe View
    const recipeButton = page.locator('button[role="tab"][aria-controls="recipe-view"]')
    await recipeButton.click()
    await page.waitForTimeout(500)

    // Verify Recipe View is active
    await expect(recipeButton).toHaveAttribute('aria-selected', 'true')

    // Navigate away (to meal plans)
    await page.goto('/meal-plans')
    await page.waitForLoadState('networkidle')

    // Navigate back to the cart
    await page.goto(TEST_CART_URL)
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible again
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Verify Recipe View is still selected
    await expect(recipeButton).toHaveAttribute('aria-selected', 'true')

    // Verify recipe view content is displayed
    const recipeView = page.locator('#recipe-view')
    await expect(recipeView).toBeVisible()
  })

  test('should display items correctly in Recipe view', async ({ page }) => {
    await page.goto(TEST_CART_URL)

    // Wait for the page to load
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible
    const viewToggle = page.locator('[role="tablist"]')
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Switch to Recipe View
    const recipeButton = page.locator('button[role="tab"][aria-controls="recipe-view"]')
    await recipeButton.click()
    await page.waitForTimeout(500)

    // Verify recipe view is displayed
    const recipeView = page.locator('#recipe-view')
    await expect(recipeView).toBeVisible()

    // Check that items are grouped by recipe
    const recipeCards = recipeView.locator('[class*="Card"]')
    const cardCount = await recipeCards.count()
    expect(cardCount).toBeGreaterThan(0)

    // Check that each recipe card has a title with the recipe emoji
    for (let i = 0; i < Math.min(cardCount, 3); i++) {
      const card = recipeCards.nth(i)
      const title = card.locator('h3')
      const titleText = await title.textContent()
      expect(titleText).toBeTruthy()

      // Check that the card has items listed
      const items = card.locator('input[type="checkbox"]')
      const itemCount = await items.count()
      expect(itemCount).toBeGreaterThan(0)
    }

    // Verify that items can be checked
    const firstCheckbox = recipeView.locator('input[type="checkbox"]').first()
    await firstCheckbox.check()
    await expect(firstCheckbox).toBeChecked()
  })

  test('should display items correctly in Category view', async ({ page }) => {
    await page.goto(TEST_CART_URL)

    // Wait for the page to load
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible
    const viewToggle = page.locator('[role="tablist"]')
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Category view should be default
    const categoryButton = page.locator('button[role="tab"][aria-controls="category-view"]')
    await expect(categoryButton).toHaveAttribute('aria-selected', 'true')

    // Verify category view is displayed
    const categoryView = page.locator('#category-view')
    await expect(categoryView).toBeVisible()

    // Check that items are grouped by category
    const categoryCards = categoryView.locator('[class*="Card"]')
    const cardCount = await categoryCards.count()
    expect(cardCount).toBeGreaterThan(0)

    // Check that each category card has a title
    for (let i = 0; i < Math.min(cardCount, 3); i++) {
      const card = categoryCards.nth(i)
      const title = card.locator('h3')
      const titleText = await title.textContent()
      expect(titleText).toBeTruthy()

      // Check that the card has items listed
      const items = card.locator('input[type="checkbox"]')
      const itemCount = await items.count()
      expect(itemCount).toBeGreaterThan(0)
    }

    // Check for "Uncategorized" section if items without categories exist
    const allTitles = await categoryView.locator('h3').allTextContents()
    const hasUncategorized = allTitles.some((title) => title.includes('Uncategorized') || title.includes('📦'))
    // This is informational - uncategorized items may or may not exist
    console.log('Has uncategorized items:', hasUncategorized)

    // Verify that items can be checked
    const firstCheckbox = categoryView.locator('input[type="checkbox"]').first()
    await firstCheckbox.check()
    await expect(firstCheckbox).toBeChecked()
  })

  test('should maintain checked state when switching views', async ({ page }) => {
    await page.goto(TEST_CART_URL)

    // Wait for the page to load
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible
    const viewToggle = page.locator('[role="tablist"]')
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Category view is default - check some items
    const categoryView = page.locator('#category-view')
    const firstCheckbox = categoryView.locator('input[type="checkbox"]').first()
    const secondCheckbox = categoryView.locator('input[type="checkbox"]').nth(1)

    await firstCheckbox.check()
    await secondCheckbox.check()

    await expect(firstCheckbox).toBeChecked()
    await expect(secondCheckbox).toBeChecked()

    // Switch to Recipe View
    const recipeButton = page.locator('button[role="tab"][aria-controls="recipe-view"]')
    await recipeButton.click()
    await page.waitForTimeout(500)

    // Verify the same items are still checked in Recipe View
    const recipeView = page.locator('#recipe-view')
    const checkedItemsInRecipeView = recipeView.locator('input[type="checkbox"]:checked')
    const checkedCount = await checkedItemsInRecipeView.count()
    expect(checkedCount).toBeGreaterThanOrEqual(2)

    // Switch back to Category View
    const categoryButton = page.locator('button[role="tab"][aria-controls="category-view"]')
    await categoryButton.click()
    await page.waitForTimeout(500)

    // Verify items are still checked
    await expect(firstCheckbox).toBeChecked()
    await expect(secondCheckbox).toBeChecked()
  })

  test('should export text in current view mode', async ({ page }) => {
    await page.goto(TEST_CART_URL)

    // Wait for the page to load
    await page.waitForLoadState('networkidle')

    // Wait for view toggle to be visible
    const viewToggle = page.locator('[role="tablist"]')
    await expect(viewToggle).toBeVisible({ timeout: 10000 })

    // Switch to Recipe View
    const recipeButton = page.locator('button[role="tab"][aria-controls="recipe-view"]')
    await recipeButton.click()
    await page.waitForTimeout(500)

    // Find and verify export button exists
    const exportButton = page.locator('button:has-text("Export TXT")')
    await expect(exportButton).toBeVisible()

    // Note: Actually testing the download would require additional setup
    // This test just verifies the button is present and clickable
    await expect(exportButton).toBeEnabled()
  })
})
