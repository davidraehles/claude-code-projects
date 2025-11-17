"""
Workflow visualization utilities.

Generates Mermaid diagrams and execution traces for the meal planning workflow.
"""

from typing import Dict, Any, List
from app.workflows.meal_planning_state import MealPlanningState


def generate_mermaid_diagram() -> str:
    """
    Generate Mermaid diagram of the meal planning workflow.

    Returns:
        Mermaid diagram as string
    """
    return """
graph TD
    START([Start]) --> INIT[Initialize State]
    INIT --> VALIDATE[Validate Constraints]

    VALIDATE --> |Valid| FETCH[Fetch Candidate Recipes]
    VALIDATE --> |Invalid| ERROR[Error Handler]

    FETCH --> CHECK_COUNT{Enough<br/>Recipes?}
    CHECK_COUNT --> |Yes| SOLVE[Run Z3 Solver]
    CHECK_COUNT --> |No, Retry < 3| RELAX[Relax Constraints]
    CHECK_COUNT --> |No, Retry >= 3| ERROR

    RELAX --> |Loop Back| FETCH

    SOLVE --> CHECK_SOLUTION{Solution<br/>Found?}
    CHECK_SOLUTION --> |Yes| STORE[Store Meal Plan]
    CHECK_SOLUTION --> |No, Retry < 2| FALLBACK[Heuristic Fallback]
    CHECK_SOLUTION --> |No, Retry >= 2| ERROR

    FALLBACK --> CHECK_FALLBACK{Fallback<br/>Success?}
    CHECK_FALLBACK --> |Yes| STORE
    CHECK_FALLBACK --> |No| ERROR

    STORE --> FINALIZE[Finalize Plan]
    FINALIZE --> END([Complete])

    ERROR --> END

    style INIT fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style VALIDATE fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style FETCH fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style RELAX fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style SOLVE fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style FALLBACK fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style STORE fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style FINALIZE fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style ERROR fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    style START fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    style END fill:#f3e5f5,stroke:#4a148c,stroke-width:3px

    classDef decision fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    class CHECK_COUNT,CHECK_SOLUTION,CHECK_FALLBACK decision
"""


def generate_execution_diagram(state: MealPlanningState) -> str:
    """
    Generate Mermaid diagram showing actual execution path.

    Args:
        state: Workflow state after execution

    Returns:
        Mermaid diagram showing execution path
    """
    nodes_executed = state.get("nodes_executed", [])

    if not nodes_executed:
        return "No execution data available"

    lines = ["graph LR"]

    # Add nodes in execution order
    for i, node in enumerate(nodes_executed):
        node_name = node["name"]
        status = node.get("status", "unknown")
        duration = node.get("duration_ms", 0)

        # Node styling based on status
        if status == "completed":
            style = "fill:#e8f5e9,stroke:#1b5e20"
        elif status == "failed":
            style = "fill:#ffebee,stroke:#b71c1c"
        else:
            style = "fill:#f5f5f5,stroke:#9e9e9e"

        node_id = f"N{i}"
        label = f"{node_name}<br/>{duration}ms"

        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    style {node_id} {style}")

        # Add edge to next node
        if i < len(nodes_executed) - 1:
            next_id = f"N{i+1}"
            lines.append(f"    {node_id} --> {next_id}")

    return "\n".join(lines)


def visualize_execution_trace(state: MealPlanningState) -> str:
    """
    Generate execution trace visualization in text format.

    Args:
        state: Workflow state

    Returns:
        Formatted execution trace
    """
    nodes_executed = state.get("nodes_executed", [])

    if not nodes_executed:
        return "No execution data available"

    lines = []
    lines.append("╔" + "═" * 58 + "╗")
    lines.append("║" + " " * 15 + "WORKFLOW EXECUTION TRACE" + " " * 19 + "║")
    lines.append("╠" + "═" * 58 + "╣")

    total_time = state.get("generation_time_ms", 0)
    lines.append(f"║ Total Time: {total_time}ms" + " " * (58 - len(f" Total Time: {total_time}ms") - 1) + "║")
    lines.append(f"║ Success: {state.get('success', False)}" + " " * (58 - len(f" Success: {state.get('success', False)}") - 1) + "║")
    lines.append(f"║ Retries: {state.get('retry_count', 0)}" + " " * (58 - len(f" Retries: {state.get('retry_count', 0)}") - 1) + "║")
    lines.append("╠" + "═" * 58 + "╣")

    for i, node in enumerate(nodes_executed, 1):
        name = node["name"]
        status = node.get("status", "unknown")
        duration = node.get("duration_ms", 0)

        # Status icon
        if status == "completed":
            icon = "✅"
        elif status == "failed":
            icon = "❌"
        else:
            icon = "⏳"

        # Format line
        line = f" {i:2d}. {icon} {name:<30s} {duration:>5d}ms "
        lines.append(f"║{line:<58s}║")

        # Add error if present
        if node.get("error"):
            error_line = f"     Error: {node['error'][:42]}"
            lines.append(f"║{error_line:<58s}║")

        # Add node-specific info
        if node.get("recipes_found") is not None:
            info = f"     Recipes: {node['recipes_found']}/{node.get('recipes_required', '?')}"
            lines.append(f"║{info:<58s}║")

        if node.get("solver_status"):
            info = f"     Solver: {node['solver_status']}"
            lines.append(f"║{info:<58s}║")

    lines.append("╚" + "═" * 58 + "╝")

    return "\n".join(lines)


def generate_statistics_table(state: MealPlanningState) -> str:
    """
    Generate statistics table from workflow execution.

    Args:
        state: Workflow state

    Returns:
        Formatted statistics table
    """
    nodes_executed = state.get("nodes_executed", [])

    lines = []
    lines.append("┌" + "─" * 58 + "┐")
    lines.append("│" + " " * 20 + "WORKFLOW STATISTICS" + " " * 19 + "│")
    lines.append("├" + "─" * 58 + "┤")

    # Overall statistics
    stats = [
        ("Meal Plan ID", state.get("meal_plan_id", "N/A")),
        ("User ID", state.get("user_id", "N/A")),
        ("Days Planned", state.get("num_days", "N/A")),
        ("Meals per Day", state.get("meals_per_day", "N/A")),
        ("Total Meals", state.get("num_days", 0) * state.get("meals_per_day", 0)),
        ("", ""),  # Separator
        ("Success", "✅ Yes" if state.get("success") else "❌ No"),
        ("Generation Time", f"{state.get('generation_time_ms', 0)}ms"),
        ("Retries", state.get("retry_count", 0)),
        ("Fallback Used", "Yes" if state.get("fallback_used") else "No"),
        ("", ""),  # Separator
        ("Nodes Executed", len(nodes_executed)),
        ("Nodes Failed", sum(1 for n in nodes_executed if n.get("status") == "failed")),
        ("Errors", len(state.get("errors", []))),
        ("Warnings", len(state.get("warnings", []))),
    ]

    for key, value in stats:
        if key == "":
            lines.append("├" + "─" * 58 + "┤")
        else:
            line = f" {key:<30s} {str(value):>25s} "
            lines.append(f"│{line:<58s}│")

    lines.append("└" + "─" * 58 + "┘")

    return "\n".join(lines)


def export_to_markdown(state: MealPlanningState) -> str:
    """
    Export workflow execution to markdown format.

    Args:
        state: Workflow state

    Returns:
        Markdown-formatted report
    """
    lines = []

    lines.append("# Meal Planning Workflow Execution Report")
    lines.append("")
    lines.append(f"**Generated**: {state.get('start_time', 'N/A')}")
    lines.append(f"**Meal Plan ID**: {state.get('meal_plan_id', 'N/A')}")
    lines.append(f"**User ID**: {state.get('user_id', 'N/A')}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Status**: {'✅ Success' if state.get('success') else '❌ Failed'}")
    lines.append(f"- **Generation Time**: {state.get('generation_time_ms', 0)}ms")
    lines.append(f"- **Retries**: {state.get('retry_count', 0)}")
    lines.append(f"- **Fallback Used**: {'Yes' if state.get('fallback_used') else 'No'}")
    lines.append("")

    # Parameters
    lines.append("## Parameters")
    lines.append("")
    lines.append(f"- **Days**: {state.get('num_days')}")
    lines.append(f"- **People**: {state.get('num_people')}")
    lines.append(f"- **Meals per Day**: {state.get('meals_per_day')}")

    if state.get("dietary_restrictions"):
        lines.append(f"- **Dietary Restrictions**: {', '.join(state['dietary_restrictions'])}")

    if state.get("excluded_ingredients"):
        lines.append(f"- **Excluded Ingredients**: {', '.join(state['excluded_ingredients'])}")

    if state.get("target_calories_per_day"):
        lines.append(f"- **Target Calories**: {state['target_calories_per_day']} cal/day")

    if state.get("target_budget"):
        lines.append(f"- **Target Budget**: €{state['target_budget']}")

    lines.append("")

    # Execution trace
    lines.append("## Execution Trace")
    lines.append("")

    nodes_executed = state.get("nodes_executed", [])
    for i, node in enumerate(nodes_executed, 1):
        status_icon = "✅" if node.get("status") == "completed" else "❌"
        lines.append(f"{i}. {status_icon} **{node['name']}** ({node.get('duration_ms', 0)}ms)")

        if node.get("error"):
            lines.append(f"   - Error: `{node['error']}`")

        if node.get("recipes_found") is not None:
            lines.append(f"   - Recipes Found: {node['recipes_found']}")

        if node.get("solver_status"):
            lines.append(f"   - Solver Status: {node['solver_status']}")

        lines.append("")

    # Errors
    if state.get("errors"):
        lines.append("## Errors")
        lines.append("")
        for error in state["errors"]:
            lines.append(f"- ❌ {error}")
        lines.append("")

    # Warnings
    if state.get("warnings"):
        lines.append("## Warnings")
        lines.append("")
        for warning in state["warnings"]:
            lines.append(f"- ⚠️ {warning}")
        lines.append("")

    # Workflow diagram
    lines.append("## Workflow Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append(generate_execution_diagram(state))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# Export all visualization functions
__all__ = [
    "generate_mermaid_diagram",
    "generate_execution_diagram",
    "visualize_execution_trace",
    "generate_statistics_table",
    "export_to_markdown",
]
