/**
 * Authentication utilities for managing user sessions.
 * Refactored to work with immutable API client.
 */

import { api } from './api'
import type { LoginRequest } from './types'

const TEST_USER: LoginRequest = {
  email: 'test@example.com',
  password: 'testpassword123',
}

/**
 * Initialize authentication with test user.
 * Returns token instead of mutating API client.
 */
export async function initTestAuth(): Promise<string | null> {
  try {
    const response = await api.login(TEST_USER)

    // Persist to localStorage (for session restoration)
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('user_email', TEST_USER.email)
    }

    console.log('✅ Test user authenticated:', TEST_USER.email)
    return response.access_token
  } catch (error) {
    console.error('❌ Test auth failed:', error)
    return null
  }
}

/**
 * Restore authentication from localStorage.
 * Returns token instead of mutating API client.
 */
export function restoreAuth(): string | null {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    if (token) {
      console.log('✅ Auth restored from localStorage')
      return token
    }
  }
  return null
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
 * Get current auth token from localStorage.
 */
export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token')
  }
  return null
}

/**
 * Clear authentication data.
 */
export function clearAuth(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_email')
    console.log('✅ Auth cleared')
  }
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}
