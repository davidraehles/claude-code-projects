'use client'

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/Card';
import { Sparkles } from 'lucide-react';

interface RecipeExplanationProps {
  recipeId: number;
  context?: string; // e.g., "meal_plan" or "search"
}

export function RecipeExplanation({ recipeId, context = 'meal_plan' }: RecipeExplanationProps) {
  const [explanation, setExplanation] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const handleExplain = async () => {
    setLoading(true);
    try {
      // Placeholder for API call
      // const res = await fetch(`/api/recipes/${recipeId}/explain?context=${context}`);
      // const data = await res.json();
      
      // Simulate response
      setTimeout(() => {
        setExplanation("This recipe was chosen because it matches your preference for Italian cuisine, uses seasonal ingredients (tomatoes, basil), and fits within your daily calorie target.");
        setLoading(false);
      }, 1500);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="mt-4">
      {!explanation ? (
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleExplain} 
          disabled={loading}
          className="gap-2 text-blue-600 border-blue-200 hover:bg-blue-50"
        >
          <Sparkles className="w-4 h-4" />
          {loading ? "Asking Chef..." : "Why this recipe?"}
        </Button>
      ) : (
        <Card className="bg-blue-50 border-blue-200 animate-in fade-in slide-in-from-top-2">
          <CardContent className="p-4 text-sm text-blue-800">
            <div className="flex items-start gap-2">
              <Sparkles className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-600" />
              <div>
                <p className="font-semibold mb-1 text-blue-900">Chef's Reasoning</p>
                <p>{explanation}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
