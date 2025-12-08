# Animation Flow Guide - Go, Cart! Landing Page

Visual reference for understanding the animation sequence and timing across all sections.

---

## Page Structure & Animation Timeline

```
┌─────────────────────────────────────────────────────────┐
│ SECTION 1: HERO (#hero)                                │
│ Animation: Framer Motion Entrance                       │
│ Duration: 1.5s total (staggered)                        │
├─────────────────────────────────────────────────────────┤
│ 0.0s: Container fade-in begins                          │
│ 0.1s: Logo slides up + fades in                         │
│ 0.3s: Headline scales up + fades in                     │
│ 0.5s: Waitlist form slides up + fades in                │
│ 1.0s: Scroll indicator starts bouncing (infinite)       │
│                                                          │
│ Interactive Elements:                                    │
│ - Input: Focus → scale 102%                             │
│ - Button: Hover → scale 105%, Tap → scale 95%           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 2: CURATION (#curation)                         │
│ Animation: Static (no custom animations yet)            │
│ Recommended: Add viewport-triggered entrance            │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 3: PLANNING (#planning)                         │
│ Animation: Framer Motion Drag + Entrance                │
│ Duration: 0.6s staggered entrance                       │
├─────────────────────────────────────────────────────────┤
│ On Scroll Into View:                                    │
│ - Section label fades in (0.6s)                         │
│ - Headline fades in (0.6s, +0.2s delay)                 │
│ - Card 1: slides up + fades (0.6s, +0.0s delay)         │
│ - Card 2: slides up + fades (0.6s, +0.1s delay)         │
│ - Card 3: slides up + fades (0.6s, +0.2s delay)         │
│ - Card 4: slides up + fades (0.6s, +0.3s delay)         │
│                                                          │
│ Interactive Elements:                                    │
│ - Drag: Full 2D movement with elastic bounce            │
│ - 3D Rotation: Based on drag direction                  │
│ - Hover: Scale 105%, lighten background                 │
│ - Tap: Scale 95%                                        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 4: AGGREGATION (#aggregation) ⭐ WOW MOMENT     │
│ Animation: GSAP ScrollTrigger (scrubbed)                │
│ Trigger: top 20% to bottom 80% of viewport              │
├─────────────────────────────────────────────────────────┤
│ Scroll Progress Timeline:                               │
│                                                          │
│ 0-30%: Recipe Cards Entrance                            │
│ ├─ Cards fly in from below (y: 100 → 0)                 │
│ ├─ Rotate in 3D (rotateX: 15deg → 0)                    │
│ ├─ Scale up (0.8 → 1.0)                                 │
│ └─ Stagger: 0.1s between cards                          │
│                                                          │
│ 30-50%: Card Compression (Merge Effect)                 │
│ ├─ Cards shrink (scale: 1.0 → 0.9)                      │
│ ├─ Move upward (y: 0 → -20)                             │
│ └─ Stagger: 0.05s between cards                         │
│                                                          │
│ 40-60%: Stats Counter Reveal                            │
│ ├─ Fade in (opacity: 0 → 1)                             │
│ └─ Slide up (y: 30 → 0)                                 │
│                                                          │
│ 60-100%: Grocery List Cascade                           │
│ ├─ Items slide in from left (x: -30 → 0)                │
│ ├─ Fade in (opacity: 0 → 1)                             │
│ ├─ Scale up (0.95 → 1.0)                                │
│ └─ Stagger: 0.08s between items                         │
│                                                          │
│ Continuous: Parallax Effect                             │
│ ├─ Recipe cards: Move up as you scroll                  │
│ └─ Grocery list: Move down as you scroll                │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 5: CHECKOUT (#checkout)                         │
│ Animation: Static (no custom animations yet)            │
│ Recommended: Add cart fill animation                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ SECTION 6: FOOTER (#footer)                             │
│ Animation: Static (no custom animations yet)            │
└─────────────────────────────────────────────────────────┘
```

---

## Scroll Progress Indicator Behavior

### Desktop (Vertical Dots - Right Side)
```
When scrollY < 100px:
  Hidden

When scrollY >= 100px:
  ┌───┐
  │ ● │ ← Active section (coral, scaled 130%)
  │ ○ │
  │ ○ │ ← Inactive sections (gray)
  │ ○ │
  │ ○ │
  │ ○ │
  └───┘

  On Hover:
  ┌────────────┐
  │ ○ │ Hero   │ ← Tooltip appears
  └────────────┘

  On Click:
  Smooth scroll to section
```

### Mobile (Horizontal Bar - Top + Counter Badge)
```
Top of viewport:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
█████████████░░░░░░░░░░░░░░░░░ ← Progress fills left to right
                                (gradient: coral → orange)

Bottom right corner:
┌─────────┐
│  3 / 6  │ ← Section counter badge
└─────────┘   (semi-transparent, backdrop blur)
```

---

## Smooth Scrolling Behavior (Lenis)

### Scroll Input vs. Page Motion
```
Mouse Wheel Input:
↓ One notch
│
└─→ Lenis Interpolation (1.2s duration)
    │
    ├─ t=0.0s: Start position
    ├─ t=0.3s: 40% progress (exponential ease)
    ├─ t=0.6s: 70% progress
    ├─ t=0.9s: 90% progress
    └─ t=1.2s: End position (100%)

Result: Buttery smooth, gradual deceleration
```

### Easing Curve
```
Speed
  │
  │ ╱╲
  │╱  ╲___
  ├────────── Time
  0s      1.2s

Custom easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t))
(Exponential ease-out for natural deceleration)
```

---

## Drag Interaction Physics (Planning Cards)

### Drag Gesture Flow
```
1. Mouse Down / Touch Start
   └─→ Cursor changes: grab → grabbing
       Card z-index: 1 → 50 (bring to front)

2. During Drag
   ├─→ X motion: Card rotates on Y axis
   │   Example: Drag right 100px → rotateY(-10deg)
   │
   └─→ Y motion: Card rotates on X axis
       Example: Drag down 100px → rotateX(-10deg)

3. Mouse Up / Touch End
   └─→ Spring back to origin (elastic bounce)
       Stiffness: 600
       Damping: 20
       Elastic: 0.2 (20% overshoot)

4. Return Animation
   ╱╲
  ╱  ╲___
 ╱       ╲___
├────────────── Time
0    200ms  400ms

Bounce effect creates playful, tactile feel
```

---

## Animation Performance Map

### GPU-Accelerated Properties (60fps)
✅ `transform: translate()`
✅ `transform: scale()`
✅ `transform: rotate()`
✅ `opacity`

### CPU-Heavy Properties (Avoid during scroll)
❌ `width` / `height`
❌ `top` / `left`
❌ `margin` / `padding`
❌ `box-shadow` (static only)

### Optimization Strategy
1. All scroll-linked animations use `transform` + `opacity`
2. `will-change` applied to animated elements
3. Single `requestAnimationFrame` loop for Lenis
4. Passive scroll listeners
5. Debounced section detection

---

## Responsive Animation Adjustments

### Desktop (1280px+)
- Full parallax effects
- 3D rotation on drag
- Complex scroll sequences
- Vertical dot navigation

### Tablet (768px - 1279px)
- Reduced parallax distance (50%)
- Simplified 3D effects
- Horizontal progress bar
- Section counter badge

### Mobile (< 768px)
- No smooth scroll (native)
- Minimal parallax
- 2D drag only (no rotation)
- Horizontal progress bar only
- Faster animation durations (-20%)

---

## Reduced Motion Support

When `prefers-reduced-motion: reduce` is enabled:

```css
* {
  animation-duration: 0.01ms !important;
  transition-duration: 0.01ms !important;
}
```

JavaScript behavior:
- Lenis smooth scroll: Disabled (native scroll)
- GSAP animations: Skipped
- Framer Motion: Instant transitions
- Scroll progress: Still functional (no animation)

---

## Animation Timing Reference

| Element | Library | Duration | Delay | Easing |
|---------|---------|----------|-------|--------|
| Hero Logo | Framer Motion | 600ms | 100ms | Spring (100/20) |
| Hero Headline | Framer Motion | 600ms | 300ms | Spring (100/20) |
| Hero Form | Framer Motion | 600ms | 500ms | Spring (100/20) |
| Scroll Indicator | Framer Motion | 600ms | 1000ms | Reverse loop |
| Planning Label | Framer Motion | 600ms | 0ms | Default |
| Planning Headline | Framer Motion | 600ms | 200ms | Default |
| Planning Cards | Framer Motion | 600ms | Index × 100ms | Spring (100/20) |
| Aggregation Cards | GSAP | Scrubbed | N/A | power3.out |
| Aggregation Stats | GSAP | Scrubbed | N/A | Default |
| Aggregation List | GSAP | Scrubbed | N/A | power3.out |
| Parallax (Continuous) | GSAP | N/A | N/A | Linear |

---

## Visual Feedback States

### Button States (Hero CTA)
```
Default:      Scale 100%,   Shadow 2xl
             ┌──────────────┐
             │ Join Waitlist│
             └──────────────┘

Hover:        Scale 105%,   Shadow increased
             ┌────────────────┐
             │ Join Waitlist  │ ← Slightly larger
             └────────────────┘

Active/Tap:   Scale 95%,    Shadow reduced
             ┌────────────┐
             │Join Waitlist│ ← Squished
             └────────────┘
```

### Playlist Card States
```
Default:      Scale 100%,   Alpha 10%
             ╔══════════════╗
             ║  [4 images]  ║
             ║  Title       ║
             ║  7 meals     ║
             ╚══════════════╝

Hover:        Scale 105%,   Alpha 20%
             ╔════════════════╗
             ║  [4 images]    ║ ← Slightly larger
             ║  Title         ║
             ║  7 meals       ║
             ╚════════════════╝

Dragging:     Scale 100%,   Rotation (3D)
              ╱╔══════════════╗
             ╱ ║  [4 images]  ║ ← Tilted
            ╱  ║  Title       ║
               ║  7 meals     ║
               ╚══════════════╝
```

---

## Next Steps for Enhanced Animations

### Phase 6 Recommendations
1. **Curation Section**: Add recipe card hover + flip animation
2. **Checkout Section**: Animate cart filling (items drop in)
3. **Footer**: Add CTA button pulse on scroll-in
4. **Particle Effects**: Add subtle floating elements (Hero, Aggregation)
5. **Loading States**: Skeleton screens with shimmer effect

### Advanced Techniques (Future)
- Three.js background for Hero (3D food models)
- Confetti burst on waitlist signup success
- Magnetic cursor effect on buttons
- Number counter animation (stats section)
- SVG path drawing animations

---

*End of Animation Flow Guide*
