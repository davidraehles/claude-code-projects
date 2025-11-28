"""
Ingredient Intelligence API endpoints.

Provides REST API for ingredient operations including classification,
substitutions, and allergen checking.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.dependencies import get_database
from app.agents.ingredient_intelligence import IngredientIntelligenceAgent


router = APIRouter()


# Pydantic schemas
class IngredientClassificationResponse(BaseModel):
    """Response schema for ingredient classification."""
    found: bool
    name: str
    normalized_name: str
    id: Optional[int] = None
    category: Optional[str] = None
    allergens: List[str] = []
    nutrition_per_100g: Optional[dict] = None
    seasonal_availability: Optional[List[int]] = None
    base_unit: Optional[str] = None
    is_common: Optional[bool] = None


class SubstituteOption(BaseModel):
    """Schema for a single substitute option."""
    substitute_id: int
    substitute_name: str
    ratio: float = Field(..., description="Substitution ratio (1.0 = 1:1)")
    quality_score: float = Field(..., description="Quality score 0-1")
    notes: Optional[str] = None
    context: Optional[dict] = None
    is_vegan: bool = False
    is_vegetarian: bool = False
    is_gluten_free: bool = False
    is_dairy_free: bool = False


class SubstitutionRequest(BaseModel):
    """Request schema for finding substitutes."""
    ingredient: str = Field(..., description="Ingredient name to substitute")
    dietary_restrictions: Optional[List[str]] = Field(
        None,
        description="Dietary restrictions (vegan, vegetarian, gluten_free, dairy_free)"
    )
    min_quality_score: float = Field(0.6, ge=0.0, le=1.0, description="Minimum quality score")


class SubstitutionResponse(BaseModel):
    """Response schema for substitution recommendations."""
    ingredient: str
    found: bool
    substitutes: List[SubstituteOption]


class AllergenCheckRequest(BaseModel):
    """Request schema for allergen checking."""
    ingredients: List[str] = Field(..., min_length=1, description="List of ingredient names")


class AllergenInfo(BaseModel):
    """Schema for allergen information."""
    allergen: str
    severity: str
    description: Optional[str] = None
    found_in: List[str]


class AllergenCheckResponse(BaseModel):
    """Response schema for allergen checking."""
    ingredients_checked: int
    unknown_ingredients: List[str]
    allergens_found: List[AllergenInfo]
    has_allergens: bool


class IngredientSearchResult(BaseModel):
    """Schema for ingredient search result."""
    id: int
    name: str
    category: Optional[str] = None
    allergens: List[str] = []
    is_common: bool


# API Endpoints

@router.post("/classify", response_model=IngredientClassificationResponse)
async def classify_ingredient(
    ingredient_name: str = Query(..., description="Ingredient name to classify"),
    db: Session = Depends(get_database)
):
    """
    Classify an ingredient and return its metadata.

    Args:
        ingredient_name: Name of the ingredient
        db: Database session

    Returns:
        IngredientClassificationResponse: Ingredient classification data
    """
    agent = IngredientIntelligenceAgent(db)
    result = agent.classify_ingredient(ingredient_name)

    return IngredientClassificationResponse(**result)


@router.post("/substitutes", response_model=SubstitutionResponse)
async def find_substitutes(
    request: SubstitutionRequest,
    db: Session = Depends(get_database)
):
    """
    Find substitutes for an ingredient.

    Args:
        request: Substitution request with ingredient and filters
        db: Database session

    Returns:
        SubstitutionResponse: List of substitution options
    """
    agent = IngredientIntelligenceAgent(db)

    # Check if ingredient exists
    classification = agent.classify_ingredient(request.ingredient)

    substitutes = agent.find_substitutes(
        request.ingredient,
        dietary_restrictions=request.dietary_restrictions,
        min_quality_score=request.min_quality_score
    )

    return SubstitutionResponse(
        ingredient=request.ingredient,
        found=classification["found"],
        substitutes=[SubstituteOption(**sub) for sub in substitutes]
    )


@router.post("/allergens/check", response_model=AllergenCheckResponse)
async def check_allergens(
    request: AllergenCheckRequest,
    db: Session = Depends(get_database)
):
    """
    Check for allergens in a list of ingredients.

    Args:
        request: List of ingredient names to check
        db: Database session

    Returns:
        AllergenCheckResponse: Allergen information
    """
    agent = IngredientIntelligenceAgent(db)
    result = agent.check_allergens(request.ingredients)

    return AllergenCheckResponse(
        ingredients_checked=result["ingredients_checked"],
        unknown_ingredients=result["unknown_ingredients"],
        allergens_found=[AllergenInfo(**a) for a in result["allergens_found"]],
        has_allergens=result["has_allergens"]
    )


@router.get("/search", response_model=List[IngredientSearchResult])
async def search_ingredients(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
    db: Session = Depends(get_database)
):
    """
    Search for ingredients by name.

    Args:
        q: Search query
        category: Optional category filter
        limit: Maximum number of results
        db: Database session

    Returns:
        List[IngredientSearchResult]: Matching ingredients
    """
    agent = IngredientIntelligenceAgent(db)
    results = agent.search_ingredients(q, category=category, limit=limit)

    return [IngredientSearchResult(**r) for r in results]


@router.get("/categories")
async def list_categories(db: Session = Depends(get_database)):
    """
    List all ingredient categories.

    Args:
        db: Database session

    Returns:
        List of categories with counts
    """
    from app.models.ingredient import IngredientCategory, Ingredient
    from sqlalchemy import func

    # Get categories with ingredient counts
    categories = db.query(
        IngredientCategory.id,
        IngredientCategory.name,
        IngredientCategory.parent_id,
        func.count(Ingredient.id).label('ingredient_count')
    ).outerjoin(
        Ingredient, IngredientCategory.id == Ingredient.category_id
    ).group_by(
        IngredientCategory.id,
        IngredientCategory.name,
        IngredientCategory.parent_id
    ).all()

    return [
        {
            "id": cat.id,
            "name": cat.name,
            "parent_id": cat.parent_id,
            "ingredient_count": cat.ingredient_count
        }
        for cat in categories
    ]


@router.get("/allergens")
async def list_allergens(db: Session = Depends(get_database)):
    """
    List all known allergens.

    Args:
        db: Database session

    Returns:
        List of allergens
    """
    from app.models.ingredient import Allergen

    allergens = db.query(Allergen).all()

    return [
        {
            "id": allergen.id,
            "name": allergen.name,
            "description": allergen.description,
            "severity": allergen.severity
        }
        for allergen in allergens
    ]
