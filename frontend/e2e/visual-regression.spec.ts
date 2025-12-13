import { test, expect } from '@playwright/test';

/**
 * Visual regression tests for logos, images, and critical UI elements
 * These tests capture screenshots and compare them to baseline images
 * to ensure visual consistency across deployments
 */

test.describe('Visual Regression Tests', () => {
  // Configure visual comparison options
  const visualOptions = {
    maxDiffPixels: 100, // Allow small differences due to anti-aliasing
    maxDiffPixelRatio: 0.01, // 1% of pixels can differ
    threshold: 0.2, // 20% similarity threshold
  };

  test.describe('Header and Logo Visual Tests', () => {
    test('header logo displays correctly - visual comparison', async ({ page }) => {
      await page.goto('/dashboard');

      // Wait for logo to be fully loaded
      const logo = page.locator('header a[aria-label="Go, Cart! Home"]');
      await expect(logo).toBeVisible();

      // Capture screenshot of header logo area
      await expect(logo).toHaveScreenshot('header-logo.png', visualOptions);
    });

    test('header with brand text - visual comparison', async ({ page }) => {
      await page.goto('/dashboard');

      // Capture entire header
      const header = page.locator('header');
      await expect(header).toBeVisible();

      await expect(header).toHaveScreenshot('header-with-brand.png', visualOptions);
    });
  });

  test.describe('Recipe Card Images Visual Tests', () => {
    test('recipe cards display images correctly - visual comparison', async ({ page }) => {
      await page.goto('/');

      // Wait for curation section
      const curationSection = page.locator('#curation');
      await expect(curationSection).toBeVisible();

      // Capture first recipe card (most likely to have image issues)
      const firstCard = curationSection.locator('article.recipe-card').first();
      await expect(firstCard).toBeVisible();

      await expect(firstCard).toHaveScreenshot('recipe-card-first.png', visualOptions);
    });

    test('all recipe cards have visible images - visual comparison', async ({ page }) => {
      await page.goto('/');

      const curationSection = page.locator('#curation');
      await expect(curationSection).toBeVisible();

      // Capture the entire curation section
      await expect(curationSection).toHaveScreenshot('curation-section-full.png', visualOptions);
    });
  });

  test.describe('Knuspr Integration Visual Tests', () => {
    test('Knuspr card displays correctly - visual comparison', async ({ page }) => {
      await page.goto('/');

      // Scroll to checkout section
      const checkoutSection = page.locator('#checkout');
      await checkoutSection.scrollIntoViewIfNeeded();
      await expect(checkoutSection).toBeVisible();

      // Capture Knuspr card specifically
      const knusprCard = checkoutSection.locator('div.border-primary-400.bg-primary-50').first();
      await expect(knusprCard).toBeVisible();

      await expect(knusprCard).toHaveScreenshot('knuspr-card.png', visualOptions);
    });

    test('checkout section with all services - visual comparison', async ({ page }) => {
      await page.goto('/');

      const checkoutSection = page.locator('#checkout');
      await checkoutSection.scrollIntoViewIfNeeded();
      await expect(checkoutSection).toBeVisible();

      await expect(checkoutSection).toHaveScreenshot('checkout-section-full.png', visualOptions);
    });
  });

  test.describe('Critical Page Elements Visual Tests', () => {
    test('landing page hero section - visual comparison', async ({ page }) => {
      await page.goto('/');

      const heroSection = page.locator('#hero');
      await expect(heroSection).toBeVisible();

      await expect(heroSection).toHaveScreenshot('hero-section.png', visualOptions);
    });

    test('aggregation section - visual comparison', async ({ page }) => {
      await page.goto('/');

      const aggregationSection = page.locator('#aggregation');
      await aggregationSection.scrollIntoViewIfNeeded();
      await expect(aggregationSection).toBeVisible();

      await expect(aggregationSection).toHaveScreenshot('aggregation-section.png', visualOptions);
    });
  });

  test.describe('Error State Visual Tests', () => {
    test('broken image handling - visual comparison', async ({ page }) => {
      await page.goto('/');

      // Check that no broken image icons are visible
      const brokenImages = page.locator('img[src*="broken"]');
      await expect(brokenImages).toHaveCount(0);

      // Capture a screenshot to verify no broken images
      await expect(page.locator('body')).toHaveScreenshot('no-broken-images.png', {
        ...visualOptions,
        mask: [page.locator('footer')] // Mask footer as it may change
      });
    });

    test('all images have proper alt text - accessibility check', async ({ page }) => {
      await page.goto('/');

      // Find all images
      const images = await page.locator('img').all();

      for (const img of images) {
        const altText = await img.getAttribute('alt');
        const src = await img.getAttribute('src');

        // Images should either have meaningful alt text or be decorative
        if (src && !src.includes('logo') && !src.includes('icon')) {
          expect(altText, `Image ${src} should have alt text`).toBeTruthy();
          expect(altText?.length, `Image ${src} alt text should not be empty`).toBeGreaterThan(0);
        }
      }
    });
  });
});
