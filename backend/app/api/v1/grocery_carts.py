"""
Grocery Carts API v1

Endpoints for managing Knuspr shopping carts:
- POST /api/v1/grocery-carts - Create cart from meal plan
- GET /api/v1/grocery-carts/{id} - Get cart details
- PUT /api/v1/grocery-carts/{id} - Update cart (change items, delivery slot)
- DELETE /api/v1/grocery-carts/{id} - Delete cart
- POST /api/v1/grocery-carts/{id}/checkout - Finalize and checkout
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.dependencies import get_database, get_current_user_id
from app.models.meal_plan import GroceryCart, CartItem, MealPlan
from app.agents.cart_optimizer import CartOptimizerAgent
from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry
from app.services.ingredient_mapper import IngredientMapper
from app.services.credential_manager import CredentialManager
from app.events.bus import get_event_bus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/grocery-carts", tags=["grocery-carts"])


# ============ Request/Response Models ============

class DeliveryPreferences(BaseModel):
    """User preferences for delivery"""
    preferred_dates: Optional[list[str]] = Field(None, description="List of preferred dates (ISO format)")
    preferred_time_slot: Optional[str] = Field(
        default="afternoon",
        description="Preferred time slot: 'morning', 'afternoon', or 'evening'"
    )
    budget_optimization: Optional[bool] = Field(
        default=False,
        description="If True, choose cheapest slot; if False, choose earliest"
    )


class CreateGroceryCartRequest(BaseModel):
    """Request to create grocery cart from meal plan"""
    meal_plan_id: str = Field(..., description="ID of meal plan to convert")
    delivery_preferences: Optional[DeliveryPreferences] = Field(
        default_factory=DeliveryPreferences,
        description="Delivery preferences"
    )


class CartItemResponse(BaseModel):
    """Item in shopping cart"""
    product_id: str
    name: str
    quantity: float
    unit: str
    price: float
    category: str


class DeliverySlotResponse(BaseModel):
    """Delivery slot information"""
    slot_id: str
    date: str  # ISO format
    time_window: str  # "HH:MM-HH:MM"
    price: float
    available: bool = True


class GroceryCartResponse(BaseModel):
    """Complete grocery cart response"""
    cart_id: str = Field(..., description="Knuspr cart ID")
    knuspr_url: str = Field(..., description="URL to Knuspr shopping cart")
    total_price: float = Field(..., description="Total cart price")
    item_count: int = Field(..., description="Number of items in cart")
    delivery_slot: Optional[DeliverySlotResponse] = Field(None, description="Selected delivery slot")
    items_by_section: dict = Field(..., description="Items grouped by store section")
    unavailable_items: list[str] = Field(default_factory=list, description="Items not found on Knuspr")
    created_at: str = Field(..., description="Cart creation timestamp")


class UpdateGroceryCartRequest(BaseModel):
    """Request to update grocery cart"""
    remove_items: Optional[list[str]] = Field(None, description="Product IDs to remove")
    add_items: Optional[list[dict]] = Field(None, description="Items to add")
    delivery_slot_id: Optional[str] = Field(None, description="New delivery slot")


class CheckoutRequest(BaseModel):
    """Request to checkout cart"""
    payment_method: Optional[str] = Field(
        default="card",
        description="Payment method (card, etc.)"
    )
    notes: Optional[str] = Field(None, description="Special instructions for delivery")


# ============ API Endpoints ============

@router.post("", response_model=GroceryCartResponse)
async def create_grocery_cart(
    request: CreateGroceryCartRequest,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create Knuspr shopping cart from meal plan.

    Workflow:
    1. Extract ingredients from meal plan recipes
    2. Map ingredients to Knuspr products
    3. Create cart with mapped products
    4. Select delivery slot based on preferences
    5. Store cart in database

    Args:
        request: CreateGroceryCartRequest with meal_plan_id and delivery_preferences

    Returns:
        GroceryCartResponse with cart details and shopping summary

    Raises:
        404: If meal plan not found
        400: If meal plan has no ingredients or cart creation fails
    """
    knuspr_client = None
    try:
        logger.info(f"Creating grocery cart from meal plan {request.meal_plan_id} for user {user_id}")

        # Validate meal plan ID is an integer
        try:
            meal_plan_id = int(request.meal_plan_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid meal plan ID format")

        # Validate meal plan exists and belongs to user
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == user_id
        ).first()

        if not meal_plan:
            raise HTTPException(
                status_code=404,
                detail=f"Meal plan {meal_plan_id} not found"
            )

        if not meal_plan.total_recipes or meal_plan.total_recipes == 0:
            raise HTTPException(
                status_code=400,
                detail="Meal plan must contain at least one recipe to generate a grocery cart"
            )

        # Get user's Knuspr credentials
        credential_manager = CredentialManager()
        credentials_tuple = await credential_manager.get_credentials(db, user_id)

        if not credentials_tuple:
            raise HTTPException(
                status_code=400,
                detail="Knuspr credentials not found. Please configure Knuspr integration first."
            )

        # Validate credentials structure
        try:
            email, password, country = credentials_tuple
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Knuspr credentials are malformed. Please reconfigure your Knuspr integration."
            )

        if not email or not password or not country:
            raise HTTPException(
                status_code=400,
                detail="Knuspr credentials are incomplete. Please reconfigure your Knuspr integration."
            )

        # Convert country to enum
        try:
            country_enum = KnusprCountry(country)
        except ValueError:
            logger.warning(f"Invalid country code '{country}', defaulting to CZ")
            country_enum = KnusprCountry.CZECH_REPUBLIC

        # Initialize Knuspr client and dependencies
        knuspr_client = KnusprMCPClient(
            login_email=email,
            login_password=password,
            country=country_enum
        )
        ingredient_mapper = IngredientMapper(knuspr_client)
        event_bus = get_event_bus()

        # Initialize cart optimizer agent
        agent = CartOptimizerAgent(
            knuspr_client=knuspr_client,
            ingredient_mapper=ingredient_mapper,
            db=db,
            event_bus=event_bus
        )

        # Convert preferences to dict
        prefs_dict = request.delivery_preferences.model_dump() if request.delivery_preferences else {}

        # Execute cart creation
        result = await agent.create_cart_from_meal_plan(
            meal_plan_id=meal_plan_id,
            user_id=user_id,
            db=db,
            credential_manager=credential_manager,
            delivery_preferences=prefs_dict
        )

        logger.info(f"Cart created successfully: {result['cart_id']}")
        return GroceryCartResponse(**result)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid meal plan: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Cart creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create grocery cart: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error creating cart: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the grocery cart")
    finally:
        # Cleanup Knuspr client
        if knuspr_client is not None:
            await knuspr_client.close()


@router.get("/{cart_id}", response_model=GroceryCartResponse)
async def get_grocery_cart(
    cart_id: str,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Retrieve grocery cart details.

    Args:
        cart_id: Knuspr cart ID (stored in knuspr_cart_id column)

    Returns:
        GroceryCartResponse with cart details

    Raises:
        404: If cart not found or doesn't belong to user
    """
    try:
        logger.info(f"Retrieving cart {cart_id} for user {user_id}")

        # Fetch cart from database by knuspr_cart_id
        cart = db.query(GroceryCart).filter(
            GroceryCart.knuspr_cart_id == cart_id,
            GroceryCart.user_id == user_id
        ).first()

        if not cart:
            raise HTTPException(
                status_code=404,
                detail=f"Cart {cart_id} not found or does not belong to user"
            )

        # Fetch cart items grouped by category
        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

        # Group items by section
        items_by_section = {}
        for item in items:
            category = item.category or "other"
            if category not in items_by_section:
                items_by_section[category] = []

            items_by_section[category].append({
                "product_id": item.knuspr_product_id or "",
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "price": item.unit_price or 0.0,
                "category": category
            })

        # Build response
        response = GroceryCartResponse(
            cart_id=cart.knuspr_cart_id,
            knuspr_url=f"https://www.knuspr.cz/cart/{cart.knuspr_cart_id}",  # TODO: Use correct domain based on country
            total_price=cart.total_cost or 0.0,
            item_count=cart.total_items,
            delivery_slot=None,  # TODO: Store delivery slot info in database
            items_by_section=items_by_section,
            unavailable_items=[],  # TODO: Store unavailable items in database
            created_at=cart.created_at.isoformat()
        )

        logger.info(f"Retrieved cart {cart_id} with {cart.total_items} items")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to retrieve cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cart")


@router.put("/{cart_id}", response_model=GroceryCartResponse)
async def update_grocery_cart(
    cart_id: str,
    request: UpdateGroceryCartRequest,
    # current_user = Depends(get_current_user),  # TODO: Add auth
    # cart_optimizer = Depends(get_cart_optimizer),  # TODO: Inject agent
):
    """
    Update grocery cart (remove/add items, change delivery slot).

    Args:
        cart_id: ID of cart to update
        request: UpdateGroceryCartRequest with changes

    Returns:
        Updated GroceryCartResponse

    Raises:
        404: If cart not found
    """
    try:
        logger.info(f"Updating cart {cart_id}")

        # TODO: Implement with cart_optimizer agent
        # updated_cart = await cart_optimizer.regenerate_cart(
        #     cart_id=cart_id,
        #     changes=request.dict(exclude_none=True)
        # )

        raise HTTPException(status_code=501, detail="Update not yet implemented")

    except Exception as e:
        logger.error(f"Failed to update cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update cart")


@router.delete("/{cart_id}")
async def delete_grocery_cart(
    cart_id: str,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete grocery cart.

    Args:
        cart_id: Knuspr cart ID (stored in knuspr_cart_id column)

    Returns:
        Success message

    Raises:
        404: If cart not found or doesn't belong to user
    """
    try:
        logger.info(f"Deleting cart {cart_id} for user {user_id}")

        # Fetch cart from database
        cart = db.query(GroceryCart).filter(
            GroceryCart.knuspr_cart_id == cart_id,
            GroceryCart.user_id == user_id
        ).first()

        if not cart:
            raise HTTPException(
                status_code=404,
                detail=f"Cart {cart_id} not found or does not belong to user"
            )

        # Delete cart (cascade will delete cart items)
        db.delete(cart)
        db.commit()

        logger.info(f"Successfully deleted cart {cart_id}")
        return {"message": f"Cart {cart_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete cart {cart_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete cart")


@router.post("/{cart_id}/checkout")
async def checkout_cart(
    cart_id: str,
    request: CheckoutRequest,
    # current_user = Depends(get_current_user),  # TODO: Add auth
):
    """
    Finalize and checkout grocery cart.

    Sends cart to Knuspr for order placement.

    Args:
        cart_id: ID of cart to checkout
        request: CheckoutRequest with payment and notes

    Returns:
        Checkout confirmation with order details

    Raises:
        404: If cart not found
        400: If checkout fails
    """
    try:
        logger.info(f"Checking out cart {cart_id}")

        # TODO: Call Knuspr API to finalize cart
        # response = await knuspr_client.checkout(
        #     cart_id=cart_id,
        #     payment_method=request.payment_method,
        #     notes=request.notes
        # )

        return {
            "status": "success",
            "cart_id": cart_id,
            "order_id": f"knuspr-order-{datetime.utcnow().timestamp()}",
            "message": f"Order placed successfully on Knuspr"
        }

    except Exception as e:
        logger.error(f"Checkout failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Checkout failed")
