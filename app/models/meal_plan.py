"""
SQLAlchemy ORM models for Meal Planning System.

Defines database schema for meal plans, recipes, and grocery carts.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Integer,
    Float,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user import JSONType


class MealPlan(Base):
    """
    Meal plan model for multi-day meal planning.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Meal plan name
        description: Optional description
        start_date: Start date of the plan
        end_date: End date of the plan
        num_people: Number of people to plan for
        dietary_restrictions: JSON list of dietary restrictions
        excluded_ingredients: JSON list of excluded ingredients
        target_calories_per_day: Target calories per day
        target_budget: Target budget in EUR
        preferred_cuisines: JSON list of preferred cuisines
        total_recipes: Total number of recipes in plan
        total_calories: Total calories across all meals
        total_cost: Total estimated cost
        optimization_score: Z3 solver optimization score
        status: Status (draft, generating, ready, active, completed)
        generation_time_seconds: Time taken to generate plan
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
    """

    __tablename__ = "meal_plans"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    num_people = Column(Integer, nullable=False, default=2)

    # Constraints and preferences
    dietary_restrictions = Column(JSONType, nullable=True)
    excluded_ingredients = Column(JSONType, nullable=True)
    target_calories_per_day = Column(Integer, nullable=True)
    target_budget = Column(Float, nullable=True)
    preferred_cuisines = Column(JSONType, nullable=True)

    # Generated metadata
    total_recipes = Column(Integer, nullable=False, default=0)
    total_calories = Column(Integer, nullable=True)
    total_cost = Column(Float, nullable=True)
    optimization_score = Column(Float, nullable=True)

    # Status tracking
    status = Column(String(50), nullable=False, default="draft", index=True)
    generation_time_seconds = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="meal_plans")
    recipes = relationship(
        "MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan"
    )
    grocery_carts = relationship(
        "GroceryCart", back_populates="meal_plan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MealPlan(id={self.id}, name='{self.name}', status='{self.status}', recipes={self.total_recipes})>"

    @property
    def num_days(self) -> int:
        """Calculate number of days in the plan."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def to_dict(self) -> dict:
        """Convert meal plan to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "num_days": self.num_days,
            "num_people": self.num_people,
            "dietary_restrictions": self.dietary_restrictions,
            "excluded_ingredients": self.excluded_ingredients,
            "target_calories_per_day": self.target_calories_per_day,
            "target_budget": self.target_budget,
            "total_recipes": self.total_recipes,
            "total_calories": self.total_calories,
            "total_cost": self.total_cost,
            "optimization_score": self.optimization_score,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MealPlanRecipe(Base):
    """
    Association between meal plans and recipes with scheduling info.

    Attributes:
        id: Primary key
        meal_plan_id: Foreign key to meal_plans
        recipe_id: Foreign key to recipes
        day_number: Day number in the plan (1-based)
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        scheduled_date: Actual date scheduled
        servings: Number of servings
        calories: Calculated calories for this meal
        cost: Estimated cost for this meal
        position: Position in the plan (for ordering)
        created_at: Creation timestamp
    """

    __tablename__ = "meal_plan_recipes"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    meal_plan_id = Column(
        BigInteger,
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipe_id = Column(
        BigInteger,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Scheduling
    day_number = Column(Integer, nullable=False)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    scheduled_date = Column(Date, nullable=True)
    servings = Column(Integer, nullable=False, default=2)

    # Calculated fields
    calories = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    position = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    meal_plan = relationship("MealPlan", back_populates="recipes")
    recipe = relationship("Recipe")

    def __repr__(self) -> str:
        return f"<MealPlanRecipe(meal_plan_id={self.meal_plan_id}, day={self.day_number}, meal={self.meal_type})>"


class GroceryCart(Base):
    """
    Grocery cart for a meal plan.

    Attributes:
        id: Primary key
        user_id: Foreign key to users
        meal_plan_id: Foreign key to meal_plans (optional)
        name: Cart name
        status: Status (active, ordered, completed)
        total_items: Total number of items
        total_cost: Total cost
        knuspr_cart_id: Knuspr cart ID (if synced)
        knuspr_synced_at: Last sync timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
        ordered_at: Order timestamp
    """

    __tablename__ = "grocery_carts"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    meal_plan_id = Column(
        BigInteger,
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="active", index=True)

    # Totals
    total_items = Column(Integer, nullable=False, default=0)
    total_cost = Column(Float, nullable=True)

    # Knuspr integration
    knuspr_cart_id = Column(String(255), nullable=True, unique=True, index=True)
    knuspr_synced_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    ordered_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="grocery_carts")
    meal_plan = relationship("MealPlan", back_populates="grocery_carts")
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GroceryCart(id={self.id}, name='{self.name}', items={self.total_items}, status='{self.status}')>"


class CartItem(Base):
    """
    Individual item in a grocery cart.

    Attributes:
        id: Primary key
        cart_id: Foreign key to grocery_carts
        ingredient_id: Foreign key to ingredients (optional)
        name: Item name
        quantity: Quantity needed
        unit: Unit of measurement
        category: Item category
        unit_price: Price per unit
        total_price: Total price for quantity
        recipe_ids: JSON list of recipe IDs that need this
        knuspr_product_id: Knuspr product ID
        knuspr_url: Knuspr product URL
        is_purchased: Has been purchased
        purchased_at: Purchase timestamp
        created_at: Creation timestamp
    """

    __tablename__ = "cart_items"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    cart_id = Column(
        BigInteger,
        ForeignKey("grocery_carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ingredient_id = Column(
        BigInteger, ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True
    )

    # Item details
    name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    category = Column(String(100), nullable=True)

    # Pricing
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)

    # Source tracking
    recipe_ids = Column(JSONType, nullable=True)

    # Knuspr integration
    knuspr_product_id = Column(String(255), nullable=True)
    knuspr_url = Column(String(500), nullable=True)

    # Status
    is_purchased = Column(Boolean, default=False, nullable=False)
    purchased_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    cart = relationship("GroceryCart", back_populates="items")
    ingredient = relationship("Ingredient")

    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, name='{self.name}', quantity={self.quantity} {self.unit})>"


# Indexes
MealPlan.__table_args__ = (
    Index("ix_meal_plans_user_status", "user_id", "status"),
    Index("ix_meal_plans_dates", "start_date", "end_date"),
)

MealPlanRecipe.__table_args__ = (
    Index("ix_meal_plan_recipes_plan_day", "meal_plan_id", "day_number"),
    Index("ix_meal_plan_recipes_plan_meal", "meal_plan_id", "meal_type"),
)

GroceryCart.__table_args__ = (
    Index("ix_grocery_carts_user_status", "user_id", "status"),
)
