/**
 * React Query hook for Knuspr credential management
 *
 * Provides methods for saving, retrieving, verifying, and deleting credentials.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthToken } from '@/contexts/AuthContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SaveCredentialsRequest {
  knuspr_email: string;
  knuspr_password: string;
  country: 'cz' | 'sk' | 'pl';
  test_connection?: boolean;
}

interface CredentialStatusResponse {
  has_credentials: boolean;
  is_active: boolean;
  country?: string;
  knuspr_email?: string; // Masked
  last_verified_at?: string;
  verification_error?: string;
}

interface VerifyCredentialsResponse {
  is_valid: boolean;
  message: string;
  last_verified_at?: string;
}

interface DeleteCredentialsResponse {
  message: string;
  success: boolean;
}

/**
 * Hook for managing Knuspr credentials
 *
 * Usage:
 * ```tsx
 * const { credentialStatus, saveCredentials, verifyCredentials } = useKnusprCredentials();
 *
 * // Get credential status
 * const status = credentialStatus.data;
 *
 * // Save credentials
 * await saveCredentials.mutateAsync({
 *   knuspr_email: 'user@example.com',
 *   knuspr_password: 'password',
 *   country: 'cz'
 * });
 *
 * // Verify credentials
 * await verifyCredentials.mutateAsync();
 * ```
 */
export const useKnusprCredentials = () => {
  const queryClient = useQueryClient();
  const token = useAuthToken();

  /**
   * Get current credential status
   */
  const credentialStatus = useQuery<CredentialStatusResponse>({
    queryKey: ['knuspr-credentials-status'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/knuspr-credentials`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          // No credentials - return empty status
          return {
            has_credentials: false,
            is_active: false,
            country: undefined,
            knuspr_email: undefined,
            last_verified_at: undefined,
          };
        }
        throw new Error('Failed to fetch credential status');
      }

      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!token, // Only run query if token exists
  });

  /**
   * Save or update credentials
   */
  const saveCredentials = useMutation({
    mutationFn: async (data: SaveCredentialsRequest) => {
      const response = await fetch(`${API_URL}/api/v1/knuspr-credentials`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save credentials');
      }

      return response.json() as Promise<CredentialStatusResponse>;
    },
    onSuccess: () => {
      // Invalidate credential status cache
      queryClient.invalidateQueries({ queryKey: ['knuspr-credentials-status'] });
    },
  });

  /**
   * Verify credentials with Knuspr API
   */
  const verifyCredentials = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/knuspr-credentials/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Verification failed');
      }

      return response.json() as Promise<VerifyCredentialsResponse>;
    },
    onSuccess: () => {
      // Invalidate credential status cache
      queryClient.invalidateQueries({ queryKey: ['knuspr-credentials-status'] });
    },
  });

  /**
   * Delete credentials
   */
  const deleteCredentials = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/knuspr-credentials`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete credentials');
      }

      return response.json() as Promise<DeleteCredentialsResponse>;
    },
    onSuccess: () => {
      // Invalidate credential status cache
      queryClient.invalidateQueries({ queryKey: ['knuspr-credentials-status'] });
    },
  });

  return {
    credentialStatus,
    saveCredentials,
    verifyCredentials,
    deleteCredentials,
  };
};
