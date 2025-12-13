"""
Pydantic schemas for Recipe entity validation.

Defines request and response schemas for API endpoints and data validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator


class RecipeCreate(BaseModel):
    """Schema for creating a new recipe."""

    title: str = Field(..., min_length=1, max_length=255, description="Recipe title")
    ingredients: List[str] = Field(..., min_items=1, description="List of ingredients")
    instructions: str = Field(..., min_length=10, description="Recipe instructions")
    prep_time: Optional[int] = Field(None, ge=0, description="Prep time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, description="Cook time in minutes")
    servings: Optional[int] = Field(None, ge=1, description="Number of servings")
    nutrition: Optional[Dict[str, Any]] = Field(None, description="Nutrition information")
    source_url: str = Field(..., description="Original source URL")
    source_type: str = Field(..., description="Type of source (html, api, rss)")

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, v):
        """Ensure ingredients are non-empty strings."""
        return [ing.strip() for ing in v if ing.strip()]

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        """Ensure source_type is valid."""
        valid_types = {"html", "api", "rss", "file_upload"}
        if v.lower() not in valid_types:
            raise ValueError(f"source_type must be one of {valid_types}")
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "title": "Pasta Carbonara",
                "ingredients": [
                    "400g spaghetti",
                    "200g pancetta",
                    "4 large eggs",
                    "100g Parmesan cheese",
                ],
                "instructions": "Cook pasta. Fry pancetta. Toss with eggs and cheese.",
                "prep_time": 10,
                "cook_time": 20,
                "servings": 4,
                "source_url": "https://example.com/recipes/pasta-carbonara",
                "source_type": "html",
            }
        }


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    ingredients: Optional[List[str]] = Field(None, min_items=1)
    instructions: Optional[str] = Field(None, min_length=10)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    nutrition: Optional[Dict[str, Any]] = None


class RecipeResponse(RecipeCreate):
    """Schema for recipe responses."""

    id: int = Field(..., description="Recipe ID")
    duplicate_of_id: Optional[int] = Field(None, description="Parent recipe if duplicate")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Pasta Carbonara",
                "ingredients": [
                    "400g spaghetti",
                    "200g pancetta",
                    "4 large eggs",
                    "100g Parmesan cheese",
                ],
                "instructions": "Cook pasta. Fry pancetta. Toss with eggs and cheese.",
                "prep_time": 10,
                "cook_time": 20,
                "servings": 4,
                "nutrition": {
                    "calories": 550,
                    "protein": 30,
                    "carbohydrates": 65,
                    "fat": 15,
                },
                "source_url": "https://example.com/recipes/pasta-carbonara",
                "source_type": "html",
                "duplicate_of_id": None,
                "created_at": "2025-11-14T10:30:00",
                "last_updated": "2025-11-14T10:30:00",
            }
        }


class RecipeListResponse(BaseModel):
    """Schema for listing recipes with pagination."""

    items: List[RecipeResponse] = Field(..., description="List of recipes")
    total: int = Field(..., ge=0, description="Total number of recipes")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, description="Maximum items returned")

    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Pasta Carbonara",
                        "ingredients": ["400g spaghetti", "200g pancetta"],
                        "instructions": "Cook pasta and fry pancetta together",
                        "prep_time": 10,
                        "cook_time": 20,
                        "servings": 4,
                        "nutrition": None,
                        "source_url": "https://example.com/recipes/pasta-carbonara",
                        "source_type": "html",
                        "duplicate_of_id": None,
                        "created_at": "2025-11-14T10:30:00",
                        "last_updated": "2025-11-14T10:30:00",
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10,
            }
        }


class RecipeHarvestRequest(BaseModel):
    """Schema for requesting recipe harvest from a URL."""

    url: str = Field(..., description="URL to harvest recipe from")
    source_type: Optional[str] = Field(
        "html",
        description="Type of source (html, api, rss). Auto-detected if not provided."
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        """Ensure source_type is valid."""
        if v is None:
            return "html"  # Default to HTML
        valid_types = {"html", "api", "rss"}
        if v.lower() not in valid_types:
            raise ValueError(f"source_type must be one of {valid_types}")
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "url": "https://ottolenghi.co.uk/recipes/pasta-carbonara",
                "source_type": "html"
            }
        }


class RecipeHarvestResponse(BaseModel):
    """Schema for recipe harvest response."""

    success: bool = Field(..., description="Whether harvest was successful")
    message: str = Field(..., description="Status message")
    recipe: Optional[RecipeResponse] = Field(None, description="Harvested recipe if successful")
    is_duplicate: bool = Field(False, description="Whether this recipe is a duplicate")
    duplicate_of_id: Optional[int] = Field(None, description="ID of original recipe if duplicate")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Recipe harvested successfully",
                "recipe": {
                    "id": 1,
                    "title": "Pasta Carbonara",
                    "ingredients": ["400g spaghetti", "200g pancetta"],
                    "instructions": "Cook pasta. Fry pancetta. Toss with eggs and cheese.",
                    "prep_time": 10,
                    "cook_time": 20,
                    "servings": 4,
                    "nutrition": None,
                    "source_url": "https://example.com/recipes/pasta-carbonara",
                    "source_type": "html",
                    "duplicate_of_id": None,
                    "created_at": "2025-11-14T10:30:00",
                    "last_updated": "2025-11-14T10:30:00",
                },
                "is_duplicate": False,
                "duplicate_of_id": None
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., ge=400, le=599, description="HTTP status code")

    class Config:
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Recipe title must be at least 1 character",
                "status_code": 422,
            }
        }
