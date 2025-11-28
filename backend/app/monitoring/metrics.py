"""
Prometheus metrics for the Recipe & Meal Planning System.

Provides application-level metrics including:
- HTTP request metrics (latency, status codes, endpoints)
- Business metrics (recipes harvested, meal plans generated)
- Agent metrics (success rates, processing times)
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time


# Application info
app_info = Info('recipe_app', 'Recipe & Meal Planning Application')
app_info.info({
    'version': '1.0.0',
    'service': 'recipe-meal-planning-api'
})

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Recipe Metrics
recipes_harvested_total = Counter(
    'recipes_harvested_total',
    'Total recipes harvested',
    ['source_type', 'status']
)

recipes_harvest_duration_seconds = Histogram(
    'recipes_harvest_duration_seconds',
    'Recipe harvest duration',
    ['source_type'],
    buckets=(1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0)
)

recipes_duplicates_detected_total = Counter(
    'recipes_duplicates_detected_total',
    'Total duplicate recipes detected'
)

recipes_total = Gauge(
    'recipes_total',
    'Total number of recipes in database',
    ['user_id']
)

# Ingredient Intelligence Metrics
ingredients_classified_total = Counter(
    'ingredients_classified_total',
    'Total ingredients classified',
    ['found']
)

substitutions_requested_total = Counter(
    'substitutions_requested_total',
    'Total substitution requests',
    ['has_dietary_restrictions']
)

allergen_checks_total = Counter(
    'allergen_checks_total',
    'Total allergen checks performed',
    ['allergens_found']
)

# Event Bus Metrics
events_published_total = Counter(
    'events_published_total',
    'Total events published to event bus',
    ['event_type']
)

events_processed_total = Counter(
    'events_processed_total',
    'Total events processed by handlers',
    ['event_type', 'status']
)

event_processing_duration_seconds = Histogram(
    'event_processing_duration_seconds',
    'Event processing duration',
    ['event_type'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Agent Metrics
agent_operations_total = Counter(
    'agent_operations_total',
    'Total agent operations',
    ['agent', 'operation', 'status']
)

agent_operation_duration_seconds = Histogram(
    'agent_operation_duration_seconds',
    'Agent operation duration',
    ['agent', 'operation'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Cart Optimizer Metrics
cart_creation_total = Counter(
    'cart_creation_total',
    'Total number of cart creation attempts',
    ['status']
)

cart_creation_duration_seconds = Histogram(
    'cart_creation_duration_seconds',
    'Time taken to create a cart',
    buckets=(1.0, 2.5, 5.0, 10.0, 15.0, 30.0, 60.0)
)

cart_value_eur = Histogram(
    'cart_value_eur',
    'Value of the created cart in EUR',
    buckets=(10.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0, 300.0, 500.0)
)

cart_items_count = Histogram(
    'cart_items_count',
    'Number of items in the created cart',
    buckets=(5, 10, 15, 20, 30, 40, 50, 75, 100)
)

# Database Metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# Redis Metrics
redis_commands_total = Counter(
    'redis_commands_total',
    'Total Redis commands',
    ['command', 'status']
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Background Task Metrics
background_tasks_total = Counter(
    'background_tasks_total',
    'Total background tasks',
    ['task_type', 'status']
)

background_task_duration_seconds = Histogram(
    'background_task_duration_seconds',
    'Background task duration',
    ['task_type'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)


# Helper functions for common metric patterns

def track_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """
    Track an HTTP request.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_recipe_harvest(source_type: str, status: str, duration: float):
    """
    Track a recipe harvest operation.

    Args:
        source_type: Type of source (html, api, rss)
        status: Operation status (success, failure)
        duration: Harvest duration in seconds
    """
    recipes_harvested_total.labels(source_type=source_type, status=status).inc()
    recipes_harvest_duration_seconds.labels(source_type=source_type).observe(duration)


def track_event(event_type: str, status: str = 'published', duration: float = None):
    """
    Track an event bus operation.

    Args:
        event_type: Type of event
        status: Event status (published, processed, failed)
        duration: Processing duration in seconds (optional)
    """
    if status == 'published':
        events_published_total.labels(event_type=event_type).inc()
    else:
        events_processed_total.labels(event_type=event_type, status=status).inc()

    if duration is not None:
        event_processing_duration_seconds.labels(event_type=event_type).observe(duration)


def track_agent_operation(agent: str, operation: str, status: str, duration: float):
    """
    Track an agent operation.

    Args:
        agent: Agent name
        operation: Operation name
        status: Operation status (success, failure)
        duration: Operation duration in seconds
    """
    agent_operations_total.labels(agent=agent, operation=operation, status=status).inc()
    agent_operation_duration_seconds.labels(agent=agent, operation=operation).observe(duration)
