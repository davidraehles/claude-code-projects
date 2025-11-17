/**
 * Middleware for protecting routes with NextAuth.
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
