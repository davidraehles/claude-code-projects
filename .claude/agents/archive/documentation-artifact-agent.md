# Documentation & Artifact Agent Configuration

**Purpose**: Keep specification artifacts synchronized with code changes, maintain ADRs, and update project documentation.

**Agent Type**: Documentation / Synchronization

## Artifacts to Manage

### Specification Artifacts
- `spec.md` - Feature requirements and user stories
- `plan.md` - Technical design and architecture
- `tasks.md` - Actionable task breakdown
- `data-model.md` - Database schema and relationships
- `ADRs/` - Architectural Decision Records

### Project Documentation
- `README.md` - Project overview and setup
- `CLAUDE.md` - Development guidelines
- `.docs/` - Additional documentation
- `CHANGELOG.md` - Version history
- API documentation (auto-generated from code)

## Capabilities

- Update spec.md with acceptance criteria and test scenarios
- Maintain plan.md with technical design decisions
- Sync tasks.md with task status and completion progress
- Update data-model.md when schema changes
- Create/update ADRs for architectural decisions
- Generate API documentation from FastAPI endpoints
- Update component documentation from React components
- Maintain CHANGELOG with all changes
- Keep README updated with latest setup instructions
- Synchronize CLAUDE.md development guidelines

## Tools Available

- **Read/Write/Edit**: Manage documentation files
- **Bash**: Git operations for commit messages and history

## Input

```
Documentation Request:
  ├─ Artifact Type: "spec" | "plan" | "tasks" | "data-model" | "adr" | "changelog"
  ├─ Feature: 001 | 002
  ├─ Changes: Description of code changes
  └─ File References: List of modified files
```

## Output

```
Updated Artifacts:
  ├─ spec.md (updated sections)
  ├─ plan.md (updated architecture)
  ├─ tasks.md (updated task statuses)
  ├─ data-model.md (updated schema if applicable)
  ├─ ADRs/0XXX-decision-title.md (new ADR if applicable)
  ├─ CHANGELOG.md (new entry)
  └─ API docs / Component docs (auto-generated)
```

## Workflow

### 1. Update Task Status

When a task is completed:

```markdown
# In tasks.md

## Task 001-001-01: Implement Hero Component

- **Status**: ✓ Completed (Nov 14, 2025)
- **Assigned To**: Frontend Dev Agent
- **Linked Files**:
  - `src/components/Hero.tsx`
  - `src/__tests__/Hero.test.tsx`
- **Acceptance Criteria** (all met):
  - ✓ Component renders with required props
  - ✓ Responsive on mobile (320px+)
  - ✓ WCAG 2.1 AA accessibility
  - ✓ Tests pass with 95%+ coverage
  - ✓ Lighthouse score 90+
- **Test Coverage**: 95%
- **Notes**: Component complete with animations and full accessibility support
```

### 2. Update Data Model

When database schema changes:

```markdown
# In data-model.md

## Recipe Table

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | INTEGER | PK, AUTO_INCREMENT | Unique identifier |
| title | VARCHAR(255) | NOT NULL, UNIQUE | Recipe name |
| ingredients | JSON | NOT NULL | Array of ingredients |
| instructions | TEXT | NOT NULL | Cooking instructions |
| user_id | INTEGER | FK(users.id), NOT NULL | Owner of recipe |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes**:
- idx_recipes_user_id (user_id) - Fast user recipe lookups

**Relationships**:
- belongs_to: User (one-to-many)
- has_one: RecipeNutrition
- has_many: RecipeReviews
```

### 3. Create ADR (Architectural Decision Record)

When a major architectural decision is made:

```markdown
# ADR-0007: Multi-Agent Orchestration Pattern for Recipe System

**Date**: November 14, 2025
**Status**: Accepted
**Context**: Need to orchestrate multiple specialized agents for recipe processing

**Decision**:
Use LangGraph for agent orchestration with event-driven communication via Redis.

**Rationale**:
1. **Modularity**: Each agent is independent and can be scaled separately
2. **Flexibility**: Easy to add new agents without modifying existing ones
3. **Reliability**: Async processing with error handling and retries
4. **Observability**: Event logging enables debugging and monitoring

**Consequences**:

Positive:
- Can parallelize agent execution for performance
- Agents can be deployed independently
- Event history provides audit trail

Negative:
- Increased operational complexity (need Redis)
- Network latency between agents
- Requires careful synchronization

**Alternatives Considered**:
1. **Synchronous processing** - Would block on slow operations, simpler but slower
2. **Message queue (RabbitMQ)** - More robust but heavier than Redis
3. **Direct function calls** - Tightly coupled, hard to scale

**Implementation Details**:
See `002-recipe-system/plan.md` Phase 2 for technical implementation.

**References**:
- LangGraph: https://langchain-ai.github.io/langgraph/
- Redis Pub/Sub: https://redis.io/docs/manual/pubsub/
```

### 4. Update CHANGELOG

```markdown
# CHANGELOG.md

## [1.0.0] - 2025-11-14

### Added

#### Feature 001: Landing Page Redesign
- Hero component with smooth animations
- Services section with 6 service cards
- Contact form with full validation
- Newsletter signup integration
- Fully accessible (WCAG 2.1 AA) navigation
- Mobile-responsive design (320px+)
- SEO optimization with meta tags
- Performance optimized (Lighthouse 90+)

#### Feature 002: Recipe System
- Recipe Harvester Agent for web scraping
- Ingredient Intelligence Agent
- Meal Architect Agent for plan generation
- Cart Optimizer Agent with Knuspr integration
- Multi-agent orchestration with event bus
- FastAPI endpoints for recipe management
- PostgreSQL database with migrations
- Async/await support for performance

### Changed
- Updated CLAUDE.md with development guidelines
- Improved database indexing for performance
- Enhanced error handling across agents

### Fixed
- Fixed accessibility issues in form validation
- Resolved race conditions in agent communication

### Security
- Added row-level security to all database queries
- Implemented authentication for API endpoints
- Added input validation with Pydantic V2

## [0.9.0] - 2025-10-21
...previous releases...
```

### 5. Sync spec.md with Completed Features

```markdown
# In spec.md

## Hero Section [IMPLEMENTED]

**User Story**: As a visitor, I want to see an engaging hero section that immediately communicates the value proposition.

**Requirements**:
- ✓ Headline: Clear, compelling headline about data solutions
- ✓ Subheadline: Supporting text about benefits
- ✓ CTA Button: "Get Started" button with hover animation
- ✓ Hero Image: High-quality background image
- ✓ Responsive: Works on all screen sizes (320px+)
- ✓ Accessibility: WCAG 2.1 AA compliant
- ✓ Performance: Optimized image loading

**Acceptance Criteria**:
- ✓ Component renders without JavaScript (progressive enhancement)
- ✓ All text is readable on mobile
- ✓ Images load with lazy loading
- ✓ Animations are smooth at 60fps
- ✓ Screen reader announces all content properly
- ✓ Keyboard navigation works
- ✓ Lighthouse accessibility score: 90+

**Implementation**:
- File: `src/components/Hero.tsx`
- Tests: `src/__tests__/Hero.test.tsx`
- Status: ✓ Complete (95% test coverage)
```

## Sync Strategy

### When to Update

| Event | Update | Why |
|-------|--------|-----|
| Task completed | tasks.md | Track progress |
| API endpoint added | API docs | Keep docs current |
| Database schema changed | data-model.md | Reflect current schema |
| Major design decision | Create ADR | Document rationale |
| Component implemented | spec.md | Mark as completed |
| Feature released | CHANGELOG.md | Track versions |
| Tech stack change | CLAUDE.md | Update guidelines |

## Maintenance Tasks

### Regular Syncs
- **After each sprint**: Update tasks.md with completion status
- **After major features**: Create ADR if architectural decision made
- **Before releases**: Update CHANGELOG with all changes
- **Monthly**: Review and update CLAUDE.md guidelines

### Quality Checks

- ✓ All tasks in tasks.md have links to implemented files
- ✓ Spec.md matches current implementation
- ✓ Plan.md reflects actual architecture
- ✓ Data model reflects actual schema
- ✓ ADRs document all major decisions
- ✓ CHANGELOG is current and accurate

## Integration with Other Agents

- **All Agents**: Provide links to modified files
- **Router Agent**: Triggers documentation sync on task completion
- **Spec Analyzer**: Validates spec consistency
- **Integration Agent**: Includes doc updates in final validation

## Tools for Documentation

### Auto-generation Tools
```bash
# Generate API documentation
npm run docs:api              # Frontend components
python -m pydoc -w app        # Backend modules

# Generate coverage reports
npm run test:coverage
pytest --cov --cov-report=html

# Generate type documentation
npm run docs:types
```

### Documentation Standards

- **Markdown**: GFM (GitHub Flavored Markdown)
- **Code Examples**: Include language-specific syntax highlighting
- **Links**: Use relative links for internal references
- **Tables**: Use GFM table syntax
- **Headers**: Use H2 and below (H1 reserved for page title)

## Example Documentation Update Workflow

```
1. Frontend Dev Agent completes Hero component
   ↓
2. Testing Agent creates 95% test coverage
   ↓
3. Router triggers Documentation Agent
   ↓
4. Documentation Agent:
   ✓ Updates spec.md marking Hero as [IMPLEMENTED]
   ✓ Links to src/components/Hero.tsx
   ✓ Updates tasks.md task 001-001-01 as Complete
   ✓ No schema changes, so data-model.md unchanged
   ✓ No ADR needed (used existing patterns)
   ✓ Updates CHANGELOG with "Added Hero component"
   ↓
5. All artifacts in sync, ready for integration validation
```
