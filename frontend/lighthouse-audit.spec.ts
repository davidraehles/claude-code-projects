import { test, expect } from '@playwright/test';
import Lighthouse from 'playwright-lighthouse';

test('Go-Cart Rebranding Lighthouse Audit', async ({ page, browser }) => {
  // Navigate to the rebranded landing page
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/Go-Cart|Meal Planner/);

  // Take full-page screenshot of rebranded landing page
  await page.screenshot({ path: 'lighthouse-playwright-screenshot.png', fullPage: true });

  // Run Lighthouse audit with specific categories
  const lighthouseReport = await Lighthouse.lighthouse(page, {
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    port: 9222,
    output: 'html',
  });

  // Save detailed Lighthouse report
  await page.context().storageState({ path: 'lighthouse-state.json' });
  
  // Generate HTML report
  const htmlReport = lighthouseReport.lhr.report;
  await page.context().addInitScript(async () => {
    // This will be handled by the lighthouse plugin output
  });

  // Save HTML report
  require('fs').writeFileSync('lighthouse-playwright-report.html', lighthouseReport.lhr.report);

  // Log scores for verification
  console.log('Lighthouse Scores:', {
    performance: lighthouseReport.lhr.categories['performance']?.score * 100,
    accessibility: lighthouseReport.lhr.categories['accessibility']?.score * 100,
    'best-practices': lighthouseReport.lhr.categories['best-practices']?.score * 100,
    seo: lighthouseReport.lhr.categories['seo']?.score * 100,
  });

  // Verify rebranding assets are present
  await expect(page.locator('link[rel="icon"]')).toHaveCount(5);
  await expect(page.locator('meta[property^="og:image"]')).toHaveCount(2);
});