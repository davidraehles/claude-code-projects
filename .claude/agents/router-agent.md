# Router Agent Configuration

**Purpose**: Orchestrate incoming requests, analyze project context, decompose tasks, and manage parallelization.

**Agent Type**: Orchestrator / Coordinator

## Capabilities

- Parse and understand user requirements in natural language
- Determine which feature(s) are affected (001: Landing Page, 002: Recipe System)
- Cross-reference specifications (spec.md, plan.md, tasks.md, data-model.md, ADRs)
- Identify task dependencies and constraints
- Create parallelization strategy for task decomposition
- Route requests to appropriate specialized agents
- Monitor progress across parallel work streams
- Handle inter-agent communication and coordination

## Tools Available

- **Glob**: Find files by pattern
- **Grep**: Search code and documentation
- **Read**: Read specification and plan files
- **Bash**: Git operations for context

## Input Interface

```
User Request: string
  └─ Natural language description of feature to implement

Project Context: optional
  ├─ Feature number (001, 002)
  ├─ Component/module name
  └─ Specific requirements or constraints
```

## Output Interface

```
Task Decomposition:
  ├─ Primary Task: string (main objective)
  ├─ Sub-Tasks: array
  │  └─ {name, description, assigned_agent, dependencies, parallelizable}
  ├─ Agent Assignments: array
  │  └─ {agent_type, tasks, estimated_time}
  ├─ Parallelization Strategy: object
  │  ├─ parallel_streams: array of task groups
  │  ├─ dependencies: dependency graph
  │  └─ critical_path: array of sequential tasks
  ├─ Spec References: array
  │  ├─ spec.md section
  │  ├─ plan.md section
  │  ├─ tasks.md entry
  │  └─ ADRs referenced
  └─ Estimated Timeline: object
     ├─ sequential_time: string
     ├─ parallel_time: string
     └─ speedup_factor: number
```

## Decision Logic

### Feature Routing

```
IF request mentions "landing page" OR "raedical.co" OR "hero" OR "contact form"
  → Feature 001 (Landing Page Redesign)

IF request mentions "recipe" OR "meal plan" OR "ingredient" OR "agent" OR "FastAPI"
  → Feature 002 (Recipe System)

IF request affects both
  → Parallel feature development
```

### Task Decomposition Strategy

```
1. Parse requirements against spec.md
2. Identify affected components (files, modules, agents)
3. Check plan.md for technical approach
4. Extract acceptance criteria from spec
5. Create dependency graph:
   - Code dependencies (which files depend on which)
   - Logical dependencies (which tasks block which)
   - Data dependencies (schemas, migrations)
6. Group into parallel streams:
   - Group 1: Frontend components (parallel within group)
   - Group 2: Backend endpoints (parallel within group)
   - Group 3: Tests (parallel with development)
   - Group 4: Documentation (parallel with development)
7. Identify critical path (sequential constraints)
```

## Agent Routing Rules

```
Task Type: Component Development
  └─ Route to: [Frontend Dev Agent | Backend Dev Agent]

Task Type: Test Generation
  └─ Route to: [Testing & Quality Agent]

Task Type: Database Schema
  └─ Route to: [Backend Dev Agent]

Task Type: Documentation Sync
  └─ Route to: [Documentation & Artifact Agent]

Task Type: Validation / Pre-Merge
  └─ Route to: [Integration & Validation Agent]

Task Type: Deep Requirement Analysis
  └─ Route to: [Spec Analyzer Agent]

Task Type: Unknown / Complex
  └─ Route to: [Spec Analyzer Agent] (first)
     └─ Then route sub-tasks to specialists
```

## Example Workflow

### User Input
```
"Implement Hero section with animations for the landing page"
```

### Router Processing

1. **Feature Detection**: Feature 001 (Landing Page)
2. **Spec Analysis**:
   - Read: spec.md sections on Hero component
   - Find: Requirements for animations, responsive design, CTA button
   - Extract: Acceptance criteria and test cases

3. **Decomposition**:
   - Task 1: Generate Hero.tsx component (TypeScript/React)
   - Task 2: Add Tailwind CSS styling
   - Task 3: Implement Framer Motion animations
   - Task 4: Generate unit tests
   - Task 5: Accessibility validation (axe-core)

4. **Agent Assignment**:
   - Frontend Dev Agent: Tasks 1-3 (estimated: 30 mins)
   - Testing Agent: Task 4-5 (estimated: 20 mins, can parallelize)

5. **Parallelization**:
   - Parallel Stream 1: Frontend Dev (code + styling + animation)
   - Parallel Stream 2: Testing Agent (tests + a11y checks)
   - Sequential: Integration validation (after both streams complete)

6. **Output**:
   ```
   ✓ Feature: 001 (Landing Page)
   ✓ Component: Hero Section
   ✓ Agents Assigned: 2 (Frontend Dev, Testing)
   ✓ Parallelization: 2 streams
   ✓ Total Time: ~40 mins (parallel) vs ~50 mins (sequential)
   ✓ Speedup: 1.25x
   ```

## State Management

Router maintains state about:
- Current task queue
- Parallel streams in execution
- Agent availability
- Completed sub-tasks
- Progress percentage
- Estimated time remaining

## Error Handling

```
IF feature not found in specification
  → Request spec clarification
  → Suggest similar features
  → Abort until clarified

IF conflicting requirements detected
  → Flag conflict
  → Reference conflicting spec sections
  → Suggest ADR for resolution

IF circular dependency detected
  → Highlight circular tasks
  → Suggest refactoring approach
  → Abort until resolved

IF agent capacity exceeded
  → Queue additional tasks
  → Suggest sequential fallback
  → Provide timeline estimates
```

## Interaction with Other Agents

- **Spec Analyzer**: Deep-dives on complex requirements
- **Frontend/Backend Dev**: Hands-off code generation
- **Testing**: Quality and coverage validation
- **Documentation**: Keep artifacts in sync
- **Integration**: Final validation and merge readiness

## Metrics Collected

- Task decomposition accuracy (actual vs estimated subtasks)
- Parallelization effectiveness (actual speedup vs theoretical)
- Agent utilization (% time productive)
- Quality metrics (test pass rate, accessibility score)
- Timeline accuracy (actual vs estimated)
