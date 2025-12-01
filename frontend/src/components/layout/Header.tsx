/**
 * Reusable header component for authenticated pages.
 */

'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/Button'
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
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-2xl sm:text-3xl">🍽️</span>
              <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                MealPlannerAI
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            {userEmail && (
              <span className="text-sm text-gray-600">
                👤 {userEmail}
              </span>
            )}
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                Recipes
              </Button>
            </Link>
              <Link href="/meal-plans" prefetch={false}>
              <Button variant="ghost" size="sm">
                Meal Plans
              </Button>
            </Link>
            <Link href="/generate">
              <Button variant="primary" size="sm">
                Generate Plan
              </Button>
            </Link>
          </div>

          {/* Mobile Navigation */}
          <MobileNav userEmail={userEmail} />
        </div>
      </div>
    </header>
  )
}
