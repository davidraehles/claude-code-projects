'use client'

/**
 * Recipe Import Page - Import recipes from URLs
 * Supports: HTML (Ottolenghi, BBC), API (Spoonacular), RSS feeds
 */

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useImportRecipe } from '@/hooks/queries/useRecipes'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

const SUPPORTED_SOURCES = [
  { type: 'html', label: 'Website (HTML)', description: 'Ottolenghi, BBC Good Food, etc.' },
  { type: 'api', label: 'API (JSON)', description: 'Spoonacular, Edamam, etc.' },
  { type: 'rss', label: 'RSS Feed', description: 'Blog feeds, news, etc.' },
]

export default function ImportPage() {
  const router = useRouter()
  const { user, isLoading: authLoading, token } = useAuth()
  const { mutate: importRecipe, isPending, error } = useImportRecipe()

  const [url, setUrl] = useState('')
  const [sourceType, setSourceType] = useState<'html' | 'api' | 'rss'>('html')
  const [success, setSuccess] = useState(false)

  // Debug: Log auth state
  useEffect(() => {
    console.log('[ImportPage] Auth state:', { token: !!token, user: user?.email, authLoading })
  }, [token, user, authLoading])

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    importRecipe(
      { url: url.trim(), source_type: sourceType },
      {
        onSuccess: () => {
          setSuccess(true)
          setUrl('')
          // Redirect to dashboard after 2 seconds
          setTimeout(() => {
            router.push('/dashboard')
          }, 2000)
        },
      }
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header userEmail={user?.email || null} />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Page Header */}
        <div className="mb-8">
          <Link href="/dashboard" className="text-blue-600 hover:text-blue-700 mb-4 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Import Recipe</h1>
          <p className="text-gray-600">
            Paste a recipe URL from any cooking website. We'll automatically extract ingredients, instructions, and nutrition info.
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <span className="text-2xl mr-3">✅</span>
              <div>
                <h3 className="text-green-900 font-semibold mb-1">Recipe imported successfully!</h3>
                <p className="text-green-700">Redirecting to dashboard...</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <span className="text-2xl mr-3">❌</span>
              <div>
                <h3 className="text-red-900 font-semibold mb-1">Failed to import recipe</h3>
                <p className="text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Import Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Recipe URL</CardTitle>
            <CardDescription>Enter the URL of the recipe you want to import</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* URL Input */}
              <div>
                <Input
                  label="Recipe URL"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.ottolenghi.co.uk/recipes/..."
                  required
                  disabled={isPending}
                />
                <p className="text-sm text-gray-500 mt-2">
                  Example: https://www.bbcgoodfood.com/recipes/chocolate-cake
                </p>
              </div>

              {/* Source Type Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Source Type</label>
                <div className="space-y-2">
                  {SUPPORTED_SOURCES.map((source) => (
                    <label key={source.type} className="flex items-start p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors">
                      <input
                        type="radio"
                        name="sourceType"
                        value={source.type}
                        checked={sourceType === source.type}
                        onChange={(e) => setSourceType(e.target.value as 'html' | 'api' | 'rss')}
                        disabled={isPending}
                        className="mt-1 mr-3"
                      />
                      <div>
                        <p className="font-medium text-gray-900">{source.label}</p>
                        <p className="text-sm text-gray-600">{source.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                className="w-full"
                disabled={isPending || !url.trim()}
              >
                {isPending ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Importing...
                  </span>
                ) : (
                  '🔗 Import Recipe'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Tips Section */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Tips for Best Results</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✅ Use direct recipe URLs (not homepage URLs)</li>
              <li>✅ Supported sites: Ottolenghi, BBC Good Food, AllRecipes, Food Network, etc.</li>
              <li>✅ The recipe should have ingredients and instructions</li>
              <li>⚠️ Some websites may block automated access - try another recipe if it fails</li>
              <li>💡 If importing fails, you can manually create the recipe instead</li>
            </ul>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
