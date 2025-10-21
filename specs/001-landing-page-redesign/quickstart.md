# Quickstart Guide: Raedical.co Landing Page

**Feature**: Landing Page Redesign
**Date**: 2025-10-20
**Tech Stack**: Next.js 14 + TypeScript + Tailwind CSS

## Overview

This guide will help you set up the Raedical.co landing page development environment and get the project running locally. The landing page is built with Next.js 14 (App Router), TypeScript, and Tailwind CSS for optimal performance and developer experience.

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js**: v18.17+ or v20+ (check with `node --version`)
- **pnpm**: v8+ (install with `npm install -g pnpm`)
- **Git**: Any recent version
- **Code Editor**: VS Code recommended (with extensions listed below)

### Recommended VS Code Extensions

- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript Vue Plugin (Volar)
- Error Lens

---

## Quick Start (5 Minutes)

### 1. Clone and Install

```bash
# Navigate to project directory
cd raedical-landing-page

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env.local

# Start development server
pnpm dev
```

The site will be available at **http://localhost:3000**

### 2. Configure Environment Variables

Edit `.env.local` and add your API keys:

```bash
# Email Service (Resend or SendGrid)
RESEND_API_KEY=your_resend_api_key_here
# OR
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Analytics (Optional for development)
NEXT_PUBLIC_GA_ID=your_google_analytics_id
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=raedical.co

# Site Configuration
NEXT_PUBLIC_SITE_URL=http://localhost:3000
CONTACT_EMAIL=team@raedical.co
```

### 3. Verify Setup

```bash
# Run tests
pnpm test

# Run accessibility checks
pnpm test:a11y

# Run Lighthouse (requires Chrome)
pnpm lighthouse
```

---

## Project Structure

```
raedical-landing-page/
├── app/                      # Next.js App Router
│   ├── api/                  # API routes (form submission)
│   │   ├── contact/
│   │   │   └── route.ts
│   │   ├── newsletter/
│   │   │   └── route.ts
│   │   └── health/
│   │       └── route.ts
│   ├── layout.tsx            # Root layout (SEO, fonts, providers)
│   ├── page.tsx              # Home page (landing page)
│   └── globals.css           # Global styles, Tailwind imports
│
├── src/
│   ├── components/           # React components
│   │   ├── Hero/
│   │   │   ├── Hero.tsx
│   │   │   └── Hero.test.tsx
│   │   ├── About/
│   │   ├── Features/
│   │   ├── SocialProof/
│   │   ├── Contact/
│   │   ├── Newsletter/
│   │   └── common/           # Shared components (Button, Input, etc.)
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── Section.tsx
│   │
│   ├── lib/                  # Utility functions and configurations
│   │   ├── validation.ts     # Zod schemas
│   │   ├── email.ts          # Email service integration
│   │   ├── analytics.ts      # Analytics helpers
│   │   └── rate-limit.ts     # Rate limiting for API
│   │
│   ├── config/               # Configuration files
│   │   ├── seo.ts            # SEO metadata
│   │   └── site.ts           # Site content and configuration
│   │
│   └── styles/               # Additional CSS (beyond Tailwind)
│       └── components/       # Component-specific styles if needed
│
├── public/                   # Static assets
│   ├── images/
│   ├── fonts/
│   └── favicon.ico
│
├── tests/                    # Test files
│   ├── accessibility/
│   ├── integration/
│   └── e2e/
│
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

---

## Development Workflow

### 1. Start Development Server

```bash
pnpm dev
```

- Hot reload enabled
- TypeScript type checking in real-time
- Tailwind CSS JIT compilation

### 2. Run Tests

```bash
# All tests
pnpm test

# Watch mode
pnpm test:watch

# Coverage
pnpm test:coverage

# Accessibility tests
pnpm test:a11y

# E2E tests
pnpm test:e2e
```

### 3. Linting and Formatting

```bash
# Lint code
pnpm lint

# Fix linting issues
pnpm lint:fix

# Format code
pnpm format

# Type check
pnpm type-check
```

### 4. Build for Production

```bash
# Create production build
pnpm build

# Preview production build locally
pnpm start

# Analyze bundle size
pnpm analyze
```

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server (http://localhost:3000) |
| `pnpm build` | Create production build |
| `pnpm start` | Start production server (after build) |
| `pnpm lint` | Run ESLint |
| `pnpm lint:fix` | Auto-fix linting issues |
| `pnpm format` | Format code with Prettier |
| `pnpm type-check` | Run TypeScript type checking |
| `pnpm test` | Run all tests (Vitest) |
| `pnpm test:watch` | Run tests in watch mode |
| `pnpm test:coverage` | Generate test coverage report |
| `pnpm test:a11y` | Run accessibility tests |
| `pnpm test:e2e` | Run E2E tests (Playwright) |
| `pnpm lighthouse` | Run Lighthouse performance audit |
| `pnpm analyze` | Analyze bundle size |

---

## Configuration Files

### package.json

```json
{
  "name": "raedical-landing-page",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "format": "prettier --write \"**/*.{ts,tsx,json,md}\"",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:a11y": "vitest run tests/accessibility",
    "test:e2e": "playwright test",
    "lighthouse": "lhci autorun",
    "analyze": "ANALYZE=true next build"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "resend": "^2.0.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest-axe": "^8.0.0",
    "@axe-core/react": "^4.8.0",
    "playwright": "^1.40.0",
    "@playwright/test": "^1.40.0",
    "eslint": "^8.50.0",
    "eslint-config-next": "^14.0.0",
    "eslint-plugin-jsx-a11y": "^6.8.0",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.5.0",
    "@lhci/cli": "^0.13.0",
    "next-sitemap": "^4.0.0"
  }
}
```

### tailwind.config.ts

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          // ... add brand colors
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        heading: ['var(--font-heading)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
```

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for optimal performance
  output: 'standalone',

  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

---

## Email Service Setup

### Option 1: Resend (Recommended)

1. Sign up at https://resend.com
2. Verify your sending domain
3. Create an API key
4. Add to `.env.local`: `RESEND_API_KEY=your_key_here`

```typescript
// src/lib/email.ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendContactEmail(data: ContactSubmissionInput) {
  return await resend.emails.send({
    from: 'contact@raedical.co',
    to: process.env.CONTACT_EMAIL!,
    subject: `Contact form: ${data.company}`,
    html: `
      <h2>New Contact Form Submission</h2>
      <p><strong>Name:</strong> ${data.name}</p>
      <p><strong>Email:</strong> ${data.email}</p>
      <p><strong>Company:</strong> ${data.company}</p>
      ${data.phone ? `<p><strong>Phone:</strong> ${data.phone}</p>` : ''}
      <p><strong>Message:</strong></p>
      <p>${data.message}</p>
    `,
  });
}
```

### Option 2: SendGrid

1. Sign up at https://sendgrid.com
2. Create an API key
3. Add to `.env.local`: `SENDGRID_API_KEY=your_key_here`

---

## Analytics Setup

### Google Analytics 4

1. Create GA4 property at https://analytics.google.com
2. Get Measurement ID (format: G-XXXXXXXXXX)
3. Add to `.env.local`: `NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX`

### Plausible (Optional)

1. Sign up at https://plausible.io
2. Add site domain
3. Add to `.env.local`: `NEXT_PUBLIC_PLAUSIBLE_DOMAIN=raedical.co`

---

## Testing

### Component Tests (Vitest + React Testing Library)

```typescript
// src/components/Hero/Hero.test.tsx
import { render, screen } from '@testing-library/react';
import { Hero } from './Hero';

describe('Hero', () => {
  it('renders headline and CTA', () => {
    render(<Hero />);

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /get started/i })).toBeInTheDocument();
  });
});
```

### Accessibility Tests

```typescript
// tests/accessibility/a11y.test.tsx
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';
import Home from '@/app/page';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Home />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### E2E Tests (Playwright)

```typescript
// tests/e2e/landing-page.spec.ts
import { test, expect } from '@playwright/test';

test('contact form submission', async ({ page }) => {
  await page.goto('http://localhost:3000');

  await page.fill('input[name="name"]', 'Test User');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="company"]', 'Test Company');
  await page.fill('textarea[name="message"]', 'This is a test message');

  await page.click('button[type="submit"]');

  await expect(page.locator('text=Thank you')).toBeVisible();
});
```

---

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import repository at https://vercel.com
3. Add environment variables in Vercel dashboard
4. Deploy!

Automatic deployments on every push to main branch.

### Netlify (Alternative)

1. Push code to GitHub
2. Import repository at https://netlify.com
3. Build command: `pnpm build`
4. Publish directory: `.next`
5. Add environment variables
6. Deploy!

---

## Troubleshooting

### Common Issues

**Issue**: `Module not found: Can't resolve 'X'`
**Solution**: Run `pnpm install` to ensure all dependencies are installed

**Issue**: TypeScript errors
**Solution**: Run `pnpm type-check` and fix type errors

**Issue**: Tailwind styles not applying
**Solution**: Check that file is included in `tailwind.config.ts` content array

**Issue**: API routes returning 404
**Solution**: Ensure route files are named `route.ts` in app router

**Issue**: Environment variables not working
**Solution**: Restart dev server after changing `.env.local`

---

## Performance Optimization

### Image Optimization

```tsx
import Image from 'next/image';

// Always use Next.js Image component
<Image
  src="/hero-image.jpg"
  alt="Description"
  width={1200}
  height={630}
  priority // For above-the-fold images
  quality={85}
/>
```

### Font Optimization

```tsx
// app/layout.tsx
import { Inter, Poppins } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });
const poppins = Poppins({
  weight: ['600', '700'],
  subsets: ['latin'],
  variable: '--font-heading'
});
```

### Code Splitting

```tsx
import dynamic from 'next/dynamic';

// Lazy load non-critical components
const NewsletterForm = dynamic(() => import('@/components/Newsletter'));
```

---

## Next Steps

1. ✅ Complete quickstart setup
2. 📋 Review [specification](./spec.md)
3. 🔍 Review [data model](./data-model.md)
4. 📄 Review [API contracts](./contracts/)
5. 🔨 Start implementing (use `/speckit.tasks` to generate tasks)
6. ✅ Write tests for each component
7. 🚀 Deploy to staging environment

---

## Support & Resources

- **Specification**: [spec.md](./spec.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/](./contracts/)
- **Research**: [research.md](./research.md)
- **Next.js Docs**: https://nextjs.org/docs
- **Tailwind Docs**: https://tailwindcss.com/docs
- **React Hook Form**: https://react-hook-form.com

---

**Last Updated**: 2025-10-20
