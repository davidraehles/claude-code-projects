"""
Meal Plan API endpoints.

Provides REST API for meal plan generation, management, and grocery cart operations.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel, Field

from app.api.dependencies import get_database, get_current_user_id
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.agents.meal_architect import MealArchitectAgent


router = APIRouter()


# Pydantic schemas
class MealPlanCreateRequest(BaseModel):
    """Schema for creating a meal plan."""

    start_date: date = Field(..., description="Start date of the meal plan")
    num_days: int = Field(..., ge=1, le=30, description="Number of days (1-30)")
    num_people: int = Field(2, ge=1, le=10, description="Number of people (1-10)")
    dietary_restrictions: Optional[List[str]] = Field(
        None, description="Dietary restrictions"
    )
    excluded_ingredients: Optional[List[str]] = Field(
        None, description="Excluded ingredients"
    )
    target_calories_per_day: Optional[int] = Field(
        None, ge=1000, le=5000, description="Target calories per day"
    )
    target_budget: Optional[float] = Field(
        None, ge=0, description="Target budget in EUR"
    )
    preferred_cuisines: Optional[List[str]] = Field(
        None, description="Preferred cuisines"
    )
    meals_per_day: int = Field(3, ge=1, le=5, description="Meals per day (1-5)")

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-11-18",
                "num_days": 7,
                "num_people": 2,
                "dietary_restrictions": ["vegetarian"],
                "target_calories_per_day": 2000,
                "target_budget": 50.0,
                "meals_per_day": 3,
            }
        }


class MealPlanResponse(BaseModel):
    """Schema for meal plan response."""

    id: int
    user_id: int
    name: str
    description: Optional[str]
    start_date: str
    end_date: str
    num_days: int
    num_people: int
    dietary_restrictions: Optional[List[str]]
    target_calories_per_day: Optional[int]
    target_budget: Optional[float]
    total_recipes: int
    total_calories: Optional[int]
    total_cost: Optional[float]
    status: str
    created_at: str

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    """Schema for a single meal."""

    meal_type: str
    recipe_id: int
    recipe_name: str
    servings: int
    calories: Optional[int]
    cost: Optional[float]


class DayResponse(BaseModel):
    """Schema for a day in the meal plan."""

    day_number: int
    date: Optional[str]
    meals: List[MealResponse]


class MealPlanDetailResponse(BaseModel):
    """Schema for detailed meal plan response."""

    meal_plan: MealPlanResponse
    days: List[DayResponse]
    statistics: dict


class GroceryCartResponse(BaseModel):
    """Schema for grocery cart response."""

    id: int
    name: str
    total_items: int
    total_cost: Optional[float]
    status: str
    created_at: str

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    """Schema for cart item response."""

    id: int
    name: str
    quantity: float
    unit: str
    category: Optional[str]
    total_price: Optional[float]
    is_purchased: bool

    class Config:
        from_attributes = True


# Meal Plan Endpoints


@router.post("", response_model=MealPlanResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_meal_plan(
    request: MealPlanCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new meal plan.

    This endpoint generates an optimized meal plan using the Z3 constraint solver.
    Generation happens in the foreground for MVP (async in production).

    Args:
        request: Meal plan creation request
        background_tasks: FastAPI background tasks
        db: Database session
        user_id: Current user ID

    Returns:
        Created meal plan
    """
    agent = MealArchitectAgent(db)

    try:
        meal_plan = agent.generate_meal_plan(
            user_id=user_id,
            start_date=request.start_date,
            num_days=request.num_days,
            num_people=request.num_people,
            dietary_restrictions=request.dietary_restrictions,
            excluded_ingredients=request.excluded_ingredients,
            target_calories_per_day=request.target_calories_per_day,
            target_budget=request.target_budget,
            preferred_cuisines=request.preferred_cuisines,
            meals_per_day=request.meals_per_day,
        )

        return MealPlanResponse(
            id=meal_plan.id,
            user_id=meal_plan.user_id,
            name=meal_plan.name,
            description=meal_plan.description,
            start_date=meal_plan.start_date.isoformat(),
            end_date=meal_plan.end_date.isoformat(),
            num_days=meal_plan.num_days,
            num_people=meal_plan.num_people,
            dietary_restrictions=meal_plan.dietary_restrictions,
            target_calories_per_day=meal_plan.target_calories_per_day,
            target_budget=meal_plan.target_budget,
            total_recipes=meal_plan.total_recipes,
            total_calories=meal_plan.total_calories,
            total_cost=meal_plan.total_cost,
            status=meal_plan.status,
            created_at=meal_plan.created_at.isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate meal plan: {str(e)}",
        )


@router.get("", response_model=List[MealPlanResponse])
async def list_meal_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    List user's meal plans.

    Args:
        skip: Number to skip (pagination)
        limit: Maximum number to return
        status_filter: Optional status filter
        db: Database session
        user_id: Current user ID

    Returns:
        List of meal plans
    """
    query = db.query(MealPlan).filter(MealPlan.user_id == user_id)

    if status_filter:
        query = query.filter(MealPlan.status == status_filter)

    meal_plans = (
        query.order_by(MealPlan.created_at.desc()).offset(skip).limit(limit).all()
    )

    return [
        MealPlanResponse(
            id=mp.id,
            user_id=mp.user_id,
            name=mp.name,
            description=mp.description,
            start_date=mp.start_date.isoformat(),
            end_date=mp.end_date.isoformat(),
            num_days=mp.num_days,
            num_people=mp.num_people,
            dietary_restrictions=mp.dietary_restrictions,
            target_calories_per_day=mp.target_calories_per_day,
            target_budget=mp.target_budget,
            total_recipes=mp.total_recipes,
            total_calories=mp.total_calories,
            total_cost=mp.total_cost,
            status=mp.status,
            created_at=mp.created_at.isoformat(),
        )
        for mp in meal_plans
    ]


@router.get("/{meal_plan_id}", response_model=MealPlanDetailResponse)
async def get_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get detailed meal plan.

    Args:
        meal_plan_id: Meal plan ID
        db: Database session
        user_id: Current user ID

    Returns:
        Detailed meal plan with all meals
    """
    # Optimized query with eager loading to avoid N+1 queries
    meal_plan = (
        db.query(MealPlan)
        .options(
            selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
        )
        .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
        .first()
    )

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal plan {meal_plan_id} not found",
        )

    agent = MealArchitectAgent(db)
    summary = agent.get_meal_plan_summary(meal_plan_id)

    return MealPlanDetailResponse(
        meal_plan=MealPlanResponse(
            id=meal_plan.id,
            user_id=meal_plan.user_id,
            name=meal_plan.name,
            description=meal_plan.description,
            start_date=meal_plan.start_date.isoformat(),
            end_date=meal_plan.end_date.isoformat(),
            num_days=meal_plan.num_days,
            num_people=meal_plan.num_people,
            dietary_restrictions=meal_plan.dietary_restrictions,
            target_calories_per_day=meal_plan.target_calories_per_day,
            target_budget=meal_plan.target_budget,
            total_recipes=meal_plan.total_recipes,
            total_calories=meal_plan.total_calories,
            total_cost=meal_plan.total_cost,
            status=meal_plan.status,
            created_at=meal_plan.created_at.isoformat(),
        ),
        days=[
            DayResponse(
                day_number=day["day_number"],
                date=day["date"],
                meals=[MealResponse(**meal) for meal in day["meals"]],
            )
            for day in summary["days"]
        ],
        statistics=summary["statistics"],
    )


@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a meal plan.

    Args:
        meal_plan_id: Meal plan ID
        db: Database session
        user_id: Current user ID
    """
    meal_plan = (
        db.query(MealPlan)
        .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
        .first()
    )

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal plan {meal_plan_id} not found",
        )

    db.delete(meal_plan)
    db.commit()


# Grocery Cart Endpoints (simplified for MVP)


@router.post("/{meal_plan_id}/grocery-cart", response_model=GroceryCartResponse)
async def generate_grocery_cart(
    meal_plan_id: int,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Generate grocery cart from meal plan.

    Args:
        meal_plan_id: Meal plan ID
        db: Database session
        user_id: Current user ID

    Returns:
        Created grocery cart
    """
    # Optimized query with eager loading to avoid N+1 queries
    meal_plan = (
        db.query(MealPlan)
        .options(
            selectinload(MealPlan.recipes).selectinload(MealPlanRecipe.recipe)
        )
        .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
        .first()
    )

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal plan {meal_plan_id} not found",
        )

    # Create grocery cart
    cart = GroceryCart(
        user_id=user_id,
        meal_plan_id=meal_plan_id,
        name=f"Groceries for {meal_plan.name}",
        status="active",
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Use already-loaded recipes from meal plan (no additional query)
    meal_plan_recipes = meal_plan.recipes

    # Aggregate ingredients
    ingredient_quantities = {}

    for mpr in meal_plan_recipes:
        if not mpr.recipe or not mpr.recipe.ingredients:
            continue

        for ingredient_str in mpr.recipe.ingredients:
            # Simple aggregation (in production, parse quantities properly)
            if ingredient_str not in ingredient_quantities:
                ingredient_quantities[ingredient_str] = {
                    "quantity": 1.0,
                    "unit": "item",
                    "recipe_ids": [],
                }

            ingredient_quantities[ingredient_str]["recipe_ids"].append(mpr.recipe_id)

    # Create cart items
    for ingredient_name, data in ingredient_quantities.items():
        cart_item = CartItem(
            cart_id=cart.id,
            name=ingredient_name,
            quantity=data["quantity"],
            unit=data["unit"],
            recipe_ids=data["recipe_ids"],
        )
        db.add(cart_item)

    cart.total_items = len(ingredient_quantities)
    db.commit()
    db.refresh(cart)

    return GroceryCartResponse(
        id=cart.id,
        name=cart.name,
        total_items=cart.total_items,
        total_cost=cart.total_cost,
        status=cart.status,
        created_at=cart.created_at.isoformat(),
    )
