/**
 * Auth Context - Single Source of Truth for authentication state.
 * Eliminates duplicate auth state across components.
 */

'use client'

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'
import { initTestAuth, restoreAuth, getAuthToken, getCurrentUserEmail as getEmailFromStorage, clearAuth as clearAuthStorage, refreshAuth, isTokenExpiringSoon } from '@/lib/auth'

interface AuthState {
  token: string | null
  user: {
    email: string | null
  } | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthContextValue extends AuthState {
  // Actions
  initializeAuth: () => Promise<void>
  logout: () => void
  refreshToken: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    token: null,
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  })

  /**
   * Initialize authentication on app startup.
   * Attempts to restore from localStorage first, falls back to test auth.
   */
  const initializeAuth = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      // Try to restore existing session
      let token = restoreAuth()

      // If no existing session, initialize with test user
      if (!token) {
        console.log('[AuthContext] No existing session, initializing test auth...')
        token = await initTestAuth()
      }

      if (token) {
        const email = getEmailFromStorage()
        setState({
          token,
          user: { email },
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        console.log('[AuthContext] Authentication successful:', email)
      } else {
        // Failed to authenticate
        setState({
          token: null,
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: 'Failed to authenticate',
        })
        console.error('[AuthContext] Authentication failed')
      }
    } catch (error) {
      console.error('[AuthContext] Error during initialization:', error)
      setState({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Authentication error',
      })
    }
  }, [])

  /**
   * Logout user and clear state.
   */
  const logout = useCallback(() => {
    clearAuthStorage()
    setState({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
    console.log('[AuthContext] User logged out')
  }, [])

  /**
   * Refresh token - re-authenticate if expired.
   * Useful for re-syncing state after external changes or token expiration.
   */
  const refreshToken = useCallback(async () => {
    try {
      // First check if we have a valid token
      const currentToken = getAuthToken()
      const email = getEmailFromStorage()

      if (currentToken && email) {
        setState({
          token: currentToken,
          user: { email },
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        console.log('[AuthContext] Token is still valid')
        return
      }

      // Token expired or not found - re-authenticate
      console.log('[AuthContext] Token invalid, re-authenticating...')
      const newToken = await refreshAuth()

      if (newToken) {
        const newEmail = getEmailFromStorage()
        setState({
          token: newToken,
          user: { email: newEmail },
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        console.log('[AuthContext] Token refreshed successfully')
      } else {
        setState({
          token: null,
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: 'Failed to refresh token',
        })
      }
    } catch (error) {
      console.error('[AuthContext] Error refreshing token:', error)
      setState({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Token refresh failed',
      })
    }
  }, [])

  // Initialize on mount
  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  const value: AuthContextValue = {
    ...state,
    initializeAuth,
    logout,
    refreshToken,
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
