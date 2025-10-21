# Research: Raedical.co Landing Page Redesign

**Date**: 2025-10-20
**Feature**: Landing Page Redesign
**Purpose**: Resolve technical unknowns from plan.md Technical Context

## Overview

This document captures technology decisions and research findings for building a high-performance, accessible, SEO-optimized landing page. All decisions prioritize the success criteria: Lighthouse score 90+, WCAG 2.1 AA compliance, fast load times, and maintainability.

---

## Decision 1: Frontend Framework

**Decision**: Next.js 14+ (App Router) with TypeScript

**Rationale**:
- **Static Site Generation (SSG)**: Next.js excels at generating static HTML at build time, critical for performance (FR-028: <3s load on 3G)
- **SEO Built-in**: Automatic meta tag management, sitemap generation, and server-side rendering capabilities meet FR-032 through FR-036
- **Performance Optimized**: Image optimization, font optimization, and automatic code splitting help achieve Lighthouse score 90+ (SC-002)
- **TypeScript**: Type safety reduces bugs and improves maintainability for future updates
- **Industry Standard**: Large ecosystem, extensive documentation, and community support
- **Progressive Enhancement**: Can deliver static HTML that works without JavaScript (FR-049 constraint)

**Alternatives Considered**:
- **Astro**: Excellent for static sites, but smaller ecosystem and less familiar to most developers
- **Vanilla HTML/CSS**: Maximum performance but poor developer experience and harder to maintain
- **Gatsby**: Good for static sites but slower build times and more complex configuration than Next.js
- **SvelteKit**: Great performance but smaller community and less corporate adoption

**Performance Evidence**: Next.js sites routinely achieve Lighthouse scores 95+ with proper optimization

---

## Decision 2: Styling Solution

**Decision**: Tailwind CSS 3.x with CSS Variables for theming

**Rationale**:
- **Small Bundle Size**: Tailwind's purge/tree-shaking produces minimal CSS (~10KB gzipped) supporting <200KB bundle constraint
- **Responsive Design**: Built-in responsive utilities simplify mobile-first development (FR-023 through FR-027)
- **Accessibility**: Utilities for focus states, screen reader text, and ARIA patterns (FR-037 through FR-042)
- **Design Consistency**: Enforces consistent spacing, colors, and typography (FR-048)
- **Developer Experience**: Fast iteration with utility classes; no context switching between files
- **CSS Variables**: Enables runtime theming and maintains semantic color names for brand consistency

**Alternatives Considered**:
- **Styled Components**: Runtime CSS-in-JS adds bundle weight and potential performance overhead
- **CSS Modules**: Good isolation but requires more boilerplate and slower development
- **Vanilla CSS**: Maximum control but harder to maintain consistency and responsive patterns
- **Chakra UI**: Component library overhead may exceed bundle size constraints

**Performance Evidence**: Tailwind's optimized output typically adds <15KB to production bundles

---

## Decision 3: Form Handling

**Decision**: React Hook Form + Zod for validation + Resend (or SendGrid) for email delivery

**Rationale**:
- **React Hook Form**: Performant, minimal re-renders, built-in validation (FR-018)
- **Zod**: TypeScript-first schema validation ensures type safety and runtime validation
- **Small Bundle**: React Hook Form is ~9KB, Zod is ~13KB - well within budget
- **Accessibility**: Integrates well with ARIA error messaging and screen reader announcements (FR-039)
- **Email Service**: Resend/SendGrid API handles backend submission without requiring server infrastructure (FR-017, FR-019)
- **Newsletter Integration**: Same service can handle both contact form and newsletter subscriptions (FR-021)

**Alternatives Considered**:
- **Formik**: Heavier bundle size (~15KB) and more complex API
- **Native HTML forms + API Routes**: More code to write and test; less type safety
- **Netlify Forms**: Vendor lock-in and limited customization
- **Custom backend**: Overkill for simple form submission; adds deployment complexity

**Implementation Pattern**:
```typescript
// Form validation schema
const contactSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
  company: z.string().min(1, "Company is required"),
  phone: z.string().optional(),
  message: z.string().min(10, "Message too short")
});

// Submit to API route → Resend/SendGrid → Email
```

---

## Decision 4: Testing Strategy

**Decision**:
- **Component Testing**: Vitest + React Testing Library
- **Accessibility Testing**: axe-core + jest-axe
- **E2E Testing**: Playwright
- **Performance Testing**: Lighthouse CI

**Rationale**:
- **Vitest**: Fast, Vite-native test runner; compatible with Jest API but much faster
- **React Testing Library**: Encourages accessible component testing; tests user behavior not implementation
- **axe-core**: Industry-standard accessibility testing; validates WCAG 2.1 AA compliance (SC-003, SC-011)
- **Playwright**: Cross-browser E2E testing; built-in accessibility tree inspection
- **Lighthouse CI**: Automated performance, accessibility, SEO audits in CI/CD pipeline (SC-002, SC-003)

**Alternatives Considered**:
- **Jest**: Slower than Vitest; requires additional configuration for ESM
- **Cypress**: Good E2E tool but Playwright has better cross-browser support and speed
- **Manual testing only**: Insufficient for regression prevention and CI/CD automation

**Testing Coverage Goals**:
- 80%+ component coverage
- 100% accessibility coverage for interactive elements
- E2E tests for all user scenarios from spec.md
- Lighthouse CI gates: Performance ≥90, Accessibility ≥95, SEO ≥90

---

## Decision 5: Analytics Integration

**Decision**: Google Analytics 4 (GA4) + Plausible Analytics (optional privacy-focused alternative)

**Rationale**:
- **GA4**: Industry standard, free tier, event-based tracking for form submissions and CTA clicks (FR-043, FR-044)
- **Plausible**: Privacy-friendly alternative (~2KB script), no cookies, GDPR/CCPA compliant (FR-045)
- **Next.js Integration**: Both integrate easily via `_app.tsx` or layout components
- **Event Tracking**: Custom events for form submissions, newsletter signups, CTA clicks (SC-008)

**Implementation Approach**:
```typescript
// utils/analytics.ts
export const trackEvent = (eventName: string, eventData?: object) => {
  // GA4
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', eventName, eventData);
  }
  // Plausible (if enabled)
  if (typeof window !== 'undefined' && window.plausible) {
    window.plausible(eventName, { props: eventData });
  }
};

// Usage in components
trackEvent('form_submit', { form_type: 'contact' });
```

**Alternatives Considered**:
- **Mixpanel**: More expensive, overkill for landing page analytics
- **No analytics**: Fails requirement FR-043
- **Custom analytics**: Time-consuming to build and maintain

---

## Decision 6: SEO & Metadata

**Decision**: Next.js Metadata API + JSON-LD structured data + next-sitemap

**Rationale**:
- **Next.js Metadata API**: Type-safe metadata in App Router (FR-032)
- **JSON-LD**: Structured data for search engines; Organization schema for business info (FR-036)
- **next-sitemap**: Auto-generates sitemap.xml and robots.txt (FR-035)
- **Open Graph & Twitter Cards**: Social media previews (FR-032, SC-013)

**Implementation**:
```typescript
// app/layout.tsx
export const metadata: Metadata = {
  title: 'Raedical - [Value Proposition]',
  description: '[Compelling meta description]',
  openGraph: {
    title: '...',
    description: '...',
    images: ['/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
  },
};

// JSON-LD in page component
const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Raedical",
  "url": "https://raedical.co",
  // ... more structured data
};
```

**Alternatives Considered**:
- **Manual meta tags**: More error-prone, less type-safe
- **Third-party SEO plugins**: Unnecessary overhead for a single page

---

## Decision 7: Image Optimization

**Decision**: Next.js Image component + Sharp + WebP/AVIF formats

**Rationale**:
- **Next.js Image**: Automatic lazy loading, responsive images, format optimization (FR-029)
- **Sharp**: Fast image processing library (used automatically by Next.js)
- **Modern Formats**: WebP/AVIF for smaller file sizes with fallbacks (supports constraint of fast loading)
- **Lazy Loading**: Images load as they enter viewport, improving initial load time (SC-005)

**Implementation**:
```tsx
import Image from 'next/image';

<Image
  src="/hero-image.jpg"
  alt="Descriptive alt text"
  width={1200}
  height={630}
  priority // for above-the-fold images
  quality={85}
/>
```

**Alternatives Considered**:
- **Manual image optimization**: Time-consuming and error-prone
- **CDN-based optimization (Cloudinary)**: Adds external dependency and cost

---

## Decision 8: Accessibility Implementation

**Decision**:
- Semantic HTML elements (FR-033)
- ARIA labels via `aria-label`, `aria-describedby` (FR-039)
- Focus management with `focus-visible` (FR-038)
- Color contrast checker in design phase (FR-040)
- Alt text for all images (FR-041)
- Relative units (rem) for text sizing (FR-042)

**Tools**:
- **eslint-plugin-jsx-a11y**: Catches accessibility issues during development
- **axe DevTools**: Browser extension for manual testing
- **Lighthouse**: Automated accessibility audits
- **Screen reader testing**: VoiceOver (macOS), NVDA (Windows)

**Key Patterns**:
```tsx
// Skip to main content link
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>

// Form with proper labels and error messages
<label htmlFor="email">Email Address</label>
<input
  id="email"
  type="email"
  aria-describedby="email-error"
  aria-invalid={errors.email ? 'true' : 'false'}
/>
{errors.email && (
  <p id="email-error" role="alert">
    {errors.email.message}
  </p>
)}
```

---

## Decision 9: Deployment Platform

**Decision**: Vercel (primary recommendation) or Netlify (alternative)

**Rationale**:
- **Vercel**: Made by Next.js creators; zero-config deployment; automatic HTTPS; global CDN; serverless API routes
- **Performance**: Edge network ensures fast global delivery (SC-005)
- **Free Tier**: Generous limits for landing page traffic
- **Analytics**: Built-in Web Analytics (can supplement GA4)
- **Preview Deployments**: Automatic for each PR/commit

**Alternatives Considered**:
- **Netlify**: Comparable features, good alternative if Vercel unavailable
- **GitHub Pages**: Free but no serverless functions for form handling
- **Self-hosted**: Unnecessary complexity and cost for a static site

---

## Decision 10: Development Tools

**Decision**:
- **Package Manager**: pnpm (faster, more efficient than npm/yarn)
- **Linting**: ESLint + Prettier + eslint-plugin-jsx-a11y
- **Git Hooks**: Husky + lint-staged (pre-commit linting)
- **CI/CD**: GitHub Actions (test, Lighthouse CI, deploy)

**Rationale**:
- **pnpm**: Faster installs, disk space efficient, strict dependency resolution
- **Linting**: Code quality and accessibility checking during development
- **Git Hooks**: Prevent committing broken or improperly formatted code
- **GitHub Actions**: Free for public repos, integrates with Vercel/Netlify

---

## Technology Stack Summary

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | Next.js | 14.x (App Router) |
| **Language** | TypeScript | 5.x |
| **Styling** | Tailwind CSS | 3.x |
| **Forms** | React Hook Form | 7.x |
| **Validation** | Zod | 3.x |
| **Email Service** | Resend or SendGrid | Latest API |
| **Testing** | Vitest + RTL + Playwright | Latest |
| **Accessibility** | axe-core + jest-axe | Latest |
| **Analytics** | Google Analytics 4 | GA4 |
| **SEO** | Next.js Metadata + next-sitemap | Built-in + 4.x |
| **Deployment** | Vercel | Platform |

---

## Dependencies List

### Core Dependencies
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.2.0",
    "@types/node": "^20.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest-axe": "^8.0.0",
    "@axe-core/react": "^4.8.0",
    "playwright": "^1.40.0",
    "@playwright/test": "^1.40.0",
    "eslint": "^8.50.0",
    "eslint-plugin-jsx-a11y": "^6.8.0",
    "prettier": "^3.0.0",
    "husky": "^8.0.0",
    "lint-staged": "^15.0.0",
    "next-sitemap": "^4.0.0"
  }
}
```

---

## Performance Budget

Based on research and requirements, establishing these budgets:

| Metric | Budget | Requirement Source |
|--------|--------|-------------------|
| **Initial Bundle (JS)** | <200KB gzipped | Constraint from plan.md |
| **Initial Bundle (CSS)** | <50KB gzipped | Best practice for landing page |
| **Total Page Weight** | <1MB | 3G load time target |
| **Time to First Byte (TTFB)** | <600ms | Vercel global CDN |
| **First Contentful Paint (FCP)** | <1.8s | Lighthouse "good" threshold |
| **Largest Contentful Paint (LCP)** | <2.5s | Core Web Vital |
| **Cumulative Layout Shift (CLS)** | <0.1 | Core Web Vital |
| **Total Blocking Time (TBT)** | <200ms | Lighthouse "good" threshold |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| **Bundle size exceeds budget** | Code splitting, dynamic imports, tree shaking verification |
| **Accessibility failures** | Automated testing in CI, manual screen reader testing |
| **Form delivery failures** | Error handling, retry logic, user-facing error messages |
| **Poor performance on 3G** | Lighthouse CI with throttling, performance budgets |
| **SEO issues** | Automated meta tag validation, sitemap generation |
| **Browser compatibility** | Browserslist config, Playwright cross-browser testing |

---

## Next Steps (Phase 1)

With research complete, proceed to Phase 1:
1. Generate `data-model.md` (entities and validation rules)
2. Generate `contracts/` (API contracts for form submission)
3. Generate `quickstart.md` (setup instructions)
4. Update agent context with chosen technologies

All "NEEDS CLARIFICATION" items from plan.md are now resolved.
