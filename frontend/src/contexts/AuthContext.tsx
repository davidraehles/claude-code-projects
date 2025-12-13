/**
 * Auth Context - Single Source of Truth for authentication state.
 * Eliminates duplicate auth state across components.
 */

'use client'

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'
import { useSession, signOut } from 'next-auth/react'

interface AuthState {
  token: string | null
  user: {
    email: string | null
    name: string | null
  } | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthContextValue extends AuthState {
  // Actions
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { data: session, status } = useSession()

  const [state, setState] = useState<AuthState>({
    token: null,
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  })

  useEffect(() => {
    if (status === 'loading') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setState(prev => ({ ...prev, isLoading: true }))
      return
    }

    if (status === 'authenticated' && session) {
      // Extract token from session (assuming it's added to session in next-auth config)
      const token = ((session as unknown) as { accessToken?: string }).accessToken || null

      setState({
        token,
        user: {
          email: session.user?.email || null,
          name: session.user?.name || null,
        },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } else {
      setState({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })
    }
  }, [session, status])

  /**
   * Logout user and clear state.
   */
  const logout = useCallback(() => {
    signOut({ callbackUrl: '/login' })
  }, [])

  const value: AuthContextValue = {
    ...state,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * Hook to access auth context.
 * Throws error if used outside AuthProvider.
 */
export function useAuth() {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}

/**
 * Hook to get auth token for API calls.
 * Returns null if not authenticated.
 */
export function useAuthToken(): string | null {
  const { token } = useAuth()
  return token
}
