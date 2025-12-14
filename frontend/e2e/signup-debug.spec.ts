import { test, expect } from '@playwright/test';

/**
 * Debug test for signup flow on current Vercel preview
 */

const VERCEL_PREVIEW_URL = 'https://meal-planner-b2cj0bijb-the-raedical-cos-projects.vercel.app';

test.describe('Signup Debug - Vercel Preview', () => {
  test('should complete signup and show detailed debugging', async ({ page }) => {
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
      const passwordInput = page.locator('input[type="password"]').first();
      
      console.log('Email input visible:', await emailInput.isVisible());
      console.log('Password input visible:', await passwordInput.isVisible());
      
      await emailInput.fill(testEmail);
      console.log('Filled email:', testEmail);
      
      await passwordInput.fill(testPassword);
      console.log('Filled password');
      
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
      
      // Check for error messages
      const errorElements = await page.locator('[role="alert"], .error, .text-red-500, .text-red-600').all();
      if (errorElements.length > 0) {
        console.log('Found error messages:');
        for (const el of errorElements) {
          const text = await el.textContent();
          console.log('  -', text);
        }
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
    });
  });
});
