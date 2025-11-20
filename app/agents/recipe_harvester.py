"""
Recipe Harvester Agent - Multi-source recipe scraping

This module provides the base class and interfaces for harvesting recipes from
multiple sources (web pages, APIs, RSS feeds) with duplicate detection and
intelligent merging.

Features:
- Async/await support for high throughput
- Schema.org/Recipe parsing for web pages
- API integration with rate limiting
- RSS feed polling
- Intelligent duplicate detection (85%+ similarity)
- Comprehensive error handling and recovery
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, Optional
import asyncio
import logging

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class RecipeScrapeResult(BaseModel):
    """Result of recipe scraping attempt"""

    title: str = Field(..., min_length=1, max_length=255)
    ingredients: list[str] = Field(..., min_length=1)
    instructions: str = Field(..., min_length=10)
    prep_time: Optional[int] = Field(None, description="Prep time in minutes")
    cook_time: Optional[int] = Field(None, description="Cook time in minutes")
    servings: Optional[int] = Field(None, ge=1)
    nutrition: Optional[dict] = Field(None, description="Nutrition information")
    source_url: str = Field(...)
    source_type: str = Field(..., description="'html', 'api', or 'rss'")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("ingredients")
    def validate_ingredients(cls, v):
        """Ensure ingredients are non-empty strings"""
        if not v:
            raise ValueError("Must have at least one ingredient")
        return [ing.strip() for ing in v if ing.strip()]

    @validator("instructions")
    def validate_instructions(cls, v):
        """Ensure instructions are substantial"""
        cleaned = v.strip()
        if len(cleaned) < 10:
            raise ValueError("Instructions must be at least 10 characters")
        return cleaned


class RecipeScraper(ABC):
    """
    Abstract base class for recipe scrapers.

    All recipe scraping implementations should inherit from this class
    and implement the required abstract methods.
    """

    def __init__(self, db_session=None, logger_instance=None):
        """
        Initialize recipe scraper.

        Args:
            db_session: SQLAlchemy async session (optional)
            logger_instance: Logger instance (optional)
        """
        self.db = db_session
        self.logger = logger_instance or logger

    @abstractmethod
    async def scrape(self, source: str) -> AsyncIterator[RecipeScrapeResult]:
        """
        Scrape recipes from source.

        Args:
            source: Source identifier (URL, feed URL, API endpoint, etc.)

        Yields:
            RecipeScrapeResult: Parsed recipe data

        Raises:
            ValueError: If source is invalid
            asyncio.TimeoutError: If scraping times out
        """
        pass

    @abstractmethod
    async def validate(self, recipe: RecipeScrapeResult) -> bool:
        """
        Validate recipe data completeness and quality.

        Args:
            recipe: Recipe to validate

        Returns:
            bool: True if recipe is valid, False otherwise
        """
        pass

    async def save_recipe(self, recipe: RecipeScrapeResult) -> dict:
        """
        Save recipe to database.

        Args:
            recipe: Recipe to save

        Returns:
            dict: Saved recipe data with ID

        Raises:
            Exception: If database operation fails
        """
        try:
            if not await self.validate(recipe):
                self.logger.warning(f"Recipe validation failed: {recipe.title}")
                raise ValueError(f"Invalid recipe: {recipe.title}")

            # Note: Actual database save would go here
            # For now, return recipe data for testing
            recipe_data = recipe.dict()
            self.logger.info(f"Recipe saved: {recipe.title}")
            return recipe_data

        except Exception as e:
            self.logger.error(f"Error saving recipe: {str(e)}")
            raise

    async def handle_error(
        self,
        error: Exception,
        source: str,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> bool:
        """
        Handle errors with exponential backoff retry logic.

        Args:
            error: The exception that occurred
            source: Source where error occurred
            retry_count: Current retry attempt (0-based)
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if should retry, False if should give up

        Raises:
            Exception: Re-raises error if max retries exceeded
        """
        if retry_count >= max_retries:
            self.logger.error(
                f"Max retries ({max_retries}) exceeded for source: {source}"
            )
            return False

        # Exponential backoff: 2^retry_count seconds
        wait_time = 2 ** retry_count
        self.logger.warning(
            f"Error scraping {source}: {str(error)}. "
            f"Retrying in {wait_time}s (attempt {retry_count + 1}/{max_retries})"
        )

        await asyncio.sleep(wait_time)
        return True


class DuplicateDetector:
    """
    Detects and manages duplicate recipes using similarity scoring.

    Uses title and ingredient overlap to identify duplicates with
    configurable similarity threshold (default 85%).
    """

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize duplicate detector.

        Args:
            similarity_threshold: Similarity score threshold (0-1) for duplicates
        """
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("Similarity threshold must be between 0 and 1")
        self.similarity_threshold = similarity_threshold
        self.logger = logger

    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate title similarity using simple string matching.

        Args:
            title1: First title
            title2: Second title

        Returns:
            float: Similarity score (0-1)
        """
        from difflib import SequenceMatcher

        return SequenceMatcher(None, title1.lower(), title2.lower()).ratio()

    def _calculate_ingredient_similarity(
        self, ingredients1: list[str], ingredients2: list[str]
    ) -> float:
        """
        Calculate ingredient overlap similarity.

        Args:
            ingredients1: First ingredient list
            ingredients2: Second ingredient list

        Returns:
            float: Similarity score (0-1) based on overlap
        """
        if not ingredients1 or not ingredients2:
            return 0.0

        set1 = set(ing.lower().strip() for ing in ingredients1)
        set2 = set(ing.lower().strip() for ing in ingredients2)

        overlap = len(set1 & set2)
        max_len = max(len(set1), len(set2))

        return overlap / max_len if max_len > 0 else 0.0

    def calculate_similarity(
        self, recipe1: RecipeScrapeResult, recipe2: RecipeScrapeResult
    ) -> float:
        """
        Calculate overall similarity between two recipes.

        Combines title similarity (60% weight) and ingredient similarity (40% weight).

        Args:
            recipe1: First recipe
            recipe2: Second recipe

        Returns:
            float: Overall similarity score (0-1)
        """
        title_sim = self._calculate_title_similarity(recipe1.title, recipe2.title)
        ingredient_sim = self._calculate_ingredient_similarity(
            recipe1.ingredients, recipe2.ingredients
        )

        # Weighted combination: 60% title, 40% ingredients
        overall_sim = (title_sim * 0.6) + (ingredient_sim * 0.4)

        self.logger.debug(
            f"Similarity for '{recipe1.title}' vs '{recipe2.title}': "
            f"{overall_sim:.2f} (title: {title_sim:.2f}, ingredients: {ingredient_sim:.2f})"
        )

        return overall_sim

    def is_duplicate(
        self, recipe1: RecipeScrapeResult, recipe2: RecipeScrapeResult
    ) -> bool:
        """
        Check if two recipes are duplicates.

        Args:
            recipe1: First recipe
            recipe2: Second recipe

        Returns:
            bool: True if recipes are duplicates, False otherwise
        """
        similarity = self.calculate_similarity(recipe1, recipe2)
        return similarity >= self.similarity_threshold

    def find_duplicate_candidates(
        self,
        recipe: RecipeScrapeResult,
        existing_recipes: list[RecipeScrapeResult],
    ) -> list[tuple[RecipeScrapeResult, float]]:
        """
        Find candidate duplicates for a recipe from existing recipes.

        Args:
            recipe: Recipe to find duplicates for
            existing_recipes: List of existing recipes to check against

        Returns:
            list[tuple[RecipeScrapeResult, float]]: List of (recipe, similarity_score)
                tuples for recipes above threshold, sorted by similarity descending
        """
        candidates = []

        for existing in existing_recipes:
            similarity = self.calculate_similarity(recipe, existing)

            if similarity >= self.similarity_threshold:
                candidates.append((existing, similarity))

        # Sort by similarity descending
        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates
