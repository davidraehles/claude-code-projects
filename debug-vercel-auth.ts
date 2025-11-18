/**
 * Playwright debug script for Vercel frontend auth issue
 * Investigates why recipe import fails with "Not authenticated" error
 */

import { chromium, Browser, Page } from 'playwright';

const VERCEL_URL = 'https://claude-code-projects.vercel.app';
const TEST_EMAIL = `test-${Date.now()}@example.com`;
const TEST_PASSWORD = 'TestPassword123!';
const TEST_RECIPE_URL = 'https://www.bbcgoodfood.com/recipes/chocolate-cake';

interface AuthDebugReport {
  signupSuccess: boolean;
  loginSuccess: boolean;
  tokenInLocalStorage: string | null;
  tokenFromContext: string | null;
  requestHeaders: Record<string, string>;
  apiResponse: {
    status: number;
    statusText: string;
    body: any;
  } | null;
  consoleErrors: string[];
  networkErrors: string[];
}

async function debugVercelAuth(): Promise<AuthDebugReport> {
  console.log('🔍 Starting Vercel auth debugging...\n');

  const report: AuthDebugReport = {
    signupSuccess: false,
    loginSuccess: false,
    tokenInLocalStorage: null,
    tokenFromContext: null,
    requestHeaders: {},
    apiResponse: null,
    consoleErrors: [],
    networkErrors: [],
  };

  const browser: Browser = await chromium.launch({
    headless: false, // Keep browser open to see what happens
    slowMo: 500 // Slow down for visibility
  });

  try {
    const context = await browser.newContext({
      recordVideo: { dir: '/home/darae/claude-code-projects/playwright-videos' }
    });
    const page: Page = await context.newPage();

    // Capture console messages
    page.on('console', (msg) => {
      const text = msg.text();
      console.log(`[CONSOLE ${msg.type()}] ${text}`);
      if (msg.type() === 'error') {
        report.consoleErrors.push(text);
      }
    });

    // Capture network requests to import endpoint
    page.on('requestfinished', async (request) => {
      if (request.url().includes('/api/v1/recipes/harvest')) {
        console.log(`\n📡 IMPORT REQUEST CAPTURED:`);
        console.log(`URL: ${request.url()}`);
        console.log(`Method: ${request.method()}`);

        const headers = await request.allHeaders();
        report.requestHeaders = headers;
        console.log(`Headers:`, JSON.stringify(headers, null, 2));

        try {
          const response = await request.response();
          if (response) {
            const status = response.status();
            const statusText = response.statusText();
            console.log(`\n📥 IMPORT RESPONSE:`);
            console.log(`Status: ${status} ${statusText}`);

            const body = await response.json().catch(() => response.text());
            console.log(`Body:`, JSON.stringify(body, null, 2));

            report.apiResponse = { status, statusText, body };
          }
        } catch (e) {
          console.error('Error getting response:', e);
        }
      }
    });

    // Capture failed requests
    page.on('requestfailed', (request) => {
      const error = `${request.method()} ${request.url()} - ${request.failure()?.errorText}`;
      console.log(`[NETWORK ERROR] ${error}`);
      report.networkErrors.push(error);
    });

    // === STEP 1: Navigate to home page ===
    console.log('\n📍 Step 1: Navigating to home page...');
    await page.goto(VERCEL_URL, { waitUntil: 'networkidle' });
    await page.screenshot({ path: '/home/darae/claude-code-projects/01-homepage.png', fullPage: true });

    // === STEP 2: Check if signup page exists ===
    console.log('\n📍 Step 2: Looking for signup/login page...');

    // Try to find signup or login link
    const signupLink = page.locator('a[href*="signup"], a[href*="register"], button:has-text("Sign up"), button:has-text("Register")').first();
    const loginLink = page.locator('a[href*="login"], a[href*="signin"], button:has-text("Log in"), button:has-text("Sign in")').first();

    let authPageFound = false;

    if (await signupLink.isVisible().catch(() => false)) {
      console.log('✅ Found signup link');
      await signupLink.click();
      await page.waitForLoadState('networkidle');
      authPageFound = true;
    } else if (await loginLink.isVisible().catch(() => false)) {
      console.log('✅ Found login link');
      await loginLink.click();
      await page.waitForLoadState('networkidle');
      authPageFound = true;
    } else {
      // Check if there's a direct auth form on the page
      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      if (await emailInput.isVisible().catch(() => false)) {
        console.log('✅ Found auth form on current page');
        authPageFound = true;
      }
    }

    if (!authPageFound) {
      console.log('❌ No auth page found. Taking screenshot...');
      await page.screenshot({ path: '/home/darae/claude-code-projects/02-no-auth-page.png', fullPage: true });

      // Try navigating directly to import page to trigger auth
      console.log('📍 Attempting direct navigation to /import...');
      await page.goto(`${VERCEL_URL}/import`, { waitUntil: 'networkidle' });
      await page.screenshot({ path: '/home/darae/claude-code-projects/03-import-page.png', fullPage: true });
    }

    // Wait a bit for auth initialization
    await page.waitForTimeout(2000);

    // === STEP 3: Check localStorage for token ===
    console.log('\n📍 Step 3: Checking localStorage for auth token...');
    const token = await page.evaluate(() => {
      return localStorage.getItem('auth_token');
    });

    report.tokenInLocalStorage = token;
    console.log(`Token in localStorage: ${token ? '✅ PRESENT (length: ' + token.length + ')' : '❌ MISSING'}`);

    if (token) {
      console.log(`Token preview: ${token.substring(0, 20)}...`);
      report.loginSuccess = true;
    }

    // === STEP 4: Check auth context state ===
    console.log('\n📍 Step 4: Checking auth context state...');
    await page.waitForTimeout(1000);

    // Look for user email or auth indicators
    const userEmail = await page.evaluate(() => {
      return localStorage.getItem('user_email');
    });
    console.log(`User email in localStorage: ${userEmail || 'None'}`);

    // === STEP 5: Navigate to import page if not there ===
    const currentUrl = page.url();
    if (!currentUrl.includes('/import')) {
      console.log('\n📍 Step 5: Navigating to /import page...');
      await page.goto(`${VERCEL_URL}/import`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(2000);
    }

    await page.screenshot({ path: '/home/darae/claude-code-projects/04-import-page-ready.png', fullPage: true });

    // === STEP 6: Fill in recipe URL and submit ===
    console.log('\n📍 Step 6: Attempting to import recipe...');

    // Wait for the form to be ready
    const urlInput = page.locator('input[type="url"], input[placeholder*="recipe"], input[placeholder*="URL"]').first();
    await urlInput.waitFor({ state: 'visible', timeout: 5000 });

    // Fill in the URL
    await urlInput.fill(TEST_RECIPE_URL);
    console.log(`✅ Filled URL: ${TEST_RECIPE_URL}`);

    // Find and click submit button
    const submitButton = page.locator('button[type="submit"], button:has-text("Import")').first();
    await submitButton.waitFor({ state: 'visible', timeout: 5000 });

    console.log('🔘 Clicking import button...');
    await submitButton.click();

    // Wait for response
    await page.waitForTimeout(3000);

    // Take screenshot of result
    await page.screenshot({ path: '/home/darae/claude-code-projects/05-import-result.png', fullPage: true });

    // === STEP 7: Check for error messages ===
    console.log('\n📍 Step 7: Checking for error messages...');
    const errorMessages = await page.locator('[class*="error"], [class*="alert-danger"], [class*="bg-red"]').allTextContents();
    if (errorMessages.length > 0) {
      console.log('❌ Error messages found:');
      errorMessages.forEach(msg => console.log(`  - ${msg}`));
    }

    // Final localStorage check
    const finalToken = await page.evaluate(() => {
      return localStorage.getItem('auth_token');
    });
    console.log(`\n📍 Final token check: ${finalToken ? '✅ Still present' : '❌ Missing'}`);

    // Keep browser open for 5 seconds to inspect
    console.log('\n⏱️  Keeping browser open for 10 seconds for inspection...');
    await page.waitForTimeout(10000);

  } catch (error) {
    console.error('\n❌ Error during debugging:', error);
    throw error;
  } finally {
    await browser.close();
  }

  return report;
}

// Run the debug script
debugVercelAuth()
  .then((report) => {
    console.log('\n' + '='.repeat(80));
    console.log('📊 FINAL REPORT');
    console.log('='.repeat(80));
    console.log(JSON.stringify(report, null, 2));
    console.log('='.repeat(80));

    // Diagnosis
    console.log('\n🔬 DIAGNOSIS:');
    if (!report.tokenInLocalStorage) {
      console.log('❌ PRIMARY ISSUE: No auth token in localStorage');
      console.log('   → The AuthContext should auto-login with test user on page load');
      console.log('   → Check if initTestAuth() is being called');
      console.log('   → Check browser console for auth errors');
    } else if (report.apiResponse?.status === 401) {
      console.log('❌ PRIMARY ISSUE: Token present but backend rejects it (401)');
      console.log('   → Check if Authorization header is properly formatted');
      console.log('   → Verify token is valid (not expired)');
      console.log('   → Check backend auth endpoint');
    } else if (!report.requestHeaders.authorization && !report.requestHeaders.Authorization) {
      console.log('❌ PRIMARY ISSUE: Token in localStorage but not in request headers');
      console.log('   → Check if useAuthToken() hook returns the token');
      console.log('   → Verify token is passed to api.importRecipe()');
      console.log('   → Check api.ts request() method adds Authorization header');
    } else {
      console.log('✅ Token flow appears correct, check other errors');
    }

    console.log('\n📸 Screenshots saved:');
    console.log('  - 01-homepage.png');
    console.log('  - 04-import-page-ready.png');
    console.log('  - 05-import-result.png');
    console.log('\n🎥 Video recording saved in playwright-videos/');
  })
  .catch((error) => {
    console.error('Script failed:', error);
    process.exit(1);
  });
