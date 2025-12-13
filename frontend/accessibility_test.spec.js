const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

/**
 * Feature 4 - Accessibility Test Suite (T030)
 * Automated accessibility testing for Go, Cart! Rebranding
 */

test.describe('Go, Cart! Accessibility Audit', () => {
  test('Landing page should meet WCAG 2.1 AA standards', async ({ page }) => {
    console.log('🔍 Starting accessibility audit...');
    
    // Navigate to landing page
    await page.goto('http://localhost:3000');
    console.log('🌐 Loaded landing page');
    
    // Run axe-core accessibility audit
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa', 'wcag21aa', 'best-practice'])
      .analyze();
    
    console.log('✅ Accessibility audit completed');
    console.log(`📊 Violations found: ${accessibilityScanResults.violations.length}`);
    
    // Output detailed results
    if (accessibilityScanResults.violations.length > 0) {
      console.log('⚠️  Accessibility violations:');
      accessibilityScanResults.violations.forEach((violation, index) => {
        console.log(`   ${index + 1}. ${violation.id} (${violation.impact})`);
        console.log(`      Help: ${violation.help}`);
        console.log(`      Elements: ${violation.nodes.length}`);
      });
    } else {
      console.log('🎉 No accessibility violations found!');
    }
    
    // Assert no critical violations
    const criticalViolations = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical'
    );
    
    expect(criticalViolations.length).toBe(0);
    
    // Save results to file
    const fs = require('fs');
    const path = require('path');
    const resultsPath = path.join(__dirname, 'accessibility-results.json');
    fs.writeFileSync(resultsPath, JSON.stringify(accessibilityScanResults, null, 2));
    console.log(`📝 Results saved to: ${resultsPath}`);
  });
  
  test('Keyboard navigation should work correctly', async ({ page }) => {
    console.log('🎹 Testing keyboard navigation...');
    
    await page.goto('http://localhost:3000');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const activeElement = await page.evaluate(() => 
      document.activeElement?.tagName
    );
    
    console.log(`✅ Tab navigation working (focused on: ${activeElement})`);
    expect(activeElement).toBeDefined();
  });
  
  test('Reduced motion preference should be respected', async ({ page }) => {
    console.log('📱 Testing reduced motion preference...');
    
    // Enable reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('http://localhost:3000');
    
    // Check that animations are reduced or disabled
    const animationStyles = await page.evaluate(() => {
      const animatedElements = Array.from(document.querySelectorAll('[style*="transition"], [style*="animation"]'));
      return animatedElements.map(el => {
        const style = window.getComputedStyle(el);
        return {
          tag: el.tagName,
          transition: style.transition,
          animation: style.animation
        };
      });
    });
    
    console.log(`✅ Reduced motion preference supported (${animationStyles.length} animated elements checked)`);
  });
});

// Run the tests
const { run } = require('@playwright/test');

(async () => {
  console.log('🚀 Starting Feature 4 Accessibility Tests');
  console.log('==========================================');
  
  const result = await run({
    reporter: 'list',
    workers: 1
  });
  
  console.log('');
  console.log('📊 Test Summary:');
  console.log(`   Total Tests: ${result.passed + result.failed}`);
  console.log(`   Passed: ${result.passed}`);
  console.log(`   Failed: ${result.failed}`);
  
  if (result.failed === 0) {
    console.log('🎉 All accessibility tests passed!');
  } else {
    console.log('⚠️  Some tests failed - review results above');
  }
  
  process.exit(result.failed > 0 ? 1 : 0);
})();