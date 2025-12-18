# Implementation Plan: Bulk Recipe Import from Parent Websites

**Branch**: `005-bulk-import` | **Date**: 2025-12-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from PR description - bulk import recipes from parent URLs with real-time progress tracking

## Summary

This feature enables users to import multiple recipes from a parent/category URL in a single operation, rather than importing recipes one at a time. The system will crawl parent pages to discover recipe links, process each recipe using existing scraping infrastructure with LLM-based validation, track progress in real-time via WebSocket/SSE, and display results with proper deduplication and error handling.

**Key Value**: Reduces recipe library building time from 10+ minutes (manual) to <10 minutes (automated bulk import of 50 recipes).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: 
- Backend: FastAPI 0.104+, SQLAlchemy 2.0 (async), Anthropic Claude API, BeautifulSoup4, httpx
- Frontend: Next.js 16, React 19, WebSocket/SSE for real-time updates
**Storage**: PostgreSQL 16+ with existing Recipe, User models + new BulkImportJob, ImportedRecipe tables  
**Testing**: pytest (backend unit/integration), Playwright (frontend E2E)  
**Target Platform**: Railway (backend API), Vercel (frontend), Neon PostgreSQL  
**Project Type**: Web application (FastAPI backend + Next.js frontend)  
**Performance Goals**: 
- Process ≥10 recipes/min (with rate limiting)
- Progress updates with <2s latency
- Handle up to 200 recipes without degradation
**Constraints**: 
- 1 request/second rate limit (configurable) to avoid site blocking
- LLM rate limits (Anthropic Claude API)
- WebSocket/SSE connection management
**Scale/Scope**: Single-user bulk imports, 10-200 recipes per job typical

## Constitution Check

*GATE: Must pass before implementation begins*

### Architecture Alignment
- ✅ **Reuses existing agents**: Leverages HTMLRecipeScraper, APIRecipeScraper, RSSRecipeScraper (no new scraping logic)
- ✅ **Extends current patterns**: Uses existing duplicate detection (85% similarity threshold)
- ✅ **Consistent with FastAPI patterns**: BackgroundTasks for async processing
- ✅ **Database schema extension**: Adds BulkImportJob, ImportedRecipe tables with proper foreign keys
- ✅ **Frontend integration**: Extends existing import UI at `/import`

### Potential Complexity Points
- **WebSocket/SSE for real-time updates**: New pattern for this project (not currently used)
  - **Justification**: Essential for user engagement during multi-minute operations
  - **Alternative rejected**: Polling would be inefficient and add unnecessary load
- **Background job management**: Need to track long-running jobs across requests
  - **Justification**: Required for cancel/pause functionality and session persistence
  - **Alternative rejected**: Synchronous processing would block API and timeout

## Project Structure

### Documentation (this feature)

```text
specs/005-bulk-import/
├── plan.md              # This file
├── tasks.md             # Task breakdown (to be created)
├── contracts/           # API contracts
│   └── bulk-import-api.md
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── agents/                    # Existing recipe scrapers (reuse)
│   │   ├── html_scraper.py       # ✓ Already exists
│   │   ├── api_scraper.py        # ✓ Already exists
│   │   ├── rss_scraper.py        # ✓ Already exists
│   │   └── recipe_harvester.py   # ✓ Already exists
│   ├── api/v1/
│   │   ├── recipes.py            # Extend with bulk import endpoint
│   │   └── bulk_import.py        # NEW: Bulk import endpoints
│   ├── models/
│   │   ├── recipe.py             # ✓ Already exists
│   │   ├── user.py               # ✓ Already exists
│   │   ├── bulk_import_job.py    # NEW: BulkImportJob model
│   │   └── imported_recipe.py    # NEW: ImportedRecipe model
│   ├── schemas/
│   │   ├── recipe.py             # ✓ Already exists
│   │   └── bulk_import.py        # NEW: Request/response schemas
│   ├── services/
│   │   ├── recipe_discovery.py   # NEW: Crawl parent URLs for recipe links
│   │   ├── bulk_import_service.py # NEW: Orchestrate bulk import
│   │   └── progress_tracker.py   # NEW: Track and broadcast progress
│   └── utils/
│       └── llm_classifier.py     # NEW: LLM-based recipe page classification
├── migrations/
│   └── versions/
│       └── xxx_add_bulk_import_tables.py  # NEW: Alembic migration
└── tests/
    ├── test_recipe_discovery.py  # NEW: Test URL discovery
    ├── test_bulk_import_service.py # NEW: Test orchestration
    └── test_progress_tracker.py  # NEW: Test progress updates

frontend/
├── src/
│   ├── app/
│   │   └── import/
│   │       └── page.tsx          # Extend with bulk import UI
│   ├── components/
│   │   ├── BulkImportForm.tsx    # NEW: Bulk import initiation
│   │   ├── ProgressTracker.tsx   # NEW: Real-time progress display
│   │   └── ImportSummary.tsx     # NEW: Results summary
│   ├── hooks/
│   │   └── useBulkImport.ts      # NEW: WebSocket/SSE hook
│   └── lib/
│       └── bulk-import-client.ts # NEW: API client for bulk import
└── e2e/
    └── bulk-import.spec.ts       # NEW: E2E tests
```

**Structure Decision**: Web application structure chosen because:
- Project has separate backend (FastAPI) and frontend (Next.js) directories
- Bulk import requires both API endpoints and UI components
- Real-time updates require WebSocket/SSE infrastructure on both sides

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| WebSocket/SSE (new pattern) | Real-time progress updates during multi-minute operations essential for UX | Polling would be inefficient, increase server load, and provide stale updates |
| Background job persistence | Need to track job state for cancel/pause/resume and 24hr session retention | Synchronous processing would timeout for large imports; in-memory state lost on restart |

## Architecture Decisions

### 1. Recipe Discovery Strategy

**Decision**: Two-phase approach (discover → import)

**Phases**:
1. **Discovery Phase**: Crawl parent URL to extract all recipe links (fast, 5-10 seconds)
2. **Import Phase**: Process each discovered recipe sequentially with rate limiting (slow, 5-10 minutes)

**Why**: 
- Users see total recipe count quickly
- Progress bar accurate from start
- Can skip already-imported URLs early
- Allows cancellation without wasted scraping

**Implementation**:
- Use BeautifulSoup4 + httpx for fast HTML parsing
- LLM classification only for ambiguous links (e.g., URLs without obvious patterns)
- Cache discovered links in RecipeDiscoveryResult temporary table

### 2. Real-Time Progress Updates

**Decision**: Server-Sent Events (SSE) over WebSocket

**Why SSE**:
- Simpler than WebSocket (unidirectional, backend → frontend)
- No connection state management needed
- Auto-reconnect built into EventSource API
- FastAPI has SSE support via StreamingResponse
- Progress updates are broadcast-only (no client messages needed)

**Implementation**:
```python
# Backend: FastAPI SSE endpoint
@router.get("/bulk-import/{job_id}/progress")
async def stream_progress(job_id: str):
    async def event_generator():
        while True:
            progress = await get_job_progress(job_id)
            yield f"data: {json.dumps(progress)}\n\n"
            if progress['status'] in ['completed', 'cancelled', 'failed']:
                break
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

```typescript
// Frontend: React hook for SSE
const useProgressStream = (jobId: string) => {
  useEffect(() => {
    const eventSource = new EventSource(`/api/v1/bulk-import/${jobId}/progress`);
    eventSource.onmessage = (event) => {
      const progress = JSON.parse(event.data);
      updateProgress(progress);
    };
    return () => eventSource.close();
  }, [jobId]);
};
```

**Alternative Rejected**: WebSocket would require bidirectional protocol overhead for what is essentially a broadcast stream.

### 3. Background Job Processing

**Decision**: FastAPI BackgroundTasks + in-database state

**Why**:
- BackgroundTasks sufficient for MVP (no Celery/RQ overhead)
- Job state persisted in PostgreSQL (survives restarts)
- Can migrate to Celery later if needed without API changes
- Simpler deployment (no separate worker process)

**Limitations Accepted**:
- Jobs lost if API server crashes during processing (acceptable for MVP)
- Single-server processing (no distributed workers)
- Manual retry if job fails (no automatic retry queue)

**Implementation**:
```python
@router.post("/bulk-import/start")
async def start_bulk_import(
    request: BulkImportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    job = await create_import_job(db, user_id, request.parent_url)
    background_tasks.add_task(process_bulk_import, job.id, db)
    return {"job_id": job.id, "status": "started"}
```

**Migration Path**: Replace BackgroundTasks with Celery in Phase 2 if concurrent user load requires it.

### 4. Rate Limiting Strategy

**Decision**: Token bucket per-domain with configurable rate (default 1 req/sec)

**Why**:
- Avoids overwhelming target websites
- Prevents IP bans / 429 errors
- Per-domain allows parallel imports from different sites
- Configurable for testing and future optimization

**Implementation**:
```python
class DomainRateLimiter:
    def __init__(self, requests_per_second: float = 1.0):
        self.buckets: dict[str, TokenBucket] = {}
        self.rate = requests_per_second
    
    async def acquire(self, url: str):
        domain = extract_domain(url)
        if domain not in self.buckets:
            self.buckets[domain] = TokenBucket(self.rate)
        await self.buckets[domain].acquire()
```

### 5. LLM Integration for Recipe Classification

**Decision**: Use Claude API to classify ambiguous pages only (not every link)

**Why**:
- LLM classification expensive (time + API cost)
- Most recipe links identifiable by URL patterns (e.g., `/recipes/`, `/recipe/`, `-recipe.html`)
- Only call LLM for ambiguous cases (e.g., `/food/italian-pasta-dish`)
- Reduces cost and latency

**Classification Logic**:
```python
async def classify_page_type(url: str, html: str) -> PageType:
    # 1. Fast: Check URL patterns
    if '/recipe/' in url or '/recipes/' in url:
        return PageType.RECIPE
    if '/category/' in url or '/tag/' in url:
        return PageType.CATEGORY
    
    # 2. Fast: Check for schema.org/Recipe JSON-LD
    if has_recipe_schema(html):
        return PageType.RECIPE
    
    # 3. Slow: Use LLM for ambiguous cases
    if is_ambiguous(url):
        return await llm_classify_page(url, html)
    
    return PageType.OTHER
```

### 6. Duplicate Detection

**Decision**: Reuse existing duplicate detection logic (URL + 85% title similarity)

**Why**:
- Already implemented and tested in `recipes.py:find_duplicate_recipe()`
- Consistent behavior with single-recipe import
- No need to reinvent the wheel

**Enhancement**: Add bulk deduplication endpoint to check all discovered URLs at once before importing.

```python
@router.post("/bulk-import/check-duplicates")
async def check_duplicates(
    urls: list[str],
    db: AsyncSession,
    user_id: int
):
    duplicates = []
    for url in urls:
        existing = await find_duplicate_recipe(db, title="", source_url=url, user_id=user_id)
        if existing:
            duplicates.append({"url": url, "existing_recipe_id": existing.id})
    return {"duplicates": duplicates, "count": len(duplicates)}
```

### 7. Error Handling Strategy

**Decision**: Continue-on-error with detailed logging and retry capability

**Error Categories**:
1. **Network errors** (timeout, DNS, connection): Retry with exponential backoff (max 3 attempts)
2. **Scraping errors** (no recipe found, invalid HTML): Skip and log (no retry)
3. **Rate limiting** (429, 403): Pause and retry after delay (exponential backoff)
4. **LLM errors** (API limit, timeout): Fallback to heuristic classification

**Implementation**:
```python
async def import_recipe_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await scrape_and_import(url)
        except NetworkError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                raise ImportFailedError(url, reason="Network timeout after retries")
        except ScrapingError as e:
            raise ImportFailedError(url, reason=str(e))  # No retry
        except RateLimitError as e:
            await asyncio.sleep(e.retry_after or 60)
            continue
```

## Database Schema Extensions

### BulkImportJob Table

```sql
CREATE TABLE bulk_import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('discovering', 'in_progress', 'completed', 'cancelled', 'failed')),
    total_discovered INTEGER DEFAULT 0,
    total_processed INTEGER DEFAULT 0,
    total_success INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    total_duplicates INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bulk_import_jobs_user_id ON bulk_import_jobs(user_id);
CREATE INDEX idx_bulk_import_jobs_status ON bulk_import_jobs(status);
CREATE INDEX idx_bulk_import_jobs_created_at ON bulk_import_jobs(created_at DESC);
```

### ImportedRecipe Table

```sql
CREATE TABLE imported_recipes (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES bulk_import_jobs(id) ON DELETE CASCADE,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
    source_url TEXT NOT NULL,
    import_status VARCHAR(20) NOT NULL CHECK (import_status IN ('success', 'failed', 'duplicate')),
    error_message TEXT,
    imported_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_imported_recipes_job_id ON imported_recipes(job_id);
CREATE INDEX idx_imported_recipes_recipe_id ON imported_recipes(recipe_id);
CREATE INDEX idx_imported_recipes_status ON imported_recipes(import_status);
```

### RecipeDiscoveryResult Table (Temporary)

```sql
CREATE TABLE recipe_discovery_results (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES bulk_import_jobs(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    page_type VARCHAR(20) CHECK (page_type IN ('recipe', 'category', 'other')),
    discovered_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_discovery_results_job_id ON recipe_discovery_results(job_id);

-- Auto-cleanup old discoveries (7 days retention)
CREATE OR REPLACE FUNCTION cleanup_old_discoveries() RETURNS void AS $$
BEGIN
    DELETE FROM recipe_discovery_results
    WHERE discovered_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
```

## API Contracts

### POST /api/v1/bulk-import/start

**Request**:
```json
{
  "parent_url": "https://www.ottolenghi.co.uk/recipes",
  "options": {
    "max_recipes": 100,
    "overwrite_duplicates": false,
    "rate_limit_per_second": 1.0
  }
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "discovering",
  "parent_url": "https://www.ottolenghi.co.uk/recipes",
  "started_at": "2025-12-15T20:00:00Z"
}
```

### GET /api/v1/bulk-import/{job_id}

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "parent_url": "https://www.ottolenghi.co.uk/recipes",
  "progress": {
    "total_discovered": 50,
    "total_processed": 25,
    "total_success": 22,
    "total_failed": 2,
    "total_duplicates": 1,
    "percentage": 50,
    "estimated_time_remaining_seconds": 150
  },
  "started_at": "2025-12-15T20:00:00Z",
  "completed_at": null
}
```

### GET /api/v1/bulk-import/{job_id}/progress (SSE)

**Event Stream**:
```
data: {"status": "discovering", "discovered": 10}

data: {"status": "in_progress", "processed": 1, "success": 1, "current_recipe": "Pasta with Tomatoes"}

data: {"status": "in_progress", "processed": 2, "success": 2, "current_recipe": "Roasted Vegetables"}

data: {"status": "completed", "processed": 50, "success": 47, "failed": 2, "duplicates": 1}
```

### POST /api/v1/bulk-import/{job_id}/cancel

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "recipes_imported": 25,
  "cancelled_at": "2025-12-15T20:05:00Z"
}
```

### GET /api/v1/bulk-import/{job_id}/results

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": {
    "total_discovered": 50,
    "total_success": 47,
    "total_failed": 2,
    "total_duplicates": 1
  },
  "successful_recipes": [
    {"recipe_id": 123, "title": "Pasta with Tomatoes", "url": "..."},
    // ... (paginated)
  ],
  "failed_imports": [
    {"url": "...", "error": "No recipe found on page"},
    {"url": "...", "error": "Scraping blocked (403)"}
  ]
}
```

## Implementation Phases

### Phase 1: Backend Core (Week 1)

**Goal**: Basic bulk import backend without real-time updates

**Deliverables**:
- Database schema (migrations)
- BulkImportJob, ImportedRecipe models
- RecipeDiscoveryService (crawl parent URLs)
- BulkImportService (orchestrate imports)
- API endpoints (start, get status, cancel, results)
- Unit tests for discovery and orchestration

**Acceptance**: Can POST to `/bulk-import/start`, job processes in background, GET status shows progress

### Phase 2: Real-Time Progress (Week 1-2)

**Goal**: Add SSE for real-time progress updates

**Deliverables**:
- ProgressTracker service (broadcast updates)
- SSE endpoint (`/bulk-import/{job_id}/progress`)
- Update BulkImportService to emit progress events
- Integration tests for SSE stream

**Acceptance**: Frontend can connect to SSE and see live progress updates

### Phase 3: Frontend UI (Week 2)

**Goal**: Bulk import UI on import page

**Deliverables**:
- BulkImportForm component (URL input, options)
- ProgressTracker component (progress bar, counters, ETA)
- ImportSummary component (results, failed list, retry)
- useBulkImport hook (SSE connection management)
- E2E tests for bulk import flow

**Acceptance**: User can initiate bulk import, see progress, view results

### Phase 4: LLM Integration (Week 2-3)

**Goal**: Intelligent recipe classification

**Deliverables**:
- LLMClassifier service (Claude API integration)
- Heuristic fallback logic
- Rate limiting for LLM calls
- Unit tests for classification

**Acceptance**: Ambiguous URLs correctly classified, costs within budget

### Phase 5: Error Handling & Retry (Week 3)

**Goal**: Robust error handling and retry

**Deliverables**:
- Retry logic with exponential backoff
- Error categorization (network, scraping, rate limit)
- Retry failed endpoint
- Comprehensive error logging

**Acceptance**: Network errors retried, scraping errors skipped, rate limits handled gracefully

### Phase 6: Optimization & Polish (Week 4)

**Goal**: Performance and UX improvements

**Deliverables**:
- Rate limiter optimization
- ETA calculation improvements
- Cancel/pause functionality
- 24hr session persistence
- Documentation and quickstart

**Acceptance**: All success criteria met, MVP ready for production

## Testing Strategy

### Unit Tests
- RecipeDiscoveryService: URL crawling, link extraction
- BulkImportService: Orchestration, state transitions
- ProgressTracker: Event emission, SSE formatting
- LLMClassifier: Claude API integration, fallback logic
- RateLimiter: Token bucket algorithm

### Integration Tests
- End-to-end bulk import flow (discover → import → complete)
- SSE connection and reconnection
- Duplicate detection during bulk import
- Error handling and retry logic
- Cancel during processing

### E2E Tests (Playwright)
- User initiates bulk import from parent URL
- Progress bar updates in real-time
- Import completes, recipes visible in library
- Cancel mid-import, imported recipes preserved
- Retry failed imports

## Deployment

### Backend (Railway)
- Deploy to existing Railway backend service
- Add ANTHROPIC_API_KEY environment variable
- No additional infrastructure needed (uses existing PostgreSQL)
- Monitor API rate limits and adjust as needed

### Frontend (Vercel)
- Deploy to existing Vercel frontend project
- No additional environment variables needed
- Test SSE connection across CDN

## Monitoring & Observability

### Metrics to Track
- Bulk import job success rate
- Average recipes processed per minute
- LLM API call rate and cost
- SSE connection count and duration
- Error rate by category (network, scraping, rate limit)

### Alerts
- Job failure rate >10%
- LLM API errors >5%
- SSE connection failures >5%
- Rate limiter queue depth >100

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM API costs exceed budget | High | Medium | Use heuristics first, LLM as fallback; monitor spend |
| Website blocks scraping | Medium | High | Implement proper rate limiting, user-agent headers, retry logic |
| SSE connections don't work across CDN | Medium | Low | Test early, fallback to polling if needed |
| Background jobs lost on restart | Low | Medium | Document limitation, migrate to Celery in Phase 2 if needed |
| Large imports (200+) cause timeout | Medium | Medium | Hard limit at 200 recipes, document in UI |

## Success Metrics

**MVP Success Criteria** (from spec):
- ✅ Discover recipes within 10s
- ✅ Process ≥10 recipes/min
- ✅ Progress updates <2s latency
- ✅ 90% success rate on valid pages
- ✅ 95% duplicate detection accuracy
- ✅ Complete 50 recipes in <10min
- ✅ Handle up to 200 recipes

**User Satisfaction**:
- 80% user satisfaction with time saved
- <5% cancellation rate mid-import
- <10% failure rate for valid recipe sites

## Future Enhancements (Post-MVP)

1. **Scheduled Bulk Imports**: Auto-import new recipes from favorite sites weekly
2. **Import Templates**: Save common parent URLs as templates
3. **Advanced Filtering**: Filter by recipe type during bulk import
4. **Parallel Processing**: Import from multiple sites simultaneously
5. **Import History**: View past bulk import jobs and re-run
6. **Smart Pagination**: Auto-detect and crawl paginated category pages
7. **Celery Migration**: Replace BackgroundTasks with Celery for distributed processing
