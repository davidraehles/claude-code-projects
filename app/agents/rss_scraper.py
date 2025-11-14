"""
RSS Recipe Scraper - Polls RSS feeds for recipe updates

Monitors RSS feeds for recipe blog updates and extracts recipe information
from feed entries. Supports automatic polling and update detection.

Features:
- RSS/Atom feed parsing
- Recipe detection heuristics
- Update tracking
- Feed polling with intervals
- Error handling and recovery
"""

import logging
import asyncio
from typing import AsyncIterator, Optional
from datetime import datetime
from urllib.parse import urljoin

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.agents.recipe_harvester import RecipeScraper, RecipeScrapeResult

logger = logging.getLogger(__name__)


class RSSRecipeScraper(RecipeScraper):
    """
    Scrapes recipes from RSS feeds.

    Monitors recipe blog RSS feeds for new content and extracts recipe
    information from feed entries.
    """

    def __init__(self, timeout: int = 30, db_session=None):
        """
        Initialize RSS recipe scraper.

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

    async def scrape(self, feed_url: str) -> AsyncIterator[RecipeScrapeResult]:
        """
        Scrape recipes from RSS feed.

        Args:
            feed_url: URL of RSS feed

        Yields:
            RecipeScrapeResult: Recipe data from feed entries

        Raises:
            ValueError: If feed_url is invalid
            httpx.HTTPError: If feed fetch fails
        """
        if not feed_url or not isinstance(feed_url, str):
            raise ValueError("Feed URL must be a non-empty string")

        if not feed_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {feed_url}")

        retry_count = 0
        max_retries = 3

        while True:
            try:
                client = await self._get_client()

                self.logger.info(f"Fetching RSS feed: {feed_url}")
                response = await client.get(feed_url)
                response.raise_for_status()

                feed_content = response.text

                # Parse feed
                feed = feedparser.parse(feed_content)

                if feed.bozo:
                    self.logger.warning(f"Feed parsing had issues: {feed.bozo_exception}")

                # Extract recipes from feed entries
                recipe_count = 0
                for entry in feed.entries:
                    recipes = await self._extract_recipes_from_entry(entry, feed_url)
                    for recipe in recipes:
                        yield recipe
                        recipe_count += 1

                self.logger.info(f"Extracted {recipe_count} recipes from feed")
                return

            except asyncio.TimeoutError:
                should_retry = await self.handle_error(
                    asyncio.TimeoutError(f"Timeout fetching feed {feed_url}"),
                    feed_url,
                    retry_count,
                    max_retries,
                )
                if should_retry:
                    retry_count += 1
                else:
                    raise

            except httpx.HTTPError as e:
                should_retry = await self.handle_error(e, feed_url, retry_count, max_retries)
                if should_retry:
                    retry_count += 1
                else:
                    raise

            except Exception as e:
                self.logger.error(f"Error scraping feed {feed_url}: {str(e)}")
                raise

    async def _extract_recipes_from_entry(
        self, entry: feedparser.munch.Munch, base_url: str
    ) -> list[RecipeScrapeResult]:
        """
        Extract recipes from a single feed entry.

        Args:
            entry: Feed entry object
            base_url: Base URL for resolving relative links

        Returns:
            list[RecipeScrapeResult]: Recipes found in entry
        """
        recipes = []

        try:
            # Get entry title and link
            entry_title = entry.get("title", "").strip()
            entry_link = entry.get("link", "").strip()

            # Check if this entry might contain a recipe
            if not self._is_recipe_entry(entry):
                return recipes

            # Try to extract recipe from summary/description
            summary = entry.get("summary", "")
            if not summary:
                summary = entry.get("description", "")

            # If we have a link, try to scrape the full page
            if entry_link:
                recipe = await self._scrape_entry_link(entry_link, base_url)
                if recipe:
                    recipes.append(recipe)

            # Also try to extract from summary text
            if summary:
                recipe = self._extract_from_summary(summary, entry_link, entry_title)
                if recipe and recipe not in recipes:
                    recipes.append(recipe)

        except Exception as e:
            self.logger.debug(f"Error extracting recipe from entry: {str(e)}")

        return recipes

    def _is_recipe_entry(self, entry: feedparser.munch.Munch) -> bool:
        """
        Heuristically detect if feed entry is about a recipe.

        Args:
            entry: Feed entry object

        Returns:
            bool: True if entry likely contains recipe
        """
        # Check title and summary for recipe keywords
        keywords = [
            "recipe",
            "cook",
            "bake",
            "ingredient",
            "instruction",
            "how to make",
            "preparation",
        ]

        text_to_check = (
            entry.get("title", "") + " " + entry.get("summary", "")
        ).lower()

        # Check for recipe keywords
        for keyword in keywords:
            if keyword in text_to_check:
                return True

        # Check for structured data hints
        if "recipeingredient" in text_to_check or "recipeinstructions" in text_to_check:
            return True

        return False

    async def _scrape_entry_link(self, link: str, base_url: str) -> Optional[RecipeScrapeResult]:
        """
        Scrape recipe from entry link.

        Args:
            link: Entry link URL
            base_url: Base URL for resolving relative links

        Returns:
            RecipeScrapeResult: Recipe or None if scraping fails
        """
        try:
            # Resolve relative URLs
            full_url = urljoin(base_url, link)

            client = await self._get_client()
            response = await client.get(full_url)
            response.raise_for_status()

            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract recipe from page
            return self._extract_recipe_from_html(soup, full_url)

        except Exception as e:
            self.logger.debug(f"Error scraping entry link {link}: {str(e)}")
            return None

    def _extract_recipe_from_html(
        self, soup: BeautifulSoup, url: str
    ) -> Optional[RecipeScrapeResult]:
        """
        Extract recipe from BeautifulSoup parsed HTML.

        Args:
            soup: Parsed HTML
            url: Source URL

        Returns:
            RecipeScrapeResult: Recipe or None
        """
        try:
            # Try to find title
            title = None
            for tag in soup.find_all(["h1", "h2"]):
                text = tag.get_text(strip=True)
                if 3 < len(text) < 200:
                    title = text
                    break

            if not title:
                return None

            # Try to find ingredients
            ingredients = []
            for tag in soup.find_all(["ul", "ol"]):
                items = tag.find_all("li")
                if 2 < len(items) < 50:
                    for item in items:
                        text = item.get_text(strip=True)
                        if text and len(text) > 2:
                            ingredients.append(text)
                    break

            if not ingredients:
                return None

            # Try to find instructions
            instructions = ""
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if 20 < len(text) < 1000:
                    instructions = text
                    break

            if not instructions:
                instructions = "See source page for instructions"

            return RecipeScrapeResult(
                title=title.strip(),
                ingredients=ingredients[:30],
                instructions=instructions.strip(),
                source_url=url,
                source_type="rss",
                scraped_at=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.debug(f"Error extracting recipe from HTML: {str(e)}")
            return None

    def _extract_from_summary(
        self, summary: str, link: str, title: str
    ) -> Optional[RecipeScrapeResult]:
        """
        Extract recipe information from feed summary.

        Args:
            summary: Entry summary/description
            link: Entry link
            title: Entry title

        Returns:
            RecipeScrapeResult: Recipe or None
        """
        try:
            # Parse HTML in summary
            soup = BeautifulSoup(summary, "html.parser")
            text = soup.get_text(separator=" ", strip=True)

            # Very basic extraction - would need much improvement
            if len(text) < 20:
                return None

            # Split into ingredients and instructions (naive approach)
            ingredients = []
            parts = text.split("•")

            if len(parts) > 1:
                for part in parts[1:]:
                    part = part.strip()
                    if 2 < len(part) < 200:
                        ingredients.append(part)

            if not ingredients:
                # Try another delimiter
                ingredients = [s.strip() for s in text.split(",")[1:5]]

            if not ingredients:
                return None

            return RecipeScrapeResult(
                title=title.strip(),
                ingredients=ingredients[:10],
                instructions=text[:500],
                source_url=link,
                source_type="rss",
                scraped_at=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.debug(f"Error extracting from summary: {str(e)}")
            return None

    async def validate(self, recipe: RecipeScrapeResult) -> bool:
        """
        Validate RSS-sourced recipe.

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
            and recipe.source_type == "rss"
        )
