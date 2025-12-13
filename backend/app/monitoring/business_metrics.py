"""
Business KPI Metrics Module

This module tracks business-critical metrics for the Go, Cart! application.
All metrics are exposed to Prometheus for monitoring and alerting.

Metrics Categories:
- Recipe harvesting and processing
- Meal plan generation and completion
- Grocery cart creation and conversion
- User activity and retention
- Error tracking and business impact
- External API integration health
"""

from functools import wraps
from typing import Callable, Optional, Any
import time
from datetime import datetime, timedelta

from prometheus_client import Counter, Gauge, Histogram, Summary
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan
from app.models.grocery_cart import GroceryCart
from app.models.user import User


# ============================================================================
# RECIPE METRICS
# ============================================================================

recipes_harvested_total = Counter(
    'recipes_harvested_total',
    'Total number of recipes harvested',
    ['source']  # web, api, rss, file
)

recipes_with_errors_total = Counter(
    'recipes_with_errors_total',
    'Total number of recipe harvest errors',
    ['source', 'error_type']
)

recipe_harvest_duration_seconds = Histogram(
    'recipe_harvest_duration_seconds',
    'Time taken to harvest a recipe',
    ['source'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)

unique_recipes_count = Gauge(
    'unique_recipes_count',
    'Total number of unique recipes in the database'
)


# ============================================================================
# MEAL PLAN METRICS
# ============================================================================

meal_plans_generated_total = Counter(
    'meal_plans_generated_total',
    'Total number of meal plans generated',
    ['generation_type']  # manual, ai_suggested, template
)

meal_plans_completed_total = Counter(
    'meal_plans_completed_total',
    'Total number of meal plans marked as completed'
)

meal_plan_generation_duration_seconds = Histogram(
    'meal_plan_generation_duration_seconds',
    'Time taken to generate a meal plan',
    ['generation_type'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0, 120.0]
)

user_satisfaction_score = Gauge(
    'user_satisfaction_score',
    'Average user satisfaction score for meal plans',
    ['plan_type']
)


# ============================================================================
# GROCERY CART METRICS
# ============================================================================

carts_created_total = Counter(
    'carts_created_total',
    'Total number of grocery carts created'
)

carts_completed_total = Counter(
    'carts_completed_total',
    'Total number of grocery carts completed (filled and submitted)'
)

items_aggregated_total = Counter(
    'items_aggregated_total',
    'Total number of items aggregated in carts'
)

knuspr_integration_success_rate = Gauge(
    'knuspr_integration_success_rate',
    'Success rate of Knuspr API integration (percentage)'
)


# ============================================================================
# USER METRICS
# ============================================================================

active_users_total = Gauge(
    'active_users_total',
    'Number of active users',
    ['period']  # daily, weekly, monthly
)

new_users_total = Counter(
    'new_users_total',
    'Total number of new user registrations'
)

user_retention_rate = Gauge(
    'user_retention_rate',
    'User retention rate',
    ['period']  # 30d, 60d, 90d
)

feature_usage_total = Counter(
    'feature_usage_total',
    'Total usage count for each feature',
    ['feature']  # recipe_search, meal_plan, cart_generation, etc.
)


# ============================================================================
# ERROR METRICS
# ============================================================================

error_rate_percent = Gauge(
    'error_rate_percent',
    'Error rate as percentage of total requests'
)

error_by_type_total = Counter(
    'error_by_type_total',
    'Total errors by type',
    ['error_type']  # validation, auth, db, external, internal
)

user_facing_errors_total = Counter(
    'user_facing_errors_total',
    'Total errors that impact user experience',
    ['endpoint', 'error_code']
)


# ============================================================================
# INTEGRATION METRICS
# ============================================================================

knuspr_api_calls_total = Counter(
    'knuspr_api_calls_total',
    'Total Knuspr API calls',
    ['status']  # success, rate_limited, failed
)

knuspr_api_latency_seconds = Summary(
    'knuspr_api_latency_seconds',
    'Knuspr API call latency',
    ['operation']
)

external_api_calls_total = Counter(
    'external_api_calls_total',
    'Total external API calls',
    ['service', 'status']
)

circuit_breaker_state_changes_total = Counter(
    'circuit_breaker_state_changes_total',
    'Total circuit breaker state changes',
    ['service', 'from_state', 'to_state']
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def track_recipe_harvest(source: str) -> Callable:
    """
    Decorator to track recipe harvesting metrics.

    Usage:
        @track_recipe_harvest('web')
        async def harvest_from_web(url: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                recipes_harvested_total.labels(source=source).inc()
                duration = time.time() - start_time
                recipe_harvest_duration_seconds.labels(source=source).observe(duration)
                return result
            except Exception as e:
                error_type = type(e).__name__
                recipes_with_errors_total.labels(
                    source=source,
                    error_type=error_type
                ).inc()
                raise
        return wrapper
    return decorator


def track_meal_plan_generation(generation_type: str) -> Callable:
    """
    Decorator to track meal plan generation metrics.

    Usage:
        @track_meal_plan_generation('ai_suggested')
        async def generate_ai_meal_plan(user_id: int):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            meal_plans_generated_total.labels(generation_type=generation_type).inc()
            duration = time.time() - start_time
            meal_plan_generation_duration_seconds.labels(
                generation_type=generation_type
            ).observe(duration)
            return result
        return wrapper
    return decorator


def track_cart_creation():
    """Track grocery cart creation."""
    carts_created_total.inc()


def track_cart_completion():
    """Track grocery cart completion."""
    carts_completed_total.inc()


def track_items_aggregated(count: int):
    """Track number of items aggregated in a cart."""
    items_aggregated_total.inc(count)


def track_new_user():
    """Track new user registration."""
    new_users_total.inc()


def track_feature_usage(feature: str):
    """
    Track feature usage.

    Features:
    - recipe_search
    - recipe_view
    - meal_plan_generation
    - meal_plan_view
    - cart_generation
    - cart_view
    - knuspr_integration
    """
    feature_usage_total.labels(feature=feature).inc()


def track_user_facing_error(endpoint: str, error_code: int):
    """Track user-facing errors."""
    user_facing_errors_total.labels(
        endpoint=endpoint,
        error_code=str(error_code)
    ).inc()


def track_error_by_type(error_type: str):
    """
    Track errors by type.

    Error types:
    - validation
    - auth
    - db
    - external
    - internal
    """
    error_by_type_total.labels(error_type=error_type).inc()


def track_knuspr_api_call(status: str, operation: str, duration: float):
    """
    Track Knuspr API call.

    Status: success, rate_limited, failed
    """
    knuspr_api_calls_total.labels(status=status).inc()
    knuspr_api_latency_seconds.labels(operation=operation).observe(duration)


def track_external_api_call(service: str, status: str):
    """Track external API calls."""
    external_api_calls_total.labels(service=service, status=status).inc()


def track_circuit_breaker_state_change(
    service: str,
    from_state: str,
    to_state: str
):
    """Track circuit breaker state changes."""
    circuit_breaker_state_changes_total.labels(
        service=service,
        from_state=from_state,
        to_state=to_state
    ).inc()


# ============================================================================
# PERIODIC METRICS UPDATES
# ============================================================================

async def update_unique_recipes_count(db: AsyncSession):
    """Update the unique recipes count gauge."""
    try:
        result = await db.execute(
            func.count(Recipe.id)
        )
        count = result.scalar()
        unique_recipes_count.set(count)
    except Exception as e:
        print(f"Error updating unique recipes count: {e}")


async def update_active_users_count(db: AsyncSession):
    """Update active users count for different periods."""
    try:
        # Daily active users
        daily_cutoff = datetime.utcnow() - timedelta(days=1)
        result = await db.execute(
            func.count(User.id).filter(User.last_login >= daily_cutoff)
        )
        daily_count = result.scalar()
        active_users_total.labels(period='daily').set(daily_count)

        # Weekly active users
        weekly_cutoff = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            func.count(User.id).filter(User.last_login >= weekly_cutoff)
        )
        weekly_count = result.scalar()
        active_users_total.labels(period='weekly').set(weekly_count)

        # Monthly active users
        monthly_cutoff = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(
            func.count(User.id).filter(User.last_login >= monthly_cutoff)
        )
        monthly_count = result.scalar()
        active_users_total.labels(period='monthly').set(monthly_count)

    except Exception as e:
        print(f"Error updating active users count: {e}")


async def update_user_retention_rates(db: AsyncSession):
    """Calculate and update user retention rates."""
    try:
        # 30-day retention
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)

        # Users who joined 30-60 days ago
        result = await db.execute(
            func.count(User.id).filter(
                User.created_at.between(sixty_days_ago, thirty_days_ago)
            )
        )
        cohort_size = result.scalar()

        if cohort_size > 0:
            # Users from that cohort still active
            result = await db.execute(
                func.count(User.id).filter(
                    User.created_at.between(sixty_days_ago, thirty_days_ago),
                    User.last_login >= thirty_days_ago
                )
            )
            retained_users = result.scalar()
            retention_rate = (retained_users / cohort_size) * 100
            user_retention_rate.labels(period='30d').set(retention_rate)

    except Exception as e:
        print(f"Error updating user retention rates: {e}")


async def update_knuspr_success_rate(db: AsyncSession):
    """Calculate and update Knuspr integration success rate."""
    try:
        # This would be calculated from actual API call logs
        # For now, using a simplified approach based on recent calls
        # In production, maintain a rolling window of success/failure counts

        # Get success/failure counts from the last hour
        # This is a placeholder - implement based on actual logging
        success_count = 950  # Example
        total_count = 1000   # Example

        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            knuspr_integration_success_rate.set(success_rate)

    except Exception as e:
        print(f"Error updating Knuspr success rate: {e}")


async def calculate_error_rate(db: AsyncSession):
    """Calculate overall error rate as percentage."""
    try:
        # This would be calculated from request logs
        # Placeholder implementation
        total_requests = 10000  # Example
        error_requests = 50      # Example

        if total_requests > 0:
            error_percentage = (error_requests / total_requests) * 100
            error_rate_percent.set(error_percentage)

    except Exception as e:
        print(f"Error calculating error rate: {e}")


# ============================================================================
# BACKGROUND TASK FOR PERIODIC UPDATES
# ============================================================================

async def update_all_business_metrics(db: AsyncSession):
    """
    Update all business metrics that require database queries.
    Should be called periodically (e.g., every 5 minutes).
    """
    await update_unique_recipes_count(db)
    await update_active_users_count(db)
    await update_user_retention_rates(db)
    await update_knuspr_success_rate(db)
    await calculate_error_rate(db)


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_business_metrics():
    """
    Initialize business metrics with default values.
    Called on application startup.
    """
    # Initialize gauges with zero values
    active_users_total.labels(period='daily').set(0)
    active_users_total.labels(period='weekly').set(0)
    active_users_total.labels(period='monthly').set(0)

    user_retention_rate.labels(period='30d').set(0)
    user_retention_rate.labels(period='60d').set(0)
    user_retention_rate.labels(period='90d').set(0)

    unique_recipes_count.set(0)
    knuspr_integration_success_rate.set(100.0)  # Optimistic start
    error_rate_percent.set(0)

    print("Business metrics initialized")
