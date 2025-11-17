"""
Conditional routing logic for meal planning workflow.

Determines which node to execute next based on current state.
"""

from app.workflows.meal_planning_state import MealPlanningState


def route_after_validation(state: MealPlanningState) -> str:
    """
    Route after validation node.

    Routes to error_handler if validation errors exist,
    otherwise proceeds to fetch_recipes.

    Args:
        state: Current workflow state

    Returns:
        Next node name: "fetch_recipes" or "error_handler"
    """
    if state.get("errors") and len(state["errors"]) > 0:
        return "error_handler"
    return "fetch_recipes"


def route_after_fetch(state: MealPlanningState) -> str:
    """
    Route after fetch_recipes node.

    Checks if enough recipes were found:
    - If yes: proceed to solve_optimization
    - If no and retry_count < 3: relax_constraints
    - If no and retry_count >= 3: error_handler

    Args:
        state: Current workflow state

    Returns:
        Next node name: "solve_optimization", "relax_constraints", or "error_handler"
    """
    min_required = state["num_days"] * state["meals_per_day"]
    recipes_count = len(state.get("candidate_recipes") or [])

    # Check if we have enough recipes
    if recipes_count >= min_required:
        return "solve_optimization"

    # Not enough recipes
    retry_count = state.get("retry_count", 0)

    if retry_count < 3:
        # Try relaxing constraints
        return "relax_constraints"
    else:
        # Max retries exceeded
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(
            f"Insufficient recipes: found {recipes_count}, need {min_required} "
            f"(after {retry_count} retries)"
        )
        return "error_handler"


def route_after_solver(state: MealPlanningState) -> str:
    """
    Route after solve_optimization node.

    Checks if Z3 solver succeeded:
    - If yes: proceed to store_meal_plan
    - If no and retry_count < 2: try fallback_heuristic
    - If no and retry_count >= 2: error_handler

    Args:
        state: Current workflow state

    Returns:
        Next node name: "store_meal_plan", "fallback_heuristic", or "error_handler"
    """
    solver_result = state.get("solver_result")

    # Check if solver succeeded
    if solver_result and solver_result.get("status") == "solved":
        return "store_meal_plan"

    # Solver failed
    retry_count = state.get("retry_count", 0)

    if retry_count < 2:
        # Try heuristic fallback
        return "fallback_heuristic"
    else:
        # Max retries exceeded
        if "errors" not in state:
            state["errors"] = []

        error_msg = solver_result.get("error", "Unknown solver error")
        state["errors"].append(f"Solver failed after {retry_count} retries: {error_msg}")
        return "error_handler"


def route_after_fallback(state: MealPlanningState) -> str:
    """
    Route after fallback_heuristic node.

    Checks if fallback heuristic succeeded:
    - If yes: proceed to store_meal_plan
    - If no: error_handler

    Args:
        state: Current workflow state

    Returns:
        Next node name: "store_meal_plan" or "error_handler"
    """
    solver_result = state.get("solver_result")

    # Check if fallback succeeded
    if solver_result and solver_result.get("status") == "solved":
        return "store_meal_plan"

    # Fallback also failed
    if "errors" not in state:
        state["errors"] = []

    error_msg = solver_result.get("error", "Unknown fallback error")
    state["errors"].append(f"Both Z3 solver and heuristic fallback failed: {error_msg}")
    return "error_handler"


def should_continue_after_relax(state: MealPlanningState) -> str:
    """
    After relaxing constraints, always return to fetch_recipes.

    Args:
        state: Current workflow state

    Returns:
        Always returns "fetch_recipes"
    """
    return "fetch_recipes"


def route_to_end(state: MealPlanningState) -> str:
    """
    Route to END node (terminal).

    Used after finalize and error_handler nodes.

    Args:
        state: Current workflow state

    Returns:
        Always returns "END"
    """
    return "END"
