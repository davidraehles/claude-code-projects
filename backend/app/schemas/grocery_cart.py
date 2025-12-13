"""
Pydantic schemas for Grocery Cart entity validation.

Defines request and response schemas for grocery cart API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator


class RecipeSource(BaseModel):
    """
    Source recipe information for a cart item.

    Attributes:
        recipe_id: ID of the recipe
        recipe_name: Name of the recipe
    """

    recipe_id: int = Field(..., description="Recipe ID")
    recipe_name: str = Field(..., description="Recipe name")

    class Config:
        schema_extra = {
            "example": {
                "recipe_id": 1,
                "recipe_name": "Pasta Carbonara",
            }
        }


class CartItemSchema(BaseModel):
    """
    Schema for a cart item with recipe source tracking.

    Attributes:
        id: Cart item ID
        name: Ingredient name
        quantity: Quantity needed
        unit: Unit of measurement
        category: Optional category (produce, dairy, etc.)
        unit_price: Optional price per unit
        total_price: Optional total price
        recipe_sources: List of recipes that use this ingredient
        knuspr_product_id: Optional Knuspr product ID
        knuspr_url: Optional Knuspr product URL
        is_purchased: Whether item has been purchased
    """

    id: Optional[int] = Field(None, description="Cart item ID")
    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name")
    quantity: float = Field(..., gt=0, description="Quantity needed")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    unit_price: Optional[float] = Field(None, ge=0, description="Price per unit")
    total_price: Optional[float] = Field(None, ge=0, description="Total price")
    recipe_sources: Optional[List[RecipeSource]] = Field(
        None, description="Recipes that use this ingredient"
    )
    knuspr_product_id: Optional[str] = Field(None, description="Knuspr product ID")
    knuspr_url: Optional[str] = Field(None, description="Knuspr product URL")
    is_purchased: bool = Field(False, description="Purchase status")

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        """Ensure quantity is positive."""
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "spaghetti",
                "quantity": 400.0,
                "unit": "g",
                "category": "pantry",
                "unit_price": 2.50,
                "total_price": 2.50,
                "recipe_sources": [
                    {"recipe_id": 1, "recipe_name": "Pasta Carbonara"},
                    {"recipe_id": 3, "recipe_name": "Spaghetti Bolognese"},
                ],
                "knuspr_product_id": "12345",
                "knuspr_url": "https://knuspr.de/products/12345",
                "is_purchased": False,
            }
        }


class GroceryCartSchema(BaseModel):
    """
    Schema for a grocery cart.

    Attributes:
        id: Cart ID
        name: Cart name
        meal_plan_id: Optional associated meal plan ID
        status: Cart status (active, ordered, completed)
        total_items: Total number of items
        total_cost: Total estimated cost
        items: List of cart items
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[int] = Field(None, description="Cart ID")
    name: str = Field(..., min_length=1, max_length=255, description="Cart name")
    meal_plan_id: Optional[int] = Field(None, description="Associated meal plan ID")
    status: str = Field("active", description="Cart status")
    total_items: int = Field(0, ge=0, description="Total number of items")
    total_cost: Optional[float] = Field(None, ge=0, description="Total cost")
    items: List[CartItemSchema] = Field(default_factory=list, description="Cart items")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Ensure status is valid."""
        valid_statuses = {"active", "ordered", "completed"}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v.lower()

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Weekly Groceries",
                "meal_plan_id": 1,
                "status": "active",
                "total_items": 15,
                "total_cost": 45.50,
                "items": [
                    {
                        "id": 1,
                        "name": "spaghetti",
                        "quantity": 400.0,
                        "unit": "g",
                        "category": "pantry",
                        "recipe_sources": [{"recipe_id": 1, "recipe_name": "Pasta Carbonara"}],
                    }
                ],
                "created_at": "2025-11-29T10:30:00",
                "updated_at": "2025-11-29T10:30:00",
            }
        }


class CreateCartFromMealPlanRequest(BaseModel):
    """
    Request schema for creating a cart from a meal plan.

    Attributes:
        meal_plan_id: ID of the meal plan
        aggregate_duplicates: Whether to aggregate duplicate ingredients (default: True)
    """

    meal_plan_id: int = Field(..., gt=0, description="Meal plan ID")
    aggregate_duplicates: bool = Field(
        True, description="Aggregate duplicate ingredients with same unit"
    )

    class Config:
        schema_extra = {
            "example": {
                "meal_plan_id": 1,
                "aggregate_duplicates": True,
            }
        }


class CartResponse(BaseModel):
    """
    Response schema for cart creation.

    Attributes:
        cart_id: ID of the created cart
        cart_name: Name of the cart
        total_items: Number of items in cart
        items: List of cart items
        unmatched_ingredients: List of ingredients that couldn't be parsed
    """

    cart_id: int = Field(..., description="Cart ID")
    cart_name: str = Field(..., description="Cart name")
    total_items: int = Field(..., ge=0, description="Total items")
    items: List[CartItemSchema] = Field(..., description="Cart items")
    unmatched_ingredients: List[str] = Field(
        default_factory=list, description="Ingredients that couldn't be parsed"
    )

    class Config:
        schema_extra = {
            "example": {
                "cart_id": 1,
                "cart_name": "Grocery List from Meal Plan #1",
                "total_items": 12,
                "items": [
                    {
                        "id": 1,
                        "name": "spaghetti",
                        "quantity": 400.0,
                        "unit": "g",
                        "category": None,
                        "recipe_sources": [{"recipe_id": 1, "recipe_name": "Pasta Carbonara"}],
                    }
                ],
                "unmatched_ingredients": [],
            }
        }


class KnusprCredentials(BaseModel):
    """
    Knuspr authentication credentials.

    Attributes:
        email: Knuspr account email
        password: Knuspr account password
        country: Country code (cz, de, at)
    """

    email: str = Field(..., min_length=1, description="Knuspr account email")
    password: str = Field(..., min_length=6, description="Knuspr account password")
    country: str = Field("de", description="Country code (cz, de, at)")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure_password",
                "country": "de",
            }
        }


class MatchPreferences(BaseModel):
    """
    Product matching preferences for Knuspr cart filling.

    Attributes:
        min_confidence: Minimum confidence score for product matches (0.0-1.0)
        allow_substitutions: Allow ingredient substitutions
        prefer_organic: Prefer organic products when available
        max_price_per_item: Maximum price per item (optional)
    """

    min_confidence: float = Field(0.5, ge=0.0, le=1.0, description="Minimum match confidence")
    allow_substitutions: bool = Field(True, description="Allow ingredient substitutions")
    prefer_organic: bool = Field(False, description="Prefer organic products")
    max_price_per_item: Optional[float] = Field(None, ge=0, description="Max price per item")

    class Config:
        schema_extra = {
            "example": {
                "min_confidence": 0.7,
                "allow_substitutions": True,
                "prefer_organic": False,
                "max_price_per_item": 10.0,
            }
        }


class FillKnusprCartRequest(BaseModel):
    """
    Request schema for filling a Knuspr cart.

    Attributes:
        credentials: Knuspr login credentials
        match_preferences: Optional product matching preferences
    """

    credentials: KnusprCredentials = Field(..., description="Knuspr credentials")
    match_preferences: Optional[MatchPreferences] = Field(
        None, description="Product matching preferences"
    )

    class Config:
        schema_extra = {
            "example": {
                "credentials": {
                    "email": "user@example.com",
                    "password": "secure_password",
                    "country": "de",
                },
                "match_preferences": {
                    "min_confidence": 0.7,
                    "allow_substitutions": True,
                    "prefer_organic": False,
                },
            }
        }


class MatchedItem(BaseModel):
    """
    Schema for a matched Knuspr product.

    Attributes:
        name: Original ingredient name
        knuspr_product_id: Matched Knuspr product ID
        knuspr_product_name: Matched Knuspr product name
        quantity: Quantity to add
        unit: Unit of measurement
        confidence: Match confidence score (0.0-1.0)
    """

    name: str = Field(..., description="Original ingredient name")
    knuspr_product_id: str = Field(..., description="Knuspr product ID")
    knuspr_product_name: str = Field(..., description="Knuspr product name")
    quantity: float = Field(..., gt=0, description="Quantity")
    unit: str = Field(..., description="Unit")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Match confidence")

    class Config:
        from_attributes = True


class FillKnusprCartResponse(BaseModel):
    """
    Response schema for Knuspr cart filling operation.

    Attributes:
        success: Whether the operation was successful
        cart_id: ID of the grocery cart in our database
        knuspr_cart_url: URL to the Knuspr cart
        matched_items: Number of items successfully matched and added
        partial_matches: Number of items with partial matches
        unmatched_items: List of items that couldn't be matched
        matched_products: Details of matched products
        progress: Progress percentage (0-100)
        message: Status message
    """

    success: bool = Field(..., description="Operation success status")
    cart_id: int = Field(..., description="Database cart ID")
    knuspr_cart_url: Optional[str] = Field(None, description="Knuspr cart URL")
    matched_items: int = Field(..., ge=0, description="Number of matched items")
    partial_matches: int = Field(0, ge=0, description="Number of partial matches")
    unmatched_items: List[str] = Field(
        default_factory=list, description="Unmatched item names"
    )
    matched_products: List[MatchedItem] = Field(
        default_factory=list, description="Details of matched products"
    )
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Status message")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "cart_id": 1,
                "knuspr_cart_url": "https://www.knuspr.de/cart/abc123",
                "matched_items": 15,
                "partial_matches": 3,
                "unmatched_items": ["rare spice", "exotic herb"],
                "matched_products": [
                    {
                        "name": "spaghetti",
                        "knuspr_product_id": "12345",
                        "knuspr_product_name": "Barilla Spaghetti 500g",
                        "quantity": 400.0,
                        "unit": "g",
                        "confidence": 0.95,
                    }
                ],
                "progress": 100,
                "message": "Successfully added 15 items to Knuspr cart",
            }
        }
