'use client'

/**
 * Recipe Creation Page - Create recipes manually with MVI pattern (ARCH-004)
 * Refactored to use reducer for form state management.
 * Allows users to add custom recipes to their library
 */

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateRecipe } from '@/hooks/queries/useRecipes'
import { useReducerWithDevTools } from '@/hooks/useReducerWithDevTools'
import {
  createRecipeFormReducer,
  getInitialCreateRecipeFormState,
  selectIsTitleValid,
  selectHasValidIngredients,
  selectCanSubmit,
  selectCreateRecipeRequest,
  selectTotalTime,
  selectHasDietaryTag,
  selectIngredientCount,
} from '@/reducers/createRecipeFormReducer'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'

const DIETARY_TAG_OPTIONS = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo']

export default function CreatePage() {
  const router = useRouter()
  const { user, isLoading: authLoading, token } = useAuth()
  const { mutate: createRecipe, isPending, error } = useCreateRecipe()

  // Form state with reducer and DevTools (ARCH-004 + ARCH-011)
  const [formState, dispatch] = useReducerWithDevTools(
    createRecipeFormReducer,
    getInitialCreateRecipeFormState(),
    'CreateRecipeForm'
  )

  // Debug: Log auth state
  useEffect(() => {
    console.log('[CreatePage] Auth state:', { token: !!token, user: user?.email, authLoading })
  }, [token, user, authLoading])

  // Redirect after successful creation
  useEffect(() => {
    if (formState.success) {
      const timer = setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [formState.success, router])

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
    if (!selectCanSubmit(formState)) return

    const requestData = selectCreateRecipeRequest(formState)

    createRecipe(requestData, {
      onSuccess: () => {
        dispatch({ type: 'RECIPE_CREATED_SUCCESSFULLY' })
      },
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
            Add a new recipe to your library. Fill in the details below and we&apos;ll calculate nutrition info automatically.
          </p>
        </div>

        {/* Success Message */}
        {formState.success && (
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
                  value={formState.title}
                  onChange={(e) => dispatch({ type: 'USER_CHANGED_TITLE', payload: e.target.value })}
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
                  value={formState.prepTime || ''}
                  onChange={(e) =>
                    dispatch({
                      type: 'USER_CHANGED_PREP_TIME',
                      payload: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  placeholder="15"
                  disabled={isPending}
                />
                <Input
                  label="Cook Time (minutes)"
                  type="number"
                  min="0"
                  value={formState.cookTime || ''}
                  onChange={(e) =>
                    dispatch({
                      type: 'USER_CHANGED_COOK_TIME',
                      payload: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  placeholder="30"
                  disabled={isPending}
                />
              </div>

              {/* Total Time Display */}
              {selectTotalTime(formState) !== undefined && (
                <div className="text-sm text-gray-600">
                  Total Time: <strong>{selectTotalTime(formState)} minutes</strong>
                </div>
              )}

              {/* Servings */}
              <Input
                label="Servings"
                type="number"
                min="1"
                value={formState.servings || ''}
                onChange={(e) =>
                  dispatch({
                    type: 'USER_CHANGED_SERVINGS',
                    payload: e.target.value ? parseInt(e.target.value) : 2,
                  })
                }
                placeholder="4"
                disabled={isPending}
              />

              {/* Ingredients */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Ingredients</label>
                <div className="space-y-2">
                  {formState.ingredients.map((ingredient, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={ingredient}
                        onChange={(e) =>
                          dispatch({
                            type: 'USER_CHANGED_INGREDIENT',
                            payload: { index, value: e.target.value },
                          })
                        }
                        placeholder="e.g., 2 cups flour"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        disabled={isPending}
                      />
                      {selectIngredientCount(formState) > 1 && (
                        <button
                          type="button"
                          onClick={() =>
                            dispatch({ type: 'USER_REMOVED_INGREDIENT', payload: { index } })
                          }
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
                  variant="secondary"
                  onClick={() => dispatch({ type: 'USER_ADDED_INGREDIENT' })}
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
                  value={formState.instructions}
                  onChange={(e) =>
                    dispatch({ type: 'USER_CHANGED_INSTRUCTIONS', payload: e.target.value })
                  }
                  placeholder="Step-by-step instructions..."
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-sans"
                  disabled={isPending}
                />
              </div>

              {/* Dietary Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Dietary Tags (optional)
                </label>
                <div className="flex flex-wrap gap-2">
                  {DIETARY_TAG_OPTIONS.map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => dispatch({ type: 'USER_TOGGLED_DIETARY_TAG', payload: tag })}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        selectHasDietaryTag(formState, tag)
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
                disabled={isPending || !selectCanSubmit(formState)}
              >
                {isPending ? (
                  <span className="flex items-center justify-center">
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
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
