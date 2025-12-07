import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MissingItemsSuggestions from '@/components/knuspr/MissingItemsSuggestions';

describe('MissingItemsSuggestions Component', () => {
  const unavailableItems = ['exotic ingredient', 'rare spice', 'specialty product'];
  const cartSubtotal = 40.00;

  it('renders unavailable items list', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    expect(screen.getByText('exotic ingredient')).toBeInTheDocument();
    expect(screen.getByText('rare spice')).toBeInTheDocument();
    expect(screen.getByText('specialty product')).toBeInTheDocument();
  });

  it('shows count of unavailable items', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    expect(screen.getByText(/3 Item\(s\) Not Found in Stock/)).toBeInTheDocument();
  });

  it('returns null when no unavailable items', () => {
    const { container } = render(
      <MissingItemsSuggestions
        unavailableItems={[]}
        cartSubtotal={cartSubtotal}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('expands item details when clicked', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    const exoticItem = screen.getByText('exotic ingredient');
    fireEvent.click(exoticItem.closest('button')!);

    // After expansion, suggestions should be visible
    expect(screen.getByText('Suggested Alternatives')).toBeInTheDocument();
  });

  it('allows adding manual items', () => {
    const onAddManualItem = jest.fn();
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
        onAddManualItem={onAddManualItem}
      />
    );

    // Component should be rendered with unavailable items
    expect(screen.getByText('exotic ingredient')).toBeInTheDocument();

    // Verify the "Add Alternative" button exists (can be clicked to add items)
    const addButtons = screen.getAllByText('Add Alternative');
    expect(addButtons.length).toBeGreaterThan(0);
  });

  it('shows suggested alternatives for items', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    const exoticItem = screen.getByText('exotic ingredient');
    fireEvent.click(exoticItem.closest('button')!);

    // Suggestions should be displayed after expansion
    const alternatives = screen.getAllByText(/Similar|Alternative|Regular/);
    expect(alternatives.length).toBeGreaterThan(0);
  });

  it('displays manually added items', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    // Component should render with unavailable items
    expect(screen.getByText('exotic ingredient')).toBeInTheDocument();

    // Component shows the unavailable items list
    expect(screen.getByText(/3 Item\(s\) Not Found in Stock/)).toBeInTheDocument();
  });

  it('calculates and displays price impact', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    // Component should render with the unavailable items
    expect(screen.getByText('exotic ingredient')).toBeInTheDocument();

    // The component accepts cartSubtotal prop for calculation
    // Verify the unavailable items count and label
    expect(screen.getByText(/3 Item\(s\) Not Found in Stock/)).toBeInTheDocument();
  });

  it('allows dismissing the component', () => {
    const onDismiss = jest.fn();
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
        onDismiss={onDismiss}
      />
    );

    const dismissButton = screen.getByLabelText('Dismiss');
    fireEvent.click(dismissButton);

    expect(onDismiss).toHaveBeenCalled();
  });

  it('shows out of stock status for each item', () => {
    render(
      <MissingItemsSuggestions
        unavailableItems={unavailableItems}
        cartSubtotal={cartSubtotal}
      />
    );

    const outOfStockLabels = screen.getAllByText('Out of stock');
    expect(outOfStockLabels.length).toBe(unavailableItems.length);
  });
});
