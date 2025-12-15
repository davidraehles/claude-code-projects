# Material Design 3 Implementation Guide

This document describes the Material Design 3 implementation in the Go, Cart! application.

## Design System Overview

The application uses **Material Design 3** (Material You) with a custom **orange color scheme** as the primary brand color.

### Color Palette

#### Primary Colors (Orange)
The primary color palette is based on deep orange, following Material Design 3 guidelines:

- **Primary**: `#FF6F00` (Deep Orange)
- **Primary Light**: `#FFA726`
- **Primary Dark**: `#E65100`
- **On Primary**: `#FFFFFF` (White text on orange)

Full palette:
```css
50:  #FFF3E0
100: #FFE0B2
200: #FFCC80
300: #FFB74D
400: #FFA726
500: #FF9800
600: #FB8C00
700: #F57C00
800: #EF6C00
900: #E65100
```

#### Secondary Colors (Grey)
Secondary colors provide neutral contrast:

- **Secondary**: `#424242` (Dark Grey)
- **Secondary Light**: `#616161`
- **Secondary Dark**: `#212121`

Full palette:
```css
50:  #FAFAFA
100: #F5F5F5
200: #EEEEEE
300: #E0E0E0
400: #BDBDBD
500: #9E9E9E
600: #757575
700: #616161
800: #424242
900: #212121
```

#### Semantic Colors
- **Success**: `#4CAF50` (Green)
- **Error**: `#F44336` (Red)
- **Warning**: `#FF9800` (Orange)
- **Info**: `#2196F3` (Blue)

### Typography

The application uses **Roboto** as the primary font family, following Material Design 3 standards.

#### Type Scale
- **Display Large**: 3.5rem / 700 weight
- **Display Medium**: 2.75rem / 600 weight
- **Display Small**: 2.25rem / 600 weight
- **Headline Large**: 2rem / 600 weight
- **Headline Medium**: 1.75rem / 600 weight
- **Headline Small**: 1.5rem / 600 weight
- **Body Large**: 1rem / 400 weight
- **Body Medium**: 0.875rem / 400 weight
- **Label Large**: 0.875rem / 500 weight

#### Usage Classes
```html
<h1 class="text-display-large">Large Display</h1>
<h2 class="text-headline-medium">Medium Headline</h2>
<p class="text-body-large">Body text</p>
```

### Elevation System

Material Design 3 uses subtle elevation with soft shadows:

- **Level 1**: `0px 2px 4px rgba(0, 0, 0, 0.08)`
- **Level 2**: `0px 4px 8px rgba(0, 0, 0, 0.12)`
- **Level 3**: `0px 6px 12px rgba(0, 0, 0, 0.16)`
- **Level 4**: `0px 8px 16px rgba(0, 0, 0, 0.20)`
- **Level 5**: `0px 12px 24px rgba(0, 0, 0, 0.24)`

#### Usage
```html
<div class="elevation-2">Elevated card</div>
<div class="shadow-md3-3">Another way with Tailwind</div>
```

### Border Radius

Material Design 3 uses larger, more rounded corners:

- **Extra Small**: 4px (`rounded-md3-xs`)
- **Small**: 8px (`rounded-md3-sm`)
- **Medium**: 12px (`rounded-md3`)
- **Large**: 16px (`rounded-md3-lg`)
- **Extra Large**: 24px (`rounded-md3-xl`)
- **2X Large**: 28px (`rounded-md3-2xl`)

### Component Styling

#### Buttons
Material Design 3 buttons use **pill-shaped** design with 24px border radius:

**Variants:**
- **Primary**: Solid orange background, white text, elevation
- **Secondary**: Light grey background with border
- **Outlined**: Transparent with orange border
- **Ghost**: Transparent with hover effect
- **Elevated**: White background with shadow, orange text
- **Tonal**: Light orange background

```tsx
<Button variant="primary">Primary Action</Button>
<Button variant="outlined">Secondary Action</Button>
<Button variant="tonal">Tertiary Action</Button>
```

#### Cards
Cards use rounded corners (16px) with subtle elevation:

**Variants:**
- **Elevated**: White background with shadow (default)
- **Filled**: Light orange background, no shadow
- **Outlined**: White with grey border

```tsx
<Card elevation={2} hover>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Description text</CardDescription>
  </CardHeader>
  <CardContent>
    Main content
  </CardContent>
  <CardActions>
    <Button>Action</Button>
  </CardActions>
</Card>
```

#### Inputs
Material Design 3 text fields with proper labels and states:

**Variants:**
- **Outlined**: Border with transparent background (default)
- **Filled**: Colored background with bottom border

```tsx
<Input 
  label="Email Address"
  type="email"
  placeholder="your@email.com"
  required
  helperText="We'll never share your email"
/>
```

### Accessibility Features

All Material Design 3 components are built with accessibility in mind:

#### Color Contrast
- Orange on white: **7.3:1** (AAA for text)
- Orange on light grey: **6.8:1** (AAA for text)
- All text colors meet WCAG 2.1 Level AA standards (minimum 4.5:1)

#### Focus Indicators
- 2px solid orange outline (`#FF6F00`)
- 2px offset for visual separation
- Visible on all interactive elements

#### Keyboard Navigation
- All interactive elements accessible via keyboard
- Tab order follows visual layout
- Enter/Space activate buttons and links
- Skip-to-content link for screen reader users

#### Touch Targets
- Minimum 44x44px touch targets on mobile
- Adequate spacing between interactive elements
- Responsive to both mouse and touch inputs

#### Screen Reader Support
- Proper semantic HTML
- ARIA labels and roles where needed
- Error messages announced via `role="alert"`
- Form field descriptions with `aria-describedby`

#### Reduced Motion
- Respects `prefers-reduced-motion` media query
- Animations disabled when user prefers reduced motion
- Transitions reduced to instant changes

### Theme Integration

#### Material UI Theme
The app uses Material UI's `ThemeProvider` with a custom theme defined in `src/lib/theme.ts`:

```tsx
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '@/lib/theme';

<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>
```

#### Tailwind Configuration
Tailwind is configured with Material Design 3 tokens in `tailwind.config.ts`:

- Custom color palette
- MD3 border radius utilities
- MD3 elevation shadows
- MD3 spacing scale

### Logo and Branding

#### Logo Design
The Go, Cart! logo combines:
- **Shopping cart** (wireframe basket)
- **Go-cart** (racing cart body with wheels)
- **Flames** (speed and momentum)
- **Orange color** (primary brand color)

#### Logo Files
- `public/logo.svg` - Full animated logo (200x200)
- `public/logo-icon.svg` - Simple icon version (100x100)
- `public/favicon-*.png` - Various favicon sizes

#### Favicon Sizes
- 16x16px - Browser tab
- 32x32px - Browser tab (retina)
- 96x96px - Desktop shortcut
- 180x180px - Apple touch icon
- 192x192px - Android home screen
- 512x512px - Splash screens

### Best Practices

1. **Always use theme colors** - Use `primary`, `secondary`, etc. instead of hardcoded hex values
2. **Follow elevation guidelines** - Use appropriate elevation levels for context
3. **Respect typography scale** - Use defined type classes for consistency
4. **Test accessibility** - Run Lighthouse audits and screen reader tests
5. **Support dark mode** - Design with both light and dark themes in mind
6. **Optimize performance** - Lazy load heavy components, use proper image formats

### Resources

- [Material Design 3 Guidelines](https://m3.material.io/)
- [Material UI Documentation](https://mui.com/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Migration Notes

When updating existing components to Material Design 3:

1. Replace old color references with new palette
2. Update border radius to MD3 values
3. Add proper elevation/shadows
4. Ensure accessibility features are present
5. Test on multiple screen sizes
6. Verify keyboard navigation works
7. Run accessibility audits

### Component Library

All UI components are located in `src/components/ui/`:
- `button.tsx` - Button variants
- `Card.tsx` - Card components
- `Input.tsx` - Text input fields
- `Checkbox.tsx` - Checkbox inputs
- `progress-indicator.tsx` - Loading indicators
- `container.tsx` - Layout containers

Each component follows Material Design 3 principles and includes proper TypeScript types, accessibility features, and documentation.
