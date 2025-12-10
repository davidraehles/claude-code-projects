# Visual Regression Tests

This directory contains Playwright visual regression tests to ensure logos, images, and critical UI elements display correctly across all deployments.

## Purpose

These tests address the issue where "logos and photos are not always showing" by:

1. **Capturing baseline screenshots** of critical UI components
2. **Comparing current state** against baselines on each test run
3. **Detecting visual regressions** before they reach production
4. **Ensuring consistent rendering** across different environments

## Test Categories

### 1. Header and Logo Tests
- `header-logo.png` - Header logo visual comparison
- `header-with-brand.png` - Complete header with branding
- Logo dimension and visibility checks
- Cross-page consistency verification

### 2. Recipe Card Image Tests
- `recipe-card-first.png` - First recipe card visual comparison
- `curation-section-full.png` - Complete curation section
- Broken image detection
- Image dimension validation

### 3. Knuspr Integration Tests
- `knuspr-card.png` - Knuspr service card
- `checkout-section-full.png` - Complete checkout section
- Integration badge verification

### 4. Critical Page Elements
- `hero-section.png` - Landing page hero section
- `aggregation-section.png` - Aggregation feature section

### 5. Error State Tests
- `no-broken-images.png` - Full page screenshot for broken image detection
- Alt text accessibility validation

## Running the Tests

### First Run (Baseline Creation)

```bash
# Run visual tests to create baseline screenshots
npx playwright test e2e/visual-regression.spec.ts --update-snapshots
```

This will create baseline screenshots in the `__screenshots__` directory.

### Subsequent Runs (Regression Detection)

```bash
# Run visual tests to detect regressions
npx playwright test e2e/visual-regression.spec.ts
```

### Running All Visual Tests

```bash
# Run both visual regression and logo/image tests
npx playwright test e2e/visual-regression.spec.ts e2e/logo-images-knuspr.spec.ts
```

### Viewing Test Results

```bash
# Open HTML report
npx playwright show-report
```

## Configuration

Visual comparison options are configured in the test file:

```typescript
const visualOptions = {
  maxDiffPixels: 100,           // Allow small differences due to anti-aliasing
  maxDiffPixelRatio: 0.01,      // 1% of pixels can differ
  threshold: 0.2,               // 20% similarity threshold
}
```

## CI/CD Integration

These tests should be integrated into your CI/CD pipeline:

1. **On PR creation**: Run tests to detect visual regressions
2. **On main branch**: Update baselines when intentional visual changes are made
3. **On deployment**: Verify visual consistency in staging/production

## Troubleshooting

### False Positives

If tests fail due to minor rendering differences (anti-aliasing, etc.):
- Adjust `maxDiffPixels` or `threshold` values
- Update baselines if changes are intentional

### Broken Images

If tests detect broken images:
1. Check network requests for failed image loads
2. Verify image URLs and paths
3. Ensure proper fallback mechanisms are in place

### Inconsistent Rendering

If tests show inconsistent results:
1. Ensure consistent viewport sizes
2. Wait for all animations to complete
3. Use `scrollIntoViewIfNeeded()` for off-screen elements

## Best Practices

1. **Update baselines intentionally**: Only update when visual changes are desired
2. **Review visual diffs**: Always examine test report visual comparisons
3. **Test across environments**: Run tests in staging before production
4. **Combine with functional tests**: Visual tests complement, don't replace, functional tests

## Related Tests

- `logo-images-knuspr.spec.ts` - Functional tests for logos and images
- `grocery-cart-views.spec.ts` - Grocery cart functionality tests
- `workflow.spec.ts` - End-to-end workflow tests

## Maintenance

Regularly review and update:
- Baseline screenshots when intentional visual changes occur
- Test coverage as new visual components are added
- Visual comparison thresholds based on test results

---

**Note**: Visual regression testing requires Playwright with screenshot comparison capabilities. Ensure your environment has proper font rendering and consistent browser versions for reliable results.