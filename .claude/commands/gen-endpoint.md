# Gen Endpoint Skill

Generate FastAPI endpoint with Pydantic validation, SQLAlchemy ORM models, database migrations, and comprehensive tests.

## Usage

```
/gen-endpoint [endpoint-path] [http-method] [entity-type] [feature]
```

## Parameters

- `endpoint-path`: API path (e.g., /recipes, /ingredients, /meal-plans)
- `http-method`: GET, POST, PUT, DELETE, PATCH
- `entity-type`: What entity the endpoint manages (e.g., Recipe, Ingredient)
- `feature`: 002 (Recipe System)

## Examples

```
/gen-endpoint /recipes POST Recipe 002
/gen-endpoint /recipes/{id} GET Recipe 002
/gen-endpoint /ingredient-substitutes GET Ingredient 002
```

## What It Does

1. Reads data model from data-model.md
2. Generates Pydantic V2 request/response schemas
3. Creates SQLAlchemy ORM model if new entity
4. Generates FastAPI endpoint with async/await
5. Implements row-level security (multi-tenant isolation)
6. Creates database migration with Alembic
7. Generates pytest test suite
8. Adds comprehensive error handling
9. Includes API documentation

## Output

Creates the following files:

```
app/
  endpoints/
    └─ endpoint_name.py        (FastAPI endpoint)
  models/
    └─ model_name.py           (SQLAlchemy ORM model)
  schemas/
    └─ schema_name.py          (Pydantic schemas)

migrations/versions/
  └─ XXXXX_add_entity.py       (Alembic migration)

tests/
  ├─ test_endpoint.py          (Unit tests)
  └─ integration/
      └─ test_workflow.py      (Integration tests)
```

## Example: Create Recipe Endpoint

```python
# app/endpoints/recipes.py
"""
Recipe Management Endpoints

Provides CRUD operations for recipes with row-level security
to ensure users can only access their own recipes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponse:
    """
    Create a new recipe for the current user.

    Args:
        recipe: Recipe data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created recipe with generated ID

    Raises:
        HTTPException: If recipe creation fails
    """
    try:
        db_recipe = Recipe(
            **recipe.dict(),
            user_id=current_user.id,
        )
        db.add(db_recipe)
        await db.commit()
        await db.refresh(db_recipe)
        return db_recipe
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recipe",
        )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponse:
    """
    Get a specific recipe for the current user.

    Uses row-level security to ensure user can only access their own recipes.

    Args:
        recipe_id: Recipe ID to fetch
        db: Database session
        current_user: Authenticated user

    Returns:
        Recipe data

    Raises:
        HTTPException 404: If recipe not found or belongs to different user
    """
    query = select(Recipe).where(
        (Recipe.id == recipe_id) & (Recipe.user_id == current_user.id)
    )
    result = await db.execute(query)
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


@router.get("/", response_model=list[RecipeResponse])
async def list_recipes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> list[RecipeResponse]:
    """
    List all recipes for the current user.

    Args:
        db: Database session
        current_user: Authenticated user
        skip: Number of recipes to skip (pagination)
        limit: Maximum number of recipes to return

    Returns:
        List of recipes
    """
    query = (
        select(Recipe)
        .where(Recipe.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponse:
    """Update an existing recipe (authorized user only)."""
    query = select(Recipe).where(
        (Recipe.id == recipe_id) & (Recipe.user_id == current_user.id)
    )
    result = await db.execute(query)
    db_recipe = result.scalar_one_or_none()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = recipe.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recipe, field, value)

    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a recipe (authorized user only)."""
    query = select(Recipe).where(
        (Recipe.id == recipe_id) & (Recipe.user_id == current_user.id)
    )
    result = await db.execute(query)
    db_recipe = result.scalar_one_or_none()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await db.delete(db_recipe)
    await db.commit()
```

## Test Coverage

Generated tests include:
- ✓ Create endpoint (success and validation errors)
- ✓ Read endpoint (success and not found)
- ✓ Update endpoint (success and authorization)
- ✓ Delete endpoint (success and authorization)
- ✓ Row-level security (users can't access other users' data)
- ✓ Request validation (Pydantic validation)
- ✓ Response format validation
- ✓ Error handling (404, 403, 422, 500)
- Target: 90%+ coverage

## Database Migration

Includes automatic Alembic migration:
```python
# migrations/versions/20231114_create_recipes_table.py
def upgrade():
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        # ... other columns
    )

def downgrade():
    op.drop_table('recipes')
```

## When to Use

- Need to quickly generate new API endpoints
- Building CRUD operations for entities
- Want consistent error handling and validation
- Need comprehensive test coverage
- Implementing row-level security
- Want database migrations automatically generated
