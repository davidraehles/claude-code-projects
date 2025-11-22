"""
Workflow API Endpoints

Exposes end-to-end workflows that coordinate multiple agents and services.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.dependencies import get_database, get_current_user_id
from app.models.meal_plan import MealPlan
from app.agents.cart_optimizer import CartOptimizerAgent
from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry
from app.services.ingredient_mapper import IngredientMapper
from app.services.credential_manager import CredentialManager
from app.events.bus import get_event_bus

logger = logging.getLogger(__name__)

router = APIRouter()


class DeliveryPreferences(BaseModel):
    """Preferences for grocery delivery."""
    preferred_dates: Optional[List[date]] = Field(None, description="List of preferred delivery dates")
    preferred_time_slot: Optional[str] = Field("afternoon", description="Preferred time slot (morning, afternoon, evening)")
    budget_optimization: bool = Field(False, description="Optimize for budget (cheapest) vs convenience (earliest)")


class MealPlanToCartRequest(BaseModel):
    """Request to convert a meal plan to a grocery cart."""
    meal_plan_id: int = Field(..., description="ID of the meal plan to convert")
    delivery_preferences: Optional[DeliveryPreferences] = Field(None, description="Delivery preferences")


class WorkflowResponse(BaseModel):
    """Response for workflow initiation."""
    workflow_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None


@router.post("/meal-plan-with-groceries", response_model=WorkflowResponse)
async def create_cart_from_meal_plan(
    request: MealPlanToCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """
    Execute the "Meal Plan to Grocery Cart" workflow.

    1. Validates meal plan ownership and status
    2. Initializes CartOptimizerAgent with dependencies
    3. Converts meal plan ingredients to Knuspr cart
    4. Selects optimal delivery slot

    Returns the created cart details.
    """
    logger.info(f"Starting meal-plan-with-groceries workflow for user {user_id}, plan {request.meal_plan_id}")

    # 1. Validate meal plan
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == request.meal_plan_id,
        MealPlan.user_id == user_id
    ).first()

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal plan {request.meal_plan_id} not found"
        )

    # Check if meal plan has recipes/ingredients
    # Note: In a real scenario, we'd check if it's in a 'ready' state or has items

    # 2. Initialize dependencies
    # We need to get credentials for the user to initialize the Knuspr client
    credential_manager = CredentialManager()
    credentials = await credential_manager.get_credentials(db, user_id)

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knuspr credentials not found. Please configure Knuspr integration first."
        )

    email, password, country = credentials

    # Convert country string to Enum if needed
    try:
        country_enum = KnusprCountry(country)
    except ValueError:
        # Default to CZ if invalid
        logger.warning(f"Invalid country code '{country}', defaulting to CZ")
        country_enum = KnusprCountry.CZECH_REPUBLIC

    # Initialize services
    knuspr_client = KnusprMCPClient(
        login_email=email,
        login_password=password,
        country=country_enum
    )

    ingredient_mapper = IngredientMapper(knuspr_client)
    event_bus = get_event_bus()

    # Initialize agent
    agent = CartOptimizerAgent(
        knuspr_client=knuspr_client,
        ingredient_mapper=ingredient_mapper,
        db=db,
        event_bus=event_bus
    )

    # 3. Execute workflow
    try:
        # Convert Pydantic model to dict for the agent
        prefs_dict = request.delivery_preferences.model_dump() if request.delivery_preferences else {}

        # Run the agent logic
        # Note: In a production environment with long-running tasks,
        # this might be offloaded to a background worker (Celery/BullMQ).
        # For this phase, we'll run it inline but handle errors gracefully.

        result = await agent.create_cart_from_meal_plan(
            meal_plan_id=str(request.meal_plan_id),
            user_id=str(user_id),
            db=db,
            credential_manager=credential_manager,
            delivery_preferences=prefs_dict
        )

        return WorkflowResponse(
            workflow_id=f"mp-cart-{request.meal_plan_id}-{result.get('cart_id', 'unknown')}",
            status="success",
            message="Successfully created grocery cart from meal plan",
            result=result
        )

    except ValueError as e:
        logger.warning(f"Validation error in workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Runtime error in workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow failed: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the workflow"
        )
    finally:
        # Cleanup resources
        await knuspr_client.close()
