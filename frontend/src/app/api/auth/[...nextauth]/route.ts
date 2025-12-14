/**
 * NextAuth configuration for authentication.
 */

import NextAuth, { NextAuthOptions } from 'next-auth'
import type { Session } from 'next-auth'
import type { JWT } from 'next-auth/jwt'
import CredentialsProvider from 'next-auth/providers/credentials'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface CustomUser {
  id: string
  email: string
  name: string
  accessToken: string
}

interface CustomJWT extends JWT {
  accessToken?: string
  id?: string
}

interface CustomSession extends Session {
  accessToken?: string
  user: {
    id: string
    email?: string
    name?: string
    image?: string
  }
}

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email', placeholder: 'you@example.com' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          console.error('Missing credentials')
          return null
        }

        try {
          // Use full Railway URL for server-side requests (NextAuth runs on server)
          // Don't use the /api/v1 proxy as that only works client-side
          const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
          
          // Call backend login endpoint
          const loginRes = await fetch(`${backendUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (!loginRes.ok) {
            const error = await loginRes.json().catch(() => ({ detail: 'Login failed' }))
            console.error('Login failed:', error)
            return null
          }

          const tokens = await loginRes.json()

          // Fetch user info using access token
          const userRes = await fetch(`${backendUrl}/api/v1/auth/me`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${tokens.access_token}`,
            },
          })

          if (!userRes.ok) {
            console.error('Failed to fetch user info')
            // Still return user with token, just use email as fallback
            return {
              id: '0',
              email: credentials.email,
              name: credentials.email.split('@')[0],
              accessToken: tokens.access_token,
            } as CustomUser
          }

          const user = await userRes.json()

          // Return user object with token
          return {
            id: user.id.toString(),
            email: user.email,
            name: user.email.split('@')[0],
            accessToken: tokens.access_token,
          } as CustomUser
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Add access_token to the token right after signin
      if (user) {
        const customToken = token as CustomJWT
        const customUser = user as CustomUser
        customToken.accessToken = customUser.accessToken
        customToken.id = customUser.id
      }
      return token as CustomJWT
    },
    async session({ session, token }) {
      // Send properties to the client
      const customSession = session as CustomSession
      const customToken = token as CustomJWT
      if (customToken && customSession.user) {
        // Set id with fallback to sub from token
        customSession.user.id = customToken.id || customToken.sub || ''
        customSession.accessToken = customToken.accessToken
      }
      return customSession
    },
  },
  pages: {
    signIn: '/login',
    signOut: '/login',
    error: '/login',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }
