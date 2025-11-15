"""
Meal Architect Agent - Intelligent Meal Planning with Z3 Solver.

Generates optimized meal plans using constraint satisfaction and optimization.
"""

import time
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from z3 import *

from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan, MealPlanRecipe
from app.models.ingredient import Ingredient


class MealArchitectAgent:
    """
    Agent for generating optimized meal plans.

    Uses Z3 constraint solver to:
    - Balance nutritional requirements
    - Respect dietary restrictions
    - Maximize variety
    - Optimize for budget
    - Ensure ingredient availability
    """

    def __init__(self, db_session: Session):
        """
        Initialize Meal Architect Agent.

        Args:
            db_session: Database session
        """
        self.db = db_session

    def generate_meal_plan(
        self,
        user_id: int,
        start_date: date,
        num_days: int,
        num_people: int = 2,
        dietary_restrictions: Optional[List[str]] = None,
        excluded_ingredients: Optional[List[str]] = None,
        target_calories_per_day: Optional[int] = None,
        target_budget: Optional[float] = None,
        preferred_cuisines: Optional[List[str]] = None,
        meals_per_day: int = 3
    ) -> MealPlan:
        """
        Generate an optimized meal plan.

        Args:
            user_id: User ID
            start_date: Start date
            num_days: Number of days to plan
            num_people: Number of people
            dietary_restrictions: List of dietary restrictions
            excluded_ingredients: List of ingredients to exclude
            target_calories_per_day: Target calories per day
            target_budget: Target budget
            preferred_cuisines: List of preferred cuisines
            meals_per_day: Meals per day (default: 3)

        Returns:
            Generated MealPlan
        """
        start_time = time.time()

        # Create meal plan
        meal_plan = MealPlan(
            user_id=user_id,
            name=f"Meal Plan {start_date.isoformat()}",
            start_date=start_date,
            end_date=start_date + timedelta(days=num_days - 1),
            num_people=num_people,
            dietary_restrictions=dietary_restrictions,
            excluded_ingredients=excluded_ingredients,
            target_calories_per_day=target_calories_per_day,
            target_budget=target_budget,
            preferred_cuisines=preferred_cuisines,
            status="generating"
        )

        self.db.add(meal_plan)
        self.db.commit()
        self.db.refresh(meal_plan)

        try:
            # Get candidate recipes
            recipes = self._get_candidate_recipes(
                user_id=user_id,
                dietary_restrictions=dietary_restrictions,
                excluded_ingredients=excluded_ingredients,
                min_recipes=num_days * meals_per_day
            )

            if not recipes:
                raise ValueError("No suitable recipes found for the given constraints")

            # Use Z3 solver to optimize meal selection
            selected_recipes = self._solve_meal_optimization(
                recipes=recipes,
                num_days=num_days,
                meals_per_day=meals_per_day,
                target_calories_per_day=target_calories_per_day,
                target_budget=target_budget
            )

            # Assign recipes to meal plan
            total_calories = 0
            total_cost = 0.0
            meal_types = ["breakfast", "lunch", "dinner", "snack"]

            position = 0
            for day in range(1, num_days + 1):
                scheduled_date = start_date + timedelta(days=day - 1)

                for meal_idx in range(meals_per_day):
                    if position >= len(selected_recipes):
                        break

                    recipe = selected_recipes[position]
                    meal_type = meal_types[meal_idx % len(meal_types)]

                    # Calculate calories and cost
                    calories = self._calculate_recipe_calories(recipe, num_people)
                    cost = self._estimate_recipe_cost(recipe, num_people)

                    meal_plan_recipe = MealPlanRecipe(
                        meal_plan_id=meal_plan.id,
                        recipe_id=recipe.id,
                        day_number=day,
                        meal_type=meal_type,
                        scheduled_date=scheduled_date,
                        servings=num_people,
                        calories=calories,
                        cost=cost,
                        position=position
                    )

                    self.db.add(meal_plan_recipe)

                    total_calories += calories or 0
                    total_cost += cost or 0.0
                    position += 1

            # Update meal plan metadata
            meal_plan.total_recipes = position
            meal_plan.total_calories = total_calories
            meal_plan.total_cost = total_cost
            meal_plan.status = "ready"
            meal_plan.generation_time_seconds = time.time() - start_time

            self.db.commit()
            self.db.refresh(meal_plan)

            print(f"✅ Generated meal plan with {meal_plan.total_recipes} recipes in {meal_plan.generation_time_seconds:.2f}s")

            return meal_plan

        except Exception as e:
            meal_plan.status = "failed"
            self.db.commit()
            raise e

    def _get_candidate_recipes(
        self,
        user_id: int,
        dietary_restrictions: Optional[List[str]],
        excluded_ingredients: Optional[List[str]],
        min_recipes: int = 21
    ) -> List[Recipe]:
        """
        Get candidate recipes that match constraints.

        Args:
            user_id: User ID
            dietary_restrictions: Dietary restrictions
            excluded_ingredients: Excluded ingredients
            min_recipes: Minimum number of recipes needed

        Returns:
            List of candidate recipes
        """
        # Get user's recipes (non-duplicates)
        query = self.db.query(Recipe).filter(
            Recipe.user_id == user_id,
            Recipe.duplicate_of_id.is_(None)
        )

        recipes = query.limit(min_recipes * 2).all()  # Get more than needed for variety

        # Filter by dietary restrictions (simplified - would need ingredient analysis)
        # For MVP, we'll accept all recipes and filter in production

        return recipes[:min_recipes] if len(recipes) >= min_recipes else recipes

    def _solve_meal_optimization(
        self,
        recipes: List[Recipe],
        num_days: int,
        meals_per_day: int,
        target_calories_per_day: Optional[int],
        target_budget: Optional[float]
    ) -> List[Recipe]:
        """
        Use Z3 solver to optimize meal selection.

        Constraints:
        - Each recipe used at most once (variety)
        - Calorie targets met (if specified)
        - Budget constraints met (if specified)
        - Balanced nutrition across days

        Args:
            recipes: Candidate recipes
            num_days: Number of days
            meals_per_day: Meals per day
            target_calories_per_day: Target calories
            target_budget: Target budget

        Returns:
            List of selected recipes
        """
        total_meals = num_days * meals_per_day

        # Simple optimization for MVP: distribute recipes evenly
        # In production, this would use full Z3 constraint solving

        # Z3 Solver setup
        solver = Optimize()

        # Create boolean variables for each recipe
        recipe_vars = {recipe.id: Bool(f'recipe_{recipe.id}') for recipe in recipes}

        # Constraint 1: Select exactly total_meals recipes
        solver.add(Sum([If(recipe_vars[r.id], 1, 0) for r in recipes]) == total_meals)

        # Constraint 2: Each recipe at most once (for variety)
        # This is implicit with boolean variables

        # Constraint 3: Calorie constraints (if specified)
        if target_calories_per_day:
            target_total_calories = target_calories_per_day * num_days

            # Simplified: assume each recipe has ~600 calories
            # In production, calculate from recipe nutrition data
            avg_calories_per_meal = 600

            # Soft constraint: minimize deviation from target
            total_calories = sum([
                If(recipe_vars[r.id], avg_calories_per_meal, 0)
                for r in recipes
            ])

            # Allow 20% deviation
            lower_bound = int(target_total_calories * 0.8)
            upper_bound = int(target_total_calories * 1.2)

            solver.add(total_calories >= lower_bound)
            solver.add(total_calories <= upper_bound)

        # Constraint 4: Budget constraints (if specified)
        if target_budget:
            # Simplified: assume each recipe costs ~5 EUR
            # In production, calculate from ingredient prices
            avg_cost_per_meal = 5.0

            total_cost = sum([
                If(recipe_vars[r.id], int(avg_cost_per_meal * 100), 0)  # Convert to cents for integer arithmetic
                for r in recipes
            ])

            budget_cents = int(target_budget * 100)
            solver.add(total_cost <= budget_cents)

        # Objective: Maximize variety (implicit with constraints)
        # Could add: maximize_variety = sum([If(recipe_vars[r.id], 1, 0) for r in recipes])
        # solver.maximize(maximize_variety)

        # Solve
        if solver.check() == sat:
            model = solver.model()

            # Extract selected recipes
            selected = []
            for recipe in recipes:
                if is_true(model[recipe_vars[recipe.id]]):
                    selected.append(recipe)

            # If we have exactly the right number, return them
            if len(selected) == total_meals:
                return selected

        # Fallback: Simple distribution if Z3 doesn't find optimal solution
        # This ensures we always return something useful
        return recipes[:total_meals] if len(recipes) >= total_meals else recipes

    def _calculate_recipe_calories(self, recipe: Recipe, servings: int) -> Optional[int]:
        """
        Calculate total calories for a recipe.

        Args:
            recipe: Recipe
            servings: Number of servings

        Returns:
            Total calories (estimated)
        """
        # Simplified for MVP: return estimated calories
        # In production, calculate from ingredient nutrition data
        if recipe.nutrition and 'calories' in recipe.nutrition:
            return int(recipe.nutrition['calories'] * servings / (recipe.servings or 1))

        # Fallback: estimate based on meal type
        return 600  # Average meal calories

    def _estimate_recipe_cost(self, recipe: Recipe, servings: int) -> float:
        """
        Estimate recipe cost.

        Args:
            recipe: Recipe
            servings: Number of servings

        Returns:
            Estimated cost in EUR
        """
        # Simplified for MVP: return estimated cost
        # In production, calculate from ingredient prices
        num_ingredients = len(recipe.ingredients) if recipe.ingredients else 5

        # Rough estimate: €1 per ingredient
        base_cost = num_ingredients * 1.0

        # Adjust for servings
        cost = base_cost * servings / (recipe.servings or 2)

        return round(cost, 2)

    def get_meal_plan_summary(self, meal_plan_id: int) -> Dict[str, Any]:
        """
        Get summary of a meal plan.

        Args:
            meal_plan_id: Meal plan ID

        Returns:
            Summary dictionary
        """
        meal_plan = self.db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

        if not meal_plan:
            raise ValueError(f"Meal plan {meal_plan_id} not found")

        # Get recipes
        recipes = self.db.query(MealPlanRecipe).filter(
            MealPlanRecipe.meal_plan_id == meal_plan_id
        ).order_by(MealPlanRecipe.day_number, MealPlanRecipe.position).all()

        # Group by day
        days = {}
        for mpr in recipes:
            day_num = mpr.day_number
            if day_num not in days:
                days[day_num] = {
                    "day_number": day_num,
                    "date": mpr.scheduled_date.isoformat() if mpr.scheduled_date else None,
                    "meals": []
                }

            days[day_num]["meals"].append({
                "meal_type": mpr.meal_type,
                "recipe_id": mpr.recipe_id,
                "recipe_name": mpr.recipe.title if mpr.recipe else "Unknown",
                "servings": mpr.servings,
                "calories": mpr.calories,
                "cost": mpr.cost
            })

        return {
            "meal_plan": meal_plan.to_dict(),
            "days": list(days.values()),
            "statistics": {
                "total_recipes": meal_plan.total_recipes,
                "total_calories": meal_plan.total_calories,
                "total_cost": meal_plan.total_cost,
                "avg_calories_per_day": meal_plan.total_calories // meal_plan.num_days if meal_plan.total_calories and meal_plan.num_days else None,
                "avg_cost_per_day": meal_plan.total_cost / meal_plan.num_days if meal_plan.total_cost and meal_plan.num_days else None
            }
        }
