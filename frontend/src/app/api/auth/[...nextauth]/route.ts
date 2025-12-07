/**
 * NextAuth configuration for authentication.
 */

import NextAuth, { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
          // Call backend login endpoint
          const loginRes = await fetch(`${API_URL}/api/v1/auth/login`, {
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
          const userRes = await fetch(`${API_URL}/api/v1/auth/me`, {
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
            }
          }

          const user = await userRes.json()

          // Return user object with token
          return {
            id: user.id.toString(),
            email: user.email,
            name: user.email.split('@')[0],
            accessToken: tokens.access_token,
          }
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }: { token: any; user: any }) {
      // Add access_token to the token right after signin
      if (user) {
        token.accessToken = user.accessToken
        token.id = user.id
      }
      return token
    },
    async session({ session, token }: { session: any; token: any }) {
      // Send properties to the client
      if (token && session.user) {
        session.user.id = token.id as string
        session.accessToken = token.accessToken
      }
      return session
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
