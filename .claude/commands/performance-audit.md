# Performance Audit Skill

Analyze performance metrics and suggest optimizations using Lighthouse and profiling tools.

## Usage

```
/performance-audit [feature-or-route]
```

## Parameters

- `feature-or-route`: Feature number (001) or route URL

## Examples

```
/performance-audit 001
/performance-audit /landing-page
/performance-audit /recipe-list
```

## What It Does

1. Runs Lighthouse audit
2. Measures page load metrics
3. Analyzes bundle size
4. Identifies performance bottlenecks
5. Checks for lazy loading
6. Measures runtime performance
7. Provides specific optimization suggestions

## Output

Returns performance audit report:
- Lighthouse scores (Performance, Accessibility, Best Practices, SEO)
- Core Web Vitals (LCP, FID, CLS)
- Bundle size analysis
- Network requests waterfall
- Optimization suggestions
- Estimated impact of optimizations
- Before/after comparisons

## When to Use

- After feature implementation
- Performance regression detection
- Optimization planning
- Production release verification
- User experience monitoring
