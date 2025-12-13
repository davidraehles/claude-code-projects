# Research: Go, Cart! Rebranding

## 1. Technology Stack Validation

### Frontend Framework: Next.js 14 (App Router)
- **Decision**: **Adopt**
- **Rationale**:
  - **Performance**: Server Components reduce client-side JS bundle size, crucial for meeting the < 200KB target despite heavy animation libraries.
  - **SEO**: Built-in metadata API and server-side rendering are essential for a landing page.
  - **Constitution Alignment**: Aligns with "UX Consistency" (React ecosystem) and "Performance" (SSR/SSG).
- **Alternatives Considered**:
  - *Remix*: Good performance, but less ecosystem momentum for static landing pages compared to Next.js SSG.
  - *Gatsby*: Too complex for a single landing page + dynamic app hybrid.

### Styling: Tailwind CSS
- **Decision**: **Adopt**
- **Rationale**:
  - **Speed**: Rapid development of custom designs.
  - **Size**: Purges unused styles, resulting in minimal CSS bundle.
  - **Constitution Alignment**: Explicitly mentioned in "UX Consistency" principle.

### Animation: Framer Motion + GSAP
- **Decision**: **Adopt Hybrid Approach**
- **Rationale**:
  - **Framer Motion**: Best for React component state transitions (hover, tap, layout changes).
  - **GSAP (ScrollTrigger)**: Industry standard for complex scroll-linked animations (the "Wow" factor required by spec).
  - **Constitution Alignment**: "UX Consistency" (Premium feel).
- **Risk Mitigation**:
  - **Bundle Size**: GSAP is relatively heavy. We will use tree-shaking and only import necessary modules (ScrollTrigger).
  - **Performance**: Will use `will-change` CSS properties and optimize animation loops.

## 2. Clarification Resolution

### Bundle Size Target (150KB vs 200KB)
- **Issue**: Constitution sets a hard limit of 150KB (gzipped) for frontend bundle size. The Design Spec targets < 200KB.
- **Resolution**: **Request Exception / Amendment for Landing Page**.
  - The "Premium" brand personality requires rich animations that necessitate libraries like GSAP.
  - **Plan**:
    - Core App (Dashboard, etc.): Stick to **150KB**.
    - Landing Page: Allow **200KB** budget due to marketing assets and animation logic.
    - **Mitigation**: Use Next.js Route Groups to isolate Landing Page dependencies from the main app bundle.

## 3. Material Design 3 Implementation
- **Decision**: **Custom Tailwind Configuration**
- **Rationale**:
  - Using a heavy component library (MUI) would blow the bundle size budget.
  - We will map MD3 design tokens (colors, typography, elevation) directly to Tailwind configuration.
  - This ensures strict adherence to the Design Spec's color system while maintaining performance.

## 4. Waitlist System
- **Decision**: **PostgreSQL + FastAPI + Background Tasks**
- **Rationale**:
  - **Reliability**: ACID compliance for user data.
  - **Performance**: FastAPI background tasks for email sending ensure < 2s UI response.
  - **Constitution Alignment**: "Observability" (easy to instrument), "Performance" (async processing).
