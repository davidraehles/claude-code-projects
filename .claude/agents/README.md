# Claude Code ReAct Agent System

This directory contains the configuration and orchestration for an 8-agent ReAct (Reason + Act) system designed to parallelize development across the AI Meal Planner application features.

**Last Updated**: November 29, 2025
**Total Agents**: 8
**Configuration Format**: JSON (.json files)

## Agent Overview

This system includes 8 specialized agents working collaboratively:

### 1. Router Agent
**Role**: Orchestrator / Coordinator
**Purpose**: Analyzes incoming requests, decomposes tasks, manages parallelization strategy
**Model**: Haiku 4.5
**Configuration**: [router-agent.json](./router-agent.json)

### 2. Spec Analyzer Agent
**Role**: Analysis / Reasoning
**Purpose**: Deep requirement analysis, constraint identification, dependency mapping
**Model**: Haiku 4.5
**Configuration**: [spec-analyzer-agent.json](./spec-analyzer-agent.json)

### 3. Frontend Dev Agent
**Role**: Implementation / Development
**Purpose**: React/Next.js component implementation with TypeScript and Tailwind CSS
**Model**: Haiku 4.5
**Configuration**: [frontend-dev-agent.json](./frontend-dev-agent.json)
**Tech Stack**: TypeScript 5.x, React 19, Next.js 16, Tailwind CSS

### 4. Backend Dev Agent
**Role**: Implementation / Development
**Purpose**: Python/FastAPI implementation, SQLAlchemy models, agent workflows
**Model**: Haiku 4.5
**Configuration**: [backend-dev-agent.json](./backend-dev-agent.json)
**Tech Stack**: Python 3.11+, FastAPI, SQLAlchemy, LangGraph

### 5. Testing & Quality Agent
**Role**: Quality Assurance / Testing
**Purpose**: Comprehensive test generation, quality gates, accessibility compliance
**Model**: Haiku 4.5
**Configuration**: [testing-quality-agent.json](./testing-quality-agent.json)
**Coverage Target**: 90%+ for all code

### 6. Documentation & Artifact Agent
**Role**: Documentation / Synchronization
**Purpose**: Keeps specs, plans, and tasks synchronized with code changes
**Model**: Haiku 4.5
**Configuration**: [documentation-artifact-agent.json](./documentation-artifact-agent.json)

### 7. Integration & Validation Agent
**Role**: Quality Assurance / Integration / Release
**Purpose**: Final validation, build checks, integration testing, merge readiness
**Model**: Haiku 4.5
**Configuration**: [integration-validation-agent.json](./integration-validation-agent.json)

### 8. Agent Registry Manager
**Role**: Registry / Management
**Purpose**: Agent discovery, creation, deletion, and lifecycle management
**Model**: Haiku 4.5
**Configuration**: [agent-registry-manager.json](./agent-registry-manager.json)

## Parallelization Strategy

The agent system enables parallel development at multiple levels:

### Level 1: Feature-Level
Multiple features can be developed independently:
- **Feature 001** (Grocery Lists) - Backend + Frontend + Tests
- **Feature 002** (Multi-Agent Recipe App) - Agent development
- **Feature 003** (AI Chat) - Chat interface + Voice features

### Level 2: Component-Level
Each feature decomposes into parallel work streams:
- **Frontend**: Components, pages, API integration (parallel development)
- **Backend**: Models, endpoints, agents, workflows (parallel development)
- **Tests**: Unit, integration, E2E (parallel with implementation)

### Level 3: Task-Level
Individual tasks execute concurrently:
- Code implementation
- Test generation
- Documentation updates
- Quality checks
- All running simultaneously across multiple agents

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

## Using the Agent System

### Agent Configuration

All agents are configured as JSON files in this directory:

```
.claude/agents/
├── router-agent.json
├── spec-analyzer-agent.json
├── frontend-dev-agent.json
├── backend-dev-agent.json
├── testing-quality-agent.json
├── documentation-artifact-agent.json
├── integration-validation-agent.json
└── agent-registry-manager.json
```

Each JSON file defines:
- Agent name and description
- When to use the agent (with examples)
- Capabilities and tools
- System prompt and behavior
- Target features

### Available Custom Commands

The agent system integrates with custom slash commands in `.claude/commands/`:

#### Development Commands
- `/gen-component` - Generate React components with tests
- `/gen-endpoint` - Generate FastAPI endpoints with migrations
- `/gen-tests` - Generate comprehensive test suites
- `/check-types` - Run TypeScript and pyright type checking
- `/run-tests` - Execute test suites (backend and frontend)

#### Quality & Validation
- `/validate-a11y` - Check WCAG 2.1 accessibility compliance
- `/performance-audit` - Run Lighthouse and performance checks
- `/commit-and-review` - Smart commits with validation

#### Workflow & Planning
- `/spec-analyze` - Analyze feature specifications
- `/task-decompose` - Break tasks into parallel units
- `/sync-artifacts` - Keep spec artifacts synchronized
- `/update-task` - Update task status and progress
- `/parallel-build` - Run builds in parallel

#### Spec-Kit Commands
- `/speckit.specify` - Create feature specifications
- `/speckit.plan` - Generate implementation plans
- `/speckit.tasks` - Create task breakdowns
- `/speckit.implement` - Execute implementations
- `/speckit.analyze` - Cross-artifact analysis

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
