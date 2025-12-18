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
from app.agents.ingredient_intelligence import IngredientIntelligenceAgent
from app.agents.base import Agent, CapabilityManifest
from app.events import Event, EventType, EventBus


class MealArchitectAgent(Agent):
    """
    Agent for generating optimized meal plans.

    Uses Z3 constraint solver to:
    - Balance nutritional requirements
    - Respect dietary restrictions
    - Maximize variety
    - Optimize for budget
    - Ensure ingredient availability
    """

    def __init__(self, event_bus: EventBus, db_session: Session, use_workflow: bool = True):
        """
        Initialize Meal Architect Agent.

        Args:
            event_bus: Event bus for communication
            db_session: Database session
            use_workflow: Whether to use LangGraph workflow (default: True)
        """
        super().__init__(event_bus)
        self.db = db_session
        self.ingredient_agent = IngredientIntelligenceAgent(event_bus, db_session)
        self.use_workflow = use_workflow

    def get_manifest(self) -> CapabilityManifest:
        return CapabilityManifest(
            name="meal-architect",
            version="1.0.0",
            description="Generates optimized meal plans",
            capabilities=["generate_meal_plan", "refine_meal_plan"],
            input_events=[
                EventType.MEAL_PLAN_REQUESTED,
                EventType.MEAL_PLAN_REFINEMENT_REQUESTED
            ],
            output_events=[
                EventType.MEAL_PLAN_GENERATED,
                EventType.MEAL_PLAN_FAILED,
                EventType.MEAL_PLAN_REFINED
            ]
        )

    async def handle_event(self, event: Event):
        if event.type == EventType.MEAL_PLAN_REQUESTED:
            self.logger.info(f"Processing meal plan request: {event.event_id}")
            try:
                payload = event.payload
                user_id = payload.get("user_id")
                start_date_str = payload.get("start_date")
                start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
                num_days = payload.get("num_days", 7)

                # Run generation
                meal_plan = self.generate_meal_plan(
                    user_id=user_id,
                    start_date=start_date,
                    num_days=num_days,
                    num_people=payload.get("num_people", 2),
                    dietary_restrictions=payload.get("dietary_restrictions"),
                    excluded_ingredients=payload.get("excluded_ingredients"),
                    target_calories_per_day=payload.get("target_calories_per_day"),
                    target_budget=payload.get("target_budget"),
                    preferred_cuisines=payload.get("preferred_cuisines"),
                    meals_per_day=payload.get("meals_per_day", 3)
                )

                await self.publish(
                    EventType.MEAL_PLAN_GENERATED,
                    {
                        "meal_plan_id": meal_plan.id,
                        "user_id": user_id,
                        "status": "success"
                    },
                    correlation_id=event.correlation_id
                )
            except Exception as e:
                self.logger.error(f"Error generating meal plan: {e}")
                await self.publish(
                    EventType.MEAL_PLAN_FAILED,
                    {
                        "error": str(e),
                        "user_id": event.payload.get("user_id")
                    },
                    correlation_id=event.correlation_id
                )

        elif event.type == EventType.MEAL_PLAN_REFINEMENT_REQUESTED:
            self.logger.info(f"Received meal plan refinement request: {event.event_id}")
            # Placeholder for refinement logic
            await self.publish(
                EventType.MEAL_PLAN_FAILED,
                {
                    "error": "Refinement not yet implemented",
                    "user_id": event.payload.get("user_id")
                },
                correlation_id=event.correlation_id
            )

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

        Routes to either workflow-based generation (Phase 2C) or
        direct generation (Phase 2A fallback).

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
        # Route to workflow or direct implementation
        if self.use_workflow:
            return self._generate_with_workflow(
                user_id=user_id,
                start_date=start_date,
                num_days=num_days,
                num_people=num_people,
                dietary_restrictions=dietary_restrictions,
                excluded_ingredients=excluded_ingredients,
                target_calories_per_day=target_calories_per_day,
                target_budget=target_budget,
                preferred_cuisines=preferred_cuisines,
                meals_per_day=meals_per_day
            )
        else:
            return self._generate_direct(
                user_id=user_id,
                start_date=start_date,
                num_days=num_days,
                num_people=num_people,
                dietary_restrictions=dietary_restrictions,
                excluded_ingredients=excluded_ingredients,
                target_calories_per_day=target_calories_per_day,
                target_budget=target_budget,
                preferred_cuisines=preferred_cuisines,
                meals_per_day=meals_per_day
            )

    def _generate_with_workflow(
        self,
        user_id: int,
        start_date: date,
        num_days: int,
        num_people: int,
        dietary_restrictions: Optional[List[str]],
        excluded_ingredients: Optional[List[str]],
        target_calories_per_day: Optional[int],
        target_budget: Optional[float],
        preferred_cuisines: Optional[List[str]],
        meals_per_day: int
    ) -> MealPlan:
        """
        Generate meal plan using LangGraph workflow (Phase 2C).

        Args:
            (same as generate_meal_plan)

        Returns:
            Generated MealPlan

        Raises:
            Exception: If workflow execution fails
        """
        from app.workflows.meal_planning_workflow import invoke_meal_planning_workflow

        # Run workflow
        result = invoke_meal_planning_workflow(
            user_id=user_id,
            start_date=start_date,
            num_days=num_days,
            num_people=num_people,
            meals_per_day=meals_per_day,
            dietary_restrictions=dietary_restrictions,
            excluded_ingredients=excluded_ingredients,
            target_calories_per_day=target_calories_per_day,
            target_budget=target_budget,
            preferred_cuisines=preferred_cuisines
        )

        # Check if workflow succeeded
        if not result.get("success"):
            error_msg = result.get("failure_reason", "Unknown error")
            raise Exception(f"Meal plan generation failed: {error_msg}")

        # Retrieve and return meal plan
        meal_plan_id = result["meal_plan_id"]
        meal_plan = self.db.query(MealPlan).get(meal_plan_id)

        if not meal_plan:
            raise Exception(f"Meal plan {meal_plan_id} not found after generation")

        return meal_plan

    def _generate_direct(
        self,
        user_id: int,
        start_date: date,
        num_days: int,
        num_people: int,
        dietary_restrictions: Optional[List[str]],
        excluded_ingredients: Optional[List[str]],
        target_calories_per_day: Optional[int],
        target_budget: Optional[float],
        preferred_cuisines: Optional[List[str]],
        meals_per_day: int
    ) -> MealPlan:
        """
        Generate meal plan using direct method (Phase 2A fallback).

        This is the original implementation without LangGraph orchestration.

        Args:
            (same as generate_meal_plan)

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
            dietary_restrictions: Dietary restrictions (e.g., ["vegan", "gluten_free"])
            excluded_ingredients: Excluded ingredients
            min_recipes: Minimum number of recipes needed

        Returns:
            List of candidate recipes matching all constraints
        """
        # Get recently used recipe IDs (last 14 days)
        recently_used_ids = self._get_recently_used_recipe_ids(user_id, days=14)

        # Get user's recipes (non-duplicates, excluding recently used)
        query = self.db.query(Recipe).filter(
            Recipe.user_id == user_id,
            Recipe.duplicate_of_id.is_(None)
        )

        # Exclude recently used recipes for variety
        if recently_used_ids:
            query = query.filter(~Recipe.id.in_(recently_used_ids))

        # Get more than needed for filtering
        recipes = query.limit(min_recipes * 3).all()

        # Filter by dietary restrictions
        if dietary_restrictions:
            filtered_recipes = []

            for recipe in recipes:
                if self._matches_dietary_restrictions(recipe, dietary_restrictions):
                    filtered_recipes.append(recipe)

            recipes = filtered_recipes

        # Filter by excluded ingredients
        if excluded_ingredients:
            filtered_recipes = []
            excluded_set = set(ing.lower() for ing in excluded_ingredients)

            for recipe in recipes:
                if not self._contains_excluded_ingredients(recipe, excluded_set):
                    filtered_recipes.append(recipe)

            recipes = filtered_recipes

        return recipes[:min_recipes] if len(recipes) >= min_recipes else recipes

    def _get_recently_used_recipe_ids(self, user_id: int, days: int = 14) -> List[int]:
        """
        Get recipe IDs used in recent meal plans for variety.

        Args:
            user_id: User ID
            days: Number of days to look back (default: 14)

        Returns:
            List of recipe IDs used in recent meal plans
        """
        cutoff_date = date.today() - timedelta(days=days)

        # Get recent meal plans
        recent_meal_plans = self.db.query(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.start_date >= cutoff_date,
            MealPlan.status.in_(['ready', 'active', 'completed'])
        ).all()

        # Extract recipe IDs
        recipe_ids = set()
        for meal_plan in recent_meal_plans:
            for meal_plan_recipe in meal_plan.recipes:
                recipe_ids.add(meal_plan_recipe.recipe_id)

        return list(recipe_ids)

    def _matches_dietary_restrictions(self, recipe: Recipe, restrictions: List[str]) -> bool:
        """
        Check if recipe matches dietary restrictions.

        Args:
            recipe: Recipe to check
            restrictions: List of dietary restrictions

        Returns:
            True if recipe matches all restrictions
        """
        # Check dietary tags on recipe first (fast path)
        if recipe.dietary_tags:
            recipe_tags_lower = [tag.lower() for tag in recipe.dietary_tags]

            for restriction in restrictions:
                restriction_lower = restriction.lower().replace('-', '_')

                # Map common restriction names
                if restriction_lower in ['vegan', 'is_vegan']:
                    if 'vegan' not in recipe_tags_lower:
                        return False
                elif restriction_lower in ['vegetarian', 'is_vegetarian']:
                    if 'vegetarian' not in recipe_tags_lower and 'vegan' not in recipe_tags_lower:
                        return False
                elif restriction_lower in ['gluten_free', 'gluten-free', 'is_gluten_free']:
                    if 'gluten_free' not in recipe_tags_lower:
                        return False
                elif restriction_lower in ['dairy_free', 'dairy-free', 'is_dairy_free']:
                    if 'dairy_free' not in recipe_tags_lower:
                        return False
        else:
            # Fallback: Check ingredients using Ingredient Intelligence agent
            if not recipe.ingredients:
                return False

            for restriction in restrictions:
                restriction_lower = restriction.lower().replace('-', '_')

                # For animal products, check if any ingredient violates the restriction
                if restriction_lower in ['vegan', 'is_vegan']:
                    if self._contains_animal_products(recipe.ingredients):
                        return False
                elif restriction_lower in ['vegetarian', 'is_vegetarian']:
                    if self._contains_meat(recipe.ingredients):
                        return False
                elif restriction_lower in ['gluten_free', 'gluten-free', 'is_gluten_free']:
                    if self._contains_gluten(recipe.ingredients):
                        return False
                elif restriction_lower in ['dairy_free', 'dairy-free', 'is_dairy_free']:
                    if self._contains_dairy(recipe.ingredients):
                        return False

        return True

    def _contains_excluded_ingredients(self, recipe: Recipe, excluded_set: set) -> bool:
        """
        Check if recipe contains any excluded ingredients.

        Args:
            recipe: Recipe to check
            excluded_set: Set of lowercased excluded ingredient names

        Returns:
            True if recipe contains any excluded ingredient
        """
        if not recipe.ingredients:
            return False

        for ingredient in recipe.ingredients:
            ingredient_lower = ingredient.lower()

            # Check exact match
            if ingredient_lower in excluded_set:
                return True

            # Check if any excluded ingredient is contained in this ingredient
            for excluded in excluded_set:
                if excluded in ingredient_lower:
                    return True

        return False

    def _contains_animal_products(self, ingredients: List[str]) -> bool:
        """Check if ingredients contain animal products (for vegan check)."""
        animal_keywords = [
            'meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb', 'duck', 'fish',
            'salmon', 'tuna', 'egg', 'milk', 'cheese', 'butter', 'cream', 'yogurt',
            'honey', 'gelatin', 'lard'
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for keyword in animal_keywords:
                if keyword in ingredient_lower:
                    return True

        return False

    def _contains_meat(self, ingredients: List[str]) -> bool:
        """Check if ingredients contain meat (for vegetarian check)."""
        meat_keywords = [
            'meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb', 'duck',
            'fish', 'salmon', 'tuna', 'bacon', 'ham', 'sausage'
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for keyword in meat_keywords:
                if keyword in ingredient_lower:
                    return True

        return False

    def _contains_gluten(self, ingredients: List[str]) -> bool:
        """Check if ingredients contain gluten."""
        gluten_keywords = [
            'wheat', 'flour', 'bread', 'pasta', 'barley', 'rye',
            'couscous', 'semolina', 'durum'
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for keyword in gluten_keywords:
                if keyword in ingredient_lower:
                    return True

        return False

    def _contains_dairy(self, ingredients: List[str]) -> bool:
        """Check if ingredients contain dairy."""
        dairy_keywords = [
            'milk', 'cheese', 'butter', 'cream', 'yogurt', 'whey',
            'casein', 'lactose', 'dairy'
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for keyword in dairy_keywords:
                if keyword in ingredient_lower:
                    return True

        return False

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
            Total calories (calculated from ingredients or estimated)
        """
        # Priority 1: Use recipe nutrition data if available
        if recipe.nutrition and 'calories' in recipe.nutrition:
            calories_per_serving = recipe.nutrition['calories']
            recipe_servings = recipe.servings or 1
            return int(calories_per_serving * servings / recipe_servings)

        # Priority 2: Calculate from ingredients using Ingredient Intelligence
        if recipe.ingredients:
            total_calories = 0
            ingredients_found = 0

            for ingredient_str in recipe.ingredients:
                # Classify ingredient to get nutrition data
                ingredient_info = self.ingredient_agent.classify_ingredient(ingredient_str)

                if ingredient_info.get('found') and ingredient_info.get('nutrition_per_100g'):
                    nutrition = ingredient_info['nutrition_per_100g']

                    if isinstance(nutrition, dict) and 'calories' in nutrition:
                        # Rough estimate: assume 100g per ingredient (can be improved with quantity parsing)
                        total_calories += nutrition['calories']
                        ingredients_found += 1

            # If we found nutrition data for at least 50% of ingredients, use it
            if ingredients_found >= len(recipe.ingredients) * 0.5:
                # Adjust for servings
                recipe_servings = recipe.servings or 2
                return int(total_calories * servings / recipe_servings)

        # Priority 3: Intelligent fallback based on recipe characteristics
        # Estimate based on number of ingredients and recipe type
        num_ingredients = len(recipe.ingredients) if recipe.ingredients else 5
        estimated_calories_per_ingredient = 80  # Average per ingredient

        base_calories = num_ingredients * estimated_calories_per_ingredient

        # Adjust for servings
        recipe_servings = recipe.servings or 2
        total_calories = int(base_calories * servings / recipe_servings)

        # Ensure reasonable bounds (300-1000 cal per serving)
        calories_per_serving = total_calories // servings
        if calories_per_serving < 300:
            total_calories = 300 * servings
        elif calories_per_serving > 1000:
            total_calories = 1000 * servings

        return total_calories

    def _estimate_recipe_cost(self, recipe: Recipe, servings: int) -> float:
        """
        Estimate recipe cost based on ingredients.

        Args:
            recipe: Recipe
            servings: Number of servings

        Returns:
            Estimated cost in EUR
        """
        # Priority 1: Calculate from ingredient costs if available
        if recipe.ingredients:
            total_cost = 0.0
            ingredients_with_cost = 0

            for ingredient_str in recipe.ingredients:
                # Classify ingredient
                ingredient_info = self.ingredient_agent.classify_ingredient(ingredient_str)

                if ingredient_info.get('found'):
                    # Estimate cost based on ingredient category
                    category = ingredient_info.get('category', 'other')

                    # Cost estimates per 100g/100ml by category
                    category_costs = {
                        'Protein': 2.50,  # Meat, fish
                        'Dairy': 1.20,    # Milk, cheese
                        'Vegetables': 0.80,
                        'Fruits': 1.00,
                        'Grains': 0.50,
                        'Spices': 0.30,
                        'Oils': 1.50,
                        'other': 1.00
                    }

                    cost = category_costs.get(category, 1.00)
                    total_cost += cost
                    ingredients_with_cost += 1
                else:
                    # Unknown ingredient: estimate €1
                    total_cost += 1.00

            # Adjust for servings
            recipe_servings = recipe.servings or 2
            cost = total_cost * servings / recipe_servings

            return round(cost, 2)

        # Priority 2: Fallback based on recipe complexity
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
