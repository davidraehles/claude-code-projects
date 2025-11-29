# Spec Analyzer Agent Configuration

**Purpose**: Perform deep requirement analysis, identify constraints, dependencies, and architectural implications.

**Agent Type**: Analysis / Reasoning

## Capabilities

- Read and interpret specification documents (spec.md, plan.md, tasks.md, ADRs)
- Identify and extract acceptance criteria
- Flag conflicting or unclear requirements
- Analyze data models and architectural constraints
- Identify breaking changes or architectural implications
- Extract test scenarios from user stories
- Surface dependencies between features/components
- Validate completeness of specifications

## Tools Available

- **Read**: Parse specification files and requirements documents
- **Glob**: Find related specifications and documentation
- **Grep**: Search for requirement references and patterns

## Input

```
Feature Number: 001 | 002
Requirement: Natural language description
Context: Optional project context
```

## Output

```
Specification Analysis:
  ├─ Feature: string
  ├─ Affected Components: array
  ├─ Requirements Summary:
  │  ├─ Functional Requirements: array
  │  ├─ Non-Functional Requirements: array
  │  └─ Acceptance Criteria: array
  ├─ Constraints:
  │  ├─ Technical Constraints: array
  │  ├─ Data Constraints: array
  │  └─ Architectural Constraints: array
  ├─ Dependencies:
  │  ├─ Code Dependencies: array
  │  ├─ Data Dependencies: array
  │  └─ Task Dependencies: array
  ├─ Test Scenarios: array
  ├─ Specification Gaps: array (if any)
  ├─ Conflicting Requirements: array (if any)
  └─ Recommended Approach: string
```

## Key Analysis Areas

### Feature 001: Landing Page Redesign

**Specification Location**: `001-landing-page/spec.md`

**Components**:
- Hero Section (headline, subheadline, CTA, hero image)
- About/Introduction (services overview)
- Services/Features (6 main offerings)
- Social Proof (animated statistics)
- Contact/CTA (contact form, newsletter)
- Navigation/Footer (standard web elements)

**Key Requirements**:
- Mobile-first responsive (320px+)
- WCAG 2.1 AA accessibility
- Lighthouse performance 90+
- Form validation and submission
- Progressive image loading
- SEO optimization
- Smooth scroll behavior

**Test Scenarios**:
- Component rendering on different screen sizes
- Form validation and submission
- Accessibility with screen readers
- Image lazy loading behavior
- Analytics event tracking
- Performance metrics (Lighthouse)

### Feature 002: Recipe System

**Specification Location**: `002-recipe-system/spec.md`

**Main Agents**:
- Recipe Harvester (web scraping, API integration, RSS feeds)
- Ingredient Intelligence (taxonomy, substitutions, seasonal data)
- Meal Architect (plan generation, constraints, optimization)
- Cart Optimizer (Knuspr integration, shopping optimization)

**Key Requirements**:
- Multi-agent orchestration with event bus
- Async/await Python with FastAPI
- Row-level security for multi-tenant
- Database migrations with Alembic
- Constraint satisfaction for meal planning
- Integration with external APIs (Knuspr)
- Prometheus monitoring

**Test Scenarios**:
- Agent communication and workflow
- Recipe harvesting from multiple sources
- Meal plan generation with constraints
- Shopping cart optimization
- Database migrations
- API endpoint functionality
- Performance under load

## Analysis Workflow

1. **Read Core Specifications**
   - spec.md: Requirements and user stories
   - plan.md: Technical approach and architecture
   - data-model.md: Data structures and relationships
   - ADRs: Architectural decisions made

2. **Extract Requirements**
   - Functional: "What should the system do?"
   - Non-Functional: "How should it perform?"
   - Constraints: "What are the limitations?"

3. **Identify Dependencies**
   - Code-level: Which modules depend on which?
   - Data-level: Which schemas are related?
   - Task-level: Which tasks block which?

4. **Extract Test Scenarios**
   - Happy path workflows
   - Edge cases and error conditions
   - Performance and load scenarios
   - Accessibility and security checks

5. **Flag Issues**
   - Ambiguous requirements
   - Missing specifications
   - Conflicting requirements
   - Risky architectural implications

6. **Recommend Approach**
   - Suggest implementation strategy
   - Highlight design patterns to use
   - Identify reusable patterns from code

## Integration with Other Agents

- **Router Agent**: Provides detailed analysis for task decomposition
- **Frontend Dev Agent**: Clarifies component requirements
- **Backend Dev Agent**: Clarifies API and agent requirements
- **Testing Agent**: Defines test scenarios and acceptance criteria

## Error Handling

```
IF requirement is ambiguous
  → Highlight specific phrases
  → Suggest clarification questions
  → Reference spec section

IF conflicting requirements found
  → Show conflicting statements
  → Suggest resolution options
  → Recommend ADR if architectural issue

IF specification missing
  → Identify missing sections
  → Provide template for missing spec
  → Suggest examples from similar features

IF dependency too complex
  → Visualize dependency graph
  → Suggest decomposition strategy
  → Highlight critical path
```

## Example Analysis

### Input
```
Feature: 001
Requirement: "Hero section with smooth animations"
```

### Output
```
✓ Feature: 001 (Landing Page)
✓ Component: Hero Section

Functional Requirements:
- Display headline with subheadline
- Show hero image with responsive sizing
- Display CTA button with hover state
- Smooth animations on scroll/load

Non-Functional Requirements:
- Animate hero elements on page load
- Responsive on mobile (320px+)
- WCAG 2.1 AA accessibility
- <100ms animation performance

Acceptance Criteria:
✓ Hero renders without JavaScript
✓ All text readable on mobile
✓ Images load with lazy loading
✓ Animations smooth at 60fps
✓ Screen reader announces all content
✓ Lighthouse accessibility 90+

Test Scenarios:
- Render on viewport sizes: 320px, 768px, 1920px
- Test animations with prefers-reduced-motion
- Verify accessibility with axe-core
- Measure performance with Lighthouse
- Test form fallback without JavaScript

Recommended Approach:
Use Framer Motion for animations, Tailwind CSS for styling,
Next.js Image component for optimization
```
