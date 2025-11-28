/**
 * Mobile navigation component with hamburger menu.
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'

interface MobileNavProps {
  userEmail?: string | null
}

export function MobileNav({ userEmail }: MobileNavProps) {
  const [isOpen, setIsOpen] = useState(false)

  const toggleMenu = () => setIsOpen(!isOpen)
  const closeMenu = () => setIsOpen(false)

  return (
    <>
      {/* Hamburger Button */}
      <button
        onClick={toggleMenu}
        className="md:hidden p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
        aria-label="Toggle menu"
      >
        {isOpen ? (
          // Close icon
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          // Hamburger icon
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        )}
      </button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={closeMenu}
        />
      )}

      {/* Mobile Menu Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-64 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out md:hidden ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-6">
          {/* Close button */}
          <button
            onClick={closeMenu}
            className="absolute top-4 right-4 p-2 text-gray-600 hover:text-gray-900"
            aria-label="Close menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          {/* User email */}
          {userEmail && (
            <div className="mb-6 pb-4 border-b border-gray-200">
              <p className="text-sm text-gray-600 flex items-center">
                <span className="mr-2">👤</span>
                {userEmail}
              </p>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="space-y-4">
            <Link
              href="/dashboard"
              onClick={closeMenu}
              className="block py-2 px-4 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Recipes
            </Link>
            <Link
              href="/meal-plans"
              onClick={closeMenu}
              className="block py-2 px-4 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Meal Plans
            </Link>
            <Link
              href="/generate"
              onClick={closeMenu}
              className="block"
            >
              <Button variant="primary" className="w-full">
                Generate Plan
              </Button>
            </Link>
          </nav>
        </div>
      </div>
    </>
  )
}
