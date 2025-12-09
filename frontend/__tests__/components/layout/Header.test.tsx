import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Header } from '@/components/layout/Header'

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: React.ImgHTMLAttributes<HTMLImageElement> & { priority?: boolean }) => {
    const { priority, ...rest } = props
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...rest} data-priority={priority ? 'true' : 'false'} />
  },
}))

// Mock next/link
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))

// Mock MobileNav
jest.mock('@/components/layout/MobileNav', () => ({
  MobileNav: () => <div data-testid="mobile-nav">Mobile Nav</div>,
}))

describe('Header Component', () => {
  it('renders the logo SVG image', () => {
    render(<Header />)

    const logo = screen.getByAltText('Go, Cart! Logo')
    expect(logo).toBeInTheDocument()
    expect(logo).toHaveAttribute('src', '/logo-icon.svg')
  })

  it('renders the Go, Cart! brand name', () => {
    render(<Header />)

    expect(screen.getByText('Go, Cart!')).toBeInTheDocument()
  })

  it('renders the home link with correct href', () => {
    render(<Header />)

    // The link text includes both the logo alt text and the brand name
    const homeLink = screen.getByRole('link', { name: /Go, Cart! Logo.*Go, Cart!/i })
    expect(homeLink).toHaveAttribute('href', '/')
  })

  it('displays user email when provided', () => {
    render(<Header userEmail="test@example.com" />)

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })

  it('does not display user email section when not provided', () => {
    render(<Header />)

    expect(screen.queryByText('@')).not.toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<Header />)

    expect(screen.getByRole('link', { name: /recipes/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /meal plans/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /grocery lists/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /generate plan/i })).toBeInTheDocument()
  })

  it('logo has priority loading attribute', () => {
    render(<Header />)

    const logo = screen.getByAltText('Go, Cart! Logo')
    expect(logo).toHaveAttribute('data-priority', 'true')
  })
})
