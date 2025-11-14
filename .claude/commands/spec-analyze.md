# Spec Analyze Skill

Quickly analyze feature specifications to understand requirements, constraints, and implementation needs.

## Usage

```
/spec-analyze [feature-number] [requirement-description]
```

## Parameters

- `feature-number`: 001 (Landing Page) or 002 (Recipe System)
- `requirement-description`: Optional description of what you want analyzed

## Examples

```
/spec-analyze 001 Hero section implementation
/spec-analyze 002 Recipe harvesting agent
```

## What It Does

1. Reads the feature specification (spec.md)
2. Identifies affected components and modules
3. Extracts functional and non-functional requirements
4. Identifies constraints and dependencies
5. Suggests acceptance criteria and test scenarios
6. Highlights any gaps or conflicts in specs

## Output

Returns a detailed specification analysis including:
- Feature overview
- Affected components
- Requirements breakdown
- Constraints and limitations
- Dependencies (code, data, task)
- Test scenarios
- Specification gaps (if any)
- Recommended implementation approach

## Example Output

```
📋 Specification Analysis: Feature 001 - Hero Component

✓ Feature: 001 (Landing Page Redesign)
✓ Component: Hero Section

Functional Requirements:
- Display compelling headline with CTA button
- Show responsive hero image
- Support smooth scroll animations
- Accessibility features (WCAG 2.1 AA)

Non-Functional Requirements:
- Performance: Lighthouse score 90+
- Responsive: Mobile-first (320px+)
- SEO: Proper meta tags and structured data

Affected Components:
- src/components/Hero.tsx
- src/styles/hero.module.css
- src/__tests__/Hero.test.tsx

Test Scenarios:
✓ Render on mobile (320px), tablet (768px), desktop (1920px)
✓ Keyboard navigation
✓ Screen reader compatibility
✓ Image lazy loading
✓ CTA button click handler

Recommended Approach:
- Use React 18.x with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- React Hook Form for any interactive elements
```

## When to Use

- Starting a new feature implementation
- Need to understand requirements before coding
- Checking for edge cases or missing requirements
- Planning test coverage
- Evaluating feasibility of requests
