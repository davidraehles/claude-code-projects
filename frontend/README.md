# Go, Cart! - Frontend

AI-powered meal planning application built with Next.js 16, TypeScript, Tailwind CSS, and Material Design 3.

## Features

- **Landing Page**: Marketing site with features, pricing, and FAQs
- **Authentication**: Secure login/signup with NextAuth.js
- **Recipe Library**: Browse and search recipes with filtering
- **Meal Plan Generator**: AI-powered meal plan creation with dietary restrictions
- **Grocery Lists**: Automatic shopping list generation with print/export
- **Mobile Responsive**: Fully optimized for mobile, tablet, and desktop
- **Material Design 3**: Modern, accessible UI with orange branding

## Tech Stack

- **Framework**: Next.js 16 (App Router, Turbopack)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4 + Material Design 3
- **UI Components**: Material UI v6 with custom theme
- **Typography**: Roboto font family
- **Authentication**: NextAuth.js
- **State Management**: React Hooks + React Query
- **API Client**: Fetch API
- **Accessibility**: WCAG 2.1 AA compliant

## Design System

The application uses **Material Design 3** (Material You) with a custom **orange color scheme**.

### Color Palette
- **Primary**: `#FF6F00` (Deep Orange) - Brand color
- **Secondary**: `#424242` (Dark Grey) - Neutral elements
- **Success**: `#4CAF50` (Green)
- **Error**: `#F44336` (Red)
- **Warning**: `#FF9800` (Orange)
- **Info**: `#2196F3` (Blue)

### Key Features
- **Elevation System**: 5 levels of subtle shadows
- **Border Radius**: Rounded corners (12-24px)
- **Typography**: Roboto font with Material Design 3 type scale
- **Accessibility**: Focus indicators, skip links, ARIA labels, keyboard navigation
- **Responsive**: Mobile-first design with proper touch targets (44x44px minimum)

For detailed design system documentation, see [MATERIAL_DESIGN_3.md](./MATERIAL_DESIGN_3.md).

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see main project README)

### Installation

1. Clone the repository and navigate to the frontend directory:
```bash
cd meal-planner-ui
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file based on `.env.example`:
```bash
cp .env.example .env.local
```

4. Update environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000
```

To generate a secure NEXTAUTH_SECRET:
```bash
openssl rand -base64 32
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

Build the application:
```bash
npm run build
```

Start the production server:
```bash
npm start
```

## Deployment to Vercel

### Quick Deploy

The easiest way to deploy is to import the GitHub repository directly in Vercel:

1. **Push your code to GitHub** (if not already done)

2. **Go to [Vercel](https://vercel.com)** and sign in

3. **Click "Add New Project"**

4. **Import your GitHub repository**

5. **Configure environment variables**:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., `https://api.yourapp.com`)
   - `NEXTAUTH_SECRET`: Generate with `openssl rand -base64 32`
   - `NEXTAUTH_URL`: Your Vercel deployment URL (e.g., `https://yourapp.vercel.app`)

6. **Deploy**!

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Environment Variables

Set these in the Vercel dashboard under Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://api.mealplanner.com` |
| `NEXTAUTH_SECRET` | Secret for NextAuth.js sessions | `<random-32-char-string>` |
| `NEXTAUTH_URL` | Frontend URL | `https://mealplanner.vercel.app` |

## Project Structure

```
meal-planner-ui/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── api/auth/          # NextAuth.js API routes
│   │   ├── dashboard/         # Recipe library page
│   │   ├── generate/          # Meal plan generator
│   │   ├── grocery-carts/     # Shopping lists
│   │   ├── login/             # Login page
│   │   ├── meal-plans/        # Meal plans list
│   │   ├── signup/            # Signup page
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── layout/           # Layout components (Header, MobileNav)
│   │   ├── recipe/           # Recipe components
│   │   └── ui/               # UI components (Button, Card, etc.)
│   ├── lib/                   # Utilities and API client
│   │   ├── api.ts            # API client
│   │   ├── auth.ts           # Auth utilities
│   │   └── types.ts          # TypeScript types
│   ├── middleware.ts         # NextAuth middleware
│   └── types/                # TypeScript declarations
├── public/                    # Static assets
├── .env.example              # Environment variables template
├── vercel.json               # Vercel configuration
└── package.json              # Dependencies
```

## Key Features Explained

### Authentication

- Uses NextAuth.js with credentials provider
- Integrates with backend `/api/v1/auth/login` and `/api/v1/auth/signup` endpoints
- JWT-based sessions with 30-day expiry
- Protected routes via middleware

### Mobile Responsiveness

- Hamburger menu on mobile devices
- Responsive grid layouts (1 column → 2 → 3 → 4)
- Touch-friendly buttons and forms
- Optimized typography for all screen sizes

### API Integration

- Centralized API client in `src/lib/api.ts`
- Automatic JWT token handling
- TypeScript types for all API responses
- Error handling and loading states

## Troubleshooting

### Build Errors

If you encounter build errors:

1. Clear Next.js cache:
```bash
rm -rf .next
npm run build
```

2. Verify all environment variables are set

3. Check that the backend API is accessible from your deployment environment

### Authentication Issues

1. Verify `NEXTAUTH_SECRET` is set and matches across deployments
2. Check `NEXTAUTH_URL` matches your actual deployment URL
3. Ensure cookies are enabled in your browser

### Mobile Display Issues

1. Clear browser cache
2. Test in incognito/private mode
3. Check that viewport meta tag is present (it is in layout.tsx)

## Development Tips

### Adding New Pages

1. Create page in `src/app/[page-name]/page.tsx`
2. Use the `Header` component for consistent navigation
3. Follow existing patterns for responsive design

### Styling Guidelines

- Use Tailwind utility classes
- Mobile-first responsive design (`sm:`, `md:`, `lg:`)
- Consistent spacing: `p-4 sm:p-6` for containers
- Text sizing: `text-3xl sm:text-4xl` for headings

### API Calls

Always use the centralized API client:
```typescript
import { api } from '@/lib/api'

const recipes = await api.getRecipes(1, 20)
```

## Support

For issues or questions:
- Check the [DEPLOYMENT.md](./DEPLOYMENT.md) guide
- Review the backend API documentation
- Open an issue on GitHub

## License

This project is part of the Go, Cart! application.
