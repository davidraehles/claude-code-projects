import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CartErrorHandler, { CartError } from '@/components/knuspr/CartErrorHandler';

describe('CartErrorHandler Component', () => {
  it('renders null when error is null', () => {
    const { container } = render(
      <CartErrorHandler
        error={null}
        onRetry={() => {}}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('displays error message', () => {
    const error: CartError = {
      code: 'PRODUCT_NOT_FOUND',
      message: 'Some ingredients are not available',
      severity: 'warning',
      details: 'One or more ingredients could not be matched to Knuspr products.',
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText('Some ingredients are not available')).toBeInTheDocument();
  });

  it('displays error details', () => {
    const error: CartError = {
      code: 'KNUSPR_CONNECTION_TIMEOUT',
      message: 'Unable to connect to Knuspr',
      severity: 'error',
      details: 'The connection to Knuspr took too long to respond.',
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText('The connection to Knuspr took too long to respond.')).toBeInTheDocument();
  });

  it('displays error code badge', () => {
    const error: CartError = {
      code: 'MISSING_CREDENTIALS',
      message: 'Knuspr credentials not configured',
      severity: 'warning',
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText('MISSING_CREDENTIALS')).toBeInTheDocument();
  });

  it('shows suggestions for error recovery', () => {
    const error: CartError = {
      code: 'PRODUCT_NOT_FOUND',
      message: 'Some ingredients are not available',
      severity: 'warning',
      suggestions: [
        'Review unavailable items',
        'Add alternatives manually',
        'Try different ingredient names',
      ],
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    expect(screen.getByText(/Review unavailable items/)).toBeInTheDocument();
    expect(screen.getByText(/Add alternatives manually/)).toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', () => {
    const onRetry = jest.fn();
    const error: CartError = {
      code: 'KNUSPR_CONNECTION_TIMEOUT',
      message: 'Unable to connect to Knuspr',
      severity: 'error',
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={onRetry}
      />
    );

    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalled();
  });

  it('calls onContactSupport when support button is clicked', () => {
    const onContactSupport = jest.fn();
    const error: CartError = {
      code: 'CART_CREATION_FAILED',
      message: 'Failed to create shopping cart',
      severity: 'error',
    };

    render(
      <CartErrorHandler
        error={error}
        onContactSupport={onContactSupport}
      />
    );

    const supportButton = screen.getByText('Contact Support');
    fireEvent.click(supportButton);

    expect(onContactSupport).toHaveBeenCalled();
  });

  it('calls onDismiss when dismiss button is clicked', () => {
    const onDismiss = jest.fn();
    const error: CartError = {
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Too many requests',
      severity: 'warning',
    };

    render(
      <CartErrorHandler
        error={error}
        onDismiss={onDismiss}
      />
    );

    const dismissButton = screen.getByLabelText('Dismiss error');
    fireEvent.click(dismissButton);

    expect(onDismiss).toHaveBeenCalled();
  });

  it('applies error severity styling', () => {
    const error: CartError = {
      code: 'KNUSPR_CONNECTION_TIMEOUT',
      message: 'Unable to connect',
      severity: 'error',
    };

    const { container } = render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    const errorBox = container.querySelector('.bg-red-50');
    expect(errorBox).toBeInTheDocument();
  });

  it('applies warning severity styling', () => {
    const error: CartError = {
      code: 'PRODUCT_NOT_FOUND',
      message: 'Items not available',
      severity: 'warning',
    };

    const { container } = render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    const warningBox = container.querySelector('.bg-amber-50');
    expect(warningBox).toBeInTheDocument();
  });

  it('uses pre-configured error details for known error codes', () => {
    const error: CartError = {
      code: 'INVALID_CREDENTIALS',
      message: 'Test message override',
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    // Should show the overridden message, not the pre-configured one
    expect(screen.getByText('Test message override')).toBeInTheDocument();
  });

  it('displays help documentation link', () => {
    const error: CartError = {
      code: 'DELIVERY_SLOT_ERROR',
      message: 'No delivery slots available',
      severity: 'warning',
    };

    render(
      <CartErrorHandler
        error={error}
        onRetry={() => {}}
      />
    );

    const helpLink = screen.getByText('View Help Documentation');
    expect(helpLink).toBeInTheDocument();
  });
});
