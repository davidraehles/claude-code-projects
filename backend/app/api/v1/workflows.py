"""
Workflow API Endpoints

Exposes end-to-end workflows that coordinate multiple agents and services.
"""

import logging
from typing import Optional, List, Dict, Any, NamedTuple
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.dependencies import get_database, get_current_user_id
from app.models.meal_plan import MealPlan, GroceryCart, CartItem
from app.models.recipe import Recipe
from app.agents.cart_optimizer import CartOptimizerAgent
from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry
from app.services.ingredient_mapper import IngredientMapper
from app.services.credential_manager import CredentialManager
from app.services.grocery_aggregator import GroceryAggregator
from app.schemas.grocery_cart import (
    CreateCartFromMealPlanRequest,
    CartResponse,
    CartItemSchema,
    RecipeSource,
    FillKnusprCartRequest,
    FillKnusprCartResponse,
    MatchedItem,
)
from app.events.bus import get_event_bus
from app.utils.rate_limit import WorkflowRateLimiter

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize rate limiter for workflow endpoints
# Prevents abuse of expensive MCP operations
rate_limiter = WorkflowRateLimiter()


class KnusprCredentials(NamedTuple):
    """Structured container for Knuspr credentials."""
    email: str
    password: str
    country: str


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


@router.post("/carts/from-meal-plan", response_model=CartResponse)
async def create_cart_from_meal_plan_simple(
    request: CreateCartFromMealPlanRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_database),
):
    """
    Create a grocery cart from a meal plan (simplified workflow).

    This endpoint:
    1. Validates meal plan ownership
    2. Aggregates ingredients from all recipes in the meal plan
    3. Creates a GroceryCart and CartItem records
    4. Stores recipe_ids for source tracking

    Args:
        request: CreateCartFromMealPlanRequest with meal_plan_id and aggregate_duplicates
        user_id: Current authenticated user ID
        db: Database session

    Returns:
        CartResponse with cart_id, items, and unmatched_ingredients

    Raises:
        404: Meal plan not found
        401: Unauthorized (meal plan doesn't belong to user)
        500: Server error during processing
    """
    logger.info(
        f"Creating cart from meal plan {request.meal_plan_id} for user {user_id}"
    )

    # Validate meal plan exists and belongs to user
    meal_plan = (
        db.query(MealPlan)
        .filter(MealPlan.id == request.meal_plan_id, MealPlan.user_id == user_id)
        .first()
    )

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal plan {request.meal_plan_id} not found",
        )

    try:
        # Initialize GroceryAggregator service
        aggregator = GroceryAggregator(db)

        # Get aggregated ingredients using synchronous method
        aggregated_ingredients = aggregator.aggregate_from_meal_plan_sync(
            request.meal_plan_id
        )

        # Pre-fetch all recipes involved to avoid N+1 queries
        all_recipe_ids = set()
        for agg_item in aggregated_ingredients:
            all_recipe_ids.update(agg_item.recipe_ids)

        recipes_dict = {}
        if all_recipe_ids:
            recipes = db.query(Recipe).filter(Recipe.id.in_(all_recipe_ids)).all()
            recipes_dict = {r.id: r for r in recipes}

        # Create grocery cart
        cart_name = f"Grocery List from {meal_plan.name}"
        cart = GroceryCart(
            user_id=user_id,
            meal_plan_id=meal_plan.id,
            name=cart_name,
            status="active",
            total_items=len(aggregated_ingredients),
            total_cost=None,  # Will be calculated when Knuspr prices are added
        )
        db.add(cart)
        db.flush()  # Get cart ID without committing

        # Create cart items
        cart_items = []
        unmatched_ingredients = []

        for agg_item in aggregated_ingredients:
            try:
                # Get recipe names for source tracking (using pre-fetched recipes)
                recipe_sources = []
                for recipe_id in agg_item.recipe_ids:
                    recipe = recipes_dict.get(recipe_id)
                    if recipe:
                        recipe_sources.append(
                            RecipeSource(recipe_id=recipe.id, recipe_name=recipe.title)
                        )

                cart_item = CartItem(
                    cart_id=cart.id,
                    name=agg_item.name,
                    quantity=agg_item.quantity,
                    unit=agg_item.unit,
                    category=agg_item.category,
                    recipe_ids=agg_item.recipe_ids,  # Store as JSON
                    is_purchased=False,
                )
                db.add(cart_item)
                cart_items.append(
                    CartItemSchema(
                        id=None,  # Will be set after commit
                        name=agg_item.name,
                        quantity=agg_item.quantity,
                        unit=agg_item.unit,
                        category=agg_item.category,
                        recipe_sources=recipe_sources,
                        is_purchased=False,
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Failed to create cart item for {agg_item.name}: {str(e)}"
                )
                unmatched_ingredients.append(agg_item.name)

        # Commit transaction
        db.commit()

        # Refresh cart to get final state
        db.refresh(cart)

        logger.info(
            f"Successfully created cart {cart.id} with {len(cart_items)} items"
        )

        return CartResponse(
            cart_id=cart.id,
            cart_name=cart.name,
            total_items=cart.total_items,
            items=cart_items,
            unmatched_ingredients=unmatched_ingredients,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error creating cart: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create grocery cart from meal plan",
        )


@router.post("/meal-plan-with-groceries", response_model=WorkflowResponse)
async def create_cart_from_meal_plan_with_knuspr(
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
    # Rate limit check (prevent abuse of expensive MCP operations)
    is_allowed, limit_info = rate_limiter.check_limit(user_id)
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit_info['limit']} requests per 5 minutes. Reset at {limit_info['reset_at']}"
        )

    logger.info(f"Starting meal-plan-with-groceries workflow for user {user_id}, plan {request.meal_plan_id}")

    # 1. Validate meal plan (optimized with eager loading)
    meal_plan = (
        db.query(MealPlan)
        .options(
            selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
        )
        .filter(
            MealPlan.id == request.meal_plan_id,
            MealPlan.user_id == user_id
        )
        .first()
    )

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal plan {request.meal_plan_id} not found"
        )

    # Validate meal plan has recipes
    if not meal_plan.total_recipes or meal_plan.total_recipes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meal plan must contain at least one recipe to generate a grocery cart"
        )

    # 2. Initialize dependencies
    # We need to get credentials for the user to initialize the Knuspr client
    credential_manager = CredentialManager()
    credentials_tuple = await credential_manager.get_credentials(db, user_id)

    if not credentials_tuple:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knuspr credentials not found. Please configure Knuspr integration first."
        )

    # Use named tuple for structured access to credentials
    try:
        credentials = KnusprCredentials(
            email=credentials_tuple[0],
            password=credentials_tuple[1],
            country=credentials_tuple[2]
        )
    except (IndexError, TypeError) as e:
        logger.error(f"Invalid credentials structure for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knuspr credentials are malformed. Please reconfigure your Knuspr integration."
        )

    # Validate credential values are not empty
    if not credentials.email or not credentials.password or not credentials.country:
        logger.error(f"Invalid credentials for user {user_id}: missing email, password, or country")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knuspr credentials are incomplete. Please reconfigure your Knuspr integration."
        )

    # Convert country string to Enum if needed
    try:
        country_enum = KnusprCountry(credentials.country)
    except ValueError:
        # Default to CZ if invalid
        logger.warning(f"Invalid country code '{credentials.country}', defaulting to CZ")
        country_enum = KnusprCountry.CZECH_REPUBLIC

    # Initialize MCP client to None for cleanup in finally block
    knuspr_client = None

    # Initialize services
    knuspr_client = KnusprMCPClient(
        login_email=credentials.email,
        login_password=credentials.password,
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
            meal_plan_id=request.meal_plan_id,  # Pass as int, not string
            user_id=user_id,  # Pass as int, not string
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
        if knuspr_client is not None:
            await knuspr_client.close()


@router.post("/carts/{cart_id}/fill-knuspr", response_model=FillKnusprCartResponse)
async def fill_knuspr_cart(
    cart_id: int,
    request: FillKnusprCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_database),
):
    """
    Fill a Knuspr cart with items from an existing grocery cart.

    This endpoint:
    1. Validates cart ownership and retrieves cart items
    2. Authenticates with Knuspr using provided credentials
    3. Uses KnusprMCPClient.add_items_batch() to match and add items
    4. Tracks progress: current_item, total_items, success_count, failure_count
    5. Updates database with Knuspr cart URL and product mappings
    6. Returns detailed results with matched/unmatched items

    Args:
        cart_id: ID of the grocery cart to fill
        request: FillKnusprCartRequest with credentials and match preferences
        user_id: Current authenticated user ID
        db: Database session

    Returns:
        FillKnusprCartResponse with success status, matched items, and Knuspr cart URL

    Raises:
        404: Cart not found
        401: Unauthorized (cart doesn't belong to user) or authentication failed
        400: Invalid request (no items in cart, invalid credentials)
        502: Knuspr API errors
        500: Server error during processing
    """
    logger.info(f"Filling Knuspr cart for cart_id={cart_id}, user_id={user_id}")

    # Rate limit check
    is_allowed, limit_info = rate_limiter.check_limit(user_id)
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit_info['limit']} requests per 5 minutes. Reset at {limit_info['reset_at']}"
        )

    # 1. Validate cart exists and belongs to user (optimized with eager loading)
    cart = (
        db.query(GroceryCart)
        .options(selectinload(GroceryCart.items))
        .filter(GroceryCart.id == cart_id, GroceryCart.user_id == user_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart {cart_id} not found or does not belong to user"
        )

    # 2. Use already-loaded cart items (no additional query)
    cart_items = cart.items

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart has no items to add to Knuspr"
        )

    logger.info(f"Found {len(cart_items)} items in cart {cart_id}")

    # 3. Initialize Knuspr client with provided credentials
    try:
        country_enum = KnusprCountry(request.credentials.country)
    except ValueError:
        logger.warning(f"Invalid country code: {request.credentials.country}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid country code: {request.credentials.country}. Must be one of: cz, de, at"
        )

    knuspr_client = None
    try:
        knuspr_client = KnusprMCPClient(
            login_email=request.credentials.email,
            login_password=request.credentials.password,
            country=country_enum
        )

        # 4. Authenticate with Knuspr
        logger.info("Authenticating with Knuspr")
        auth_success = await knuspr_client.authenticate()
        if not auth_success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Knuspr. Please check your credentials."
            )

        logger.info("Knuspr authentication successful")

        # 5. Prepare items for batch operation
        items_to_add = []
        for item in cart_items:
            items_to_add.append({
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category
            })

        # 6. Execute batch add operation
        logger.info(f"Starting batch add operation for {len(items_to_add)} items")
        batch_result = await knuspr_client.add_items_batch(
            items=items_to_add,
            batch_size=10,
            max_retries=3
        )

        # 7. Process results and update database
        matched_products = []
        unmatched_items = []

        # Process succeeded items
        for result_item in batch_result.succeeded_items:
            matched_products.append(MatchedItem(
                name=result_item.name,
                knuspr_product_id=result_item.knuspr_product_id or "",
                knuspr_product_name=result_item.knuspr_product_name or "",
                quantity=result_item.quantity,
                unit=result_item.unit,
                confidence=result_item.match_confidence
            ))

            # Update database cart item with Knuspr product ID
            db_item = next((item for item in cart_items if item.name == result_item.name), None)
            if db_item:
                db_item.knuspr_product_id = result_item.knuspr_product_id
                db_item.knuspr_url = f"{knuspr_client.get_domain()}/product/{result_item.knuspr_product_id}"

        # Process partial matches
        for result_item in batch_result.partial_matches:
            matched_products.append(MatchedItem(
                name=result_item.name,
                knuspr_product_id=result_item.knuspr_product_id or "",
                knuspr_product_name=result_item.knuspr_product_name or "",
                quantity=result_item.quantity,
                unit=result_item.unit,
                confidence=result_item.match_confidence
            ))

            # Update database cart item
            db_item = next((item for item in cart_items if item.name == result_item.name), None)
            if db_item:
                db_item.knuspr_product_id = result_item.knuspr_product_id
                db_item.knuspr_url = f"{knuspr_client.get_domain()}/product/{result_item.knuspr_product_id}"

        # Process failed items
        for result_item in batch_result.failed_items:
            unmatched_items.append(result_item.name)
            logger.warning(f"Failed to match item: {result_item.name} - {result_item.error_message}")

        # 8. Update cart with Knuspr cart ID and sync timestamp
        if batch_result.cart_id:
            cart.knuspr_cart_id = batch_result.cart_id
            cart.knuspr_synced_at = datetime.utcnow()
            logger.info(f"Updated cart with Knuspr cart ID: {batch_result.cart_id}")

        # Commit database changes
        db.commit()
        db.refresh(cart)

        # 9. Calculate progress
        total_items = len(cart_items)
        matched_count = batch_result.success_count + batch_result.partial_count
        progress = int((matched_count / total_items * 100)) if total_items > 0 else 0

        # 10. Build success message
        message = f"Successfully added {batch_result.success_count} items to Knuspr cart"
        if batch_result.partial_count > 0:
            message += f" ({batch_result.partial_count} partial matches)"
        if batch_result.failure_count > 0:
            message += f". Failed to match {batch_result.failure_count} items."

        logger.info(
            f"Fill operation complete: {batch_result.success_count} succeeded, "
            f"{batch_result.partial_count} partial, {batch_result.failure_count} failed"
        )

        return FillKnusprCartResponse(
            success=batch_result.success_count > 0,
            cart_id=cart.id,
            knuspr_cart_url=batch_result.cart_url,
            matched_items=batch_result.success_count,
            partial_matches=batch_result.partial_count,
            unmatched_items=unmatched_items,
            matched_products=matched_products,
            progress=progress,
            message=message
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Knuspr API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Knuspr API error: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error filling Knuspr cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while filling the Knuspr cart"
        )
    finally:
        # Cleanup resources
        if knuspr_client is not None:
            await knuspr_client.close()
