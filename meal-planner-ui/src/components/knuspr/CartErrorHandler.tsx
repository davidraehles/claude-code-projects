'use client';

import React from 'react';
import { AlertTriangle, AlertCircle, RefreshCw, Phone, MessageCircle, ArrowLeft, HelpCircle } from 'lucide-react';

export type ErrorSeverity = 'error' | 'warning' | 'info';

export interface CartError {
  code: string;
  message: string;
  severity?: ErrorSeverity;
  details?: string;
  suggestions?: string[];
  action?: {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  };
}

interface CartErrorHandlerProps {
  error: CartError | null;
  onRetry?: () => void;
  onDismiss?: () => void;
  onContactSupport?: () => void;
}

const errorConfigs: Record<string, Partial<CartError>> = {
  KNUSPR_CONNECTION_TIMEOUT: {
    message: 'Unable to connect to Knuspr',
    details: 'The connection to Knuspr took too long to respond.',
    severity: 'error',
    suggestions: [
      'Check your internet connection',
      'Wait a few moments and try again',
      'Contact support if the issue persists',
    ],
  },
  PRODUCT_NOT_FOUND: {
    message: 'Some ingredients are not available',
    details: 'One or more ingredients could not be matched to Knuspr products.',
    severity: 'warning',
    suggestions: [
      'Review unavailable items',
      'Add alternatives manually',
      'Try different ingredient names',
    ],
  },
  INVALID_CREDENTIALS: {
    message: 'Knuspr credentials are invalid',
    details: 'Your Knuspr account credentials could not be verified.',
    severity: 'error',
    suggestions: [
      'Update your Knuspr credentials in settings',
      'Verify your email and password are correct',
      'Contact Knuspr support if you forgot your password',
    ],
  },
  MISSING_CREDENTIALS: {
    message: 'Knuspr credentials not configured',
    details: 'Please add your Knuspr account details to use this feature.',
    severity: 'warning',
    suggestions: [
      'Go to Settings → Knuspr Integration',
      'Enter your Knuspr email and password',
      'Verify your credentials',
    ],
  },
  DELIVERY_SLOT_ERROR: {
    message: 'No delivery slots available',
    details: 'There are no available delivery slots for your area or date range.',
    severity: 'warning',
    suggestions: [
      'Try a different delivery date',
      'Check if your address is within Knuspr service area',
      'Contact Knuspr support for assistance',
    ],
  },
  CART_CREATION_FAILED: {
    message: 'Failed to create shopping cart',
    details: 'The cart could not be created on Knuspr.',
    severity: 'error',
    suggestions: [
      'Check that items are in stock',
      'Verify your Knuspr account is active',
      'Try again in a moment',
    ],
  },
  RATE_LIMIT_EXCEEDED: {
    message: 'Too many requests',
    details: 'You have exceeded the rate limit for cart generation.',
    severity: 'warning',
    suggestions: [
      'Wait a few minutes before trying again',
      'Check back in 5 minutes',
    ],
  },
  GENERIC_ERROR: {
    message: 'Something went wrong',
    details: 'An unexpected error occurred. Please try again.',
    severity: 'error',
    suggestions: [
      'Refresh the page',
      'Try again in a moment',
      'Contact support if problem persists',
    ],
  },
};

export const CartErrorHandler: React.FC<CartErrorHandlerProps> = ({
  error,
  onRetry,
  onDismiss,
  onContactSupport,
}) => {
  if (!error) {
    return null;
  }

  const config = errorConfigs[error.code] || errorConfigs.GENERIC_ERROR;
  const mergedError = { ...config, ...error };

  const severity = mergedError.severity || 'error';

  const colors = {
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: 'text-red-600',
      badge: 'bg-red-100 text-red-800',
      button: 'bg-red-600 hover:bg-red-700',
      text: 'text-red-900',
      lightText: 'text-red-800',
    },
    warning: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      icon: 'text-amber-600',
      badge: 'bg-amber-100 text-amber-800',
      button: 'bg-amber-600 hover:bg-amber-700',
      text: 'text-amber-900',
      lightText: 'text-amber-800',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'text-blue-600',
      badge: 'bg-blue-100 text-blue-800',
      button: 'bg-blue-600 hover:bg-blue-700',
      text: 'text-blue-900',
      lightText: 'text-blue-800',
    },
  };

  const currentColors = colors[severity];

  const getIcon = () => {
    switch (severity) {
      case 'error':
        return <AlertTriangle className={`h-6 w-6 ${currentColors.icon}`} />;
      case 'warning':
        return <AlertCircle className={`h-6 w-6 ${currentColors.icon}`} />;
      case 'info':
        return <HelpCircle className={`h-6 w-6 ${currentColors.icon}`} />;
    }
  };

  return (
    <div className={`rounded-lg border-2 ${currentColors.border} ${currentColors.bg} p-6`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start gap-4">
          {getIcon()}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className={`text-lg font-bold ${currentColors.text}`}>
                {mergedError.message}
              </h3>
              <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${currentColors.badge}`}>
                {error.code}
              </span>
            </div>
            {mergedError.details && (
              <p className={`text-sm ${currentColors.lightText}`}>
                {mergedError.details}
              </p>
            )}
          </div>

          {/* Dismiss Button */}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className={`rounded p-1 ${currentColors.bg} hover:${currentColors.badge} transition-colors flex-shrink-0`}
              aria-label="Dismiss error"
            >
              <span className={`${currentColors.icon}`}>✕</span>
            </button>
          )}
        </div>

        {/* Suggestions */}
        {mergedError.suggestions && mergedError.suggestions.length > 0 && (
          <div className={`rounded-lg ${currentColors.badge.split(' ')[0]} p-4 space-y-2`}>
            <p className="text-sm font-semibold">💡 What you can try:</p>
            <ul className="space-y-2">
              {mergedError.suggestions.map((suggestion, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <span className="mt-1">→</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          {onRetry && (
            <button
              onClick={onRetry}
              className={`inline-flex items-center gap-2 rounded-lg ${currentColors.button} text-white px-4 py-2 font-semibold transition-colors`}
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>
          )}

          {onContactSupport && (
            <button
              onClick={onContactSupport}
              className={`inline-flex items-center gap-2 rounded-lg border-2 ${currentColors.border} ${currentColors.text} px-4 py-2 font-semibold hover:${currentColors.bg} transition-colors`}
            >
              <Phone className="h-4 w-4" />
              Contact Support
            </button>
          )}

          {!onRetry && (
            <a
              href="/dashboard"
              className={`inline-flex items-center gap-2 rounded-lg border-2 ${currentColors.border} ${currentColors.text} px-4 py-2 font-semibold hover:${currentColors.bg} transition-colors`}
            >
              <ArrowLeft className="h-4 w-4" />
              Go Back
            </a>
          )}
        </div>

        {/* Help Link */}
        <div className="text-center pt-2">
          <a
            href="/help"
            className={`inline-flex items-center gap-1 text-sm ${currentColors.lightText} hover:font-semibold transition-all`}
          >
            <MessageCircle className="h-4 w-4" />
            View Help Documentation
          </a>
        </div>
      </div>
    </div>
  );
};

export default CartErrorHandler;
