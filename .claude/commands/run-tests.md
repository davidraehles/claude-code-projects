# Run Tests Skill

Execute test suites with coverage reporting and result analysis.

## Usage

```
/run-tests [feature-or-path] [test-type]
```

## Parameters

- `feature-or-path`: Feature number (001, 002) or test file path
- `test-type`: unit | integration | e2e | all (default: all)

## Examples

```
/run-tests 001
/run-tests 001 unit
/run-tests 002 integration
/run-tests src/__tests__/Hero.test.tsx
```

## What It Does

1. Executes appropriate test runner (npm test / pytest)
2. Collects test results
3. Generates coverage report
4. Identifies failing tests
5. Shows test execution time
6. Provides debugging suggestions for failures
7. Compares against coverage targets

## Output

Returns test results:
- Tests passed/failed count
- Execution time
- Coverage percentage
- Failed test details
- Performance metrics
- Recommendations

## When to Use

- Pre-commit validation
- CI/CD pipeline
- Test-driven development
- Coverage verification
- Performance regression detection
