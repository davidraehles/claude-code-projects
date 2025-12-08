# Go, Cart! - Frontend

AI-powered meal planning application built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Landing Page**: Marketing site with features, pricing, and FAQs
- **Authentication**: Secure login/signup with NextAuth.js
- **Recipe Library**: Browse and search recipes with filtering
- **Meal Plan Generator**: AI-powered meal plan creation with dietary restrictions
- **Grocery Lists**: Automatic shopping list generation with print/export
- **Mobile Responsive**: Fully optimized for mobile, tablet, and desktop

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: NextAuth.js
- **State Management**: React Hooks
- **API Client**: Fetch API

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
