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

export function Header({ userEmail }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <Link href="/" className="flex items-center space-x-2" aria-label="Go, Cart! Home">
              <span className="text-2xl sm:text-3xl" role="img" aria-label="Food icon">🍽️</span>
              <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
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
