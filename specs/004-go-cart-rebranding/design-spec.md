# Go, Cart! — Brand & Landing Page Design Specification

> **Tagline**: *"Favorites on repeat. New loves on deck. Groceries on autopilot."*

This document serves as the comprehensive design system and implementation guide for the Go, Cart! landing page. Feed this to Claude Code for consistent, high-quality implementation.

---

## Table of Contents

1. [Brand Identity](#brand-identity)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Component Library](#component-library)
6. [Page Structure](#page-structure)
7. [Animation Specifications](#animation-specifications)
8. [Responsive Breakpoints](#responsive-breakpoints)
9. [Technical Requirements](#technical-requirements)
10. [Asset Requirements](#asset-requirements)

---

## Brand Identity

### Brand Personality

| Trait | Expression |
|-------|------------|
| **Smart** | Subtle animations that reveal intelligence, not flashy gimmicks |
| **Effortless** | Smooth transitions, minimal friction, "it just works" feel |
| **Playful** | Warm colors, friendly copy, delightful micro-interactions |
| **Premium** | Generous whitespace, refined typography, attention to detail |
| **Trustworthy** | Clean UI, clear information hierarchy, no dark patterns |

### Brand Voice

- Conversational, not corporate
- Confident, not arrogant
- Clever, not try-hard
- Helpful, not pushy

### Logo Usage

- Primary logo: Wordmark "Go, Cart!" with optional cart icon
- Minimum clear space: 1x height of the "G" on all sides
- Never stretch, rotate, or apply effects
- Light backgrounds: Use primary coral or dark navy version
- Dark backgrounds: Use white or coral version

---

## Color System

### Primary Palette

```css
:root {
  /* Primary - Coral/Tomato (energetic, appetizing) */
  --color-primary-50: #FFF5F4;
  --color-primary-100: #FFE5E3;
  --color-primary-200: #FFCCC7;
  --color-primary-300: #FFA69E;
  --color-primary-400: #FF7A6F;
  --color-primary-500: #E85A4F;  /* Main brand color */
  --color-primary-600: #D04439;
  --color-primary-700: #AE3328;
  --color-primary-800: #902B22;
  --color-primary-900: #772922;

  /* Secondary - Deep Navy (grounding, premium) */
  --color-secondary-50: #F4F5F7;
  --color-secondary-100: #E4E7EB;
  --color-secondary-200: #CBD2D9;
  --color-secondary-300: #9AA5B1;
  --color-secondary-400: #616E7C;
  --color-secondary-500: #3E4C59;
  --color-secondary-600: #2D3748;  /* Main secondary */
  --color-secondary-700: #1A202C;
  --color-secondary-800: #1A1A2E;  /* Deep backgrounds */
  --color-secondary-900: #0F0F1A;

  /* Accent - Mint/Sage (fresh, success, smart) */
  --color-accent-50: #F0FDF7;
  --color-accent-100: #DCFCE9;
  --color-accent-200: #BBF7D4;
  --color-accent-300: #86EFAD;
  --color-accent-400: #4ADE7F;
  --color-accent-500: #7EC8A3;  /* Main accent */
  --color-accent-600: #16A34A;
  --color-accent-700: #15803C;
  --color-accent-800: #166533;
  --color-accent-900: #14532B;

  /* Neutrals - Warm tones */
  --color-neutral-0: #FFFFFF;
  --color-neutral-50: #FDFCFB;
  --color-neutral-100: #FAF7F5;  /* Main background */
  --color-neutral-200: #F0EBE6;
  --color-neutral-300: #E2DBD4;
  --color-neutral-400: #C4BAB0;
  --color-neutral-500: #A69B8F;
  --color-neutral-600: #857A6E;
  --color-neutral-700: #635A50;
  --color-neutral-800: #433C35;
  --color-neutral-900: #2A2521;
}
```

### Semantic Colors

```css
:root {
  /* Backgrounds */
  --bg-primary: var(--color-neutral-100);
  --bg-secondary: var(--color-neutral-0);
  --bg-dark: var(--color-secondary-800);
  --bg-card: var(--color-neutral-0);
  --bg-card-hover: var(--color-neutral-50);

  /* Text */
  --text-primary: var(--color-secondary-800);
  --text-secondary: var(--color-neutral-600);
  --text-muted: var(--color-neutral-500);
  --text-inverse: var(--color-neutral-0);
  --text-accent: var(--color-primary-500);

  /* Interactive */
  --interactive-primary: var(--color-primary-500);
  --interactive-primary-hover: var(--color-primary-600);
  --interactive-secondary: var(--color-secondary-600);
  --interactive-success: var(--color-accent-500);

  /* Borders */
  --border-light: var(--color-neutral-200);
  --border-medium: var(--color-neutral-300);
  --border-focus: var(--color-primary-500);
}
```

### Gradients

```css
:root {
  /* Hero gradient - warm, inviting */
  --gradient-hero: linear-gradient(135deg, var(--color-primary-500) 0%, #FF9472 100%);

  /* Playlist section gradient - Spotify-inspired */
  --gradient-playlist: linear-gradient(180deg, var(--color-secondary-800) 0%, #2D1F3D 100%);

  /* Success/Smart gradient - for aggregation section */
  --gradient-smart: linear-gradient(135deg, var(--color-accent-400) 0%, var(--color-accent-600) 100%);

  /* Card shimmer effect */
  --gradient-shimmer: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%);

  /* Glassmorphism overlay */
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.3);
}
```

---

## Typography

### Font Stack

```css
:root {
  /* Primary - Headlines */
  --font-display: 'Cabinet Grotesk', 'Space Grotesk', system-ui, sans-serif;

  /* Secondary - Body */
  --font-body: 'Inter', 'DM Sans', system-ui, sans-serif;

  /* Mono - Code/numbers */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### Font Loading

```html
<!-- Preconnect for performance -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Cabinet Grotesk from Fontshare (free) -->
<link href="https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@400,500,700,800&display=swap" rel="stylesheet">

<!-- Inter from Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### Type Scale

```css
:root {
  /* Base size */
  --text-base: 1rem;      /* 16px */

  /* Scale - 1.25 ratio (Major Third) */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-md: 1rem;        /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.563rem;   /* 25px */
  --text-3xl: 1.953rem;   /* 31px */
  --text-4xl: 2.441rem;   /* 39px */
  --text-5xl: 3.052rem;   /* 49px */
  --text-6xl: 3.815rem;   /* 61px */
  --text-7xl: 4.768rem;   /* 76px */

  /* Line heights */
  --leading-none: 1;
  --leading-tight: 1.15;
  --leading-snug: 1.3;
  --leading-normal: 1.5;
  --leading-relaxed: 1.65;

  /* Letter spacing */
  --tracking-tighter: -0.03em;
  --tracking-tight: -0.015em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
}
```

### Typography Classes

```css
/* Headlines */
.heading-hero {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 8vw, var(--text-7xl));
  font-weight: 800;
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tighter);
  color: var(--text-primary);
}

.heading-section {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 5vw, var(--text-5xl));
  font-weight: 700;
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--text-primary);
}

.heading-card {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: var(--leading-snug);
  color: var(--text-primary);
}

/* Body text */
.body-large {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
}

.body-default {
  font-family: var(--font-body);
  font-size: var(--text-md);
  font-weight: 400;
  line-height: var(--leading-normal);
  color: var(--text-secondary);
}

.body-small {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  line-height: var(--leading-normal);
  color: var(--text-muted);
}

/* Labels & UI */
.label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 600;
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--text-muted);
}

.button-text {
  font-family: var(--font-body);
  font-size: var(--text-md);
  font-weight: 600;
  letter-spacing: var(--tracking-wide);
}
```

---

## Spacing & Layout

### Spacing Scale

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.5rem;    /* 24px */
  --space-6: 2rem;      /* 32px */
  --space-7: 2.5rem;    /* 40px */
  --space-8: 3rem;      /* 48px */
  --space-9: 4rem;      /* 64px */
  --space-10: 5rem;     /* 80px */
  --space-11: 6rem;     /* 96px */
  --space-12: 8rem;     /* 128px */
  --space-13: 10rem;    /* 160px */
}
```

### Container Widths

```css
:root {
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1440px;
  --container-max: 1600px;
}

.container {
  width: 100%;
  max-width: var(--container-xl);
  margin-inline: auto;
  padding-inline: var(--space-5);
}

@media (min-width: 768px) {
  .container {
    padding-inline: var(--space-8);
  }
}

@media (min-width: 1280px) {
  .container {
    padding-inline: var(--space-10);
  }
}
```

### Section Spacing

```css
.section {
  padding-block: var(--space-11);
}

@media (min-width: 768px) {
  .section {
    padding-block: var(--space-12);
  }
}

@media (min-width: 1024px) {
  .section {
    padding-block: var(--space-13);
  }
}
```

### Border Radius

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;
}
```

### Shadows

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.2);

  /* Colored shadows for cards */
  --shadow-primary: 0 10px 40px -10px rgba(232, 90, 79, 0.3);
  --shadow-accent: 0 10px 40px -10px rgba(126, 200, 163, 0.3);

  /* Glow effects */
  --glow-primary: 0 0 30px rgba(232, 90, 79, 0.4);
  --glow-accent: 0 0 30px rgba(126, 200, 163, 0.4);
}
```

---

## Component Library

### Buttons

```css
/* Base button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  font-family: var(--font-body);
  font-size: var(--text-md);
  font-weight: 600;
  line-height: 1;
  text-decoration: none;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 200ms ease;
}

/* Primary CTA */
.btn-primary {
  background: var(--gradient-hero);
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-md), var(--shadow-primary);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-primary);
}

.btn-primary:active {
  transform: translateY(0);
}

/* Secondary */
.btn-secondary {
  background: var(--color-neutral-0);
  color: var(--text-primary);
  border: 2px solid var(--border-medium);
}

.btn-secondary:hover {
  border-color: var(--color-primary-500);
  color: var(--color-primary-500);
}

/* Ghost */
.btn-ghost {
  background: transparent;
  color: var(--text-primary);
}

.btn-ghost:hover {
  background: var(--color-neutral-200);
}

/* Sizes */
.btn-sm {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

.btn-lg {
  padding: var(--space-4) var(--space-7);
  font-size: var(--text-lg);
}
```

### Recipe Cards

```css
.recipe-card {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: all 300ms ease;
}

.recipe-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.recipe-card__image {
  aspect-ratio: 4/3;
  object-fit: cover;
  width: 100%;
}

.recipe-card__content {
  padding: var(--space-4);
}

.recipe-card__title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.recipe-card__meta {
  display: flex;
  gap: var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* Selected state */
.recipe-card--selected {
  ring: 3px solid var(--color-primary-500);
  box-shadow: var(--shadow-lg), var(--glow-primary);
}
```

### Playlist/Meal List Cards

```css
.playlist-card {
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  min-width: 280px;
  transition: all 300ms ease;
}

.playlist-card:hover {
  background: linear-gradient(145deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.08) 100%);
  transform: scale(1.02);
}

.playlist-card__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.playlist-card__grid img {
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.playlist-card__title {
  color: var(--color-neutral-0);
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.playlist-card__count {
  color: rgba(255,255,255,0.6);
  font-size: var(--text-sm);
}
```

### Grocery List Items

```css
.grocery-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  transition: all 200ms ease;
}

.grocery-item__checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-medium);
  border-radius: var(--radius-sm);
  transition: all 200ms ease;
}

.grocery-item__checkbox--checked {
  background: var(--color-accent-500);
  border-color: var(--color-accent-500);
}

.grocery-item__name {
  flex: 1;
  font-size: var(--text-md);
  color: var(--text-primary);
}

.grocery-item__quantity {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--text-muted);
  background: var(--color-neutral-200);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

/* Merging animation state */
.grocery-item--merging {
  animation: merge-pulse 600ms ease;
}

@keyframes merge-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); background: var(--color-accent-100); }
}
```

### Progress Indicator

```css
.progress-indicator {
  position: fixed;
  top: 50%;
  right: var(--space-6);
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  z-index: 100;
}

.progress-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  background: var(--color-neutral-300);
  transition: all 300ms ease;
  cursor: pointer;
}

.progress-dot--active {
  background: var(--color-primary-500);
  transform: scale(1.3);
}

.progress-dot:hover {
  background: var(--color-primary-400);
}

/* Alternative: horizontal bar */
.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--gradient-hero);
  transform-origin: left;
  z-index: 100;
}
```

---

## Page Structure

### Section 1: Hero

**Scroll Position**: 0vh - 100vh

**Layout**:
- Full viewport height
- Centered content with logo, headline, subheadline, CTA
- Subtle animated background (floating food illustrations or abstract shapes)
- Down arrow indicator at bottom

**Content**:
```
[Logo: Go, Cart!]

"Favorites on repeat.
New loves on deck.
Groceries on autopilot."

[CTA Button: "See How It Works"]

[Scroll indicator arrow]
```

**Visual Elements**:
- Floating recipe card previews in background (parallax, low opacity)
- Gradient mesh or soft blob shapes
- Optional: Video background showing app in action (muted, subtle)

---

### Section 2: Recipe Curation

**Scroll Position**: 100vh - 200vh

**Section Label**: "CURATE" or "01"

**Headline**: "Your recipes. Your way."

**Subheadline**: "Save recipes from anywhere. Build your personal cookbook."

**Animation Sequence** (triggered at 100vh, plays over ~50vh scroll):

1. **0-20%**: Recipe cards fly in from different angles (staggered, physics-based)
2. **20-50%**: Cards settle into a neat 3-column grid
3. **50-70%**: One card "glows" with selection ring, slightly elevates
4. **70-100%**: Ingredients list cascades down from selected card (typewriter effect)

**Visual Elements**:
- 6-9 recipe cards with appetizing food photography
- Ingredient tags/pills that appear
- Subtle grid lines or dots in background
- "Save" and "Heart" icon animations

**Mock UI Elements**:
- Browser extension popup saving from a recipe blog
- Mobile app card stack interface

---

### Section 3: Meal Planning (Playlist Feature)

**Scroll Position**: 200vh - 300vh

**Section Label**: "PLAN" or "02"

**Headline**: "Meal planning that feels like making a playlist."

**Subheadline**: "Drag, drop, done. Your week, your way."

**Background**: Dark/Spotify-inspired gradient

**Animation Sequence**:

1. **0-20%**: Horizontal scroll container slides in from right
2. **20-40%**: Playlist cards populate (staggered fade-in)
3. **40-60%**: A recipe card "lifts" and drags toward a calendar
4. **60-80%**: Card drops into "Monday Dinner" slot with satisfying snap
5. **80-100%**: Calendar week fills in with meal thumbnails, shuffle button pulses

**Visual Elements**:
- Horizontal scrolling playlist cards (like Spotify browse)
- Weekly calendar visualization
- Drag ghost animation
- "Shuffle" button with randomize icon
- Play/pause metaphor elements

**Mock UI Elements**:
- "Quick Week" auto-fill button
- Dietary filter toggles
- Serving size adjusters

---

### Section 4: Smart Grocery Aggregation

**Scroll Position**: 300vh - 400vh

**Section Label**: "AGGREGATE" or "03"

**Headline**: "One list. Zero duplicates."

**Subheadline**: "We combine ingredients across all your planned meals. Like magic, but it's math."

**Background**: Light with mint/sage accents

**Animation Sequence** (THE WOW MOMENT):

1. **0-15%**: Multiple recipe cards float in (3-5 cards)
2. **15-30%**: Cards begin "collapsing" toward center point
3. **30-50%**: Cards merge/compress into a single unified grocery list
4. **50-70%**: Duplicate items visually combine:
   - Two "garlic" items slide together → "2× garlic" with quantity tick-up
   - Three "olive oil" merge → single entry with combined amount
5. **70-85%**: List items organize by category (Produce, Dairy, Pantry)
6. **85-100%**: Final list "locks in" with satisfying checkmark animation

**Visual Elements**:
- Particle effects during merge
- Numbers ticking up (like a counter)
- Category color coding
- "Smart" sparkle/wand icon
- Before/after comparison (split screen optional)

**Technical Display**:
- Show actual math: "3 recipes × 4 servings = 12 servings optimized"
- Savings indicator: "Consolidated 47 items → 23 unique ingredients"

---

### Section 5: Cart Handoff / Checkout

**Scroll Position**: 400vh - 500vh

**Section Label**: "ORDER" or "04"

**Headline**: "Straight to your cart."

**Subheadline**: "One tap to your favorite delivery app. Checkout in seconds."

**Animation Sequence**:

1. **0-20%**: Delivery app logos slide in (Instacart, Amazon Fresh, Walmart, etc.)
2. **20-40%**: User "selects" preferred app (highlight animation)
3. **40-60%**: Grocery list items "pour" into cart icon (fluid animation)
4. **60-80%**: Cart fills up, price total counts up
5. **80-100%**: "Ready to checkout" button pulses, optional confetti burst

**Visual Elements**:
- Delivery partner logos (use real ones if allowed, or abstracted versions)
- Shopping cart icon that fills
- Price counter animation
- Confetti or particle celebration
- Mobile phone mockup showing final cart

**Mock UI Elements**:
- Store selector
- Delivery time picker
- "Best prices" comparison indicator

---

### Section 6: CTA / Footer

**Scroll Position**: 500vh - 550vh

**Headline**: "Ready to simplify dinner?"

**Content**:
- Final CTA button: "Get Started Free" or "Join the Waitlist"
- App store badges (if applicable)
- Email signup form
- Social links
- Footer navigation

**Visual Elements**:
- Return of hero gradient
- Floating food elements
- Trust badges or testimonial snippets

---

## Animation Specifications

### General Animation Principles

1. **Easing**: Use custom easing for organic feel
   ```css
   --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
   --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);
   --ease-in-out-smooth: cubic-bezier(0.65, 0, 0.35, 1);
   ```

2. **Duration Guidelines**:
   - Micro-interactions: 150-250ms
   - Card animations: 300-500ms
   - Section transitions: 600-1000ms
   - Complex sequences: 1000-2000ms total

3. **Stagger Timing**: 50-100ms between elements

4. **Scroll-linked animations** should feel "sticky" at key moments

### GSAP ScrollTrigger Configuration

```javascript
// Recommended ScrollTrigger defaults
gsap.defaults({
  ease: "power3.out",
  duration: 0.8
});

// Pin sections during key animations
ScrollTrigger.create({
  trigger: ".section-aggregate",
  start: "top top",
  end: "+=150%",
  pin: true,
  scrub: 1
});
```

### Framer Motion Configuration

```javascript
// Recommended spring config
const smoothSpring = {
  type: "spring",
  stiffness: 100,
  damping: 20
};

// Viewport animation trigger
const viewportConfig = {
  once: false,
  amount: 0.3
};
```

### Key Animation Keyframes

```css
/* Card float-in */
@keyframes float-in {
  0% {
    opacity: 0;
    transform: translateY(60px) rotate(-5deg) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) rotate(0) scale(1);
  }
}

/* List item cascade */
@keyframes cascade {
  0% {
    opacity: 0;
    transform: translateX(-20px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Merge compression */
@keyframes merge {
  0% {
    transform: scale(1) translateY(0);
  }
  50% {
    transform: scale(0.8) translateY(20px);
  }
  100% {
    transform: scale(0) translateY(40px);
    opacity: 0;
  }
}

/* Success pulse */
@keyframes success-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(126, 200, 163, 0.4);
  }
  50% {
    box-shadow: 0 0 0 20px rgba(126, 200, 163, 0);
  }
}

/* Confetti burst */
@keyframes confetti {
  0% {
    transform: translateY(0) rotate(0);
    opacity: 1;
  }
  100% {
    transform: translateY(-200px) rotate(720deg);
    opacity: 0;
  }
}
```

---

## Responsive Breakpoints

```css
/* Mobile first approach */

/* Small phones */
@media (min-width: 375px) { }

/* Large phones */
@media (min-width: 480px) { }

/* Tablets */
@media (min-width: 768px) { }

/* Small laptops */
@media (min-width: 1024px) { }

/* Desktops */
@media (min-width: 1280px) { }

/* Large screens */
@media (min-width: 1536px) { }

/* Tailwind equivalent classes */
/* sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px */
```

### Mobile Considerations

- Scroll animations should be simplified on mobile (reduce particle count, simpler transforms)
- Touch-friendly tap targets (minimum 44x44px)
- Consider reduced motion preference:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```
- Progress indicator moves to bottom on mobile
- Horizontal scroll sections become vertical stacks

---

## Technical Requirements

### Recommended Stack

```json
{
  "framework": "Next.js 14+ (App Router)",
  "styling": "Tailwind CSS + CSS Variables",
  "animations": [
    "Framer Motion (primary)",
    "GSAP + ScrollTrigger (complex sequences)"
  ],
  "smoothScroll": "Lenis",
  "3d": "Three.js (optional, for hero effects)",
  "deployment": "Vercel"
}
```

### Package Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.16.0",
    "gsap": "^3.12.0",
    "@studio-freight/lenis": "^1.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0"
  }
}
```

### Performance Targets

- Lighthouse Performance: 90+
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- Total bundle size: < 200KB (gzipped)

### Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation for all interactive elements
- Skip-to-content link
- Proper heading hierarchy
- Alt text for all images
- Sufficient color contrast (4.5:1 for text)
- Focus indicators on all interactive elements
- Reduced motion support

---

## Asset Requirements

### Photography

- High-quality food photography (hero and recipe cards)
- Consistent lighting style: bright, natural, appetizing
- Aspect ratios: 4:3 for cards, 16:9 for backgrounds
- Minimum resolution: 1200px wide
- Format: WebP with JPEG fallback

### Icons

- Consistent icon set (recommend: Lucide, Phosphor, or custom)
- Stroke width: 1.5-2px
- Sizes: 16px, 20px, 24px, 32px
- Include: heart, save, plus, check, cart, calendar, shuffle, play, search, filter, menu, close, arrow-down, external-link

### Illustrations (Optional)

- Style: Line art or flat with brand colors
- Use for: empty states, loading, error pages
- Consistent character style if using people

### Logo Files Needed

- SVG (primary)
- PNG (fallback, multiple sizes)
- Favicon set (16, 32, 180, 192, 512)
- Open Graph image (1200x630)
- Twitter card image (1200x600)

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Set up Next.js project with TypeScript
- [ ] Configure Tailwind with custom design tokens
- [ ] Implement CSS variables from this spec
- [ ] Set up font loading
- [ ] Create base component library (buttons, cards, containers)

### Phase 2: Static Layout
- [ ] Build all 6 sections as static components
- [ ] Implement responsive layouts
- [ ] Add placeholder content and images
- [ ] Verify typography and spacing

### Phase 3: Animations
- [ ] Set up Lenis for smooth scrolling
- [ ] Implement scroll progress indicator
- [ ] Add section 1 (Hero) animations
- [ ] Add section 2 (Curation) animations
- [ ] Add section 3 (Planning) animations
- [ ] Add section 4 (Aggregation) animations — THE KEY SECTION
- [ ] Add section 5 (Checkout) animations
- [ ] Add micro-interactions (hover, focus states)

### Phase 4: Polish
- [ ] Optimize images (WebP, lazy loading, blur placeholders)
- [ ] Add loading states
- [ ] Implement reduced motion support
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Cross-browser testing

### Phase 5: Launch
- [ ] SEO meta tags
- [ ] Open Graph / social cards
- [ ] Analytics setup
- [ ] 404 page
- [ ] Final QA

---

## Quick Reference: Key Design Decisions

| Element | Value |
|---------|-------|
| Primary Brand Color | `#E85A4F` (Coral) |
| Dark Background | `#1A1A2E` (Navy) |
| Success/Smart Color | `#7EC8A3` (Mint) |
| Headline Font | Cabinet Grotesk |
| Body Font | Inter |
| Border Radius (cards) | 16px |
| Section Padding | 160px (desktop) |
| Animation Easing | `cubic-bezier(0.16, 1, 0.3, 1)` |
| Scroll Trigger | GSAP ScrollTrigger + Lenis |

---

*Document version: 1.0*
*Last updated: December 2024*
*For: Claude Code implementation*
