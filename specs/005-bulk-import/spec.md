# Feature Specification: Bulk Recipe Import from Parent Websites

**Feature Branch**: `005-bulk-import`  
**Created**: 2025-12-15  
**Status**: Draft  
**Input**: User description: "New feature: bulk import of recipes from a parent website in the Frontend UI. The import should start a web scraper using Python scripts and LLM powered understanding of what's a recipe and ingredients etc. The frontend should include a progress bar and show the imported recipes in the library afterwards."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initiate Bulk Import from Parent Site (Priority: P1)

A user wants to import all available recipes from a specific website (e.g., all recipes from ottolenghi.co.uk or a specific section/category) in one operation, rather than importing recipes one at a time. The user provides the parent/category URL and the system discovers and imports all linked recipes automatically.

**Why this priority**: This is the core feature that delivers immediate value - saving users significant time when building their recipe library. Without this, users must manually find and import each recipe individually, which defeats the purpose of bulk import.

**Independent Test**: Can be fully tested by providing a parent URL (e.g., https://www.ottolenghi.co.uk/recipes), initiating the bulk import, and verifying that the system discovers recipe links, imports all recipes, and adds them to the user's library with proper deduplication.

**Acceptance Scenarios**:

1. **Given** a user on the import page, **When** they enter a parent website URL and select "Bulk Import", **Then** the system crawls the page to discover all recipe links
2. **Given** a list of discovered recipe URLs, **When** the bulk import starts, **Then** the system processes each recipe using existing scraping agents with intelligent LLM-based recipe detection
3. **Given** recipes are being imported, **When** the user views the import page, **Then** a real-time progress bar shows the current progress (e.g., "Importing 15/50 recipes")
4. **Given** the bulk import completes, **When** the user navigates to their recipe library, **Then** all successfully imported recipes are visible with proper metadata

---

### User Story 2 - Monitor Import Progress with Live Updates (Priority: P1)

A user wants to see real-time feedback during the bulk import process, including how many recipes have been discovered, how many are being processed, success/failure counts, and estimated time remaining.

**Why this priority**: Large bulk imports can take several minutes. Without progress feedback, users may think the system is frozen or unresponsive. This is essential for user confidence and engagement.

**Independent Test**: Can be tested by initiating a bulk import and verifying that the UI updates in real-time showing: discovered count, processed count, success count, failure count, current recipe being processed, and progress percentage.

**Acceptance Scenarios**:

1. **Given** a bulk import is running, **When** the user views the import page, **Then** they see a progress bar with percentage completion (e.g., "45% complete")
2. **Given** recipes are being processed, **When** each recipe completes, **Then** the success/failure counters update in real-time without page refresh
3. **Given** a large bulk import (50+ recipes), **When** processing begins, **Then** the system displays estimated time remaining based on current processing rate
4. **Given** individual recipes fail to import, **When** viewing progress details, **Then** the user sees which recipes failed and a brief error reason (e.g., "No recipe found on page", "Scraping blocked")

---

### User Story 3 - Handle Errors and Partial Failures Gracefully (Priority: P2)

A user wants the bulk import to continue even when some recipes fail to import, with clear reporting of which recipes succeeded and which failed, along with the ability to retry failed imports.

**Why this priority**: Websites may have mixed content (some pages with recipes, some without), anti-scraping measures, or temporary issues. The system must be resilient and provide transparency.

**Independent Test**: Can be tested by attempting to bulk import from a URL that contains both valid recipes and non-recipe pages, then verifying successful imports are saved, failures are logged, and the user can retry failures.

**Acceptance Scenarios**:

1. **Given** a bulk import encounters a page without a valid recipe, **When** processing that page, **Then** the system skips it, logs it as "No recipe found", and continues with remaining URLs
2. **Given** some recipes fail due to scraping errors, **When** the bulk import completes, **Then** the user sees a summary showing X recipes succeeded, Y failed, with a list of failed URLs
3. **Given** a completed bulk import with failures, **When** the user clicks "Retry Failed", **Then** the system re-attempts only the failed imports without re-processing successful ones
4. **Given** the website blocks or rate-limits requests, **When** receiving 429/403 errors, **Then** the system pauses briefly and retries with exponential backoff before marking as failed

---

### User Story 4 - Deduplicate Recipes During Bulk Import (Priority: P2)

A user wants the system to automatically detect and skip recipes that already exist in their library during bulk import, preventing duplicate entries and wasted processing time.

**Why this priority**: Users may run bulk imports multiple times on the same site (e.g., to catch new recipes), or a parent site may link to recipes the user already imported individually. Deduplication saves time and maintains library integrity.

**Independent Test**: Can be tested by first importing specific recipes individually, then running a bulk import that would include those same recipes, and verifying they are detected as duplicates and skipped.

**Acceptance Scenarios**:

1. **Given** a recipe with the same source URL already exists in the user's library, **When** the bulk import encounters that URL, **Then** the system skips it and marks it as "Already imported"
2. **Given** recipes with similar titles but different URLs, **When** processing them during bulk import, **Then** the system uses existing similarity detection (85%+ threshold) to identify potential duplicates
3. **Given** a potential duplicate is detected, **When** the user reviews the import summary, **Then** they see which recipes were skipped as duplicates with links to the existing recipes
4. **Given** the user wants to force re-import, **When** they enable "Overwrite duplicates" option, **Then** the system updates existing recipes with newly scraped data

---

### User Story 5 - Cancel or Pause Long-Running Imports (Priority: P3)

A user wants the ability to cancel or pause a bulk import that's taking too long or was started by mistake, without losing progress on already-imported recipes.

**Why this priority**: This improves user control and handles accidental bulk imports (e.g., importing from a site with 1000+ recipes). It's lower priority because most imports will be manageable in size.

**Independent Test**: Can be tested by starting a large bulk import, clicking "Cancel" or "Pause" mid-process, and verifying that already-imported recipes are saved and remaining imports stop.

**Acceptance Scenarios**:

1. **Given** a bulk import is running, **When** the user clicks "Cancel", **Then** the system stops processing new recipes and saves all recipes imported so far
2. **Given** a bulk import is paused, **When** the user returns later, **Then** they see a "Resume Import" button that continues from where it left off
3. **Given** a cancellation is requested, **When** a recipe is currently being scraped, **Then** the system completes that recipe before fully stopping (graceful shutdown)
4. **Given** a bulk import is cancelled, **When** the user views their library, **Then** all successfully imported recipes before cancellation are visible and usable

---

### Edge Cases

- What happens when the parent URL contains hundreds or thousands of recipe links? (Rate limiting, processing time)
- How does the system handle websites with pagination on category pages? (Discover all pages vs. first page only)
- What happens when recipe links are dynamically loaded via JavaScript? (Puppeteer/Playwright requirement)
- How does the system handle recipe URLs that redirect to different domains?
- What happens when LLM rate limits are hit during bulk processing? (Queue-based processing)
- How does the system distinguish between actual recipe pages and other content (blogs, articles, product pages)?
- What happens if the user closes the browser during import? (Background processing vs. real-time)
- How does the system handle recipe pages that require authentication or subscription?
- What happens when the parent site's HTML structure changes mid-import?
- How does the system handle recipe pages in different languages?

## Requirements *(mandatory)*

### Functional Requirements

#### Bulk Import Initiation
- **FR-001**: System MUST accept a parent/category URL from the user via the frontend UI
- **FR-002**: System MUST validate that the provided URL is accessible and returns a valid HTML response
- **FR-003**: System MUST discover all recipe links from the parent page by crawling the HTML structure
- **FR-004**: System MUST support discovering recipes from paginated category pages (at least the first 5 pages or up to 100 recipes, whichever comes first)
- **FR-005**: System MUST intelligently identify recipe links versus other content links using URL patterns and LLM-based page analysis

#### Recipe Processing and Scraping
- **FR-006**: System MUST use existing recipe scraping agents (HTMLRecipeScraper, APIRecipeScraper, RSSScrap) to extract recipe data
- **FR-007**: System MUST leverage LLM (Claude) to identify whether a discovered page contains a valid recipe or not
- **FR-008**: System MUST extract recipe title, ingredients, instructions, prep/cook times, servings, and images from each discovered recipe
- **FR-009**: System MUST handle scraping failures gracefully by logging errors and continuing with remaining recipes
- **FR-010**: System MUST implement rate limiting to avoid overwhelming target websites (default: 1 request per second, configurable)
- **FR-011**: System MUST retry failed recipe imports up to 3 times with exponential backoff before marking as permanently failed

#### Progress Tracking and Updates
- **FR-012**: System MUST track import progress including: total recipes discovered, recipes processed, successful imports, failed imports
- **FR-013**: System MUST send real-time progress updates to the frontend via WebSocket or Server-Sent Events (SSE)
- **FR-014**: Frontend MUST display a progress bar showing percentage completion based on processed/total recipes
- **FR-015**: Frontend MUST display current status (e.g., "Discovering recipes...", "Importing recipe 15/50", "Completed")
- **FR-016**: Frontend MUST display a list of successfully imported recipes with thumbnails and titles
- **FR-017**: Frontend MUST display a list of failed imports with URLs and error messages
- **FR-018**: System MUST calculate and display estimated time remaining based on average processing time per recipe

#### Deduplication
- **FR-019**: System MUST check for duplicate recipes by source URL before importing each recipe
- **FR-020**: System MUST check for duplicate recipes using title similarity (85%+ threshold) if URL doesn't match
- **FR-021**: System MUST skip duplicate recipes and mark them as "Already imported" in the progress report
- **FR-022**: System MUST provide an option to "Overwrite duplicates" that updates existing recipes with new data

#### User Controls
- **FR-023**: User MUST be able to cancel an in-progress bulk import at any time
- **FR-024**: System MUST gracefully stop processing when cancelled, completing the current recipe before fully stopping
- **FR-025**: System MUST save all successfully imported recipes even if the import is cancelled
- **FR-026**: User MUST be able to retry failed imports from the import summary page
- **FR-027**: System MUST preserve the import session data for at least 24 hours to allow resumption or retry

#### Post-Import
- **FR-028**: After bulk import completes, the system MUST display a summary showing total imported, total failed, and total duplicates skipped
- **FR-029**: User MUST be able to navigate directly to their recipe library from the import summary
- **FR-030**: Newly imported recipes MUST be immediately visible in the user's recipe library with proper filtering and search functionality

### Key Entities

- **BulkImportJob**: Represents a bulk import session with job ID, user ID, parent URL, status (discovering, in_progress, completed, cancelled, failed), total discovered, processed count, success count, failure count, started timestamp, completed timestamp
- **ImportedRecipe**: Links imported recipes to their bulk import job, includes recipe ID, job ID, import status (success, failed, duplicate), error message if failed, imported timestamp
- **RecipeDiscoveryResult**: Temporary entity for discovered recipe URLs during the crawling phase, includes URL, discovered timestamp, page type classification (recipe, category, other)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can initiate a bulk import from a parent URL and see discovered recipes within 10 seconds
- **SC-002**: System processes at least 10 recipes per minute on average (considering rate limiting and LLM processing)
- **SC-003**: Progress bar updates in real-time with less than 2 second delay from actual processing state
- **SC-004**: 90% of valid recipe pages are successfully imported with complete data (title, ingredients, instructions)
- **SC-005**: Duplicate detection correctly identifies 95% of duplicate recipes based on URL and title similarity
- **SC-006**: Users can complete a bulk import of 50 recipes in under 10 minutes
- **SC-007**: Failed imports provide actionable error messages that help users understand why the import failed
- **SC-008**: Cancellation of bulk import completes within 5 seconds and saves all processed recipes
- **SC-009**: Users report 80% satisfaction with the bulk import feature based on time saved versus manual import
- **SC-010**: System handles bulk imports of up to 200 recipes without performance degradation

## Assumptions *(optional)*

- Users will primarily bulk import from well-structured recipe websites with consistent HTML patterns
- The existing LLM integration (Anthropic Claude) has sufficient rate limits to handle bulk recipe analysis
- Most recipe category pages contain between 10-50 recipe links
- Users have a reasonably fast internet connection for real-time progress updates
- The frontend remains open during bulk import (no background job persistence required for MVP)
- Recipe websites allow at least 1 request per second without blocking
- The existing recipe database schema can handle the volume of bulk imported recipes

## Out of Scope *(optional)*

- Bulk import from password-protected or subscription-only recipe sites
- Scheduled/automated bulk imports that run periodically
- Bulk import from recipe apps or mobile-only sources
- Advanced filtering during bulk import (e.g., "only import vegetarian recipes")
- Bulk export of recipes to other platforms
- Collaborative bulk imports where multiple users contribute
- Machine learning-based recipe recommendation during bulk import
- Bulk editing of imported recipes (must be edited individually after import)

## Dependencies *(optional)*

- Existing recipe scraping infrastructure (HTMLRecipeScraper, APIRecipeScraper, RSSRecipeScraper)
- LLM integration (Anthropic Claude API) for intelligent recipe detection
- WebSocket or Server-Sent Events (SSE) support for real-time progress updates
- PostgreSQL database with existing Recipe, User models
- Frontend framework (Next.js/React) with existing recipe display components
- Background task processing capability (FastAPI BackgroundTasks or Celery for async processing)
