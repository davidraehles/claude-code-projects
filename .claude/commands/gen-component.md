# Gen Component Skill

Generate a complete React component with TypeScript types, Tailwind styling, and comprehensive tests.

## Usage

```
/gen-component [component-name] [feature] [requirements]
```

## Parameters

- `component-name`: Name of component (e.g., Hero, Services, ContactForm)
- `feature`: 001 (Landing Page) or 002 (Recipe System)
- `requirements`: Description of what the component should do

## Examples

```
/gen-component Hero 001 "Main hero section with headline, subheadline, and CTA button"
/gen-component Services 001 "Display 6 service cards in a responsive grid"
/gen-component RecipeCard 002 "Display single recipe with ingredients and rating"
```

## What It Does

1. Reads component requirements from spec.md
2. Generates TypeScript component with full type safety
3. Creates Tailwind CSS styling with responsive design
4. Adds accessibility features (WCAG 2.1 AA)
5. Generates comprehensive unit tests
6. Adds animations if applicable
7. Includes documentation and examples

## Output

Creates the following files:

```
src/
  components/
    ├─ ComponentName.tsx          (React component)
    └─ ComponentName.module.css   (Tailwind styles)

src/__tests__/
  └─ ComponentName.test.tsx       (Unit tests)

stories/
  └─ ComponentName.stories.tsx    (Storybook examples)

types/
  └─ ComponentName.ts             (TypeScript types)
```

## Example: Hero Component

```typescript
// src/components/Hero.tsx
/**
 * Hero Component
 *
 * Main hero section with headline, subheadline, CTA button, and background image.
 * Features smooth animations, responsive design, and full accessibility.
 *
 * @example
 * ```tsx
 * <Hero
 *   headline="Data Solutions for Your Business"
 *   subheadline="Transform raw data into actionable insights"
 *   ctaText="Get Started"
 *   imageUrl="/hero.jpg"
 *   onCTAClick={() => navigate('/contact')}
 * />
 * ```
 */

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { HeroProps } from '@/types/Hero';
import styles from './Hero.module.css';

export const Hero: React.FC<HeroProps> = ({
  headline,
  subheadline,
  ctaText,
  imageUrl,
  onCTAClick,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <section
      className={`
        relative min-h-screen flex items-center justify-center
        px-4 sm:px-6 lg:px-8 py-20 sm:py-32 lg:py-40
        bg-gradient-to-br from-blue-50 to-indigo-100
        overflow-hidden
      `}
      role="region"
      aria-label="Hero section"
    >
      {/* Background Image */}
      <div className="absolute inset-0 -z-10">
        <Image
          src={imageUrl}
          alt="Hero background"
          fill
          className="object-cover opacity-20"
          priority
          sizes="100vw"
        />
      </div>

      {/* Content Container */}
      <motion.div
        className="relative max-w-4xl mx-auto text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={isVisible ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8 }}
      >
        {/* Headline */}
        <motion.h1
          className={`
            text-4xl sm:text-5xl lg:text-6xl font-bold
            text-gray-900 dark:text-white
            mb-4 sm:mb-6 leading-tight
          `}
          initial={{ opacity: 0, y: 20 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.1 }}
        >
          {headline}
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          className={`
            text-lg sm:text-xl lg:text-2xl
            text-gray-600 dark:text-gray-300
            mb-8 sm:mb-10 max-w-2xl mx-auto
          `}
          initial={{ opacity: 0, y: 20 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {subheadline}
        </motion.p>

        {/* CTA Button */}
        <motion.button
          onClick={onCTAClick}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onCTAClick?.();
            }
          }}
          className={`
            inline-block px-8 py-4
            bg-blue-600 hover:bg-blue-700 active:bg-blue-800
            text-white font-bold rounded-lg
            transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            dark:focus:ring-offset-gray-900
          `}
          initial={{ opacity: 0, y: 20 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.3 }}
          aria-label={ctaText}
          role="button"
          tabIndex={0}
        >
          {ctaText}
          <span className="ml-2" aria-hidden="true">→</span>
        </motion.button>
      </motion.div>
    </section>
  );
};

export default Hero;
```

## Test Coverage

Generated tests include:
- ✓ Component rendering with required props
- ✓ Optional prop handling
- ✓ Click handlers and callbacks
- ✓ Responsive design across viewports
- ✓ Accessibility (keyboard navigation, screen reader)
- ✓ Animation behavior
- ✓ Dark mode support
- Target: 95%+ coverage

## Quality Assurance

All generated components:
- ✓ Full TypeScript type safety
- ✓ WCAG 2.1 AA accessibility compliant
- ✓ Mobile-responsive (320px+)
- ✓ Dark mode support
- ✓ Error boundaries
- ✓ Proper prop validation
- ✓ Semantic HTML
- ✓ Performance optimized (lazy loading, memoization)

## When to Use

- Need to quickly generate new React components
- Following standardized patterns across project
- Want to ensure consistency (types, tests, accessibility)
- Rapid prototyping with quality assurance
- Component needs both styling and comprehensive tests
