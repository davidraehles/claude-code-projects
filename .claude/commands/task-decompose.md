# Task Decompose Skill

Break down complex features into parallelizable subtasks with clear dependencies and agent assignments.

## Usage

```
/task-decompose [task-id] [optional-context]
```

## Parameters

- `task-id`: Task ID from tasks.md (e.g., 001-001-01)
- `optional-context`: Additional context or constraints

## Examples

```
/task-decompose 001-001-01
/task-decompose 002-002-01 "Need parallel development for 3 agents"
```

## What It Does

1. Analyzes the task from tasks.md
2. Identifies logical subtasks and components
3. Creates dependency graph showing task relationships
4. Determines which tasks can run in parallel
5. Assigns tasks to appropriate agents
6. Provides estimated timeline for sequential vs parallel execution
7. Highlights critical path

## Output

Returns a structured task decomposition:
- Primary task and objectives
- List of subtasks with dependencies
- Agent assignments
- Parallelization strategy
- Critical path analysis
- Timeline estimates (sequential vs parallel)
- Speedup factor

## Example Output

```
🎯 Task Decomposition: 001-001-01 - Implement Landing Page Hero Section

PRIMARY OBJECTIVE:
Create an accessible, responsive hero section with animations

SUBTASKS:
┌─────────────────────────────────────────────────────────────────┐
│ Task 1.1: Component Definition (Frontend Dev Agent)            │
│ └─ Create Hero.tsx with TypeScript types                        │
│    Estimated: 15 mins | Dependencies: None | Parallel: Yes     │
└─────────────────────────────────────────────────────────────────┘
  ├─ Task 1.1.1: Define HeroProps interface
  ├─ Task 1.1.2: Create component skeleton
  └─ Task 1.1.3: Add prop validation

┌─────────────────────────────────────────────────────────────────┐
│ Task 1.2: Styling with Tailwind (Frontend Dev Agent)           │
│ └─ Add responsive styling and animations                         │
│    Estimated: 20 mins | Dependencies: 1.1 | Parallel: Yes      │
└─────────────────────────────────────────────────────────────────┘
  ├─ Task 1.2.1: Base layout styling
  ├─ Task 1.2.2: Responsive classes (mobile/tablet/desktop)
  └─ Task 1.2.3: Animation classes with Framer Motion

┌─────────────────────────────────────────────────────────────────┐
│ Task 1.3: Testing (Testing Agent)                               │
│ └─ Generate comprehensive test suite                            │
│    Estimated: 20 mins | Dependencies: 1.1, 1.2 | Parallel: Yes │
└─────────────────────────────────────────────────────────────────┘
  ├─ Task 1.3.1: Unit tests (rendering, props)
  ├─ Task 1.3.2: Accessibility tests (axe-core)
  └─ Task 1.3.3: Responsive design tests

PARALLELIZATION STRATEGY:

Timeline Comparison:
  Sequential: Task 1.1 (15m) → Task 1.2 (20m) → Task 1.3 (20m) = 55 mins
  Parallel:   Tasks run together = 40 mins (with 1.3 after 1.1)
  Speedup:    1.38x faster

Critical Path:
  1.1 (Component) → 1.2 (Styling) → 1.3 (Testing)
  Cannot parallelize component creation, but styling and testing can run after component skeleton

Recommended Execution:
  Stream 1: Frontend Dev Agent
    Step 1: Create component skeleton (1.1) → 15 mins
    Step 2: Add styling (1.2) → 20 mins
    Total: 35 mins

  Stream 2: Testing Agent (starts after step 1)
    Step 1: Wait for component skeleton
    Step 2: Generate tests (1.3) → 20 mins
    Total: 20 mins

  Total with parallelization: 40 mins (35 + 20 concurrent after 15 min overlap)

AGENT ASSIGNMENTS:
- Frontend Dev Agent: Tasks 1.1, 1.2 (35 mins)
- Testing Agent: Task 1.3 (20 mins, starts after 1.1)

CRITICAL DEPENDENCIES:
  - Task 1.2 requires Task 1.1 (need component structure before styling)
  - Task 1.3 requires Task 1.1 (need component to write tests)
  - Testing can start once component skeleton is ready

RISKS:
  ⚠️ If component structure changes significantly, tests may need updates
  ⚠️ Styling and testing can both depend on final component API

RECOMMENDATIONS:
  ✓ Finalize component props interface before starting styling/tests
  ✓ Use test-driven development (write tests as you build)
  ✓ Regular sync between Frontend Dev and Testing agents
```

## When to Use

- Planning a sprint or feature implementation
- Need to understand task dependencies
- Want to optimize for parallel execution
- Estimating timeline for feature completion
- Assigning tasks to team members
