/**
 * Unit tests for UnmatchedItemsAlert component
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { UnmatchedItemsAlert } from '@/components/grocery/UnmatchedItemsAlert'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('UnmatchedItemsAlert', () => {
  const mockItems = ['Exotic Spice', 'Rare Herb', 'Specialty Product']
  const cartId = 123

  beforeEach(() => {
    localStorageMock.clear()
  })

  it('renders the alert with correct item count', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    expect(screen.getByText('3 Items Could Not Be Matched')).toBeInTheDocument()
  })

  it('renders alert with accessibility attributes', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    const alert = screen.getByRole('alert')
    expect(alert).toHaveAttribute('aria-live', 'polite')
    expect(alert).toHaveAttribute('aria-atomic', 'true')
  })

  it('displays all unmatched items when expanded', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    mockItems.forEach((item) => {
      expect(screen.getByText(item)).toBeInTheDocument()
    })
  })

  it('toggles expansion when clicking expand/collapse button', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    // Initially expanded, items should be visible
    expect(screen.getByText('Hide Items')).toBeInTheDocument()
    expect(screen.getByText(mockItems[0])).toBeInTheDocument()

    // Click to collapse
    const collapseButton = screen.getByText('Hide Items')
    fireEvent.click(collapseButton)

    // Items should be hidden
    expect(screen.getByText(`Show Items (${mockItems.length})`)).toBeInTheDocument()
    expect(screen.queryByText(mockItems[0])).not.toBeInTheDocument()

    // Click to expand again
    const expandButton = screen.getByText(`Show Items (${mockItems.length})`)
    fireEvent.click(expandButton)

    // Items should be visible again
    expect(screen.getByText('Hide Items')).toBeInTheDocument()
    expect(screen.getByText(mockItems[0])).toBeInTheDocument()
  })

  it('dismisses individual items', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    // All items should be visible initially
    expect(screen.getByText(mockItems[0])).toBeInTheDocument()

    // Find and click the dismiss button for the first item
    const dismissButtons = screen.getAllByLabelText(/Mark .* as handled/)
    fireEvent.click(dismissButtons[0])

    // First item should be removed
    expect(screen.queryByText(mockItems[0])).not.toBeInTheDocument()

    // Other items should still be visible
    expect(screen.getByText(mockItems[1])).toBeInTheDocument()
    expect(screen.getByText(mockItems[2])).toBeInTheDocument()
  })

  it('dismisses the entire alert', () => {
    const { container } = render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    // Alert should be visible initially
    expect(screen.getByText('3 Items Could Not Be Matched')).toBeInTheDocument()

    // Click the dismiss alert button
    const dismissButton = screen.getByLabelText('Dismiss this alert')
    fireEvent.click(dismissButton)

    // Alert should be hidden
    expect(container.firstChild).toBeNull()
  })

  it('persists dismissed items in localStorage', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    // Dismiss the first item
    const dismissButtons = screen.getAllByLabelText(/Mark .* as handled/)
    fireEvent.click(dismissButtons[0])

    // Check localStorage
    const stored = JSON.parse(localStorageMock.getItem(`unmatched-items-dismissed-${cartId}`) || '[]')
    expect(stored).toContain(mockItems[0])
  })

  it('loads dismissed items from localStorage on mount', () => {
    // Set up localStorage with a dismissed item
    localStorageMock.setItem(
      `unmatched-items-dismissed-${cartId}`,
      JSON.stringify([mockItems[0]])
    )

    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    // First item should not be visible
    expect(screen.queryByText(mockItems[0])).not.toBeInTheDocument()

    // Other items should be visible
    expect(screen.getByText(mockItems[1])).toBeInTheDocument()
    expect(screen.getByText(mockItems[2])).toBeInTheDocument()

    // Count should reflect visible items only
    expect(screen.getByText('2 Items Could Not Be Matched')).toBeInTheDocument()
  })

  it('renders search links for each item', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    mockItems.forEach((item) => {
      const searchLink = screen.getByLabelText(`Search for ${item} in Knuspr`)
      expect(searchLink).toHaveAttribute(
        'href',
        `https://www.knuspr.cz/search?q=${encodeURIComponent(item)}`
      )
      expect(searchLink).toHaveAttribute('target', '_blank')
      expect(searchLink).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  it('does not render when there are no items', () => {
    const { container } = render(<UnmatchedItemsAlert items={[]} cartId={cartId} />)

    expect(container.firstChild).toBeNull()
  })

  it('handles singular item count correctly', () => {
    render(<UnmatchedItemsAlert items={['Single Item']} cartId={cartId} />)

    expect(screen.getByText('1 Item Could Not Be Matched')).toBeInTheDocument()
  })

  it('shows correct message in the suggestions footer', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    expect(
      screen.getByText(/Click the search button to find alternatives in Knuspr/)
    ).toBeInTheDocument()
  })

  it('includes a link to browse Knuspr', () => {
    render(<UnmatchedItemsAlert items={mockItems} cartId={cartId} />)

    const browseLink = screen.getByText('Browse Knuspr')
    expect(browseLink.closest('a')).toHaveAttribute('href', 'https://www.knuspr.cz')
    expect(browseLink.closest('a')).toHaveAttribute('target', '_blank')
  })
})
