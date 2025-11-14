# ADR Template: Architecture Decision Records

**Purpose**: Document all significant architectural decisions for future reference and knowledge sharing.

**Usage**: Copy this template to `docs/adr/ADR-XXX-short-title.md` and fill in all sections.

---

# ADR-XXX: [Short Title of Decision]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-YYY
**Deciders**: [Names of people involved in decision]
**Affected Components**: [List of components affected]
**Effort Estimate**: [Phase/Sprint this is planned for]

---

## Problem Statement

**Context**: Describe the situation that prompted this decision. What was the state of the system? What motivated the need for this decision?

**Example**:
```
The multi-agent recipe system needs a communication mechanism between independent agents
(Recipe Harvester, Ingredient Intelligence, Meal Architect, Cart Optimizer). This communication
must be asynchronous, scalable, and resilient to failures.
```

**Requirements** (List what the decision must satisfy):
- Requirement 1: ...
- Requirement 2: ...
- Requirement 3: ...

**Constraints** (List what limits our options):
- Constraint 1: ...
- Constraint 2: ...
- Constraint 3: ...

---

## Options Considered

### Option 1: [Technology/Approach Name]

**Pros**:
- ✅ Benefit 1
- ✅ Benefit 2
- ✅ Benefit 3

**Cons**:
- ❌ Limitation 1
- ❌ Limitation 2
- ❌ Limitation 3

**Implementation Effort**: [Low/Medium/High]
**Learning Curve**: [Low/Medium/High]
**Cost**: [Cost estimate or description]

**Example**:
```
Option 1: RabbitMQ
Pros: ✅ Production-proven, ✅ Advanced routing, ✅ Clustering support
Cons: ❌ New dependency, ❌ Operational overhead, ❌ Complex setup
Effort: Medium (2-3 days to integrate)
```

### Option 2: [Technology/Approach Name]

[Repeat the same structure for Option 2, 3, etc.]

### Option 3: [Technology/Approach Name]

[Repeat the same structure for Option 3, etc.]

---

## Decision

**We have chosen [Selected Option] for the following reasons:**

### Rationale

Explain **why** this decision was made (not just what was chosen):

1. **Alignment with Principles**: How does this align with constitution principles?
   ```
   Example: Aligns with "PostgreSQL as Single Source of Truth" principle by ensuring
   message persistence and preventing data loss.
   ```

2. **Phase Appropriateness**: Is this the right choice for the current phase?
   ```
   Example: Phase 1 requires MVP speed + simplicity. Redis Pub/Sub chosen over RabbitMQ
   to reduce operational overhead. Clear upgrade path documented for Phase 2.
   ```

3. **Risk Mitigation**: How does this reduce key risks?
   ```
   Example: Reduces risk of multi-agent communication failures by providing guaranteed
   delivery semantics and dead-letter queue support.
   ```

4. **Team Capability**: Does the team have expertise with this technology?
   ```
   Example: Team has existing Redis expertise, reducing learning curve.
   ```

### Chosen Option Details

**Name**: [Full name/version of selected technology]
**Version**: [Specific version to use]
**Configuration**: [Key configuration decisions]

```yaml
# Example configuration for chosen technology
service:
  name: redis-event-bus
  version: 7.0.0
  config:
    cluster_enabled: no  # Phase 1 (single instance)
    appendonly: yes      # Enable persistence
    maxmemory: 2gb
    maxmemory_policy: allkeys-lru
```

**Integration Point**: [Where in the codebase this technology is integrated]
```
src/events/bus.py → EventBus class
src/events/handlers.py → Agent event handlers
```

---

## Implementation Plan

### Phase [Current Phase]

**Timeline**: [When this gets implemented]
**Effort**: [Estimated work]
**Dependencies**: [What this depends on]
**Blocked By**: [What blocks this]

**Steps**:
```
1. [First implementation step]
2. [Second implementation step]
3. [Testing/validation step]
4. [Documentation step]
```

### Phase [Future Phase] - Upgrade Path

**Timeline**: [When we upgrade]
**Upgrade Reason**: [Why we need to upgrade]
**Migration Strategy**: [How we migrate from Phase 1 to Phase 2]

**Example**:
```
Phase 2 (Week 32+): Upgrade from Redis Pub/Sub to Redis Streams
Reason: Need message persistence and ordering as message volume grows beyond 100 msg/sec
Migration:
  Week 32: Implement Redis Streams alongside Pub/Sub
  Week 33: Dual-write testing (publish to both)
  Week 34: Gradual consumer migration (10% Streams, 90% Pub/Sub)
  Week 35: Full Streams migration
  Week 36: Remove Pub/Sub code
```

---

## Consequences

### Positive Consequences ✅

1. **Consequence 1**: [What improves/enables this decision]
   - Impact: [Specific impact]
   - Metrics: [How we measure this]

2. **Consequence 2**: ...

### Negative Consequences ❌

1. **Consequence 1**: [What this limits/prevents]
   - Mitigation: [How we address this limitation]
   - Future: [When we upgrade to avoid limitation]

2. **Consequence 2**: ...

### Trade-offs Made

| Factor | Selected | Tradeoff | Resolution |
|--------|----------|----------|-----------|
| Persistence | Phase 1: No | Data loss on crash | Upgrade Phase 2 to Streams |
| Scalability | <1000 msg/sec | Limit on Volume | Upgrade Phase 2 to Streams |
| Operational Cost | Low (Redis only) | Fewer features | Phase 2: More features |

---

## Testing Strategy

### Unit Tests
```python
# How we test this decision at unit level
def test_event_published_to_topic():
    """Verify event is published to correct topic"""
    event = RecipeHarvestedEvent(recipe_id=123)
    await event_bus.publish(event)
    # Assert event published to "recipe.*" topic
```

### Integration Tests
```python
# How we test agent-to-agent communication
async def test_recipe_harvester_to_meal_architect_flow():
    """Verify recipe.harvested.success triggers meal planner update"""
    # 1. Publish recipe.harvested.success event
    # 2. Verify meal planner received it
    # 3. Verify planner updated ingredient taxonomy
```

### Performance Tests
```python
# How we verify performance expectations
def test_event_bus_throughput():
    """Verify event bus handles expected message rate"""
    # Target: 100 msg/sec for Phase 1 (10 concurrent users)
    # Test with 200 msg/sec (2x safety margin)
```

---

## Validation Criteria

How will we know this decision is successful?

- [ ] **Criterion 1**: [Measurable criteria for success]
  - Target: [Specific metric]
  - Measurement: [How we measure it]

- [ ] **Criterion 2**: ...

**Example**:
```
✓ Recipe harvester can publish 100+ events/sec
✓ Event delivery latency <100ms (p99)
✓ Zero message loss in 24-hour test
✓ Agents handle out-of-order events gracefully
✓ Dead letter queue processes failed events within 5 seconds
```

---

## Rollback Plan

**If this decision proves wrong, how do we revert?**

### Rollback Conditions
- [ ] If [condition 1] occurs, rollback
- [ ] If [condition 2] occurs, rollback
- [ ] If [condition 3] occurs, rollback

### Rollback Steps
```
1. [Revert this specific change]
2. [Restore to previous state]
3. [Verify system stability]
4. [Document lessons learned]
```

**Rollback Timeline**: [How quickly we can execute rollback]

**Example**:
```
If event loss detected (>0.1% of events):
1. Pause event publishing (EventBus.pause())
2. Switch to Redis Streams immediately
3. Replay from Redis Streams persistence
4. Resume event publishing
5. Post-mortem on what triggered loss

Estimated rollback time: 5 minutes
```

---

## Related Decisions

- **ADR-XXX**: [Title of related decision]
  - Relationship: [How this ADR relates to ADR-XXX]

- **Principle**: [Constitution principle this aligns with]
  - Reference: [Link to constitution principle]

**Example**:
```
Related to:
- ADR-002: PostgreSQL as Primary Data Store (coordinates with event persistence)
- ADR-005: Prometheus Monitoring (metrics for event bus health)
- Principle VI: PostgreSQL as Single Source of Truth (events must be recoverable)
```

---

## Future Considerations

### Phase [Future Phase] Revisit
- **Timeline**: [When we should revisit this]
- **Reason**: [Why we should reconsider]
- **Trigger**: [What metric or condition triggers review]

**Example**:
```
Phase 2 Revisit (Week 32+):
- Timeline: When message volume exceeds 500 msg/sec
- Reason: Redis Pub/Sub may become bottleneck
- Trigger: If event latency > 1s or message loss observed
- Action: Evaluate upgrade to Redis Streams or RabbitMQ
```

### Known Limitations
- Limitation 1: [What doesn't work well now]
- Limitation 2: ...

### Growth Plan
- When do we outgrow this solution?
- What's the upgrade trigger?
- What's the long-term vision?

---

## References & Resources

### Documentation
- [Link to specification] - Context for this decision
- [Link to constitution] - Principles we follow
- [Link to architecture diagram] - How this fits in the system

### External Resources
- [Technology documentation] - How to use the selected technology
- [Comparison article] - Why we chose this over alternatives
- [Tutorial/guide] - Implementation reference

### Related ADRs
- [ADR-XXX] - Precursor decision
- [ADR-YYY] - Related decision

---

## Approval & Tracking

| Role | Name | Approval | Date |
|------|------|----------|------|
| Technical Lead | [Name] | ⬜ Approve / ❌ Reject | YYYY-MM-DD |
| Architect | [Name] | ⬜ Approve / ❌ Reject | YYYY-MM-DD |
| Project Manager | [Name] | ⬜ Approve / ❌ Reject | YYYY-MM-DD |

**Approval Status**: ⬜ Pending | ✅ Approved | ❌ Rejected

**Change Log**:
- 2025-11-14 (v1.0): Initial proposal
- 2025-11-21 (v1.1): Updated based on feedback
- 2025-12-01 (v2.0): Approved and implemented

---

## Implementation Checklist

### Before Implementation
- [ ] ADR approved by all deciders
- [ ] Technical spike completed (if needed)
- [ ] Performance benchmarked
- [ ] Test plan written
- [ ] Documentation outline created
- [ ] Team trained on technology
- [ ] Rollback procedure documented

### During Implementation
- [ ] Code follows architecture principles
- [ ] Unit tests written
- [ ] Integration tests passing
- [ ] Performance benchmarks verified
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Deployed to staging

### After Implementation
- [ ] Validation criteria met
- [ ] Monitoring/alerting active
- [ ] Production deployment successful
- [ ] Post-implementation review scheduled
- [ ] Lessons learned documented
- [ ] Next phase planning started

---

## Notes & Discussion

**Discussion Points** (What we discussed):
- Point 1: [Key debate or consideration]
- Point 2: [Alternative that was close]
- Point 3: [Unresolved question to revisit]

**Dissenting Opinions** (If anyone disagrees):
- [Person]: [Their concern and why]
  - Response: [How we addressed this concern]

**Future Questions to Answer**:
- [ ] [Question 1 for Phase 2]
- [ ] [Question 2 for Phase 3]

---

---

## How to Use This Template

1. **Copy this file**: `cp adr-template.md docs/adr/ADR-XXX-short-title.md`
2. **Fill in all sections** - Every section should be completed
3. **Get stakeholder approval** before marking as "Accepted"
4. **Link from code** - Reference ADR-XXX in code comments when relevant
5. **Review periodically** - Update "Superseded by" if decision changes
6. **Archive decisions** - Keep all ADRs, even superseded ones

### Minimal ADR (If Short Timeline)
If you need to document quickly, use these sections minimum:
1. Problem Statement
2. Options Considered (title + rationale only)
3. Decision (chosen option + why)
4. Implementation Plan (next immediate steps)
5. Rollback Plan (if goes wrong, how to revert)

### Comprehensive ADR (Standard)
Use all sections for:
- Major technology choices
- Architectural decisions
- Integration patterns
- Security/compliance decisions

---

**Last Updated**: 2025-11-14
**Status**: Template Version 1.0
**For Questions**: Refer to [Architecture Guide](../plan.md) or ask tech lead
