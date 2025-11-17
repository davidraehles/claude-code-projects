"""
LangSmith tracing integration for meal planning workflow.

Provides observability and debugging capabilities.
"""

import os
from typing import Dict, Any, Optional
from functools import wraps

from app.workflows.meal_planning_state import MealPlanningState

# Check if LangSmith is available
LANGSMITH_ENABLED = os.getenv("LANGSMITH_API_KEY") is not None

if LANGSMITH_ENABLED:
    try:
        from langsmith import Client
        from langsmith.run_helpers import traceable

        # Initialize LangSmith client
        langsmith_client = Client(
            api_key=os.getenv("LANGSMITH_API_KEY"),
            api_url=os.getenv("LANGSMITH_API_URL", "https://api.smith.langchain.com")
        )
    except ImportError:
        LANGSMITH_ENABLED = False
        print("Warning: langsmith package not installed, tracing disabled")


def trace_workflow_execution(func):
    """
    Decorator to trace complete workflow execution.

    Args:
        func: Function to trace

    Returns:
        Decorated function with tracing
    """
    if not LANGSMITH_ENABLED:
        return func

    @wraps(func)
    @traceable(run_type="chain", name="meal_planning_workflow")
    def wrapper(state: MealPlanningState, *args, **kwargs):
        result = func(state, *args, **kwargs)

        # Log workflow summary
        trace_data = {
            "user_id": state.get("user_id"),
            "meal_plan_id": state.get("meal_plan_id"),
            "success": state.get("success"),
            "generation_time_ms": state.get("generation_time_ms"),
            "errors": state.get("errors", []),
            "warnings": state.get("warnings", []),
            "nodes_executed": [n["name"] for n in state.get("nodes_executed", [])],
            "retry_count": state.get("retry_count", 0),
            "fallback_used": state.get("fallback_used", False),
        }

        return result

    return wrapper


def trace_node_execution(node_name: str):
    """
    Decorator to trace individual node execution.

    Args:
        node_name: Name of the node

    Returns:
        Decorator function
    """
    def decorator(func):
        if not LANGSMITH_ENABLED:
            return func

        @wraps(func)
        @traceable(run_type="tool", name=f"node_{node_name}")
        def wrapper(state: MealPlanningState, *args, **kwargs):
            # Log node input
            input_data = {
                "node": node_name,
                "current_step": state.get("current_step"),
                "retry_count": state.get("retry_count", 0),
                "errors_so_far": len(state.get("errors", [])),
                "warnings_so_far": len(state.get("warnings", [])),
            }

            result = func(state, *args, **kwargs)

            # Log node output
            output_data = {
                "node": node_name,
                "new_errors": len(result.get("errors", [])) - len(state.get("errors", [])),
                "new_warnings": len(result.get("warnings", [])) - len(state.get("warnings", [])),
            }

            return result

        return wrapper

    return decorator


def trace_solver_execution(func):
    """
    Decorator to trace Z3 solver execution.

    Args:
        func: Solver function to trace

    Returns:
        Decorated function with tracing
    """
    if not LANGSMITH_ENABLED:
        return func

    @wraps(func)
    @traceable(run_type="tool", name="z3_solver")
    def wrapper(state: MealPlanningState, *args, **kwargs):
        # Log solver input
        solver_input = {
            "num_recipes": len(state.get("candidate_recipes", [])),
            "num_days": state.get("num_days"),
            "meals_per_day": state.get("meals_per_day"),
            "dietary_restrictions": state.get("dietary_restrictions"),
            "target_calories": state.get("target_calories_per_day"),
            "target_budget": state.get("target_budget"),
        }

        result = func(state, *args, **kwargs)

        # Log solver output
        solver_result = result.get("solver_result", {})
        solver_output = {
            "status": solver_result.get("status"),
            "solver_time_ms": solver_result.get("time_ms"),
            "method": solver_result.get("method", "z3"),
        }

        return result

    return wrapper


def get_workflow_trace_url(run_id: str) -> Optional[str]:
    """
    Get LangSmith trace URL for a workflow run.

    Args:
        run_id: LangSmith run ID

    Returns:
        URL to view trace, or None if LangSmith not enabled
    """
    if not LANGSMITH_ENABLED:
        return None

    project = os.getenv("LANGSMITH_PROJECT", "meal-planning-orchestration")
    return f"https://smith.langchain.com/o/default/projects/{project}/r/{run_id}"


def log_workflow_metrics(state: MealPlanningState) -> Dict[str, Any]:
    """
    Extract metrics from workflow state for monitoring.

    Args:
        state: Final workflow state

    Returns:
        Dictionary of metrics
    """
    nodes_executed = state.get("nodes_executed", [])

    metrics = {
        # Overall metrics
        "success": state.get("success", False),
        "generation_time_ms": state.get("generation_time_ms", 0),
        "retry_count": state.get("retry_count", 0),
        "fallback_used": state.get("fallback_used", False),

        # Error metrics
        "error_count": len(state.get("errors", [])),
        "warning_count": len(state.get("warnings", [])),

        # Node metrics
        "nodes_executed_count": len(nodes_executed),
        "nodes_failed_count": sum(1 for n in nodes_executed if n.get("status") == "failed"),

        # Timing breakdown
        "time_initialize_ms": next(
            (n.get("duration_ms", 0) for n in nodes_executed if n["name"] == "initialize"), 0
        ),
        "time_validate_ms": next(
            (n.get("duration_ms", 0) for n in nodes_executed if n["name"] == "validate"), 0
        ),
        "time_fetch_recipes_ms": next(
            (n.get("duration_ms", 0) for n in nodes_executed if n["name"] == "fetch_recipes"), 0
        ),
        "time_solver_ms": next(
            (n.get("duration_ms", 0) for n in nodes_executed if n["name"] == "solve_optimization"), 0
        ),
        "time_store_ms": next(
            (n.get("duration_ms", 0) for n in nodes_executed if n["name"] == "store_meal_plan"), 0
        ),

        # Recipe metrics
        "recipes_found": len(state.get("candidate_recipes", [])),
        "recipes_required": state.get("num_days", 0) * state.get("meals_per_day", 3),

        # Constraint metrics
        "constraints_relaxed": state.get("constraints_relaxed", False),
        "relaxation_strategy": state.get("relaxation_strategy"),
    }

    return metrics


def format_execution_trace(state: MealPlanningState) -> str:
    """
    Format workflow execution trace as human-readable string.

    Args:
        state: Workflow state

    Returns:
        Formatted trace string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("Meal Planning Workflow Execution Trace")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("Summary:")
    lines.append(f"  User ID: {state.get('user_id')}")
    lines.append(f"  Meal Plan ID: {state.get('meal_plan_id')}")
    lines.append(f"  Success: {state.get('success')}")
    lines.append(f"  Generation Time: {state.get('generation_time_ms')}ms")
    lines.append(f"  Retry Count: {state.get('retry_count', 0)}")
    lines.append(f"  Fallback Used: {state.get('fallback_used', False)}")
    lines.append("")

    # Nodes executed
    lines.append("Nodes Executed:")
    for i, node in enumerate(state.get("nodes_executed", []), 1):
        status_icon = "✅" if node.get("status") == "completed" else "❌"
        lines.append(f"  {i}. {status_icon} {node['name']}")
        lines.append(f"     Duration: {node.get('duration_ms', 0)}ms")

        if node.get("status") == "failed":
            lines.append(f"     Error: {node.get('error')}")

        if node.get("recipes_found") is not None:
            lines.append(f"     Recipes Found: {node.get('recipes_found')}")

        if node.get("solver_status"):
            lines.append(f"     Solver Status: {node.get('solver_status')}")

        lines.append("")

    # Errors
    if state.get("errors"):
        lines.append("Errors:")
        for error in state["errors"]:
            lines.append(f"  ❌ {error}")
        lines.append("")

    # Warnings
    if state.get("warnings"):
        lines.append("Warnings:")
        for warning in state["warnings"]:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


# Export tracing utilities
__all__ = [
    "trace_workflow_execution",
    "trace_node_execution",
    "trace_solver_execution",
    "get_workflow_trace_url",
    "log_workflow_metrics",
    "format_execution_trace",
    "LANGSMITH_ENABLED",
]
