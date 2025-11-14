# Sync Artifacts Skill

Keep specification artifacts (spec.md, plan.md, tasks.md, ADRs) synchronized with code changes.

## Usage

```
/sync-artifacts [feature] [changes-description]
```

## Parameters

- `feature`: Feature number (001, 002)
- `changes-description`: Brief description of code changes

## Examples

```
/sync-artifacts 001 "Implemented Hero component with animations"
/sync-artifacts 002 "Added Recipe Harvester Agent"
```

## What It Does

1. Reads code changes from git diff
2. Updates spec.md with completed items
3. Updates plan.md with implemented architecture
4. Updates tasks.md task status
5. Updates data-model.md if schema changed
6. Creates/updates ADRs if needed
7. Updates CHANGELOG with new entries
8. Verifies artifact consistency

## Output

Returns synchronization report:
- Updated artifacts (spec.md, plan.md, tasks.md)
- New ADRs created (if applicable)
- CHANGELOG entries added
- Consistency verification results
- Missing updates (if any)

## When to Use

- After completing a feature
- Before creating pull request
- Regular artifact maintenance
- Release preparation
- Documentation accuracy verification
