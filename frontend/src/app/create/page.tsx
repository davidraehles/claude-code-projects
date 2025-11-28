'use client'

/**
 * Recipe Creation Page - Create recipes manually
 * Allows users to add custom recipes to their library
 */

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateRecipe } from '@/hooks/queries/useRecipes'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

interface FormData {
  title: string
  ingredients: string[]
  instructions: string
  prepTime?: number
  cookTime?: number
  servings?: number
  dietaryTags?: string[]
}

export default function CreatePage() {
  const router = useRouter()
  const { user, isLoading: authLoading, token } = useAuth()
  const { mutate: createRecipe, isPending, error } = useCreateRecipe()

  const [formData, setFormData] = useState<FormData>({
    title: '',
    ingredients: [''],
    instructions: '',
    prepTime: undefined,
    cookTime: undefined,
    servings: 2,
    dietaryTags: [],
  })
  const [success, setSuccess] = useState(false)

  // Debug: Log auth state
  useEffect(() => {
    console.log('[CreatePage] Auth state:', { token: !!token, user: user?.email, authLoading })
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
    if (!formData.title.trim() || formData.ingredients.filter((i) => i.trim()).length === 0) {
      return
    }

    createRecipe(
      {
        title: formData.title,
        ingredients: formData.ingredients.filter((i) => i.trim()),
        instructions: formData.instructions,
        prep_time: formData.prepTime,
        cook_time: formData.cookTime,
        servings: formData.servings,
        dietary_tags: formData.dietaryTags?.filter((t) => t.trim()),
      },
      {
        onSuccess: () => {
          setSuccess(true)
          // Redirect to dashboard after 2 seconds
          setTimeout(() => {
            router.push('/dashboard')
          }, 2000)
        },
      }
    )
  }

  const handleAddIngredient = () => {
    setFormData({
      ...formData,
      ingredients: [...formData.ingredients, ''],
    })
  }

  const handleRemoveIngredient = (index: number) => {
    setFormData({
      ...formData,
      ingredients: formData.ingredients.filter((_, i) => i !== index),
    })
  }

  const handleIngredientChange = (index: number, value: string) => {
    const newIngredients = [...formData.ingredients]
    newIngredients[index] = value
    setFormData({
      ...formData,
      ingredients: newIngredients,
    })
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
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Create Recipe</h1>
          <p className="text-gray-600">
            Add a new recipe to your library. Fill in the details below and we'll calculate nutrition info automatically.
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <span className="text-2xl mr-3">✅</span>
              <div>
                <h3 className="text-green-900 font-semibold mb-1">Recipe created successfully!</h3>
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
                <h3 className="text-red-900 font-semibold mb-1">Failed to create recipe</h3>
                <p className="text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Recipe Form */}
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6 pt-6">
              {/* Title */}
              <div>
                <Input
                  label="Recipe Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., Chocolate Chip Cookies"
                  required
                  disabled={isPending}
                />
              </div>

              {/* Times */}
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Prep Time (minutes)"
                  type="number"
                  min="0"
                  value={formData.prepTime || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      prepTime: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  placeholder="15"
                  disabled={isPending}
                />
                <Input
                  label="Cook Time (minutes)"
                  type="number"
                  min="0"
                  value={formData.cookTime || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      cookTime: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  placeholder="30"
                  disabled={isPending}
                />
              </div>

              {/* Servings */}
              <Input
                label="Servings"
                type="number"
                min="1"
                value={formData.servings || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    servings: e.target.value ? parseInt(e.target.value) : 2,
                  })
                }
                placeholder="4"
                disabled={isPending}
              />

              {/* Ingredients */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Ingredients</label>
                <div className="space-y-2">
                  {formData.ingredients.map((ingredient, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={ingredient}
                        onChange={(e) => handleIngredientChange(index, e.target.value)}
                        placeholder="e.g., 2 cups flour"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        disabled={isPending}
                      />
                      {formData.ingredients.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveIngredient(index)}
                          className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50"
                          disabled={isPending}
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleAddIngredient}
                  className="mt-2 w-full"
                  disabled={isPending}
                >
                  + Add Ingredient
                </Button>
              </div>

              {/* Instructions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Instructions</label>
                <textarea
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  placeholder="Step-by-step instructions..."
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-sans"
                  disabled={isPending}
                />
              </div>

              {/* Dietary Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Dietary Tags (optional)</label>
                <div className="flex flex-wrap gap-2">
                  {['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo'].map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => {
                        const newTags = formData.dietaryTags || []
                        setFormData({
                          ...formData,
                          dietaryTags: newTags.includes(tag)
                            ? newTags.filter((t) => t !== tag)
                            : [...newTags, tag],
                        })
                      }}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        (formData.dietaryTags || []).includes(tag)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                      disabled={isPending}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                className="w-full"
                disabled={isPending || !formData.title.trim()}
              >
                {isPending ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Creating Recipe...
                  </span>
                ) : (
                  '✨ Create Recipe'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
