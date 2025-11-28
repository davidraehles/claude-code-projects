/**
 * Authentication utilities for managing user sessions.
 * Refactored to work with immutable API client.
 * Includes automatic token refresh on expiration.
 */

import { api } from './api'
import type { LoginRequest } from './types'

const TEST_USER: LoginRequest = {
  email: 'test@example.com',
  password: 'testpassword123',
}

const TOKEN_EXPIRY_KEY = 'auth_token_expiry'
const ACCESS_TOKEN_EXPIRE_MINUTES = 30 // Must match backend

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
      // Store token expiry time (current time + 30 minutes)
      const expiryTime = Date.now() + ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 1000
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString())
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
      // Check if token is expired
      const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY)
      if (expiryTime && Date.now() > parseInt(expiryTime)) {
        console.log('⚠️ Auth token expired, clearing...')
        clearAuth()
        return null
      }
      console.log('✅ Auth restored from localStorage')
      return token
    }
  }
  return null
}

/**
 * Refresh authentication by re-logging in with test user.
 * Called when token expires or 403 error occurs.
 */
export async function refreshAuth(): Promise<string | null> {
  console.log('🔄 Refreshing authentication...')
  clearAuth()
  return initTestAuth()
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
    const token = localStorage.getItem('auth_token')
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY)

    // Check if token exists and hasn't expired
    if (token && expiryTime && Date.now() < parseInt(expiryTime)) {
      return token
    }

    // Token is expired or doesn't exist
    if (token && expiryTime && Date.now() > parseInt(expiryTime)) {
      console.log('⚠️ Token expired, clearing...')
      clearAuth()
    }

    return null
  }
  return null
}

/**
 * Check if token is about to expire (within 5 minutes).
 */
export function isTokenExpiringSoon(): boolean {
  if (typeof window !== 'undefined') {
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY)
    if (expiryTime) {
      const timeUntilExpiry = parseInt(expiryTime) - Date.now()
      return timeUntilExpiry < 5 * 60 * 1000 // 5 minutes
    }
  }
  return false
}

/**
 * Clear authentication data.
 */
export function clearAuth(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_email')
    localStorage.removeItem(TOKEN_EXPIRY_KEY)
    console.log('✅ Auth cleared')
  }
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}
