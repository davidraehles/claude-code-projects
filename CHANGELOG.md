# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Recipe Harvester Agent (Wave 1-4)
- **Core Components**:
  - `RecipeScraper` abstract base class with async/await pattern
  - `HTMLRecipeScraper` for HTML-based recipe extraction with schema.org/Recipe JSON-LD support
  - `APIRecipeScraper` for API-based recipe fetching with token bucket rate limiting
  - `RSSRecipeScraper` for RSS feed polling with recipe detection heuristics
  - `DuplicateDetector` with weighted similarity scoring (60% title, 40% ingredients)

- **Data Models**:
  - `RecipeScrapeResult` Pydantic model with validation
  - `Recipe` SQLAlchemy ORM model with self-referential duplicate tracking
  - `RecipeCreate`, `RecipeUpdate`, `RecipeResponse` Pydantic schemas

- **Database**:
  - Alembic migration for recipes table with 6 optimized indexes:
    - `ix_recipes_source_url` (unique identifier)
    - `ix_recipes_source_type` (filter by source type)
    - `ix_recipes_created_at` (temporal queries)
    - `ix_recipes_duplicate_of_id` (duplicate lookup)
    - `ix_recipes_not_duplicate` (composite: duplicate_of_id + created_at)
    - `ix_recipes_title` (search queries)

- **Testing**:
  - 45+ unit and integration tests for all components
  - AsyncIO support with pytest-asyncio
  - Test coverage for:
    - RecipeScrapeResult validation
    - DuplicateDetector similarity calculations
    - HTMLRecipeScraper JSON-LD and HTML parsing
    - APIRecipeScraper response parsing and rate limiting
    - RSSRecipeScraper feed entry detection
    - Error handling with exponential backoff
    - Integration workflows
    - Performance testing (100+ recipes)

- **Error Handling**:
  - Exponential backoff retry logic (2^retry_count seconds)
  - Configurable max retries (default 3)
  - Per-component error handling and logging
  - URL validation and timeout configuration

- **Features**:
  - ISO 8601 duration parsing (PT30M, PT1H30M, PT2H)
  - JSON-LD recipe format detection and fallback to heuristic parsing
  - Recipe ingredient whitespace normalization and trimming
  - URL-based duplicate detection with configurable similarity threshold (85% default)
  - Async context manager support for resource cleanup

### Changed
- Initialized feature 002-multi-agent-recipe-app with comprehensive specifications

### Status
- ✅ Phase 1D Implementation: Code generation and testing complete
- ⏳ Pending: Integration testing, API endpoint wiring, event bus integration
- Estimated completion: 1-2 days

## [0.0.0] - Initial Project Setup

- Project initialization with ReAct agent system framework
- Feature 001 (Landing Page Redesign) specification
- Feature 002 (Multi-Agent Recipe & Meal Planning System) specification
