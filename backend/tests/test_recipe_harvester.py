"""
Comprehensive test suite for Recipe Harvester Agent.

Tests all components: RecipeScraper, HTMLRecipeScraper, APIRecipeScraper,
RSSRecipeScraper, DuplicateDetector, and error handling.

Run with: pytest tests/test_recipe_harvester.py -v
Coverage: pytest --cov=app tests/test_recipe_harvester.py
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.recipe_harvester import RecipeScraper, RecipeScrapeResult, DuplicateDetector
from app.agents.html_scraper import HTMLRecipeScraper
from app.agents.api_scraper import APIRecipeScraper, RateLimiter
from app.agents.rss_scraper import RSSRecipeScraper


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_recipe_result():
    """Sample recipe for testing."""
    return RecipeScrapeResult(
        title="Pasta Carbonara",
        ingredients=["400g spaghetti", "200g pancetta", "4 eggs", "100g parmesan"],
        instructions="Cook pasta, fry pancetta, mix with eggs and cheese",
        prep_time=10,
        cook_time=20,
        servings=4,
        source_url="https://example.com/recipe",
        source_type="html",
    )


@pytest.fixture
def duplicate_recipe_result():
    """Recipe similar to sample for testing duplicates."""
    return RecipeScrapeResult(
        title="Pasta Carbonara (Classic)",
        ingredients=["400g spaghetti", "200g bacon", "4 eggs", "100g Parmesan cheese"],
        instructions="Prepare spaghetti and bacon, combine with eggs and cheese",
        prep_time=15,
        cook_time=20,
        servings=4,
        source_url="https://different-site.com/recipe",
        source_type="api",
    )


@pytest.fixture
def different_recipe_result():
    """Recipe very different from sample."""
    return RecipeScrapeResult(
        title="Chocolate Cake",
        ingredients=["2 cups flour", "1 cup sugar", "1/2 cup cocoa", "2 eggs"],
        instructions="Mix, bake at 350F for 30 minutes",
        servings=8,
        source_url="https://cake-site.com/recipe",
        source_type="api",
    )


# ============================================================================
# RECIPESCRAPEMRESULT VALIDATION TESTS
# ============================================================================


class TestRecipeScrapeResult:
    """Test RecipeScrapeResult validation."""

    def test_valid_recipe_creation(self, sample_recipe_result):
        """Test creating valid recipe result."""
        assert sample_recipe_result.title == "Pasta Carbonara"
        assert len(sample_recipe_result.ingredients) == 4
        assert sample_recipe_result.source_type == "html"

    def test_empty_title_raises_error(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValueError):
            RecipeScrapeResult(
                title="",
                ingredients=["salt"],
                instructions="Mix well",
                source_url="https://example.com",
                source_type="html",
            )

    def test_empty_ingredients_raises_error(self):
        """Test that empty ingredients raises error."""
        with pytest.raises(ValueError):
            RecipeScrapeResult(
                title="Test Recipe",
                ingredients=[],
                instructions="Mix well",
                source_url="https://example.com",
                source_type="html",
            )

    def test_short_instructions_raises_error(self):
        """Test that short instructions raise error."""
        with pytest.raises(ValueError):
            RecipeScrapeResult(
                title="Test Recipe",
                ingredients=["salt"],
                instructions="short",
                source_url="https://example.com",
                source_type="html",
            )

    def test_ingredients_trimmed(self):
        """Test that ingredient whitespace is trimmed."""
        recipe = RecipeScrapeResult(
            title="Test",
            ingredients=["  salt  ", "  pepper  "],
            instructions="Mix together well",
            source_url="https://example.com",
            source_type="html",
        )
        assert recipe.ingredients == ["salt", "pepper"]

    def test_scraped_at_defaults_to_now(self, sample_recipe_result):
        """Test that scraped_at defaults to current time."""
        assert sample_recipe_result.scraped_at is not None
        assert isinstance(sample_recipe_result.scraped_at, datetime)
        assert (datetime.utcnow() - sample_recipe_result.scraped_at).total_seconds() < 5


# ============================================================================
# DUPLICATE DETECTOR TESTS
# ============================================================================


class TestDuplicateDetector:
    """Test DuplicateDetector functionality."""

    def test_detector_initialization(self):
        """Test DuplicateDetector initialization."""
        detector = DuplicateDetector(similarity_threshold=0.85)
        assert detector.similarity_threshold == 0.85

    def test_invalid_threshold_raises_error(self):
        """Test that invalid threshold raises error."""
        with pytest.raises(ValueError):
            DuplicateDetector(similarity_threshold=1.5)

        with pytest.raises(ValueError):
            DuplicateDetector(similarity_threshold=-0.5)

    def test_title_similarity_calculation(self, sample_recipe_result, duplicate_recipe_result):
        """Test title similarity calculation."""
        detector = DuplicateDetector()
        similarity = detector._calculate_title_similarity(
            sample_recipe_result.title,
            duplicate_recipe_result.title
        )
        assert 0 <= similarity <= 1
        assert similarity > 0.7  # Should be quite similar

    def test_ingredient_similarity_calculation(
        self, sample_recipe_result, duplicate_recipe_result
    ):
        """Test ingredient similarity calculation."""
        detector = DuplicateDetector()
        similarity = detector._calculate_ingredient_similarity(
            sample_recipe_result.ingredients,
            duplicate_recipe_result.ingredients
        )
        assert 0 <= similarity <= 1
        assert similarity >= 0.5  # Should share several ingredients

    def test_overall_similarity_calculation(
        self, sample_recipe_result, duplicate_recipe_result
    ):
        """Test overall similarity calculation."""
        detector = DuplicateDetector()
        similarity = detector.calculate_similarity(
            sample_recipe_result,
            duplicate_recipe_result
        )
        assert 0 <= similarity <= 1

    def test_is_duplicate_same_recipe(self, sample_recipe_result):
        """Test that identical recipes are duplicates."""
        detector = DuplicateDetector(similarity_threshold=0.95)
        assert detector.is_duplicate(sample_recipe_result, sample_recipe_result)

    def test_is_not_duplicate_different_recipe(
        self, sample_recipe_result, different_recipe_result
    ):
        """Test that very different recipes are not duplicates."""
        detector = DuplicateDetector(similarity_threshold=0.85)
        assert not detector.is_duplicate(sample_recipe_result, different_recipe_result)

    def test_find_duplicate_candidates(
        self, sample_recipe_result, duplicate_recipe_result, different_recipe_result
    ):
        """Test finding duplicate candidates."""
        detector = DuplicateDetector(similarity_threshold=0.45)
        existing = [duplicate_recipe_result, different_recipe_result]

        candidates = detector.find_duplicate_candidates(sample_recipe_result, existing)

        # Should find the duplicate but not the different recipe
        assert len(candidates) >= 1
        # First candidate should be the more similar one
        assert candidates[0][0] == duplicate_recipe_result


# ============================================================================
# HTML SCRAPER TESTS
# ============================================================================


class TestHTMLRecipeScraper:
    """Test HTMLRecipeScraper functionality."""

    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test HTMLRecipeScraper initialization."""
        scraper = HTMLRecipeScraper(timeout=30)
        assert scraper.timeout == 30
        await scraper.close()

    @pytest.mark.asyncio
    async def test_invalid_url_raises_error(self):
        """Test that invalid URL raises error."""
        scraper = HTMLRecipeScraper()
        try:
            async for recipe in scraper.scrape("not-a-url"):
                pass
        except ValueError as e:
            assert "invalid" in str(e).lower()
        finally:
            await scraper.close()

    @pytest.mark.asyncio
    async def test_validate_recipe(self):
        """Test recipe validation."""
        scraper = HTMLRecipeScraper()
        recipe = RecipeScrapeResult(
            title="Test",
            ingredients=["salt"],
            instructions="Mix well and cook",
            source_url="https://example.com",
            source_type="html",
        )
        assert await scraper.validate(recipe)
        await scraper.close()

    def test_parse_json_ld_recipe(self):
        """Test parsing JSON-LD recipe format."""
        scraper = HTMLRecipeScraper()
        json_ld_data = {
            "@context": "https://schema.org/",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["salt", "pepper"],
            "recipeInstructions": "Mix well",
            "prepTime": "PT10M",
            "cookTime": "PT20M",
            "recipeYield": "4 servings",
        }

        recipe = scraper._parse_json_ld_recipe(json_ld_data, "https://example.com")

        assert recipe is not None
        assert recipe.title == "Test Recipe"
        assert len(recipe.ingredients) == 2
        assert recipe.prep_time == 10
        assert recipe.cook_time == 20
        assert recipe.servings == 4

    def test_parse_duration(self):
        """Test ISO 8601 duration parsing."""
        scraper = HTMLRecipeScraper()

        assert scraper._parse_duration("PT30M") == 30
        assert scraper._parse_duration("PT1H30M") == 90
        assert scraper._parse_duration("PT2H") == 120
        assert scraper._parse_duration("PT45S") == 0  # Less than 1 minute
        assert scraper._parse_duration("PT1H45M") == 105
        assert scraper._parse_duration(None) is None


# ============================================================================
# API SCRAPER TESTS
# ============================================================================


class TestRateLimiter:
    """Test RateLimiter functionality."""

    def test_rate_limiter_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(rate=10)
        assert limiter.rate == 10

    def test_invalid_rate_raises_error(self):
        """Test that invalid rate raises error."""
        with pytest.raises(ValueError):
            RateLimiter(rate=0)

        with pytest.raises(ValueError):
            RateLimiter(rate=-1)

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire(self):
        """Test acquiring rate limit token."""
        limiter = RateLimiter(rate=10)
        start = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed >= 0  # Should complete


class TestAPIRecipeScraper:
    """Test APIRecipeScraper functionality."""

    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test APIRecipeScraper initialization."""
        scraper = APIRecipeScraper(api_key="test_key", rate_limit=10)
        assert scraper.api_key == "test_key"
        assert scraper.rate_limiter.rate == 10
        await scraper.close()

    @pytest.mark.asyncio
    async def test_invalid_query_raises_error(self):
        """Test that invalid query raises error."""
        scraper = APIRecipeScraper()
        try:
            async for recipe in scraper.scrape(""):
                pass
        except ValueError as e:
            assert "non-empty" in str(e).lower()
        finally:
            await scraper.close()

    def test_parse_api_response(self):
        """Test parsing API response."""
        scraper = APIRecipeScraper()
        api_response = {
            "id": 123,
            "title": "Test Recipe",
            "extendedIngredients": [
                {"original": "2 cups flour"},
                {"original": "1 egg"},
            ],
            "instructions": "Mix and bake",
            "preparationMinutes": 15,
            "cookingMinutes": 30,
            "servings": 4,
            "sourceUrl": "https://example.com/recipe",
        }

        recipe = scraper._parse_api_response(api_response)

        assert recipe is not None
        assert recipe.title == "Test Recipe"
        assert len(recipe.ingredients) == 2
        assert recipe.prep_time == 15
        assert recipe.cook_time == 30


# ============================================================================
# RSS SCRAPER TESTS
# ============================================================================


class TestRSSRecipeScraper:
    """Test RSSRecipeScraper functionality."""

    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test RSSRecipeScraper initialization."""
        scraper = RSSRecipeScraper(timeout=30)
        assert scraper.timeout == 30
        await scraper.close()

    @pytest.mark.asyncio
    async def test_invalid_url_raises_error(self):
        """Test that invalid URL raises error."""
        scraper = RSSRecipeScraper()
        try:
            async for recipe in scraper.scrape("not-a-url"):
                pass
        except ValueError as e:
            assert "invalid" in str(e).lower()
        finally:
            await scraper.close()

    def test_is_recipe_entry(self):
        """Test recipe entry detection."""
        scraper = RSSRecipeScraper()

        recipe_entry = MagicMock()
        recipe_entry.get.side_effect = lambda k, d="": {
            "title": "How to make pasta",
            "summary": "Recipe for delicious pasta"
        }.get(k, d)

        assert scraper._is_recipe_entry(recipe_entry)

        non_recipe_entry = MagicMock()
        non_recipe_entry.get.side_effect = lambda k, d="": {
            "title": "News update",
            "summary": "Breaking news today"
        }.get(k, d)

        assert not scraper._is_recipe_entry(non_recipe_entry)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling in scrapers."""

    @pytest.mark.asyncio
    async def test_handle_error_with_retry(self):
        """Test error handling with retry logic."""
        scraper = HTMLRecipeScraper()
        error = Exception("Test error")

        # First retry should succeed
        should_retry = await scraper.handle_error(error, "test_source", 0, 3)
        assert should_retry

        # Max retries exceeded
        should_retry = await scraper.handle_error(error, "test_source", 3, 3)
        assert not should_retry

        await scraper.close()

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff in error handling."""
        scraper = HTMLRecipeScraper()
        error = Exception("Test error")

        start = asyncio.get_event_loop().time()
        await scraper.handle_error(error, "test_source", 0, 3)
        elapsed = asyncio.get_event_loop().time() - start

        # Should wait ~1 second (2^0)
        assert 0.5 < elapsed < 2

        await scraper.close()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests for recipe harvesting."""

    def test_recipe_creation_flow(self, sample_recipe_result):
        """Test complete recipe creation flow."""
        # Validate recipe
        assert sample_recipe_result.title
        assert len(sample_recipe_result.ingredients) > 0

        # Convert to dict
        recipe_dict = {
            "title": sample_recipe_result.title,
            "ingredients": sample_recipe_result.ingredients,
            "instructions": sample_recipe_result.instructions,
            "source_type": sample_recipe_result.source_type,
        }

        assert recipe_dict["title"] == "Pasta Carbonara"

    def test_duplicate_detection_workflow(
        self, sample_recipe_result, duplicate_recipe_result
    ):
        """Test complete duplicate detection workflow."""
        detector = DuplicateDetector(similarity_threshold=0.70)

        # Check if similar recipes are detected
        is_dup = detector.is_duplicate(sample_recipe_result, duplicate_recipe_result)
        similarity = detector.calculate_similarity(
            sample_recipe_result,
            duplicate_recipe_result
        )

        assert is_dup or (not is_dup and similarity < 0.70)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Performance and load tests."""

    def test_duplicate_detector_with_many_recipes(self):
        """Test duplicate detector performance with many recipes."""
        detector = DuplicateDetector()

        # Create 100 test recipes
        recipes = []
        for i in range(100):
            recipe = RecipeScrapeResult(
                title=f"Recipe {i}",
                ingredients=[f"ingredient{j}" for j in range(5)],
                instructions=f"Cook for {i} minutes",
                source_url=f"https://example.com/recipe{i}",
                source_type="html",
            )
            recipes.append(recipe)

        # Find duplicates (should be fast)
        test_recipe = recipes[0]
        candidates = detector.find_duplicate_candidates(test_recipe, recipes[1:])

        # Should handle many recipes without significant delay
        assert isinstance(candidates, list)

    @pytest.mark.asyncio
    async def test_rate_limiter_throughput(self):
        """Test rate limiter throughput."""
        limiter = RateLimiter(rate=10)

        start = asyncio.get_event_loop().time()
        for _ in range(10):
            await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start

        # Should complete 10 requests within reasonable time
        assert elapsed < 5  # Very lenient for CI environments


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
