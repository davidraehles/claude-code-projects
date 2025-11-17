'use client'

/**
 * Dashboard page - Recipe library with search and import.
 */

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { initTestAuth, restoreAuth, getCurrentUserEmail } from '@/lib/auth'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { RecipeCard } from '@/components/recipe/RecipeCard'
import type { Recipe } from '@/lib/types'

export default function DashboardPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [authLoading, setAuthLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Initialize authentication on component mount
  useEffect(() => {
    async function authenticate() {
      try {
        // Try to restore existing auth
        const restored = restoreAuth()

        if (!restored) {
          // No existing auth, initialize test user
          console.log('No existing auth, logging in with test user...')
          await initTestAuth()
        }

        setUserEmail(getCurrentUserEmail())
        setAuthLoading(false)
      } catch (err) {
        console.error('Authentication failed:', err)
        setError('Failed to authenticate. Please refresh the page.')
        setAuthLoading(false)
      }
    }

    authenticate()
  }, [])

  // Load recipes after authentication
  useEffect(() => {
    if (authLoading) return

    async function loadRecipes() {
      try {
        setLoading(true)
        const response = await api.getRecipes(1, 50)
        setRecipes(response.items)
        setFilteredRecipes(response.items)
        setError(null)
      } catch (err: any) {
        console.error('Failed to load recipes:', err)
        setError(err.message || 'Failed to load recipes')
      } finally {
        setLoading(false)
      }
    }

    loadRecipes()
  }, [authLoading])

  // Filter recipes based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredRecipes(recipes)
      return
    }

    const query = searchQuery.toLowerCase()
    const filtered = recipes.filter((recipe) => {
      return (
        recipe.title.toLowerCase().includes(query) ||
        recipe.ingredients.some((ing) => ing.toLowerCase().includes(query)) ||
        recipe.dietary_tags?.some((tag) => tag.toLowerCase().includes(query))
      )
    })

    setFilteredRecipes(filtered)
  }, [searchQuery, recipes])

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Authenticating...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header userEmail={userEmail} />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Recipe Library</h1>
          <p className="text-sm sm:text-base text-gray-600">
            Browse your recipes or import new ones to start meal planning
          </p>
        </div>

        {/* Search and Actions Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search recipes, ingredients, or dietary tags..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                }
              />
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <Link href="/import" className="w-full sm:w-auto">
                <Button variant="outline" className="w-full sm:w-auto">
                  <span className="mr-2">🔗</span>
                  <span className="hidden sm:inline">Import from URL</span>
                  <span className="sm:hidden">Import</span>
                </Button>
              </Link>
              <Link href="/create" className="w-full sm:w-auto">
                <Button variant="primary" className="w-full sm:w-auto">
                  <span className="mr-2">➕</span>
                  <span className="hidden sm:inline">Create Recipe</span>
                  <span className="sm:hidden">Create</span>
                </Button>
              </Link>
            </div>
          </div>

          {/* Results count */}
          <div className="mt-4 text-sm text-gray-600">
            Showing {filteredRecipes.length} of {recipes.length} recipes
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="text-red-900 font-semibold mb-1">Error loading recipes</h3>
                <p className="text-red-700">{error}</p>
                <p className="text-sm text-red-600 mt-2">
                  Make sure the backend API is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-80 animate-pulse"
              >
                <div className="h-6 bg-gray-200 rounded mb-4 w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded mb-6 w-1/2"></div>
                <div className="space-y-3">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredRecipes.length === 0 && recipes.length === 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">🍽️</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No recipes yet</h3>
            <p className="text-gray-600 mb-6">
              Get started by importing recipes from your favorite cooking websites or creating your own.
            </p>
            <div className="flex gap-3 justify-center">
              <Link href="/import">
                <Button variant="outline">Import from URL</Button>
              </Link>
              <Link href="/create">
                <Button variant="primary">Create Recipe</Button>
              </Link>
            </div>
          </div>
        )}

        {/* No Search Results */}
        {!loading && !error && filteredRecipes.length === 0 && recipes.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No recipes found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your search terms or browse all recipes.
            </p>
            <Button variant="outline" onClick={() => setSearchQuery('')}>
              Clear Search
            </Button>
          </div>
        )}

        {/* Recipe Grid */}
        {!loading && filteredRecipes.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRecipes.map((recipe) => (
              <RecipeCard
                key={recipe.id}
                recipe={recipe}
                onClick={() => {
                  // TODO: Open recipe detail modal/page
                  console.log('View recipe:', recipe.id)
                }}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
