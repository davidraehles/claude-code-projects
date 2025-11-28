"""
State schema for meal planning workflow.

Defines the state that flows through the LangGraph workflow nodes.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import date


class MealPlanningState(TypedDict, total=False):
    """
    State that flows through the LangGraph meal planning workflow.

    This state is passed between workflow nodes and tracks the entire
    meal planning generation process from initialization to completion.
    """

    # ===== Input Parameters (from API request) =====
    user_id: int
    start_date: date
    num_days: int
    num_people: int
    dietary_restrictions: Optional[List[str]]
    excluded_ingredients: Optional[List[str]]
    target_calories_per_day: Optional[int]
    target_budget: Optional[float]
    preferred_cuisines: Optional[List[str]]
    meals_per_day: int

    # ===== Workflow Tracking =====
    meal_plan_id: Optional[int]  # Created after initialization node
    current_step: str  # Name of current workflow node
    errors: List[str]  # Accumulated error messages
    warnings: List[str]  # Accumulated warning messages
    retry_count: int  # Number of retries attempted
    start_time: float  # Workflow start timestamp (time.time())
    nodes_executed: List[Dict[str, Any]]  # History of executed nodes

    # ===== Intermediate Results =====
    candidate_recipes: Optional[List[Dict[str, Any]]]  # Recipes fetched from database
    constraints_relaxed: bool  # Whether constraints were relaxed
    relaxation_strategy: Optional[str]  # How constraints were relaxed
    solver_result: Optional[Dict[str, Any]]  # Z3 solver output
    solver_time_ms: Optional[int]  # Time taken by Z3 solver
    fallback_used: bool  # Whether heuristic fallback was used

    # ===== Final Output =====
    meal_plan: Optional[Dict[str, Any]]  # Generated meal plan (serialized)
    generation_time_ms: Optional[int]  # Total generation time in milliseconds
    success: bool  # Whether workflow succeeded
    failure_reason: Optional[str]  # Reason if workflow failed


def create_initial_state(
    user_id: int,
    start_date: date,
    num_days: int,
    num_people: int,
    meals_per_day: int = 3,
    dietary_restrictions: Optional[List[str]] = None,
    excluded_ingredients: Optional[List[str]] = None,
    target_calories_per_day: Optional[int] = None,
    target_budget: Optional[float] = None,
    preferred_cuisines: Optional[List[str]] = None,
) -> MealPlanningState:
    """
    Create initial state for workflow.

    Args:
        user_id: User ID
        start_date: Start date for meal plan
        num_days: Number of days to plan
        num_people: Number of people
        meals_per_day: Meals per day (default: 3)
        dietary_restrictions: Optional dietary restrictions
        excluded_ingredients: Optional ingredients to exclude
        target_calories_per_day: Optional calorie target per day
        target_budget: Optional budget constraint
        preferred_cuisines: Optional preferred cuisines

    Returns:
        Initial MealPlanningState
    """
    return MealPlanningState(
        # Input parameters
        user_id=user_id,
        start_date=start_date,
        num_days=num_days,
        num_people=num_people,
        dietary_restrictions=dietary_restrictions,
        excluded_ingredients=excluded_ingredients,
        target_calories_per_day=target_calories_per_day,
        target_budget=target_budget,
        preferred_cuisines=preferred_cuisines,
        meals_per_day=meals_per_day,

        # Initialize workflow state
        meal_plan_id=None,
        current_step="start",
        errors=[],
        warnings=[],
        retry_count=0,
        nodes_executed=[],

        # Initialize intermediate results
        candidate_recipes=None,
        constraints_relaxed=False,
        relaxation_strategy=None,
        solver_result=None,
        solver_time_ms=None,
        fallback_used=False,

        # Initialize final output
        meal_plan=None,
        generation_time_ms=None,
        success=False,
        failure_reason=None,
    )
