import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CartPreview, { CartPreviewData } from '@/components/knuspr/CartPreview';

describe('CartPreview Component', () => {
  const mockCartData: CartPreviewData = {
    cart_id: 'test_cart_123',
    knuspr_url: 'https://www.knuspr.cz/cart/test_cart_123',
    total_price: 42.50,
    item_count: 12,
    delivery_slot: {
      slot_id: 'slot_001',
      date: '2025-11-24',
      time_window: '14:00-16:00',
      price: 4.99,
    },
    items_by_section: {
      dairy: [
        { name: 'Milk 1L', quantity: 1, unit: 'l', price: 2.50, available: true, category: 'dairy' },
        {
          name: 'Cheese 200g',
          quantity: 200,
          unit: 'g',
          price: 3.80,
          available: true,
          category: 'dairy',
        },
      ],
      produce: [
        {
          name: 'Carrots 500g',
          quantity: 500,
          unit: 'g',
          price: 1.50,
          available: true,
          category: 'produce',
        },
      ],
    },
    unavailable_items: ['exotic ingredient', 'rare spice'],
    created_at: '2025-11-22T15:30:00',
  };

  it('renders cart preview with correct data', () => {
    render(<CartPreview data={mockCartData} />);

    expect(screen.getByText('Your Shopping Cart')).toBeInTheDocument();
    expect(screen.getByText('12 items • Ready for checkout')).toBeInTheDocument();
    expect(screen.getByText('€42.50')).toBeInTheDocument();
  });

  it('displays items grouped by section', () => {
    render(<CartPreview data={mockCartData} />);

    expect(screen.getByText('dairy')).toBeInTheDocument();
    expect(screen.getByText('produce')).toBeInTheDocument();
    expect(screen.getByText('Milk 1L')).toBeInTheDocument();
    expect(screen.getByText('Carrots 500g')).toBeInTheDocument();
  });

  it('shows delivery slot information', () => {
    render(<CartPreview data={mockCartData} />);

    expect(screen.getByText('Delivery Scheduled')).toBeInTheDocument();
    expect(screen.getByText(/14:00-16:00/)).toBeInTheDocument();
    expect(screen.getByText(/€4.99/)).toBeInTheDocument();
  });

  it('displays unavailable items warning', () => {
    render(<CartPreview data={mockCartData} />);

    expect(screen.getByText('2 Item(s) Not Available')).toBeInTheDocument();
    expect(screen.getByText('exotic ingredient')).toBeInTheDocument();
    expect(screen.getByText('rare spice')).toBeInTheDocument();
  });

  it('shows price breakdown correctly', () => {
    render(<CartPreview data={mockCartData} />);

    expect(screen.getByText('Subtotal (12 items)')).toBeInTheDocument();
    expect(screen.getByText('Delivery Fee')).toBeInTheDocument();
    expect(screen.getByText('Total')).toBeInTheDocument();
  });

  it('calls onCheckout when button clicked', () => {
    const onCheckout = jest.fn();
    render(<CartPreview data={mockCartData} onCheckout={onCheckout} />);

    const checkoutButton = screen.getByText('Continue to Checkout');
    fireEvent.click(checkoutButton);

    expect(onCheckout).toHaveBeenCalled();
  });

  it('shows loading state when isLoading is true', () => {
    render(<CartPreview data={mockCartData} isLoading={true} />);

    expect(screen.getByText(/Generating your shopping cart/)).toBeInTheDocument();
  });

  it('shows error state with retry button', () => {
    const errorMessage = 'Failed to generate cart';
    render(<CartPreview data={mockCartData} error={errorMessage} />);

    expect(screen.getByText('Cart Generation Failed')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('displays cart ID for reference', () => {
    render(<CartPreview data={mockCartData} />);

    expect(screen.getByText('test_cart_123')).toBeInTheDocument();
  });

  it('handles cart without delivery slot', () => {
    const cartWithoutSlot = { ...mockCartData, delivery_slot: null };
    render(<CartPreview data={cartWithoutSlot} />);

    expect(screen.queryByText('Delivery Scheduled')).not.toBeInTheDocument();
  });

  it('handles empty unavailable items list', () => {
    const cartNoUnavailable = { ...mockCartData, unavailable_items: [] };
    render(<CartPreview data={cartNoUnavailable} />);

    expect(screen.queryByText(/Item\(s\) Not Available/)).not.toBeInTheDocument();
  });
});
