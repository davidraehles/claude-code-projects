/**
 * Simple test authentication utility.
 * For development/testing only - replace with NextAuth later.
 */

import { api } from './api'

// Test user credentials
export const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
}

/**
 * Initialize test authentication by logging in with test credentials.
 * Call this on app startup for development.
 */
export async function initTestAuth(): Promise<boolean> {
  try {
    // Try to login with test credentials
    const response = await api.login(TEST_USER)

    // Set the token in the API client
    api.setToken(response.access_token)

    // Store token in localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('user_email', TEST_USER.email)
    }

    console.log('✅ Test user authenticated:', TEST_USER.email)
    return true
  } catch (error) {
    console.error('❌ Test auth failed:', error)
    return false
  }
}

/**
 * Restore authentication from localStorage if available.
 */
export function restoreAuth(): boolean {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    if (token) {
      api.setToken(token)
      console.log('✅ Auth restored from localStorage')
      return true
    }
  }
  return false
}

/**
 * Clear authentication.
 */
export function clearAuth(): void {
  api.clearToken()
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_email')
  }
  console.log('🚪 Logged out')
}

/**
 * Get current user email from localStorage.
 */
export function getCurrentUserEmail(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('user_email')
  }
  return null
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  if (typeof window !== 'undefined') {
    return !!localStorage.getItem('auth_token')
  }
  return false
}
