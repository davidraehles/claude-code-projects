# Validate A11y Skill

Check accessibility compliance against WCAG 2.1 AA standards and suggest fixes.

## Usage

```
/validate-a11y [component-or-route]
```

## Parameters

- `component-or-route`: Component file path or route URL

## Examples

```
/validate-a11y src/components/Hero.tsx
/validate-a11y /landing-page
/validate-a11y src/components/ContactForm.tsx
```

## What It Does

1. Runs jest-axe accessibility scans
2. Checks for WCAG 2.1 AA violations
3. Validates keyboard navigation
4. Checks color contrast ratios
5. Verifies semantic HTML usage
6. Tests with screen readers (axe-core)
7. Provides specific fixes for violations

## Output

Returns accessibility audit report:
- Violations (critical, serious, moderate, minor)
- Specific fixes for each violation
- Keyboard navigation test results
- Color contrast analysis
- WCAG 2.1 AA compliance score
- Recommendations

## Example Report

```
♿ Accessibility Validation Report: Hero Component

Target: src/components/Hero.tsx
Standard: WCAG 2.1 Level AA
Status: ⚠️ VIOLATIONS FOUND (3 issues)

CRITICAL VIOLATIONS (must fix):
├─ Issue 1: Missing heading structure
│  └─ Location: line 24
│  └─ Problem: h1 skipped, jumps to h3
│  └─ Fix: Change h3 to h2
│  └─ Impact: Screen reader users miss content hierarchy

SERIOUS VIOLATIONS (should fix):
├─ Issue 2: Low color contrast
│  └─ Location: Subheadline text
│  └─ Ratio: 3.2:1 (needs 4.5:1 for AA)
│  └─ Fix: Change text color from #666 to #444
│  └─ Impact: Users with low vision can't read text

MODERATE VIOLATIONS (consider fixing):
├─ Issue 3: Form field missing label
│  └─ Location: Email input
│  └─ Fix: Add <label htmlFor="email">Email</label>
│  └─ Impact: Screen reader users won't know field purpose

KEYBOARD NAVIGATION:
✓ All interactive elements reachable with Tab
✓ Focus indicator visible (outline: 2px solid)
✓ Escape key closes modal
✓ Arrow keys work for menus

COLOR CONTRAST:
├─ Headline: 7.2:1 ✓ (exceeds AA requirement)
├─ Subheadline: 3.2:1 ⚠️ (below AA requirement)
└─ Body text: 5.1:1 ✓ (meets AA requirement)

SEMANTIC HTML:
✓ Using <button> for clickable actions
✓ Using <img> with alt text
✓ Using <nav> for navigation
✓ Proper heading hierarchy

ARIA ATTRIBUTES:
✓ aria-label on buttons
✓ aria-labelledby on headings
✓ aria-hidden on decorative elements
✓ role="region" on important sections

OVERALL SCORE: 67/100 (Level A)
TARGET SCORE: 90+/100 (Level AA)

NEXT STEPS:
1. Fix critical violations (2 items)
2. Fix serious violations (1 item)
3. Consider moderate violations (1 item)
4. Re-run audit to verify fixes

ESTIMATED TIME: 30 minutes
```

## When to Use

- After creating new components
- Before submitting pull request
- Accessibility audit for features
- Compliance verification
- User testing preparation
