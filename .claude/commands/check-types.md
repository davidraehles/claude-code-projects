# Check Types Skill

Full TypeScript and Python type checking with detailed error reports and fix suggestions.

## Usage

```
/check-types [feature-or-path]
```

## Parameters

- `feature-or-path`: Feature number (001, 002) or file path pattern

## Examples

```
/check-types 001
/check-types src/components/
/check-types app/endpoints/recipes.py
```

## What It Does

1. Runs TypeScript compiler with strict mode
2. Runs Python pyright in strict mode
3. Identifies type errors and mismatches
4. Suggests specific fixes
5. Highlights type coverage gaps
6. Provides type inference help
7. Generates type correction report

## Output

Returns type checking report:
- Total errors count
- Errors by category
- File-by-file breakdown
- Suggested fixes for each error
- Type coverage percentage
- Time to fix estimate

## When to Use

- Before committing code
- Type safety verification
- Code review preparation
- Refactoring verification
- Library updates compatibility check
