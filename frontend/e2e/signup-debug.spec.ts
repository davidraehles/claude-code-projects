import { test, expect } from '@playwright/test';

/**
 * Debug tests for signup and login flows on Vercel preview
 */

const VERCEL_PREVIEW_URL = 'https://meal-planner-dab7mgsjm-the-raedical-cos-projects.vercel.app';

test.describe('Auth Flow Debug - Vercel Preview', () => {
  test('should complete signup flow end-to-end', async ({ page }) => {
    // Enable console logging
    page.on('console', msg => console.log('BROWSER:', msg.text()));

    // Capture network errors
    page.on('requestfailed', request => {
      console.log('REQUEST FAILED:', request.url(), request.failure()?.errorText);
    });

    // Capture responses
    page.on('response', response => {
      if (response.url().includes('/auth/') || response.url().includes('/api/')) {
        console.log('API RESPONSE:', response.url(), response.status());
      }
    });

    const testEmail = `test-${Date.now()}@example.com`;
    const testPassword = 'TestPassword123!';

    await test.step('Navigate to signup page', async () => {
      console.log('Navigating to signup...');
      await page.goto(`${VERCEL_PREVIEW_URL}/signup`);
      await page.waitForLoadState('networkidle');
      console.log('Page loaded');
    });

    await test.step('Take screenshot of signup page', async () => {
      await page.screenshot({ path: 'test-results/01-signup-page.png', fullPage: true });
      console.log('Screenshot saved: 01-signup-page.png');
    });

    await test.step('Fill and submit signup form', async () => {
      console.log('Looking for form fields...');

      // Wait for form to be visible
      await page.waitForSelector('form', { timeout: 10000 });

      const emailInput = page.locator('input[type="email"]').first();
      const passwordInputs = page.locator('input[type="password"]');
      const passwordCount = await passwordInputs.count();

      console.log('Email input visible:', await emailInput.isVisible());
      console.log('Password inputs found:', passwordCount);

      await emailInput.fill(testEmail);
      console.log('Filled email:', testEmail);

      // Fill all password fields (password + confirm password)
      for (let i = 0; i < passwordCount; i++) {
        await passwordInputs.nth(i).fill(testPassword);
        console.log(`Filled password field ${i + 1}`);
      }

      // Check for country selector
      const countrySelect = page.locator('select').first();
      if (await countrySelect.isVisible({ timeout: 2000 }).catch(() => false)) {
        await countrySelect.selectOption('US');
        console.log('Selected country: US');
      }

      await page.screenshot({ path: 'test-results/02-form-filled.png', fullPage: true });

      // Find submit button
      const submitButton = page.locator('button[type="submit"]').first();
      console.log('Submit button visible:', await submitButton.isVisible());
      console.log('Submit button text:', await submitButton.textContent());

      // Click and wait for navigation or response
      const [response] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/auth/register'), { timeout: 10000 }).catch(() => null),
        submitButton.click()
      ]);

      if (response) {
        console.log('Register response status:', response.status());
        const body = await response.text().catch(() => 'Could not read body');
        console.log('Register response body:', body);
      } else {
        console.log('No register response captured');
      }

      // Wait a bit to see what happens
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'test-results/03-after-submit.png', fullPage: true });
    });

    await test.step('Check current URL and page state', async () => {
      const currentUrl = page.url();
      console.log('Current URL after submit:', currentUrl);

      // Wait a bit for any errors to populate
      await page.waitForTimeout(1000);

      // Check for error messages (look for error text in various places)
      const errorAlert = await page.locator('[role="alert"]').first().textContent().catch(() => null);
      const errorDiv = await page.locator('.error, [class*="error"]').first().textContent().catch(() => null);
      const errorText = await page.locator('.text-red-500, .text-red-600, .text-danger').first().textContent().catch(() => null);
      
      const allErrors = [errorAlert, errorDiv, errorText].filter(Boolean);
      if (allErrors.length > 0) {
        console.log('Found error messages:', allErrors);
      } else {
        console.log('No error messages found');
      }

      // Check if redirected to dashboard/login
      const isDashboard = currentUrl.includes('/dashboard');
      const isLogin = currentUrl.includes('/login');

      console.log('On dashboard:', isDashboard);
      console.log('On login:', isLogin);

      // Check page content
      const pageText = await page.locator('body').textContent();
      console.log('Page contains "success":', pageText?.toLowerCase().includes('success'));
      console.log('Page contains "error":', pageText?.toLowerCase().includes('error'));

      await page.screenshot({ path: 'test-results/04-final-state.png', fullPage: true });

      // Verify successful signup
      if (isDashboard) {
        console.log('✅ Signup successful - redirected to dashboard');
      } else if (isLogin) {
        console.log('⚠️ Redirected to login page - need to test login separately');
      } else {
        console.log('❌ Still on signup page - check for errors above');
      }
    });
  });

  test('should complete login flow with test credentials', async ({ page }) => {
    // Enable console logging
    page.on('console', msg => console.log('BROWSER:', msg.text()));

    // Capture network errors
    page.on('requestfailed', request => {
      console.log('REQUEST FAILED:', request.url(), request.failure()?.errorText);
    });

    // Capture API responses
    page.on('response', response => {
      if (response.url().includes('/auth/') || response.url().includes('/api/')) {
        console.log('API RESPONSE:', response.url(), response.status());
      }
    });

    const testEmail = 'test@example.com';
    const testPassword = 'testpassword123';

    await test.step('Navigate to login page', async () => {
      console.log('Navigating to login...');
      await page.goto(`${VERCEL_PREVIEW_URL}/login`);
      await page.waitForLoadState('networkidle');
      console.log('Login page loaded');
    });

    await test.step('Take screenshot of login page', async () => {
      await page.screenshot({ path: 'test-results/05-login-page.png', fullPage: true });
      console.log('Screenshot saved: 05-login-page.png');
    });

    await test.step('Fill and submit login form', async () => {
      console.log('Looking for login form fields...');

      await page.waitForSelector('form', { timeout: 10000 });

      const emailInput = page.locator('input[type="email"]').first();
      const passwordInput = page.locator('input[type="password"]').first();

      console.log('Email input visible:', await emailInput.isVisible());
      console.log('Password input visible:', await passwordInput.isVisible());

      await emailInput.fill(testEmail);
      console.log('Filled email:', testEmail);

      await passwordInput.fill(testPassword);
      console.log('Filled password');

      await page.screenshot({ path: 'test-results/06-login-form-filled.png', fullPage: true });

      // Find submit button
      const submitButton = page.locator('button[type="submit"]').first();
      console.log('Submit button visible:', await submitButton.isVisible());
      console.log('Submit button text:', await submitButton.textContent());

      // Click and wait for response
      const [response] = await Promise.all([
        page.waitForResponse(resp =>
          resp.url().includes('/auth/') && resp.request().method() === 'POST',
          { timeout: 15000 }
        ).catch(() => null),
        submitButton.click()
      ]);

      if (response) {
        console.log('Auth response status:', response.status());
        console.log('Auth response URL:', response.url());
      } else {
        console.log('No auth response captured');
      }

      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'test-results/07-after-login.png', fullPage: true });
    });

    await test.step('Check login result', async () => {
      const currentUrl = page.url();
      console.log('Current URL after login:', currentUrl);

      // Check for error messages
      const errorElements = await page.locator('[role="alert"], .error, .text-red-500, .text-red-600').all();
      if (errorElements.length > 0) {
        console.log('Found error messages:');
        for (const el of errorElements) {
          const text = await el.textContent();
          console.log('  -', text);
        }
      } else {
        console.log('No error messages found');
      }

      const isDashboard = currentUrl.includes('/dashboard');
      const isStillLogin = currentUrl.includes('/login');

      console.log('On dashboard:', isDashboard);
      console.log('Still on login:', isStillLogin);

      await page.screenshot({ path: 'test-results/08-login-final-state.png', fullPage: true });

      if (isDashboard) {
        console.log('✅ Login successful - redirected to dashboard');
      } else if (isStillLogin) {
        console.log('❌ Still on login page - login failed');
      } else {
        console.log('⚠️ Unexpected redirect to:', currentUrl);
      }
    });
  });
});
