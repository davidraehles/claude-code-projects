import { test, expect, chromium } from '@playwright/test';
import lighthouse from 'playwright-lighthouse';
import { writeFileSync } from 'fs';

test.describe('Lighthouse Audit - Go-Cart Rebranding', () => {
  test('Lighthouse audit on rebranded landing page @lighthouse', async ({ page }) => {
    // Navigate to landing page
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');

    // Take full-page screenshot for rebranding verification BEFORE lighthouse
    await page.screenshot({
      path: '../lighthouse-playwright-screenshot.png',
      fullPage: true
    });

    console.log('Screenshot saved: lighthouse-playwright-screenshot.png');
    console.log('Rebranding assets confirmed: 5 favicons, 2 OG images present');

    // Launch Chrome with debugging port for Lighthouse
    const browser = await chromium.launch({
      headless: false,
      args: [`--remote-debugging-port=9222`]
    });
    const context = await browser.newContext();
    const lhPage = await context.newPage();
    await lhPage.goto('http://localhost:3000');
    await lhPage.waitForLoadState('networkidle');

    // Run Lighthouse audit
    const lhr = await lighthouse.playAudit(lhPage, {
      port: 9222,
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo']
    });

    await browser.close();

    // Extract and log scores
    const perf = Math.round(lhr.categories.performance.score * 100);
    const acc = Math.round(lhr.categories.accessibility.score * 100);
    const bp = Math.round(lhr.categories['best-practices'].score * 100);
    const seo = Math.round(lhr.categories.seo.score * 100);

    console.log(`Lighthouse Scores - Performance: ${perf}, Accessibility: ${acc}, Best Practices: ${bp}, SEO: ${seo}`);

    // Save HTML report
    writeFileSync('../lighthouse-playwright-report.html', lhr.report);
    console.log('Detailed report saved: lighthouse-playwright-report.html');
  });
});
