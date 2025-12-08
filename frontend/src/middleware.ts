/**
 * Proxy middleware for protecting routes with NextAuth.
 * Renamed from middleware.ts to address Next.js deprecation warning.
 */

import { withAuth } from 'next-auth/middleware'

export default withAuth({
  pages: {
    signIn: '/login',
  },
})

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/generate/:path*',
    '/meal-plans/:path*',
    '/grocery-carts/:path*',
  ],
}
