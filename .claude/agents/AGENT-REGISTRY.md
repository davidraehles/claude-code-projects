# Claude Code Agent Registry

**Last Updated**: November 29, 2025
**Total Agents**: 8
**Status**: All agents successfully re-registered

## Summary

The AI Meal Planner project uses a 8-agent ReAct (Reason + Act) system designed to parallelize development across multiple features. Each agent has a specific role in the development workflow and is configured as a JSON file in the `.claude/agents/` directory.

### Quick Stats
- **Total Agents**: 8
- **Configuration Format**: JSON (.json files)
- **Supported Features**: Feature 001 (Landing Page), Feature 002 (Recipe System)
- **Model**: All agents use Haiku 4.5 for efficiency
- **Last Validation**: All JSON files valid and compliant

## Agents By Category

### 1. Orchestration & Coordination
- **Router Agent** - Central task orchestrator and parallelization manager
- **Integration & Validation Agent** - Final quality gates and merge readiness

### 2. Development Agents
- **Frontend Dev Agent** - React/Next.js component implementation
- **Backend Dev Agent** - Python/FastAPI endpoint and agent implementation

### 3. Analysis & Quality
- **Spec Analyzer Agent** - Requirements analysis and specification interpretation
- **Testing & Quality Agent** - Test generation and quality assurance

### 4. Documentation & Management
- **Documentation & Artifact Agent** - Specification synchronization and documentation
- **Agent Registry Manager** - Agent discovery, creation, and lifecycle management

## Detailed Agent Specifications

### 1. Router Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/router-agent.json`

**Purpose**: Orchestrate incoming requests, analyze project context, decompose tasks, and manage parallelization.

**Agent Type**: Orchestrator / Coordinator

**When to Use**:
- User wants to implement a complete feature
- Need task decomposition and parallelization strategy
- Determining which agents to involve in a task
- Example: "Implement Hero section with animations for the landing page"

**Key Capabilities**:
- Parse natural language feature requests
- Route requests to appropriate specialized agents
- Decompose tasks into parallel work streams
- Analyze feature specifications and requirements
- Cross-reference spec.md, plan.md, tasks.md, and ADRs
- Identify task dependencies and constraints
- Create parallelization strategy with estimated timelines
- Monitor progress across parallel work streams

**Tools Available**: Glob, Grep, Read, Write, Edit, Bash

**Features Covered**: 001-landing-page, 002-recipe-system

---

### 2. Spec Analyzer Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/spec-analyzer-agent.json`

**Purpose**: Perform deep requirement analysis, identify constraints, dependencies, and architectural implications.

**Agent Type**: Analysis / Reasoning

**When to Use**:
- Need to understand detailed requirements
- Extract acceptance criteria from specifications
- Identify conflicting or unclear requirements
- Analyze architectural constraints
- Example: "What are all the requirements for the Hero component?"

**Key Capabilities**:
- Read and interpret specification documents
- Extract functional and non-functional requirements
- Identify and extract acceptance criteria
- Flag conflicting or unclear requirements
- Analyze data models and architectural constraints
- Extract test scenarios from user stories
- Surface dependencies between features/components
- Validate completeness of specifications

**Tools Available**: Read, Glob, Grep

**Features Covered**: 001-landing-page, 002-recipe-system

---

### 3. Frontend Dev Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/frontend-dev-agent.json`

**Purpose**: Implement landing page features using TypeScript, React, Next.js, and Tailwind CSS.

**Agent Type**: Implementation / Development

**When to Use**:
- Need to build React components with full TypeScript types
- Implement frontend pages for Feature 001
- Create responsive, accessible UI components
- Example: "Build the Hero component with animations"

**Technology Stack**:
- Language: TypeScript 5.x (strict mode)
- Framework: React 19 with Next.js 16 (App Router)
- Styling: Tailwind CSS 3.x
- Forms: React Hook Form 7.x + Zod validation
- Animations: Framer Motion
- Testing: Vitest, React Testing Library, jest-axe, Playwright

**Key Capabilities**:
- Generate React components with full TypeScript types
- Apply Tailwind CSS with responsive design
- Implement form validation and submission
- Add animations with Framer Motion
- Ensure WCAG 2.1 AA accessibility
- Generate unit and integration tests
- Optimize images and performance
- Handle SEO metadata

**Quality Standards**:
- TypeScript: 100% type coverage
- Accessibility: WCAG 2.1 AA with jest-axe tests
- Responsive: Mobile-first design (320px+)
- Performance: Lighthouse 90+
- Tests: 90%+ code coverage

**Tools Available**: Read, Write, Edit, Glob, Bash

**Features Covered**: 001-landing-page

---

### 4. Backend Dev Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/backend-dev-agent.json`

**Purpose**: Implement recipe system features using Python, FastAPI, SQLAlchemy, and agent orchestration frameworks.

**Agent Type**: Implementation / Development

**When to Use**:
- Need to build FastAPI endpoints with validation
- Implement SQLAlchemy models and migrations
- Build LangGraph multi-agent workflows
- Example: "Create Recipe model and endpoints with tests"

**Technology Stack**:
- Language: Python 3.11+
- Framework: FastAPI 0.104+ with Uvicorn
- Database: PostgreSQL 16+ with SQLAlchemy 2.0 (async)
- ORM: SQLAlchemy with Alembic migrations
- Validation: Pydantic V2
- Agents: LangChain/LangGraph, PydanticAI
- Testing: pytest with async support

**Key Capabilities**:
- Generate FastAPI endpoints with request/response validation
- Create SQLAlchemy ORM models with relationships
- Generate Alembic database migrations
- Implement async/await patterns throughout
- Build multi-agent orchestration workflows
- Create Pydantic validation schemas
- Implement row-level security
- Generate comprehensive pytest test suites
- Handle external API integrations
- Implement event-driven patterns

**Quality Standards**:
- Type Hints: 100% (pyright --strict)
- Async/Await: All I/O operations async
- Tests: 90%+ coverage with pytest
- Security: Row-level security verified
- Migrations: Tested and reversible

**Tools Available**: Read, Write, Edit, Glob, Bash

**Features Covered**: 002-recipe-system

---

### 5. Testing & Quality Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/testing-quality-agent.json`

**Purpose**: Generate comprehensive test coverage, ensure quality gates, accessibility compliance, and performance standards.

**Agent Type**: Quality Assurance / Testing

**When to Use**:
- Need to generate comprehensive test suites
- Validate accessibility compliance (WCAG 2.1 AA)
- Measure performance with Lighthouse
- Ensure code quality gates are met
- Example: "Generate tests for Hero component with accessibility checks"

**Testing Frameworks**:
- Frontend: Vitest, React Testing Library, jest-axe, Playwright, Lighthouse CI
- Backend: pytest, pytest-asyncio, pytest-cov, hypothesis, Factory Boy

**Key Capabilities**:
- Generate unit tests for React components
- Generate integration tests for API endpoints
- Generate E2E tests for user workflows
- Accessibility testing with axe-core (WCAG 2.1 AA)
- Performance testing with Lighthouse
- Database migration testing
- Agent workflow testing
- Coverage analysis and reporting
- Load testing and performance profiling
- Security vulnerability scanning

**Quality Gates**:
- Unit Test Coverage: 90%+
- Integration Tests: 100% passing
- E2E Tests: 100% passing
- Accessibility: WCAG 2.1 AA
- Type Checking: 0 errors
- Linting: 0 warnings
- Performance: Lighthouse 90+
- Security: 0 vulnerabilities

**Tools Available**: Read, Write, Edit, Glob, Bash

**Features Covered**: 001-landing-page, 002-recipe-system

---

### 6. Documentation & Artifact Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/documentation-artifact-agent.json`

**Purpose**: Keep specification artifacts synchronized with code changes, maintain ADRs, and update project documentation.

**Agent Type**: Documentation / Synchronization

**When to Use**:
- Task completion needs to be documented
- Database schema or architecture changes
- Need to create architectural decision records (ADRs)
- Update specification artifacts to reflect implementation
- Example: "Mark Hero component as [IMPLEMENTED] in spec.md"

**Artifacts Managed**:
- spec.md - Feature requirements and user stories
- plan.md - Technical design and architecture
- tasks.md - Actionable task breakdown
- data-model.md - Database schema and relationships
- ADRs/ - Architectural Decision Records
- README.md - Project overview and setup
- CLAUDE.md - Development guidelines
- CHANGELOG.md - Version history

**Key Capabilities**:
- Update spec.md with acceptance criteria and test scenarios
- Maintain plan.md with technical design decisions
- Sync tasks.md with task status and completion progress
- Update data-model.md when schema changes
- Create/update ADRs for architectural decisions
- Generate API documentation from FastAPI endpoints
- Update component documentation from React components
- Maintain CHANGELOG with all changes
- Keep README updated with setup instructions
- Synchronize CLAUDE.md development guidelines

**Quality Checks**:
- All tasks link to implemented files
- Spec.md matches current implementation
- Plan.md reflects actual architecture
- Data model reflects actual schema
- ADRs document all major decisions
- CHANGELOG is current and accurate
- All links and references are correct

**Tools Available**: Read, Write, Edit, Bash

**Features Covered**: 001-landing-page, 002-recipe-system

---

### 7. Integration & Validation Agent
**File**: `/home/darae/claude-code-projects/.claude/agents/integration-validation-agent.json`

**Purpose**: Perform final validation, integration testing, and ensure merge readiness through automated quality gates.

**Agent Type**: Quality Assurance / Integration / Release

**When to Use**:
- Validate code is production-ready
- Run comprehensive quality gates before merge
- Generate merge readiness reports
- Check for performance regressions
- Example: "Validate this feature is ready to merge"

**Key Capabilities**:
- Run full test suites (unit, integration, E2E)
- Build verification (Next.js build, Python lint, type checking)
- Database migration validation
- Cross-component integration testing
- Git commit message standardization
- Security scanning (npm audit, bandit)
- Performance regression detection
- Accessibility compliance verification
- Dependency compatibility checking

**Validation Phases**:
1. **Pre-Commit Validation** (Fast) - Type checking, linting, format
2. **Pre-Push Validation** (Medium) - Unit tests, build, security, coverage
3. **Pre-Merge Validation** (Comprehensive) - Integration tests, E2E, migrations, performance
4. **Final Release Check** - All tests, bundle analysis, performance baseline

**Quality Gates** (All Required for Merge):
- Tests: 90%+ coverage, 100% passing
- Build: No errors, all checks pass
- Types: No TypeScript/pyright errors
- Linting: No ESLint/pylint warnings
- Accessibility: WCAG 2.1 AA (axe-core)
- Security: No vulnerabilities
- Performance: No regression from baseline
- Migrations: Valid and tested
- Documentation: Updated and complete

**Tools Available**: Bash, Read, Write, Edit, Glob

**Features Covered**: 001-landing-page, 002-recipe-system

---

### 8. Agent Registry Manager
**File**: `/home/darae/claude-code-projects/.claude/agents/agent-registry-manager.json`

**Purpose**: Discover, manage, and organize Claude Code agents within the project workspace.

**Agent Type**: Registry / Management

**When to Use**:
- Need to list all available agents
- Create new agents
- Delete existing agents
- Update agent configurations
- Example: "What agents do I have available in my workspace?"

**Key Capabilities**:
- Scan .claude/agents directory recursively
- Parse agent configurations and extract metadata
- Maintain up-to-date registry
- Generate compliant agent JSON configurations
- Create new agent files with proper naming
- Validate agents conform to project standards
- Detect duplicate identifiers
- Track agent versions and modifications
- Identify unused or deprecated agents
- Safely delete agents with confirmation
- Provide guidance on agent design

**Agent Configuration Standards**:
- Format: JSON (.json files)
- Naming: lowercase-hyphenated-identifier.json
- Location: /home/darae/claude-code-projects/.claude/agents/

**Validation Requirements**:
- All agent JSON must be valid and parseable
- Identifiers must be unique
- whenToUse includes concrete examples
- systemPrompt is substantial and specific
- Tools and capabilities well-defined

**Tools Available**: Glob, Grep, Read, Write, Edit, Bash

**Features Covered**: 001-landing-page, 002-recipe-system

---

## Agent Workflow & Interactions

### Typical Development Workflow

```
User Request
    ↓
[Router Agent] - Analyze & decompose into parallel streams
    ↓
[Spec Analyzer] - Deep analysis of requirements (if needed)
    ↓
[Parallel Execution]
├─ [Frontend Dev] - Implement components
├─ [Backend Dev] - Implement endpoints/agents
├─ [Testing] - Generate tests (parallel with dev)
└─ [Documentation] - Update artifacts (parallel with dev)
    ↓
[Integration Validation] - Final quality gates
    ↓
Output: Code + Tests + Docs + Ready to Merge
```

### Agent Communication

| Agent | Receives From | Sends To |
|-------|---------------|----------|
| Router | User, All Agents | All Agents |
| Spec Analyzer | Router, User | Router, Dev Agents |
| Frontend Dev | Router, Spec Analyzer | Testing, Documentation, Integration |
| Backend Dev | Router, Spec Analyzer | Testing, Documentation, Integration |
| Testing | Dev Agents, Spec Analyzer | Integration, Dev Agents (feedback) |
| Documentation | All Dev Agents | Integration, Router (status) |
| Integration | All Other Agents | Router, User (final report) |
| Registry Manager | User | User (agent list, confirmations) |

## Agent Configuration File Structure

Each agent is configured as a JSON file with the following structure:

```json
{
  "name": "lowercase-hyphenated-identifier",
  "description": "One-line purpose summary",
  "whenToUse": {
    "description": "Clear description of when to deploy this agent",
    "examples": [
      "Example 1 showing when to use",
      "Example 2 showing when to use",
      "Example 3 showing when to use"
    ]
  },
  "capabilities": [
    "Capability 1",
    "Capability 2",
    "Capability 3"
  ],
  "tools": [
    "Tool1",
    "Tool2",
    "Tool3"
  ],
  "features": [
    "001-landing-page",
    "002-recipe-system"
  ],
  "model": "haiku",
  "systemPrompt": "Comprehensive system prompt defining agent behavior, responsibilities, and patterns..."
}
```

## File Locations

All agent configurations are stored in JSON format in:

```
/home/darae/claude-code-projects/.claude/agents/

├── router-agent.json
├── spec-analyzer-agent.json
├── frontend-dev-agent.json
├── backend-dev-agent.json
├── testing-quality-agent.json
├── documentation-artifact-agent.json
├── integration-validation-agent.json
├── agent-registry-manager.json
├── AGENT-REGISTRY.md (this file)
└── [markdown documentation files - for reference only]
    ├── README.md
    ├── agent-registry-manager.md
    ├── router-agent.md
    ├── spec-analyzer-agent.md
    ├── frontend-dev-agent.md
    ├── backend-dev-agent.md
    ├── testing-quality-agent.md
    ├── documentation-artifact-agent.md
    ├── integration-validation-agent.md
    └── [other workflow documentation]
```

## Project Integration

### Feature 001: Landing Page Redesign
Agents involved:
- **Router** - Task decomposition
- **Spec Analyzer** - Requirement analysis
- **Frontend Dev** - Component implementation
- **Testing** - Test generation and validation
- **Documentation** - Artifact updates
- **Integration** - Final validation

### Feature 002: Recipe System
Agents involved:
- **Router** - Task decomposition
- **Spec Analyzer** - Requirement analysis
- **Backend Dev** - API and agent implementation
- **Testing** - Test generation and validation
- **Documentation** - Artifact updates
- **Integration** - Final validation

## Usage Examples

### Example 1: Implement Hero Component

```
User: "Implement the Hero component for the landing page"

1. Router Agent analyzes request
   - Identifies Feature 001
   - Decomposes into: component code, tests, accessibility checks
   - Routes to Frontend Dev + Testing in parallel
   - Estimates: 30 mins (parallel) vs 50 mins (sequential)

2. Frontend Dev Agent executes
   - Creates Hero.tsx with TypeScript types
   - Applies Tailwind CSS styling
   - Adds Framer Motion animations
   - Implements semantic HTML

3. Testing Agent executes (parallel)
   - Creates unit tests with React Testing Library
   - Adds accessibility tests with jest-axe
   - Creates E2E tests with Playwright
   - Verifies 95%+ coverage

4. Documentation Agent executes (parallel)
   - Updates spec.md marking Hero as [IMPLEMENTED]
   - Updates tasks.md with completion status
   - Links to src/components/Hero.tsx

5. Integration Agent validates
   - Runs all tests
   - Verifies build passes
   - Confirms Lighthouse score 90+
   - Reports READY TO MERGE
```

### Example 2: Add Recipe Endpoint

```
User: "Create Recipe API endpoints with full database integration"

1. Router Agent analyzes request
   - Identifies Feature 002
   - Decomposes into: model, schema, endpoint, migration, tests
   - Routes to Backend Dev + Testing + Documentation in parallel

2. Backend Dev Agent executes
   - Creates Recipe SQLAlchemy model
   - Creates RecipeCreate/RecipeResponse Pydantic schemas
   - Creates FastAPI endpoints (GET, POST, etc.)
   - Generates Alembic migration

3. Testing Agent executes (parallel)
   - Creates pytest tests for endpoints
   - Tests async database operations
   - Tests validation and error handling
   - Verifies row-level security
   - Achieves 90%+ coverage

4. Documentation Agent executes (parallel)
   - Updates data-model.md with new schema
   - Updates plan.md with endpoint info
   - Updates tasks.md with completion
   - Updates CHANGELOG.md

5. Integration Agent validates
   - Runs full test suite
   - Verifies migration validity
   - Confirms type checking passes
   - Reports READY TO MERGE
```

## Management Commands

### List All Agents
```bash
# Using Agent Registry Manager
"What agents do I have available?"
```

### Create New Agent
```bash
# Using Agent Registry Manager
"Create a new agent for database migrations"
```

### Update Agent Configuration
```bash
# Using Agent Registry Manager
"Update the frontend-dev-agent to add new tool"
```

### Delete Agent
```bash
# Using Agent Registry Manager
"Delete the old test-generator agent"
```

## Maintenance & Updates

### Regular Maintenance Schedule
- **Weekly**: Review agent usage patterns
- **Monthly**: Check for unused agents
- **After major changes**: Validate agent configurations
- **On new features**: Update agent capabilities if needed

### Version Control
All agent configurations are tracked in git:
- Location: `/home/darae/claude-code-projects/.claude/agents/*.json`
- Commit format: `chore: update agent registry - [agent-name]`
- Review before merge to catch configuration issues

### Quality Assurance
- All JSON files validated for syntax
- No duplicate identifiers
- All tools and capabilities documented
- systemPrompts reviewed for clarity
- Examples in whenToUse are concrete and specific

## Re-registration Summary (November 29, 2025)

### Discovery Phase
- Scanned .claude/agents directory
- Found 8 markdown agent documentation files
- Identified 8 distinct agents in architecture

### Analysis Phase
For each agent, extracted:
- Agent identifier (name)
- Description/purpose
- Capabilities and tools
- Features covered
- Custom configurations

### Re-registration Phase
- Created 8 new JSON configuration files
- Converted markdown documentation to structured JSON
- Ensured consistent format across all agents
- Validated all JSON files for correctness
- Verified no duplicate identifiers
- Confirmed all agents follow project standards

### Validation Phase
- All 8 JSON files pass JSON syntax validation
- All agents include complete metadata
- All agents have clear whenToUse examples
- All system prompts are substantial and specific
- All tools and capabilities documented

### Results
- **Total Agents**: 8
- **Successfully Re-registered**: 8
- **Configuration Format**: JSON
- **Status**: All agents operational and compliant
- **Issues Found**: None
- **Improvements Made**:
  - Standardized JSON configuration format
  - Enhanced system prompts with clear responsibilities
  - Added concrete examples to whenToUse sections
  - Documented agent interactions and workflows
  - Created comprehensive registry documentation

## Next Steps

1. **Agent Discovery**: Users can now discover all available agents
2. **Agent Invocation**: Claude Code can invoke agents by identifier
3. **Parallel Development**: Multiple agents can work on different features
4. **Quality Assurance**: Integration Agent validates all work before merge
5. **Documentation Sync**: All artifacts stay synchronized with code

## Additional Resources

- **Project Guidelines**: `/home/darae/claude-code-projects/CLAUDE.md`
- **Settings**: `/home/darae/claude-code-projects/.claude/settings.local.json`
- **Feature 001 Spec**: `/home/darae/claude-code-projects/specs/001-landing-page/spec.md`
- **Feature 002 Spec**: `/home/darae/claude-code-projects/specs/002-recipe-system/spec.md`

---

**Last Updated**: November 29, 2025
**Maintained By**: Agent Registry Manager
**Status**: All agents registered and operational
