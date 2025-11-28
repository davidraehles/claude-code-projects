"""
Recipe API endpoints.

Provides REST API for recipe operations including harvesting, retrieval,
and management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
import tempfile
import os

from app.api.dependencies import get_database, get_current_user_id
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import (
    RecipeResponse,
    RecipeListResponse,
    RecipeHarvestRequest,
    RecipeHarvestResponse,
    RecipeCreate,
    RecipeUpdate,
)
from app.agents.html_scraper import HTMLRecipeScraper
from app.agents.api_scraper import APIRecipeScraper
from app.agents.rss_scraper import RSSRecipeScraper
from app.agents.file_parser import FileRecipeParser
from app.events import (
    Event,
    EventType,
    RecipeHarvestRequestedEvent,
    RecipeHarvestCompletedEvent,
    RecipeHarvestFailedEvent,
)
from app.events.bus import get_event_bus

router = APIRouter()


# Duplicate detection helper
def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple similarity score between two strings.

    Args:
        text1: First string
        text2: Second string

    Returns:
        float: Similarity score between 0 and 1
    """
    # Simple word-based similarity (can be improved with fuzzy matching)
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union) if union else 0.0


def find_duplicate_recipe(
    db: Session, title: str, source_url: str, user_id: int, threshold: float = 0.85
) -> Optional[Recipe]:
    """
    Find if a recipe is a duplicate based on title similarity or URL.

    Args:
        db: Database session
        title: Recipe title
        source_url: Source URL
        user_id: User ID
        threshold: Similarity threshold (default 0.85)

    Returns:
        Recipe if duplicate found, None otherwise
    """
    # Check for exact URL match first
    existing = db.query(Recipe).filter(
        Recipe.source_url == source_url,
        Recipe.user_id == user_id
    ).first()

    if existing:
        return existing

    # Check for similar titles
    user_recipes = db.query(Recipe).filter(
        Recipe.user_id == user_id,
        Recipe.duplicate_of_id.is_(None)  # Only check against non-duplicates
    ).all()

    for recipe in user_recipes:
        similarity = calculate_similarity(title, recipe.title)
        if similarity >= threshold:
            return recipe

    return None


async def harvest_recipe_background(
    url: str,
    source_type: str,
    user_id: int,
    correlation_id: str,
    db_session: Session
):
    """
    Background task to harvest recipe from URL.

    Args:
        url: URL to harvest from
        source_type: Type of source (html, api, rss)
        user_id: User ID
        correlation_id: Correlation ID for event tracking
        db_session: Database session
    """
    event_bus = get_event_bus()

    try:
        # Publish started event
        await event_bus.publish(Event(
            event_type=EventType.RECIPE_HARVEST_STARTED,
            correlation_id=correlation_id,
            user_id=user_id,
            payload={"url": url, "source_type": source_type}
        ))

        # Select appropriate scraper
        if source_type == "html":
            scraper = HTMLRecipeScraper(timeout=30, db_session=db_session)
        elif source_type == "api":
            scraper = APIRecipeScraper(db_session=db_session)
        elif source_type == "rss":
            scraper = RSSRecipeScraper(db_session=db_session)
        else:
            raise ValueError(f"Invalid source_type: {source_type}")

        # Scrape recipe
        recipes_found = []
        async for recipe_result in scraper.scrape(url):
            recipes_found.append(recipe_result)

        if not recipes_found:
            raise ValueError("No recipes found at URL")

        # Take the first recipe (most scrapers return 1 recipe per URL)
        recipe_data = recipes_found[0]

        # Check for duplicates
        duplicate = find_duplicate_recipe(
            db_session,
            recipe_data.title,
            recipe_data.source_url,
            user_id
        )

        if duplicate:
            # Publish duplicate detected event
            await event_bus.publish(Event(
                event_type=EventType.RECIPE_DUPLICATE_DETECTED,
                correlation_id=correlation_id,
                user_id=user_id,
                payload={
                    "title": recipe_data.title,
                    "url": url,
                    "duplicate_of_id": duplicate.id
                }
            ))

            # Create duplicate entry
            new_recipe = Recipe(
                user_id=user_id,
                title=recipe_data.title,
                ingredients=recipe_data.ingredients,
                instructions=recipe_data.instructions,
                prep_time=recipe_data.prep_time,
                cook_time=recipe_data.cook_time,
                servings=recipe_data.servings,
                nutrition=recipe_data.nutrition,
                source_url=recipe_data.source_url,
                source_type=recipe_data.source_type,
                duplicate_of_id=duplicate.id
            )
            db_session.add(new_recipe)
            db_session.commit()
            db_session.refresh(new_recipe)

            # Publish completed event
            await event_bus.publish(Event(
                event_type=EventType.RECIPE_HARVEST_COMPLETED,
                correlation_id=correlation_id,
                user_id=user_id,
                payload=RecipeHarvestCompletedEvent(
                    recipe_id=new_recipe.id,
                    title=new_recipe.title,
                    source_url=new_recipe.source_url,
                    is_duplicate=True,
                    duplicate_of_id=duplicate.id
                ).model_dump()
            ))

        else:
            # Save new recipe
            new_recipe = Recipe(
                user_id=user_id,
                title=recipe_data.title,
                ingredients=recipe_data.ingredients,
                instructions=recipe_data.instructions,
                prep_time=recipe_data.prep_time,
                cook_time=recipe_data.cook_time,
                servings=recipe_data.servings,
                nutrition=recipe_data.nutrition,
                source_url=recipe_data.source_url,
                source_type=recipe_data.source_type,
                duplicate_of_id=None
            )
            db_session.add(new_recipe)
            db_session.commit()
            db_session.refresh(new_recipe)

            # Publish saved event
            await event_bus.publish(Event(
                event_type=EventType.RECIPE_SAVED,
                correlation_id=correlation_id,
                user_id=user_id,
                payload={"recipe_id": new_recipe.id, "title": new_recipe.title}
            ))

            # Publish completed event
            await event_bus.publish(Event(
                event_type=EventType.RECIPE_HARVEST_COMPLETED,
                correlation_id=correlation_id,
                user_id=user_id,
                payload=RecipeHarvestCompletedEvent(
                    recipe_id=new_recipe.id,
                    title=new_recipe.title,
                    source_url=new_recipe.source_url,
                    is_duplicate=False,
                    duplicate_of_id=None
                ).model_dump()
            ))

        # Clean up scraper
        if hasattr(scraper, 'close'):
            await scraper.close()

    except Exception as e:
        # Publish failed event
        await event_bus.publish(Event(
            event_type=EventType.RECIPE_HARVEST_FAILED,
            correlation_id=correlation_id,
            user_id=user_id,
            payload=RecipeHarvestFailedEvent(
                url=url,
                error_message=str(e),
                error_type=type(e).__name__,
                retry_count=0
            ).model_dump()
        ))
        print(f"❌ Recipe harvest failed: {e}")


@router.post("/harvest", response_model=RecipeHarvestResponse, status_code=status.HTTP_202_ACCEPTED)
async def harvest_recipe(
    request: RecipeHarvestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Harvest a recipe from a URL.

    This endpoint triggers asynchronous recipe harvesting from the provided URL.
    The actual harvesting happens in the background, and events are published
    to track progress.

    Args:
        request: Recipe harvest request with URL and source type
        background_tasks: FastAPI background tasks
        db: Database session
        user_id: Current user ID from JWT token

    Returns:
        RecipeHarvestResponse: Status of harvest request
    """
    # Generate correlation ID for event tracking
    correlation_id = str(uuid.uuid4())

    # Publish requested event
    event_bus = get_event_bus()
    await event_bus.publish(Event(
        event_type=EventType.RECIPE_HARVEST_REQUESTED,
        correlation_id=correlation_id,
        user_id=user_id,
        payload=RecipeHarvestRequestedEvent(
            url=request.url,
            source_type=request.source_type,
            user_id=user_id
        ).model_dump()
    ))

    # Queue background task
    background_tasks.add_task(
        harvest_recipe_background,
        request.url,
        request.source_type,
        user_id,
        correlation_id,
        db
    )

    return RecipeHarvestResponse(
        success=True,
        message=f"Recipe harvest queued for {request.url}. Check back shortly.",
        recipe=None,
        is_duplicate=False,
        duplicate_of_id=None
    )


@router.post("/upload", response_model=RecipeHarvestResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_recipe_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Import a recipe from an uploaded file (HTML or PDF).

    Supports:
    - HTML files (.html, .htm)
    - PDF files (.pdf)

    Args:
        file: The recipe file to upload
        db: Database session
        user_id: Current user ID from JWT token

    Returns:
        RecipeHarvestResponse: Status of import request

    Raises:
        HTTPException 400: Invalid file type or format
    """
    # Validate file type
    allowed_extensions = {'.html', '.htm', '.pdf'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file content
        content = await file.read()

        # Parse recipe based on file type
        if file_ext in ['.html', '.htm']:
            parsed_recipe = FileRecipeParser.parse_html_file(content.decode('utf-8'))
        else:  # PDF
            # Save to temp file for PDF processing
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                parsed_recipe = FileRecipeParser.parse_pdf_file(tmp_path)
            finally:
                os.unlink(tmp_path)

        # Check for duplicates
        source_url = f"file://{file.filename}"
        duplicate_recipe = find_duplicate_recipe(
            db,
            parsed_recipe['title'],
            source_url,
            user_id
        )

        if duplicate_recipe:
            return RecipeHarvestResponse(
                success=False,
                message=f"Recipe '{parsed_recipe['title']}' already exists in your library",
                recipe=None,
                is_duplicate=True,
                duplicate_of_id=duplicate_recipe.id
            )

        # Create recipe in database
        recipe = Recipe(
            user_id=user_id,
            title=parsed_recipe['title'],
            ingredients=parsed_recipe['ingredients'],
            instructions=parsed_recipe['instructions'],
            prep_time=parsed_recipe.get('prep_time'),
            cook_time=parsed_recipe.get('cook_time'),
            servings=parsed_recipe.get('servings', 4),
            source_type='file_upload',
            source_url=source_url,
        )

        db.add(recipe)
        db.commit()
        db.refresh(recipe)

        # Publish success event
        event_bus = get_event_bus()
        await event_bus.publish(Event(
            event_type=EventType.RECIPE_HARVEST_COMPLETED,
            correlation_id=str(uuid.uuid4()),
            user_id=user_id,
            payload=RecipeHarvestCompletedEvent(
                recipe_id=recipe.id,
                title=recipe.title,
                source_url=recipe.source_url,
                is_duplicate=False
            ).model_dump()
        ))

        return RecipeHarvestResponse(
            success=True,
            message=f"Recipe '{parsed_recipe['title']}' successfully imported from file",
            recipe=RecipeResponse.from_orm(recipe),
            is_duplicate=False,
            duplicate_of_id=None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    include_duplicates: bool = Query(False, description="Include duplicate recipes"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    List recipes for the current user.

    Args:
        skip: Number of recipes to skip (pagination)
        limit: Maximum number of recipes to return
        include_duplicates: Whether to include duplicate recipes
        source_type: Optional filter by source type
        db: Database session
        user_id: Current user ID from JWT token

    Returns:
        RecipeListResponse: List of recipes with pagination info
    """
    # Build query
    query = db.query(Recipe).filter(Recipe.user_id == user_id)

    # Filter duplicates
    if not include_duplicates:
        query = query.filter(Recipe.duplicate_of_id.is_(None))

    # Filter by source type
    if source_type:
        query = query.filter(Recipe.source_type == source_type.lower())

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    recipes = query.order_by(desc(Recipe.created_at)).offset(skip).limit(limit).all()

    return RecipeListResponse(
        items=[RecipeResponse.model_validate(recipe) for recipe in recipes],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get a specific recipe by ID.

    Args:
        recipe_id: Recipe ID
        db: Database session
        user_id: Current user ID from JWT token

    Returns:
        RecipeResponse: Recipe details

    Raises:
        HTTPException: If recipe not found or access denied
    """
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user_id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found"
        )

    return RecipeResponse.model_validate(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a recipe.

    Args:
        recipe_id: Recipe ID
        db: Database session
        user_id: Current user ID from JWT token

    Raises:
        HTTPException: If recipe not found or access denied
    """
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user_id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found"
        )

    db.delete(recipe)
    db.commit()


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    update_data: RecipeUpdate,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update a recipe.

    Args:
        recipe_id: Recipe ID
        update_data: Fields to update
        db: Database session
        user_id: Current user ID from JWT token

    Returns:
        RecipeResponse: Updated recipe

    Raises:
        HTTPException: If recipe not found or access denied
    """
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user_id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found"
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)

    return RecipeResponse.model_validate(recipe)
