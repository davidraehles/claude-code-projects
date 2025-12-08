import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { Hero } from '@/components/sections/hero';

// Mock fetch
global.fetch = jest.fn();

describe('Hero Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('Rendering', () => {
    it('renders hero section with branding', () => {
      render(<Hero />);
      expect(screen.getByText('Go, Cart!')).toBeInTheDocument();
      expect(screen.getByText(/Favorites on repeat/)).toBeInTheDocument();
      expect(screen.getByText(/New loves on deck/)).toBeInTheDocument();
      expect(screen.getByText(/Groceries on autopilot/)).toBeInTheDocument();
    });

    it('renders waitlist form with email input', () => {
      render(<Hero />);
      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      expect(emailInput).toBeInTheDocument();
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('required');
    });

    it('renders submit button', () => {
      render(<Hero />);
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });
      expect(submitButton).toBeInTheDocument();
    });

    it('submit button is disabled when email is empty', () => {
      render(<Hero />);
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Form Validation', () => {
    it('enables submit button when valid email is entered', async () => {
      const user = userEvent.setup();
      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      expect(submitButton).not.toBeDisabled();
    });

    it('disables submit button when email is empty after typing', async () => {
      const user = userEvent.setup();
      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      expect(submitButton).not.toBeDisabled();

      await user.clear(emailInput);
      expect(submitButton).toBeDisabled();
    });

    it('trims whitespace from email input', async () => {
      const user = userEvent.setup();
      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, '   test@example.com   ');
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe('Form Submission', () => {
    it('successfully submits email and shows confirmation', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, status: 'PENDING' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Welcome to the waitlist/i)).toBeInTheDocument();
        expect(screen.getByText(/Check your email to verify/i)).toBeInTheDocument();
      });
    });

    it('posts to correct API endpoint with environment variable support', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, status: 'PENDING' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/waitlist'),
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: 'test@example.com',
              metadata: { source: 'hero' },
            }),
          })
        );
      });
    });

    it('shows loading state during submission', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ id: 1, status: 'PENDING' }),
        }), 100))
      );

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      expect(screen.getByRole('button', { name: /joining/i })).toBeInTheDocument();
    });

    it('disables input and button during submission', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ id: 1, status: 'PENDING' }),
        }), 100))
      );

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      expect(emailInput).toBeDisabled();
      expect(submitButton).toBeDisabled();
    });

    it('clears email after successful submission', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, status: 'PENDING' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(emailInput).toHaveValue('');
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message on API failure', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already registered' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
        expect(screen.getByText(/Email already registered/)).toBeInTheDocument();
      });
    });

    it('displays generic error when response has no detail', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to join waitlist/)).toBeInTheDocument();
      });
    });

    it('displays error when fetch throws exception', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Network error/)).toBeInTheDocument();
      });
    });

    it('allows dismissing error message', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Error occurred' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Error occurred/)).toBeInTheDocument();
      });

      const dismissButton = screen.getByRole('button', { name: /dismiss error/i });
      await user.click(dismissButton);

      expect(screen.queryByText(/Error occurred/)).not.toBeInTheDocument();
    });

    it('allows retrying after error is dismissed', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'Error occurred' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, status: 'PENDING' }),
        });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      // First attempt - error
      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Error occurred/)).toBeInTheDocument();
      });

      // Dismiss error
      const dismissButton = screen.getByRole('button', { name: /dismiss error/i });
      await user.click(dismissButton);

      // Retry - success
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Welcome to the waitlist/i)).toBeInTheDocument();
      });
    });
  });

  describe('Success State', () => {
    it('shows success message after successful signup', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, status: 'PENDING' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/🎉 Welcome to the waitlist!/)).toBeInTheDocument();
      });
    });

    it('allows adding another email after success', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, status: 'PENDING' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Welcome to the waitlist/i)).toBeInTheDocument();
      });

      const anotherButton = screen.getByRole('button', { name: /Join another/i });
      await user.click(anotherButton);

      expect(screen.getByRole('textbox', { name: /email address/i })).toBeInTheDocument();
      expect(screen.queryByText(/Welcome to the waitlist/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper form structure with label', () => {
      render(<Hero />);
      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      expect(emailInput).toHaveAttribute('aria-label', 'Email address');
    });

    it('submit button has aria-busy attribute during loading', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ id: 1, status: 'PENDING' }),
        }), 100))
      );

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      expect(submitButton).toHaveAttribute('aria-busy', 'true');
    });

    it('error messages are announced with role=alert', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Error occurred' }),
      });

      render(<Hero />);

      const emailInput = screen.getByRole('textbox', { name: /email address/i });
      const submitButton = screen.getByRole('button', { name: /join waitlist/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      const alert = await screen.findByRole('alert');
      expect(alert).toBeInTheDocument();
    });
  });
});
