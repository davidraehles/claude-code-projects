/**
 * Knuspr Settings Component
 *
 * Display Knuspr credential status and allow users to:
 * - Add/update credentials
 * - Verify credentials
 * - Remove credentials
 * - View last verification status
 */

import React, { useState } from 'react';
import { useKnusprCredentials } from '@/hooks/queries/useKnusprCredentials';
import { KnusprSetupModal } from './KnusprSetupModal';

export const KnusprSettings: React.FC = () => {
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [verifyMessage, setVerifyMessage] = useState<string | null>(null);
  const [deleteMessage, setDeleteMessage] = useState<string | null>(null);

  const {
    credentialStatus,
    saveCredentials,
    verifyCredentials,
    deleteCredentials,
  } = useKnusprCredentials();

  const status = credentialStatus.data;
  const isLoading = credentialStatus.isLoading;
  const hasCredentials = status?.has_credentials || false;
  const isActive = status?.is_active || false;

  const handleVerify = async () => {
    try {
      setVerifyMessage(null);
      const result = await verifyCredentials.mutateAsync();
      setVerifyMessage(result.message);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Verification failed';
      setVerifyMessage(message);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure? This will disconnect your Knuspr account.')) {
      return;
    }

    try {
      setDeleteMessage(null);
      const result = await deleteCredentials.mutateAsync();
      setDeleteMessage(result.message);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete credentials';
      setDeleteMessage(message);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg">
        <p className="text-gray-600">Loading Knuspr settings...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="knuspr-settings">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Knuspr Integration</h2>
        <p className="text-gray-600 mt-1">
          Connect your Knuspr account to enable automatic grocery ordering
        </p>
      </div>

      {/* Status Card */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {/* Status Indicator */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Account Status</h3>
          {hasCredentials && (
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                isActive
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
              data-testid="credential-status-badge"
            >
              {isActive ? '✓ Connected' : '⚠ Inactive'}
            </span>
          )}
        </div>

        {hasCredentials ? (
          <div className="space-y-4">
            {/* Credential Details */}
            <div className="grid grid-cols-2 gap-4 pb-4 border-b border-gray-200">
              <div>
                <p className="text-sm text-gray-600">Email/Phone</p>
                <p className="text-sm font-medium text-gray-900" data-testid="credential-email">
                  {status?.knuspr_email || '••••••••'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Country</p>
                <p className="text-sm font-medium text-gray-900" data-testid="credential-country">
                  {status?.country?.toUpperCase() || 'Unknown'}
                </p>
              </div>
            </div>

            {/* Verification Status */}
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Last Verification</p>
              {status?.last_verified_at ? (
                <p className="text-sm text-green-700">
                  ✓ Verified on {new Date(status.last_verified_at).toLocaleString()}
                </p>
              ) : (
                <p className="text-sm text-yellow-700">
                  ⚠ Not yet verified
                </p>
              )}

              {status?.verification_error && (
                <p className="text-sm text-red-700">
                  Error: {status.verification_error}
                </p>
              )}
            </div>

            {/* Messages */}
            {verifyMessage && (
              <div
                className={`p-3 rounded-md ${
                  verifyMessage.includes('successfully')
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700'
                }`}
                data-testid="verify-message"
              >
                <p className="text-sm">{verifyMessage}</p>
              </div>
            )}

            {deleteMessage && (
              <div className="p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-700">{deleteMessage}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleVerify}
                disabled={verifyCredentials.isPending}
                className="flex-1 px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 disabled:opacity-50"
                data-testid="verify-credentials-button"
              >
                {verifyCredentials.isPending ? 'Verifying...' : 'Verify Credentials'}
              </button>
              <button
                onClick={() => setShowSetupModal(true)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                data-testid="update-credentials-button"
              >
                Update Credentials
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteCredentials.isPending}
                className="flex-1 px-4 py-2 border border-red-600 text-red-600 rounded-md hover:bg-red-50 disabled:opacity-50"
                data-testid="delete-credentials-button"
              >
                {deleteCredentials.isPending ? 'Removing...' : 'Disconnect'}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-700">
                No Knuspr account connected yet. Connect your account to enable automatic grocery ordering.
              </p>
            </div>
            <button
              onClick={() => setShowSetupModal(true)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              data-testid="connect-knuspr-button"
            >
              Connect Knuspr Account
            </button>
          </div>
        )}
      </div>

      {/* Security Info */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-3">🔒 Security</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ Your credentials are encrypted before storage</li>
          <li>✓ Password is never transmitted in plain text</li>
          <li>✓ We only use your credentials for Knuspr API calls</li>
          <li>✓ You can disconnect anytime</li>
          <li>✓ Compliant with GDPR data protection</li>
        </ul>
      </div>

      {/* Setup Modal */}
      <KnusprSetupModal
        isOpen={showSetupModal}
        onClose={() => setShowSetupModal(false)}
        onSuccess={() => setShowSetupModal(false)}
      />
    </div>
  );
};
