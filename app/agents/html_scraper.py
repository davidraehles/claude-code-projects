"""
HTML Recipe Scraper - Extracts recipes from web pages

Uses schema.org/Recipe structured data and heuristic parsing to extract
recipes from HTML pages. Supports BeautifulSoup4 for parsing and fallback
heuristic extraction.

Features:
- Schema.org/Recipe JSON-LD extraction
- Fallback HTML heuristic parsing
- Image extraction
- Nutrition information parsing
- Error handling for malformed HTML
"""

import asyncio
import json
import logging
from typing import AsyncIterator, Optional
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
import re

from app.agents.recipe_harvester import RecipeScraper, RecipeScrapeResult

logger = logging.getLogger(__name__)


class HTMLRecipeScraper(RecipeScraper):
    """
    Scrapes recipes from HTML pages using schema.org/Recipe structured data.

    Prioritizes JSON-LD structured data but falls back to heuristic HTML parsing
    when structured data is not available.
    """

    def __init__(self, timeout: int = 30, db_session=None):
        """
        Initialize HTML recipe scraper.

        Args:
            timeout: HTTP request timeout in seconds
            db_session: SQLAlchemy async session (optional)
        """
        super().__init__(db_session=db_session)
        self.timeout = timeout
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

    async def scrape(self, url: str) -> AsyncIterator[RecipeScrapeResult]:
        """
        Scrape recipes from a web page URL.

        Args:
            url: URL of the web page containing recipe

        Yields:
            RecipeScrapeResult: Extracted recipe data

        Raises:
            ValueError: If URL is invalid
            httpx.HTTPError: If HTTP request fails
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {url}")

        retry_count = 0
        max_retries = 3

        while True:
            try:
                client = await self._get_client()

                self.logger.info(f"Fetching HTML from {url}")
                response = await client.get(url)
                response.raise_for_status()

                html_content = response.text

                # Try to extract recipes from JSON-LD first
                recipes = await self._extract_from_json_ld(html_content, url)

                if recipes:
                    for recipe in recipes:
                        yield recipe
                    return

                # Fallback to heuristic parsing
                recipe = await self._extract_from_html(html_content, url)
                if recipe:
                    yield recipe
                else:
                    self.logger.warning(f"No recipe found in {url}")

                return

            except asyncio.TimeoutError:
                should_retry = await self.handle_error(
                    asyncio.TimeoutError(f"Timeout fetching {url}"),
                    url,
                    retry_count,
                    max_retries,
                )
                if should_retry:
                    retry_count += 1
                else:
                    raise

            except httpx.HTTPError as e:
                should_retry = await self.handle_error(e, url, retry_count, max_retries)
                if should_retry:
                    retry_count += 1
                else:
                    raise

            except Exception as e:
                self.logger.error(f"Error scraping {url}: {str(e)}")
                raise

    async def _extract_from_json_ld(
        self, html_content: str, url: str
    ) -> list[RecipeScrapeResult]:
        """
        Extract recipes from JSON-LD structured data.

        Args:
            html_content: HTML page content
            url: Source URL

        Returns:
            list[RecipeScrapeResult]: Extracted recipes (may be empty)
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            recipes = []

            # Find all JSON-LD script tags
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)

                    # Handle both single recipes and lists
                    items = data if isinstance(data, list) else [data]

                    for item in items:
                        if item.get("@type") == "Recipe" or (
                            isinstance(item.get("@type"), list)
                            and "Recipe" in item.get("@type")
                        ):
                            recipe = self._parse_json_ld_recipe(item, url)
                            if recipe:
                                recipes.append(recipe)

                except json.JSONDecodeError as e:
                    self.logger.debug(f"Invalid JSON-LD: {str(e)}")
                    continue

            return recipes

        except Exception as e:
            self.logger.debug(f"Error extracting JSON-LD: {str(e)}")
            return []

    def _parse_json_ld_recipe(self, data: dict, url: str) -> Optional[RecipeScrapeResult]:
        """
        Parse a JSON-LD recipe object.

        Args:
            data: JSON-LD recipe data
            url: Source URL

        Returns:
            RecipeScrapeResult: Parsed recipe or None if invalid
        """
        try:
            title = data.get("name", "").strip()
            if not title:
                return None

            ingredients = []
            recipe_ingredients = data.get("recipeIngredient", [])
            if isinstance(recipe_ingredients, list):
                ingredients = [ing.strip() for ing in recipe_ingredients if ing]

            instructions = ""
            recipe_instructions = data.get("recipeInstructions", [])
            if isinstance(recipe_instructions, list):
                # Handle both string and HowToStep formats
                inst_parts = []
                for inst in recipe_instructions:
                    if isinstance(inst, dict):
                        inst_parts.append(inst.get("text", ""))
                    else:
                        inst_parts.append(str(inst))
                instructions = " ".join(inst_parts)
            else:
                instructions = str(recipe_instructions)

            instructions = instructions.strip()

            # Extract timing
            prep_time = self._parse_duration(data.get("prepTime"))
            cook_time = self._parse_duration(data.get("cookTime"))

            # Extract servings
            servings = None
            recipe_yield = data.get("recipeYield")
            if isinstance(recipe_yield, int):
                servings = recipe_yield
            elif isinstance(recipe_yield, str):
                # Try to extract number from "4 servings"
                match = re.search(r"(\d+)", recipe_yield)
                if match:
                    servings = int(match.group(1))

            # Extract nutrition
            nutrition = self._extract_nutrition(data.get("nutrition", {}))

            return RecipeScrapeResult(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                prep_time=prep_time,
                cook_time=cook_time,
                servings=servings,
                nutrition=nutrition if nutrition else None,
                source_url=url,
                source_type="html",
                scraped_at=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.debug(f"Error parsing JSON-LD recipe: {str(e)}")
            return None

    def _parse_duration(self, duration_str: Optional[str]) -> Optional[int]:
        """
        Parse ISO 8601 duration string to minutes.

        Args:
            duration_str: Duration string like "PT30M" or "PT1H30M"

        Returns:
            int: Duration in minutes (0 for < 1 minute) or None if invalid
        """
        if not duration_str:
            return None

        try:
            # Match ISO 8601 format: PT[nH][nM][nS]
            match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)

                total_minutes = hours * 60 + minutes + (seconds // 60)
                # Return 0 for durations < 1 minute (not None)
                return total_minutes

        except (AttributeError, ValueError):
            pass

        return None

    def _extract_nutrition(self, nutrition_data: dict) -> Optional[dict]:
        """
        Extract nutrition information from JSON-LD nutrition object.

        Args:
            nutrition_data: Nutrition data from recipe

        Returns:
            dict: Nutrition information or None
        """
        if not nutrition_data:
            return None

        try:
            nutrition = {}

            # Extract common nutrition values
            nutrition_fields = {
                "calories": "calories",
                "carbohydrateContent": "carbohydrates",
                "proteinContent": "protein",
                "fatContent": "fat",
                "fiberContent": "fiber",
                "sodiumContent": "sodium",
            }

            for json_key, friendly_key in nutrition_fields.items():
                if json_key in nutrition_data:
                    value = nutrition_data[json_key]
                    if isinstance(value, (int, float)):
                        nutrition[friendly_key] = value

            return nutrition if nutrition else None

        except Exception as e:
            self.logger.debug(f"Error extracting nutrition: {str(e)}")
            return None

    async def _extract_from_html(
        self, html_content: str, url: str
    ) -> Optional[RecipeScrapeResult]:
        """
        Extract recipe using heuristic HTML parsing.

        Falls back to this method when structured data is not available.

        Args:
            html_content: HTML page content
            url: Source URL

        Returns:
            RecipeScrapeResult: Extracted recipe or None
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Try to find title from common HTML patterns
            title = None
            for tag in soup.find_all(["h1", "h2"]):
                text = tag.get_text(strip=True)
                if len(text) > 3 and len(text) < 200:
                    title = text
                    break

            if not title:
                # Try to get from page title
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)

            if not title or len(title.strip()) < 3:
                return None

            # Try to find ingredients
            ingredients = []
            for tag in soup.find_all(["ul", "ol"]):
                items = tag.find_all("li")
                if len(items) > 2:
                    # Likely an ingredient list
                    for item in items:
                        text = item.get_text(strip=True)
                        if text and len(text) > 2:
                            ingredients.append(text)
                    break

            if not ingredients:
                # Didn't find useful ingredients
                return None

            # Try to find instructions
            instructions = ""
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    instructions = text
                    break

            if not instructions:
                instructions = "See source page for instructions"

            return RecipeScrapeResult(
                title=title.strip(),
                ingredients=ingredients[:20],  # Limit to first 20
                instructions=instructions.strip(),
                source_url=url,
                source_type="html",
                scraped_at=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.debug(f"Error with heuristic parsing: {str(e)}")
            return None

    async def validate(self, recipe: RecipeScrapeResult) -> bool:
        """
        Validate HTML-scraped recipe.

        Args:
            recipe: Recipe to validate

        Returns:
            bool: True if recipe is valid for HTML scraping
        """
        # HTML scraping may have less complete data, so be lenient
        return (
            recipe.title
            and len(recipe.title) > 3
            and recipe.ingredients
            and len(recipe.ingredients) > 0
            and recipe.instructions
            and len(recipe.instructions) > 10
        )
