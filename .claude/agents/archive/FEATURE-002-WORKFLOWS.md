# ReAct Workflows for Feature 002: Recipe & Meal Planning System

This document provides detailed, real-world workflows specifically tailored to implementing the **Recipe & Meal Planning SaaS** using the ReAct agent system.

---

## Workflow 1: Recipe Harvester Agent Implementation

### User Request

"Implement the Recipe Harvester Agent that can scrape recipes from multiple sources (web, APIs, RSS feeds) with duplicate detection"

### Step-by-Step Execution

#### Step 1: Specification Analysis

```bash
/spec-analyze 002 "Recipe Harvester Agent with web scraping and duplicate detection"
```

**Spec Analyzer Agent:**
1. Reads `002-recipe-system/spec.md` and `data-model.md`
2. Extracts requirements for Recipe Harvester:
   - Parse recipes from HTML (schema.org/Recipe)
   - Handle API integrations (rate limiting)
   - Poll RSS feeds for recipe updates
   - Detect and merge duplicates
   - Validate recipe data completeness
3. Identifies data models:
   - Recipe entity with ingredients, instructions, nutrition
   - RecipeSource (URL source tracking)
   - RecipeDuplicate (duplicate management)
4. Identifies constraints:
   - Async/await for performance
   - Error handling for network failures
   - Rate limiting for external APIs
   - Transaction handling for duplicates
5. Suggests test scenarios:
   - Parse various HTML structures
   - Handle API errors gracefully
   - Detect duplicates accurately
   - Manage rate limiting
   - Feed update cycling

**Output**:
```
✓ Feature: 002 (Recipe System)
✓ Agent: Recipe Harvester

Requirements:
├─ Functional
│  ├─ Parse recipes from web pages (schema.org)
│  ├─ Integrate with recipe APIs
│  ├─ Poll RSS feeds
│  ├─ Detect and merge duplicates
│  └─ Store recipe metadata
├─ Non-Functional
│  ├─ Handle 100+ recipes/minute throughput
│  ├─ Retry failed fetches with backoff
│  ├─ Rate limiting for external APIs
│  └─ Transaction safety for duplicates
└─ Constraints
   ├─ Async/await required (no blocking I/O)
   ├─ Database transactions for atomic writes
   ├─ Error recovery without data loss
   └─ Monitoring with Prometheus metrics

Test Scenarios:
✓ Parse 50+ recipe formats
✓ Handle network timeouts
✓ Detect duplicate recipes (95% accuracy)
✓ Rate limit enforcement
✓ RSS feed update cycles
```

---

#### Step 2: Task Decomposition

```bash
/task-decompose 002-001-01 "Recipe Harvester with parallel sources"
```

**Router Agent:**
1. Decomposes Recipe Harvester into subtasks:
   ```
   Task 1.1: Create RecipeScraper base class (Backend Dev)
   Task 1.2: Implement HTML parser (Web scraping)
   Task 1.3: Implement API connector (Rate limiting)
   Task 1.4: Implement RSS feed poller
   Task 1.5: Implement duplicate detection algorithm
   Task 1.6: Implement recipe validation
   Task 1.7: Create database models (Task 1.1 dependency)
   Task 1.8: Create Alembic migration (Task 1.7 dependency)
   Task 1.9: Generate unit tests (Task 1.1-1.6)
   Task 1.10: Generate integration tests (After 1.8)
   Task 1.11: Update documentation
   ```

2. Creates dependency graph:
   ```
   Task 1.1 (Base) ──→ Task 1.2, 1.3, 1.4, 1.5, 1.6
         ↓
   Task 1.7 (Models) ──→ Task 1.8 (Migration)
         ↓
   Task 1.9 (Unit Tests) ──→ Task 1.10 (Integration)
         ↓
   Task 1.11 (Documentation)
   ```

3. Identifies parallelization:
   - **Wave 1**: Create base class (15 mins)
   - **Wave 2** (parallel, starts after Wave 1):
     - HTML parser (20 mins)
     - API connector (20 mins)
     - RSS poller (15 mins)
     - Duplicate detector (25 mins)
     - Validation (10 mins)
   - **Wave 3** (parallel, after Wave 2):
     - Database models (10 mins)
     - Migration (5 mins)
   - **Wave 4** (parallel):
     - Unit tests (30 mins)
     - Documentation (15 mins)
   - **Wave 5**: Integration tests (25 mins)

**Timeline**:
```
Sequential: 15 + (20+20+15+25+10) + 10 + 5 + 30 + 25 + 15 = 190 mins
Parallel:   15 + 25 + 15 + 25 + 30 = 110 mins (agents work simultaneously)
Speedup:    1.7x faster
```

---

#### Step 3: Parallel Agent Assignments

**Wave 1: Base Class** (15 mins)

```bash
/gen-endpoint /recipes/harvest POST Recipe 002
```

Backend Dev Agent:
```python
# app/agents/recipe_harvester.py
from typing import AsyncIterator
from pydantic import BaseModel
from abc import ABC, abstractmethod

class RecipeScrapeResult(BaseModel):
    """Result of recipe scraping attempt"""
    title: str
    ingredients: list[str]
    instructions: str
    nutrition: dict | None = None
    source_url: str
    scraped_at: datetime

class RecipeScraper(ABC):
    """Base class for recipe scrapers"""

    def __init__(self, db_session, logger):
        self.db = db_session
        self.logger = logger

    @abstractmethod
    async def scrape(self, source: str) -> AsyncIterator[RecipeScrapeResult]:
        """Scrape recipes from source"""
        pass

    @abstractmethod
    async def validate(self, recipe: RecipeScrapeResult) -> bool:
        """Validate recipe data completeness"""
        pass

    async def save_recipe(self, recipe: RecipeScrapeResult) -> Recipe:
        """Save to database with error handling"""
        pass
```

**Wave 2: Parallel Component Development** (25 mins)

```bash
# Run 4 agents in parallel
/gen-endpoint /recipes/scrape/html POST Recipe 002
/gen-endpoint /recipes/scrape/api POST Recipe 002
/gen-endpoint /recipes/scrape/rss POST Recipe 002
/gen-endpoint /recipes/duplicates/detect POST Recipe 002
```

**Task 1.2: HTML Parser** (Backend Dev - parallel)
```python
# app/agents/scrapers/html_scraper.py
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me

class HTMLRecipeScraper(RecipeScraper):
    """Scrapes recipes from HTML using schema.org/Recipe"""

    async def scrape(self, url: str) -> RecipeScrapeResult:
        """Extract recipe from webpage"""
        scraper = scrape_me(url)
        return RecipeScrapeResult(
            title=scraper.title(),
            ingredients=scraper.ingredients(),
            instructions=scraper.instructions(),
            nutrition=scraper.nutrients(),
            source_url=url,
        )

    async def validate(self, recipe: RecipeScrapeResult) -> bool:
        """Validate recipe has required fields"""
        return (
            recipe.title and
            len(recipe.ingredients) > 0 and
            len(recipe.instructions) > 20
        )
```

**Task 1.3: API Connector** (Backend Dev - parallel)
```python
# app/agents/scrapers/api_scraper.py
import httpx
import asyncio

class APIRecipeScraper(RecipeScraper):
    """Integrates with recipe APIs (Spoonacular, etc)"""

    def __init__(self, api_key: str, rate_limit: int = 10):
        self.api_key = api_key
        self.rate_limiter = asyncio.Semaphore(rate_limit)

    async def scrape(self, query: str) -> AsyncIterator[RecipeScrapeResult]:
        """Search and fetch recipes from API"""
        async with self.rate_limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.spoonacular.com/recipes/search",
                    params={"query": query, "apiKey": self.api_key}
                )
                recipes = response.json()
                for recipe_id in recipes:
                    yield await self._fetch_recipe(client, recipe_id)

    async def _fetch_recipe(self, client: httpx.AsyncClient, recipe_id: int):
        """Fetch detailed recipe from API"""
        # Implementation with error handling and retry logic
        pass
```

**Task 1.4: RSS Feed Poller** (Backend Dev - parallel)
```python
# app/agents/scrapers/rss_scraper.py
import feedparser

class RSSRecipeScraper(RecipeScraper):
    """Polls RSS feeds for recipe updates"""

    async def scrape(self, feed_url: str) -> AsyncIterator[RecipeScrapeResult]:
        """Parse RSS feed for recipes"""
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if self._is_recipe(entry):
                yield await self._extract_recipe(entry)

    def _is_recipe(self, entry) -> bool:
        """Check if feed entry is a recipe"""
        keywords = ['recipe', 'cook', 'ingredient', 'instruction']
        text = (entry.title + entry.summary).lower()
        return any(kw in text for kw in keywords)

    async def _extract_recipe(self, entry) -> RecipeScrapeResult:
        """Extract recipe data from feed entry"""
        # Parse HTML embedded in feed entry
        pass
```

**Task 1.5: Duplicate Detection** (Backend Dev - parallel)
```python
# app/agents/duplicate_detector.py
from difflib import SequenceMatcher

class DuplicateDetector:
    """Detects and merges duplicate recipes"""

    async def find_duplicates(self, recipe: RecipeScrapeResult) -> list[Recipe]:
        """Find existing recipes that match this one"""
        # Find recipes with similar titles
        query = select(Recipe).where(
            Recipe.title.ilike(f"%{recipe.title}%")
        )
        candidates = await db.execute(query)

        # Score similarity
        matches = []
        for candidate in candidates:
            score = self._calculate_similarity(recipe, candidate)
            if score > 0.85:  # 85% similarity threshold
                matches.append((candidate, score))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _calculate_similarity(self, recipe1, recipe2) -> float:
        """Calculate similarity score (0-1)"""
        title_sim = SequenceMatcher(
            None, recipe1.title, recipe2.title
        ).ratio()
        ingredient_sim = len(
            set(recipe1.ingredients) & set(recipe2.ingredients)
        ) / max(len(recipe1.ingredients), len(recipe2.ingredients))
        return (title_sim * 0.6) + (ingredient_sim * 0.4)

    async def merge_recipes(self, primary: Recipe, duplicate: Recipe):
        """Merge duplicate into primary recipe"""
        # Keep highest quality source
        # Combine ingredients lists
        # Mark duplicate as merged
        pass
```

**Wave 3: Database & Migrations** (15 mins, parallel with Wave 2)

```bash
/gen-endpoint /recipes POST Recipe 002
```

Creates database models and migration:
```python
# app/models/recipe.py
class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    ingredients: Mapped[list[str]] = mapped_column(JSON)
    instructions: Mapped[str] = mapped_column(Text)

    source_url: Mapped[str] = mapped_column(String(2000))
    source_type: Mapped[str] = mapped_column(
        String(50)  # 'html', 'api', 'rss'
    )

    # Duplicate tracking
    duplicate_of_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id"))
    duplicates: Mapped[list["Recipe"]] = relationship(
        "Recipe",
        remote_side=[id],
        foreign_keys=[duplicate_of_id]
    )

    nutrition: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

# alembic migration
def upgrade():
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False, unique=True),
        sa.Column('ingredients', sa.JSON(), nullable=False),
        # ... other columns
    )
    op.create_index(op.f('ix_recipes_source_url'), 'recipes', ['source_url'])
    op.create_index(op.f('ix_recipes_duplicate_of_id'), 'recipes', ['duplicate_of_id'])
```

**Wave 4: Testing & Documentation** (45 mins, parallel)

**Task 1.9: Unit Tests** (Testing Agent - parallel)

```bash
/gen-tests app/agents/recipe_harvester.py all
```

```python
# tests/test_recipe_harvester.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_html_scraper_parses_recipe():
    """Test HTML scraper extracts recipe correctly"""
    scraper = HTMLRecipeScraper()

    result = await scraper.scrape("https://example.com/recipe")

    assert result.title == "Pasta Carbonara"
    assert len(result.ingredients) > 0
    assert len(result.instructions) > 0

@pytest.mark.asyncio
async def test_duplicate_detection_finds_matches():
    """Test duplicate detector identifies similar recipes"""
    detector = DuplicateDetector()

    recipe1 = RecipeScrapeResult(
        title="Pasta Carbonara",
        ingredients=["pasta", "eggs", "bacon", "parmesan"],
        instructions="Cook and mix"
    )
    recipe2 = Recipe(
        title="Pasta Carbonara (Classic)",
        ingredients=["pasta", "eggs", "bacon", "parmesan", "black pepper"]
    )

    similarity = detector._calculate_similarity(recipe1, recipe2)
    assert similarity > 0.85

@pytest.mark.asyncio
async def test_api_scraper_respects_rate_limit():
    """Test API scraper enforces rate limiting"""
    scraper = APIRecipeScraper(api_key="test", rate_limit=3)

    start = time.time()
    tasks = [scraper.scrape(f"query{i}") for i in range(6)]
    await asyncio.gather(*tasks)
    elapsed = time.time() - start

    # Should take at least 2 seconds (rate_limit=3, 6 requests)
    assert elapsed >= 2.0

@pytest.mark.asyncio
async def test_rss_scraper_parses_feed():
    """Test RSS scraper extracts recipes from feed"""
    scraper = RSSRecipeScraper()

    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value = SAMPLE_FEED
        recipes = []
        async for recipe in scraper.scrape("https://example.com/feed.xml"):
            recipes.append(recipe)

        assert len(recipes) > 0

@pytest.mark.asyncio
async def test_recipe_validation():
    """Test recipe validation catches incomplete data"""
    scraper = HTMLRecipeScraper()

    valid_recipe = RecipeScrapeResult(
        title="Good Recipe",
        ingredients=["a", "b"],
        instructions="Long instructions with many words here"
    )
    assert await scraper.validate(valid_recipe)

    invalid_recipe = RecipeScrapeResult(
        title="",  # Empty title
        ingredients=[],
        instructions="short"
    )
    assert not await scraper.validate(invalid_recipe)
```

**Task 1.11: Documentation Update** (Documentation Agent - parallel)

```bash
/sync-artifacts 002 "Implemented Recipe Harvester Agent with HTML, API, RSS, and duplicate detection"
```

Updates artifacts:
- spec.md: Mark "Recipe Harvester Agent" as [IMPLEMENTED]
- plan.md: Update Phase 1 with implementation details
- tasks.md: Update all subtasks as complete
- data-model.md: Add Recipe entity documentation
- CHANGELOG.md: Add entry for Recipe Harvester
- ADR: Create ADR-0008 for duplicate detection algorithm choice

---

#### Step 4: Integration Testing

```bash
/run-tests 002 integration
```

**Integration tests verify:**
- Recipe Harvester can process 100 recipes without errors
- Duplicate detection accuracy > 95%
- Database transactions prevent data loss
- Rate limiting works correctly
- Graceful error recovery

---

#### Step 5: Merge Validation

```bash
/commit-and-review "feat(recipe-system): Implement Recipe Harvester Agent with multi-source support"
```

**Quality Gates:**
```
✓ Type checking: pyright --strict (0 errors)
✓ Linting: pylint app/ (0 warnings)
✓ Format check: black --check
✓ Unit tests: pytest tests/test_recipe_harvester.py (45/45 passing)
✓ Integration tests: pytest tests/integration (8/8 passing)
✓ Coverage: 92% (exceeds 90% target)
✓ Database migration: Valid and reversible
✓ Performance: Handles 100 recipes/min
✓ Monitoring: Prometheus metrics configured
```

### Timeline Summary

```
Sequential Development:
  Wave 1: Base class           = 15 mins
  Wave 2: Components           = 25 mins (after 1)
  Wave 3: DB & migrations      = 15 mins (after 2)
  Wave 4: Tests & docs         = 45 mins (after 3)
  Wave 5: Integration tests    = 25 mins (after 4)
  ─────────────────────────────────────
  Total:                        125 mins

Parallel with ReAct:
  Wave 1: Base class           = 15 mins
  Wave 2: Components           = 25 mins (parallel, no wait)
  Wave 3: DB & migrations      = 15 mins (parallel with Wave 2)
  Wave 4: Tests & docs         = 30 mins (parallel)
  Wave 5: Integration tests    = 25 mins (sequential, final)
  ─────────────────────────────────────
  Total:                        80 mins

Speedup: 1.56x faster
```

---

## Workflow 2: Meal Architect Agent with Constraint Solving

### User Request

"Implement the Meal Architect Agent that generates weekly meal plans respecting dietary constraints, avoiding recipe repetition, and optimizing ingredient reuse"

### Step-by-Step Execution

#### Step 1: Specification Analysis

```bash
/spec-analyze 002 "Meal Architect Agent with constraint satisfaction"
```

**Output:**
```
✓ Feature: 002 (Recipe System)
✓ Agent: Meal Architect

Requirements:
├─ Functional
│  ├─ Generate 7-day meal plan from recipes
│  ├─ Respect dietary constraints (vegan, gluten-free, allergies)
│  ├─ Avoid recipe repetition (90-day lookback)
│  ├─ Maximize ingredient overlap (reduce shopping list)
│  ├─ Optimize for cooking time and difficulty
│  └─ Support custom recipe preferences
├─ Non-Functional
│  ├─ Generate plan in < 2 seconds
│  ├─ Handle 10,000+ recipes efficiently
│  ├─ Support multi-constraint satisfaction (3+ constraints)
│  └─ Maintain consistency across meal plans
└─ Constraints
   ├─ Use Z3 constraint solver or similar
   ├─ Async processing for large recipe sets
   ├─ Database query optimization needed
   └─ Transaction safety for plan creation

Test Scenarios:
✓ Vegan + gluten-free constraints (both active)
✓ 90-day no-repeat constraint enforced
✓ Ingredient overlap maximized
✓ Performance < 2 seconds for 10K recipes
✓ Invalid constraint handling
✓ User preference weights applied
```

---

#### Step 2: Task Decomposition

```bash
/task-decompose 002-002-01 "Meal planning with Z3 constraint solver"
```

**Parallel Tasks:**
```
Task 1: Create MealPlan model (Backend Dev)
Task 2: Load and filter recipes by constraints (Backend Dev)
Task 3: Implement Z3 constraint solver (Backend Dev)
Task 4: Implement ingredient overlap optimizer (Backend Dev)
Task 5: Generate meal plan from solution (Backend Dev)
Task 6: Create database migration
Task 7: Unit tests (in parallel with Tasks 2-5)
Task 8: Integration tests (after Task 6)
Task 9: Documentation
```

---

#### Step 3: Parallel Component Development

```bash
/gen-endpoint /meal-plans POST MealPlan 002
```

**Backend Dev Agent generates:**

```python
# app/agents/meal_architect.py
from z3 import Solver, Bools, If, Sum, Int

class MealArchitect:
    """Generates meal plans with constraint satisfaction"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.solver = Solver()

    async def generate_plan(
        self,
        user_id: int,
        constraints: dict,
        preferences: dict,
    ) -> MealPlan:
        """Generate weekly meal plan"""

        # 1. Load recipes matching constraints
        recipes = await self._load_eligible_recipes(user_id, constraints)

        # 2. Build constraint satisfaction problem
        plan_vars = [Int(f"day_{i}_recipe") for i in range(7)]
        self.solver.reset()

        # Add constraints
        self._add_constraints(plan_vars, recipes, constraints)
        self._add_preferences(plan_vars, recipes, preferences)

        # 3. Solve
        if self.solver.check():
            model = self.solver.model()
            meal_plan = self._extract_solution(model, recipes)
            return meal_plan

        raise NoFeasiblePlanError("Could not find meal plan satisfying constraints")

    async def _load_eligible_recipes(
        self,
        user_id: int,
        constraints: dict
    ) -> list[Recipe]:
        """Load recipes matching dietary constraints"""

        query = select(Recipe)

        # Filter by dietary constraints
        if constraints.get('vegan'):
            query = query.where(Recipe.dietary_tags.contains(['vegan']))

        if constraints.get('gluten_free'):
            query = query.where(Recipe.dietary_tags.contains(['gluten-free']))

        if allergies := constraints.get('allergies', []):
            for allergen in allergies:
                query = query.where(~Recipe.allergens.contains([allergen]))

        # Exclude recently used recipes (90-day lookback)
        recent_recipes = await self._get_recent_recipes(user_id, days=90)
        if recent_recipes:
            query = query.where(Recipe.id.notin_(recent_recipes))

        result = await self.db.execute(query)
        return result.scalars().all()

    def _add_constraints(self, vars, recipes, constraints):
        """Add Z3 constraints"""

        # Each day must have a valid recipe
        for var in vars:
            self.solver.add(var >= 0, var < len(recipes))

        # No recipe appears twice in week
        self.solver.add(Distinct(vars))

        # Respect dietary constraints
        if constraints.get('vegan'):
            for i, var in enumerate(vars):
                self.solver.add(
                    If(var == recipe_idx, recipe.is_vegan, True)
                    for recipe_idx, recipe in enumerate(recipes)
                )

    def _add_preferences(self, vars, recipes, preferences):
        """Add preference optimizations"""

        # Maximize ingredient overlap
        overlap_score = 0
        for i in range(len(vars) - 1):
            recipe_i = recipes[vars[i]]
            recipe_j = recipes[vars[i + 1]]
            shared = len(set(recipe_i.ingredients) & set(recipe_j.ingredients))
            overlap_score += shared

        self.solver.maximize(overlap_score)

        # Respect cooking time preferences
        if max_time := preferences.get('max_prep_time'):
            for var in vars:
                recipe = recipes[var]
                self.solver.add(recipe.prep_time <= max_time)

    def _extract_solution(self, model, recipes) -> MealPlan:
        """Convert Z3 solution to MealPlan"""
        meals = []
        for i in range(7):
            recipe_idx = model.eval(Int(f"day_{i}_recipe"))
            recipe = recipes[recipe_idx]
            meals.append(
                MealPlanDay(
                    day=i,
                    recipe=recipe,
                    date=datetime.now().date() + timedelta(days=i)
                )
            )

        return MealPlan(
            user_id=self.user_id,
            meals=meals,
            created_at=datetime.now(),
            constraints_applied=len([c for c in self.constraints if c])
        )

    async def _get_recent_recipes(self, user_id: int, days: int = 90) -> list[int]:
        """Get recipes eaten in past N days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        query = select(distinct(MealPlan.recipe_id)).where(
            (MealPlan.user_id == user_id) &
            (MealPlan.date >= cutoff_date)
        )

        result = await self.db.execute(query)
        return result.scalars().all()
```

#### Step 4: Testing & Validation

```bash
/gen-tests app/agents/meal_architect.py all
```

**Example Tests:**

```python
@pytest.mark.asyncio
async def test_vegan_constraint_satisfied():
    """Ensure generated plan respects vegan constraint"""
    architect = MealArchitect(db)

    plan = await architect.generate_plan(
        user_id=1,
        constraints={'vegan': True},
        preferences={}
    )

    for meal in plan.meals:
        assert 'vegan' in meal.recipe.dietary_tags

@pytest.mark.asyncio
async def test_no_recipe_repetition():
    """Ensure no recipe appears twice in same week"""
    architect = MealArchitect(db)

    plan = await architect.generate_plan(
        user_id=1,
        constraints={},
        preferences={'avoid_recent': 90}
    )

    recipe_ids = [meal.recipe_id for meal in plan.meals]
    assert len(recipe_ids) == len(set(recipe_ids))

@pytest.mark.asyncio
async def test_performance_under_10k_recipes():
    """Generate plan in < 2 seconds with 10K recipes"""
    architect = MealArchitect(db)

    start = time.time()
    plan = await architect.generate_plan(
        user_id=1,
        constraints={'vegan': True},
        preferences={'max_prep_time': 45}
    )
    elapsed = time.time() - start

    assert elapsed < 2.0
    assert plan is not None

@pytest.mark.asyncio
async def test_ingredient_overlap_optimization():
    """Verify meal plan optimizes ingredient overlap"""
    architect = MealArchitect(db)

    plan = await architect.generate_plan(
        user_id=1,
        constraints={},
        preferences={'optimize_shopping': True}
    )

    all_ingredients = []
    for meal in plan.meals:
        all_ingredients.extend(meal.recipe.ingredients)

    unique_count = len(set(all_ingredients))
    overlap_ratio = 1 - (unique_count / len(all_ingredients))

    # Expect 60%+ ingredient overlap
    assert overlap_ratio > 0.6
```

### Timeline Summary

```
Sequential: 90 mins
Parallel:   60 mins
Speedup:    1.5x
```

---

## Workflow 3: Multi-Agent Orchestration Testing

### User Request

"Create integration tests ensuring Recipe Harvester, Ingredient Intelligence, Meal Architect, and Cart Optimizer agents work together"

### Step-by-Step Execution

#### Step 1: Full Workflow Test

```bash
/gen-tests tests/integration/multi_agent_workflow.py all
```

```python
# tests/integration/test_meal_planning_flow.py
@pytest.mark.asyncio
async def test_complete_meal_planning_workflow():
    """Test full flow: harvest → plan → optimize cart"""

    # 1. Recipe Harvester fetches recipes
    harvester = RecipeHarvester(db)
    recipes_added = await harvester.scrape_and_store(
        sources=['https://recipes.example.com']
    )
    assert recipes_added > 50

    # 2. Ingredient Intelligence enriches recipes
    enricher = IngredientIntelligence(db)
    await enricher.enrich_recipes(
        recipes=recipes_added,
        include_substitutions=True,
        include_seasonal=True
    )

    # Verify enrichment
    enriched = await db.execute(
        select(Recipe).where(Recipe.dietary_tags.is_not(None))
    )
    assert enriched.scalars().count() > 40

    # 3. Meal Architect generates plan
    architect = MealArchitect(db)
    plan = await architect.generate_plan(
        user_id=1,
        constraints={'vegan': True, 'gluten_free': False},
        preferences={'max_prep_time': 45}
    )
    assert len(plan.meals) == 7

    # 4. Cart Optimizer creates shopping list
    optimizer = CartOptimizer(db)
    cart = await optimizer.optimize_cart(
        meal_plan=plan,
        consider_store_sections=True,
        optimize_cost=True
    )
    assert cart.total_items > 0
    assert cart.estimated_cost > 0

    # Verify full flow success
    assert plan.recipes_count == 7
    assert cart.items_count > 20

@pytest.mark.asyncio
async def test_multi_agent_event_flow():
    """Test agents communicate via event bus"""

    events = []

    async def capture_event(event):
        events.append(event)

    # Subscribe to events
    event_bus.subscribe('recipe.harvested', capture_event)
    event_bus.subscribe('plan.created', capture_event)
    event_bus.subscribe('cart.optimized', capture_event)

    # Trigger workflow
    await full_meal_planning_workflow(
        user_id=1,
        constraints={'vegan': True}
    )

    # Verify event sequence
    assert events[0].type == 'recipe.harvested'
    assert events[1].type == 'plan.created'
    assert events[2].type == 'cart.optimized'

@pytest.mark.asyncio
async def test_agent_error_recovery():
    """Test agents handle failures gracefully"""

    # Simulate API failure in recipe scraping
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = httpx.ConnectError("API down")

        harvester = RecipeHarvester(db)
        result = await harvester.scrape_and_store(sources=['api'])

        # Should recover and return partial results
        assert result.status == 'partial'
        assert result.recipes_added > 0
        assert result.failures > 0
```

#### Step 2: Merge & Deploy Validation

```bash
/commit-and-review "test(recipe-system): Add comprehensive multi-agent integration tests"
```

**Quality Gates Pass:**
- ✅ All integration tests pass
- ✅ Event flow verified
- ✅ Error recovery tested
- ✅ Performance acceptable
- ✅ Database transactions consistent

---

## Workflow 4: Performance Optimization Sprint

### User Request

"Optimize meal plan generation to handle 100K recipes in under 1 second"

### Step-by-Step Execution

```bash
/performance-audit 002
```

**Initial Performance Report:**
```
Current: 2.1 seconds for 10K recipes
Target: < 1.0 second for 100K recipes
Gap: 2.1x slower than target

Bottlenecks:
1. Recipe filtering (900ms) - N+1 queries
2. Constraint solving (800ms) - Z3 optimization
3. Solution extraction (400ms) - String operations
```

---

#### Optimization Workflow

**Backend Dev Agent optimizes database queries:**

```python
# Batch recipe filtering with proper indexes
async def _load_eligible_recipes_optimized(self, user_id, constraints):
    query = (
        select(Recipe)
        .where(
            Recipe.dietary_tags.overlap(constraints['required_tags'])
        )
        .where(Recipe.id.notin_(recent_recipes_subquery))
        .options(selectinload(Recipe.allergens))
    )
    # Use database indexes instead of in-app filtering
    result = await self.db.execute(query)
    return result.scalars().all()
```

**Testing Agent verifies optimization:**

```bash
/performance-audit 002
```

**Performance Improvement:**
```
Before: 2.1 seconds
After:  0.8 seconds
Speedup: 2.6x
Result: ✅ PASS (< 1.0 second target)
```

---

## Workflow 5: Database Schema Migration

### User Request

"Add dietary tags and allergen tracking to recipes, ensuring zero downtime migration"

### Step-by-Step

```bash
/gen-endpoint /recipes POST Recipe 002
# Includes migration
```

**Generated Migration:**

```python
# migrations/versions/20231114_add_dietary_data.py
"""Add dietary tags and allergen tracking"""

def upgrade():
    # 1. Add new columns as nullable
    op.add_column('recipes', sa.Column('dietary_tags', sa.JSON()))
    op.add_column('recipes', sa.Column('allergens', sa.JSON()))

    # 2. Backfill data (can be done asynchronously)
    op.execute("""
        UPDATE recipes SET dietary_tags = '[]'
        WHERE dietary_tags IS NULL
    """)

    # 3. Add indexes
    op.create_index(
        'ix_recipes_dietary_tags',
        'recipes',
        ['dietary_tags'],
        mysql_length={'dietary_tags': 255}
    )

def downgrade():
    op.drop_index('ix_recipes_dietary_tags', 'recipes')
    op.drop_column('recipes', 'allergens')
    op.drop_column('recipes', 'dietary_tags')
```

**Validation:**

```bash
/run-tests 002 integration
# Tests verify migration doesn't lose data
```

---

## Quick Reference: Feature 002 Agent Assignments

| Task | Agent | Tech Stack | Estimated Time |
|------|-------|-----------|-----------------|
| Recipe Harvester | Backend Dev | Python/FastAPI | 80 mins |
| Ingredient Intelligence | Backend Dev | SQLAlchemy/Pydantic | 75 mins |
| Meal Architect | Backend Dev | Python/Z3 | 60 mins |
| Cart Optimizer | Backend Dev | FastAPI | 70 mins |
| Database Migrations | Backend Dev | Alembic | 30 mins |
| Unit Tests | Testing | pytest | 120 mins |
| Integration Tests | Testing | pytest/asyncio | 90 mins |
| Documentation | Documentation | Markdown/spec sync | 45 mins |
| Quality Validation | Integration | Pre-merge checks | 20 mins |

**Parallel Timeline: 80 + 75 + 60 = 215 mins (3.6 hours)**
**Sequential Timeline: 80 + 75 + 60 + 70 + 30 + 120 + 90 + 45 + 20 = 590 mins (9.8 hours)**
**Speedup: 2.7x faster** ⚡

---

## Success Metrics for Feature 002

### Code Quality
- ✅ Type coverage: 100%
- ✅ Test coverage: 92%+
- ✅ All agents have comprehensive test suites
- ✅ Zero linting warnings

### Performance
- ✅ Meal plan generation: < 1 second for 100K recipes
- ✅ Recipe harvesting: 100+ recipes/minute
- ✅ Duplicate detection: 95%+ accuracy
- ✅ Cart optimization: < 500ms

### Functionality
- ✅ All dietary constraints supported
- ✅ Multi-source recipe harvesting works
- ✅ Ingredient overlap optimization active
- ✅ Cost minimization functional
- ✅ Multi-agent communication reliable

### Documentation
- ✅ All agents documented with examples
- ✅ API endpoints documented with OpenAPI
- ✅ Data models documented in data-model.md
- ✅ Architecture decisions documented in ADRs
- ✅ CHANGELOG updated with all changes

