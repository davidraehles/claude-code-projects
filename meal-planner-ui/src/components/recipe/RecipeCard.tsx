/**
 * Recipe card component for displaying recipes in grid/list views.
 */

import React from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import type { Recipe } from '@/lib/types'

interface RecipeCardProps {
  recipe: Recipe
  onClick?: () => void
}

export function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  const { title, ingredients, dietary_tags, nutrition, servings } = recipe

  return (
    <Card
      hover
      className="cursor-pointer h-full flex flex-col"
      onClick={onClick}
    >
      <CardHeader>
        <CardTitle className="line-clamp-2">{title}</CardTitle>
        <CardDescription className="text-sm">
          {servings} serving{servings !== 1 ? 's' : ''}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col justify-between">
        {/* Ingredients preview */}
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Ingredients:</p>
          <ul className="text-sm text-gray-600 space-y-1">
            {ingredients.slice(0, 3).map((ingredient, idx) => (
              <li key={idx} className="line-clamp-1">
                • {ingredient}
              </li>
            ))}
            {ingredients.length > 3 && (
              <li className="text-gray-500 italic">
                +{ingredients.length - 3} more...
              </li>
            )}
          </ul>
        </div>

        {/* Tags and nutrition */}
        <div className="space-y-3">
          {/* Dietary tags */}
          {dietary_tags && dietary_tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {dietary_tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Nutrition info */}
          {nutrition && (
            <div className="grid grid-cols-3 gap-2 text-xs text-gray-600 border-t pt-3">
              <div className="text-center">
                <div className="font-semibold text-gray-900">{Math.round(nutrition.calories || 0)}</div>
                <div className="text-gray-500">cal</div>
              </div>
              <div className="text-center border-l border-r">
                <div className="font-semibold text-gray-900">{Math.round(nutrition.protein || 0)}g</div>
                <div className="text-gray-500">protein</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-gray-900">{Math.round(nutrition.carbs || 0)}g</div>
                <div className="text-gray-500">carbs</div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
