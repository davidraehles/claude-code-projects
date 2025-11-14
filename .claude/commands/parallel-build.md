# Parallel Build Skill

Run frontend and backend builds in parallel with comprehensive error reporting.

## Usage

```
/parallel-build [build-target]
```

## Parameters

- `build-target`: frontend | backend | both (default: both)

## Examples

```
/parallel-build both
/parallel-build frontend
/parallel-build backend
```

## What It Does

1. Starts frontend and backend builds simultaneously
2. Monitors build progress
3. Captures error logs
4. Provides real-time status updates
5. Detects build failures
6. Suggests fixes for common errors
7. Reports bundle sizes
8. Verifies build output
9. Calculates build time savings from parallelization

## Output

Returns build report:
- Build status (success/failure)
- Frontend build time
- Backend build time
- Total time (sequential vs parallel)
- Speedup factor
- Bundle sizes
- Error logs (if any)
- Next steps

## Example Output

```
🏗️  Parallel Build Report

Starting parallel builds...

Frontend Build:
  Tool: Next.js
  Status: ✅ Success
  Time: 23.4s
  Bundle Size: 142 KB
  Chunks: 45

Backend Build:
  Tool: Python/Uvicorn
  Status: ✅ Success
  Time: 5.2s
  Dependencies: 89 packages

Timeline:
  Sequential Time: 28.6s (23.4 + 5.2)
  Parallel Time: 23.4s (backend runs during frontend)
  Speedup: 1.22x faster

Build Artifacts:
  ✓ .next/ (frontend)
  ✓ dist/ (if applicable)
  ✓ __pycache__/ (backend)

Ready for Testing: ✅
Ready for Deployment: ✅
```

## When to Use

- Before pull request creation
- Pre-merge validation
- Release builds
- CI/CD pipeline
- Performance regression testing
- Quick validation builds
