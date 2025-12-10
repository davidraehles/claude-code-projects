import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Checkout } from '@/components/sections/checkout'

// Mock framer-motion if used
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<object>) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: React.PropsWithChildren<object>) => <span {...props}>{children}</span>,
  },
}))

describe('Checkout Component', () => {
  beforeEach(() => {
    render(<Checkout />)
  })

  describe('Knuspr Integration', () => {
    it('renders Knuspr as a delivery option', () => {
      expect(screen.getByText('Knuspr')).toBeInTheDocument()
    })

    it('shows "Integrated" badge for Knuspr', () => {
      expect(screen.getByText('Integrated')).toBeInTheDocument()
    })

    it('shows "One-click cart fill" text for Knuspr', () => {
      expect(screen.getByText('One-click cart fill')).toBeInTheDocument()
    })

    it('Knuspr appears before other delivery services', () => {
      const allServices = screen.getAllByText(/Knuspr|Instacart|Amazon Fresh|Walmart\+|DoorDash/)
      expect(allServices[0]).toHaveTextContent('Knuspr')
    })
  })

  describe('Other Delivery Services', () => {
    it('renders Instacart option', () => {
      expect(screen.getByText('Instacart')).toBeInTheDocument()
    })

    it('renders Amazon Fresh option', () => {
      expect(screen.getByText('Amazon Fresh')).toBeInTheDocument()
    })

    it('renders Walmart+ option', () => {
      expect(screen.getByText('Walmart+')).toBeInTheDocument()
    })

    it('renders DoorDash option', () => {
      expect(screen.getByText('DoorDash')).toBeInTheDocument()
    })

    it('other services do not show "Integrated" badge', () => {
      // There should be exactly one "Integrated" badge (for Knuspr)
      const integratedBadges = screen.getAllByText('Integrated')
      expect(integratedBadges).toHaveLength(1)
    })

    it('other services do not show "One-click cart fill"', () => {
      // There should be exactly one "One-click cart fill" text (for Knuspr)
      const cartFillTexts = screen.getAllByText('One-click cart fill')
      expect(cartFillTexts).toHaveLength(1)
    })
  })

  describe('Section Content', () => {
    it('renders the ORDER label', () => {
      expect(screen.getByText('ORDER')).toBeInTheDocument()
    })

    it('renders the main headline', () => {
      expect(screen.getByText('Straight to your cart.')).toBeInTheDocument()
    })

    it('renders the subtitle', () => {
      expect(screen.getByText('One tap to your favorite delivery app. Checkout in seconds.')).toBeInTheDocument()
    })

    it('renders "Choose Your Store" heading', () => {
      expect(screen.getByText('Choose Your Store')).toBeInTheDocument()
    })

    it('renders the cart mockup with items', () => {
      expect(screen.getByText('🛒 Your Cart')).toBeInTheDocument()
      expect(screen.getByText('23 items')).toBeInTheDocument()
    })
  })
})
