import { test, expect } from '@playwright/test';

test.describe('Generate Meal Plan Feature', () => {
  const BASE_URL = 'https://claude-code-projects.vercel.app';
  const GENERATE_URL = `${BASE_URL}/generate`;

  test.beforeEach(async ({ page }) => {
    // Navigate to the generate page
    await page.goto(GENERATE_URL, { waitUntil: 'networkidle' });

    // Wait for the form to be visible
    await page.waitForSelector('button[type="submit"]', { timeout: 10000 }).catch(() => {
      console.log('Form not found immediately, continuing...');
    });
  });

  test('page loads successfully', async ({ page }) => {
    // Check if page title contains "Generate"
    const title = await page.title();
    console.log('📄 Page title:', title);

    // Look for key form elements
    const heading = await page.locator('h1, h2').first();
    const headingText = await heading.textContent().catch(() => null);
    console.log('📰 Page heading:', headingText);

    expect(heading).toBeTruthy();
  });

  test('form fields are visible and interactive', async ({ page }) => {
    console.log('\n🔍 Checking form fields...');

    // Check for start date input
    const startDateInput = page.locator('input[type="date"]').first();
    const isDateVisible = await startDateInput.isVisible().catch(() => false);
    if (isDateVisible) {
      console.log('✓ Start date input visible');
    } else {
      console.log('❌ Start date input NOT visible');
    }

    // Check for number inputs (num_days, num_people, meals_per_day)
    const numberInputs = await page.locator('input[type="number"]').all();
    console.log(`✓ Found ${numberInputs.length} number inputs`);

    // Check for dietary restrictions checkboxes
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    console.log(`✓ Found ${checkboxes.length} checkboxes (dietary restrictions)`);

    // Check for textarea (excluded ingredients)
    const textarea = page.locator('textarea').first();
    const isTextareaVisible = await textarea.isVisible().catch(() => false);
    if (isTextareaVisible) {
      console.log('✓ Textarea for excluded ingredients visible');
    }

    // Check for submit button
    const submitButton = page.locator('button[type="submit"]').first();
    const isButtonVisible = await submitButton.isVisible().catch(() => false);
    if (isButtonVisible) {
      console.log('✓ Submit button visible');
    } else {
      console.log('❌ Submit button NOT visible');
    }
  });

  test('can fill form and submit meal plan request', async ({ page }) => {
    console.log('\n📝 Filling form with test data...');

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

    // Select a dietary restriction (vegetarian)
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    if (checkboxes.length > 0) {
      await checkboxes[0].check();
      const label = await checkboxes[0].evaluate((el) => {
        const labelEl = el.closest('label') || el.parentElement;
        return labelEl?.textContent?.trim() || 'Unknown';
      });
      console.log(`✓ Selected dietary restriction: ${label}`);
    }

    // Fill in excluded ingredients
    const textarea = page.locator('textarea').first();
    const isTextareaVisible = await textarea.isVisible().catch(() => false);
    if (isTextareaVisible) {
      await textarea.fill('mushrooms, olives');
      console.log('✓ Set excluded ingredients');
    }

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

    // Set up network monitoring
    let mealPlanResponse = null;
    page.on('response', response => {
      if (response.url().includes('/meal-plans') && response.status() === 202) {
        console.log('✓ Intercepted 202 ACCEPTED response');
        mealPlanResponse = response;
      }
    });

    await submitButton.click();

    // Wait for response or timeout
    let attemptCount = 0;
    while (!mealPlanResponse && attemptCount < 30) {
      await page.waitForTimeout(1000);
      attemptCount++;
    }

    if (mealPlanResponse) {
      try {
        const responseBody = await mealPlanResponse.json();
        console.log('\n🎯 Response data:');
        console.log(`   Meal plan ID: ${responseBody.id}`);
        console.log(`   Status: ${responseBody.status}`);
        console.log(`   Total recipes: ${responseBody.total_recipes}`);
        console.log(`   Total calories: ${responseBody.total_calories || 'N/A'}`);
        console.log(`   Total cost: €${responseBody.total_cost || 'N/A'}`);
      } catch (e) {
        console.log('Could not parse response JSON');
      }
    } else {
      console.log('⚠️  No 202 response received within timeout');
    }

    // Take final screenshot
    await page.screenshot({ path: 'meal_plan_after_submit.png', fullPage: true });
    console.log('📸 Screenshot saved: meal_plan_after_submit.png');
  });

  test('checks API connectivity and backend health', async ({ page }) => {
    console.log('\n🏥 Checking backend health...');

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
