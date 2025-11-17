"""
LangGraph workflow for meal planning.

Orchestrates the complete meal planning process using a state machine.
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any

from app.workflows.meal_planning_state import MealPlanningState
from app.workflows.meal_planning_nodes import (
    initialize_state_node,
    validate_constraints_node,
    fetch_recipes_node,
    solve_optimization_node,
    fallback_heuristic_node,
    relax_constraints_node,
    store_meal_plan_node,
    finalize_node,
    error_handler_node,
)
from app.workflows.meal_planning_routing import (
    route_after_validation,
    route_after_fetch,
    route_after_solver,
    route_after_fallback,
)


def create_meal_planning_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for meal planning.

    Workflow structure:
    1. Initialize - Create meal plan record
    2. Validate - Check constraints
    3. Fetch Recipes - Get candidates
    4. Solve Optimization - Run Z3 solver
       - If insufficient recipes -> Relax Constraints -> back to Fetch
       - If solver fails -> Fallback Heuristic
    5. Store Meal Plan - Save to database
    6. Finalize - Update status
    7. Error Handler - Handle failures

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    workflow = StateGraph(MealPlanningState)

    # Add all nodes
    workflow.add_node("initialize", initialize_state_node)
    workflow.add_node("validate", validate_constraints_node)
    workflow.add_node("fetch_recipes", fetch_recipes_node)
    workflow.add_node("solve_optimization", solve_optimization_node)
    workflow.add_node("fallback_heuristic", fallback_heuristic_node)
    workflow.add_node("relax_constraints", relax_constraints_node)
    workflow.add_node("store_meal_plan", store_meal_plan_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_node("error_handler", error_handler_node)

    # Set entry point
    workflow.set_entry_point("initialize")

    # Add edges
    # Initialize -> Validate (always)
    workflow.add_edge("initialize", "validate")

    # Validate -> Fetch Recipes or Error Handler (conditional)
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "fetch_recipes": "fetch_recipes",
            "error_handler": "error_handler"
        }
    )

    # Fetch Recipes -> Solve, Relax, or Error (conditional)
    workflow.add_conditional_edges(
        "fetch_recipes",
        route_after_fetch,
        {
            "solve_optimization": "solve_optimization",
            "relax_constraints": "relax_constraints",
            "error_handler": "error_handler"
        }
    )

    # Relax Constraints -> Fetch Recipes (loop back)
    workflow.add_edge("relax_constraints", "fetch_recipes")

    # Solve Optimization -> Store, Fallback, or Error (conditional)
    workflow.add_conditional_edges(
        "solve_optimization",
        route_after_solver,
        {
            "store_meal_plan": "store_meal_plan",
            "fallback_heuristic": "fallback_heuristic",
            "error_handler": "error_handler"
        }
    )

    # Fallback Heuristic -> Store or Error (conditional)
    workflow.add_conditional_edges(
        "fallback_heuristic",
        route_after_fallback,
        {
            "store_meal_plan": "store_meal_plan",
            "error_handler": "error_handler"
        }
    )

    # Store Meal Plan -> Finalize (always)
    workflow.add_edge("store_meal_plan", "finalize")

    # Finalize -> END (terminal)
    workflow.add_edge("finalize", END)

    # Error Handler -> END (terminal)
    workflow.add_edge("error_handler", END)

    # Compile and return
    return workflow.compile()


def invoke_meal_planning_workflow(
    user_id: int,
    start_date: Any,  # date or str
    num_days: int,
    num_people: int,
    meals_per_day: int = 3,
    dietary_restrictions: list = None,
    excluded_ingredients: list = None,
    target_calories_per_day: int = None,
    target_budget: float = None,
    preferred_cuisines: list = None,
) -> Dict[str, Any]:
    """
    Invoke the meal planning workflow.

    Convenience function that creates initial state and runs workflow.

    Args:
        user_id: User ID
        start_date: Start date (date object or ISO string)
        num_days: Number of days
        num_people: Number of people
        meals_per_day: Meals per day (default: 3)
        dietary_restrictions: Optional dietary restrictions
        excluded_ingredients: Optional excluded ingredients
        target_calories_per_day: Optional calorie target
        target_budget: Optional budget
        preferred_cuisines: Optional cuisines

    Returns:
        Final workflow state as dict
    """
    from datetime import date as date_type
    from app.workflows.meal_planning_state import create_initial_state

    # Convert start_date to date object if string
    if isinstance(start_date, str):
        start_date = date_type.fromisoformat(start_date)

    # Create initial state
    initial_state = create_initial_state(
        user_id=user_id,
        start_date=start_date,
        num_days=num_days,
        num_people=num_people,
        meals_per_day=meals_per_day,
        dietary_restrictions=dietary_restrictions,
        excluded_ingredients=excluded_ingredients,
        target_calories_per_day=target_calories_per_day,
        target_budget=target_budget,
        preferred_cuisines=preferred_cuisines,
    )

    # Create and run workflow
    workflow = create_meal_planning_workflow()
    result = workflow.invoke(initial_state)

    return result


# For easier imports
__all__ = [
    "create_meal_planning_workflow",
    "invoke_meal_planning_workflow",
]
