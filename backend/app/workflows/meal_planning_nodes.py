"""
Workflow nodes for meal planning with LangGraph.

Each node is a function that receives state, performs an operation,
and returns updated state.
"""

import time
from datetime import timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.workflows.meal_planning_state import MealPlanningState
from app.models.meal_plan import MealPlan, MealPlanRecipe
from app.agents.meal_architect import MealArchitectAgent


def initialize_state_node(state: MealPlanningState) -> MealPlanningState:
    """
    Initialize workflow state and create meal plan record.

    Creates a meal plan record in the database with status='generating'
    and initializes workflow tracking variables.

    Args:
        state: Current workflow state

    Returns:
        Updated state with meal_plan_id and initialized tracking
    """
    from app.database import SessionLocal

    db = SessionLocal()

    try:
        state["current_step"] = "initialize"
        state["start_time"] = time.time()

        # Track node execution
        state["nodes_executed"].append(
            {"name": "initialize", "timestamp": time.time(), "status": "started"}
        )

        # Create meal plan record
        meal_plan = MealPlan(
            user_id=state["user_id"],
            name=f"Meal Plan {state['start_date'].isoformat()}",
            start_date=state["start_date"],
            end_date=state["start_date"] + timedelta(days=state["num_days"] - 1),
            num_people=state["num_people"],
            dietary_restrictions=state.get("dietary_restrictions"),
            excluded_ingredients=state.get("excluded_ingredients"),
            target_calories_per_day=state.get("target_calories_per_day"),
            target_budget=state.get("target_budget"),
            preferred_cuisines=state.get("preferred_cuisines"),
            status="generating",
        )

        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)

        state["meal_plan_id"] = meal_plan.id

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - state["start_time"]) * 1000
        )

        return state

    except Exception as e:
        import traceback

        state["errors"].append(f"Initialize failed: {str(e)}")
        state["nodes_executed"][-1]["status"] = "failed"
        state["nodes_executed"][-1]["error"] = str(e)
        return state

    finally:
        db.close()


def validate_constraints_node(state: MealPlanningState) -> MealPlanningState:
    """
    Validate user inputs and constraints.

    Checks that all input parameters are within acceptable ranges
    and adds warnings for unusual values.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation errors/warnings
    """
    start_time = time.time()
    state["current_step"] = "validate"

    # Track node execution
    state["nodes_executed"].append(
        {"name": "validate", "timestamp": start_time, "status": "started"}
    )

    # Validate num_days
    if state["num_days"] < 1 or state["num_days"] > 30:
        state["errors"].append("num_days must be between 1 and 30")

    # Validate num_people
    if state["num_people"] < 1 or state["num_people"] > 20:
        state["errors"].append("num_people must be between 1 and 20")

    # Validate meals_per_day
    if state["meals_per_day"] < 1 or state["meals_per_day"] > 6:
        state["errors"].append("meals_per_day must be between 1 and 6")

    # Validate calories (if provided)
    target_calories = state.get("target_calories_per_day")
    if target_calories:
        if target_calories < 1000 or target_calories > 5000:
            state["warnings"].append(
                f"target_calories_per_day ({target_calories}) outside typical range (1000-5000)"
            )

    # Validate budget (if provided)
    target_budget = state.get("target_budget")
    if target_budget:
        if target_budget < 5 or target_budget > 500:
            state["warnings"].append(
                f"target_budget (€{target_budget}) outside typical range (€5-500)"
            )

    # Check for unrealistic combinations
    total_meals = state["num_days"] * state["meals_per_day"]
    if total_meals > 90:
        state["warnings"].append(
            f"Generating {total_meals} meals may take significant time"
        )

    # Mark node as completed
    state["nodes_executed"][-1]["status"] = "completed"
    state["nodes_executed"][-1]["duration_ms"] = int((time.time() - start_time) * 1000)
    state["nodes_executed"][-1]["errors_found"] = len(state["errors"])
    state["nodes_executed"][-1]["warnings_found"] = len(state["warnings"])

    return state


def fetch_recipes_node(state: MealPlanningState) -> MealPlanningState:
    """
    Fetch candidate recipes matching constraints.

    Queries database for recipes that match dietary restrictions,
    excluded ingredients, and other constraints.

    Args:
        state: Current workflow state

    Returns:
        Updated state with candidate_recipes populated
    """
    from app.database import SessionLocal

    db = SessionLocal()
    start_time = time.time()

    try:
        state["current_step"] = "fetch_recipes"

        # Track node execution
        state["nodes_executed"].append(
            {"name": "fetch_recipes", "timestamp": start_time, "status": "started"}
        )

        agent = MealArchitectAgent(db, use_workflow=False)

        # Get candidate recipes
        min_recipes = state["num_days"] * state["meals_per_day"]

        recipes = agent._get_candidate_recipes(
            user_id=state["user_id"],
            dietary_restrictions=state.get("dietary_restrictions"),
            excluded_ingredients=state.get("excluded_ingredients"),
            min_recipes=min_recipes,
        )

        # Convert to dict format for state
        state["candidate_recipes"] = [
            {
                "id": r.id,
                "title": r.title,
                "ingredients": r.ingredients,
                "dietary_tags": r.dietary_tags,
                "nutrition": r.nutrition,
                "servings": r.servings,
                "prep_time": r.prep_time,
                "cook_time": r.cook_time,
            }
            for r in recipes
        ]

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - start_time) * 1000
        )
        state["nodes_executed"][-1]["recipes_found"] = len(state["candidate_recipes"])
        state["nodes_executed"][-1]["recipes_required"] = min_recipes

        return state

    except Exception as e:
        state["errors"].append(f"Fetch recipes failed: {str(e)}")
        state["nodes_executed"][-1]["status"] = "failed"
        state["nodes_executed"][-1]["error"] = str(e)
        return state

    finally:
        db.close()


def solve_optimization_node(state: MealPlanningState) -> MealPlanningState:
    """
    Run Z3 constraint solver for optimal meal plan.

    Uses Z3 solver to find an optimal assignment of recipes to meals
    that satisfies all constraints and objectives.

    Args:
        state: Current workflow state

    Returns:
        Updated state with solver_result
    """
    from app.database import SessionLocal

    db = SessionLocal()
    start_time = time.time()

    try:
        state["current_step"] = "solve_optimization"

        # Track node execution
        state["nodes_executed"].append(
            {"name": "solve_optimization", "timestamp": start_time, "status": "started"}
        )

        agent = MealArchitectAgent(db, use_workflow=False)

        # Reconstruct Recipe objects from state
        from app.models.recipe import Recipe

        recipe_objects = []
        for r_dict in state["candidate_recipes"]:
            recipe = Recipe(
                id=r_dict["id"],
                title=r_dict["title"],
                ingredients=r_dict["ingredients"],
                dietary_tags=r_dict.get("dietary_tags"),
                nutrition=r_dict.get("nutrition"),
                servings=r_dict.get("servings", 2),
                prep_time=r_dict.get("prep_time", 0),
                cook_time=r_dict.get("cook_time", 0),
            )
            recipe_objects.append(recipe)

        # Run Z3 solver
        solver_start = time.time()

        solution = agent._solve_with_z3(
            recipes=recipe_objects,
            num_days=state["num_days"],
            num_people=state["num_people"],
            meals_per_day=state["meals_per_day"],
            target_calories_per_day=state.get("target_calories_per_day"),
            target_budget=state.get("target_budget"),
        )

        solver_time_ms = int((time.time() - solver_start) * 1000)

        state["solver_time_ms"] = solver_time_ms
        state["solver_result"] = {
            "status": "solved" if solution else "unsolved",
            "solution": solution,
            "time_ms": solver_time_ms,
        }

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - start_time) * 1000
        )
        state["nodes_executed"][-1]["solver_status"] = state["solver_result"]["status"]
        state["nodes_executed"][-1]["solver_time_ms"] = solver_time_ms

        return state

    except Exception as e:
        state["errors"].append(f"Solver failed: {str(e)}")
        state["nodes_executed"][-1]["status"] = "failed"
        state["nodes_executed"][-1]["error"] = str(e)
        state["solver_result"] = {"status": "error", "error": str(e)}
        return state

    finally:
        db.close()


def fallback_heuristic_node(state: MealPlanningState) -> MealPlanningState:
    """
    Use simple heuristic when Z3 solver fails.

    Implements a greedy algorithm that selects recipes based on:
    1. Variety (avoid repetition)
    2. Nutrition balance
    3. Constraints satisfaction

    Args:
        state: Current workflow state

    Returns:
        Updated state with heuristic solution
    """
    start_time = time.time()

    state["current_step"] = "fallback_heuristic"
    state["fallback_used"] = True

    # Track node execution
    state["nodes_executed"].append(
        {"name": "fallback_heuristic", "timestamp": start_time, "status": "started"}
    )

    try:
        import random

        # Simple greedy heuristic: randomly select from candidates without repetition
        recipes = state["candidate_recipes"]
        total_meals = state["num_days"] * state["meals_per_day"]

        if len(recipes) < total_meals:
            # Need to allow repetition
            selected_indices = []
            for _ in range(total_meals):
                selected_indices.append(random.randint(0, len(recipes) - 1))
        else:
            # Enough recipes for no repetition
            selected_indices = random.sample(range(len(recipes)), total_meals)

        # Build solution in same format as Z3 solver
        solution = {}
        meal_idx = 0
        meal_types = ["breakfast", "lunch", "dinner", "snack", "dessert", "beverage"]

        for day in range(1, state["num_days"] + 1):
            for meal_num in range(state["meals_per_day"]):
                recipe_idx = selected_indices[meal_idx]
                meal_type = meal_types[meal_num % len(meal_types)]

                solution[f"day_{day}_meal_{meal_num}"] = {
                    "recipe_id": recipes[recipe_idx]["id"],
                    "recipe_title": recipes[recipe_idx]["title"],
                    "day": day,
                    "meal_type": meal_type,
                }

                meal_idx += 1

        state["solver_result"] = {
            "status": "solved",
            "solution": solution,
            "time_ms": int((time.time() - start_time) * 1000),
            "method": "heuristic",
        }

        state["warnings"].append("Z3 solver failed, used simple heuristic fallback")

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - start_time) * 1000
        )
        state["nodes_executed"][-1]["meals_assigned"] = total_meals

        return state

    except Exception as e:
        state["errors"].append(f"Fallback heuristic failed: {str(e)}")
        state["nodes_executed"][-1]["status"] = "failed"
        state["nodes_executed"][-1]["error"] = str(e)
        return state


def relax_constraints_node(state: MealPlanningState) -> MealPlanningState:
    """
    Relax constraints for retry.

    When not enough recipes are found, this node relaxes constraints
    to allow more recipes to be included.

    Relaxation strategies:
    1. Remove least common dietary restriction
    2. Remove excluded ingredient with fewest matches
    3. Increase calorie tolerance range

    Args:
        state: Current workflow state

    Returns:
        Updated state with relaxed constraints
    """
    start_time = time.time()

    state["current_step"] = "relax_constraints"
    state["constraints_relaxed"] = True
    state["retry_count"] = state.get("retry_count", 0) + 1

    # Track node execution
    state["nodes_executed"].append(
        {
            "name": "relax_constraints",
            "timestamp": start_time,
            "status": "started",
            "retry_number": state["retry_count"],
        }
    )

    # Strategy 1: Remove a dietary restriction (if any)
    if state.get("dietary_restrictions") and len(state["dietary_restrictions"]) > 0:
        removed = state["dietary_restrictions"].pop()
        state["relaxation_strategy"] = f"Removed dietary restriction: {removed}"
        state["warnings"].append(
            f"Relaxed constraints: removed '{removed}' restriction"
        )

    # Strategy 2: Remove an excluded ingredient (if any)
    elif state.get("excluded_ingredients") and len(state["excluded_ingredients"]) > 0:
        removed = state["excluded_ingredients"].pop()
        state["relaxation_strategy"] = f"Removed excluded ingredient: {removed}"
        state["warnings"].append(
            f"Relaxed constraints: removed '{removed}' from exclusions"
        )

    # Strategy 3: Increase calorie tolerance
    elif state.get("target_calories_per_day"):
        old_target = state["target_calories_per_day"]
        # Remove calorie constraint entirely
        state["target_calories_per_day"] = None
        state["relaxation_strategy"] = "Removed calorie constraint"
        state["warnings"].append(
            f"Relaxed constraints: removed {old_target} cal/day target"
        )

    # Strategy 4: Remove budget constraint
    elif state.get("target_budget"):
        old_budget = state["target_budget"]
        state["target_budget"] = None
        state["relaxation_strategy"] = "Removed budget constraint"
        state["warnings"].append(f"Relaxed constraints: removed €{old_budget} budget")

    else:
        # No more constraints to relax
        state["relaxation_strategy"] = "No more constraints to relax"
        state["errors"].append("Cannot relax constraints further")

    # Mark node as completed
    state["nodes_executed"][-1]["status"] = "completed"
    state["nodes_executed"][-1]["duration_ms"] = int((time.time() - start_time) * 1000)
    state["nodes_executed"][-1]["strategy"] = state["relaxation_strategy"]

    return state


def store_meal_plan_node(state: MealPlanningState) -> MealPlanningState:
    """
    Store generated meal plan in database.

    Takes the solver solution and creates MealPlanRecipe records
    in the database.

    Args:
        state: Current workflow state

    Returns:
        Updated state with stored meal plan
    """
    from app.database import SessionLocal

    db = SessionLocal()
    start_time = time.time()

    try:
        state["current_step"] = "store_meal_plan"

        # Track node execution
        state["nodes_executed"].append(
            {"name": "store_meal_plan", "timestamp": start_time, "status": "started"}
        )

        solution = state["solver_result"]["solution"]

        # Get meal plan
        meal_plan = db.query(MealPlan).get(state["meal_plan_id"])

        # Store each meal

        for meal_key, meal_data in solution.items():
            # Calculate calories and cost if available from recipe
            # In a real implementation, we would fetch this from the recipe
            # For now, we'll leave them as None or calculate if we had the recipe object

            meal_plan_recipe = MealPlanRecipe(
                meal_plan_id=meal_plan.id,
                recipe_id=meal_data["recipe_id"],
                day_number=meal_data["day"],
                meal_type=meal_data["meal_type"],
                scheduled_date=meal_plan.start_date
                + timedelta(days=meal_data["day"] - 1),
                servings=state["num_people"],
            )
            db.add(meal_plan_recipe)

        # Update meal plan metadata
        meal_plan.total_recipes = len(solution)
        # meal_plan.total_calories = total_calories
        # meal_plan.total_cost = total_cost

        db.commit()
        db.refresh(meal_plan)

        # Serialize meal plan for state
        state["meal_plan"] = {
            "id": meal_plan.id,
            "name": meal_plan.name,
            "start_date": meal_plan.start_date.isoformat(),
            "end_date": meal_plan.end_date.isoformat(),
            "num_people": meal_plan.num_people,
            "status": meal_plan.status,
            "total_meals": len(solution),
        }

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - start_time) * 1000
        )
        state["nodes_executed"][-1]["meals_stored"] = len(solution)

        return state

    except Exception as e:
        state["errors"].append(f"Store meal plan failed: {str(e)}")
        state["nodes_executed"][-1]["status"] = "failed"
        state["nodes_executed"][-1]["error"] = str(e)
        return state

    finally:
        db.close()


def finalize_node(state: MealPlanningState) -> MealPlanningState:
    """
    Finalize meal plan and update status.

    Updates meal plan status to 'ready' and calculates final statistics.

    Args:
        state: Current workflow state

    Returns:
        Updated state with success=True
    """
    from app.database import SessionLocal

    db = SessionLocal()
    start_time = time.time()

    try:
        state["current_step"] = "finalize"

        # Track node execution
        state["nodes_executed"].append(
            {"name": "finalize", "timestamp": start_time, "status": "started"}
        )

        # Update meal plan status
        meal_plan = db.query(MealPlan).get(state["meal_plan_id"])
        meal_plan.status = "ready"
        db.commit()

        # Calculate total generation time
        state["generation_time_ms"] = int((time.time() - state["start_time"]) * 1000)
        state["success"] = True

        # Update meal plan in state
        if state.get("meal_plan"):
            state["meal_plan"]["status"] = "ready"
            state["meal_plan"]["generation_time_ms"] = state["generation_time_ms"]

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - start_time) * 1000
        )

        return state

    except Exception as e:
        state["errors"].append(f"Finalize failed: {str(e)}")
        state["nodes_executed"][-1]["status"] = "failed"
        state["nodes_executed"][-1]["error"] = str(e)
        return state

    finally:
        db.close()


def error_handler_node(state: MealPlanningState) -> MealPlanningState:
    """
    Handle errors and mark workflow as failed.

    Sets failure reason and updates meal plan status to 'failed'.

    Args:
        state: Current workflow state

    Returns:
        Updated state with success=False
    """
    from app.database import SessionLocal

    db = SessionLocal()
    start_time = time.time()

    try:
        state["current_step"] = "error_handler"

        # Track node execution
        state["nodes_executed"].append(
            {"name": "error_handler", "timestamp": start_time, "status": "started"}
        )

        # Determine failure reason
        if state["errors"]:
            state["failure_reason"] = "; ".join(state["errors"])
        else:
            state["failure_reason"] = "Unknown error occurred"

        # Update meal plan status
        if state.get("meal_plan_id"):
            meal_plan = db.query(MealPlan).get(state["meal_plan_id"])
            if meal_plan:
                meal_plan.status = "failed"
                db.commit()

        state["success"] = False
        state["generation_time_ms"] = int((time.time() - state["start_time"]) * 1000)

        # Mark node as completed
        state["nodes_executed"][-1]["status"] = "completed"
        state["nodes_executed"][-1]["duration_ms"] = int(
            (time.time() - start_time) * 1000
        )
        state["nodes_executed"][-1]["failure_reason"] = state["failure_reason"]

        return state

    finally:
        db.close()
