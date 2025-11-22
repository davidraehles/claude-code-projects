# Phase 4: Performance Optimization Guide

**Status**: T208 Implementation
**Date**: 2025-11-22
**Target**: Core Web Vitals optimization for cart workflow

---

## Performance Baseline

### Metrics to Track
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **TTFB (Time to First Byte)**: < 600ms
- **Bundle Size**: < 300KB gzipped

### Current Estimated Size
- CartPreview.tsx: ~15KB
- DeliverySlotPicker.tsx: ~12KB
- MissingItemsSuggestions.tsx: ~18KB
- CartErrorHandler.tsx: ~10KB
- Workflow Page: ~20KB
- Dependencies (React, Next.js): ~150KB
- **Total Estimated**: ~225KB gzipped

---

## Optimization Strategies

### 1. Code Splitting

#### Dynamic Imports
```typescript
// Split delivery slot picker from main bundle
const DeliverySlotPicker = dynamic(() =>
  import('@/components/knuspr/DeliverySlotPicker'),
  {
    loading: () => <div className="animate-pulse h-20 bg-gray-200 rounded" />,
    ssr: false,
  }
);

// Split missing items from main bundle
const MissingItemsSuggestions = dynamic(() =>
  import('@/components/knuspr/MissingItemsSuggestions'),
  {
    loading: () => <div className="animate-pulse h-24 bg-gray-200 rounded" />,
    ssr: true,
  }
);
```

#### Route-based Code Splitting
- `/workflow` route only loads workflow-specific components
- Other routes don't load cart workflow code
- Lazy load error handlers on-demand

### 2. Image Optimization

#### Product Images (if added later)
```typescript
import Image from 'next/image';

<Image
  src={product.image}
  alt={product.name}
  width={200}
  height={200}
  quality={80}
  priority={false}
  placeholder="blur"
/>
```

#### Icon Optimization
- Use lucide-react icons (tree-shakable)
- Only import used icons
- Consider SVG sprites for frequently used icons

### 3. Component Optimization

#### Memoization
```typescript
// CartPreview.tsx
export const CartPreview = React.memo(
  ({ data, onCheckout, isLoading, error }: CartPreviewProps) => {
    // Component implementation
  },
  (prevProps, nextProps) => {
    // Custom comparison logic
    return prevProps.data === nextProps.data;
  }
);
```

#### useCallback and useMemo
```typescript
// Workflow page
const handleCheckout = useCallback(() => {
  if (state.cartData) {
    window.open(state.cartData.knuspr_url, '_blank');
  }
}, [state.cartData]);

const workflowSteps = useMemo(() => [
  { name: 'Cart Review', step: 'cart-preview' as const },
  { name: 'Delivery', step: 'delivery-selection' as const },
  { name: 'Complete', step: 'review' as const },
], []);
```

### 4. Bundle Analysis

#### Build Optimization
```bash
# Analyze bundle size
npm run build
npx next-bundle-analyzer

# Check bundle composition
npm run build -- --analyze
```

#### Tree Shaking
- Remove unused Tailwind CSS classes (handled by Next.js)
- Only import needed utilities from lucide-react
- Remove unused component exports

### 5. Request Optimization

#### Request Deduplication
```typescript
// Use React Query or SWR for automatic deduplication
import { useQuery } from '@tanstack/react-query';

const { data: cartData } = useQuery({
  queryKey: ['cart', mealPlanId],
  queryFn: () => fetchCart(mealPlanId),
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

#### Caching Strategy
```typescript
// API response caching
const response = await fetch(apiUrl, {
  headers: {
    'Cache-Control': 'max-age=300', // 5 minutes
  },
});
```

### 6. CSS Optimization

#### Utility Class Purging
- Tailwind CSS automatically purges unused classes in production
- Current config covers `.tsx`, `.ts` files
- Ensure all component files are included

#### Critical CSS
```typescript
// Inline critical CSS for above-fold content
const criticalStyles = `
  .workflow-container { /* Above-fold styles */ }
  .cart-preview { /* Critical layout */ }
`;
```

### 7. Font Optimization

#### Font Loading Strategy
```typescript
// next/font for optimized font loading
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Prevent FOUT
  preload: true,
});
```

---

## Implementation Checklist

### Phase 4A: Code Splitting
- [ ] Implement dynamic imports for workflow page components
- [ ] Add loading skeletons for split components
- [ ] Test bundle size reduction
- [ ] Verify component loading performance

### Phase 4B: Component Optimization
- [ ] Add React.memo to CartPreview
- [ ] Add React.memo to DeliverySlotPicker
- [ ] Implement useCallback in workflow page
- [ ] Implement useMemo for workflow steps

### Phase 4C: Image & Asset Optimization
- [ ] Optimize icon imports (tree-shaking)
- [ ] Add Next.js Image component if images needed
- [ ] Implement lazy loading for images
- [ ] Add webp format support

### Phase 4D: Metrics & Monitoring
- [ ] Set up Core Web Vitals tracking
- [ ] Implement Sentry/Monitoring for performance
- [ ] Create performance baseline dashboard
- [ ] Set up alerts for performance regressions

### Phase 4E: Testing & Validation
- [ ] Run Lighthouse audits
- [ ] Test on slow 4G connection
- [ ] Test on low-end devices
- [ ] Verify metrics in production

---

## Code Examples

### Dynamic Import Template
```typescript
const Component = dynamic(
  () => import('@/components/knuspr/Component'),
  {
    loading: () => (
      <div className="animate-pulse">
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    ),
    ssr: true, // or false depending on component
  }
);
```

### Performance Hook
```typescript
// hooks/usePerformanceMetrics.ts
export function usePerformanceMetrics() {
  useEffect(() => {
    const metrics = {
      lcp: 0,
      fid: 0,
      cls: 0,
    };

    // Observe LCP
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
    }).observe({ entryTypes: ['largest-contentful-paint'] });

    // Observe FID
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      metrics.fid = entries[0].processingDuration;
    }).observe({ entryTypes: ['first-input'] });

    // Observe CLS
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        metrics.cls += entry.value;
      });
    }).observe({ entryTypes: ['layout-shift'] });

    return metrics;
  }, []);
}
```

### Lazy Loading Component
```typescript
// components/knuspr/LazyCartPreview.tsx
import dynamic from 'next/dynamic';
import { CartPreviewData } from './CartPreview';

const CartPreview = dynamic(() =>
  import('./CartPreview').then((mod) => mod.default),
  {
    loading: () => (
      <div className="rounded-lg bg-white p-6 shadow-sm animate-pulse">
        <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    ),
    ssr: true,
  }
);

export function LazyCartPreview(props: CartPreviewProps) {
  return <CartPreview {...props} />;
}
```

---

## Monitoring & Reporting

### Performance Dashboard Metrics
- Bundle size trends (gzipped vs uncompressed)
- Core Web Vitals scores
- Page load times by device type
- API response times
- Error rates

### Tracking Script
```typescript
// lib/analytics.ts
export function trackPerformanceMetrics() {
  if (typeof window === 'undefined') return;

  // Web Vitals
  import('web-vitals').then(({ getCLS, getFID, getLCP }) => {
    getCLS(console.log);
    getFID(console.log);
    getLCP(console.log);
  });

  // Navigation timing
  window.addEventListener('load', () => {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    console.log('Page Load Time:', pageLoadTime);
  });
}
```

---

## Lighthouse Audit Targets

### Mobile (4G)
- Performance: 90+
- Accessibility: 95+
- Best Practices: 90+
- SEO: 95+
- PWA: 90+ (if applicable)

### Desktop
- Performance: 95+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 100+
- PWA: 95+ (if applicable)

---

## Deployment Checklist

- [ ] Run `npm run build` with no errors
- [ ] Verify bundle size < 300KB gzipped
- [ ] Test on slow 4G (Lighthouse throttling)
- [ ] Verify all performance optimizations deployed
- [ ] Monitor Core Web Vitals in production
- [ ] Set up performance regression alerts
- [ ] Document performance improvements in commit

---

## Resources

- [Next.js Performance Optimization](https://nextjs.org/docs/advanced-features/measuring-performance)
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Tailwind CSS Optimization](https://tailwindcss.com/docs/optimizing-for-production)
- [React Performance](https://react.dev/reference/react/memo)

---

**Last Updated**: 2025-11-22
**Status**: Ready for Implementation
**Owner**: Frontend Team
