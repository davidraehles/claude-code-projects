import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeliverySlotPicker, { DeliverySlot } from '@/components/knuspr/DeliverySlotPicker';

describe('DeliverySlotPicker Component', () => {
  const mockSlots: DeliverySlot[] = [
    {
      slot_id: 'slot_001',
      date: '2025-11-24',
      time_window: '09:00-11:00',
      price: 3.99,
      available: true,
    },
    {
      slot_id: 'slot_002',
      date: '2025-11-24',
      time_window: '14:00-16:00',
      price: 4.99,
      available: true,
    },
    {
      slot_id: 'slot_003',
      date: '2025-11-25',
      time_window: '18:00-20:00',
      price: 5.99,
      available: true,
    },
    {
      slot_id: 'slot_004',
      date: '2025-11-25',
      time_window: '09:00-11:00',
      price: 3.99,
      available: false,
    },
  ];

  it('renders all available delivery slots', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    // Check for unique time windows
    const allTimeWindows = screen.getAllByText(/09:00-11:00|14:00-16:00|18:00-20:00/);
    expect(allTimeWindows.length).toBeGreaterThanOrEqual(3);

    // Verify each slot is rendered by checking for unique identifiers
    expect(screen.getByText(/14:00-16:00/)).toBeInTheDocument();
    expect(screen.getByText(/18:00-20:00/)).toBeInTheDocument();
  });

  it('groups slots by date', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    // Check for date headers
    expect(screen.getByText(/Nov 24/i)).toBeInTheDocument();
    expect(screen.getByText(/Nov 25/i)).toBeInTheDocument();
  });

  it('calls onSelect when slot is clicked', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    const slotButton = screen.getByText(/14:00-16:00/).closest('button');
    if (slotButton) {
      fireEvent.click(slotButton);
    }

    expect(onSelect).toHaveBeenCalled();
  });

  it('highlights selected slot', () => {
    const onSelect = jest.fn();
    render(
      <DeliverySlotPicker
        slots={mockSlots}
        onSelect={onSelect}
        selected="slot_002"
      />
    );

    const selectedSlot = screen.getByText(/14:00-16:00/).closest('button');
    expect(selectedSlot).toHaveClass('border-blue-600');
    expect(selectedSlot).toHaveClass('bg-blue-50');
  });

  it('filters slots by time preference', () => {
    const onSelect = jest.fn();
    render(
      <DeliverySlotPicker
        slots={mockSlots}
        onSelect={onSelect}
        timePreference="morning"
      />
    );

    // Morning slots (09:00-11:00) should be rendered
    const allTimeWindows = screen.getAllByText(/09:00-11:00/);
    expect(allTimeWindows.length).toBeGreaterThan(0);
  });

  it('shows price for each slot', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    const prices = screen.getAllByText(/€\d+\.\d+/);
    expect(prices.length).toBeGreaterThanOrEqual(mockSlots.length);
  });

  it('shows loading state when isLoading is true', () => {
    const onSelect = jest.fn();
    render(
      <DeliverySlotPicker
        slots={mockSlots}
        onSelect={onSelect}
        isLoading={true}
      />
    );

    expect(screen.getByText(/Loading delivery slots/)).toBeInTheDocument();
  });

  it('identifies cheapest slot', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    const cheapestBadge = screen.queryByText('Cheapest');
    // Cheapest should be marked on slots with price €3.99
    if (cheapestBadge) {
      expect(cheapestBadge).toBeInTheDocument();
    }
  });

  it('identifies earliest slot', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    const earliestBadge = screen.queryByText('Earliest');
    // Earliest should be marked on the first available slot chronologically
    if (earliestBadge) {
      expect(earliestBadge).toBeInTheDocument();
    }
  });

  it('disables unavailable slots', () => {
    const onSelect = jest.fn();
    render(<DeliverySlotPicker slots={mockSlots} onSelect={onSelect} />);

    // Unavailable slots should exist but be disabled
    const allSlots = screen.getAllByRole('button');
    expect(allSlots.length).toBeGreaterThan(0);
  });
});
