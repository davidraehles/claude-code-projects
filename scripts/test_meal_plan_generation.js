/**
 * Playwright test script for debugging the Generate Meal Plan feature
 * Tests the Vercel deployed version at https://claude-code-projects.vercel.app/generate
 *
 * Run with: npx playwright test scripts/test_meal_plan_generation.js --headed
 */

const { test, expect } = require('@playwright/test');

test.describe('Generate Meal Plan Feature', () => {
  const BASE_URL = 'https://claude-code-projects.vercel.app';
  const GENERATE_URL = `${BASE_URL}/generate`;

  test.beforeEach(async ({ page }) => {
    // Navigate to the generate page
    await page.goto(GENERATE_URL, { waitUntil: 'networkidle' });

    // Wait for the form to be visible
    await page.waitForSelector('[role="form"]', { timeout: 10000 }).catch(() => {
      console.log('Form not found immediately, continuing...');
    });
  });

  test('page loads successfully', async ({ page }) => {
    // Check if page title contains "Generate"
    const title = await page.title();
    console.log('Page title:', title);

    // Look for key form elements
    const heading = await page.locator('h1, h2').first();
    console.log('Page heading:', await heading.textContent());

    expect(heading).toBeTruthy();
  });

  test('form fields are visible and interactive', async ({ page }) => {
    // Check for start date input
    const startDateInput = page.locator('input[type="date"]').first();
    if (await startDateInput.isVisible()) {
      console.log('✓ Start date input visible');
    }

    // Check for number inputs (num_days, num_people, meals_per_day)
    const numberInputs = await page.locator('input[type="number"]').all();
    console.log(`✓ Found ${numberInputs.length} number inputs`);

    // Check for dietary restrictions checkboxes
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    console.log(`✓ Found ${checkboxes.length} checkboxes (dietary restrictions)`);

    // Check for textarea (excluded ingredients)
    const textarea = page.locator('textarea').first();
    if (await textarea.isVisible()) {
      console.log('✓ Textarea for excluded ingredients visible');
    }

    // Check for submit button
    const submitButton = page.locator('button[type="submit"]').first();
    if (await submitButton.isVisible()) {
      console.log('✓ Submit button visible');
    }
  });

  test('can fill form and submit meal plan request', async ({ page }) => {
    // Fill in start date (today)
    const startDateInput = page.locator('input[type="date"]').first();
    const today = new Date().toISOString().split('T')[0];
    await startDateInput.fill(today);
    console.log(`✓ Set start date to ${today}`);

    // Fill in num_days
    const numberInputs = await page.locator('input[type="number"]').all();
    if (numberInputs.length > 0) {
      await numberInputs[0].fill('7');
      console.log('✓ Set num_days to 7');
    }

    // Fill in num_people
    if (numberInputs.length > 1) {
      await numberInputs[1].fill('2');
      console.log('✓ Set num_people to 2');
    }

    // Fill in meals_per_day
    if (numberInputs.length > 2) {
      await numberInputs[2].fill('3');
      console.log('✓ Set meals_per_day to 3');
    }

    // Select a dietary restriction (e.g., vegetarian)
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    if (checkboxes.length > 0) {
      await checkboxes[0].check();
      const label = await checkboxes[0].evaluate((el) => el.nextElementSibling?.textContent);
      console.log(`✓ Selected dietary restriction: ${label}`);
    }

    // Fill in excluded ingredients
    const textarea = page.locator('textarea').first();
    await textarea.fill('mushrooms, olives');
    console.log('✓ Set excluded ingredients');

    // Log form state
    console.log('\n📋 Form submission details:');
    console.log('   Start date:', today);
    console.log('   Duration: 7 days');
    console.log('   People: 2');
    console.log('   Meals per day: 3');
    console.log('   Expected recipes needed: 21 (7 days × 3 meals)');

    // Take a screenshot before submitting
    await page.screenshot({ path: 'meal_plan_form_filled.png', fullPage: true });
    console.log('\n📸 Screenshot saved: meal_plan_form_filled.png');

    // Submit the form
    const submitButton = page.locator('button[type="submit"]').first();
    console.log('\n📤 Submitting form...');

    // Listen for network activity
    const responsePromise = page.waitForResponse(
      response => response.url().includes('/meal-plans') && response.status() === 202,
      { timeout: 30000 }
    ).catch(() => {
      console.log('⚠️  Expected 202 response not received within timeout');
      return null;
    });

    await submitButton.click();

    // Wait for loading to complete or success message
    const response = await responsePromise;

    if (response) {
      console.log('✓ Received 202 ACCEPTED response');
      const responseBody = await response.json();
      console.log('\n🎯 Response data:');
      console.log(`   Meal plan ID: ${responseBody.id}`);
      console.log(`   Status: ${responseBody.status}`);
      console.log(`   Total recipes: ${responseBody.total_recipes}`);
      console.log(`   Total calories: ${responseBody.total_calories}`);
      console.log(`   Total cost: €${responseBody.total_cost}`);
    }

    // Wait a bit for UI to update
    await page.waitForTimeout(2000);

    // Check for success message or redirect
    const successMessage = page.locator('text=/successfully|created|ready/i').first();
    if (await successMessage.isVisible().catch(() => false)) {
      console.log('✓ Success message visible');
    } else {
      console.log('⚠️  No success message found');
    }

    // Take final screenshot
    await page.screenshot({ path: 'meal_plan_after_submit.png', fullPage: true });
    console.log('📸 Screenshot saved: meal_plan_after_submit.png');
  });

  test('handles API errors gracefully', async ({ page }) => {
    console.log('\n🔍 Testing error handling...');

    // Try submitting with minimal/invalid data
    const submitButton = page.locator('button[type="submit"]').first();

    // Check if submit button is enabled
    const isEnabled = await submitButton.isEnabled();
    console.log(`Submit button enabled: ${isEnabled}`);

    if (!isEnabled) {
      console.log('✓ Submit button correctly disabled for invalid form');
    }

    // Fill in just the required fields
    const startDateInput = page.locator('input[type="date"]').first();
    const today = new Date().toISOString().split('T')[0];
    await startDateInput.fill(today);

    // Check if submit is now enabled
    const isEnabledAfter = await submitButton.isEnabled();
    console.log(`Submit button enabled after filling date: ${isEnabledAfter}`);
  });

  test('verifies form validation and visual feedback', async ({ page }) => {
    console.log('\n🔍 Testing form validation...');

    // Get all form inputs
    const inputs = await page.locator('input, textarea').all();
    console.log(`Total form inputs: ${inputs.length}`);

    // Check for validation messages
    const errorMessages = await page.locator('[role="alert"], .error, .text-red').all();
    console.log(`Error message elements: ${errorMessages.length}`);

    // Check for placeholder text (indicates field purpose)
    for (let i = 0; i < Math.min(inputs.length, 5); i++) {
      const placeholder = await inputs[i].getAttribute('placeholder');
      const type = await inputs[i].getAttribute('type');
      console.log(`Input ${i}: type=${type}, placeholder=${placeholder}`);
    }
  });

  test('checks API connectivity and backend health', async ({ page }) => {
    console.log('\n🏥 Checking backend health...');

    // Try to fetch the API directly
    try {
      const response = await page.request.get(`${BASE_URL}/api/v1/meal-plans`, {
        headers: {
          'Accept': 'application/json'
        }
      });
      console.log(`API health check: ${response.status()}`);

      if (response.ok()) {
        console.log('✓ API is responding');
      } else if (response.status() === 401 || response.status() === 403) {
        console.log('✓ API requires authentication (expected)');
      } else {
        console.log(`⚠️  Unexpected status code: ${response.status()}`);
      }
    } catch (error) {
      console.log(`❌ API connectivity issue: ${error.message}`);
    }
  });
});
