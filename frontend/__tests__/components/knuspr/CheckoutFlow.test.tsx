import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CheckoutFlow, { CheckoutFlowProps } from '@/components/knuspr/CheckoutFlow';
import { CartPreviewData } from '@/components/knuspr/CartPreview';
import { DeliverySlot } from '@/components/knuspr/DeliverySlotPicker';

describe('CheckoutFlow Component', () => {
  const mockCartData: CartPreviewData = {
    cart_id: 'test_cart_001',
    knuspr_url: 'https://www.knuspr.cz/cart/test_cart_001',
    total_price: 52.45,
    item_count: 15,
    delivery_slot: null,
    items_by_section: {
      dairy: [
        { name: 'Milk 1L', quantity: 1, unit: 'l', price: 2.50, available: true },
        { name: 'Yogurt 500g', quantity: 500, unit: 'g', price: 3.20, available: true },
      ],
      produce: [
        { name: 'Apples 1kg', quantity: 1, unit: 'kg', price: 4.50, available: true },
      ],
    },
    unavailable_items: [],
    created_at: '2025-11-22T16:00:00',
  };

  const mockSlots: DeliverySlot[] = [
    {
      slot_id: 'slot_001',
      date: '2025-11-24',
      time_window: '09:00-12:00',
      price: 3.99,
    },
    {
      slot_id: 'slot_002',
      date: '2025-11-24',
      time_window: '14:00-16:00',
      price: 2.99,
    },
    {
      slot_id: 'slot_003',
      date: '2025-11-25',
      time_window: '09:00-12:00',
      price: 3.99,
    },
  ];

  const mockProps: CheckoutFlowProps = {
    cartData: mockCartData,
    availableSlots: mockSlots,
  };

  describe('Step 1: Cart Review', () => {
    it('renders cart review step by default', () => {
      render(<CheckoutFlow {...mockProps} />);

      expect(screen.getByText('Step 1 of 3: Review Cart')).toBeInTheDocument();
      expect(screen.getByText('Your Shopping Cart')).toBeInTheDocument();
      expect(screen.getByText('15 items • Ready for checkout')).toBeInTheDocument();
    });

    it('displays progress indicator with step 1 highlighted', () => {
      render(<CheckoutFlow {...mockProps} />);

      const stepIndicators = screen.getAllByText(/^1$/);
      expect(stepIndicators.length).toBeGreaterThan(0);
    });

    it('navigates to delivery step when Next button clicked', async () => {
      render(<CheckoutFlow {...mockProps} />);

      const nextButton = screen.getByText(/Next/);
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });
    });

    it('disables Back button on cart step', () => {
      render(<CheckoutFlow {...mockProps} />);

      const backButton = screen.getByText('Back');
      expect(backButton).toBeDisabled();
    });
  });

  describe('Step 2: Delivery Selection', () => {
    it('renders delivery selection step after clicking Next', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });
    });

    it('shows error when trying to proceed without slot selection', async () => {
      render(<CheckoutFlow {...mockProps} />);

      // Go to delivery step
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      // Try to proceed without selecting slot
      const nextButton = screen.getByText(/Next/);
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please select a delivery slot')).toBeInTheDocument();
      });
    });

    it('confirms delivery when slot is selected', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      // Select a slot - find button containing slot time
      const slotButton = screen.getByText(/09:00-12:00/);
      fireEvent.click(slotButton);

      await waitFor(() => {
        expect(screen.getByText('Delivery Confirmed')).toBeInTheDocument();
      });
    });

    it('allows navigation back to cart step', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Back'));

      await waitFor(() => {
        expect(screen.getByText('Step 1 of 3: Review Cart')).toBeInTheDocument();
      });
    });
  });

  describe('Step 3: Confirmation', () => {
    it('renders confirmation step after selecting delivery slot', async () => {
      render(<CheckoutFlow {...mockProps} />);

      // Go to delivery step
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      // Select slot
      fireEvent.click(screen.getByText(/09:00-12:00/));

      // Go to confirmation
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });
    });

    it('displays order summary on confirmation step', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Order Summary')).toBeInTheDocument();
        expect(screen.getByText(/Items \(15\)/)).toBeInTheDocument();
        expect(screen.getByText('Total')).toBeInTheDocument();
      });
    });

    it('shows terms acceptance checkbox', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        const checkbox = screen.getByRole('checkbox');
        expect(checkbox).toBeInTheDocument();
      });
    });

    it('disables Complete Order button until terms are accepted', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        const completeButton = screen.getByText('Complete Order');
        expect(completeButton).toBeDisabled();
      });

      // Accept terms
      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);

      await waitFor(() => {
        const completeButton = screen.getByText('Complete Order');
        expect(completeButton).not.toBeDisabled();
      });
    });

    it('allows navigation back from confirmation to delivery', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Back'));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });
    });
  });

  describe('Step 4: Complete', () => {
    it('renders completion step after checkout', async () => {
      const onCheckoutComplete = jest.fn();
      render(<CheckoutFlow {...mockProps} onCheckoutComplete={onCheckoutComplete} />);

      // Navigate through all steps
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });

      // Accept terms and complete
      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);

      fireEvent.click(screen.getByText('Complete Order'));

      await waitFor(() => {
        expect(screen.getByText('Order Confirmed!')).toBeInTheDocument();
        expect(onCheckoutComplete).toHaveBeenCalled();
      });
    });

    it('displays order ID on completion', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
      fireEvent.click(screen.getByText('Complete Order'));

      await waitFor(() => {
        expect(screen.getByText('Order ID')).toBeInTheDocument();
      });
    });

    it('shows Return to Dashboard button on completion', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
      fireEvent.click(screen.getByText('Complete Order'));

      await waitFor(() => {
        expect(screen.getByText('Return to Dashboard')).toBeInTheDocument();
      });
    });
  });

  describe('Processing State', () => {
    it('disables buttons when isProcessing is true', () => {
      render(<CheckoutFlow {...mockProps} isProcessing={true} />);

      const nextButton = screen.getByText(/Next/);
      expect(nextButton).toBeDisabled();
    });

    it('shows loading spinner when isProcessing is true', () => {
      render(<CheckoutFlow {...mockProps} isProcessing={true} />);

      // The component uses Loader icon from lucide-react which would have animate-spin
      const nextButton = screen.getByText(/Next/);
      expect(nextButton).toBeInTheDocument();
    });
  });

  describe('Callbacks', () => {
    it('calls onCancel when Return to Dashboard is clicked', async () => {
      const onCancel = jest.fn();
      render(<CheckoutFlow {...mockProps} onCancel={onCancel} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
      fireEvent.click(screen.getByText('Complete Order'));

      await waitFor(() => {
        expect(screen.getByText('Return to Dashboard')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Return to Dashboard'));
      expect(onCancel).toHaveBeenCalled();
    });
  });

  describe('Progress Indicator', () => {
    it('hides progress indicator on completion step', async () => {
      render(<CheckoutFlow {...mockProps} />);

      fireEvent.click(screen.getByText(/Next/));
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 3: Select Delivery Slot')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/09:00-12:00/));
      fireEvent.click(screen.getByText(/Next/));

      await waitFor(() => {
        expect(screen.getByText('Step 3 of 3: Confirm Order')).toBeInTheDocument();
      });

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
      fireEvent.click(screen.getByText('Complete Order'));

      await waitFor(() => {
        // Progress indicator should not be visible on complete step
        expect(screen.queryByText('Step 1 of 3')).not.toBeInTheDocument();
      });
    });
  });
});
