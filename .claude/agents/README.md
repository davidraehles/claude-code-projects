# Claude Code ReAct Agent System

This directory contains the configuration and orchestration for a 7-agent ReAct (Reason + Act) system designed to parallelize development across the claude-code-projects features.

## Agent Types

### 1. Router Agent
Orchestrates incoming requests, analyzes project context, decomposes tasks, and manages parallelization.

### 2. Spec Analyzer Agent
Performs deep requirement analysis, identifies constraints, dependencies, and architectural implications.

### 3. Frontend Dev Agent
Implements landing page features using TypeScript, React, Next.js, and Tailwind CSS.

### 4. Backend Dev Agent
Implements recipe system using Python, FastAPI, SQLAlchemy, and agent orchestration frameworks.

### 5. Testing & Quality Agent
Generates comprehensive tests, ensures quality gates, accessibility compliance, and performance standards.

### 6. Documentation & Artifact Agent
Keeps specification artifacts (spec.md, plan.md, tasks.md, ADRs) synchronized with code changes.

### 7. Integration & Validation Agent
Performs final validation, build checks, integration testing, and pre-merge quality gates.

## Parallelization Strategy

### Level 1: Feature-Level
- Feature 001 (Landing Page) and Feature 002 (Recipe System) can work independently
- No shared code dependencies between features

### Level 2: Component-Level
Each feature can be decomposed into parallel work streams:
- **Frontend**: Hero, Services, Contact, Navigation (4 parallel components)
- **Backend**: Recipe Harvester, Ingredient, Meal Architect, Cart Optimizer agents (4 parallel agents)

### Level 3: Task-Level
Tasks can execute in parallel:
- Code implementation
- Test generation
- Documentation updates
- All running simultaneously

## ReAct Workflow

```
User Request
    ↓
[Router Agent] - Analyze & decompose
    ↓
[Spec Analyzer] - Deep analysis
    ↓
[Parallel Execution]
├→ [Frontend Dev]
├→ [Backend Dev]
├→ [Testing Agent]
└→ [Documentation]
    ↓
[Integration Agent] - Final validation
    ↓
Output (Code + Tests + Docs + Ready to Merge)
```

## Usage with Claude Code

This agent system is designed to work with Claude Code's task orchestration capabilities:

```bash
# Run a ReAct task
claude task --agent router --prompt "Implement Hero section for landing page"

# Run agents in parallel
claude task --agents frontend backend testing --parallel

# Validate before merge
claude task --agent integration --mode final-check
```

## Custom Skills (Slash Commands)

The agent system works with 13 custom skills defined in `.claude/commands/`:

- `/spec-analyze` - Analyze feature specifications
- `/task-decompose` - Break tasks into parallel units
- `/gen-component` - Generate React components with tests
- `/gen-endpoint` - Generate FastAPI endpoints with migrations
- `/gen-tests` - Generate test suites
- `/validate-a11y` - Check accessibility compliance
- `/check-types` - Full TypeScript validation
- `/run-tests` - Execute test suites
- `/performance-audit` - Lighthouse + performance checks
- `/sync-artifacts` - Keep spec artifacts synchronized
- `/update-task` - Update task status and progress
- `/commit-and-review` - Smart commits with validation
- `/parallel-build` - Run builds in parallel

## Key Benefits

- **2x speedup** through full parallelization
- **Consistent quality** through spec-driven validation
- **Automation** reduces manual repetition
- **Scalability** easy to add new agents or skills
- **Traceability** clear task → agent → output mapping
- **Flexibility** agents adapt to different project contexts

## Future Extensions

- Add specialized agents for performance optimization
- Create agents for deployment and infrastructure
- Integrate with GitHub for automated PR workflows
- Add monitoring and metrics collection
- Extend to additional projects beyond Features 001 & 002
