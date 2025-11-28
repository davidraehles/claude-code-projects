"""
Error handling for meal planning workflow.

Defines custom exceptions and error recovery strategies.
"""

from typing import Callable, Any
from functools import wraps

from app.workflows.meal_planning_state import MealPlanningState


# ===== Custom Exceptions =====

class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class ValidationError(WorkflowError):
    """Validation failed."""
    pass


class InsufficientRecipesError(WorkflowError):
    """Not enough recipes found to satisfy constraints."""
    pass


class SolverError(WorkflowError):
    """Z3 solver failed to find solution."""
    pass


class DatabaseError(WorkflowError):
    """Database operation failed."""
    pass


class TimeoutError(WorkflowError):
    """Workflow exceeded time limit."""
    pass


# ===== Error Handling Functions =====

def handle_error(state: MealPlanningState, error: Exception) -> MealPlanningState:
    """
    Handle errors in workflow.

    Determines if error is retryable and updates state accordingly.

    Args:
        state: Current workflow state
        error: Exception that occurred

    Returns:
        Updated state with error information
    """
    error_message = str(error)

    # Add to errors list
    if "errors" not in state:
        state["errors"] = []
    state["errors"].append(error_message)

    # Determine if retryable
    retryable_errors = (
        InsufficientRecipesError,
        SolverError,
        TimeoutError
    )

    is_retryable = isinstance(error, retryable_errors)

    # Check retry count
    retry_count = state.get("retry_count", 0)
    max_retries = 3

    if is_retryable and retry_count < max_retries:
        # Increment retry count
        state["retry_count"] = retry_count + 1

        # Add warning
        if "warnings" not in state:
            state["warnings"] = []
        state["warnings"].append(
            f"Retrying after error (attempt {state['retry_count']}/{max_retries}): {error_message}"
        )

        return state

    # Non-retryable or max retries exceeded
    state["success"] = False
    state["failure_reason"] = error_message

    return state


def with_retry(max_retries: int = 3) -> Callable:
    """
    Decorator to add retry logic to node functions.

    Args:
        max_retries: Maximum number of retry attempts

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: MealPlanningState, *args: Any, **kwargs: Any) -> MealPlanningState:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(state, *args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Update retry count
                    state["retry_count"] = state.get("retry_count", 0) + 1

                    # Add warning
                    if "warnings" not in state:
                        state["warnings"] = []
                    state["warnings"].append(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {str(e)}"
                    )

                    # If last attempt, handle error and return
                    if attempt == max_retries - 1:
                        return handle_error(state, e)

            # Should not reach here, but handle gracefully
            if last_exception:
                return handle_error(state, last_exception)

            return state

        return wrapper

    return decorator


def is_retriable_error(error: Exception) -> bool:
    """
    Check if an error is retriable.

    Args:
        error: Exception to check

    Returns:
        True if error can be retried, False otherwise
    """
    retriable_types = (
        InsufficientRecipesError,
        SolverError,
        TimeoutError,
    )

    return isinstance(error, retriable_types)


def get_error_category(error: Exception) -> str:
    """
    Categorize error for monitoring and alerting.

    Args:
        error: Exception to categorize

    Returns:
        Error category string
    """
    if isinstance(error, ValidationError):
        return "validation"
    elif isinstance(error, InsufficientRecipesError):
        return "insufficient_recipes"
    elif isinstance(error, SolverError):
        return "solver_failure"
    elif isinstance(error, DatabaseError):
        return "database"
    elif isinstance(error, TimeoutError):
        return "timeout"
    else:
        return "unknown"


def format_error_for_user(error: Exception) -> str:
    """
    Format error message for user-friendly display.

    Args:
        error: Exception to format

    Returns:
        User-friendly error message
    """
    if isinstance(error, ValidationError):
        return f"Invalid input: {str(error)}"

    elif isinstance(error, InsufficientRecipesError):
        return (
            "We couldn't find enough recipes matching your constraints. "
            "Try relaxing some dietary restrictions or excluded ingredients."
        )

    elif isinstance(error, SolverError):
        return (
            "We had trouble optimizing your meal plan. "
            "Please try again or adjust your preferences."
        )

    elif isinstance(error, DatabaseError):
        return (
            "A technical error occurred. Please try again in a few moments."
        )

    elif isinstance(error, TimeoutError):
        return (
            "Meal plan generation took too long. "
            "Try reducing the number of days or simplifying constraints."
        )

    else:
        return (
            "An unexpected error occurred. Please try again or contact support."
        )


def should_alert(error: Exception, retry_count: int) -> bool:
    """
    Determine if error should trigger an alert.

    Args:
        error: Exception that occurred
        retry_count: Number of retries attempted

    Returns:
        True if should alert operations team, False otherwise
    """
    # Alert on database errors
    if isinstance(error, DatabaseError):
        return True

    # Alert if max retries exceeded
    if retry_count >= 3:
        return True

    # Alert on repeated solver failures
    if isinstance(error, SolverError) and retry_count >= 2:
        return True

    return False
