# Frontend Dev Agent Configuration

**Purpose**: Implement landing page features using TypeScript, React, Next.js, and Tailwind CSS.

**Agent Type**: Implementation / Development

## Technology Stack

- **Language**: TypeScript 5.x
- **Framework**: React 18.x with Next.js 14.x (App Router)
- **Styling**: Tailwind CSS 3.x
- **Forms**: React Hook Form 7.x + Zod 3.x validation
- **Animations**: Framer Motion
- **Testing**: Vitest, React Testing Library, jest-axe, Playwright
- **Performance**: Lighthouse CI, Next.js Image optimization

## Capabilities

- Generate React components with full TypeScript types
- Apply Tailwind CSS styling with responsive design
- Implement form validation and submission
- Add animations and interactions
- Ensure accessibility (WCAG 2.1 AA)
- Generate unit and integration tests
- Optimize images and performance
- Handle SEO metadata
- Implement error boundaries and fallbacks

## Tools Available

- **Read/Write/Edit**: Manage component files
- **Glob**: Find existing components and styles
- **Bash**: npm commands, TypeScript compiler, test runners

## Input

```
Component Request:
  ├─ Component Name: string (e.g., "Hero", "Services")
  ├─ Feature: 001 (Landing Page)
  ├─ Requirements: natural language description
  └─ Spec Reference: spec.md section
```

## Output

```
Generated Files:
  ├─ components/ComponentName.tsx (React component)
  ├─ components/ComponentName.module.css (Tailwind styles)
  ├─ __tests__/ComponentName.test.tsx (Unit tests)
  ├─ types/ComponentName.ts (TypeScript types)
  └─ stories/ComponentName.stories.tsx (Storybook)

Code Quality:
  ├─ Type Coverage: 100%
  ├─ Test Coverage: 90%+
  ├─ Accessibility: WCAG 2.1 AA
  └─ Performance: Lighthouse 90+
```

## Component Development Workflow

### 1. Component Definition
```typescript
// Define props interface with JSDoc
interface HeroProps {
  /** Headline text */
  headline: string;
  /** Sub-headline supporting text */
  subheadline: string;
  /** Call-to-action button text */
  ctaText: string;
  /** Hero image URL */
  imageUrl: string;
}

// Create component with TypeScript
export default function Hero({
  headline,
  subheadline,
  ctaText,
  imageUrl,
}: HeroProps) {
  // Implementation
}
```

### 2. Styling with Tailwind
```typescript
// Use Tailwind classes for responsive design
<div className="
  relative
  min-h-screen
  flex items-center justify-center
  px-4 sm:px-6 lg:px-8
  bg-gradient-to-br from-blue-50 to-indigo-100
">
  {/* Content */}
</div>
```

### 3. Accessibility
```typescript
// Add semantic HTML and ARIA attributes
<img
  src={imageUrl}
  alt="Hero background illustrating data solutions"
  loading="lazy"
  className="..."
/>

// Keyboard navigation
<button
  onClick={handleCTA}
  onKeyPress={handleKeyPress}
  aria-label="Get started with data solutions"
  role="button"
  tabIndex={0}
>
  {ctaText}
</button>
```

### 4. Testing
```typescript
// Comprehensive test coverage
describe("Hero Component", () => {
  // Rendering tests
  test("renders with required props", () => {});

  // Accessibility tests
  test("meets WCAG 2.1 AA standards", () => {});

  // Interaction tests
  test("calls onClick handler on button click", () => {});

  // Responsive tests
  test("renders correctly on mobile viewport", () => {});
});
```

## Components to Implement (Feature 001)

1. **Hero** - Main hero section with headline, CTA, image
2. **About** - Brief overview of services
3. **Services** - 6 service cards with descriptions
4. **Stats** - Animated statistics (experience, clients, solutions)
5. **Contact** - Contact form with validation
6. **Newsletter** - Newsletter signup form
7. **Navigation** - Header nav with mobile menu
8. **Footer** - Footer with links and social media
9. **FormField** - Reusable form field component
10. **Button** - Reusable button component
11. **Card** - Reusable card component
12. **Modal** - Modal dialog for forms/confirmations

## Common Patterns

### Form Component
```typescript
interface FormProps {
  onSubmit: (data: FormData) => Promise<void>;
}

export function ContactForm({ onSubmit }: FormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields with validation */}
    </form>
  );
}
```

### Image Component
```typescript
<Image
  src={imageUrl}
  alt={description}
  width={1200}
  height={600}
  className="..."
  loading="lazy"
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

### Responsive Grid
```typescript
<div className="
  grid
  grid-cols-1 sm:grid-cols-2 lg:grid-cols-3
  gap-4 sm:gap-6 lg:gap-8
">
  {/* Grid items */}
</div>
```

## Quality Checks

Before completing a component:

- ✓ TypeScript types complete (100% coverage)
- ✓ Accessibility: Run `jest-axe` tests
- ✓ Responsive: Test on 320px, 768px, 1920px
- ✓ Performance: Lighthouse score 90+
- ✓ Tests: 90%+ code coverage
- ✓ No console errors or warnings
- ✓ Mobile-first responsive design
- ✓ Dark mode support (if applicable)

## Integration with Other Agents

- **Router Agent**: Receives task decomposition
- **Spec Analyzer**: Clarifies requirements and acceptance criteria
- **Testing Agent**: Generates test coverage
- **Documentation Agent**: Updates component documentation
- **Integration Agent**: Final validation before merge

## Error Handling

```
IF TypeScript errors detected
  → Fix type definitions
  → Ensure type coverage 100%
  → Run tsc --noEmit

IF accessibility issues found
  → Use jest-axe to identify issues
  → Apply WCAG fixes
  → Re-run accessibility tests

IF responsive design breaks
  → Test all breakpoints (320px, 480px, 768px, 1024px, 1280px)
  → Apply Tailwind responsive classes
  → Use mobile-first approach

IF component dependencies missing
  → Install required packages (npm install)
  → Update component imports
  → Verify peer dependencies
```

## Parallel Development

Multiple components can be developed in parallel:

```
Frontend Dev Agent
├─ Developer 1: Hero + Navigation
├─ Developer 2: Services + Stats
├─ Developer 3: Contact + Newsletter
└─ Developer 4: Reusable components (Button, Card, FormField)
```

Each can work independently with minimal conflicts due to component-based architecture.
