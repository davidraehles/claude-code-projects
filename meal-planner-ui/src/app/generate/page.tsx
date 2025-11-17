'use client'

/**
 * Meal Plan Generator page - Create personalized meal plans.
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import { initTestAuth, restoreAuth, getCurrentUserEmail } from '@/lib/auth'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Checkbox } from '@/components/ui/Checkbox'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

const COMMON_DIETARY_RESTRICTIONS = [
  'vegetarian',
  'vegan',
  'gluten-free',
  'dairy-free',
  'keto',
  'paleo',
  'low-carb',
  'low-fat',
  'nut-free',
  'pescatarian',
]

export default function GeneratePage() {
  const router = useRouter()
  const [authLoading, setAuthLoading] = useState(true)
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [startDate, setStartDate] = useState('')
  const [numDays, setNumDays] = useState(7)
  const [numPeople, setNumPeople] = useState(2)
  const [mealsPerDay, setMealsPerDay] = useState(3)
  const [selectedRestrictions, setSelectedRestrictions] = useState<string[]>([])
  const [excludedIngredients, setExcludedIngredients] = useState('')

  // Initialize authentication
  useEffect(() => {
    async function authenticate() {
      try {
        const restored = restoreAuth()
        if (!restored) {
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

  // Set default start date to tomorrow
  useEffect(() => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    setStartDate(tomorrow.toISOString().split('T')[0])
  }, [])

  // Toggle dietary restriction
  const toggleRestriction = (restriction: string) => {
    setSelectedRestrictions((prev) =>
      prev.includes(restriction)
        ? prev.filter((r) => r !== restriction)
        : [...prev, restriction]
    )
  }

  // Handle form submission
  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setGenerating(true)

    try {
      // Parse excluded ingredients
      const excludedList = excludedIngredients
        .split(',')
        .map((item) => item.trim())
        .filter((item) => item.length > 0)

      // Create meal plan request
      const mealPlan = await api.createMealPlan({
        start_date: startDate,
        num_days: numDays,
        num_people: numPeople,
        meals_per_day: mealsPerDay,
        dietary_restrictions: selectedRestrictions.length > 0 ? selectedRestrictions : undefined,
        excluded_ingredients: excludedList.length > 0 ? excludedList : undefined,
      })

      console.log('✅ Meal plan created:', mealPlan)

      // Redirect to meal plan view
      router.push(`/meal-plans/${mealPlan.id}`)
    } catch (err: any) {
      console.error('Failed to generate meal plan:', err)
      setError(err.message || 'Failed to generate meal plan. Please try again.')
      setGenerating(false)
    }
  }

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
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Link href="/" className="flex items-center space-x-2">
                <span className="text-3xl">🍽️</span>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  MealPlannerAI
                </span>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              {userEmail && (
                <span className="text-sm text-gray-600">👤 {userEmail}</span>
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
              <Link href="/generate">
                <Button variant="primary" size="sm">
                  Generate Plan
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Page Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Generate Meal Plan
          </h1>
          <p className="text-gray-600">
            Create a personalized weekly meal plan based on your preferences
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="text-red-900 font-semibold mb-1">
                  Failed to generate meal plan
                </h3>
                <p className="text-red-700">{error}</p>
                <p className="text-sm text-red-600 mt-2">
                  Make sure the backend API is running and you have recipes in your library.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Generation Form */}
        <form onSubmit={handleGenerate}>
          <div className="space-y-6">
            {/* Basic Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Settings</CardTitle>
                <CardDescription>
                  Configure your meal plan duration and household size
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <Input
                    label="Start Date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                    min={new Date().toISOString().split('T')[0]}
                  />
                  <Input
                    label="Number of Days"
                    type="number"
                    value={numDays}
                    onChange={(e) => setNumDays(parseInt(e.target.value))}
                    required
                    min={1}
                    max={14}
                  />
                  <Input
                    label="Number of People"
                    type="number"
                    value={numPeople}
                    onChange={(e) => setNumPeople(parseInt(e.target.value))}
                    required
                    min={1}
                    max={10}
                  />
                  <Input
                    label="Meals per Day"
                    type="number"
                    value={mealsPerDay}
                    onChange={(e) => setMealsPerDay(parseInt(e.target.value))}
                    required
                    min={1}
                    max={5}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Dietary Restrictions */}
            <Card>
              <CardHeader>
                <CardTitle>Dietary Restrictions</CardTitle>
                <CardDescription>
                  Select any dietary requirements or preferences (optional)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {COMMON_DIETARY_RESTRICTIONS.map((restriction) => (
                    <Checkbox
                      key={restriction}
                      label={restriction.charAt(0).toUpperCase() + restriction.slice(1)}
                      checked={selectedRestrictions.includes(restriction)}
                      onChange={() => toggleRestriction(restriction)}
                      disabled={generating}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Excluded Ingredients */}
            <Card>
              <CardHeader>
                <CardTitle>Excluded Ingredients</CardTitle>
                <CardDescription>
                  List any ingredients you want to avoid (comma-separated, optional)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Input
                  placeholder="e.g., mushrooms, cilantro, bell peppers"
                  value={excludedIngredients}
                  onChange={(e) => setExcludedIngredients(e.target.value)}
                  disabled={generating}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Separate multiple ingredients with commas
                </p>
              </CardContent>
            </Card>

            {/* Summary & Generate */}
            <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm mb-6">
                  <p>
                    <span className="font-semibold">📅 Duration:</span>{' '}
                    {numDays} day{numDays !== 1 ? 's' : ''} starting {new Date(startDate).toLocaleDateString()}
                  </p>
                  <p>
                    <span className="font-semibold">👥 Household:</span>{' '}
                    {numPeople} person{numPeople !== 1 ? 's' : ''},{' '}
                    {mealsPerDay} meal{mealsPerDay !== 1 ? 's' : ''} per day
                  </p>
                  <p>
                    <span className="font-semibold">🎯 Total Meals:</span>{' '}
                    {numDays * mealsPerDay} meals
                  </p>
                  {selectedRestrictions.length > 0 && (
                    <p>
                      <span className="font-semibold">🥗 Dietary:</span>{' '}
                      {selectedRestrictions.join(', ')}
                    </p>
                  )}
                  {excludedIngredients && (
                    <p>
                      <span className="font-semibold">🚫 Excluding:</span>{' '}
                      {excludedIngredients}
                    </p>
                  )}
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full"
                  disabled={generating}
                >
                  {generating ? (
                    <span className="flex items-center justify-center">
                      <svg
                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
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
                      Generating Your Meal Plan...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <span className="mr-2">✨</span>
                      Generate Meal Plan
                    </span>
                  )}
                </Button>

                {generating && (
                  <p className="text-xs text-gray-600 text-center mt-3">
                    This may take 10-30 seconds depending on your preferences...
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="mr-2">💡</span>
            How it works
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>
              • Our AI analyzes your recipe library and preferences
            </li>
            <li>
              • Recipes are selected to maximize variety and nutrition balance
            </li>
            <li>
              • All dietary restrictions and excluded ingredients are respected
            </li>
            <li>
              • You can adjust or regenerate your plan at any time
            </li>
          </ul>
        </div>
      </main>
    </div>
  )
}
