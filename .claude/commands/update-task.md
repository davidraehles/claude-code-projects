# Update Task Skill

Update task status and progress in tasks.md with automatic artifact synchronization.

## Usage

```
/update-task [task-id] [status] [notes]
```

## Parameters

- `task-id`: Task ID from tasks.md (e.g., 001-001-01)
- `status`: in-progress | completed | blocked | pending
- `notes`: Optional notes about task progress

## Examples

```
/update-task 001-001-01 completed "Hero component done, tests passing"
/update-task 002-001-02 blocked "Waiting for data schema finalization"
/update-task 001-002-03 in-progress "Services section 60% complete"
```

## What It Does

1. Updates task status in tasks.md
2. Records completion timestamp
3. Links to implemented files
4. Adds notes and blockers
5. Updates percentage completion
6. Automatically creates git commit
7. Updates related artifacts
8. Triggers documentation sync if completed

## Output

Returns confirmation:
- Task updated with new status
- Timestamp recorded
- File links added
- Commit created
- Related artifacts updated

## When to Use

- Task status change
- Daily progress tracking
- Blocker documentation
- Task completion marking
- Team communication
