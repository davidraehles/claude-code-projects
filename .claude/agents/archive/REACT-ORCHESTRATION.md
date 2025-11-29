# ReAct Pattern Orchestration Guide

This guide explains how the 7-agent ReAct system orchestrates work to parallelize development and maintain quality.

## Quick Start

The ReAct system is triggered through the Router Agent, which analyzes requests and coordinates parallel execution.

### Basic Usage Pattern

```
User Request
    ↓
Router Agent (Analysis & Decomposition)
    ├─ Reads specifications
    ├─ Analyzes feature scope
    ├─ Creates task breakdown
    └─ Assigns to agents
    ↓
Parallel Execution Phase
    ├→ Frontend Dev Agent (code generation)
    ├→ Backend Dev Agent (code generation)
    ├→ Testing Agent (test generation)
    └→ Documentation Agent (artifact sync)
    ↓
Integration Phase
    └→ Integration Agent (validation & merge check)
    ↓
Output: Code + Tests + Docs + Ready to Merge
```

## Router Agent Decision Tree

The Router Agent uses this decision logic:

```
IF request contains landing page keywords
  → Feature 001 (Landing Page)
  → Route to: Frontend Dev Agent
  → Secondary: Testing Agent (parallel)

ELSE IF request contains recipe/meal keywords
  → Feature 002 (Recipe System)
  → Route to: Backend Dev Agent
  → Secondary: Testing Agent (parallel)

ELSE IF ambiguous
  → Route to: Spec Analyzer Agent (first)
  → Then decompose and route to specialists

FOR ALL routes:
  → Assign Documentation Agent (parallel)
  → Plan Integration validation (sequential, at end)
```

## Parallelization Strategy

### Level 1: Feature-Level (Independent)

Features 001 and 002 can work completely independently:

```
Feature 001 Team              Feature 002 Team
(Landing Page)               (Recipe System)
├─ Frontend Dev              ├─ Backend Dev
├─ Testing (Frontend)        ├─ Testing (Backend)
└─ Documentation             └─ Documentation

No shared code dependencies = True parallel development
Estimated speedup: 1.0x (completely independent)
```

### Level 2: Component-Level (Within Feature)

Multiple components/endpoints can be developed in parallel within a feature:

```
Landing Page Development:
Component 1: Hero          (Frontend Dev Agent 1)
Component 2: Services      (Frontend Dev Agent 2)
Component 3: Contact Form  (Frontend Dev Agent 3)
Component 4: Navigation    (Frontend Dev Agent 4)

Testing All:               (Testing Agent - parallel)

No file conflicts = Parallel development possible
Estimated speedup: 0.8-0.9x (some merge coordination needed)
```

### Level 3: Task-Level (Within Component)

For a single component, different phases can run in parallel:

```
Component Implementation Phases:
├─ Phase 1: Component generation (15 mins)
│   └─ TypeScript types
│   └─ Component structure
│   └─ Props definition
│
├─ Phase 2: Styling (20 mins) [starts after Phase 1]
│   └─ Tailwind CSS
│   └─ Responsive design
│   └─ Animations
│
├─ Phase 3: Testing (20 mins) [starts after Phase 1]
│   └─ Unit tests
│   └─ Accessibility tests
│   └─ Integration tests
│
└─ Phase 4: Documentation (10 mins) [runs in parallel]
    └─ Update spec.md
    └─ Update tasks.md
    └─ Storybook stories

Timeline:
  Sequential: 15 + 20 + 20 + 10 = 65 mins
  Parallel: max(15 + 20, 20) + 10 = 45 mins
  Speedup: 1.44x
```

## Example Orchestration: Hero Component

### User Input

```
"Implement the Hero section with smooth animations"
```

### Router Agent Analysis

1. **Feature Detection**: Feature 001 (Landing Page)
2. **Requirement Analysis**:
   - Headline with subheadline
   - CTA button with animations
   - Hero image with lazy loading
   - Responsive design (320px+)
   - WCAG 2.1 AA accessibility
3. **Task Decomposition**:
   ```
   Task 1: Generate Hero component (Frontend Dev)
   Task 2: Add styling and animations (Frontend Dev)
   Task 3: Generate unit tests (Testing Agent)
   Task 4: Generate accessibility tests (Testing Agent)
   Task 5: Update spec.md (Documentation Agent)
   Task 6: Validate and prepare merge (Integration Agent)
   ```

### Parallelization Plan

```
Timeline (with parallelization):

Minute 0:
  Frontend Dev Agent starts
  └─ Generating Hero.tsx component...

Minute 15:
  Styling Agent starts (after component skeleton ready)
  Testing Agent starts (after component skeleton ready)
  Documentation Agent starts
  └─ Updating spec.md with [IMPLEMENTED] status...

Minute 35:
  Frontend Dev completes styling
  Testing completes tests (running in parallel)
  Documentation completes updates

Minute 35-40:
  All agents complete, Integration Agent validates:
  ├─ Run tests (should pass)
  ├─ Type check (should pass)
  ├─ Lint (should pass)
  └─ Merge readiness check (PASS)

Total time: ~40 minutes
Sequential equivalent: ~60 minutes
Speedup: 1.5x
```

## Agent Coordination Protocol

### Communication Between Agents

Agents communicate through:

1. **Task Queue**: Router enqueues tasks with specifications
2. **State Updates**: Each agent updates task status
3. **Handoffs**: Downstream agents wait for dependencies
4. **Artifacts**: Agents read/write shared files (spec.md, plan.md, tasks.md)

### Error Handling & Recovery

```
IF Agent encounters error:
  1. Log error with context
  2. Update task status to "blocked"
  3. Notify Router Agent
  4. Suggest fix or alternative approach
  5. Wait for manual intervention or automatic retry

IF multiple agents conflict on same file:
  1. Queue writes sequentially
  2. Merge-friendly file format (markdown/JSON)
  3. Avoid race conditions

IF dependency not ready:
  1. Agent waits with timeout
  2. After timeout, notifies Router
  3. Suggest parallelization alternative
```

## Quality Gates in Orchestration

The system maintains quality through staged gates:

```
Gate 1: Pre-Commit (Fast)
  ├─ Type checking (TypeScript/Python)
  ├─ Linting
  └─ Format check

Gate 2: Pre-Push (Comprehensive)
  ├─ All unit tests pass
  ├─ Build verification
  └─ Coverage 90%+

Gate 3: Pre-Merge (Final)
  ├─ Integration tests pass
  ├─ E2E smoke tests pass
  ├─ Accessibility audit passes
  ├─ Performance regression check
  └─ Database migrations valid

Gate 4: Release (Full)
  ├─ Complete test suite
  ├─ Full accessibility audit
  ├─ Performance baseline
  └─ Documentation complete
```

## Metrics & Monitoring

### Parallelization Effectiveness

```
Metric: Speedup Factor
  Definition: Sequential Time / Parallel Time
  Target: 2.0x (2x faster with parallelization)

  Realistic: 1.5-1.8x
  Reasons for gap:
    - Some tasks have hard dependencies
    - Merge coordination overhead
    - Testing runs serially (must pass before merge)

Metric: Agent Utilization
  Definition: % time agent is active vs idle
  Target: 85%+ utilized

Metric: Critical Path
  Definition: Longest sequential task chain
  Target: < 50% of total project time
```

### Success Metrics

After implementing ReAct pattern, measure:

1. **Time-to-Merge**: From task start to ready-to-merge (target: 40 mins for component)
2. **Quality**: Test coverage, accessibility score, performance score
3. **Consistency**: Code follows patterns, no rework needed
4. **Developer Experience**: Clear task assignments, minimal blocked time

## Troubleshooting

### Problem: Agents Creating Merge Conflicts

**Solution**:
- Design components to minimize file overlap
- Use feature branches for parallel work
- Coordinate through task assignments
- Use git rebasing strategy

### Problem: Task Dependencies Not Met

**Solution**:
- Update task.md with clear dependency declarations
- Router Agent validates dependencies before assignment
- Implement task ordering algorithm
- Queue dependent tasks intelligently

### Problem: Quality Gates Failing

**Solution**:
- Earlier agent validates output before handoff
- Testing Agent catches issues before Integration
- Use pre-commit hooks locally
- Fail fast with clear error messages

### Problem: Slow Parallelization

**Solution**:
- Profile critical path
- Reduce coupling between tasks
- Cache build outputs
- Use incremental builds
- Optimize agent performance

## Next Steps

1. **Monitor**: Track metrics above during development
2. **Iterate**: Adjust parallelization strategy based on data
3. **Optimize**: Identify bottlenecks and optimize
4. **Scale**: Add more agents if needed (e.g., Performance Agent, Security Agent)
5. **Automate**: Fully automate through CI/CD

## Advanced Patterns

### Dynamic Task Adjustment

If an agent finishes early, it can claim additional tasks:

```
Frontend Dev Agent completes:
  ✓ Hero component
  ✓ Services component

Looking for additional work:
  → Checks task queue
  → Claims: Navigation component
  → Notifies Router and Testing Agent
```

### Fallback Patterns

If parallelization not viable:

```
IF dependencies too complex:
  → Fall back to sequential execution
  → But still maintain test generation in parallel
  → Reduced but non-zero speedup (1.2-1.3x)

IF time-critical:
  → Route to single "fast-path" agent
  → Skip some tests (run locally)
  → Trade quality for speed
```

### Cross-Feature Coordination

For features that share components (rare):

```
Feature 001 (Landing Page)
Feature 002 (Recipe System)
Shared: Component library or utility functions

Coordination:
  1. Identify shared components early
  2. Frontend Dev Agent develops shared components first
  3. Both features depend on shared components
  4. Parallel development after shared components ready
  5. Integration Agent tests cross-feature compatibility
```

## Implementation Checklist

- [ ] Router Agent configured and tested
- [ ] All 7 specialist agents configured
- [ ] All 13 skills implemented
- [ ] Task decomposition algorithm working
- [ ] Parallelization strategy validated
- [ ] Quality gates implemented
- [ ] Error handling and recovery tested
- [ ] Metrics collection set up
- [ ] Team trained on ReAct workflow
- [ ] Monitoring and alerting configured
