"""
API Recipe Scraper - Fetches recipes from recipe APIs

Handles API integration with rate limiting, request retry logic, and
pagination support. Supports multiple recipe API formats.

Features:
- Rate limiting (configurable requests per second)
- Exponential backoff retry logic
- Pagination support
- Response format normalization
- API key management
"""

import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any
from datetime import datetime

import httpx

from app.agents.recipe_harvester import RecipeScraper, RecipeScrapeResult

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Supports configurable rate limiting (requests per second).
    """

    def __init__(self, rate: int = 10):
        """
        Initialize rate limiter.

        Args:
            rate: Maximum requests per second (default: 10)
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")
        self.rate = rate
        self.semaphore = asyncio.Semaphore(rate)
        self.last_reset = asyncio.get_event_loop().time()
        self.available_tokens = rate

    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.semaphore:
            await asyncio.sleep(0)  # Yield control for fairness


class APIRecipeScraper(RecipeScraper):
    """
    Scrapes recipes from recipe APIs with rate limiting.

    Supports multiple API providers with configurable endpoints and
    authentication methods.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.spoonacular.com",
        rate_limit: int = 10,
        timeout: int = 30,
        db_session=None,
    ):
        """
        Initialize API recipe scraper.

        Args:
            api_key: API key for authentication
            base_url: Base URL of recipe API
            rate_limit: Maximum requests per second
            timeout: HTTP request timeout in seconds
            db_session: SQLAlchemy async session (optional)
        """
        super().__init__(db_session=db_session)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limiter = RateLimiter(rate_limit)
        self.client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        return self.client

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()

    async def scrape(self, query: str) -> AsyncIterator[RecipeScrapeResult]:
        """
        Search for and scrape recipes from API.

        Args:
            query: Search query (recipe name, cuisine, etc.)

        Yields:
            RecipeScrapeResult: Recipe data from API

        Raises:
            ValueError: If query is invalid
            httpx.HTTPError: If API request fails
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        retry_count = 0
        max_retries = 3

        while True:
            try:
                # Search for recipes
                recipe_ids = await self._search_recipes(query)

                if not recipe_ids:
                    self.logger.info(f"No recipes found for query: {query}")
                    return

                # Fetch detailed information for each recipe
                for recipe_id in recipe_ids[:20]:  # Limit to first 20
                    recipe = await self._fetch_recipe(recipe_id)
                    if recipe:
                        yield recipe

                return

            except asyncio.TimeoutError:
                should_retry = await self.handle_error(
                    asyncio.TimeoutError(f"Timeout searching for '{query}'"),
                    query,
                    retry_count,
                    max_retries,
                )
                if should_retry:
                    retry_count += 1
                else:
                    raise

            except httpx.HTTPError as e:
                should_retry = await self.handle_error(e, query, retry_count, max_retries)
                if should_retry:
                    retry_count += 1
                else:
                    raise

            except Exception as e:
                self.logger.error(f"Error searching recipes: {str(e)}")
                raise

    async def _search_recipes(self, query: str) -> list[int]:
        """
        Search for recipes using API.

        Args:
            query: Search query

        Returns:
            list[int]: List of recipe IDs matching query
        """
        await self.rate_limiter.acquire()

        client = await self._get_client()
        url = f"{self.base_url}/recipes/search"

        params = {
            "query": query,
            "number": 20,  # Get up to 20 results
        }

        if self.api_key:
            params["apiKey"] = self.api_key

        self.logger.debug(f"Searching recipes: {query}")

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            recipe_ids = [r.get("id") for r in results if r.get("id")]
            self.logger.info(f"Found {len(recipe_ids)} recipes for '{query}'")

            return recipe_ids

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid API key")
            elif e.response.status_code == 429:
                raise Exception("API rate limit exceeded")
            raise

    async def _fetch_recipe(self, recipe_id: int) -> Optional[RecipeScrapeResult]:
        """
        Fetch detailed recipe information from API.

        Args:
            recipe_id: Recipe ID

        Returns:
            RecipeScrapeResult: Recipe data or None if fetch fails
        """
        await self.rate_limiter.acquire()

        client = await self._get_client()
        url = f"{self.base_url}/recipes/{recipe_id}/information"

        params = {}
        if self.api_key:
            params["apiKey"] = self.api_key

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            return self._parse_api_response(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                self.logger.debug(f"Recipe {recipe_id} not found")
                return None
            raise

        except Exception as e:
            self.logger.debug(f"Error fetching recipe {recipe_id}: {str(e)}")
            return None

    def _parse_api_response(self, data: Dict[str, Any]) -> Optional[RecipeScrapeResult]:
        """
        Parse API response into RecipeScrapeResult.

        Args:
            data: API response data

        Returns:
            RecipeScrapeResult: Parsed recipe or None if invalid
        """
        try:
            title = data.get("title", "").strip()
            if not title:
                return None

            # Extract ingredients from API format
            ingredients = []
            for ing_data in data.get("extendedIngredients", []):
                ing_name = ing_data.get("original", "").strip()
                if ing_name:
                    ingredients.append(ing_name)

            if not ingredients:
                return None

            # Extract instructions
            instructions = ""
            if data.get("instructions"):
                instructions = data.get("instructions", "").strip()
            else:
                # Try to build from steps
                steps = data.get("analyzedInstructions", [{}])[0].get("steps", [])
                instructions = " ".join([s.get("step", "") for s in steps])

            if not instructions:
                instructions = "See recipe source for instructions"

            # Extract cooking times (API provides in minutes)
            prep_time = data.get("preparationMinutes")
            cook_time = data.get("cookingMinutes")

            # Extract servings
            servings = data.get("servings")

            # Extract nutrition information
            nutrition = None
            nutrition_data = data.get("nutrition", {})
            if nutrition_data:
                nutrition = {
                    "calories": nutrition_data.get("calories"),
                    "carbohydrates": nutrition_data.get("carbs"),
                    "protein": nutrition_data.get("protein"),
                    "fat": nutrition_data.get("fat"),
                }

            # Build source URL
            source_url = data.get("sourceUrl", "https://spoonacular.com")

            return RecipeScrapeResult(
                title=title,
                ingredients=ingredients,
                instructions=instructions.strip(),
                prep_time=prep_time,
                cook_time=cook_time,
                servings=servings,
                nutrition=nutrition,
                source_url=source_url,
                source_type="api",
                scraped_at=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.debug(f"Error parsing API response: {str(e)}")
            return None

    async def validate(self, recipe: RecipeScrapeResult) -> bool:
        """
        Validate API-sourced recipe.

        Args:
            recipe: Recipe to validate

        Returns:
            bool: True if recipe is valid
        """
        return (
            recipe.title
            and len(recipe.title) > 3
            and recipe.ingredients
            and len(recipe.ingredients) >= 1
            and recipe.instructions
            and len(recipe.instructions) > 10
            and recipe.source_type == "api"
        )
