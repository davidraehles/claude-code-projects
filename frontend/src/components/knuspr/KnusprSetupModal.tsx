/**
 * Knuspr Setup Modal Component
 *
 * Modal for users to add or update their Knuspr credentials.
 * Provides secure input for Knuspr account details and tests credentials.
 */

import React, { useState } from 'react';
import { useKnusprCredentials } from '@/hooks/queries/useKnusprCredentials';

interface KnusprSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type Country = 'cz' | 'sk' | 'pl';

const COUNTRIES: { value: Country; label: string; description: string }[] = [
  { value: 'cz', label: 'Česká republika', description: 'Czech Republic' },
  { value: 'sk', label: 'Slovensko', description: 'Slovakia' },
  { value: 'pl', label: 'Polska', description: 'Poland' },
];

export const KnusprSetupModal: React.FC<KnusprSetupModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [country, setCountry] = useState<Country>('cz');
  const [testConnection, setTestConnection] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { saveCredentials, verifyCredentials } = useKnusprCredentials();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Validate inputs
      if (!email.trim()) {
        throw new Error('Email or phone number is required');
      }
      if (!password.trim()) {
        throw new Error('Password is required');
      }
      if (password.length < 6) {
        throw new Error('Password appears invalid (too short)');
      }

      // Save credentials
      await saveCredentials.mutateAsync({
        knuspr_email: email.trim(),
        knuspr_password: password,
        country,
        test_connection: testConnection,
      });

      // Success
      onClose();
      onSuccess?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save credentials';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4" data-testid="knuspr-setup-modal">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Connect Knuspr Account</h2>
          <p className="text-sm text-gray-600 mt-1">
            Add your Knuspr login to enable automatic grocery ordering
          </p>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Error Alert */}
          {error && (
            <div
              className="p-3 bg-red-50 border border-red-200 rounded-md"
              data-testid="credential-error"
            >
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Country Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Country
            </label>
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value as Country)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="country-select"
            >
              {COUNTRIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          {/* Email/Phone Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email or Phone Number
            </label>
            <input
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com or +420..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="knuspr-email-input"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">
              Your Knuspr login credentials (email or phone)
            </p>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="knuspr-password-input"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">
              Your Knuspr password (encrypted before storage)
            </p>
          </div>

          {/* Test Connection Checkbox */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="test-connection"
              checked={testConnection}
              onChange={(e) => setTestConnection(e.target.checked)}
              className="rounded"
              data-testid="test-connection-checkbox"
              disabled={isLoading}
            />
            <label htmlFor="test-connection" className="ml-2 text-sm text-gray-700">
              Test connection before saving
            </label>
          </div>

          {/* Security Note */}
          <div className="p-3 bg-blue-50 rounded-md">
            <p className="text-xs text-blue-700">
              🔒 Your credentials are encrypted and stored securely. We never share your Knuspr password.
            </p>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !email.trim() || !password.trim()}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="save-credentials-button"
            >
              {isLoading ? 'Saving...' : 'Save Credentials'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
