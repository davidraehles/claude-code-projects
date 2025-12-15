"""Compatibility router for legacy /api/v1/carts paths

Provides lightweight list and get endpoints for carts to maintain
backwards compatibility with tests and clients that expect
`/api/v1/carts` rather than `/api/v1/grocery-carts`.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_database, get_current_user_id
from app.models.meal_plan import GroceryCart

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/carts", tags=["carts-compat"])


class CartListItem(BaseModel):
    cart_id: str
    total_price: float
    item_count: int
    created_at: str
    knuspr_url: str


@router.get("", response_model=List[CartListItem])
async def list_carts(db=Depends(get_database), user_id: int = Depends(get_current_user_id)):
    try:
        carts = db.query(GroceryCart).filter(GroceryCart.user_id == user_id).all()
        results = [
            CartListItem(
                cart_id=c.knuspr_cart_id,
                total_price=c.total_cost or 0.0,
                item_count=c.total_items,
                created_at=c.created_at.isoformat(),
                knuspr_url=f"/cart/{c.knuspr_cart_id}",
            )
            for c in carts
        ]
        return results
    except Exception as e:
        logger.exception("Failed to list carts: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list carts")


@router.get("/{cart_id}", response_model=CartListItem)
async def get_cart(cart_id: str, db=Depends(get_database), user_id: int = Depends(get_current_user_id)):
    try:
        cart = db.query(GroceryCart).filter(
            GroceryCart.knuspr_cart_id == cart_id,
            GroceryCart.user_id == user_id,
        ).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        return CartListItem(
            cart_id=cart.knuspr_cart_id,
            total_price=cart.total_cost or 0.0,
            item_count=cart.total_items,
            created_at=cart.created_at.isoformat(),
            knuspr_url=f"/cart/{cart.knuspr_cart_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get cart %s: %s", cart_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve cart")
