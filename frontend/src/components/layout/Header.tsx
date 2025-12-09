/**
 * Reusable header component for authenticated pages.
 */

'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { MobileNav } from './MobileNav'

interface HeaderProps {
  userEmail?: string | null
}

// Inline SVG logo for better iOS compatibility
function LogoIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      role="img"
      aria-label="Go, Cart! Logo"
    >
      <path d="M5 8h3l4 14h12l3-10H10" stroke="#E85A4F" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
      <circle cx="12" cy="26" r="2" fill="#E85A4F"/>
      <circle cx="22" cy="26" r="2" fill="#E85A4F"/>
      <circle cx="15" cy="16" r="2" fill="#7EC8A3"/>
      <circle cx="20" cy="15" r="1.5" fill="#7EC8A3" opacity="0.8"/>
    </svg>
  )
}

export function Header({ userEmail }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <Link href="/" className="flex items-center space-x-2" aria-label="Go, Cart! Home">
              <LogoIcon className="w-8 h-8 sm:w-10 sm:h-10" />
              <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-primary-500 to-orange-500 bg-clip-text text-transparent">
                Go, Cart!
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-4" aria-label="Main navigation">
            {userEmail && (
              <span className="text-sm text-gray-600" aria-label="Current user">
                <span role="img" aria-label="User icon">👤</span> {userEmail}
              </span>
            )}
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                Recipes
              </Button>
            </Link>
            <Link href="/meal-plans">
              <Button variant="ghost" size="sm">
                Meal Plans
              </Button>
            </Link>
            <Link href="/grocery-carts">
              <Button variant="ghost" size="sm">
                <span role="img" aria-label="Shopping cart">🛒</span> Grocery Lists
              </Button>
            </Link>
            <Link href="/generate">
              <Button variant="primary" size="sm">
                Generate Plan
              </Button>
            </Link>
          </nav>

          {/* Mobile Navigation */}
          <MobileNav userEmail={userEmail} />
        </div>
      </div>
    </header>
  )
}
