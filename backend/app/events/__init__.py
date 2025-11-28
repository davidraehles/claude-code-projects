"""
Event definitions for the Recipe & Meal Planning System.

Defines event types, schemas, and event bus interfaces for agent communication.
"""

from enum import Enum
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid


class EventType(str, Enum):
    """Event types for the system."""

    # Recipe Harvester Events
    RECIPE_HARVEST_REQUESTED = "recipe.harvest.requested"
    RECIPE_HARVEST_STARTED = "recipe.harvest.started"
    RECIPE_HARVEST_COMPLETED = "recipe.harvest.completed"
    RECIPE_HARVEST_FAILED = "recipe.harvest.failed"
    RECIPE_SAVED = "recipe.saved"
    RECIPE_DUPLICATE_DETECTED = "recipe.duplicate.detected"

    # Ingredient Intelligence Events
    INGREDIENT_CLASSIFICATION_REQUESTED = "ingredient.classification.requested"
    INGREDIENT_CLASSIFICATION_COMPLETED = "ingredient.classification.completed"
    INGREDIENT_SUBSTITUTION_REQUESTED = "ingredient.substitution.requested"
    INGREDIENT_SUBSTITUTION_COMPLETED = "ingredient.substitution.completed"

    # Meal Planning Events
    MEAL_PLAN_REQUESTED = "meal_plan.requested"
    MEAL_PLAN_GENERATED = "meal_plan.generated"
    MEAL_PLAN_FAILED = "meal_plan.failed"

    # Grocery Cart Events
    CART_CREATION_REQUESTED = "cart.creation.requested"
    CART_CREATED = "cart.created"
    CART_CREATION_FAILED = "cart.creation.failed"
    CART_KNUSPR_SYNC_REQUESTED = "cart.knuspr.sync.requested"
    CART_KNUSPR_SYNCED = "cart.knuspr.synced"

    # System Events
    AGENT_ERROR = "agent.error"
    DEAD_LETTER = "system.dead_letter"


class Event(BaseModel):
    """
    Base event model for all events in the system.

    Attributes:
        event_id: Unique identifier for this event
        event_type: Type of event (from EventType enum)
        correlation_id: ID to correlate related events across agents
        timestamp: When the event was created
        user_id: ID of the user who triggered the event
        payload: Event-specific data
        metadata: Additional metadata (e.g., source agent, retry count)
    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = None
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class RecipeHarvestRequestedEvent(BaseModel):
    """Payload for RECIPE_HARVEST_REQUESTED event."""

    url: str
    source_type: str  # 'html', 'api', or 'rss'
    user_id: int


class RecipeHarvestCompletedEvent(BaseModel):
    """Payload for RECIPE_HARVEST_COMPLETED event."""

    recipe_id: int
    title: str
    source_url: str
    is_duplicate: bool = False
    duplicate_of_id: Optional[int] = None


class RecipeHarvestFailedEvent(BaseModel):
    """Payload for RECIPE_HARVEST_FAILED event."""

    url: str
    error_message: str
    error_type: str  # 'network', 'parsing', 'validation', 'storage'
    retry_count: int = 0


class IngredientClassificationRequestedEvent(BaseModel):
    """Payload for INGREDIENT_CLASSIFICATION_REQUESTED event."""

    recipe_id: int
    ingredients: list[str]


class MealPlanRequestedEvent(BaseModel):
    """Payload for MEAL_PLAN_REQUESTED event."""

    user_id: int
    num_days: int
    num_people: int
    dietary_restrictions: list[str] = []
    excluded_ingredients: list[str] = []
    target_calories_per_day: Optional[int] = None


class AgentErrorEvent(BaseModel):
    """Payload for AGENT_ERROR event."""

    agent_name: str
    error_message: str
    error_type: str
    original_event_id: Optional[str] = None
    stack_trace: Optional[str] = None


# Export all event types and models
__all__ = [
    "EventType",
    "Event",
    "RecipeHarvestRequestedEvent",
    "RecipeHarvestCompletedEvent",
    "RecipeHarvestFailedEvent",
    "IngredientClassificationRequestedEvent",
    "MealPlanRequestedEvent",
    "AgentErrorEvent",
]
