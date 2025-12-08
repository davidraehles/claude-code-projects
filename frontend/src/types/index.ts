/**
 * Shared TypeScript types for Go, Cart! frontend.
 * Matches backend models and API contracts.
 */

export enum WaitlistStatus {
  PENDING = 'PENDING',
  VERIFIED = 'VERIFIED',
  INVITED = 'INVITED',
  ONBOARDED = 'ONBOARDED',
}

export interface WaitlistEntry {
  id: number;
  email: string;
  status: WaitlistStatus;
  position?: number;
  created_at: string;
  verified_at?: string | null;
  invited_at?: string | null;
}

export type ThemePreference = 'light' | 'dark' | 'system';

export interface WaitlistCreate {
  email: string;
  metadata?: Record<string, unknown>;
}

export interface WaitlistResponse extends WaitlistEntry {
  position?: number;
}
