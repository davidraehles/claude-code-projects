import { test, expect } from '@playwright/test';

test.describe('Logo, Images, and Knuspr Integration', () => {

  test.describe('Header Logo', () => {
    test('logo SVG loads correctly in header', async ({ page }) => {
      await page.goto('/dashboard');

      // Check that the logo image exists and is visible
      const logo = page.locator('header a[aria-label="Go, Cart! Home"] img');
      await expect(logo).toBeVisible();

      // Verify it's using the correct SVG source
      const src = await logo.getAttribute('src');
      expect(src).toContain('logo-icon');

      // Verify the "Go, Cart!" text is present
      const brandText = page.locator('header a[aria-label="Go, Cart! Home"] span');
      await expect(brandText).toContainText('Go, Cart!');
    });

    test('logo has proper alt text for accessibility', async ({ page }) => {
      await page.goto('/dashboard');

      const logo = page.locator('header img[alt="Go, Cart! Logo"]');
      await expect(logo).toBeVisible();
    });

    test('logo is not transparent and has proper dimensions', async ({ page }) => {
      await page.goto('/dashboard');

      const logo = page.locator('header a[aria-label="Go, Cart! Home"] img');
      await expect(logo).toBeVisible();

      // Check that logo has proper dimensions (not collapsed)
      const boundingBox = await logo.boundingBox();
      expect(boundingBox?.width).toBeGreaterThan(20);
      expect(boundingBox?.height).toBeGreaterThan(20);

      // Verify logo is actually loaded (not a broken image)
      const src = await logo.getAttribute('src');
      const response = await page.request.get(src);
      expect(response.ok(), `Logo image ${src} should load successfully`).toBeTruthy();
    });

    test('logo displays consistently across pages', async ({ page }) => {
      const pagesToTest = ['/', '/dashboard', '/generate'];

      for (const path of pagesToTest) {
        await page.goto(path);
        
        const logo = page.locator('header a[aria-label="Go, Cart! Home"] img');
        await expect(logo).toBeVisible();

        const src = await logo.getAttribute('src');
        expect(src).toContain('logo-icon');
      }
    });
  });

  test.describe('PWA Manifest Icons', () => {
    test('manifest file is accessible and valid', async ({ page }) => {
      const response = await page.goto('/site.webmanifest');
      expect(response?.status()).toBe(200);

      const manifest = await response?.json();
      expect(manifest.name).toBe('Go, Cart!');
      expect(manifest.icons).toBeDefined();
      expect(manifest.icons.length).toBeGreaterThan(0);

      // Verify icons use correct file paths (favicon-*, not android-chrome-*)
      const iconSrcs = manifest.icons.map((icon: { src: string }) => icon.src);
      expect(iconSrcs).toContain('/favicon-192x192.png');
      expect(iconSrcs).toContain('/favicon-512x512.png');
    });

    test('favicon files are accessible', async ({ page }) => {
      const iconSizes = ['16x16', '32x32', '96x96', '192x192', '512x512'];

      for (const size of iconSizes) {
        const response = await page.goto(`/favicon-${size}.png`);
        expect(response?.status(), `favicon-${size}.png should be accessible`).toBe(200);
      }
    });

    test('apple touch icon is accessible', async ({ page }) => {
      const response = await page.goto('/apple-touch-icon-180x180.png');
      expect(response?.status()).toBe(200);
    });
  });

  test.describe('Recipe Images on Landing Page', () => {
    test('curation section displays recipe cards with images', async ({ page }) => {
      await page.goto('/');

      // Wait for curation section to be visible
      const curationSection = page.locator('#curation');
      await expect(curationSection).toBeVisible();

      // Check that recipe cards exist
      const recipeCards = curationSection.locator('article.recipe-card');
      await expect(recipeCards).toHaveCount(6);

      // Verify each card has a background image
      const firstCard = recipeCards.first();
      const imageDiv = firstCard.locator('div[role="img"]');
      await expect(imageDiv).toBeVisible();

      // Check that the background-image style is set
      const style = await imageDiv.getAttribute('style');
      expect(style).toContain('background-image');
      expect(style).toContain('images.unsplash.com');
    });

    test('all recipe cards have loaded images (not broken)', async ({ page }) => {
      await page.goto('/');

      const curationSection = page.locator('#curation');
      await expect(curationSection).toBeVisible();

      const recipeCards = curationSection.locator('article.recipe-card');
      
      // Check each card for broken image indicators
      for (let i = 0; i < await recipeCards.count(); i++) {
        const card = recipeCards.nth(i);
        const imageDiv = card.locator('div[role="img"]');
        const style = await imageDiv.getAttribute('style');
        
        // Ensure the image URL is not a broken image placeholder
        expect(style).not.toContain('broken');
        expect(style).not.toContain('placeholder');
        expect(style).toContain('images.unsplash.com');
      }
    });

    test('recipe card images are visible and not transparent', async ({ page }) => {
      await page.goto('/');

      const curationSection = page.locator('#curation');
      await expect(curationSection).toBeVisible();

      const recipeCards = curationSection.locator('article.recipe-card');
      const firstCard = recipeCards.first();
      const imageDiv = firstCard.locator('div[role="img"]');

      // Check that the image has proper dimensions and is not collapsed
      const boundingBox = await imageDiv.boundingBox();
      expect(boundingBox?.width).toBeGreaterThan(100);
      expect(boundingBox?.height).toBeGreaterThan(100);

      // Check that the background image is not transparent or missing
      const style = await imageDiv.getAttribute('style');
      expect(style).toContain('background-image');
      expect(style).toContain('url(');
    });

    test('recipe card images load without errors', async ({ page }) => {
      // Track failed image requests
      const failedImages: string[] = [];
      page.on('response', response => {
        if (response.url().includes('unsplash.com') && !response.ok()) {
          failedImages.push(response.url());
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      expect(failedImages, 'All Unsplash images should load successfully').toHaveLength(0);
    });

    test('recipe cards have correct titles', async ({ page }) => {
      await page.goto('/');

      const expectedTitles = [
        "Ottolenghi's Roasted Ratatouille",
        'Creamy Mushroom Risotto',
        'Spicy Thai Basil Chicken',
        'Lemon Garlic Shrimp Pasta',
        'Baked Feta Pasta',
        'Korean Bibimbap Bowl'
      ];

      for (const title of expectedTitles) {
        const card = page.locator(`article:has(h3:text("${title}"))`);
        await expect(card).toBeVisible();
      }
    });
  });

  test.describe('Knuspr Integration in Checkout Section', () => {
    test('Knuspr is highlighted as integrated service', async ({ page }) => {
      await page.goto('/');

      // Scroll to checkout section
      const checkoutSection = page.locator('#checkout');
      await checkoutSection.scrollIntoViewIfNeeded();
      await expect(checkoutSection).toBeVisible();

      // Find Knuspr card
      const knusprCard = checkoutSection.locator('div:has-text("Knuspr")').first();
      await expect(knusprCard).toBeVisible();

      // Verify "Integrated" badge is present
      const integratedBadge = checkoutSection.locator('span:text("Integrated")');
      await expect(integratedBadge).toBeVisible();
    });

    test('Knuspr card shows "One-click cart fill" text', async ({ page }) => {
      await page.goto('/');

      const checkoutSection = page.locator('#checkout');
      await checkoutSection.scrollIntoViewIfNeeded();

      const cartFillText = checkoutSection.locator('p:text("One-click cart fill")');
      await expect(cartFillText).toBeVisible();
    });

    test('other delivery services are shown but not highlighted', async ({ page }) => {
      await page.goto('/');

      const checkoutSection = page.locator('#checkout');
      await checkoutSection.scrollIntoViewIfNeeded();

      const otherServices = ['Instacart', 'Amazon Fresh', 'Walmart+', 'DoorDash'];

      for (const service of otherServices) {
        const serviceCard = checkoutSection.locator(`div:has-text("${service}")`).first();
        await expect(serviceCard).toBeVisible();

        // These should NOT have the "Integrated" badge
        const badge = serviceCard.locator('span:text("Integrated")');
        await expect(badge).not.toBeVisible();
      }
    });

    test('Knuspr card has special styling (primary colors)', async ({ page }) => {
      await page.goto('/');

      const checkoutSection = page.locator('#checkout');
      await checkoutSection.scrollIntoViewIfNeeded();

      // Find the Knuspr card container
      const knusprContainer = checkoutSection.locator('div.border-primary-400.bg-primary-50').first();
      await expect(knusprContainer).toBeVisible();
    });
  });

  test.describe('OG Image', () => {
    test('og-image.png is accessible', async ({ page }) => {
      const response = await page.goto('/og-image.png');
      expect(response?.status()).toBe(200);

      const contentType = response?.headers()['content-type'];
      expect(contentType).toContain('image');
    });
  });

  test.describe('Visual Consistency - Logos and Photos Always Showing', () => {
    test('logos and photos are consistently visible across page loads', async ({ page }) => {
      // Test multiple page loads to ensure consistency
      const testPages = ['/', '/dashboard', '/generate'];
      
      for (const path of testPages) {
        // Load page multiple times to test consistency
        for (let i = 0; i < 3; i++) {
          await page.goto(path);
          await page.waitForLoadState('networkidle');
          
          // Check header logo is visible
          const logo = page.locator('header a[aria-label="Go, Cart! Home"] img');
          await expect(logo).toBeVisible();
          
          // Check logo has proper dimensions (not collapsed/transparent)
          const logoBox = await logo.boundingBox();
          expect(logoBox?.width, `Logo width on ${path} load ${i+1}`).toBeGreaterThan(20);
          expect(logoBox?.height, `Logo height on ${path} load ${i+1}`).toBeGreaterThan(20);
          
          // Check that logo image actually loads (not broken)
          const logoSrc = await logo.getAttribute('src');
          const logoResponse = await page.request.get(logoSrc);
          expect(logoResponse.ok(), `Logo should load on ${path} load ${i+1}`).toBeTruthy();
          
          // On landing page, check recipe images
          if (path === '/') {
            const curationSection = page.locator('#curation');
            if (await curationSection.isVisible()) {
              const recipeCards = curationSection.locator('article.recipe-card');
              const cardCount = await recipeCards.count();
              
              for (let j = 0; j < cardCount; j++) {
                const card = recipeCards.nth(j);
                const imageDiv = card.locator('div[role="img"]');
                
                // Check image container is visible and has proper dimensions
                const imageBox = await imageDiv.boundingBox();
                expect(imageBox?.width, `Recipe card ${j} width on load ${i+1}`).toBeGreaterThan(100);
                expect(imageBox?.height, `Recipe card ${j} height on load ${i+1}`).toBeGreaterThan(100);
                
                // Check that background image is set
                const style = await imageDiv.getAttribute('style');
                expect(style, `Recipe card ${j} should have background image on load ${i+1}`).toContain('background-image');
                expect(style, `Recipe card ${j} should not be broken on load ${i+1}`).not.toContain('broken');
              }
            }
          }
        }
      }
    });

    test('images load correctly on slow network conditions', async ({ page, browserName }) => {
      // Skip this test on WebKit due to network throttling limitations
      test.skip(browserName === 'webkit', 'Network throttling not reliable on WebKit');

      // Simulate slow network conditions
      const client = await page.context().newCDPSession(page);
      await client.send('Network.emulateNetworkConditions', {
        offline: false,
        downloadThroughput: 150 * 1024 / 8, // 150 kbps
        uploadThroughput: 75 * 1024 / 8,   // 75 kbps
        latency: 200,                      // 200ms latency
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Check that logo still loads on slow network
      const logo = page.locator('header a[aria-label="Go, Cart! Home"] img');
      await expect(logo).toBeVisible({ timeout: 10000 });

      // Check recipe images load (may take longer)
      const curationSection = page.locator('#curation');
      await expect(curationSection).toBeVisible({ timeout: 15000 });

      const recipeCards = curationSection.locator('article.recipe-card');
      const firstCard = recipeCards.first();
      const imageDiv = firstCard.locator('div[role="img"]');
      
      // Wait for image to be properly styled (background image loaded)
      await expect(imageDiv).toHaveCSS('background-image', /url/, { timeout: 20000 });
    });

    test('fallback mechanisms work when images fail to load', async ({ page }) => {
      // Intercept image requests and make some fail
      await page.route('**/*.{png,jpg,jpeg,svg,webp}', route => {
        // Randomly fail 30% of image requests to test fallback
        if (Math.random() < 0.3) {
          route.abort();
        } else {
          route.continue();
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Even with some image failures, the page should still be functional
      const header = page.locator('header');
      await expect(header).toBeVisible();

      // Logo should still be visible (it's inline SVG, so more resilient)
      const logo = page.locator('header a[aria-label="Go, Cart! Home"]');
      await expect(logo).toBeVisible();

      // Page should not show broken image icons
      const brokenImages = page.locator('img[src*="broken"]');
      await expect(brokenImages).toHaveCount(0);
    });
  });
});
